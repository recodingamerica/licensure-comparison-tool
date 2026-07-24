"""Pass 1a: section-level keep/drop trimming.

For each cleaned state corpus, ask a cheap LLM to classify each section as
keep (substantive: scope, license, practice, prohibitions) or drop (ministerial:
board composition, fund administration, forms, severability).

Hallucination guardrails:
  - The model NEVER emits section text. It only returns citations + a boolean.
  - The citation field is constrained to a Literal of the actual citations in
    the input. Pydantic rejects invented citations.
  - We require a decision for every input citation; missing → re-prompt.
  - The kept text is read verbatim from the cleaned corpus we already have.

Inputs:  extract/results/clean/<profession>/<STATE>.json
Outputs: extract/results/trimmed/<profession>/<STATE>.json
         extract/results/trimmed/<profession>/_summary.json

Usage:
  python trim_state.py --profession podiatry [--states CT,FL,NM] [--model claude-haiku-4-5-20251001]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field

from typing import Literal as TLiteral

from pydantic import BaseModel, Field, ValidationError, create_model

# Load API key from shared .env if present
from pipeline._env import load_env  # noqa: E402
load_env()

from pipeline._llm import call_structured
from pipeline._records import record_files, write_json_atomic
from pipeline._runlog import record_run
from pipeline.paths import CLEAN_DIR, TRIMMED_DIR, LOGS_DIR
from pipeline import provenance
from pipeline.ingest._trim_health import LLM_FAIL_REASON
from pipeline.config.loaders import load_limits, model_for

LOG_PATH = LOGS_DIR / "trim_state.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = model_for("trim")
SECTION_TEXT_CAP = load_limits()["trim"]["section_text_cap"]  # truncate any one section's text fed to the LLM (chars)
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("trim_state")


from pipeline._prompts import load_prompt

SYSTEM_PROMPT = load_prompt("trim_state")

# Classify at most this many sections per LLM call. A single call over a
# 350+-section chapter overflows the output-token cap and truncates the JSON →
# total trim failure (poison). Chunking splits those. The threshold is set ABOVE
# the size of the largest chapter that classifies fine in one call (dentistry/CA
# at 344 worked; 391 truncated), so cells that never overflowed keep their exact
# single-call behavior — the model sees less whole-chapter context when chunked
# and drops slightly less, so we only pay that where we must.
TRIM_CHUNK = 250
# Skip reason for a chunk whose LLM call failed, when OTHER chunks succeeded —
# distinct from LLM_FAIL_REASON so a partial failure isn't flagged poisoned.
CHUNK_FAIL_REASON = "llm_chunk_failed_kept"


def build_decisions_model(citations: list[str]) -> type[BaseModel]:
    """Model for one chunk's keep/drop decisions.

    `citation` stays a Literal over the input citations (hallucination → a clean
    validation error, and — measurably — a Literal-constrained call also keeps
    the model's keep/drop behavior stable; relaxing it to a plain str made the
    model drop ~13% less). The output-token overflow that used to truncate large
    chapters is handled by CHUNKING the call (see TRIM_CHUNK), not by relaxing
    the schema or dropping the per-decision `reason`."""
    if not citations:
        raise ValueError("no citations to classify")
    cite_literal = TLiteral[tuple(citations)]  # type: ignore[valid-type]
    Decision = create_model(
        "TrimDecision",
        citation=(cite_literal, ...),
        keep=(bool, ...),
        reason=(str, Field(description="One-line rationale")),
    )
    return create_model("TrimResult", decisions=(list[Decision], ...))


_QUOTE_NORMALIZE = str.maketrans({
    "‘": "'", "’": "'",  # curly single quotes
    "“": '"', "”": '"',  # curly double quotes
    "–": "-", "—": "-",  # en/em dash
})


def _normalize_citation(cite: str) -> str:
    """Fold typographic punctuation (curly quotes, en/em dashes) to ASCII.

    Cheap models tend to re-type these as plain ASCII when echoing a citation
    back verbatim, which fails the exact-Literal validation in
    build_decisions_model (e.g. "Electricians'" vs "Electricians'"). Since
    `cite` is only an internal join key between our prompt and the model's
    response (never the section's displayed citation), normalizing it here is
    free — it just makes the Literal alphabet ASCII-only so the model's most
    likely output actually matches.
    """
    return cite.translate(_QUOTE_NORMALIZE)


def section_input_for_llm(sections: list[dict]) -> tuple[list[str], str]:
    """Build the user-message payload of (citation, label, truncated text).

    Returns (citations, formatted_text).
    """
    citations: list[str] = []
    used: set[str] = set()
    parts = []
    for sec in sections:
        cite = _normalize_citation(sec["citation"] or sec["url"])
        # Disambiguate within a single state in the rare case of duplicate cites
        base, idx = cite, 1
        while cite in used:
            idx += 1
            cite = f"{base}#{idx}"
        used.add(cite)
        citations.append(cite)
        text = sec.get("text", "")
        if len(text) > SECTION_TEXT_CAP:
            text = text[:SECTION_TEXT_CAP] + "\n…[truncated]"
        parts.append(f"---\nCITATION: {cite}\nLABEL: {sec.get('label','')}\nTEXT:\n{text}\n")
    return citations, "\n".join(parts)


def _citation_recover(valid_citations: list[str]):
    """Recovery for the `citation` Literal: a cheap model occasionally re-types a
    citation (punctuation/case), which would fail the whole call and poison the
    state. On validation failure, remap each drifted citation to its valid member
    by a punctuation-insensitive key; drop any decision that still can't be
    matched (its section then keeps by default). This preserves the Literal's
    anti-hallucination guard while making trivial drift non-fatal — without
    relaxing the schema (which measurably shifted keep/drop behavior)."""
    valid = set(valid_citations)
    norm: dict[str, str] = {}
    for c in valid_citations:
        norm.setdefault(re.sub(r"[^a-z0-9]+", "", c.lower()), c)

    def recover(data: dict, _ve: ValidationError) -> dict:
        decs = data.get("decisions")
        if not isinstance(decs, list):
            return data
        fixed = []
        for d in decs:
            if not isinstance(d, dict):
                continue
            c = d.get("citation")
            if c in valid:
                fixed.append(d)
                continue
            m = norm.get(re.sub(r"[^a-z0-9]+", "", str(c or "").lower()))
            if m is not None:
                d["citation"] = m
                fixed.append(d)
            # else: unrecoverable citation → drop the decision (section keeps)
        data["decisions"] = fixed
        return data

    return recover


def call_model(model: str, system: str, user: str, schema_cls: type[BaseModel],
               citations: list[str] | None = None) -> BaseModel | None:
    """Trim-stage LLM call: structured output via the shared _llm helper.
    Passing `citations` enables citation-drift recovery (see _citation_recover)."""
    return call_structured(
        model=model,
        system=system,
        user=user,
        schema_cls=schema_cls,
        embed_schema=True,
        max_tokens=16000,
        max_retries=MAX_RETRIES,
        log_prefix="  ",
        logger=log,
        recover_fn=_citation_recover(citations) if citations else None,
    )


@dataclass
class TrimmedCorpus:
    state: str
    profession: str
    model: str
    chapter_urls: list[str] = field(default_factory=list)
    sections: list[dict] = field(default_factory=list)  # kept sections, verbatim
    dropped: list[dict] = field(default_factory=list)  # {citation, label, reason}
    skipped: list[dict] = field(default_factory=list)  # input cites with no decision
    total_chars: int = 0
    trim_degraded: bool = False  # True if LLM failed and we fell back to keep-everything
    oversize_kept: int = 0  # sections bypassed LLM because text > SECTION_TEXT_CAP


class TrimLLMError(Exception):
    """Raised under --strict when the trim LLM call fails (no degraded write)."""


def trim_state(state: str, profession: str, model: str, strict: bool = False) -> TrimmedCorpus | None:
    in_path = CLEAN_DIR / profession / f"{state}.json"
    raw = json.loads(in_path.read_text())
    sections = raw.get("sections", [])
    out = TrimmedCorpus(state=state, profession=profession, model=model, chapter_urls=raw.get("chapter_urls", []))
    if not sections:
        log.warning("[%s] no sections", state)
        return out

    log.info("[%s] %d sections, %d chars in", state, len(sections), sum(len(s.get("text", "")) for s in sections))

    # A1: Oversize sections (text > SECTION_TEXT_CAP) are KEPT UNCONDITIONALLY —
    # the LLM must not decide to drop what it cannot fully read. They bypass the
    # LLM batch entirely and are marked kept_oversize=true in the output so
    # downstream auditors know they were never evaluated by the trim LLM.
    oversize: list[dict] = []
    normal: list[dict] = []
    for sec in sections:
        if len(sec.get("text", "")) > SECTION_TEXT_CAP:
            oversize.append(sec)
        else:
            normal.append(sec)

    for sec in oversize:
        flagged = dict(sec)
        flagged["kept_oversize"] = True
        out.sections.append(flagged)
        out.total_chars += sec.get("text_len", len(sec.get("text", "")))

    if oversize:
        log.info("[%s] auto-kept %d oversize section(s) (text > %d chars) — bypassed LLM",
                 state, len(oversize), SECTION_TEXT_CAP)
    out.oversize_kept = len(oversize)

    # Single-section short-circuit: nothing to classify, keep verbatim. This
    # also avoids the IL case where the whole act is one inline section and
    # Haiku invents sub-cites that fail Literal validation.
    # Applied to the NORMAL (non-oversize) sections only.
    if not normal:
        log.info("[%s] no normal-sized sections remain after oversize bypass — done", state)
        return out

    if len(normal) == 1 and not oversize:
        log.info("[%s] single section — skipping LLM, keeping as-is", state)
        for sec in normal:
            out.sections.append(sec)
            out.total_chars += sec.get("text_len", len(sec.get("text", "")))
        return out

    def _keep(sec: dict) -> None:
        out.sections.append(sec)
        out.total_chars += sec.get("text_len", len(sec.get("text", "")))

    n_ok = 0
    for start in range(0, len(normal), TRIM_CHUNK):
        chunk = normal[start:start + TRIM_CHUNK]
        citations, user_msg = section_input_for_llm(chunk)
        by_cite = {c: s for c, s in zip(citations, chunk)}
        result = call_model(model, SYSTEM_PROMPT, user_msg, build_decisions_model(citations), citations)
        if result is None:
            if strict:
                log.error("[%s] LLM failed and --strict set — refusing to write degraded trim", state)
                raise TrimLLMError(f"{profession}/{state}")
            # Keep this chunk un-trimmed. Reason is chunk-specific so a partial
            # failure isn't mistaken for a fully-degraded (poisoned) trim; if
            # EVERY chunk fails we normalize to LLM_FAIL_REASON below.
            log.warning("[%s] chunk of %d sections failed — keeping un-trimmed", state, len(chunk))
            for cite, sec in by_cite.items():
                out.skipped.append({"citation": cite, "label": sec.get("label", ""), "reason": CHUNK_FAIL_REASON})
                _keep(sec)
            continue
        n_ok += 1
        decisions = {d.citation: d for d in result.decisions}  # type: ignore[attr-defined]
        for cite, sec in by_cite.items():
            d = decisions.get(cite)
            if d is None:
                # Conservative default: keep. (Not a failure — the Literal
                # guarantees any returned citation is one of ours; this only
                # fires if the model omitted a section entirely.)
                out.skipped.append({"citation": cite, "label": sec.get("label", "")})
                _keep(sec)
            elif d.keep:
                _keep(sec)
            else:
                out.dropped.append({"citation": cite, "label": sec.get("label", ""), "reason": getattr(d, "reason", "")})

    # Poison ONLY when NO chunk succeeded (total failure) — mirror the legacy
    # keep-everything semantics so preflight/_trim_health still gate it.
    if n_ok == 0:
        log.error("[%s] every trim chunk failed — DEGRADED keep-everything (trim_degraded=true)", state)
        out.trim_degraded = True
        for s in out.skipped:
            s["reason"] = LLM_FAIL_REASON

    log.info("[%s] kept=%d dropped=%d skipped=%d oversize_auto-kept=%d → %d chars",
             state, len(out.sections), len(out.dropped), len(out.skipped), out.oversize_kept, out.total_chars)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--states", default="")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--strict", action="store_true",
                    help="On LLM failure, exit nonzero and write nothing (no degraded keep-everything fallback)")
    args = ap.parse_args()

    profession = args.profession.lower()
    only = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    in_dir = CLEAN_DIR / profession
    if not in_dir.exists():
        sys.exit(f"input dir not found: {in_dir}")
    out_dir = TRIMMED_DIR / profession
    out_dir.mkdir(parents=True, exist_ok=True)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    n_run = 0
    strict_failures: list[str] = []
    for path in record_files(in_dir):
        state = path.stem
        if only and state not in only:
            continue
        try:
            corpus = trim_state(state, profession, args.model, strict=args.strict)
        except TrimLLMError:
            strict_failures.append(state)
            continue
        except Exception:
            log.exception("[%s] crashed", state)
            continue
        if corpus is None:
            continue
        out_path = out_dir / f"{state}.json"
        write_json_atomic(out_path, asdict(corpus))
        provenance.record("trim", profession, state, model=args.model)
        n_run += 1

    # Cumulative summary rebuilt from every trimmed corpus on disk (not just this
    # run's states), so a --states subset run can't drop other states' rows.
    summary = []
    for path in record_files(out_dir):
        d = json.loads(path.read_text())
        summary.append({
            "state": path.stem,
            "kept": len(d.get("sections") or []),
            "dropped": len(d.get("dropped") or []),
            "skipped": len(d.get("skipped") or []),
            "chars": int(d.get("total_chars") or 0),
        })
    write_json_atomic(out_dir / "_summary.json", summary)
    log.info("done: %d states this run, %d total in summary", n_run, len(summary))
    record_run("trim_state", profession=profession)

    if strict_failures:
        sys.exit(f"--strict: LLM failed for {len(strict_failures)} state(s), wrote nothing for them: {strict_failures}")


if __name__ == "__main__":
    main()
