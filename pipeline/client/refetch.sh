#!/bin/bash
# Re-fetch one occupation's law for one or more states — for when a state changes
# its statutes and you need fresh text a year from now. This is the ONE step that
# needs the internet. The source, Justia, sits behind a "Just a moment…" Cloudflare
# check, but the fetcher (a headless stealth browser) clears it automatically — no
# browser window opens and there's nothing to click. Everything after this
# (clean/trim/extract) is the normal three commands and needs no internet.
#
# Usage:
#   bash pipeline/client/refetch.sh <occupation> <STATE[,STATE,...]>
#   e.g.  bash pipeline/client/refetch.sh court_reporter UT
#         bash pipeline/client/refetch.sh forester UT,ID,MT
#
# After it finishes, re-run the normal steps for those same states to get data:
#   ...run clean / trim / extract  (see the dashboard or CLIENT_GUIDE.md)

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

PROF="${1:-}"; STATES="${2:-}"
if [ -z "$PROF" ] || [ -z "$STATES" ]; then
  echo "usage: bash pipeline/client/refetch.sh <occupation> <STATE[,STATE,...]>"
  echo "   e.g. bash pipeline/client/refetch.sh court_reporter UT"
  exit 1
fi

PY="pipeline/.venv/bin/python"

# --- fetch (same engine the whole pipeline uses; headless, clears Cloudflare itself) ---
echo "Fetching $PROF for: $STATES  (this can take a couple of minutes per state)"
$PY -m pipeline.ingest.refresh_corpus --profession "$PROF" --states "$STATES"

# --- what to do next -------------------------------------------------------------
cat <<EOF

Fetched. The fresh text is in pipeline/results/text/$PROF/.
Now turn it into data with the normal steps (only these two cost money) — every state
with work to do for $PROF is picked up automatically, no file needed:

  $PY -m pipeline.client.run clean   --professions $PROF
  $PY -m pipeline.client.run trim    --professions $PROF
  $PY -m pipeline.client.run extract --professions $PROF
EOF
