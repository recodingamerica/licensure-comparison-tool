"""Check our regulatory_model classifications against Utah OPLR ground truth.

Utah's Office of Professional Licensure Review (OPLR) publishes per-profession
periodic-review reports. Each states a "Regulatory Model Recommendation" — the
model OPLR thinks Utah should use (which, for "Continue to ..." reports, is also
the current Utah model). That gives us an independent ground-truth label for
the Utah (UT) jurisdiction, which we can compare against what our pipeline
extracted for UT.

Ground truth lives in docs/lit_review/oplr_ground_truth.csv (one row per
profession). This script joins it to our structured UT extraction and reports
matches / mismatches / not-yet-extracted.

This is the held-out-validation harness: as OPLR publishes more reports (and we
run those professions through the pipeline), add rows to the CSV and re-run.

Usage:
  python -m pipeline.eval.check_vs_oplr
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR  # noqa: E402

GROUND_TRUTH = Path(__file__).resolve().parent.parent.parent / "docs" / "lit_review" / "oplr_ground_truth.csv"
STRUCTURED = RESULTS_DIR / "structured"

# Map free-text OPLR recommendation language to our RegulatoryModel enum, in
# case a row stores the raw recommendation instead of a normalized model.
_KEYWORDS = [
    ("market_forces", ("no regulation", "deregulate", "market forces")),
    ("voluntary_certification", ("voluntary cert", "title protection", "right-to-title", "right to title")),
    ("registration", ("registr",)),
    ("exemption", ("exempt",)),
    ("mandatory_certification", ("mandatory cert",)),
    ("license", ("licens",)),  # last: "license" substring is the most permissive
]


def normalize_model(text: str) -> str | None:
    t = (text or "").lower()
    for model, kws in _KEYWORDS:
        if any(k in t for k in kws):
            return model
    return None


def our_ut_model(profession: str) -> str | None:
    p = STRUCTURED / profession / "UT.json"
    if not p.exists():
        return "__NOT_EXTRACTED__"
    d = json.loads(p.read_text())
    rm = (d.get("licensure") or {}).get("regulatory_model") or {}
    return rm.get("value")


def main() -> None:
    rows = list(csv.DictReader(GROUND_TRUTH.open()))
    print(f"OPLR ground-truth check — {len(rows)} profession(s)\n")
    print(f"{'profession':22s} {'oplr':24s} {'ours (UT)':24s} verdict")
    print("-" * 84)
    matches = mismatches = pending = 0
    for r in rows:
        prof = r["profession"].strip()
        # Compare against the CURRENT Utah model (what the statute is today) —
        # our pipeline extracts current law, not OPLR's policy recommendation.
        oplr = (r.get("oplr_current_model") or "").strip() or normalize_model(
            r.get("oplr_recommendation_text", "")
        )
        ours = our_ut_model(prof)
        if ours == "__NOT_EXTRACTED__":
            verdict = "— not extracted yet"
            pending += 1
            ours_disp = "(not run)"
        elif ours == oplr:
            verdict = "✓ match"
            matches += 1
            ours_disp = ours or "None"
        else:
            verdict = "✗ MISMATCH"
            mismatches += 1
            ours_disp = ours or "None"
        print(f"{prof:22s} {oplr or '?':24s} {ours_disp:24s} {verdict}")
    print("-" * 84)
    print(f"{matches} match, {mismatches} mismatch, {pending} not yet extracted")
    if mismatches:
        sys.exit(1)


if __name__ == "__main__":
    main()
