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
import re
import logging
import os
import sys
from typing import Any, Literal as TLiteral

from pydantic import BaseModel, Field, ValidationError, create_model

# Load shared .env
from pipeline._env import load_env  # noqa: E402
load_env()

# Make sibling modules and pipeline.paths importable regardless of CWD
from pipeline._llm import call_structured
from pipeline._records import record_files, write_json_atomic
from pipeline._runlog import record_run
from pipeline.ingest._section_patterns import canonical_year_url
from pipeline.extract.standard_model import (  # noqa: E402
    BoolEvidence,
    IntEvidence,
    LicensureRequirements,
    ScopeOfPractice,
    StrEvidence,
    StrListEvidence,
    derive_regulatory_model,
    iter_evidence,
)
from pipeline.extract.locate_quote import (  # noqa: E402
    normalize_for_match as _normalize_for_match,
    quote_fuzzy_match,
    quote_in_corpus,
)
from pipeline.paths import TRIMMED_DIR, DISCOVERED_DIR, STRUCTURED_DIR, LOGS_DIR, RESULTS_DIR, SCOPE_VOCAB_DIR
from pipeline import provenance
from pipeline.eval.check_consistency import check_record
from pipeline.config.loaders import model_for

LOG_PATH = LOGS_DIR / "extract_state.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = model_for("extract")
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


# ---------- Scope matrices (discover the union → per-state three-state) ----------
# A discovered free-text scope LIST field (e.g. laser_procedures_authorized) is
# upgraded into a per-item matrix: for the corpus-discovered vocabulary of that
# dimension, the model classifies EVERY item in this state. The vocabulary lives
# in results/scope_vocab/<profession>.json (see pipeline.discover.scope_vocab).
# This is the "connection": the enumerated field lands in the schema automatically
# from that file — nothing is hand-edited here per profession.

_STATUS_LITERALS = {
    "three_state": ("authorized", "prohibited", "not_addressed"),
    "present_absent": ("present", "absent"),
}


def load_scope_dims(profession: str) -> list[dict]:
    """Discovered scope dimensions for this profession (empty if none)."""
    p = SCOPE_VOCAB_DIR / f"{profession}.json"
    if not p.exists():
        return []
    return json.loads(p.read_text()).get("dimensions", [])


class ScopeMatrixItem(BaseModel):
    """One row of a scope matrix. `item`/`status` are plain str, NOT Literal:
    a required Literal here is dangerous, because the shared _recover_invalid_fields
    pass nulls any drifted leaf to None and a single off-by-a-word item name would
    then fail re-validation and drop the WHOLE state. Instead the model is guided by
    the field description (which lists the vocab + allowed statuses) and
    finalize_scope_matrices canonicalizes items to the vocab and normalizes statuses
    afterward — hallucinated items are dropped, missing ones post-filled."""
    item: str
    status: str = ""
    quote: str = Field(default="", description="Verbatim statute phrase; required for authorized/prohibited/present, empty otherwise")
    citation: str = ""


def _scope_field_description(dim: dict) -> str:
    n = len(dim["vocab"])
    if dim["eval_flavor"] == "present_absent":
        rule = ("For EACH item, status is `present` if this state's statute provides for it, "
                "else `absent`. Quote verbatim for `present`.")
    else:
        rule = ("For EACH item, status is `authorized` if the statute permits it, `prohibited` "
                "if the statute forbids it (including via a broad exclusion/prohibition that covers "
                "it), or `not_addressed` if the statute is genuinely silent. Quote verbatim for "
                "`authorized` and `prohibited`.")
    return (f"Scope checklist for '{dim['source_field']}'. Return EXACTLY one entry for each of "
            f"these {n} items, using the item name verbatim: {dim['vocab']}. {rule}")


def build_profession_specific_model(discovered: dict, scope_dims: list[dict] | None = None) -> type[BaseModel]:
    fields: dict[str, tuple[Any, Any]] = {}
    for fspec in discovered["fields"]:
        EvCls = _evidence_class_for(fspec)
        # Optional[EvCls], default None — most fields won't be present in any one state
        py_t = EvCls | None
        desc = fspec.get("description", "")
        fields[fspec["name"]] = (py_t, Field(default=None, description=desc))
    for dim in scope_dims or []:
        fields[dim["matrix_field"]] = (
            list[ScopeMatrixItem],
            Field(default_factory=list, description=_scope_field_description(dim)),
        )
    Model = create_model("ProfessionSpecific", **fields)
    Model.__doc__ = ("Fields discovered specifically for this profession (auto-derived from its "
                     "statutes); they vary profession to profession.")
    return Model


def build_profile_model(profession: str, discovered: dict) -> type[BaseModel]:
    Specific = build_profession_specific_model(discovered, load_scope_dims(profession))
    return create_model(
        f"{profession.title()}Profile",
        state=(str, ...),
        profession=(str, ...),
        licensure=(LicensureRequirements, ...),
        scope=(ScopeOfPractice, ...),
        profession_specific=(Specific, ...),
    )


from pipeline._prompts import load_prompt

SYSTEM_PROMPT = load_prompt("extract_state")


def _null_out_invalid_paths(data: dict, errors: list[dict]) -> int:
    """Walk Pydantic validation errors and null the smallest recoverable subtree
    containing each offending leaf, so call_structured can re-validate the rest of
    the record instead of discarding the whole state over one drifted enum. Returns
    count of fixes applied.

    Nulls at the NEAREST dict-keyed ancestor of the offending leaf:
      1. A plain Optional field            -> null the field.
      2. `value` inside an Evidence wrapper -> null the whole wrapper at its parent
         key (nulling just `.value` doesn't help — the wrapper still requires the
         typed field).
      3. A field inside a LIST element (e.g. exams[2].degree_level) -> null that
         field in the element, leaving the siblings intact.
      4. A bad element of a list[...] field -> null the whole list at its parent key.
    Cases 3 and 4 used to be unreachable — the null only fired when the parent was a
    dict — so a single invalid value anywhere inside a list dropped the ENTIRE state
    as an extraction gap. All these fields are Optional in standard_model, so nulling
    them is safe.
    """
    fixed = 0
    for err in errors:
        loc = err.get("loc") or ()
        if not loc:
            continue
        # If the offending leaf is `value`, aim at the Evidence wrapper (its parent).
        target_path = loc[:-1] if loc[-1] == "value" else loc
        if not target_path:
            continue
        # Walk the path, remembering the last point where the container is a dict.
        # A list index can't be nulled in place (None isn't a valid element type), so
        # for a leaf inside/at a list we fall back to nulling that nearest dict key.
        cur: Any = data
        null_container: Any = None
        null_key: Any = None
        ok = True
        for key in target_path:
            if isinstance(cur, dict) and key in cur:
                null_container, null_key = cur, key
                cur = cur[key]
            elif isinstance(cur, list) and isinstance(key, int) and 0 <= key < len(cur):
                cur = cur[key]
            else:
                ok = False
                break
        if ok and null_container is not None:
            null_container[null_key] = None
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
    """Year-prefix-stripping URL key (shared, state-agnostic — was Utah-only)."""
    return canonical_year_url(url)


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
    the verbatim quote can't be located in the corpus. When strict
    verification fails, run a fuzzy fallback (`quote_fuzzy_match`) and
    attach `approximate: {ratio, matched_normalized}` on the same node so
    the UI can surface a candidate match with an explicit confidence
    rather than just "couldn't verify". Returns (verified, unverified)
    counts; approximate matches still count as unverified."""
    verified = unverified = 0
    for _, ev_node in iter_evidence(node):
        quote = ev_node.get("quote", "")
        if quote_in_corpus(quote, normalized_corpus):
            ev_node.pop("unverified", None)
            ev_node.pop("approximate", None)
            verified += 1
        else:
            ev_node["unverified"] = True
            fuzzy = quote_fuzzy_match(quote, normalized_corpus)
            if fuzzy is not None:
                ev_node["approximate"] = fuzzy
            else:
                ev_node.pop("approximate", None)
            unverified += 1
    return verified, unverified


def _normalize_item_key(s: str) -> str:
    """Loose key for matching a model-returned item name to a vocab entry —
    case/space/punctuation-insensitive so trivial phrasing drift still maps."""
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def finalize_scope_matrices(record: dict, profession: str, normalized_corpus: str) -> None:
    """For every discovered scope-matrix field, produce a complete, canonical,
    fixed-order matrix:

    - Canonicalize each returned item to the discovered vocabulary (exact, then
      case/punctuation-insensitive, then alias). Items that match nothing are
      dropped (model hallucinations don't leak into the matrix).
    - Normalize status to the flavor's allowed set; an unrecognized status
      degrades to silent (`not_addressed` / `absent`) rather than propagating.
    - Verify the quote for a claimed authorized/prohibited/present item against
      the corpus; flag `unverified` when it isn't found.
    - Post-fill every vocab item the model omitted as silent, so the matrix is
      always exactly the vocabulary, in vocabulary order.

    Scope items are intentionally NOT Evidence-shaped (no `value` key), so
    annotate_evidence skips them and their quotes are verified here."""
    dims = load_scope_dims(profession)
    if not dims:
        return
    ps = record.get("profession_specific") or {}
    for dim in dims:
        fld, vocab, flavor = dim["matrix_field"], dim["vocab"], dim["eval_flavor"]
        allowed = set(_STATUS_LITERALS.get(flavor, _STATUS_LITERALS["three_state"]))
        silent = "absent" if flavor == "present_absent" else "not_addressed"
        needs_quote = {"present"} if flavor == "present_absent" else {"authorized", "prohibited"}

        # canonical-name lookup: exact name, loose key, and any aliases.
        canon: dict[str, str] = {}
        for name in vocab:
            canon[name] = name
            canon[_normalize_item_key(name)] = name
        for name, al in (dim.get("aliases") or {}).items():
            for a in al:
                canon.setdefault(_normalize_item_key(a), name)

        by_item: dict[str, dict] = {}
        for it in ps.get(fld) or []:
            if not isinstance(it, dict):
                continue
            name = canon.get(it.get("item", "")) or canon.get(_normalize_item_key(it.get("item", "")))
            if name is None or name in by_item:
                continue  # hallucinated item, or duplicate — keep the first
            status = it.get("status") if it.get("status") in allowed else silent
            quote = (it.get("quote") or "").strip()
            entry = {"item": name, "status": status, "quote": quote, "citation": it.get("citation", "")}
            if status in needs_quote and quote and not quote_in_corpus(quote, normalized_corpus):
                entry["unverified"] = True
            by_item[name] = entry

        ps[fld] = [
            by_item.get(name, {"item": name, "status": silent, "quote": "", "citation": ""})
            for name in vocab
        ]
    record["profession_specific"] = ps


def verify_record(record: dict, profession: str, state_text: str, umbrella_text: str) -> tuple[int, int]:
    """Shared post-extraction pass for both the sync and batch extractors:
    finalize scope matrices, then verify every Evidence quote. Quotes can come
    from either the practice-act text OR the umbrella text, so verify against
    both. Returns (verified, unverified) Evidence counts."""
    normalized_corpus = _normalize_for_match(state_text + "\n" + umbrella_text)
    finalize_scope_matrices(record, profession, normalized_corpus)
    return annotate_evidence(record, normalized_corpus)


def build_user_message(state: str, profession: str) -> str | None:
    """The single prompt-formatting path for one (state, profession) — used by
    BOTH the sync extractor and the batch submitter, so the exact text the model
    sees can't drift between them. Returns None if there's nothing to extract.

    The umbrella corpus is filtered to sections scoped to this specific
    profession, based on what the umbrella statute itself enumerates. See
    pipeline/scope/assign_umbrella_scope.py for the parser and the
    load_umbrella_text docstring for the include/exclude rule."""
    in_path = TRIMMED_DIR / profession / f"{state}.json"
    if not in_path.exists():
        return None
    raw = json.loads(in_path.read_text())
    if not raw.get("sections"):
        return None
    state_text = build_state_text(raw)
    umbrella_text = load_umbrella_text(state, profession)
    if umbrella_text:
        return (
            f"State: {state}\nProfession: {profession}\n\n"
            f"Practice act text (extract values from here primarily):\n{state_text}\n\n"
            f"=== Cross-cutting umbrella context (definitions, board rules, "
            f"licensing procedures that apply to this profession too) ===\n"
            f"{umbrella_text}"
        )
    return f"State: {state}\nProfession: {profession}\n\nTrimmed statute text:\n{state_text}"


def apply_derived_regulatory_model(record: dict, state: str) -> None:
    """Derive the UORF rung from the orthogonal axes (credential_type +
    scope_protection) rather than trusting the model's free pick, which
    flip-flops deterministically on title-protection schemes. The model's quoted
    scope/credential facts drive the rung; this makes the cross-field invariants
    in eval/check_consistency.py structurally satisfied instead of merely
    flagged. See standard_model.derive_regulatory_model."""
    lic = record.get("licensure") or {}
    rm_ev = lic.get("regulatory_model")

    def _ev_val(field: object) -> object:
        return field.get("value") if isinstance(field, dict) else None

    derived = derive_regulatory_model(
        _ev_val(lic.get("credential_type")),
        _ev_val(lic.get("scope_protection")),
    )
    if derived is not None and isinstance(rm_ev, dict) and rm_ev.get("value") != derived.value:
        log.info(
            "[%s] regulatory_model derived: %s → %s (credential_type=%s, scope_protection=%s)",
            state, rm_ev.get("value"), derived.value,
            _ev_val(lic.get("credential_type")), _ev_val(lic.get("scope_protection")),
        )
        rm_ev["value"] = derived.value
        # The model's quote justified the value we just replaced, so it is now orphaned:
        # it stays verbatim-verifiable and renders in the Sheet as a sky-blue "verified"
        # card that argues against its own value (issue #62 — e.g. EMT/KS kept
        # "...unlawful...unless...holds a valid certificate" under voluntary_certification).
        # Drop it and mark the node derived. No evidence is lost: the rung comes from
        # credential_type + scope_protection, which keep their own quotes in the same Sheet.
        rm_ev["quote"] = ""
        rm_ev["citation"] = ""
        rm_ev["derived"] = True


def finalize_and_persist(record: dict, profession: str, state: str, model: str | None) -> dict:
    """The single post-extraction pipeline, shared by the sync and batch paths so
    they can't diverge: derive the regulatory rung, finalize scope matrices +
    verify quotes, run the cross-field consistency guard (log-only — detection,
    not silent fix), then write the record and stamp provenance. Returns
    {'verified', 'unverified'} evidence counts.

    Re-reads the trimmed + umbrella corpus from disk (both callers have only
    profession+state at this point); the reads are cheap and keep this the one
    place that knows the whole finalize sequence."""
    raw = json.loads((TRIMMED_DIR / profession / f"{state}.json").read_text())
    state_text = build_state_text(raw)
    umbrella_text = load_umbrella_text(state, profession)

    apply_derived_regulatory_model(record, state)
    verified, unverified = verify_record(record, profession, state_text, umbrella_text)
    for v in check_record(profession, state, record):
        log.warning("[%s] CONSISTENCY %s: %s", state, v["rule"], v["detail"])

    out_path = STRUCTURED_DIR / profession / f"{state}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(out_path, record, ensure_ascii=False)
    provenance.record("extract", profession, state, model=model)
    log.info("[%s] evidence: verified=%d unverified=%d", state, verified, unverified)
    return {"verified": verified, "unverified": unverified}


def extract_one(state: str, profession: str, model: str, profile_cls: type[BaseModel]) -> tuple[dict, dict] | None:
    """Sync single-state extraction: build the prompt, call the model, then run
    the shared finalize_and_persist pipeline. Returns (record, stats) or None."""
    user_msg = build_user_message(state, profession)
    if user_msg is None:
        log.warning("[%s] no sections to extract from", state)
        return None
    log.info("[%s] extracting %s (%d chars)", state, profession, len(user_msg))
    result = call_model(model, SYSTEM_PROMPT, user_msg, profile_cls)
    if result is None:
        return None
    record = result.model_dump()
    stats = finalize_and_persist(record, profession, state, model)
    return record, stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--states", default="")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument(
        "--force",
        action="store_true",
        help=(
            "Re-extract states that already have a structured/<state>.json. "
            "Default is to SKIP existing — so a crashed bulk run can be resumed "
            "without redoing work. Use this when the schema or prompt changed "
            "and you want every state re-extracted."
        ),
    )
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
    skipped = 0
    for path in record_files(in_dir):
        state = path.stem
        if only and state not in only:
            continue
        out_path = out_dir / f"{state}.json"
        if out_path.exists() and not args.force:
            skipped += 1
            continue
        try:
            outcome = extract_one(state, profession, args.model, profile_cls)
        except Exception:
            log.exception("[%s] crashed", state)
            continue
        if outcome is None:
            summary.append({"state": state, "ok": False})
            continue
        # extract_one already ran the shared finalize_and_persist pipeline
        # (derive rung → verify → consistency guard → write → provenance).
        record, stats = outcome
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

    write_json_atomic(out_dir / "_summary.json", summary)
    log.info(
        "done: %d states extracted, %d already-present skipped (use --force to redo)",
        len(summary), skipped,
    )
    record_run("extract_state", profession=profession)


if __name__ == "__main__":
    main()
