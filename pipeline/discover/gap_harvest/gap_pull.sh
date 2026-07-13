#!/bin/bash
# Self-healing gap-harvest pull. ONE state per process (Playwright cross-thread bug),
# skips already-pulled (resumable), commits per profession. Fetching is headless via
# Scrapling (no debug Chrome, no wait-for-Chrome). Reads
# results/gap_harvest/pull_worklist.json ({prof: [states]}, written by reuse.py).
# Launch: caffeinate -disu bash pipeline/discover/gap_harvest/gap_pull.sh
cd "$(git rev-parse --show-toplevel)" || exit 1
# Tell pull_text's over-broad guard our own per-cell timeout (below) so it can skip in
# seconds + flag for narrowing any chapter too large to fetch in that time — regardless
# of label match — instead of grinding the full timeout and reverting empty every pass
# (the 2026-07-07 lesson: see pull_text.py's _fetch_budget_max_leaves comment).
export PULL_BATCH_TIMEOUT_SECONDS=900
PY="pipeline/.venv/bin/python"
WL="pipeline/results/gap_harvest/pull_worklist.json"
MISSES="pipeline/results/gap_harvest/miss_counts.json"
PARKED="pipeline/results/gap_harvest/parked_cells.json"
MISS_LIMIT=3   # consecutive empty attempts before a cell is parked (not deleted)

is_pulled() {  # 0 if corpus $1/$2 exists with >=1 section
  $PY - "$1" "$2" <<'PY' 2>/dev/null
import json,sys,os
f=f"pipeline/results/text/{sys.argv[1]}/{sys.argv[2]}.json"
if not os.path.exists(f): sys.exit(1)
d=json.load(open(f)); s=d if isinstance(d,list) else d.get("sections",[])
sys.exit(0 if len(s)>0 else 1)
PY
}

# A cell that's genuinely, permanently empty (bad locator guess, exemption-only
# chapter, repealed statute) will fail every retry forever -- with no circuit
# breaker, gap_supervise.sh's while-true loop re-grinds it every single pass and
# can never reach 0-unpulled. After MISS_LIMIT consecutive failed attempts, park it
# (remove from the worklist, record in parked_cells.json for human review) instead
# of retrying forever. A transient miss (Cloudflare hiccup) still gets MISS_LIMIT
# tries first, so self-healing per pull_text's documented behavior isn't cut short.
record_miss() {
  $PY - "$1" "$2" "$MISSES" "$WL" "$PARKED" "$MISS_LIMIT" <<'PY'
import json, sys
prof, st, misses_path, wl_path, parked_path, limit = sys.argv[1:7]
limit = int(limit)
misses = json.load(open(misses_path)) if __import__("os").path.exists(misses_path) else {}
n = misses.setdefault(prof, {}).get(st, 0) + 1
misses[prof][st] = n
json.dump(misses, open(misses_path, "w"), indent=1)
if n >= limit:
    wl = json.load(open(wl_path))
    if st in wl.get(prof, []):
        wl[prof].remove(st)
        if not wl[prof]:
            del wl[prof]
        json.dump(wl, open(wl_path, "w"), indent=1)
    parked = json.load(open(parked_path)) if __import__("os").path.exists(parked_path) else []
    parked.append({"profession": prof, "state": st, "misses": n})
    json.dump(parked, open(parked_path, "w"), indent=1)
    print(f"PARKED {prof}/{st} after {n} consecutive misses -- see gap_harvest/parked_cells.json")
PY
}

kill_pull_orphans() {
  # Reap anything the per-cell `timeout` left behind. `timeout` kills refresh_corpus but
  # NOT its browser-driver grandchild; an orphaned driver can wedge subsequent cells (the
  # 2026-07-06 cascade: one 15-min timeout poisoned the whole run). Reap both so a slow
  # cell only costs itself. Targets the pip Playwright driver ONLY
  # (site-packages/…/run-driver) — never the separate `playwright-mcp` browser tooling.
  pkill -f "pipeline.ingest.refresh_corpus"                2>/dev/null
  pkill -f "site-packages/playwright/driver.*run-driver"   2>/dev/null
  sleep 2
}

echo "########## GAP PULL START $(date) ##########"
for prof in $($PY -c "import json;print(' '.join(sorted(json.load(open('$WL')))))"); do
  states=$($PY -c "import json;print(' '.join(json.load(open('$WL'))['$prof']))")
  changed=0
  for st in $states; do
    is_pulled "$prof" "$st" && continue
    echo "===== $prof / $st $(date +%T) ====="
    timeout --kill-after=60 900 $PY -m pipeline.ingest.refresh_corpus --profession "$prof" --states "$st" 2>&1 \
      | grep -E "leaf sections|refresh complete|thread|-> 0 leaf|SOLVE" | tail -3
    kill_pull_orphans   # reap orphaned driver so a timed-out cell can't wedge the next
    if is_pulled "$prof" "$st"; then
      changed=1
    else
      record_miss "$prof" "$st"
    fi
  done
  if [ "$changed" = "1" ]; then
    git add pipeline/results/text/"$prof"/ 2>/dev/null
    git commit -q -m "gap-harvest: pull $prof ($(date +%H:%M))" 2>/dev/null && echo "  committed $prof"
  fi
done
echo "########## GAP PULL DONE $(date) ##########"
