"""Stage similarity/outlier analysis for the frontend.

Mirrors results/analysis/<prof>.json -> web/public/data/analysis/<prof>.json (baked
into the Next build) AND uploads to Blob at data/analysis/<prof>.json — exactly how
build_frontend ships the profession payloads, so the Compare tab's fetch resolves
whether the site serves /data from the build or from Blob.

Usage:
  python -m pipeline.analyze.publish_analysis            # all analyzed professions
  python -m pipeline.analyze.publish_analysis --professions optometry,dietetics
  python -m pipeline.analyze.publish_analysis --no-upload   # local mirror only (dev)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from pipeline.paths import WEB_DATA_DIR

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "pipeline" / "results" / "analysis"
DST = WEB_DATA_DIR / "analysis"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", help="comma-separated; default = all in results/analysis")
    ap.add_argument("--no-upload", action="store_true", help="local public/data mirror only (skip Blob)")
    args = ap.parse_args()
    DST.mkdir(parents=True, exist_ok=True)
    profs = (
        [p.strip().lower() for p in args.professions.split(",")]
        if args.professions
        else [p.stem for p in sorted(SRC.glob("*.json"))]
    )
    upload_json = None
    if not args.no_upload:
        try:
            from pipeline.publish.blob_upload import upload_json  # noqa: E402
        except Exception as e:  # noqa: BLE001
            print(f"  (blob upload unavailable: {e} — staging local mirror only)")
    n = up = 0
    for p in profs:
        src = SRC / f"{p}.json"
        if not src.exists():
            print(f"  skip {p}: no analysis (run pipeline.analyze.similarity --json)")
            continue
        body = src.read_text()
        (DST / f"{p}.json").write_text(body)
        n += 1
        if upload_json:
            try:
                _url, skipped = upload_json(f"data/analysis/{p}.json", body)
                up += 0 if skipped else 1
            except Exception as e:  # noqa: BLE001
                print(f"  blob upload failed for {p}: {e}")
    print(f"staged {n} analysis files -> {DST}" + (f"; uploaded {up} to Blob" if upload_json else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
