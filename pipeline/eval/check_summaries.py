"""Invariant: each results/<stage>/<profession>/_summary.json must have exactly
one row per committed corpus file in that directory.

This guards against the per-run-overwrite class of bug, where a `--states <subset>`
run rewrote `_summary.json` with only the run's states and dropped every other
state's row (PR #42's `--states PA` left all 7 published summaries PA-only).
`pull_text` now rebuilds the summary cumulatively from disk; this check fails
loudly if any code path ever reintroduces a stale summary.

Usage:
  pipeline/.venv/bin/python -m pipeline.eval.check_summaries          # all stages
  pipeline/.venv/bin/python -m pipeline.eval.check_summaries --stage text
Exit code 1 on any mismatch.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parents[1] / "results"
STAGES = ["text", "clean", "trimmed"]


def check_stage(stage: str) -> list[str]:
    """Return a list of human-readable problems for one stage dir (empty = clean)."""
    problems: list[str] = []
    stage_dir = RESULTS / stage
    if not stage_dir.exists():
        return problems
    for prof_dir in sorted(p for p in stage_dir.iterdir() if p.is_dir()):
        summary_path = prof_dir / "_summary.json"
        corpora = sorted(
            p.stem for p in prof_dir.glob("*.json") if not p.name.startswith("_")
        )
        if not summary_path.exists():
            if corpora:
                problems.append(f"{stage}/{prof_dir.name}: {len(corpora)} corpora but no _summary.json")
            continue
        try:
            rows = json.loads(summary_path.read_text())
            summary_states = sorted(r["state"] for r in rows)
        except Exception as e:  # noqa: BLE001
            problems.append(f"{stage}/{prof_dir.name}: unreadable _summary.json ({e})")
            continue
        if summary_states != corpora:
            missing = sorted(set(corpora) - set(summary_states))
            extra = sorted(set(summary_states) - set(corpora))
            detail = []
            if missing:
                detail.append(f"missing rows for {missing}")
            if extra:
                detail.append(f"rows with no corpus {extra}")
            problems.append(
                f"{stage}/{prof_dir.name}: summary has {len(summary_states)} rows "
                f"vs {len(corpora)} corpora — " + "; ".join(detail)
            )
    return problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=STAGES, help="Check only this stage (default: all)")
    args = ap.parse_args()

    stages = [args.stage] if args.stage else STAGES
    all_problems: list[str] = []
    for stage in stages:
        all_problems.extend(check_stage(stage))

    if all_problems:
        print(f"FAIL: {len(all_problems)} stale/inconsistent summaries:")
        for p in all_problems:
            print(f"  - {p}")
        sys.exit(1)
    print(f"OK: all _summary.json files match on-disk corpora ({', '.join(stages)})")


if __name__ == "__main__":
    main()
