#!/bin/bash
# Held-out OPLR prompt test: extract UT-only for 8 professions with published
# OPLR ground truth, then check regulatory_model vs OPLR. Full chain per
# profession: pull -> clean -> trim -> extract (no publish; local test only).
set -e
cd /Users/abigailhaddad/Documents/repos/utah
PY=pipeline/.venv/bin/python   # has curl_cffi for the Justia fetch
PROFS="physician_assistant respiratory_care occupational_therapy physical_therapy acupuncture athletic_training hearing_instrument_specialist speech_language_audiology"
for p in $PROFS; do
  echo "===== $p (UT) ====="
  $PY -m pipeline.ingest.pull_text --profession "$p" --states UT || { echo "PULL FAILED $p"; continue; }
  $PY -m pipeline.ingest.clean_text --profession "$p" || { echo "CLEAN FAILED $p"; continue; }
  $PY -m pipeline.ingest.trim_state --profession "$p" --states UT || { echo "TRIM FAILED $p"; continue; }
  $PY -m pipeline.extract.extract_state --profession "$p" --states UT || { echo "EXTRACT FAILED $p"; continue; }
done
echo "===== CHECK vs OPLR ====="
$PY -m pipeline.eval.check_vs_oplr || true
