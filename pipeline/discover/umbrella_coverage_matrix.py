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
from scope_sources import CLASSIFIED_SOURCES, professions_for  # noqa: E402

UMBRELLA_SCOPE_DIR = RESULTS_DIR / "umbrella_scope"


def _all_professions() -> list[str]:
    return sorted(p.stem for p in PROFESSION_INDEX_DIR.glob("*.json"))


def coverage_summary(state: str) -> dict | None:
    """Per-state residual view: how many umbrella sections the pipeline scoped
    confidently vs. how many remain undetermined (the 'needs-a-human' residual).

    This is the reliable detector of where automation didn't reach — it counts
    every section in the scope file by scope_source, so the undetermined tail
    is visible rather than silently dropped.
    """
    scope_path = UMBRELLA_SCOPE_DIR / f"{state}.json"
    if not scope_path.exists():
        return None
    data = json.loads(scope_path.read_text())
    by_source: dict[str, int] = {}
    for entry in data.get("sections", []):
        src = entry.get("scope_source") or "undetermined"
        by_source[src] = by_source.get(src, 0) + 1
    total = sum(by_source.values())
    classified = sum(by_source.get(s, 0) for s in CLASSIFIED_SOURCES)
    undetermined = by_source.get("undetermined", 0)
    return {
        "state": state,
        "total_sections": total,
        "classified": classified,
        "undetermined": undetermined,
        "pct_classified": round(100 * classified / total, 1) if total else 0.0,
        "by_source": by_source,
    }


def matrix_for_state(state: str) -> list[dict]:
    scope_path = UMBRELLA_SCOPE_DIR / f"{state}.json"
    if not scope_path.exists():
        return []
    data = json.loads(scope_path.read_text())
    profs = _all_professions()
    rows: list[dict] = []
    for entry in data.get("sections", []):
        src = entry.get("scope_source")
        # undetermined → professions_for returns None → no rows for this section
        applicable = professions_for(src, entry.get("applies_to_professions"), profs) or []
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

    # Residual / coverage summary — the "what's still unresolved" detector.
    summaries = [s for s in (coverage_summary(st) for st in states) if s]
    summary_out = PROFESSION_INDEX_DIR / "_umbrella_coverage_summary.csv"
    if summaries:
        with summary_out.open("w", newline="") as f:
            w = csv.DictWriter(
                f, fieldnames=["state", "total_sections", "classified", "undetermined", "pct_classified"]
            )
            w.writeheader()
            for s in summaries:
                w.writerow({k: s[k] for k in w.fieldnames})

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

    # Coverage / residual table — confident vs. undetermined per state.
    if summaries:
        print(f"\nCoverage summary (wrote {summary_out.name}):")
        tot_all = sum(s["total_sections"] for s in summaries)
        cls_all = sum(s["classified"] for s in summaries)
        und_all = sum(s["undetermined"] for s in summaries)
        print(f"  {'state':5} {'total':>6} {'classified':>11} {'undetermined':>13} {'%cls':>6}")
        for s in sorted(summaries, key=lambda x: x["pct_classified"]):
            print(f"  {s['state']:5} {s['total_sections']:>6} {s['classified']:>11} "
                  f"{s['undetermined']:>13} {s['pct_classified']:>5}%")
        pct_all = round(100 * cls_all / tot_all, 1) if tot_all else 0.0
        print(f"  {'ALL':5} {tot_all:>6} {cls_all:>11} {und_all:>13} {pct_all:>5}%")


if __name__ == "__main__":
    main()
