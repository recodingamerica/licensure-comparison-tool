"""Pass 2b: SEMANTIC verification of explicit-negative extractions.

`annotate_evidence` (the pass-2 verifier) checks only that a quote EXISTS in the
corpus — it cannot tell whether the quote SUPPORTS the value. The extract model
occasionally records an explicit negative (a scope field = false, or a scope
matrix item = prohibited) and attaches a real but UNRELATED quote — e.g. podiatry
`ankle_surgery_authorized = false` in NV with a quote about systemic disease. That
renders as a wrong red "excluded" cell in the state-comparison grid.

This stage re-reads every cell the grid would show as EXCLUDED and asks the model
whether its quote actually establishes the prohibition. Unsupported negatives are
reverted to NULL (the field/item becomes not-addressed → grey), never invented as
a positive. It is general — any profession, any bool/enum/scope-matrix negative —
and runs as a wired-in stage (pipeline_stages: extract → verify → mapprep →
publish), so it self-heals every re-extract instead of being a one-off cleanup.

"Excluded" is defined by the SAME polarity rules the grid uses
(build_scope_matrices._polarity / _bool_status), imported here so the verifier and
the display can never disagree about what counts as an exclusion.

Usage:
  python -m pipeline.extract.verify_negatives --profession podiatry
  python -m pipeline.extract.verify_negatives --all
"""

from __future__ import annotations

import argparse
import json
import logging
from typing import Any

from pydantic import BaseModel, Field

from pipeline._env import load_env  # noqa: E402
load_env()

from pipeline._llm import call_structured
from pipeline._records import record_files, write_json_atomic
from pipeline.extract.model_helpers import is_evidence_node
from pipeline.extract.extract_state import load_scope_dims
from pipeline.publish.build_scope_matrices import _polarity, _bool_status, _label
from pipeline.paths import STRUCTURED_DIR, DISCOVERED_DIR, LOGS_DIR, core_professions
from pipeline.config.loaders import model_for

LOG_PATH = LOGS_DIR / "verify_negatives.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("verify_negatives")

MODEL = model_for("verify_negatives")  # falls back to models.yaml `default`
_CHUNK = 40  # negatives per LLM call


class Verdict(BaseModel):
    id: int
    supported: bool = Field(description="True iff the quote itself establishes the prohibition/exclusion")
    reason: str = Field(default="", description="brief")


class VerdictSet(BaseModel):
    verdicts: list[Verdict]


_SYSTEM = (
    "You audit statutory extractions. Each item names a CAPABILITY that an extraction recorded as "
    "PROHIBITED / NOT PERMITTED / EXCLUDED for this profession in this state, citing a verbatim "
    "quote as its sole evidence. For EACH item decide ONE thing: does the quote itself establish "
    "that this capability is forbidden / not permitted / outside scope?\n"
    "  supported=true  — the quote forbids or excludes the capability (e.g. 'shall not perform X', "
    "'may not X', 'X is excluded', or a scope boundary that plainly leaves X out).\n"
    "  supported=false — the quote is about something else, is a general definition that never "
    "addresses this capability, actually PERMITS it, or is just the capability's name with no "
    "prohibiting language.\n"
    "Judge ONLY from the quote text given. Do not use outside knowledge. 'supported' is about the "
    "PROHIBITION being backed by the quote — not about whether the capability is authorized."
)


def _discovered_fields(profession: str) -> dict[str, dict]:
    p = DISCOVERED_DIR / f"{profession}.json"
    if not p.exists():
        return {}
    return {f["name"]: f for f in json.loads(p.read_text()).get("fields", []) if f.get("name")}


def _collect(record: dict, fields: dict[str, dict], scope_dims: list[dict]) -> list[dict]:
    """Every cell in this record that the grid renders as EXCLUDED, as an audit item
    carrying a back-reference (`ref`) for applying the verdict."""
    out: list[dict] = []
    ps = record.get("profession_specific") or {}
    scope_field_names = {d["matrix_field"] for d in scope_dims}
    for name, node in ps.items():
        if name in scope_field_names or not isinstance(node, (dict, list)):
            continue
        if is_evidence_node(node):
            v, q = node.get("value"), (node.get("quote") or "").strip()
            if not q:
                continue
            fspec = fields.get(name, {})
            typ = fspec.get("type")
            excluded = (typ == "bool" and _bool_status(v, _polarity(name)) == "excluded")
            if excluded:
                out.append({
                    "ref": ("field", name),
                    # Clean capability label, NOT the "whether the state authorizes X"
                    # meta-description — the meta phrasing inverts the model's
                    # supported/false judgment.
                    "meaning": _label(name),
                    "quote": q,
                })
    # scope matrix items with status prohibited
    for dim in scope_dims:
        items = ps.get(dim["matrix_field"])
        if not isinstance(items, list):
            continue
        for i, it in enumerate(items):
            if isinstance(it, dict) and it.get("status") == "prohibited" and (it.get("quote") or "").strip():
                out.append({
                    "ref": ("scope", dim["matrix_field"], i),
                    "meaning": f"{_label(dim['source_field'])}: {it.get('item')}",
                    "quote": (it.get("quote") or "").strip(),
                })
    return out


def _apply_null(record: dict, ref: tuple) -> None:
    """Revert an unsupported negative to null / not-addressed."""
    ps = record.get("profession_specific") or {}
    if ref[0] == "field":
        ps[ref[1]] = None
    elif ref[0] == "scope":
        _, fld, i = ref
        items = ps.get(fld) or []
        if 0 <= i < len(items) and isinstance(items[i], dict):
            items[i]["status"] = "not_addressed"
            items[i]["quote"] = ""
            items[i].pop("unverified", None)
    record["profession_specific"] = ps


def _judge(items: list[dict], state: str, profession: str) -> dict[int, Verdict]:
    """LLM verdicts keyed by item id. On failure returns {} (→ change nothing)."""
    verdicts: dict[int, Verdict] = {}
    for start in range(0, len(items), _CHUNK):
        chunk = items[start:start + _CHUNK]
        user = json.dumps({
            "profession": profession, "state": state,
            "items": [{"id": start + j, "capability": it["meaning"], "quote": it["quote"]}
                      for j, it in enumerate(chunk)],
        }, ensure_ascii=False)
        res = call_structured(model=MODEL, system=_SYSTEM, user=user, schema_cls=VerdictSet,
                              embed_schema=True, max_tokens=4000, temperature=None,
                              log_prefix=f"[{profession}/{state}]", logger=log)
        if res is None:
            log.warning("[%s/%s] verify call failed for a chunk — leaving those cells unchanged", profession, state)
            continue
        for v in res.verdicts:
            verdicts[v.id] = v
    return verdicts


def run_profession(profession: str) -> dict:
    profession = profession.lower()
    prof_dir = STRUCTURED_DIR / profession
    if not prof_dir.exists():
        log.warning("[%s] no structured dir", profession)
        return {"checked": 0, "nulled": 0}
    fields = _discovered_fields(profession)
    scope_dims = load_scope_dims(profession)
    checked = nulled = 0
    for path in record_files(prof_dir):
        record = json.loads(path.read_text())
        if not isinstance(record, dict):
            continue
        items = _collect(record, fields, scope_dims)
        if not items:
            continue
        verdicts = _judge(items, path.stem, profession)
        state_nulled = 0
        for idx, it in enumerate(items):
            checked += 1
            v = verdicts.get(idx)
            if v is not None and not v.supported:
                _apply_null(record, it["ref"])
                state_nulled += 1
                log.info("[%s/%s] NULLED %s — %s", profession, path.stem, it["meaning"][:50], v.reason[:70])
        if state_nulled:
            write_json_atomic(path, record, ensure_ascii=False)
            nulled += state_nulled
    log.info("[%s] checked %d excluded cells, reverted %d unsupported → null", profession, checked, nulled)
    return {"checked": checked, "nulled": nulled}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession")
    ap.add_argument("--all", action="store_true", help="every core (published) profession")
    args = ap.parse_args()
    profs = core_professions() if args.all else ([args.profession] if args.profession else [])
    if not profs:
        ap.error("pass --profession X or --all")
    tot_c = tot_n = 0
    for p in profs:
        r = run_profession(p)
        tot_c += r["checked"]; tot_n += r["nulled"]
    log.info("DONE: checked %d, reverted %d across %d professions", tot_c, tot_n, len(profs))


if __name__ == "__main__":
    main()
