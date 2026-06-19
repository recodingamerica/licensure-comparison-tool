"""Stage similarity/outlier analysis for the frontend.

Copies results/analysis/<prof>.json -> web/public/data/analysis/<prof>.json so the
Compare tab can fetch it (kept separate from the profession JSON so it doesn't
couple to the build_frontend / refresh_all publish path).

Usage:
  python -m pipeline.analyze.publish_analysis            # all analyzed professions
  python -m pipeline.analyze.publish_analysis --professions optometry,dietetics
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "pipeline" / "results" / "analysis"
DST = REPO / "pipeline" / "publish" / "web" / "public" / "data" / "analysis"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", help="comma-separated; default = all in results/analysis")
    args = ap.parse_args()
    DST.mkdir(parents=True, exist_ok=True)
    profs = (
        [p.strip().lower() for p in args.professions.split(",")]
        if args.professions
        else [p.stem for p in sorted(SRC.glob("*.json"))]
    )
    n = 0
    for p in profs:
        src = SRC / f"{p}.json"
        if not src.exists():
            print(f"  skip {p}: no analysis (run pipeline.analyze.similarity --json)")
            continue
        shutil.copyfile(src, DST / f"{p}.json")
        n += 1
        print(f"  staged {p}")
    print(f"staged {n} analysis files -> {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
