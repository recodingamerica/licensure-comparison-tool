#!/bin/bash
# Re-arming supervisor for the gap-harvest pull driver — the autonomy layer.
#
# Runs gap_pull.sh, waits for it to finish (a full worklist pass), then RE-RUNS it if
# any cells are still unpulled (e.g. Cloudflare-challenge misses that self-heal once the
# wall clears). Exits only when the worklist is fully pulled. Because it runs in the
# user's session it inherits the ~/Documents (TCC) access a launchd agent lacks.
#
# Launch (detached, idle-sleep-inhibited):
#   caffeinate -disu bash pipeline/discover/gap_harvest/gap_supervise.sh
#
# Survives: driver crashes, a completed-but-incomplete pass, and sleep-WAKE (both the
#   supervisor and driver suspend/resume). Does NOT survive: logout / reboot / being
#   killed (for that, load the launchd plist after granting Full Disk Access — see
#   com.utah.gapharvest.plist), or lid-close sleep (needs AC + lid open / `sudo pmset`).
#
# Idempotent + safe to run once; a flock in refresh_corpus still guards the one Chrome.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
PY="pipeline/.venv/bin/python"

count_unpulled() {
  "$PY" - <<'PY'
import json, os
wl = json.load(open("pipeline/results/gap_harvest/pull_worklist.json"))
def pulled(p, s):
    f = f"pipeline/results/text/{p}/{s}.json"
    if not os.path.exists(f):
        return False
    try:
        d = json.load(open(f))
    except Exception:
        return False
    return len(d if isinstance(d, list) else d.get("sections", [])) > 0
print(sum(1 for p, ss in wl.items() for s in ss if not pulled(p, s)))
PY
}

echo "########## SUPERVISOR START $(date) ##########"
passes=0
while true; do
  u=$(count_unpulled 2>/dev/null || echo "?")
  if [ "$u" = "0" ]; then
    echo "$(date) supervisor: worklist COMPLETE after $passes pass(es) — exiting"
    break
  fi
  passes=$((passes + 1))
  echo "$(date) supervisor: pass #$passes starting ($u cells unpulled)"
  bash pipeline/discover/gap_harvest/gap_pull.sh
  echo "$(date) supervisor: pass #$passes ended; 30s cooldown then re-check"
  sleep 30
done
