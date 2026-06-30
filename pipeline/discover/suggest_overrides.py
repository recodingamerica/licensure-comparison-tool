"""For each (profession, state) where label match found nothing, ask a cheap LLM
which of the state's chapters most likely covers that profession.

Output is a suggestions JSON for human review, NOT a binding addition to the
profession index. Reviewer copies accepted suggestions into
config/state_structure.yaml under the state's `professions:` key;
match_profession.py reads them as overrides on the next run.

Hallucination guardrails:
  - chapter_label is constrained to a Literal of the actual labels in the
    state's hierarchy. Pydantic rejects invented labels.
  - confidence is an enum; "none" is the bail-out path.
  - The model is told explicitly that "no good match" is a valid answer.

States with extraction_level=section_fallback (AZ, OK, WI, LA, KY) are skipped:
their "chapter list" is 1500+ section labels, not chapter labels — those are
handled instead by `map_state_sections.py` (chapter mapper for flat
section lists).

Inputs:  config/professions.yaml, results/hierarchy/<STATE>.json,
         results/profession_index/<profession>.json
Outputs: results/profession_index/<profession>_suggestions.json

Usage:
  python -m pipeline.discover.suggest_overrides --profession podiatry
  python -m pipeline.discover.suggest_overrides --all
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Literal as TLiteral

import yaml
from pydantic import BaseModel, Field, ValidationError, create_model

# .env loader for ANTHROPIC_API_KEY (mirrors trim_state.py / extract_state.py)
from pipeline._env import load_env  # noqa: E402
load_env()

import litellm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import HIERARCHY_DIR, PROFESSION_INDEX_DIR, CONFIG_DIR, LOGS_DIR  # noqa: E402
from _records import record_files  # noqa: E402
from config.states import ALL_STATES  # noqa: E402

LOG_PATH = LOGS_DIR / "suggest_overrides.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("suggest_overrides")


SYSTEM_PROMPT = """\
You are helping locate the chapter in a state's licensing code that regulates a
specific profession. Sometimes the chapter title doesn't include the profession
name — e.g., podiatry is often regulated under a chapter titled "Medicine and
Other Healing Arts" rather than as a standalone "Podiatry" chapter.

You will be given:
  - A profession name and its description
  - The full list of chapters in one state's licensing code

Your job: identify which chapter (or chapters) most likely covers this
profession's licensure and scope of practice. Use the chapter labels — you do
NOT have access to the chapter bodies.

Rules:
  - Pick at most 3 chapters. Most professions live in just one.
  - Set confidence based on how clear the chapter title is:
      * high   — title explicitly names this profession or its alternate names
      * medium — title broadly covers this profession (e.g. "Medicine" for podiatry)
      * low    — could be it but I'm guessing from indirect signals
      * none   — no chapter in this list looks plausible; return zero suggestions
  - Use only the chapter_label values supplied in the input. Do not invent labels.
  - "no plausible chapter" is a valid answer. Return an empty suggestions list.

Return ONLY valid JSON.
"""


class ConfidenceLevel(__import__("enum").Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


def build_suggestions_model(chapter_labels: list[str]) -> type[BaseModel]:
    if not chapter_labels:
        raise ValueError("no chapter labels to pick from")
    label_literal = TLiteral[tuple(chapter_labels)]  # type: ignore[valid-type]

    Suggestion = create_model(
        "ChapterSuggestion",
        chapter_label=(label_literal, ...),
        confidence=(TLiteral["high", "medium", "low"], ...),
        rationale=(str, Field(description="One-line reason this chapter likely covers the profession")),
    )
    Result = create_model(
        "SuggestionsResult",
        suggestions=(list[Suggestion], Field(default_factory=list)),
    )
    return Result


def call_haiku(model: str, user_msg: str, schema_cls: type[BaseModel]) -> BaseModel | None:
    from pipeline._llm import call_structured
    schema = schema_cls.model_json_schema()
    sys_with_schema = (
        SYSTEM_PROMPT + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2)
        + "\n\nReturn ONLY a single JSON object."
    )
    return call_structured(
        model=model, system=sys_with_schema, user=user_msg, schema_cls=schema_cls,
        max_tokens=2000, max_retries=MAX_RETRIES, logger=log,
    )


def suggest_for_state(profession_def: dict, hierarchy: dict, model: str) -> dict:
    state = hierarchy["state"]
    chapters = hierarchy.get("chapters", [])
    if not chapters:
        return {"state": state, "skipped": "no_chapters"}
    if hierarchy.get("extraction_level") == "section_fallback":
        return {"state": state, "skipped": "section_fallback_layout"}
    # Constrain to manageable list — Haiku can handle 200 chapter labels comfortably
    if len(chapters) > 200:
        return {"state": state, "skipped": f"too_many_chapters ({len(chapters)})"}

    label_to_url = {c["label"]: c["url"] for c in chapters}
    labels = list(label_to_url.keys())
    schema_cls = build_suggestions_model(labels)

    profession_block = (
        f"Profession: {profession_def.get('display', '?')}\n"
        f"Patterns it usually goes by: {', '.join(profession_def.get('patterns', []))}\n"
    )
    chapter_list = "\n".join(f"- {lbl}" for lbl in labels)
    user_msg = f"{profession_block}\n\nState: {state}\nChapters in this state's licensing code:\n{chapter_list}"

    log.info("[%s] %d chapters → asking Haiku", state, len(labels))
    result = call_haiku(model, user_msg, schema_cls)
    if result is None:
        return {"state": state, "skipped": "llm_failed"}
    payload = result.model_dump()
    suggestions = payload.get("suggestions", [])
    for s in suggestions:
        s["chapter_url"] = label_to_url.get(s["chapter_label"])
    return {"state": state, "suggestions": suggestions}


def load_hierarchies() -> dict[str, dict]:
    out = {}
    for p in record_files(HIERARCHY_DIR):
        d = json.loads(p.read_text())
        out[d["state"]] = d
    return out


def load_index(profession: str) -> dict:
    path = PROFESSION_INDEX_DIR / f"{profession}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def run_for_profession(profession: str, profession_def: dict, model: str) -> None:
    index = load_index(profession)
    if not index:
        log.warning("[%s] no profession_index — run match_profession first", profession)
        return
    hierarchies = load_hierarchies()
    by_state = index.get("by_state", {})

    out = {
        "profession": profession,
        "display": profession_def.get("display", profession),
        "by_state": {},
    }
    suggested_count = 0
    for state in ALL_STATES:
        # Skip states that already had a label match
        if by_state.get(state, {}).get("matched"):
            out["by_state"][state] = {"already_matched": True}
            continue
        h = hierarchies.get(state)
        if not h:
            out["by_state"][state] = {"skipped": "no_hierarchy"}
            continue
        result = suggest_for_state(profession_def, h, model)
        out["by_state"][state] = result
        sugg = result.get("suggestions") or []
        if sugg:
            suggested_count += 1
            log.info("  [%s] %d suggestions: %s", state,
                     len(sugg), [s["chapter_label"][:50] for s in sugg])

    out_path = PROFESSION_INDEX_DIR / f"{profession}_suggestions.json"
    out_path.write_text(json.dumps(out, indent=2))
    log.info("[%s] wrote %s — %d states with suggestions", profession, out_path, suggested_count)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="", help="Run for one profession (empty = all in professions.yaml)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    professions = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text())
    if args.profession:
        if args.profession not in professions:
            sys.exit(f"unknown profession: {args.profession}")
        professions = {args.profession: professions[args.profession]}

    for prof, defn in professions.items():
        log.info("====== %s ======", prof)
        run_for_profession(prof, defn, args.model)


if __name__ == "__main__":
    main()
