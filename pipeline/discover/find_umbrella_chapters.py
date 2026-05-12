"""Find the umbrella / cross-cutting licensing chapter(s) in each state.

Meeting Q3: practice acts often reference "the umbrella act" — a chapter
with cross-cutting definitions, board-composition rules, disciplinary
procedures, fee-collection authority, public-records exemptions — that
applies to many professions but isn't pulled when we extract one specific
practice act. Missing this context can leave the per-profession extraction
incomplete.

This script: for each state, look at the hierarchy's chapter labels and
LLM-identify the chapter(s) most likely to be the umbrella. Cache the
result. Downstream (extract_state.py) can inject umbrella text as
supplemental context when extracting any profession in that state.

Heuristic for what counts as umbrella:
  - Chapter labels mentioning "General Provisions", "Definitions",
    "Health Occupations Generally", "Professions in General",
    "Administrative Procedures", "Licensure (general)", etc.
  - Located within the same title as profession-specific chapters
  - NOT specific to one profession

Returns a list (some states have more than one umbrella — e.g., one for
all health professions and another for boards in general).

Usage:
  python -m pipeline.discover.find_umbrella_chapters --state TX
  python -m pipeline.discover.find_umbrella_chapters         # all states
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Literal as TLiteral

from pydantic import create_model

from pipeline._env import load_env
load_env()

import litellm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import HIERARCHY_DIR, RESULTS_DIR, LOGS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402
from pipeline._llm import call_structured  # noqa: E402
from pipeline._fetch_config import PER_HOST_DELAY  # noqa: E402

UMBRELLA_DIR = RESULTS_DIR / "umbrella_chapters"
UMBRELLA_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOGS_DIR / "find_umbrella_chapters.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "claude-sonnet-4-6"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("find_umbrella_chapters")


SYSTEM_PROMPT = """\
You are identifying UMBRELLA / cross-cutting licensing chapters in a state's
statutory hierarchy.

An "umbrella chapter" contains cross-cutting rules that apply to MANY
licensed professions, not the licensure scheme for one specific profession.
Examples of umbrella content:
  - Definitions used across all licensure
  - Composition / appointment of licensing boards in general
  - Administrative procedures common to all boards
  - Fee structures or collection authority
  - Public records exemptions for license applications
  - Disciplinary procedures that apply to all licensees
  - "General Provisions Relating to Licensing"

Examples of NON-umbrella (skip these):
  - Practice acts for specific professions (Podiatry, Accountancy, etc.)
  - Sub-board-specific rules
  - Sections about one profession's scope

Many states have 0 umbrella chapters — that's a valid answer (return empty).
Some have 1 (e.g., "Title 1 - Definitions" or "Chapter 1 - General Provisions").
A few have 2-3 (one for health professions overall, one for the parent
licensing department, etc.). Don't return more than 5; if you're considering
more than 5 you're over-classifying.

Return JSON only.
"""


def find_for_state(state: str, model: str, force: bool) -> dict | None:
    out_path = UMBRELLA_DIR / f"{state}.json"
    if out_path.exists() and not force:
        log.info("[%s] cached, skip", state)
        return json.loads(out_path.read_text())

    h_path = HIERARCHY_DIR / f"{state}.json"
    if not h_path.exists():
        log.warning("[%s] no hierarchy file — run build_hierarchy first", state)
        return None
    h = json.loads(h_path.read_text())
    chapters = h.get("chapters", [])
    if not chapters:
        return None
    if len(chapters) > 600:
        # Too many to classify in one call; sample top chapters whose labels
        # contain umbrella-suggestive words
        candidates = [c for c in chapters if any(
            kw in c.get("label", "").lower()
            for kw in ("general", "definition", "provision", "administ", "board", "license", "professions", "occupations")
        )][:200]
        if not candidates:
            log.info("[%s] %d chapters but no obvious umbrella candidates", state, len(chapters))
            record = {"state": state, "umbrella_chapter_slugs": [], "filtered_from": len(chapters)}
            out_path.write_text(json.dumps(record, indent=2))
            return record
        chapters_to_send = candidates
    else:
        chapters_to_send = chapters

    valid_slugs = [c["slug"] for c in chapters_to_send]
    SlugLit = TLiteral[tuple(valid_slugs)]  # type: ignore[valid-type]
    Result = create_model("UmbrellaSelection", umbrella_chapter_slugs=(list[SlugLit], ...))

    chap_block = "\n".join(f"  {c['slug']}\t{c['label'][:140]}" for c in chapters_to_send)
    user = (
        f"State: {state}\n\n"
        f"Chapters in this state's licensing hierarchy:\n{chap_block}\n\n"
        f"Return the slugs of umbrella / cross-cutting chapters only."
    )
    schema = Result.model_json_schema()
    system = (
        SYSTEM_PROMPT + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2)
    )

    log.info("[%s] %d chapters → asking %s", state, len(chapters_to_send), model)
    result = call_structured(
        model=model, system=system, user=user, schema_cls=Result,
        max_tokens=2000, max_retries=2, log_prefix=f"[{state}]", logger=log,
    )
    if result is None:
        return None

    # Resolve slugs to {slug, label, url}
    slug_to_info = {c["slug"]: c for c in chapters_to_send}
    resolved = []
    for slug in result.umbrella_chapter_slugs:  # type: ignore[attr-defined]
        info = slug_to_info[slug]
        resolved.append({
            "slug": slug,
            "label": info.get("label", ""),
            "url": info.get("url", ""),
            "source_title_url": info.get("source_title_url"),
        })

    record = {
        "state": state,
        "umbrella_chapters": resolved,
        "umbrella_chapter_slugs": [r["slug"] for r in resolved],
    }
    out_path.write_text(json.dumps(record, indent=2))
    log.info("[%s] -> %d umbrella chapters saved %s", state, len(resolved), out_path.name)
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="")
    ap.add_argument("--states", default="")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.state:
        targets = [args.state.upper()]
    elif args.states:
        targets = [s.strip().upper() for s in args.states.split(",") if s.strip()]
    else:
        targets = list(ALL_STATES)

    log.info("finding umbrella chapters for %d states", len(targets))
    for st in targets:
        try:
            find_for_state(st, args.model, args.force)
            time.sleep(PER_HOST_DELAY)
        except Exception:
            log.exception("[%s] crashed", st)


if __name__ == "__main__":
    main()
