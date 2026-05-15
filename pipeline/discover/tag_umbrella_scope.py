"""SUPERSEDED — kept for reference only.

This script asked Claude Haiku to classify each umbrella chapter into one of
four family buckets (universal / health / business / building_design /
public_safety). It augmented `results/umbrella_chapters/<STATE>.json` with
`applies_to` (the bucket), `scope_evidence`, and `reasoning`.

It is no longer wired into the pipeline. Two reasons:

  1. The four-bucket abstraction was lossy. Real state regulatory taxonomies
     don't fit four categories, and forcing chapter/profession into the same
     enum hides real ambiguity. See issue #1.
  2. Chapter-level granularity was wrong. Within a single chapter, many
     individual sections target specific professions while others apply to
     all. A chapter-level tag can't honor that.

The replacement — `pipeline/discover/assign_umbrella_scope.py` — assigns
scope per SECTION, deterministically, by parsing the umbrella statute's own
"licensed under Chapter X" enumerations and universal-applicability
phrasing. No LLM. See issue #1.

Kept here in case we ever want to compare LLM-classified family buckets
against the deterministic per-section scope (audit cross-check) or
re-purpose the prompt for a different classification task.

Original docstring follows.
================================================================

Classify each umbrella chapter by which profession-families it actually
applies to. Augments `results/umbrella_chapters/<STATE>.json` in place
with `applies_to`, `scope_evidence`, and `reasoning` per chapter.

Cheap: one LLM call per umbrella chapter (~150 calls across 50 states).

Usage:
  python -m pipeline.discover.tag_umbrella_scope --state UT
  python -m pipeline.discover.tag_umbrella_scope            # all states
  python -m pipeline.discover.tag_umbrella_scope --force    # re-tag cached
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Literal as TLiteral

from pydantic import BaseModel, Field

from pipeline._env import load_env  # noqa: E402
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR, LOGS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402
from _llm import call_structured  # noqa: E402
from _prompts import load_prompt  # noqa: E402


UMBRELLA_CHAPTERS_DIR = RESULTS_DIR / "umbrella_chapters"
UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
LOG_PATH = LOGS_DIR / "tag_umbrella_scope.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Closed enum; matches `family` values in pipeline/config/professions.yaml,
# plus "universal" for the catch-all case.
SCOPE_VALUES = ("universal", "health", "building_design", "business", "public_safety")
ScopeLit = TLiteral[SCOPE_VALUES]  # type: ignore[valid-type]

# Context budget per chapter sent to the LLM. The classification signal lives
# almost entirely in the first 1-3 sections (definitions, "applies to",
# "purpose"); past that it's procedural noise that wastes tokens.
MAX_CONTEXT_CHARS = 4000

DEFAULT_MODEL = "claude-haiku-4-5-20251001"  # classification task, Haiku is enough

SYSTEM_PROMPT = load_prompt("tag_umbrella_scope")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("tag_umbrella_scope")


class ScopeClassification(BaseModel):
    applies_to: list[ScopeLit] = Field(..., min_length=1)
    scope_evidence: str
    reasoning: str


def _build_chapter_context(chapter_slug: str, umbrella_sections: list[dict]) -> str:
    """Concatenate the first few sections of `chapter_slug` from the cached
    umbrella_text record, capped at MAX_CONTEXT_CHARS. These are
    `umbrella_chapter_slug`-tagged section dicts; preserve original order."""
    chunks: list[str] = []
    total = 0
    for sec in umbrella_sections:
        if sec.get("umbrella_chapter_slug") != chapter_slug:
            continue
        label = (sec.get("label") or "").strip()
        text = (sec.get("text") or "").strip()
        if not text:
            continue
        block = f"[{label}]\n{text}"
        if total + len(block) > MAX_CONTEXT_CHARS and chunks:
            break
        chunks.append(block)
        total += len(block)
        if total >= MAX_CONTEXT_CHARS:
            break
    return "\n\n".join(chunks)


def classify_chapter(
    state: str, chapter: dict, umbrella_sections: list[dict], model: str
) -> dict | None:
    """Return the chapter dict augmented with applies_to / scope_evidence /
    reasoning, or None on LLM failure. Falls back to ["universal"] when the
    cached umbrella_text has no content for this chapter (rare — happens
    when find_umbrella_chapters listed a chapter but pull_umbrella_text
    couldn't fetch its sections, e.g., AZ)."""
    slug = chapter.get("slug", "")
    label = chapter.get("label", "")
    context = _build_chapter_context(slug, umbrella_sections)
    if not context:
        log.warning("[%s/%s] no cached section text — defaulting to universal", state, slug)
        return {
            **chapter,
            "applies_to": ["universal"],
            "scope_evidence": "",
            "reasoning": "no cached section text; conservative default",
        }
    user = (
        f"State: {state}\n"
        f"Chapter label: {label}\n\n"
        f"Chapter intro text (first sections, capped at {MAX_CONTEXT_CHARS} chars):\n"
        f"{context}"
    )
    result = call_structured(
        model=model, system=SYSTEM_PROMPT, user=user,
        schema_cls=ScopeClassification,
        max_tokens=800, max_retries=2,
        log_prefix=f"[{state}/{slug}]", logger=log,
    )
    if result is None:
        return None
    return {
        **chapter,
        "applies_to": list(result.applies_to),
        "scope_evidence": result.scope_evidence,
        "reasoning": result.reasoning,
    }


def tag_state(state: str, force: bool, model: str) -> bool:
    """Augment one state's umbrella_chapters record. Returns True on
    success (or skip), False if any chapter classification crashed."""
    chap_path = UMBRELLA_CHAPTERS_DIR / f"{state}.json"
    if not chap_path.exists():
        log.info("[%s] no umbrella_chapters file, skip", state)
        return True
    rec = json.loads(chap_path.read_text())
    chapters = rec.get("umbrella_chapters", [])
    if not chapters:
        log.info("[%s] no umbrella chapters declared, skip", state)
        return True

    text_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    umbrella_sections = []
    if text_path.exists():
        umbrella_sections = json.loads(text_path.read_text()).get("sections") or []

    new_chapters = []
    crashed = False
    for chapter in chapters:
        if not force and "applies_to" in chapter:
            new_chapters.append(chapter)
            continue
        tagged = classify_chapter(state, chapter, umbrella_sections, model)
        if tagged is None:
            crashed = True
            new_chapters.append(chapter)  # keep untagged rather than drop
            continue
        log.info("[%s/%s] applies_to=%s", state, chapter.get("slug"), tagged["applies_to"])
        new_chapters.append(tagged)

    rec["umbrella_chapters"] = new_chapters
    chap_path.write_text(json.dumps(rec, indent=2))
    return not crashed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="")
    ap.add_argument("--states", default="")
    ap.add_argument("--force", action="store_true",
                    help="Re-tag chapters that already have applies_to.")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    if args.state:
        targets = [args.state.upper()]
    elif args.states:
        targets = [s.strip().upper() for s in args.states.split(",") if s.strip()]
    else:
        targets = list(ALL_STATES)

    log.info("tagging umbrella scope for %d state(s) using %s", len(targets), args.model)
    failures = []
    for st in targets:
        try:
            ok = tag_state(st, args.force, args.model)
        except Exception:
            log.exception("[%s] crashed", st)
            failures.append(st)
            continue
        if not ok:
            failures.append(st)

    if failures:
        log.warning("crashes/partial in %d state(s): %s", len(failures), failures)
    else:
        log.info("done, no failures")


if __name__ == "__main__":
    main()
