"""Re-group an existing discovered/<profession>.json into plain-English
category labels chosen by Sonnet, replacing the hand-coded jargon labels
(advanced_tier, scope_inclusion, etc).

Surgical: preserves the existing field set + types + descriptions. Only the
`category` value changes. No re-extraction needed; frontend just regroups
on next build.

Usage:
  python -m pipeline.extract.recategorize_fields --profession podiatry
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field, create_model

from pipeline._env import load_env  # noqa: E402
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _llm import call_structured  # noqa: E402
from paths import DISCOVERED_DIR  # noqa: E402

DEFAULT_MODEL = "claude-sonnet-4-6"

SYSTEM = """\
Re-group a list of profession-specific licensure fields into plain-English
category labels. Goal: a non-expert reader scanning the modal grouping
should immediately understand what's in each group.

Rules:
  - 5 to 8 categories total. Don't over-fragment.
  - Use lowercase plain English. Spaces are fine. No snake_case, no jargon.
  - Examples of GOOD names: "extra credentials and tiered scope", "what they
    can do", "what they can't do", "where the work must happen", "drugs and
    anesthesia", "supervision and delegation".
  - Examples of BAD names: "advanced_tier", "scope_inclusion", "facility",
    "anatomy_or_procedure".
  - Keep similar fields together. If a field could fit two categories, pick
    the one that gives the cleanest grouping.
  - Every input field must appear in exactly one category.

Return JSON: { "categories": [ { "name": "...", "fields": ["field_name_1", ...] } ] }
"""


class Category(BaseModel):
    name: str = Field(description="plain-English category label, lowercase, no underscores")
    fields: list[str] = Field(description="exact field names from the input list")


class RegroupResult(BaseModel):
    categories: list[Category]


def regroup(profession: str, model: str) -> None:
    path = DISCOVERED_DIR / f"{profession}.json"
    data = json.loads(path.read_text())
    fields = data.get("fields", [])
    if not fields:
        sys.exit(f"no fields in {path}")

    valid_field_names = [f["name"] for f in fields]
    # Constrain categories[].fields to a Literal of actual field names so
    # the LLM can't invent or drop fields.
    from typing import Literal as TLiteral
    field_lit = TLiteral[tuple(valid_field_names)]  # type: ignore[valid-type]
    Cat = create_model(
        "Category",
        name=(str, ...),
        fields=(list[field_lit], ...),  # type: ignore[valid-type]
    )
    Result = create_model("RegroupResult", categories=(list[Cat], ...))

    prompt = "Fields to group:\n\n"
    for f in fields:
        prompt += f"- {f['name']}: {f.get('description', '')}\n"

    result = call_structured(
        model=model,
        system=SYSTEM,
        user=prompt,
        schema_cls=Result,
        embed_schema=True,
        max_tokens=4000,
    )
    if result is None:
        sys.exit("LLM call failed after retries")

    # Build field_name → category_name map and apply
    name_to_cat: dict[str, str] = {}
    for cat in result.categories:
        for fn in cat.fields:
            name_to_cat[fn] = cat.name

    missing = [f["name"] for f in fields if f["name"] not in name_to_cat]
    if missing:
        sys.exit(f"LLM dropped {len(missing)} field(s): {missing[:5]}…")

    for f in fields:
        f["category"] = name_to_cat[f["name"]]

    path.write_text(json.dumps(data, indent=2))
    print(f"Re-grouped {len(fields)} fields in {path.name} into {len(result.categories)} categories:")
    for cat in result.categories:
        print(f"  {cat.name} ({len(cat.fields)})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()
    regroup(args.profession.lower(), args.model)


if __name__ == "__main__":
    main()
