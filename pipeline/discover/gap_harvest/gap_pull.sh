#!/bin/bash
# Self-healing gap-harvest pull. ONE state per process (Playwright cross-thread bug),
# flock-guarded (one CDP Chrome), skips already-pulled (resumable), commits per profession,
# waits out Chrome-down. Reads results/gap_harvest/pull_worklist.json ({prof: [states]},
# written by reuse.py). Launch: caffeinate -disu bash pipeline/discover/gap_harvest/gap_pull.sh
cd "$(git rev-parse --show-toplevel)" || exit 1
export JUSTIA_CDP_URL=${JUSTIA_CDP_URL:-http://127.0.0.1:9222}
PY="pipeline/.venv/bin/python"
WL="pipeline/results/gap_harvest/pull_worklist.json"

is_pulled() {  # 0 if corpus $1/$2 exists with >=1 section
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
    is_pulled "$prof" "$st" && continue
    until curl -s --max-time 5 "$JUSTIA_CDP_URL/json/version" >/dev/null 2>&1; do
      echo "$(date) Chrome down — waiting 60s"; sleep 60; done
    echo "===== $prof / $st $(date +%T) ====="
    timeout --kill-after=60 900 $PY -m pipeline.ingest.refresh_corpus --profession "$prof" --states "$st" 2>&1 \
      | grep -E "leaf sections|refresh complete|thread|-> 0 leaf|SOLVE" | tail -3
    is_pulled "$prof" "$st" && changed=1
  done
  if [ "$changed" = "1" ]; then
    git add pipeline/results/text/"$prof"/ 2>/dev/null
    git commit -q -m "gap-harvest: pull $prof ($(date +%H:%M))" 2>/dev/null && echo "  committed $prof"
  fi
done
echo "########## GAP PULL DONE $(date) ##########"
