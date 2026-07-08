#!/bin/bash
# Re-fetch one occupation's law for one or more states — for when a state changes
# its statutes and you need fresh text a year from now. This is the ONE step that
# needs the internet + a real Chrome window (the source, Justia, sits behind a
# "Just a moment…" check that only a genuine browser clears). Everything after this
# (clean/trim/extract) is the normal three commands and needs no browser.
#
# Usage:
#   bash pipeline/client/refetch.sh <occupation> <STATE[,STATE,...]>
#   e.g.  bash pipeline/client/refetch.sh court_reporter UT
#         bash pipeline/client/refetch.sh forester UT,ID,MT
#
# After it finishes, re-run the normal steps for those same states to get data:
#   ...run clean / trim / extract  (see the dashboard or docs/runbooks/client_refetch.md)
#
# PLATFORM: macOS only. The "start Chrome" hint below uses the macOS app path
# (/Applications/Google Chrome.app). On Windows/Linux, launch Chrome yourself with
# --remote-debugging-port=9222 --user-data-dir=<tmp>, clear the Justia challenge once,
# then re-run this (JUSTIA_CDP_URL points at that Chrome).

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

PROF="${1:-}"; STATES="${2:-}"
if [ -z "$PROF" ] || [ -z "$STATES" ]; then
  echo "usage: bash pipeline/client/refetch.sh <occupation> <STATE[,STATE,...]>"
  echo "   e.g. bash pipeline/client/refetch.sh court_reporter UT"
  exit 1
fi

PY="pipeline/.venv/bin/python"
export JUSTIA_CDP_URL="${JUSTIA_CDP_URL:-http://127.0.0.1:9222}"

# --- 1. is the debug Chrome up? If not, tell the user exactly how to start it. ----
if ! curl -s --max-time 5 "$JUSTIA_CDP_URL/json/version" >/dev/null 2>&1; then
  cat <<EOF

The fetch browser isn't running yet. Start it once, then re-run this command:

  1. Open a NEW terminal window and paste this (macOS):

     /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \\
       --remote-debugging-port=9222 --user-data-dir=/tmp/justia-chrome

  2. In the Chrome window that opens, go to:  https://law.justia.com/
     If you see a "Just a moment…" / "Verify you are human" screen, wait for it
     to finish (or click the checkbox). Once a normal Justia page shows, you're set.

  3. Leave that Chrome open and re-run:
     bash pipeline/client/refetch.sh $PROF $STATES

EOF
  exit 1
fi

# --- 2. fetch (same engine the whole pipeline uses) ------------------------------
echo "Fetching $PROF for: $STATES  (this can take a couple of minutes per state)"
$PY -m pipeline.ingest.refresh_corpus --profession "$PROF" --states "$STATES"

# --- 3. what to do next ----------------------------------------------------------
cat <<EOF

Fetched. The fresh text is in pipeline/results/text/$PROF/.
Now turn it into data with the normal steps (only these two cost money) — every state
with work to do for $PROF is picked up automatically, no file needed:

  $PY -m pipeline.client.run clean   --professions $PROF
  $PY -m pipeline.client.run trim    --professions $PROF
  $PY -m pipeline.client.run extract --professions $PROF
EOF
