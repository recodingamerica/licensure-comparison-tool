"""Show newly-matched (state, profession) pairs after expand_hierarchy +
match_profession reruns.

Compares the current results/profession_index/_coverage.csv against a
snapshot saved to /tmp/coverage_before.csv (taken before the expand).
Prints a markdown-ish table of new matches per profession.

Usage:
  cp pipeline/results/profession_index/_coverage.csv /tmp/coverage_before.csv  # before expand
  # ... run expand_hierarchy + match_profession ...
  python -m pipeline.discover.diff_coverage
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import PROFESSION_INDEX_DIR  # noqa: E402

BEFORE_PATH = Path("/tmp/coverage_before.csv")
AFTER_PATH = PROFESSION_INDEX_DIR / "_coverage.csv"


def parse_coverage(path: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    with path.open() as f:
        for row in csv.DictReader(f):
            out[row["profession"]] = {
                "display": row.get("display", ""),
                "states_matched": int(row.get("states_matched", 0)),
                "states_total": int(row.get("states_total", 0)),
                "missing_states": set(row.get("missing_states", "").split(",")) - {""},
            }
    return out


def main() -> None:
    if not BEFORE_PATH.exists():
        sys.exit(f"missing {BEFORE_PATH} — snapshot before running expand")
    if not AFTER_PATH.exists():
        sys.exit(f"missing {AFTER_PATH}")
    before = parse_coverage(BEFORE_PATH)
    after = parse_coverage(AFTER_PATH)

    rows = []
    for prof, a in after.items():
        b = before.get(prof, {"states_matched": 0, "missing_states": set()})
        # States that were missing before and are matched now
        newly_matched = sorted((b.get("missing_states") or set()) - a["missing_states"])
        # States that were matched before but are now missing (regressions)
        regressions = sorted(a["missing_states"] - (b.get("missing_states") or set()))
        rows.append({
            "profession": prof,
            "display": a["display"],
            "before": b["states_matched"],
            "after": a["states_matched"],
            "delta": a["states_matched"] - b["states_matched"],
            "newly_matched": newly_matched,
            "regressions": regressions,
        })
    rows.sort(key=lambda r: (-r["delta"], r["profession"]))

    print(f"{'profession':30s}  {'before':>6}  {'after':>5}  {'Δ':>3}  newly_matched")
    print("-" * 100)
    for r in rows:
        if r["delta"] == 0 and not r["regressions"]:
            continue
        marker = "+" if r["delta"] > 0 else ""
        new = ",".join(r["newly_matched"]) if r["newly_matched"] else "—"
        reg = f"  ⚠ regressions: {','.join(r['regressions'])}" if r["regressions"] else ""
        print(f"{r['profession']:30s}  {r['before']:>6}  {r['after']:>5}  {marker}{r['delta']:>3}  {new}{reg}")


if __name__ == "__main__":
    main()
