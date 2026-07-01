"""State similarity / novel models analysis (meeting Q5).

For a profession, compute how unusual each state's regulatory shape is and
which specific fields make it unusual. Approach: for each universal field,
count value frequencies across states; a state's "novelty score" is the sum
across fields of (1 / count_of_same_value_in_this_field). Rare values weigh
heavily, common values barely move the score.

Output: a markdown report per profession listing typical states and
outliers + which fields drove the outlier classification.

Usage:
  python -m pipeline.publish.state_similarity --profession podiatry
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from pipeline.paths import RESULTS_DIR

REPORTS_DIR = RESULTS_DIR / "similarity_reports"


# Universal fields used for similarity scoring. Coverage_gap / evidence_*
# excluded (orthogonal to regulatory shape).
SCORING_FIELDS = [
    "license_required",
    "regulatory_model",
    "title_protection",
    "scope_protection",
    "reciprocity_available",
    "exams_count",
    "renewal_years",
    "ce_hours",
    "ce_period_years",
    "disciplinary_grounds_count",
    "credential_type",
    "is_mandatory",
]


def _bucket(v: Any, field: str) -> Any:
    """Normalize values for bucketing. None → 'none', else as-is for cats;
    numerics get coarse-binned so '20' and '24' aren't always separate."""
    if v is None:
        return "none"
    if field in ("exams_count", "disciplinary_grounds_count"):
        return f"{(v // 5) * 5}-{(v // 5) * 5 + 4}" if isinstance(v, int) else str(v)
    if field == "ce_hours":
        return f"{(v // 10) * 10}-{(v // 10) * 10 + 9}" if isinstance(v, int) else str(v)
    return v


def score_state(row: dict, frequencies: dict[str, Counter]) -> tuple[float, list[tuple[str, Any, int]]]:
    """Return (novelty_score, [(field, value, count_of_states_sharing) ...])."""
    contributions: list[tuple[str, Any, int]] = []
    score = 0.0
    for field in SCORING_FIELDS:
        bucket = _bucket(row.get(field), field)
        count = frequencies[field].get(bucket, 1)
        contribution = 1.0 / count
        score += contribution
        contributions.append((field, bucket, count))
    return score, contributions


def analyze_profession(profession: str) -> dict:
    """Return per-state scores + a typical/novel breakdown."""
    web_data = Path(__file__).resolve().parent / "web" / "public" / "data" / f"{profession}.json"
    if not web_data.exists():
        sys.exit(f"no published data at {web_data}")
    d = json.loads(web_data.read_text())
    rows = [r for r in d["rows"] if not r.get("coverage_gap")]
    if len(rows) < 5:
        sys.exit(f"only {len(rows)} states covered — too few for similarity analysis")

    # Build frequency tables per field
    frequencies: dict[str, Counter] = {f: Counter() for f in SCORING_FIELDS}
    for r in rows:
        for f in SCORING_FIELDS:
            frequencies[f][_bucket(r.get(f), f)] += 1

    scored = []
    for r in rows:
        score, contributions = score_state(r, frequencies)
        scored.append({
            "state": r["state"],
            "score": score,
            "contributions": contributions,
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {
        "profession": profession,
        "display": d.get("display", profession),
        "n_states": len(rows),
        "frequencies": {f: dict(c) for f, c in frequencies.items()},
        "scored": scored,
    }


def write_report(result: dict, out_path: Path) -> None:
    lines: list[str] = []
    lines.append(f"# {result['display']} — state-similarity analysis")
    lines.append("")
    lines.append(
        f"Across {result['n_states']} covered states. Higher novelty score = unusual combination "
        f"of regulatory choices. Fields scored: {', '.join(SCORING_FIELDS)}."
    )
    lines.append("")

    # Top novel states — but flag data-quality outliers (many `none` buckets)
    lines.append("## Most novel models (outliers)")
    lines.append("")
    lines.append(
        "Reviewer note: if the rarest fields are all `none`, the state's outlier "
        "status reflects sparse extraction, not a genuinely unusual regulatory shape — "
        "look at evidence_verified count on the live site to confirm."
    )
    lines.append("")
    for entry in result["scored"][:5]:
        st = entry["state"]
        score = entry["score"]
        rare = sorted(entry["contributions"], key=lambda c: c[2])[:3]
        none_count = sum(1 for _, b, _ in rare if b == "none")
        flag = "  ⚠ likely data gap" if none_count >= 2 else ""
        lines.append(f"### {st}  (score {score:.2f}){flag}")
        lines.append("")
        lines.append("Rarest values driving the outlier classification:")
        for field, bucket, count in rare:
            lines.append(f"- **{field}** = `{bucket}`  ({count} of {result['n_states']} states share this)")
        lines.append("")

    # Most typical
    lines.append("## Most typical")
    lines.append("")
    typical = list(reversed(result["scored"][-5:]))
    for entry in typical:
        lines.append(f"- **{entry['state']}** — score {entry['score']:.2f}")
    lines.append("")

    # Field value distributions
    lines.append("## Field distributions")
    lines.append("")
    lines.append("How values cluster across states (typical = high count; outlier values appear only once or twice):")
    lines.append("")
    for field in SCORING_FIELDS:
        freq = result["frequencies"][field]
        most_common = sorted(freq.items(), key=lambda kv: -kv[1])
        items = ", ".join(f"`{k}` ({v})" for k, v in most_common)
        lines.append(f"- **{field}**: {items}")
    lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--out-dir", default="")
    args = ap.parse_args()
    profession = args.profession.lower()
    result = analyze_profession(profession)

    from datetime import date
    out_dir = Path(args.out_dir) if args.out_dir else REPORTS_DIR / date.today().isoformat()
    out_path = out_dir / f"{profession}.md"
    write_report(result, out_path)

    top_novel = result["scored"][:3]
    print(f"wrote {out_path}")
    print(f"n_states analyzed: {result['n_states']}")
    print("top 3 most novel:")
    for e in top_novel:
        print(f"  {e['state']} (score {e['score']:.2f})")


if __name__ == "__main__":
    main()
