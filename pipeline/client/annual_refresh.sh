#!/bin/bash
# Annual statute refresh — re-pull EVERY occupation's law for every state and report
# what changed. This is the once-a-year "has any state rewritten its statutes?" check.
#
# Just run:
#   bash pipeline/client/annual_refresh.sh
#
# What to expect:
#   * It first tells you how many corpora it will check and roughly how long, and
#     asks you to confirm. It's a big job (can be an hour+ of fetching).
#   * A live progress bar shows where it is; the raw fetch logs go to a file, not
#     your screen.
#   * It's SAFE to stop (Ctrl-C) and re-run this same command — it picks up where it
#     left off (--resume) and re-tries anything that failed.
#   * Nothing is ever silently destroyed: a pull that comes back smaller than what's
#     committed is HELD BACK for your review, and every change is its own git commit
#     you can undo with `git revert`.
#
# At the end you get a plain-English summary (also saved to a file) listing anything
# that needs your eyes. For a held-back occupation you've confirmed is a real change:
#   bash pipeline/client/refetch.sh <occupation> <STATE>        # normal re-pull, or
#   pipeline/.venv/bin/python -m pipeline.ingest.refresh_corpus \
#       --profession <occupation> --states <STATE> --force      # to accept a shrink
#
# Optional: pass a run id (defaults to the current year), e.g.
#   bash pipeline/client/annual_refresh.sh 2027

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

PY="pipeline/.venv/bin/python"
RUN_ID="${1:-$(date +%Y)}"

RESUME=""
if [ -f "pipeline/results/refresh_status_${RUN_ID}.json" ]; then
  echo "Found an earlier run for ${RUN_ID} — resuming where it left off."
  echo "(To start over instead, use a different id: bash $0 ${RUN_ID}-rerun)"
  echo
  RESUME="--resume"
fi

$PY -m pipeline.ingest.refresh_corpus --all-professions --run-id "$RUN_ID" $RESUME
