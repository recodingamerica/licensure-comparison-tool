"""Map each chapter in a state's hierarchy to the profession it covers,
in one batch per state. Mirrors map_state_sections_v2.py but for chapters
(not sections). Output: results/chapter_maps/<STATE>.json, consumed by
match_profession.py as a fallback for chapter-layout states.

This eliminates the per-(state, profession) hand-curation that was the
default for chapter-layout quirk states (NV, WV, AL, AK, OH, VA, OR, …).
One run per state covers every current and future profession.

Hallucination guardrails:
  - chapter_slug constrained to a Literal of slugs actually in the hierarchy.
  - profession key constrained to a Literal of registered professions.
  - Each chapter maps to at most one profession; empty mapping is valid.

Labels-only — no body excerpts fetched. For recodification cases (e.g. WV
where the chapter labeled "Podiatrists" was repealed and the live law is
in "Medical Practice Act"), labels may not be enough; flag and add bodies
later if needed.

Usage:
  python -m pipeline.discover.map_state_chapters --state WV
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
from pydantic import ValidationError, create_model

from pipeline._env import load_env  # noqa: E402
load_env()

import litellm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import HIERARCHY_DIR, RESULTS_DIR, CONFIG_DIR, LOGS_DIR  # noqa: E402

CHAPTER_MAPS_DIR = RESULTS_DIR / "chapter_maps"
CHAPTER_MAPS_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOGS_DIR / "map_state_chapters.log"

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("map_state_chapters")


SYSTEM_PROMPT = """\
You are mapping every chapter in a state's licensing title to the regulated
profession it covers. The state's title page lists chapters (or articles);
each profession's licensure law lives in one chapter.

You will see:
  1. A list of profession identifiers (snake_case keys + display names + label patterns).
  2. The chapter list for one state: for each chapter, its slug + label.

For each chapter, decide which profession's licensing it covers, or none.

Rules:
  - Each chapter maps to at most one profession. If unclear, leave it out.
  - "None" is the right answer for chapters about general administration,
    boards in the abstract, repealed sections, paramedics, EMTs, mobile
    intensive care, etc. Only map chapters that contain the actual
    licensure scheme for one of the listed professions.
  - Watch for recodification: a chapter whose label looks like it covers a
    profession may actually be repealed; another chapter may now hold the
    current law. If you can't tell from the label alone, leave it out.
  - Don't invent profession names — use only the IDs supplied.
  - Don't invent slugs.

Return JSON only. No prose, no fences.
"""


def _filter_to_profession_candidates(chapters: list[dict], professions: dict) -> list[dict]:
    """Trim a giant chapter list down to plausible profession candidates.

    Post multi-title expand, hierarchies can hit 2000-10000 entries (most
    irrelevant: criminal procedure, water rights, taxation, etc.). Sending
    them all to the LLM blows context + times out. Pre-filter to chapters
    whose label mentions ANY profession-pattern keyword from professions.yaml.
    That typically takes us from 2000 → 50-300 candidates.
    """
    all_keywords: set[str] = set()
    for prof_def in professions.values():
        for p in prof_def.get("patterns", []):
            all_keywords.add(p.lower())
    if not all_keywords:
        return chapters
    kept = []
    for c in chapters:
        label_lower = c.get("label", "").lower()
        if any(kw in label_lower for kw in all_keywords):
            kept.append(c)
    return kept


def map_state_chapters(state: str, professions: dict, model: str) -> dict | None:
    h_path = HIERARCHY_DIR / f"{state}.json"
    if not h_path.exists():
        sys.exit(f"missing {h_path}")
    h = json.loads(h_path.read_text())
    chapters = h.get("chapters", [])
    if not chapters:
        log.warning("[%s] hierarchy has 0 chapters — nothing to map", state)
        return None

    # Pre-filter when the hierarchy is huge. Otherwise the LLM call balloons
    # past context limits or times out.
    if len(chapters) > 300:
        filtered = _filter_to_profession_candidates(chapters, professions)
        log.info("[%s] pre-filter: %d → %d chapters (only those whose labels mention a profession pattern)",
                 state, len(chapters), len(filtered))
        chapters = filtered
        if not chapters:
            log.warning("[%s] no chapters survived pre-filter — saving empty map", state)
            out = {"state": state, "title_url": h.get("target_url"), "professions": {}}
            return out

    slug_to_url = {c["slug"]: c["url"] for c in chapters}
    slug_to_label = {c["slug"]: c["label"] for c in chapters}
    valid_slugs = list(slug_to_url.keys())
    valid_profs = list(professions.keys())

    SlugLit = TLiteral[tuple(valid_slugs)]  # type: ignore[valid-type]
    ProfLit = TLiteral[tuple(valid_profs)]  # type: ignore[valid-type]
    Mapping = create_model(
        "ChapterMapping",
        chapter_slug=(SlugLit, ...),
        profession=(ProfLit, ...),
    )
    Result = create_model("StateMap", mappings=(list[Mapping], ...))

    prof_block = "\n".join(
        f"- {k}: {v.get('display','')} (patterns: {', '.join(v.get('patterns', []))})"
        for k, v in professions.items()
    )
    chap_block = "\n".join(f"  {c['slug']}\t{c['label'][:160]}" for c in chapters)
    log.info("[%s] %d chapters, %d professions → asking %s", state, len(chapters), len(professions), model)

    user = (
        f"State: {state}\nTitle URL: {h.get('target_url')}\n\n"
        f"Available profession identifiers:\n{prof_block}\n\n"
        f"Chapters in this state's title (slug, label):\n{chap_block}\n"
    )

    schema = Result.model_json_schema()
    sys_with_schema = (
        SYSTEM_PROMPT + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2) + "\n\nReturn ONLY a single JSON object."
    )
    from pipeline._llm import call_structured
    result = call_structured(
        model=model, system=sys_with_schema, user=user, schema_cls=Result,
        max_tokens=8000, max_retries=MAX_RETRIES, log_prefix=f"[{state}]", logger=log,
    )
    if result is None:
        return None

    out: dict = {"state": state, "title_url": h.get("target_url"), "professions": {}}
    for mapping in result.mappings:  # type: ignore[attr-defined]
        url = slug_to_url[mapping.chapter_slug]
        label = slug_to_label[mapping.chapter_slug]
        # last writer wins if model maps two chapters to one profession (rare).
        out["professions"][mapping.profession] = {
            "url": url,
            "chapter_slug": mapping.chapter_slug,
            "label": f"{state} {mapping.chapter_slug} — {label[:80]} (LLM-mapped)",
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    professions = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text())
    state = args.state.upper()
    result = map_state_chapters(state, professions, args.model)
    if not result:
        return
    out_path = CHAPTER_MAPS_DIR / f"{state}.json"
    out_path.write_text(json.dumps(result, indent=2))
    log.info("[%s] mapped %d professions → %s", state, len(result["professions"]), out_path.name)


if __name__ == "__main__":
    main()
