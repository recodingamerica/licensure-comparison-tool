#!/bin/bash
# Watchdog for the gap-harvest supervisor. Polls every 5 minutes; if
# gap_supervise.sh isn't running, relaunches it (nohup + disown, reparented to
# init) the same way it was started manually. Protects against ANY silent death
# of the supervisor -- known cause or not (2026-07-07: it died silently for 3+
# hours with nobody noticing, cause unclear -- not a Mac sleep, since pmset -g
# log showed no sleep/wake event in that window).
#
# Caps restarts at MAX_RESTARTS so a persistently-broken environment (e.g. the
# debug Chrome itself gone) doesn't respawn forever uselessly -- it gives up
# loudly instead, logged here.
#
# Launch (detached, from repo root):
#   nohup bash pipeline/discover/gap_harvest/watchdog.sh >> pipeline/results/gap_harvest/watchdog.log 2>&1 &
#   disown
cd "$(git rev-parse --show-toplevel)" || exit 1
POLL_SECONDS=300
MAX_RESTARTS=20
restarts=0

echo "########## WATCHDOG START $(date) ##########"
while true; do
  sleep "$POLL_SECONDS"
  if pgrep -f "bash pipeline/discover/gap_harvest/gap_supervise.sh" >/dev/null 2>&1; then
    continue
  fi
  restarts=$((restarts + 1))
  if [ "$restarts" -gt "$MAX_RESTARTS" ]; then
    echo "$(date) watchdog: gap_supervise.sh is down and MAX_RESTARTS ($MAX_RESTARTS) exceeded -- giving up, needs a human"
    break
  fi
  echo "$(date) watchdog: gap_supervise.sh not running -- relaunching (restart #$restarts)"
  nohup caffeinate -disu bash pipeline/discover/gap_harvest/gap_supervise.sh \
    >> pipeline/results/gap_harvest/gap_supervise.log 2>&1 &
  disown
done
echo "########## WATCHDOG STOPPED $(date) ##########"
