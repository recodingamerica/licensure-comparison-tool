"""LLM pass: per-profession field importance + value closeness.

The math can't know which fields define a licensing regime, or how far apart two
categorical values are. This makes ONE cheap structured call per profession (the
cost is O(fields), not O(states*fields)) that, given each field and its observed
value set, returns:
  - importance  (0..1) — how much the field defines the regime, for THIS profession
  - closeness   — ordinal (with an order, low->high) or nominal

Output is written to config/field_semantics/<profession>.yaml — a reviewable,
hand-editable artifact, NOT a hidden score. pipeline.analyze.similarity layers it
over the universal baseline in config/field_semantics.yaml.

Usage:
  python -m pipeline.analyze.gen_semantics --profession optometry
  python -m pipeline.analyze.gen_semantics --professions optometry,dietetics,medicine
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

REPO = Path(__file__).resolve().parents[2]
from pipeline._env import load_env
load_env()
from pipeline._llm import call_structured
from pipeline.config.loaders import load_limits
from pipeline.config.loaders import model_for

log = logging.getLogger(__name__)

DATA_DIR = REPO / "pipeline" / "publish" / "web" / "public" / "data"
OUT_DIR = REPO / "pipeline" / "config" / "field_semantics"
MODEL = model_for("semantics")

# Maximum distinct field values sent to the LLM for semantic-label generation.
# Read from config/limits.yaml so all data-shaping numbers are in one place.
_MAX_FIELD_VALUES: int = load_limits()["gen_semantics"]["max_values"]

SYSTEM = """You assign two semantic properties to each field of a state professional-licensing dataset, for one occupation. The downstream code uses these to measure which states have SIMILAR licensing regimes and which are OUTLIERS — so your judgments must reflect what actually characterizes how strictly/differently a state regulates this occupation.

For each field return:
1. importance (0.0–1.0): how much this field defines the CHARACTER of the licensing regime for this occupation. High (0.8–1.0): regulatory model, whether a license is required, scope of practice, the core education/experience bar, profession-defining scope grants (e.g. surgical/drug authority). Low (0.1–0.3): administrative trivia (advisory board exists, fee amounts, renewal interval). Weight scope-of-practice fields higher for professions where scope is contested (surgery, prescribing).
2. closeness_kind:
   - "ordinal" if the values fall on a low→high ladder (more schooling, stricter rung, longer experience, more authority). Return `order` as the FULL value list low→high. Booleans that mean "more regulated when true" are ordinal ["false","true"].
   - "nominal" if values are unordered categories (which body, which accreditor type) — no order.
   - "continuous" only if the value is already a raw number.
Return EVERY field given. Be decisive; this is editable config."""


class FieldSem(BaseModel):
    field_name: str
    importance: float = Field(ge=0.0, le=1.0)
    closeness_kind: Literal["ordinal", "nominal", "continuous"]
    order: list[str] | None = Field(default=None, description="low->high value list for ordinal; null otherwise")


class ProfSem(BaseModel):
    fields: list[FieldSem]


def field_inventory(profession: str):
    d = json.loads((DATA_DIR / f"{profession}.json").read_text())
    mp = d["map_prep"]
    kinds = {s["field_name"]: s["kind"] for s in mp["spec"]}
    vals: dict[str, set] = {}
    for r in mp["rows"]:
        v = r.get("normalized")
        if v is None:
            continue
        vals.setdefault(r["field_name"], set()).add(str(v))
    inv = []
    for f, vs in sorted(vals.items()):
        if len(vs) <= 1:
            continue  # uniform fields carry no similarity signal
        all_vals = sorted(vs)
        if len(all_vals) > _MAX_FIELD_VALUES:
            log.warning("field %r has %d distinct values; capping LLM input at %d "
                        "(dropping %d tail values — semantics quality knob, not data loss)",
                        f, len(all_vals), _MAX_FIELD_VALUES, len(all_vals) - _MAX_FIELD_VALUES)
        inv.append({"field": f, "kind": kinds.get(f, "categorical"), "values": all_vals[:_MAX_FIELD_VALUES]})
    return d.get("display", profession), inv


def gen(profession: str) -> Path:
    display, inv = field_inventory(profession)
    user = (
        f"Occupation: {display}\n\nFields (name | data kind | observed values):\n"
        + "\n".join(f"- {x['field']} | {x['kind']} | {x['values']}" for x in inv)
    )
    res = call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=ProfSem,
                          embed_schema=True, max_tokens=8000)
    if res is None:
        sys.exit(f"[{profession}] LLM failed")
    fields = {}
    for fs in res.fields:
        cl: dict = {"kind": fs.closeness_kind}
        if fs.closeness_kind == "ordinal" and fs.order:
            cl["order"] = fs.order
        fields[fs.field_name] = {"importance": round(fs.importance, 2), "closeness": cl}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{profession}.yaml"
    out.write_text(
        f"# Per-profession field importance + closeness for {display}.\n"
        f"# Generated by pipeline.analyze.gen_semantics (LLM); hand-editable.\n"
        + yaml.safe_dump({"fields": fields}, sort_keys=True, width=200)
    )
    print(f"[{profession}] wrote {out} ({len(fields)} fields)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession")
    ap.add_argument("--professions", help="comma-separated")
    args = ap.parse_args()
    profs = [args.profession] if args.profession else (args.professions.split(",") if args.professions else [])
    if not profs:
        sys.exit("need --profession or --professions")
    for p in profs:
        gen(p.strip().lower())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
