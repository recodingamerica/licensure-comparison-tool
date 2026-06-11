#!/bin/bash
# Step 2 of held-out test: trim data is already staged for the 8 professions.
# Run the discovery pass (creates discovered/<prof>.json that extract needs),
# then extract UT, then check vs OPLR ground truth.
set -e
cd /Users/abigailhaddad/Documents/repos/utah
PY=pipeline/.venv/bin/python
PROFS="physician_assistant respiratory_care occupational_therapy physical_therapy acupuncture athletic_training hearing_instrument_specialist speech_language_audiology"
for p in $PROFS; do
  echo "===== $p: discover + extract (UT) ====="
  $PY -m pipeline.extract.discover_schema --profession "$p" --max-states 1 || { echo "DISCOVER FAILED $p"; continue; }
  $PY -m pipeline.extract.extract_state --profession "$p" --states UT || { echo "EXTRACT FAILED $p"; continue; }
done
echo "===== CHECK vs OPLR ====="
$PY -m pipeline.eval.check_vs_oplr || true
