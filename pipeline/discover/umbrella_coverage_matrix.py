"""Materialize the (state × profession) → umbrella-sections map from
`umbrella_scope/<STATE>.json` files. Useful both as a deliverable artifact
and as a sanity-check view ("which sections does this profession actually
inherit?").

Output: pipeline/results/profession_index/_umbrella_coverage.csv with rows:
  state, profession, scope_source, chapter, part, section_label, section_url

Usage:
  python -m pipeline.discover.umbrella_coverage_matrix
  python -m pipeline.discover.umbrella_coverage_matrix --state UT
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR, PROFESSION_INDEX_DIR  # noqa: E402

UMBRELLA_SCOPE_DIR = RESULTS_DIR / "umbrella_scope"


def _all_professions() -> list[str]:
    return sorted(p.stem for p in PROFESSION_INDEX_DIR.glob("*.json"))


def matrix_for_state(state: str) -> list[dict]:
    scope_path = UMBRELLA_SCOPE_DIR / f"{state}.json"
    if not scope_path.exists():
        return []
    data = json.loads(scope_path.read_text())
    profs = _all_professions()
    rows: list[dict] = []
    for entry in data.get("sections", []):
        src = entry.get("scope_source")
        if src in ("anchor_universal", "universal"):
            applicable = profs
        elif src in ("anchor_enumeration", "inherited_enumeration"):
            applicable = entry.get("applies_to_professions") or []
        else:
            applicable = []  # undetermined → no row (we excluded these from prompts too)
        for prof in applicable:
            rows.append({
                "state": state,
                "profession": prof,
                "scope_source": src,
                "chapter": entry.get("umbrella_chapter_slug", ""),
                "part": entry.get("umbrella_part", ""),
                "section_label": entry.get("label", ""),
                "section_url": entry.get("url", ""),
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", help="single state (default: all states with a scope file)")
    args = ap.parse_args()

    states = (
        [args.state]
        if args.state
        else sorted(p.stem for p in UMBRELLA_SCOPE_DIR.glob("*.json"))
    )

    rows: list[dict] = []
    for st in states:
        rows.extend(matrix_for_state(st))

    out = PROFESSION_INDEX_DIR / "_umbrella_coverage.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # Quick summary table to stdout
    by_state_prof: dict[tuple[str, str], int] = {}
    for r in rows:
        k = (r["state"], r["profession"])
        by_state_prof[k] = by_state_prof.get(k, 0) + 1

    print(f"Wrote {out}  ({len(rows)} rows across {len(states)} state(s))")
    print()
    by_state: dict[str, dict[str, int]] = {}
    for (st, pr), n in by_state_prof.items():
        by_state.setdefault(st, {})[pr] = n
    for st, pr_map in sorted(by_state.items()):
        items = sorted(pr_map.items(), key=lambda kv: -kv[1])
        print(f"{st}: {len(pr_map)} professions reached")
        for pr, n in items[:6]:
            print(f"   {pr:30}  {n:>4} sections")
        if len(items) > 6:
            print(f"   ...+{len(items)-6} more")


if __name__ == "__main__":
    main()
