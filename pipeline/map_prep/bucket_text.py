"""Pass 3 — bucket the FREE-TEXT fields that the original `map_prep` pass
left `not_mappable`.

Pass 1 of map_prep.run decides each field is continuous / categorical /
not_mappable. Categorical + continuous fields are normalized for the
choropleth. not_mappable fields (free-text idiosyncratic prose like
"education.degree_required" or "issuing_authority") got skipped — which
makes the per-state table cells unreadable: 50 distinct walls of statute
text in a column with no cross-state pattern.

This pass relaxes the bucketing constraint. We don't need a perfectly
comparable scale — we just need a loose categorization so the user can
scan the column and group similar states at a glance. Output buckets
are usually 3-7 labels per field, derived from the actual values seen.

Output: pipeline/results/map_prep/<profession>/text_buckets.json
Shape:
    {
      "profession": "podiatry",
      "fields": [
         {
           "field_name": "licensure.education.degree_required",
           "bucket_set": ["Doctor of Podiatric Medicine", "DPM or equivalent", "..."],
           "rationale": "Most states say DPM; a few use broader 'medical degree' phrasing.",
           "assignments": [
             {"state": "AL", "raw_value": "Doctor of Podiatry from...", "bucket": "Doctor of Podiatric Medicine"},
             ...
           ]
         },
         ...
      ]
    }

Run:
    python -m pipeline.map_prep.bucket_text podiatry
    python -m pipeline.map_prep.bucket_text --all
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from pydantic import BaseModel, Field

# Same path setup pattern as run.py
_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from _env import load_env  # noqa: E402
from _llm import call_structured  # noqa: E402
from _prompts import load_prompt  # noqa: E402

load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bucket_text")

_OUT_ROOT = _PIPELINE_DIR / "results" / "map_prep"
_STRUCTURED_DIR = _PIPELINE_DIR / "results" / "structured"

MODEL = "claude-sonnet-4-6"


class BucketAssignment(BaseModel):
    state: str
    raw_value: str
    bucket: str | None = Field(
        description="One of bucket_set, or null if the state's value doesn't fit any bucket.",
    )


class FieldBuckets(BaseModel):
    field_name: str
    bucket_set: list[str] = Field(
        description=(
            "3-7 short labels covering the value distribution. Snake-case-or-Title-Case "
            "is fine — prefer concise human-readable phrases ('Doctorate degree', "
            "'Single state board') over jargon."
        ),
    )
    rationale: str
    assignments: list[BucketAssignment]


def _resolve_field(rec: dict, dotted: str):
    """Walk dotted path into a structured record. Returns None if missing/empty."""
    cur = rec
    for seg in dotted.split("."):
        if not isinstance(cur, dict) or seg not in cur:
            return None
        cur = cur[seg]
    # Evidence-wrapped values: pull the actual value
    if isinstance(cur, dict) and "value" in cur:
        return cur.get("value")
    return cur


def _collect_per_state(profession: str, dotted: str) -> list[dict]:
    out = []
    prof_dir = _STRUCTURED_DIR / profession
    if not prof_dir.exists():
        return out
    for f in sorted(prof_dir.glob("*.json")):
        if f.stem.startswith("_"):
            continue  # _summary.json and similar are not per-state
        rec = json.loads(f.read_text())
        if not isinstance(rec, dict):
            continue
        state = rec.get("state") or f.stem
        v = _resolve_field(rec, dotted)
        if v is None or v == "" or v == []:
            continue
        if isinstance(v, list):
            v = "; ".join(str(x) for x in v if x)
        out.append({"state": state, "raw_value": str(v)[:600]})
    return out


def bucket_one_field(profession: str, dotted: str, raw_per_state: list[dict]) -> FieldBuckets | None:
    if len(raw_per_state) < 2:
        log.info("[%s] %s: only %d states with values — skipping", profession, dotted, len(raw_per_state))
        return None
    system = load_prompt("map_prep_bucket_text")
    user = json.dumps({
        "profession": profession,
        "field_name": dotted,
        "per_state_raw_values": raw_per_state,
    }, ensure_ascii=False)
    log.info("[%s] %s: %d states → asking %s", profession, dotted, len(raw_per_state), MODEL)
    result = call_structured(
        model=MODEL,
        system=system,
        user=user,
        schema_cls=FieldBuckets,
        embed_schema=True,
        max_tokens=4000,
        max_retries=2,
        temperature=None,
        log_prefix=f"[{profession}/{dotted}]",
        logger=log,
    )
    return result


def run_profession(profession: str) -> None:
    spec_path = _OUT_ROOT / profession / "spec.json"
    if not spec_path.exists():
        log.warning("[%s] no map_prep spec.json — run `python -m pipeline.map_prep.run %s` first",
                    profession, profession)
        return
    spec = json.loads(spec_path.read_text())
    not_mappable = [f["field_name"] for f in spec["fields"] if f.get("kind") == "not_mappable"]
    log.info("[%s] %d not_mappable fields to bucket", profession, len(not_mappable))

    field_results: list[FieldBuckets] = []
    for dotted in not_mappable:
        raw = _collect_per_state(profession, dotted)
        result = bucket_one_field(profession, dotted, raw)
        if result is not None:
            field_results.append(result)

    out_path = _OUT_ROOT / profession / "text_buckets.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "profession": profession,
        "fields": [r.model_dump() for r in field_results],
    }, indent=2, ensure_ascii=False))
    log.info("[%s] wrote %s — %d fields bucketed", profession, out_path.name, len(field_results))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("profession", nargs="?", help="single profession (omit + use --all)")
    ap.add_argument("--all", action="store_true", help="process every profession with a spec.json")
    args = ap.parse_args()

    if args.all:
        for p in sorted(_OUT_ROOT.iterdir()):
            if p.is_dir() and (p / "spec.json").exists():
                run_profession(p.name)
        return
    if not args.profession:
        ap.error("provide a profession or --all")
    run_profession(args.profession)


if __name__ == "__main__":
    main()
