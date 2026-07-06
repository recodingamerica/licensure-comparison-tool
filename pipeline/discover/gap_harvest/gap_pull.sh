#!/bin/bash
# Self-healing gap-harvest pull. One state per process (Playwright thread bug),
# flock-guarded (one CDP process), skips already-pulled (resumable), commits per
# profession, waits out Chrome-down. Launch: caffeinate -disu bash gap_pull.sh
cd /Users/abigailhaddad/Documents/repos/utah
export JUSTIA_CDP_URL=http://127.0.0.1:9222
PY="pipeline/.venv/bin/python"
SP="/private/tmp/claude-501/-Users-abigailhaddad-Documents-repos-utah/a4c2a38a-3f03-4281-9391-7b1770858434/scratchpad"
WL="$SP/gap_pull_worklist.json"

is_pulled() {  # 0 if corpus $1/$2 exists with real sections
  $PY - "$1" "$2" <<'PY' 2>/dev/null
import json,sys,os
f=f"pipeline/results/text/{sys.argv[1]}/{sys.argv[2]}.json"
if not os.path.exists(f): sys.exit(1)
d=json.load(open(f)); s=d if isinstance(d,list) else d.get("sections",[])
sys.exit(0 if len(s)>0 else 1)
PY
}

echo "########## GAP PULL START $(date) ##########"
for prof in $($PY -c "import json;print(' '.join(sorted(json.load(open('$WL')))))"); do
  states=$($PY -c "import json;print(' '.join(json.load(open('$WL'))['$prof']))")
  changed=0
  for st in $states; do
    if is_pulled "$prof" "$st"; then continue; fi
    # wait for Chrome if it went down
    until curl -s --max-time 5 http://127.0.0.1:9222/json/version >/dev/null 2>&1; do
      echo "$(date) Chrome down — waiting 60s"; sleep 60; done
    echo "===== $prof / $st $(date +%T) ====="
    timeout --kill-after=60 900 $PY -m pipeline.ingest.refresh_corpus --profession "$prof" --states "$st" 2>&1 \
      | grep -E "leaf sections|refresh complete|thread|-> 0 leaf|SOLVE" | tail -3
    is_pulled "$prof" "$st" && changed=1
  done
  # commit per profession if anything landed
  if [ "$changed" = "1" ]; then
    git add pipeline/results/text/"$prof"/ 2>/dev/null
    git commit -q -m "gap-harvest: pull $prof ($(date +%H:%M))" 2>/dev/null && echo "  committed $prof"
  fi
done
echo "########## GAP PULL DONE $(date) ##########"
