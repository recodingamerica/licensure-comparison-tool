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
import time
from pathlib import Path
from typing import Any, Literal as TLiteral

from pydantic import BaseModel, Field, ValidationError, create_model

# Load shared .env
from pipeline._env import load_env  # noqa: E402
load_env()

import litellm  # noqa: E402

# Make sibling modules and pipeline.paths importable regardless of CWD
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from standard_model import (  # noqa: E402
    BoolEvidence,
    IntEvidence,
    LicensureRequirements,
    ScopeOfPractice,
    StrEvidence,
    StrListEvidence,
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


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```")


def _extract_json(raw: str) -> str:
    if not raw:
        return ""
    m = _JSON_FENCE_RE.search(raw)
    if m:
        return m.group(1).strip()
    s = raw.strip()
    if s.startswith("{"):
        return s
    i = s.find("{")
    j = s.rfind("}")
    if i >= 0 and j > i:
        return s[i : j + 1]
    return s


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


def call_model(model: str, system: str, user: str, schema_cls: type[BaseModel]) -> BaseModel | None:
    schema = schema_cls.model_json_schema()
    sys_with_schema = (
        system
        + "\n\nSCHEMA:\n"
        + json.dumps(schema, indent=2)
    )
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": sys_with_schema},
                    {"role": "user", "content": user},
                ],
                temperature=0.0,
                max_tokens=16000,
            )
            raw = resp.choices[0].message.content or ""
            payload = _extract_json(raw)
            data = json.loads(payload)
            try:
                return schema_cls.model_validate(data)
            except ValidationError as ve:
                fixes = _null_out_invalid_paths(data, ve.errors())
                if fixes > 0:
                    log.info("  recovered %d invalid fields → null", fixes)
                    return schema_cls.model_validate(data)
                raise
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = e
            log.warning("  parse attempt %d failed: %s", attempt + 1, str(e)[:200])
        except Exception as e:
            last_err = e
            log.warning("  api attempt %d failed: %s", attempt + 1, str(e)[:200])
        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)
    log.error("  giving up: %s", str(last_err)[:200])
    return None


def build_state_text(state_corpus: dict) -> str:
    parts = []
    for sec in state_corpus.get("sections", []):
        parts.append(f"\n[{sec.get('citation','')}] {sec.get('label','')}\n{sec.get('text','')}\n")
    return "".join(parts)


def load_umbrella_text(state: str) -> str:
    """Return the state's umbrella / cross-cutting chapter text if cached,
    else ''. Meeting Q3: practice acts often reference a general-provisions
    chapter (definitions, board composition, fee rules) that applies to
    multiple professions. Including it here gives the model the context it
    needs to fill fields that the practice act itself only points to.
    """
    p = RESULTS_DIR / "umbrella_text" / f"{state}.json"
    if not p.exists():
        return ""
    rec = json.loads(p.read_text())
    parts = []
    for sec in rec.get("sections", []):
        chap_label = sec.get("umbrella_chapter_label", "")
        parts.append(f"\n[UMBRELLA / {chap_label[:60]}] {sec.get('label','')}\n{sec.get('text','')}\n")
    return "".join(parts)


_TYPO_TRANS = str.maketrans({
    # smart quotes → ASCII
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    # dashes → hyphen
    "–": "-", "—": "-", "−": "-",
    # non-breaking & odd spaces → regular space
    " ": " ", " ": " ", " ": " ", " ": " ",
    # ellipsis
    "…": "...",
})


_NON_ALNUM_RE = re.compile(r"[^a-z0-9 ]+")

# Strip parenthesized list markers from source BEFORE non-alnum stripping, so
# they're surgically removed and don't become bare "1"/"a"/"i" tokens that
# would then either (a) break match against a prose-quoted list, or (b) tempt
# us to strip ALL bare single letters/digits, which would create false
# positives (model wrote "a doctor" instead of "the doctor" — we don't want
# to accept that just because we stripped the "a"). This pre-stripping
# targets only enumeration FORMS (parenthesized or trailing dot), not bare
# words.
# Only parenthesized list markers — N. / a. trailing-dot patterns also appear
# inside legal citations like "RSA 318-B:10, IX." or "Title 2, chapter 15,
# part 17" and stripping those creates false negatives. Limit to forms that
# can ONLY be list markers: bracketed numerals/letters/romans.
_LIST_MARKER_RE = re.compile(
    r"\(\s*(?:\d{1,3}|[a-z]|[ivxIVX]+)\s*\)",   # (1) (a) (iv) (IV)
    re.IGNORECASE,
)


def _normalize_for_match(text: str) -> str:
    """Aggressive normalization for tolerant substring lookup:
      - lowercase
      - smart quotes / dashes → ASCII
      - strip parenthesized list markers '(1)', '(a)', '(iv)' and
        'N.'-style enumeration so a prose-quoted list still matches
      - drop ALL non-alphanumeric (so '§', quote chars, etc. don't break)
      - collapse whitespace
    """
    t = text.translate(_TYPO_TRANS).lower()
    # Remove list markers BEFORE non-alnum strip, so they don't become bare tokens.
    t = _LIST_MARKER_RE.sub(" ", t)
    t = _NON_ALNUM_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


_ELLIPSIS_SPLIT = __import__("re").compile(r"\s*(?:\.\s*\.\s*\.|…)\s*")


def quote_in_corpus(quote: str, normalized_corpus: str) -> bool:
    """Return True if `quote` appears in `normalized_corpus`, allowing the
    LLM to elide non-contiguous segments with ellipses ('...' or '…').
    Each segment (split on ellipsis BEFORE normalization) must appear in
    order; intermediate corpus content is skipped."""
    if not quote:
        return False
    parts = [p for p in (s.strip() for s in _ELLIPSIS_SPLIT.split(quote)) if p]
    if not parts:
        return False
    cursor = 0
    matched_any = False
    for part in parts:
        nq = _normalize_for_match(part)
        if len(nq) < 8:
            continue  # too-short segment isn't strong evidence either way
        idx = normalized_corpus.find(nq, cursor)
        if idx < 0:
            return False
        cursor = idx + len(nq)
        matched_any = True
    return matched_any


def annotate_evidence(node: Any, normalized_corpus: str) -> tuple[int, int]:
    """Walk a model_dump'd dict tree; for any Evidence-shaped object
    (has 'value' AND 'quote' AND 'citation'), set 'unverified': True if the
    quote can't be located in the corpus. Returns (verified, unverified) counts."""
    verified = unverified = 0
    if isinstance(node, dict):
        keys = set(node.keys())
        if {"value", "quote", "citation"}.issubset(keys):
            ok = quote_in_corpus(node.get("quote", ""), normalized_corpus)
            if ok:
                verified += 1
            else:
                node["unverified"] = True
                unverified += 1
            # Recurse into 'value' in case a list-evidence holds nested models (shouldn't here, but safe)
            v, u = annotate_evidence(node.get("value"), normalized_corpus)
            verified += v
            unverified += u
            return verified, unverified
        for v_ in node.values():
            v, u = annotate_evidence(v_, normalized_corpus)
            verified += v
            unverified += u
    elif isinstance(node, list):
        for item in node:
            v, u = annotate_evidence(item, normalized_corpus)
            verified += v
            unverified += u
    return verified, unverified


def extract_one(state: str, profession: str, model: str, profile_cls: type[BaseModel]) -> tuple[dict, dict] | None:
    """Returns (validated_record_dict_with_unverified_flags, validation_stats)."""
    in_path = TRIMMED_DIR / profession / f"{state}.json"
    raw = json.loads(in_path.read_text())
    if not raw.get("sections"):
        log.warning("[%s] no sections to extract from", state)
        return None
    state_text = build_state_text(raw)
    umbrella_text = load_umbrella_text(state)
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
        "[%s] extracting (%d sections, %d chars; umbrella=%d chars)",
        state, len(raw["sections"]), len(user_msg), len(umbrella_text),
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
