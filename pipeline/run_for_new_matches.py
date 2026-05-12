"""After expand_hierarchy + match_profession, run pull → clean → trim →
extract → publish for any (state, profession) pairs that newly matched.

Reads coverage diff between /tmp/coverage_before.csv (snapshot before
expand) and results/profession_index/_coverage.csv (after). For each
profession that gained states, runs the full ingestion + extraction
pipeline only on the newly-matched states, then publishes.

Usage:
  python -m pipeline.run_for_new_matches --profession public_accountancy
  python -m pipeline.run_for_new_matches --profession public_accountancy --deploy
  python -m pipeline.run_for_new_matches  # all professions that gained
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PIPELINE = Path(__file__).resolve().parent

sys.path.insert(0, str(PIPELINE))
from paths import RESULTS_DIR  # noqa: E402

BEFORE_PATH = Path("/tmp/coverage_before.csv")
AFTER_PATH = RESULTS_DIR / "profession_index" / "_coverage.csv"


def parse_coverage(path: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    with path.open() as f:
        for row in csv.DictReader(f):
            out[row["profession"]] = set(row.get("missing_states", "").split(",")) - {""}
    return out


def new_matches() -> dict[str, list[str]]:
    """{profession: [newly-matched state codes]}"""
    before = parse_coverage(BEFORE_PATH) if BEFORE_PATH.exists() else {}
    after = parse_coverage(AFTER_PATH)
    out = {}
    for prof, after_missing in after.items():
        before_missing = before.get(prof, set())
        newly = sorted(before_missing - after_missing)
        if newly:
            out[prof] = newly
    return out


def run(cmd: list[str]) -> None:
    print(f"\n$ {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=REPO_ROOT)
    if r.returncode != 0:
        sys.exit(f"command failed: {' '.join(cmd)}")


def run_pipeline_for(profession: str, states: list[str], deploy: bool) -> None:
    print(f"\n=== {profession}: pulling {len(states)} new states: {','.join(states)} ===")
    state_arg = ",".join(states)
    pyexe = str(REPO_ROOT / "pipeline" / ".venv" / "bin" / "python")
    run([pyexe, "-m", "pipeline.ingest.pull_text", "--profession", profession, "--states", state_arg])
    run([pyexe, "-m", "pipeline.ingest.clean_text", "--profession", profession])
    run([pyexe, "-m", "pipeline.ingest.trim_state", "--profession", profession, "--states", state_arg])
    run([pyexe, "-m", "pipeline.extract.extract_state", "--profession", profession, "--states", state_arg])
    publish_args = [pyexe, "-m", "pipeline.publish.build_frontend", "--profession", profession]
    if deploy:
        publish_args.append("--deploy")
    run(publish_args)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="", help="Limit to one profession; default = all that gained")
    ap.add_argument("--deploy", action="store_true", help="Redeploy Vercel after publish")
    ap.add_argument("--dry-run", action="store_true", help="Just print what would run")
    args = ap.parse_args()

    new = new_matches()
    if not new:
        print("No new matches detected — nothing to do.")
        return

    if args.profession:
        prof = args.profession.lower()
        if prof not in new:
            print(f"{prof} gained no new states — nothing to do.")
            return
        new = {prof: new[prof]}

    print("New matches per profession:")
    for prof, states in new.items():
        print(f"  {prof}: {len(states)} new ({','.join(states)})")

    if args.dry_run:
        return

    for prof, states in new.items():
        run_pipeline_for(prof, states, args.deploy)

    print("\nDone.")


if __name__ == "__main__":
    main()
