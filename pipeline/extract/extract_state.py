"""Pass 2: per-state structured extraction.

Loads the universal base model (standard_model.py) plus the discovered
profession-specific schema (results/discovered/<profession>.json) and composes
a typed Pydantic model. For each state's trimmed text, prompts Haiku and
validates the response.

Inputs:  extract/results/trimmed/<profession>/<STATE>.json
         extract/results/discovered/<profession>.json
         extract/standard_model.py
Outputs: extract/results/structured/<profession>/<STATE>.json

Usage:
  python extract_state.py --profession podiatry [--states CT,FL] [--model claude-haiku-4-5-20251001]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Any, Literal as TLiteral

from pydantic import BaseModel, Field, ValidationError, create_model

# Load shared .env
from pipeline._env import load_env  # noqa: E402
load_env()

# Make sibling modules and pipeline.paths importable regardless of CWD
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _llm import call_structured  # noqa: E402
from standard_model import (  # noqa: E402
    BoolEvidence,
    IntEvidence,
    LicensureRequirements,
    ScopeOfPractice,
    StrEvidence,
    StrListEvidence,
    iter_evidence,
)
from locate_quote import (  # noqa: E402
    normalize_for_match as _normalize_for_match,
    quote_in_corpus,
)
from paths import TRIMMED_DIR, DISCOVERED_DIR, STRUCTURED_DIR, LOGS_DIR, RESULTS_DIR  # noqa: E402

LOG_PATH = LOGS_DIR / "extract_state.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("extract_state")


# Build a per-field Evidence carrier from each discovered field's type.
# Each profession-specific field becomes Optional[FieldEvidence]; the
# Evidence carrier wraps the typed value plus a verbatim quote and citation.
def _evidence_class_for(field_spec: dict) -> type[BaseModel]:
    t = field_spec["type"]
    if t == "bool":
        return BoolEvidence
    if t == "int":
        return IntEvidence
    if t == "str":
        return StrEvidence
    if t == "list[str]":
        return StrListEvidence
    if t == "enum":
        values = field_spec.get("enum_values") or []
        if not values:
            return StrEvidence
        # Build a one-off Evidence subclass with `value` typed to a Literal of allowed values
        return create_model(
            f"EnumEvidence_{field_spec['name']}",
            value=(TLiteral[tuple(values)], ...),  # type: ignore[valid-type]
            quote=(str, ...),
            citation=(str, ...),
        )
    return StrEvidence


def build_profession_specific_model(discovered: dict) -> type[BaseModel]:
    fields: dict[str, tuple[Any, Any]] = {}
    for fspec in discovered["fields"]:
        EvCls = _evidence_class_for(fspec)
        # Optional[EvCls], default None — most fields won't be present in any one state
        py_t = EvCls | None
        desc = fspec.get("description", "")
        fields[fspec["name"]] = (py_t, Field(default=None, description=desc))
    return create_model("ProfessionSpecific", **fields)


def build_profile_model(profession: str, discovered: dict) -> type[BaseModel]:
    Specific = build_profession_specific_model(discovered)
    return create_model(
        f"{profession.title()}Profile",
        state=(str, ...),
        profession=(str, ...),
        licensure=(LicensureRequirements, ...),
        scope=(ScopeOfPractice, ...),
        profession_specific=(Specific, ...),
    )


from _prompts import load_prompt  # noqa: E402

SYSTEM_PROMPT = load_prompt("extract_state")


def _null_out_invalid_paths(data: dict, errors: list[dict]) -> int:
    """Walk Pydantic validation errors and set offending leaf fields to None.
    Returns count of fixes applied. Used to recover from cases where Haiku
    returns an enum value outside our Literal set: rather than drop the whole
    extraction, we keep the rest of the structure and null the bad field."""
    fixed = 0
    for err in errors:
        loc = err.get("loc") or ()
        if not loc:
            continue
        # Walk to the parent of the leaf
        cur: Any = data
        ok = True
        for key in loc[:-1]:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            elif isinstance(cur, list) and isinstance(key, int) and 0 <= key < len(cur):
                cur = cur[key]
            else:
                ok = False
                break
        if not ok:
            continue
        leaf = loc[-1]
        if isinstance(cur, dict) and leaf in cur:
            cur[leaf] = None
            fixed += 1
    return fixed


def _recover_invalid_fields(data: dict, ve: ValidationError) -> dict:
    """Null out leaf fields the LLM filled with values outside our Pydantic
    Literal sets. Lets call_structured re-validate the otherwise-good record
    instead of discarding everything because one enum drifted."""
    fixes = _null_out_invalid_paths(data, ve.errors())
    if fixes > 0:
        log.info("  recovered %d invalid fields → null", fixes)
    return data


def call_model(model: str, system: str, user: str, schema_cls: type[BaseModel]) -> BaseModel | None:
    return call_structured(
        model=model,
        system=system,
        user=user,
        schema_cls=schema_cls,
        embed_schema=True,
        max_tokens=16000,
        max_retries=MAX_RETRIES,
        backoff_base=2.0,
        log_prefix="  ",
        logger=log,
        recover_fn=_recover_invalid_fields,
    )


def build_state_text(state_corpus: dict) -> str:
    parts = []
    for sec in state_corpus.get("sections", []):
        parts.append(f"\n[{sec.get('citation','')}] {sec.get('label','')}\n{sec.get('text','')}\n")
    return "".join(parts)


def _canonical_url(url: str) -> str:
    """Year-prefix-stripping URL key, mirroring assign_umbrella_scope."""
    import re as _re
    return _re.sub(r"/codes/utah/\d{4}/", "/codes/utah/", url)


def load_umbrella_text(state: str, profession: str | None = None) -> str:
    """Return the state's umbrella / cross-cutting chapter text as injectable
    prompt context.

    Filtering rule (when `profession` is given AND we have a scope file for
    the state in `pipeline/results/umbrella_scope/<STATE>.json`): include a
    section iff its `scope_source` is universal (`anchor_universal` /
    `universal`) OR `profession` is in its `applies_to_professions`. Sections
    with `scope_source: "undetermined"` are NOT included — that's the loud
    failure path. They show up in the scope file's `triage` array for review.

    When `profession` is None (the verifier's path), include everything:
    a quote may have been legitimately drawn from any umbrella section the
    model saw at extraction time. Permissive verification beats
    false-positive `unverified` flags.

    Fallback: for states with no `umbrella_scope/<STATE>.json` yet (i.e.
    states the section-level rework hasn't reached), include everything —
    same as the verifier path. This keeps the pipeline working as we roll
    the new approach out state-by-state.
    """
    text_path = RESULTS_DIR / "umbrella_text" / f"{state}.json"
    if not text_path.exists():
        return ""
    sections = (json.loads(text_path.read_text()).get("sections") or [])

    scope_path = RESULTS_DIR / "umbrella_scope" / f"{state}.json"
    if profession and scope_path.exists():
        scope_data = json.loads(scope_path.read_text())
        keep_urls: set[str] = set()
        for entry in scope_data.get("sections", []):
            src = entry.get("scope_source")
            if src in ("anchor_universal", "universal"):
                keep_urls.add(_canonical_url(entry.get("url", "")))
            elif src in ("anchor_enumeration", "inherited_enumeration"):
                if profession in (entry.get("applies_to_professions") or []):
                    keep_urls.add(_canonical_url(entry.get("url", "")))
            # `undetermined` sections are NOT kept — fail loudly.
        sections = [s for s in sections if _canonical_url(s.get("url", "")) in keep_urls]

    parts = []
    for sec in sections:
        chap_label = sec.get("umbrella_chapter_label", "")
        parts.append(f"\n[UMBRELLA / {chap_label[:60]}] {sec.get('label','')}\n{sec.get('text','')}\n")
    return "".join(parts)


def annotate_evidence(node: Any, normalized_corpus: str) -> tuple[int, int]:
    """For every Evidence-shaped dict in `node`, set `unverified: True` when
    the verbatim quote can't be located in the corpus. Returns
    (verified, unverified) counts across the whole tree."""
    verified = unverified = 0
    for _, ev_node in iter_evidence(node):
        if quote_in_corpus(ev_node.get("quote", ""), normalized_corpus):
            ev_node.pop("unverified", None)
            verified += 1
        else:
            ev_node["unverified"] = True
            unverified += 1
    return verified, unverified


def extract_one(state: str, profession: str, model: str, profile_cls: type[BaseModel]) -> tuple[dict, dict] | None:
    """Returns (validated_record_dict_with_unverified_flags, validation_stats)."""
    in_path = TRIMMED_DIR / profession / f"{state}.json"
    raw = json.loads(in_path.read_text())
    if not raw.get("sections"):
        log.warning("[%s] no sections to extract from", state)
        return None
    state_text = build_state_text(raw)
    # Filter the umbrella corpus to sections scoped to this specific
    # profession, based on what the umbrella statute itself enumerates.
    # See pipeline/discover/assign_umbrella_scope.py for the parser that
    # produces `umbrella_scope/<STATE>.json`, and the load_umbrella_text
    # docstring for the include/exclude rule.
    umbrella_text = load_umbrella_text(state, profession)
    if umbrella_text:
        user_msg = (
            f"State: {state}\nProfession: {profession}\n\n"
            f"Practice act text (extract values from here primarily):\n{state_text}\n\n"
            f"=== Cross-cutting umbrella context (definitions, board rules, "
            f"licensing procedures that apply to this profession too) ===\n"
            f"{umbrella_text}"
        )
    else:
        user_msg = f"State: {state}\nProfession: {profession}\n\nTrimmed statute text:\n{state_text}"
    log.info(
        "[%s] extracting %s (%d sections, %d chars; umbrella=%d chars)",
        state, profession, len(raw["sections"]), len(user_msg), len(umbrella_text),
    )
    result = call_model(model, SYSTEM_PROMPT, user_msg, profile_cls)
    if result is None:
        return None
    record = result.model_dump()
    # Quotes can come from either practice-act text OR umbrella text — verify against both.
    normalized_corpus = _normalize_for_match(state_text + "\n" + umbrella_text)
    verified, unverified = annotate_evidence(record, normalized_corpus)
    log.info("[%s] evidence: verified=%d unverified=%d", state, verified, unverified)
    return record, {"verified": verified, "unverified": unverified}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--states", default="")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    profession = args.profession.lower()
    only = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    discovered_path = DISCOVERED_DIR / f"{profession}.json"
    if not discovered_path.exists():
        sys.exit(f"missing discovered schema: {discovered_path}")
    discovered = json.loads(discovered_path.read_text())
    profile_cls = build_profile_model(profession, discovered)
    log.info("composed model with %d profession-specific fields", len(discovered["fields"]))

    out_dir = STRUCTURED_DIR / profession
    out_dir.mkdir(parents=True, exist_ok=True)

    in_dir = TRIMMED_DIR / profession
    summary = []
    for path in sorted(in_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        state = path.stem
        if only and state not in only:
            continue
        try:
            outcome = extract_one(state, profession, args.model, profile_cls)
        except Exception:
            log.exception("[%s] crashed", state)
            continue
        if outcome is None:
            summary.append({"state": state, "ok": False})
            continue
        record, stats = outcome
        out_path = out_dir / f"{state}.json"
        out_path.write_text(json.dumps(record, indent=2))
        spec_dump = record.get("profession_specific") or {}
        filled = sum(1 for v in spec_dump.values() if v not in (None, [], ""))
        summary.append({
            "state": state, "ok": True,
            "specific_fields_filled": filled,
            "specific_fields_total": len(discovered["fields"]),
            "evidence_verified": stats["verified"],
            "evidence_unverified": stats["unverified"],
        })
        log.info(
            "[%s] OK — %d/%d profession-specific fields filled, evidence verified=%d unverified=%d",
            state, filled, len(discovered["fields"]), stats["verified"], stats["unverified"],
        )

    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))
    log.info("done: %d states", len(summary))


if __name__ == "__main__":
    main()
