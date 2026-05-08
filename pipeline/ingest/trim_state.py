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
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal as TLiteral

from pydantic import BaseModel, Field, ValidationError, create_model

# Load API key from shared .env if present
_ENV_PATH = Path("/Users/abigailhaddad/Documents/repos/.env")
if _ENV_PATH.exists() and not os.environ.get("ANTHROPIC_API_KEY"):
    for line in _ENV_PATH.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import litellm  # noqa: E402

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import CLEAN_DIR, TRIMMED_DIR, LOGS_DIR  # noqa: E402

LOG_PATH = LOGS_DIR / "trim_state.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
SECTION_TEXT_CAP = 6000  # truncate any one section's text fed to the LLM (chars)
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("trim_state")


from _prompts import load_prompt  # noqa: E402

SYSTEM_PROMPT = load_prompt("trim_state")


def build_decisions_model(citations: list[str]) -> type[BaseModel]:
    """Build a Pydantic model whose `decisions[].citation` is constrained
    to exactly the citations we passed in. Hallucination becomes a Pydantic
    validation error rather than silent drift."""
    if not citations:
        raise ValueError("no citations to classify")
    cite_literal = TLiteral[tuple(citations)]  # type: ignore[valid-type]

    Decision = create_model(
        "TrimDecision",
        citation=(cite_literal, ...),
        keep=(bool, ...),
        reason=(str, Field(description="One-line rationale")),
    )
    Result = create_model(
        "TrimResult",
        decisions=(list[Decision], ...),
    )
    return Result


def section_input_for_llm(sections: list[dict]) -> tuple[list[str], str]:
    """Build the user-message payload of (citation, label, truncated text).

    Returns (citations, formatted_text).
    """
    citations: list[str] = []
    used: set[str] = set()
    parts = []
    for sec in sections:
        cite = sec["citation"] or sec["url"]
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


_JSON_FENCE_RE = __import__("re").compile(r"```(?:json)?\s*([\s\S]*?)```")


def _extract_json(raw: str) -> str:
    """Extract a JSON object from a model response that may include fences or
    leading/trailing prose. Falls back to the substring between the first '{'
    and last '}'."""
    if not raw:
        return ""
    m = _JSON_FENCE_RE.search(raw)
    if m:
        return m.group(1).strip()
    if raw.strip().startswith("{"):
        return raw.strip()
    i = raw.find("{")
    j = raw.rfind("}")
    if i >= 0 and j > i:
        return raw[i : j + 1]
    return raw


def call_model(model: str, system: str, user: str, schema_cls: type[BaseModel]) -> BaseModel | None:
    """One call to the model with structured output via LiteLLM."""
    schema = schema_cls.model_json_schema()
    sys_with_schema = (
        system
        + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2)
        + "\n\nReturn ONLY a single JSON object. No prose, no code fences."
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
            return schema_cls.model_validate(data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            last_err = e
            log.warning("  parse attempt %d failed: %s", attempt + 1, str(e)[:200])
            if attempt < MAX_RETRIES:
                time.sleep(1.5 ** attempt)
            continue
        except Exception as e:
            last_err = e
            log.warning("  api attempt %d failed: %s", attempt + 1, str(e)[:200])
            if attempt < MAX_RETRIES:
                time.sleep(1.5 ** attempt)
            continue
    log.error("  giving up after %d attempts: %s", MAX_RETRIES + 1, str(last_err)[:200])
    return None


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


def trim_state(state: str, profession: str, model: str) -> TrimmedCorpus | None:
    in_path = CLEAN_DIR / profession / f"{state}.json"
    raw = json.loads(in_path.read_text())
    sections = raw.get("sections", [])
    out = TrimmedCorpus(state=state, profession=profession, model=model, chapter_urls=raw.get("chapter_urls", []))
    if not sections:
        log.warning("[%s] no sections", state)
        return out

    log.info("[%s] %d sections, %d chars in", state, len(sections), sum(len(s.get("text", "")) for s in sections))

    # Single-section short-circuit: nothing to classify, keep verbatim. This
    # also avoids the IL case where the whole act is one inline section and
    # Haiku invents sub-cites that fail Literal validation.
    if len(sections) == 1:
        log.info("[%s] single section — skipping LLM, keeping as-is", state)
        for sec in sections:
            out.sections.append(sec)
            out.total_chars += sec.get("text_len", len(sec.get("text", "")))
        return out

    citations, user_msg = section_input_for_llm(sections)
    schema_cls = build_decisions_model(citations)

    result = call_model(model, SYSTEM_PROMPT, user_msg, schema_cls)
    if result is None:
        log.warning("[%s] LLM failed — falling back to keep-everything", state)
        for cite, sec in zip(citations, sections):
            out.skipped.append({"citation": cite, "label": sec.get("label", ""), "reason": "llm_failed_kept_by_default"})
            out.sections.append(sec)
            out.total_chars += sec.get("text_len", len(sec.get("text", "")))
        return out

    decisions = {d.citation: d for d in result.decisions}  # type: ignore[attr-defined]
    by_cite = {c: s for c, s in zip(citations, sections)}
    for cite, sec in by_cite.items():
        d = decisions.get(cite)
        if d is None:
            out.skipped.append({"citation": cite, "label": sec.get("label", "")})
            # Conservative default: keep
            out.sections.append(sec)
            out.total_chars += sec.get("text_len", len(sec.get("text", "")))
            continue
        if d.keep:
            out.sections.append(sec)
            out.total_chars += sec.get("text_len", len(sec.get("text", "")))
        else:
            out.dropped.append({"citation": cite, "label": sec.get("label", ""), "reason": d.reason})

    log.info("[%s] kept=%d dropped=%d skipped=%d → %d chars",
             state, len(out.sections), len(out.dropped), len(out.skipped), out.total_chars)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--states", default="")
    ap.add_argument("--model", default=DEFAULT_MODEL)
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

    summary = []
    for path in sorted(in_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        state = path.stem
        if only and state not in only:
            continue
        try:
            corpus = trim_state(state, profession, args.model)
        except Exception:
            log.exception("[%s] crashed", state)
            continue
        if corpus is None:
            continue
        out_path = out_dir / f"{state}.json"
        out_path.write_text(json.dumps(asdict(corpus), indent=2))
        summary.append({
            "state": state,
            "kept": len(corpus.sections),
            "dropped": len(corpus.dropped),
            "skipped": len(corpus.skipped),
            "chars": corpus.total_chars,
        })
    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))
    log.info("done: %d states", len(summary))


if __name__ == "__main__":
    main()
