"""Cross-profession harmonization of universal text-bucket fields (#16).

`bucket_text.py` buckets each free-text field ONE PROFESSION AT A TIME, so a
universal field like `licensure.issuing_authority` gets a different label set
per profession ("State Health Dept" for dietetics vs "Health Department" for
podiatry vs "State Dept / Agency" for dentistry). Same real-world thing, three
labels — so the chips can't be compared across professions, and you can't ask
"which states use a dedicated profession board vs. a general health/licensing
dept across ALL professions?"

This pass takes a fixed list of genuinely-universal fields, gathers EVERY
profession's per-state raw values for each (reusing the per-profession
text_buckets.json that bucket_text already produced — no re-reading structured/),
and makes ONE LLM call per field that emits a SINGLE profession-independent
bucket set and assigns every (profession, state) cell through it.

`build_frontend` then overrides the per-profession buckets for these fields with
the harmonized assignment (see `_apply_harmonized` there), so the table chips
line up across professions. Non-harmonized fields keep their per-profession
buckets untouched.

Output: results/map_prep/_harmonized/universal_buckets.json
  {
    "fields": [
      {"field_name": "licensure.issuing_authority",
       "bucket_set": ["Profession-Specific Board", "Shared Medical/Allied Board", ...],
       "rationale": "...",
       "by_profession": {"podiatry": {"AK": "Shared Medical/Allied Board", ...}, ...}}
    ]
  }

Run:
  python -m pipeline.map_prep.harmonize_universal                 # default field set
  python -m pipeline.map_prep.harmonize_universal --fields licensure.issuing_authority
"""
from __future__ import annotations

import argparse
import json
import logging

from pydantic import BaseModel, Field


from pipeline._env import load_env
from pipeline._llm import call_structured
from pipeline._prompts import load_prompt
from pipeline.paths import MAP_PREP_DIR as _OUT_ROOT
from pipeline.config.loaders import model_for

load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("harmonize_universal")

_HARMONIZED_DIR = _OUT_ROOT / "_harmonized"
MODEL = model_for("map_prep")

# Universal fields whose concept is genuinely profession-INDEPENDENT, so a single
# shared bucket set is meaningful. Each entry carries a short concept hint that
# steers the model toward the cross-profession dimension. Deliberately EXCLUDES
# fields that are inherently profession-specific (degree names — DDS/MD/DPM —,
# scope.methods_authorized, drug_authority): forcing those into shared buckets
# would be lossy. Extend by adding entries here; cost is one LLM call per field.
HARMONIZE_FIELDS: dict[str, str] = {
    "licensure.issuing_authority":
        "The state body that issues/administers the license. Group by the TYPE "
        "of body, profession-independently: a board dedicated to THIS profession; "
        "a board shared with a related profession (e.g. a medical or allied-health "
        "board); a general state health department; a general licensing / commerce "
        "/ regulation agency; or other.",
    "licensure.regulatory_authority.name":
        "The named regulating body for this profession — the same concept as "
        "issuing_authority. Use the same body-TYPE buckets: profession-specific "
        "board; board shared with a related profession; state health department; "
        "general licensing / commerce / regulation agency; or other.",
    "licensure.regulatory_authority.umbrella_agency":
        "The parent department the licensing board sits under. Group "
        "profession-independently by department TYPE: Health; Consumer Affairs; "
        "Commerce / Economic Development; Professional Licensing / Regulation "
        "Office; Labor; Secretary of State; or other.",
    "licensure.education.accrediting_body":
        "Who must accredit the applicant's school/program. Group by accreditor "
        "TYPE, profession-independently: a profession-specific national accreditor; "
        "a regional / institutional accreditor; a federal reference (US Dept of "
        "Education / CHEA); board discretion; or another named body.",
    "licensure.reciprocity.requirements":
        "What an out-of-state licensee must satisfy to be recognized. Group by the "
        "TYPE of requirement, profession-independently: substantially-equivalent "
        "standards; a years-of-practice threshold; an interstate compact pathway; "
        "exam equivalency; endorsement / fee only; or a strict multi-factor review.",
}


class _AssignmentLLM(BaseModel):
    profession: str
    state: str
    bucket: str | None = Field(
        description="One of bucket_set, or null if the value fits no bucket.",
    )


class _HarmonizedFieldLLM(BaseModel):
    field_name: str
    bucket_set: list[str] = Field(
        description="4-8 short PROFESSION-INDEPENDENT labels (never a single "
                    "profession's name). Render as chips."
    )
    rationale: str
    assignments: list[_AssignmentLLM]


def _collect_cross_profession(dotted: str) -> list[dict]:
    """Every profession's per-state raw values for `dotted`, from the
    per-profession text_buckets.json (the bucket_text pass already extracted
    them). Returns rows of {profession, state, raw_value}."""
    rows: list[dict] = []
    for tb_path in sorted(_OUT_ROOT.glob("*/text_buckets.json")):
        profession = tb_path.parent.name
        if profession.startswith("_"):
            continue
        data = json.loads(tb_path.read_text())
        entry = next((e for e in data.get("fields", []) if e["field_name"] == dotted), None)
        if entry is None:
            continue
        for a in entry.get("assignments", []):
            raw = a.get("raw_value")
            if not raw:
                continue
            rows.append({"profession": profession, "state": a["state"], "raw_value": str(raw)[:600]})
    return rows


def harmonize_field(dotted: str, concept: str) -> dict | None:
    rows = _collect_cross_profession(dotted)
    professions = sorted({r["profession"] for r in rows})
    if len(professions) < 2:
        log.info("%s: only %d profession(s) have this field — nothing to harmonize", dotted, len(professions))
        return None
    log.info("%s: %d values across %d professions → asking %s",
             dotted, len(rows), len(professions), MODEL)
    system = load_prompt("map_prep_harmonize_universal")
    user = json.dumps({
        "field_name": dotted,
        "field_meaning": concept,
        "professions": professions,
        "per_profession_state_raw_values": rows,
    }, ensure_ascii=False)
    # Output is one terse {profession, state, bucket} per row (~350 rows for a
    # 7-profession field); give a generous ceiling so it never truncates.
    result = call_structured(
        model=MODEL,
        system=system,
        user=user,
        schema_cls=_HarmonizedFieldLLM,
        embed_schema=True,
        # One {profession, state, bucket} object per row, and the widest fields span
        # ~38 professions x 50 states ~= 1900 rows ~= 50k tokens. 16000 was NOT a
        # generous ceiling: on 2026-08-01 and again 08-03 every call returned exactly
        # 16000 output tokens and died on unterminated JSON (#127).
        max_tokens=64000,
        max_retries=2,
        temperature=None,
        log_prefix=f"[harmonize/{dotted}]",
        logger=log,
    )
    if result is None:
        return None
    by_profession: dict[str, dict[str, str]] = {}
    for a in result.assignments:
        if a.bucket is None:
            continue
        by_profession.setdefault(a.profession, {})[a.state] = a.bucket
    return {
        "field_name": result.field_name,
        "bucket_set": result.bucket_set,
        "rationale": result.rationale,
        "by_profession": by_profession,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fields", nargs="+", default=list(HARMONIZE_FIELDS),
                    help="Dotted field names to harmonize (default: all in HARMONIZE_FIELDS)")
    args = ap.parse_args()

    _HARMONIZED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = _HARMONIZED_DIR / "universal_buckets.json"

    # Start from what's already on disk and REPLACE only what this run harmonized.
    # Writing just this run's fields meant `--fields a b` deleted every other field,
    # and a run where every field failed wrote an empty file — which is how the
    # 2026-08-01 run silently shrank 5 fields to 3, and an 08-03 re-run of 2 fields
    # took it to 0 (#127).
    existing: dict[str, dict] = {}
    if out_path.exists():
        try:
            for f in (json.loads(out_path.read_text()).get("fields") or []):
                if f.get("field_name"):
                    existing[f["field_name"]] = f
        except Exception:
            log.warning("could not read existing %s — starting fresh", out_path)

    failed = []
    for dotted in args.fields:
        concept = HARMONIZE_FIELDS.get(dotted, "")
        if not concept:
            log.warning("%s not in HARMONIZE_FIELDS — using empty concept hint", dotted)
        res = harmonize_field(dotted, concept)
        if res is None:
            failed.append(dotted)
            if dotted in existing:
                log.error("%s FAILED — keeping the previously harmonized version", dotted)
            else:
                log.error("%s FAILED and has no previous version — it will be absent", dotted)
            continue
        existing[dotted] = res
        log.info("%s → %d buckets: %s", dotted, len(res["bucket_set"]), res["bucket_set"])

    # Preserve HARMONIZE_FIELDS order for a stable diff, then any extras.
    order = [f for f in HARMONIZE_FIELDS if f in existing]
    order += [f for f in existing if f not in order]
    fields_out = [existing[f] for f in order]

    out_path.write_text(json.dumps({"fields": fields_out}, indent=2, ensure_ascii=False))
    log.info("wrote %s — %d field(s) total, %d harmonized this run, %d failed%s",
             out_path, len(fields_out), len(args.fields) - len(failed), len(failed),
             f" ({', '.join(failed)})" if failed else "")
    # Non-zero so the runner cannot report `ok` on a partial harmonize.
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
