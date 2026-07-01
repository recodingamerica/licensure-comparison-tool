"""Turn config/verified_absences.yaml into structured records.

A verified absence is a (profession, state) that hand-verified research confirmed has
NO state license (regulated locally, or not at all). It is a correct-blank, not a data
gap. Rather than invent a new "blank" concept, we emit a normal structured record with
`regulatory_model = market_forces` — the pipeline's existing "no state regulation" value
(same as an extracted market_forces state) — so the frontend renders it without any
special-casing.

The records are transparently marked `source: verified_absence` with the research
`basis`/`note`/`citation`, so they are never confused with statute-grounded extractions
and the evidence-verifier can skip quote-grounding them (their quotes are intentionally
empty — there is no state statute to quote).

Writes results/structured/<profession>/<state>.json (skips ones that already have a
real extracted record unless --force).

Usage:
  python -m pipeline.extract.apply_verified_absences            # all
  python -m pipeline.extract.apply_verified_absences --profession electrician
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

import yaml  # noqa: E402

from paths import CONFIG_DIR, STRUCTURED_DIR  # noqa: E402
from _runlog import record_run  # noqa: E402

MANIFEST = CONFIG_DIR / "verified_absences.yaml"


def _ev(value, citation: str):
    # An Evidence object with an intentionally empty quote: a verified absence has
    # no state statute to quote; the provenance lives in the record's source/basis.
    return {"value": value, "quote": "", "citation": citation}


def make_record(profession: str, state: str, spec: dict) -> dict:
    cit = spec.get("citation", "") or ""
    return {
        "state": state,
        "profession": profession,
        "source": "verified_absence",
        "basis": spec.get("basis", "local_only"),
        "note": spec.get("note", ""),
        "licensure": {
            "license_required": _ev(False, cit),
            "regulatory_model": _ev("market_forces", cit),
            "credential_type": _ev("none", cit),
            "is_mandatory": _ev(False, cit),
        },
        "scope": {},
        "profession_specific": {},
    }


def _is_extracted(path: Path) -> bool:
    """True if a real extracted record already sits here (don't clobber it)."""
    if not path.exists():
        return False
    try:
        return json.loads(path.read_text()).get("source") != "verified_absence"
    except Exception:
        return True


def apply(only_profession: str | None, force: bool) -> int:
    manifest = yaml.safe_load(MANIFEST.read_text()) or {}
    written = skipped = 0
    for profession, states in manifest.items():
        if only_profession and profession != only_profession:
            continue
        out_dir = STRUCTURED_DIR / profession
        out_dir.mkdir(parents=True, exist_ok=True)
        for state, spec in (states or {}).items():
            out = out_dir / f"{state}.json"
            if _is_extracted(out) and not force:
                print(f"  skip {profession}/{state} — real extracted record present (use --force)")
                skipped += 1
                continue
            out.write_text(json.dumps(make_record(profession, state, spec), indent=2, ensure_ascii=False))
            written += 1
    print(f"verified absences: wrote {written}, skipped {skipped}")
    record_run("verified_absences", written=written)
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profession")
    ap.add_argument("--force", action="store_true", help="overwrite even a real extracted record")
    args = ap.parse_args()
    apply(args.profession, args.force)


if __name__ == "__main__":
    main()
