"""Pass 1b: aggregate trimmed text across states → discover profession-specific
fields not already covered by the universal base model.

Inputs:  extract/results/trimmed/<profession>/<STATE>.json (cross-state)
         extract/standard_model.py (so the LLM doesn't duplicate)
Outputs: extract/results/discovered/<profession>.json
         extract/results/discovered/<profession>.md  (human-readable preview)

Usage:
  python discover_schema.py --profession podiatry [--model claude-sonnet-4-6]
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
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

# Load shared .env
from pipeline._env import load_env  # noqa: E402
load_env()

import litellm  # noqa: E402

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import TRIMMED_DIR, DISCOVERED_DIR, LOGS_DIR  # noqa: E402

LOG_PATH = LOGS_DIR / "discover_schema.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DISCOVERED_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("discover_schema")


from _prompts import load_prompt  # noqa: E402

SYSTEM_PROMPT = load_prompt("discover_schema")


class FieldType(str, __import__("enum").Enum):
    BOOL = "bool"
    INT = "int"
    STR = "str"
    LIST_STR = "list[str]"
    ENUM = "enum"


class DiscoveredField(BaseModel):
    name: str = Field(description="snake_case field name, profession-agnostic when possible")
    category: str = Field(
        description=(
            "Plain-English category label, lowercase, no underscores or jargon. "
            "Pick something a non-expert could understand at a glance. Aim for "
            "5-8 categories total across the field set, with similar fields grouped. "
            "Examples of GOOD names: 'what they can treat and where on the body', "
            "'extra credentials and tiered scope', 'drugs and anesthesia', "
            "'supervision and delegation'. Examples of BAD names: 'advanced_tier', "
            "'scope_inclusion', 'facility'."
        ),
    )
    type: FieldType
    enum_values: list[str] | None = Field(
        default=None,
        description="If type=enum, the allowed values normalized across the corpus",
    )
    description: str = Field(description="One-sentence semantic description")
    sample_quote: str = Field(description="Verbatim statutory phrase from one state that anchors this field")
    sample_state: str = Field(description="Two-letter state code where sample_quote appears")
    states_supporting: list[str] = Field(description="State codes where this dimension appears (≥2)")


class DiscoveredSchema(BaseModel):
    profession: str
    fields: list[DiscoveredField]


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


def build_corpus(profession: str) -> tuple[str, list[str]]:
    """Concatenate per-state trimmed corpora, prefixed with state header.
    Returns (corpus_text, states_included)."""
    in_dir = TRIMMED_DIR / profession
    if not in_dir.exists():
        sys.exit(f"missing input dir: {in_dir}")
    parts = []
    states = []
    for path in sorted(in_dir.glob("*.json")):
        if path.name.startswith("_"):
            continue
        d = json.loads(path.read_text())
        if not d.get("sections"):
            continue
        states.append(d["state"])
        parts.append(f"\n========== STATE: {d['state']} ==========\n")
        for sec in d["sections"]:
            parts.append(f"\n[{sec.get('citation','')}] {sec.get('label','')}\n{sec.get('text','')}\n")
    return "".join(parts), states


def call_model(model: str, system: str, user: str) -> DiscoveredSchema | None:
    schema = DiscoveredSchema.model_json_schema()
    sys_with_schema = (
        system
        + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2)
        + "\n\nReturn ONLY a single JSON object. No prose, no code fences."
    )
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            log.info("calling %s (attempt %d)", model, attempt + 1)
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
            return DiscoveredSchema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = e
            log.warning("parse attempt %d failed: %s", attempt + 1, str(e)[:300])
        except Exception as e:
            last_err = e
            log.warning("api attempt %d failed: %s", attempt + 1, str(e)[:300])
        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)
    log.error("giving up: %s", str(last_err)[:200])
    return None


def write_markdown_preview(schema: DiscoveredSchema, path: Path) -> None:
    lines = [f"# Discovered fields — {schema.profession}", ""]
    by_cat: dict[str, list[DiscoveredField]] = {}
    for f in schema.fields:
        by_cat.setdefault(f.category.value, []).append(f)
    for cat, fields in by_cat.items():
        lines.append(f"## {cat}")
        lines.append("")
        for f in fields:
            type_str = f.type.value
            if f.type == FieldType.ENUM and f.enum_values:
                type_str = f"enum[{', '.join(f.enum_values)}]"
            states_str = ", ".join(sorted(f.states_supporting)[:8])
            if len(f.states_supporting) > 8:
                states_str += f", … (+{len(f.states_supporting)-8})"
            lines.append(f"### `{f.name}` — {type_str}")
            lines.append(f"- **what:** {f.description}")
            lines.append(f"- **states:** {states_str}")
            lines.append(f"- **sample ({f.sample_state}):** \"{f.sample_quote}\"")
            lines.append("")
    path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    profession = args.profession.lower()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    corpus, states = build_corpus(profession)
    log.info("aggregating corpus: %d states, %d chars (~%d tokens)",
             len(states), len(corpus), len(corpus) // 4)

    user_msg = f"Profession: {profession}\nStates included: {', '.join(states)}\n\nTrimmed statute text:\n{corpus}"

    schema = call_model(args.model, SYSTEM_PROMPT, user_msg)
    if schema is None:
        sys.exit("LLM call failed")

    out_json = DISCOVERED_DIR / f"{profession}.json"
    out_md = DISCOVERED_DIR / f"{profession}.md"
    out_json.write_text(schema.model_dump_json(indent=2))
    write_markdown_preview(schema, out_md)
    log.info("wrote %s (%d fields) and %s", out_json, len(schema.fields), out_md)


if __name__ == "__main__":
    main()
