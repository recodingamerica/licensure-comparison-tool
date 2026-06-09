# suggest_scope_rules.py — Build Plan

## What This Script Does

`pipeline/discover/suggest_scope_rules.py` — LLM-assisted StateScopeRules generator.

Given a state abbreviation, it:
1. Loads `pipeline/results/umbrella_text/<STATE>.json`
2. Filters to anchor sections only (ANCHOR_LABEL_RE from `_scope_rules.py`)
3. Calls Claude via Anthropic SDK (tool_use) with the anchor text + few-shot examples
4. Gets back a validated Pydantic `ScopeRulesProposal` with all the regex fields
5. Prints rendered Python code for the new `StateScopeRules` entry
6. `--apply` flag appends the entry to `_scope_rules.py`
7. `--run` flag runs `assign_umbrella_scope.py` and shows triage stats

## Pydantic Schema

```python
from typing import Literal
from pydantic import BaseModel, model_validator
import re

class UniversalPattern(BaseModel):
    pattern: str   # raw regex string (no re.compile)
    target: Literal["title", "chapter", "part"]

class ScopeRulesProposal(BaseModel):
    universal_patterns: list[UniversalPattern]
    trigger_patterns: list[str]
    chapter_cite_pattern: str
    section_cite_pattern: str
    slug_prefix: str = "chapter"
    range_chapter_pattern: str | None = None
    profession_name_trigger_patterns: list[str] = []
    rationale: str

    @model_validator(mode="after")
    def validate_regex_strings(self) -> "ScopeRulesProposal":
        patterns = (
            [p.pattern for p in self.universal_patterns]
            + self.trigger_patterns
            + [self.chapter_cite_pattern, self.section_cite_pattern]
            + ([self.range_chapter_pattern] if self.range_chapter_pattern else [])
            + self.profession_name_trigger_patterns
        )
        for p in patterns:
            try:
                re.compile(p, re.I)
            except re.error as e:
                raise ValueError(f"Invalid regex {p!r}: {e}") from e
        return self
```

## Anthropic SDK Pattern (tool_use)

```python
import anthropic
import json

client = anthropic.Anthropic()

tool_schema = {
    "name": "propose_scope_rules",
    "description": "Propose StateScopeRules regex patterns for a state's umbrella legislation",
    "input_schema": ScopeRulesProposal.model_json_schema(),
}

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=4096,
    tools=[tool_schema],
    tool_choice={"type": "tool", "name": "propose_scope_rules"},
    messages=[
        {"role": "user", "content": prompt}
    ],
    system=system_prompt,
)

# Extract tool_use block
tool_use_block = next(b for b in response.content if b.type == "tool_use")
raw = tool_use_block.input   # already a dict, not a string
proposal = ScopeRulesProposal(**raw)
```

## System Prompt Contents

1. Field-by-field documentation from `_scope_rules.py` docstrings
2. Two few-shot examples (UT and FL) showing hand-written rules and what they produce
3. How `ANCHOR_LABEL_RE` works (what sections are passed in)
4. Instruction: "Return patterns that are as general as possible — avoid hard-coding chapter numbers in universal_patterns unless the statute literally says them"

## CLI Interface

```
python -m pipeline.discover.suggest_scope_rules --state NY
python -m pipeline.discover.suggest_scope_rules --state OH --apply
python -m pipeline.discover.suggest_scope_rules --state AL --apply --run
```

## Output Format

Prints:
```
=== Proposed StateScopeRules for NY ===

NY_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"...", re.I), "title"),
        ...
    ),
    ...
)
--- Rationale ---
<model's explanation>
```

With `--run` appended:
```
=== Walker triage for NY ===
  sections: 412
  universal: 289  enumerated: 98  undetermined: 25
  triage entries: 12
```

## Test Validation Plan

Run against UT, FL, CO, IA and compare to hand-written rules:
- Universal patterns should fire on same anchor sections
- Section counts per scope_source should be in the same ballpark
- Zero triage differences is unrealistic; flag big divergences

## File Locations

- Script: `pipeline/discover/suggest_scope_rules.py`
- Scope rules: `pipeline/discover/_scope_rules.py` (read + optionally append)
- Umbrella text input: `pipeline/results/umbrella_text/<STATE>.json`
- Scope output: `pipeline/results/umbrella_scope/<STATE>.json`

## Dependencies

```bash
pip install anthropic pydantic
```

`ANTHROPIC_API_KEY` must be set in env.

## Notes

- Only anchor sections are passed to LLM (filtered by ANCHOR_LABEL_RE) — keeps token count low
- For big states like WI (234K tokens), anchor sections may still be large — consider truncating text to first 2000 chars per section
- State-specific context to include in prompt: the state abbreviation, full state name, and a note about the citation style we expect (e.g. "NY uses §-prefixed citations")
- The `--apply` flag should append the new `XX_RULES = StateScopeRules(...)` block AND add `"XX": XX_RULES` to `STATE_RULES`

## Status

**Not yet built.** This is the next task.

The UI work (per-cell unverified flagging, 3-line row height, hover tooltips, scope_definition column) is complete and committed.
