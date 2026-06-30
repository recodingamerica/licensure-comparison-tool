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
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# Load shared .env
from pipeline._env import load_env  # noqa: E402
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _llm import call_structured  # noqa: E402
from paths import TRIMMED_DIR, DISCOVERED_DIR, LOGS_DIR  # noqa: E402
from _records import record_files  # noqa: E402

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


def build_corpus(profession: str) -> tuple[str, list[str]]:
    """Concatenate per-state trimmed corpora, prefixed with state header.
    Returns (corpus_text, states_included)."""
    in_dir = TRIMMED_DIR / profession
    if not in_dir.exists():
        sys.exit(f"missing input dir: {in_dir}")
    parts = []
    states = []
    for path in record_files(in_dir):
        d = json.loads(path.read_text())
        if not d.get("sections"):
            continue
        states.append(d["state"])
        parts.append(f"\n========== STATE: {d['state']} ==========\n")
        for sec in d["sections"]:
            parts.append(f"\n[{sec.get('citation','')}] {sec.get('label','')}\n{sec.get('text','')}\n")
    return "".join(parts), states


def call_model(model: str, system: str, user: str) -> DiscoveredSchema | None:
    return call_structured(
        model=model,
        system=system,
        user=user,
        schema_cls=DiscoveredSchema,
        embed_schema=True,
        max_tokens=16000,
        max_retries=MAX_RETRIES,
        backoff_base=2.0,
        logger=log,
    )


def write_markdown_preview(schema: DiscoveredSchema, path: Path) -> None:
    lines = [f"# Discovered fields — {schema.profession}", ""]
    by_cat: dict[str, list[DiscoveredField]] = {}
    for f in schema.fields:
        # category is plain-English str per the prompt (no Enum). Older runs
        # used an Enum here; defensive .value access for those cases.
        cat = f.category.value if hasattr(f.category, "value") else f.category
        by_cat.setdefault(cat, []).append(f)
    for cat, fields in by_cat.items():
        lines.append(f"## {cat}")
        lines.append("")
        for f in fields:
            type_str = f.type.value if hasattr(f.type, "value") else f.type
            if (f.type == FieldType.ENUM if hasattr(f.type, "ENUM") else f.type == "enum") and f.enum_values:
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
    ap.add_argument("--max-states", type=int, default=10,
                    help="Cap states sent to schema-discovery LLM. Default 10. "
                    "Large corpora (e.g. medicine, all 14 states ~1M tokens) exceed "
                    "context. A representative sample is enough to derive fields.")
    args = ap.parse_args()

    profession = args.profession.lower()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")

    corpus, states = build_corpus(profession)
    if len(states) > args.max_states:
        log.info("sampling %d / %d states for schema discovery (corpus would be too large)",
                 args.max_states, len(states))
        # Re-build corpus from first N states (alphabetical — consistent across runs)
        kept = set(states[:args.max_states])
        states_kept = []
        parts = []
        for path in record_files(TRIMMED_DIR / profession):
            d = json.loads(path.read_text())
            if d["state"] not in kept:
                continue
            if not d.get("sections"):
                continue
            states_kept.append(d["state"])
            parts.append(f"\n========== STATE: {d['state']} ==========\n")
            for sec in d["sections"]:
                parts.append(f"\n[{sec.get('citation','')}] {sec.get('label','')}\n{sec.get('text','')}\n")
        corpus = "".join(parts)
        states = states_kept

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
