#!/bin/bash
# After the UT umbrella re-pull: forced re-pull CO/IN umbrella (already-pulled
# states won't re-pull via the grind), then resume the trades-first grind which
# pulls the 15 new missed-match states + the broad harvest.
cd /Users/abigailhaddad/Documents/repos/utah
export JUSTIA_CDP_URL=http://localhost:9222 PULL_HOST_DELAY=3
PY=pipeline/.venv/bin/python
echo "[cont] forced umbrella re-pull: CO electrician/plumbing + IN plumbing"
$PY -m pipeline.ingest.pull_text --profession electrician --states CO --limit-sections 250 --force 2>&1 | tail -2
$PY -m pipeline.ingest.pull_text --profession plumbing   --states CO,IN --limit-sections 250 --force 2>&1 | tail -3
echo "[cont] resuming grind (trades-first; pulls 15 missed-match new states then broad harvest)"
$PY pipeline/results/batches/_cdp_grind.py >> pipeline/results/batches/_cdp_grind.log 2>&1 &
GPID=$!
sleep 5
GPID=$(pgrep -f _cdp_grind.py | head -1)
nohup caffeinate -dimsu -w "$GPID" >/dev/null 2>&1 &
echo "[cont] grind resumed PID $GPID, re-caffeinated. DONE"
