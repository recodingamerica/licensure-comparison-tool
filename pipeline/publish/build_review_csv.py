"""Per-profession CSV for reviewer markup.

Walks the Evidence-shaped leaves in each state's structured record and emits
one row per (state, field, value, quote, citation, verified, reviewer_notes).
Long format is reviewer-friendly: notes attach to specific (state, field)
pairs, and the reviewer can sort/filter on field path or state.

Output: pipeline/results/reviews/<YYYY-MM-DD>/<profession>.csv

Usage:
  python -m pipeline.publish.build_review_csv --profession podiatry
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from extract.standard_model import iter_evidence  # noqa: E402
from paths import STRUCTURED_DIR, RESULTS_DIR  # noqa: E402
from _records import record_files  # noqa: E402

REVIEWS_DIR = RESULTS_DIR / "reviews"


def _format_path(path: tuple[str | int, ...]) -> str:
    """Render the tuple path as a dotted string with `[i]` for list indices."""
    parts: list[str] = []
    for p in path:
        if isinstance(p, int):
            parts.append(f"[{p}]")
        else:
            parts.append(("." if parts else "") + p)
    return "".join(parts)


def format_value(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return str(v)


def build_rows(structured_record: dict) -> list[dict]:
    state = structured_record.get("state", "?")
    rows = []
    for raw_path, ev in iter_evidence(structured_record):
        path = _format_path(raw_path)
        rows.append({
            "state": state,
            "field": path,
            "value": format_value(ev.get("value")),
            "quote": ev.get("quote", ""),
            "citation": ev.get("citation", ""),
            "verified": "no" if ev.get("unverified") else "yes",
            "reviewer_notes": "",
        })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--out-dir", default="",
                    help="Override output dir; default = results/reviews/<today>/")
    args = ap.parse_args()

    profession = args.profession.lower()
    src_dir = STRUCTURED_DIR / profession
    if not src_dir.exists():
        sys.exit(f"no structured data at {src_dir}")

    out_dir = Path(args.out_dir) if args.out_dir else REVIEWS_DIR / date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{profession}.csv"

    all_rows: list[dict] = []
    for f in record_files(src_dir):
        rec = json.loads(f.read_text())
        all_rows.extend(build_rows(rec))

    if not all_rows:
        sys.exit("no rows to write")

    with out_path.open("w", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=[
            "state", "field", "value", "quote", "citation", "verified", "reviewer_notes",
        ])
        w.writeheader()
        w.writerows(all_rows)

    states = sorted({r["state"] for r in all_rows})
    fields = sorted({r["field"] for r in all_rows})
    unverified = sum(1 for r in all_rows if r["verified"] == "no")
    print(f"wrote {out_path}")
    print(f"  rows: {len(all_rows)}")
    print(f"  states: {len(states)}")
    print(f"  distinct field paths: {len(fields)}")
    print(f"  unverified evidence: {unverified}")


if __name__ == "__main__":
    main()
