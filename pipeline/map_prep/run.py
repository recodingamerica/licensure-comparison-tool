"""Two-pass LLM normalization so a profession's structured fields become
mappable across all states.

Pass 1 (spec): looks at every field and its raw values across all states for
one profession, decides which fields are mappable (continuous / categorical /
not_mappable) and emits a normalization spec — units for continuous fields,
the normalized category set for categorical fields.

Pass 2 (apply): given that spec plus the raw values, emits a flat list of
(field, state, raw_value, normalized) rows. Numbers are in the spec's unit;
categories are one of the spec's category strings; nulls preserved.

Outputs land in pipeline/results/map_prep/<profession>/{spec.json, normalized.json}.

Run:
    python -m pipeline.map_prep.run podiatry
"""

from __future__ import annotations

import argparse
import json
import logging
from typing import Literal

from pydantic import BaseModel, Field

# Make the pipeline package importable when invoked as a script.

from pipeline._env import load_env
from pipeline._llm import call_structured
from pipeline._prompts import load_prompt
from pipeline.paths import STRUCTURED_DIR as _STRUCTURED_DIR, MAP_PREP_DIR as _OUT_ROOT

load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("map_prep")

_REPO_ROOT = _PIPELINE_DIR.parent

MODEL = "claude-sonnet-4-6"


# ---------- Pass 1: spec ----------

class FieldSpec(BaseModel):
    field_name: str = Field(description="Dotted path, e.g. 'licensure.age_minimum'")
    mappable: bool
    kind: Literal["continuous", "categorical", "not_mappable"]
    unit: str | None = Field(
        default=None,
        description="For continuous fields only: short unit phrase ('years', 'hours per renewal period', 'USD').",
    )
    categories: list[str] | None = Field(
        default=None,
        description="For categorical fields only: normalized category labels (snake_case).",
    )
    reason: str


class SpecResult(BaseModel):
    profession: str
    fields: list[FieldSpec]


# ---------- Pass 2: apply ----------

class NormalizedRow(BaseModel):
    field_name: str
    state: str
    raw_value: str | None = Field(
        default=None,
        description=(
            "Short string of original value, for audit. Null is allowed but "
            "STRONGLY DISCOURAGED — if a state has no raw value for this "
            "field, omit the row entirely rather than emitting one with "
            "null raw_value."
        ),
    )
    normalized: float | str | None = Field(
        description=(
            "Number for continuous fields, category string for categorical, "
            "null if the state didn't address the field OR the raw value is "
            "too ambiguous to land on the spec's scale. No hedging — emit "
            "null rather than a guess."
        )
    )


class ApplyResult(BaseModel):
    profession: str
    rows: list[NormalizedRow]


# ---------- Helpers ----------

def _flatten_evidence(record: dict) -> dict:
    """Pull `.value` out of every Evidence-shaped leaf, keep dotted paths.

    Result: {dotted_field_name: value}, with None values dropped. We drop
    nulls deliberately — they otherwise leak parent-container paths into
    the spec pass (e.g. when a state's whole `continuing_education` block
    is null, the walker would emit `licensure.continuing_education = None`
    alongside the real leaf fields). The apply prompt tells the LLM to
    emit null for any state missing a value, so dropping at the input
    side loses no information.
    """
    out: dict[str, object] = {}

    def walk(node, prefix: str) -> None:
        if isinstance(node, dict):
            # Evidence carrier? Detect by the value/quote/citation signature
            # alone — NOT by key count. Verified records carry extra annotation
            # keys (`unverified`, `approximate.{ratio,matched_normalized}`) on
            # the same node; an earlier `len(node) <= 4` cap rejected those,
            # so the walker descended and leaked `<field>.value`,
            # `<field>.approximate.ratio`, etc. as bogus fields. Any node
            # carrying all three keys is an Evidence leaf by schema invariant.
            if node.keys() >= {"value", "quote", "citation"}:
                val = node.get("value")
                if val is not None:
                    out[prefix] = val
                return
            for k, v in node.items():
                if k == "citations":
                    continue  # not useful for mapping
                child = f"{prefix}.{k}" if prefix else k
                walk(v, child)
        elif isinstance(node, list):
            # Don't descend into list[Citation] / list[Exam] structures here —
            # the spec pass only handles scalar fields. Lists of strings (e.g.
            # methods_authorized) are passed through as-is.
            if all(isinstance(x, str) for x in node):
                out[prefix] = node
        else:
            if node is None:
                return
            if prefix and prefix not in ("state", "profession"):
                out[prefix] = node

    walk(record, prefix="")
    return out


def _load_profession(profession: str) -> dict[str, dict]:
    """Return {state: flat_field_map} for every state JSON under structured/<profession>/."""
    src_dir = _STRUCTURED_DIR / profession
    if not src_dir.is_dir():
        raise FileNotFoundError(f"no structured data for profession {profession!r} at {src_dir}")
    out: dict[str, dict] = {}
    for path in sorted(src_dir.glob("*.json")):
        state = path.stem
        # Skip non-state files (e.g. _summary.json aggregates).
        if not (len(state) == 2 and state.isupper() and state.isalpha()):
            continue
        record = json.loads(path.read_text())
        out[state] = _flatten_evidence(record)
    return out


def _field_index(per_state: dict[str, dict]) -> dict[str, dict[str, object]]:
    """Pivot to {field_name: {state: value, ...}} so the LLM sees per-field
    coverage at a glance."""
    index: dict[str, dict[str, object]] = {}
    for state, fields in per_state.items():
        for field, value in fields.items():
            index.setdefault(field, {})[state] = value
    return index


# ---------- Main flow ----------

def build_spec(profession: str, per_field: dict[str, dict[str, object]]) -> SpecResult:
    system = load_prompt("map_prep_spec")
    user = json.dumps({"profession": profession, "fields": per_field}, ensure_ascii=False)
    log.info("[%s] pass-1 spec: %d fields, %d bytes user input",
             profession, len(per_field), len(user))
    result = call_structured(
        model=MODEL,
        system=system,
        user=user,
        schema_cls=SpecResult,
        max_tokens=16000,
        log_prefix=f"[{profession} spec]",
        logger=log,
    )
    if result is None:
        raise RuntimeError(f"pass-1 spec call failed for {profession}")
    return result


APPLY_CHUNK_SIZE = 10  # mappable fields per apply call; tuned so output stays under 32k tokens.


def apply_spec(profession: str, spec: SpecResult, per_field: dict[str, dict[str, object]]) -> ApplyResult:
    mappable_specs = [s for s in spec.fields if s.mappable and s.kind != "not_mappable"]
    system = load_prompt("map_prep_apply")
    all_rows: list[NormalizedRow] = []

    for i in range(0, len(mappable_specs), APPLY_CHUNK_SIZE):
        chunk = mappable_specs[i : i + APPLY_CHUNK_SIZE]
        chunk_names = {s.field_name for s in chunk}
        trimmed = {fn: per_field[fn] for fn in chunk_names if fn in per_field}
        payload = {
            "profession": profession,
            "spec": [s.model_dump() for s in chunk],
            "raw_values": trimmed,
        }
        user = json.dumps(payload, ensure_ascii=False)
        log.info("[%s] pass-2 apply chunk %d/%d: %d fields, %d bytes",
                 profession, i // APPLY_CHUNK_SIZE + 1,
                 (len(mappable_specs) + APPLY_CHUNK_SIZE - 1) // APPLY_CHUNK_SIZE,
                 len(chunk), len(user))
        result = call_structured(
            model=MODEL,
            system=system,
            user=user,
            schema_cls=ApplyResult,
            max_tokens=32000,
            log_prefix=f"[{profession} apply {i//APPLY_CHUNK_SIZE + 1}]",
            logger=log,
        )
        if result is None:
            raise RuntimeError(f"pass-2 apply chunk {i//APPLY_CHUNK_SIZE + 1} failed for {profession}")
        all_rows.extend(result.rows)

    return ApplyResult(profession=profession, rows=all_rows)


def main() -> int:
    global MODEL
    ap = argparse.ArgumentParser()
    ap.add_argument("profession", help="e.g. podiatry")
    ap.add_argument("--model", default=MODEL, help=f"override model (default {MODEL})")
    ap.add_argument("--refresh-spec", action="store_true",
                    help="rebuild spec.json even if it exists")
    args = ap.parse_args()
    MODEL = args.model

    per_state = _load_profession(args.profession)
    per_field = _field_index(per_state)
    log.info("[%s] loaded %d states, %d unique fields",
             args.profession, len(per_state), len(per_field))

    out_dir = _OUT_ROOT / args.profession
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_path = out_dir / "spec.json"
    if spec_path.exists() and not args.refresh_spec:
        spec = SpecResult.model_validate_json(spec_path.read_text())
        log.info("[%s] reusing existing spec.json (%d fields, %d mappable)",
                 args.profession, len(spec.fields),
                 sum(1 for s in spec.fields if s.mappable))
    else:
        spec = build_spec(args.profession, per_field)
        spec_path.write_text(spec.model_dump_json(indent=2))
        log.info("[%s] wrote spec.json (%d fields, %d mappable)",
                 args.profession, len(spec.fields),
                 sum(1 for s in spec.fields if s.mappable))

    applied = apply_spec(args.profession, spec, per_field)
    (out_dir / "normalized.json").write_text(applied.model_dump_json(indent=2))
    log.info("[%s] wrote normalized.json (%d rows)", args.profession, len(applied.rows))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
