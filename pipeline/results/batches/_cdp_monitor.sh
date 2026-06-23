#!/bin/bash
# Grind health monitor — fires on the first real event, prints % + health.
# Re-armed by the agent after each firing. Signals (chosen deliberately):
#   - PROFESSION_DONE: a new "via CDP-Justia grind" commit (ignores manual commits).
#   - GRIND_DEAD: driver process gone.
#   - POSSIBLE_HANG: no new state file in 20 min (generous — big multi-chapter
#     states take <10 min; a stuck challenge errors-and-continues rather than
#     freezing, so a true 20-min silence means something is actually wrong).
# Cloudflare trouble shows as a RISING ERROR RATE, surfaced in the per-profession
# health report below — not as an idle log.
set -u
cd /Users/abigailhaddad/Documents/repos/utah
PY=pipeline/.venv/bin/python
TEXT=pipeline/results/text
SEEN=$(git log --oneline --grep "via CDP-Justia grind" -1 --format=%H 2>/dev/null)
PROF=""
for i in $(seq 1 75); do          # ~2.5h at 120s
  sleep 120
  if ! pgrep -f _cdp_grind.py >/dev/null; then echo "EVENT=GRIND_DEAD"; break; fi
  LATEST=$(git log --oneline --grep "via CDP-Justia grind" -1 --format=%H 2>/dev/null)
  if [ -n "$LATEST" ] && [ "$LATEST" != "$SEEN" ]; then
    PROF=$(git log -1 --format=%s "$LATEST" | sed -E 's/^data: ([a-z_]+) via.*/\1/')
    echo "EVENT=PROFESSION_DONE: $PROF"; break
  fi
  if [ -z "$(find "$TEXT" -name '*.json' -newermt '-20 minutes' 2>/dev/null)" ]; then
    echo "EVENT=POSSIBLE_HANG (no new state file in 20min — check the grind/Chrome)"; break
  fi
  # Disk guard: pause the grind before it can fill the disk.
  FREEKB=$(df -k . | tail -1 | awk '{print $4}')
  if [ "$FREEKB" -lt 3145728 ]; then   # < 3GB
    pkill -f _cdp_grind.py
    echo "EVENT=LOW_DISK (<3GB free — PAUSED the grind to protect the disk)"; break
  fi
done
echo ""
echo "  free disk: $(df -h . | tail -1 | awk '{print $4}')"
$PY pipeline/results/batches/_cdp_progress.py 2>/dev/null | grep -E "HARVEST|states pulled|professions complete|currently"
if [ -n "$PROF" ]; then
  echo ""
  echo "  --- health: $PROF ---"
  $PY pipeline/results/batches/_cdp_audit.py --profession "$PROF" 2>/dev/null | grep -vE "^wrote " | head -20
fi
