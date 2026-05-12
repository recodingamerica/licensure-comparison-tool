"""Like map_state_sections.py but uses cached section body excerpts instead
of just labels. Run fetch_section_bodies.py first.

When the bodies cache exists, each section is sent to Sonnet as
(slug, label, first 300 chars of body). For generic-labeled sections like
"§37:611. Definitions", the body excerpt makes it clear which profession
the section covers.

Falls back to label-only for sections without a cached body.

Usage:
  python -m pipeline.discover.map_state_sections_v2 --state LA
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
from typing import Literal as TLiteral

import yaml
from pydantic import BaseModel, Field, ValidationError, create_model

from pipeline._env import load_env  # noqa: E402
load_env()

import litellm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import HIERARCHY_DIR, RESULTS_DIR, CONFIG_DIR, LOGS_DIR  # noqa: E402

SECTION_MAPS_DIR = RESULTS_DIR / "section_maps"
BODIES_DIR = RESULTS_DIR / "section_bodies"
SECTION_MAPS_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOGS_DIR / "map_state_sections_v2.log"

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("map_state_sections_v2")


SYSTEM_PROMPT = """\
You are mapping every section in a state's licensing title to the regulated
profession it covers. The state lists its sections in one flat numbered run
within a single title; most professions live in contiguous section ranges.

You will see:
  1. A list of profession identifiers (snake_case keys + display names + patterns).
  2. For every section: its slug, its label, AND a short excerpt from its body.

The body excerpt is the most-discriminating signal. A section labeled just
"Definitions" or "License required" can belong to any profession; the body
will tell you which.

Your job: for each profession, return the list of section slugs that belong
to that profession's licensing scheme. Use only slugs from the input list.

Rules:
  - Each section can map to at most one profession. If unclear, leave it out.
  - Don't include sections about a board, fund, or fee that's clearly
    cross-cutting administrative — only include sections that are part of
    a profession's licensure / scope / discipline.
  - Empty list is a valid answer if a profession isn't regulated under
    this title at all.
  - Don't invent profession names — use only the IDs supplied.
  - Don't invent slugs.

Return JSON only. No prose, no fences.
"""


_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```")


def _extract_json(raw: str) -> str:
    m = _JSON_FENCE.search(raw or "")
    s = m.group(1).strip() if m else (raw or "").strip()
    if s.startswith("{"):
        return s
    i, j = s.find("{"), s.rfind("}")
    return s[i:j + 1] if i >= 0 and j > i else s


def map_state_with_bodies(state: str, professions: dict, model: str) -> dict | None:
    h_path = HIERARCHY_DIR / f"{state}.json"
    bodies_path = BODIES_DIR / f"{state}.json"
    if not h_path.exists():
        sys.exit(f"missing {h_path}")
    if not bodies_path.exists():
        sys.exit(f"missing {bodies_path} — run fetch_section_bodies.py first")

    h = json.loads(h_path.read_text())
    bodies = json.loads(bodies_path.read_text()).get("bodies", {})
    sections = h.get("chapters", [])
    if not sections:
        return None

    slug_to_url = {s["slug"]: s["url"] for s in sections}
    valid_slugs = list(slug_to_url.keys())
    valid_profs = list(professions.keys())

    SlugLit = TLiteral[tuple(valid_slugs)]  # type: ignore[valid-type]
    ProfLit = TLiteral[tuple(valid_profs)]  # type: ignore[valid-type]
    Mapping = create_model(
        "ProfessionMapping",
        profession=(ProfLit, ...),
        section_slugs=(list[SlugLit], ...),  # type: ignore[valid-type]
    )
    Result = create_model("StateMap", mappings=(list[Mapping], ...))

    prof_block = "\n".join(
        f"- {k}: {v.get('display','')} (patterns: {', '.join(v.get('patterns', []))})"
        for k, v in professions.items()
    )
    sec_lines = []
    bodies_count = 0
    for s in sections:
        slug = s["slug"]
        label = s["label"][:120]
        body = bodies.get(slug, {}).get("excerpt", "") or ""
        if body:
            bodies_count += 1
        line = f"  {slug}\t{label}"
        if body:
            line += f"\n    body: {body[:280]}"
        sec_lines.append(line)
    sec_block = "\n".join(sec_lines)
    log.info("[%s] %d sections, %d with bodies, %d professions → asking Sonnet",
             state, len(sections), bodies_count, len(professions))

    user = (
        f"State: {state}\nTitle URL: {h.get('target_url')}\n\n"
        f"Available profession identifiers:\n{prof_block}\n\n"
        f"Sections in this state's title (slug, label, body excerpt):\n{sec_block}\n"
    )

    schema = Result.model_json_schema()
    sys_with_schema = (
        SYSTEM_PROMPT + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2) + "\n\nReturn ONLY a single JSON object."
    )
    from pipeline._llm import call_structured
    result = call_structured(
        model=model, system=sys_with_schema, user=user, schema_cls=Result,
        max_tokens=16000, max_retries=MAX_RETRIES, log_prefix=f"[{state}]", logger=log,
    )
    if result is None:
        return None

    out = {"state": state, "title_url": h.get("target_url"), "v": "v2-with-bodies", "professions": {}}
    for mapping in result.mappings:  # type: ignore[attr-defined]
        urls = [slug_to_url[sl] for sl in mapping.section_slugs]
        if urls:
            out["professions"][mapping.profession] = {
                "section_count": len(urls),
                "section_url_list": urls,
                "label": f"{state} {h.get('target_url','').rstrip('/').rsplit('/',1)[-1]} — {mapping.profession} (LLM-mapped v2)",
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
    result = map_state_with_bodies(state, professions, args.model)
    if not result:
        return
    out_path = SECTION_MAPS_DIR / f"{state}_v2.json"
    out_path.write_text(json.dumps(result, indent=2))
    n = len(result["professions"])
    s = sum(p["section_count"] for p in result["professions"].values())
    log.info("[%s] mapped %d professions across %d sections → %s", state, n, s, out_path.name)


if __name__ == "__main__":
    main()
