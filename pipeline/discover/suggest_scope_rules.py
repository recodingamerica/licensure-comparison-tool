"""LLM-assisted StateScopeRules generator.

Given a state abbreviation:
1. Loads pipeline/results/umbrella_text/<STATE>.json
2. Filters to anchor sections (ANCHOR_LABEL_RE from _scope_rules.py)
3. Calls Claude (claude-opus-4-7) via Anthropic SDK (tool_use) with anchor text + few-shot
4. Validates the response with Pydantic ScopeRulesProposal
5. Runs the scope walker in-memory to check quality; refines if too many undetermined
6. Prints rendered Python code for the new StateScopeRules entry
7. --apply appends the entry to _scope_rules.py
8. --run writes the official umbrella_scope/<STATE>.json to disk

Usage:
  python -m pipeline.discover.suggest_scope_rules --state NY
  python -m pipeline.discover.suggest_scope_rules --state OH --apply
  python -m pipeline.discover.suggest_scope_rules --state AL --apply --run
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, model_validator

# Load .env from repo root (CLAUDE_API_KEY → used as Anthropic api_key)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Suppress httpx request logging from the Anthropic SDK
logging.getLogger("httpx").setLevel(logging.WARNING)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR  # noqa: E402
from discover._scope_rules import ANCHOR_LABEL_RE, NARROW_LABEL_HINTS  # noqa: E402

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
SCOPE_RULES_PATH = Path(__file__).resolve().parent / "_scope_rules.py"
REPO_ROOT = Path(__file__).resolve().parents[2]

# Truncate each section's text to keep token count manageable on large states
MAX_TEXT_PER_SECTION = 2000
# Max chars of text per undetermined section sent back in refinement pass
MAX_TEXT_PER_UNDET = 500
# Trigger a refinement call if this many non-narrow undetermined sections remain
UNDETERMINED_THRESHOLD = 5
# Max undetermined sections to include in refinement message
MAX_UNDET_IN_REFINEMENT = 10


# ---------------------------------------------------------------------------
# Pydantic schema for the LLM's proposed rules
# ---------------------------------------------------------------------------

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

    @field_validator(
        "trigger_patterns", "profession_name_trigger_patterns",
        "universal_patterns", mode="before",
    )
    @classmethod
    def _coerce_json_string_list(cls, v: object) -> object:
        # The model occasionally returns a list field as a JSON-encoded string
        # (e.g. trigger_patterns='["licensed\\\\s+under\\\\b", ...]'). Parse it
        # back into a real list before normal validation runs.
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
            except json.JSONDecodeError:
                return v
            if isinstance(parsed, list):
                return parsed
        return v

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


# ---------------------------------------------------------------------------
# State name lookup
# ---------------------------------------------------------------------------

STATE_NAME_MAP: dict[str, str] = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
}


# ---------------------------------------------------------------------------
# Few-shot examples embedded in the system prompt
# ---------------------------------------------------------------------------

_FEW_SHOT = """
=== FEW-SHOT EXAMPLE 1: Utah ===

State: UT (Utah)
Umbrella titles: Title 58 – Occupations and Professions; Chapter 1b in Title 13

Selected anchor sections (truncated):
  Section 58-1-102 – Definitions.
    "As used in this title: (1) 'Ablative procedure' means..."
    "...licensed under Chapter 4a..."
    "...licensed under Chapter 31b..."
  Section 13-1b-102 – Applicability.
    "This chapter applies to any regulation of an occupation that is
    administered by a state executive branch agency."
  Section 58-1-501 – Unlawful conduct.
    "...any holder of a license issued under this title..."

Resulting UT_RULES:
  universal_patterns:
    - ("this title applies to (?:any|every|all)\\b[^.]*", "title")
    - ("as used in this title\\b", "title")
    - ("any holder of a license[^.]*under this title", "title")
    - ("this chapter applies to (?:any|every|all)\\b[^.]*", "chapter")
    - ("applies to (?:any|every) regulation of an occupation", "chapter")
    - ("this part applies to (?:any|every|all)\\b[^.]*", "part")
  trigger_patterns:
    - "licensed\\s+(?:to\\s+practice|as|under)\\b"
  chapter_cite_pattern: "\\b(?:Title\\s+58,?\\s+)?Chapter\\s+(\\d+[a-z]?)\\b"
  section_cite_pattern: "\\b(?:Sub)?[Ss]ection\\s+58-(\\d+[a-z]?)-"
  slug_prefix: "chapter"

Rationale: Title 58 is UT's occupations title. Chapter 1 uses "As used in this title"
and applies universally. Chapter 1b uses "any regulation of an occupation." Section cites
look like "Section 58-31b-101" – the chapter token is the middle segment "31b". Chapter
cites look like "Chapter 5a" or "Title 58, Chapter 5a".

=== FEW-SHOT EXAMPLE 2: Florida ===

State: FL (Florida)
Umbrella: Chapter 455 (DBPR) and Chapter 456 (DOH)

Selected anchor sections (truncated):
  Section 455.001 – Definitions.
    "...any person licensed under chapter 457; chapter 458; chapter 459..."
  Section 456.001 – Definitions; application.
    "As used in this chapter..."
    "...licensed pursuant to chapter 457, chapter 458..."

Resulting FL_RULES:
  universal_patterns:
    - ("this chapter applies to (?:any|every|all)\\b[^.]*", "chapter")
    - ("as used in this chapter\\b[^.]*\\bevery (?:person|profession)", "chapter")
  trigger_patterns:
    - "licensed\\s+under\\b"
    - "licensed\\s+pursuant\\s+to\\b"
  chapter_cite_pattern: "\\bchapter\\s+(\\d+)\\b"
  section_cite_pattern: "(?:§|s\\.)\\s*(\\d+)\\.\\d+"
  slug_prefix: "chapter"

Rationale: FL writes bare "chapter NNN" cites. Section cites like "s. 456.001" or
"§ 456.001(4)" have the chapter number as the prefix before the dot. Universal patterns
are chapter-level since each umbrella chapter (455/456) applies to a different subset
of professions. The trigger phrases introduce enumeration lists of practice act chapters.
Note: FL § 455.017 says "This chapter applies only to the regulation of professions by
the department" — this is DBPR-scoped, NOT a universal pattern. It is deliberately
excluded so it surfaces in triage for manual review.
"""


def _build_system_prompt() -> str:
    return f"""You are an expert in state occupational licensing law. Your job is to analyze
anchor sections (Applicability / Definitions / Scope sections) from a state's umbrella
occupational licensing statute and propose regex patterns for a StateScopeRules object.

## StateScopeRules field documentation

**universal_patterns** – List of (pattern, target) pairs that match phrases asserting
the statute applies universally to all occupations/professions in the scope target.
  target="title"   → applies title-wide (all chapters of that title)
  target="chapter" → applies chapter-wide
  target="part"    → applies only within a specific part of a chapter
Examples of universal phrases:
  "This chapter applies to every...",
  "This part applies to any/every/all...",
  "any holder of a license issued under this title"
IMPORTANT: Make patterns as general as possible — avoid hard-coding specific chapter
numbers. More-specific (part/chapter-level) patterns should come before title-level ones.

**trigger_patterns** – Phrases that INTRODUCE a list of practice-act citations
(chapter or section cites that follow the trigger in the text). The walker scans
forward from the trigger location looking for chapter/section cites.
Examples: "licensed under", "licensed to practice", "licensed pursuant to"

**chapter_cite_pattern** – How this state writes chapter citations.
Group 1 MUST capture the chapter token (e.g., "5a", "31b", "457", "200").
The slug is formed as `<slug_prefix>-<group1_lowercased>`.
Examples: "\\bchapter\\s+(\\d+[a-z]?)\\b", "\\barticle\\s+(\\d+)\\b"

**section_cite_pattern** – Section citations that resolve to a chapter.
Group 1 MUST capture the chapter token (same token as chapter_cite_pattern group 1).
Examples: "\\b(?:Sub)?[Ss]ection\\s+58-(\\d+[a-z]?)-", "(?:§|s\\.)\\s*(\\d+)\\.\\d+"

**slug_prefix** – Prefix for reverse-index slugs. Default "chapter".
Use "article" only for states whose Justia slugs look like "article-200".

**range_chapter_pattern** – Optional. For when a single phrase covers a range of
chapter numbers (e.g., "applies to articles 200 to 315 of this title 12").
Groups 1 and 2 must capture the range start and end integers.

**profession_name_trigger_patterns** – Optional. Like trigger_patterns but the text
following the trigger lists PROFESSION NAMES rather than chapter citations.
(Iowa-style: "when applied to a physician and surgeon, podiatric physician, ...")
Example: "when\\s+applied\\s+to\\b"

## Cross-state patterns already handled (do NOT duplicate in universal_patterns)

The walker uses a cross-state AS_USED_RE that automatically detects scope target from:
  - "As used in this title/subtitle/chapter/part"
  - "For the purpose(s) of this title/subtitle/chapter/part"

These are already detected by the walker; the walker maps "subtitle" → title tier.
Do NOT put bare "as used in this chapter/title/subtitle" in universal_patterns —
the walker handles target detection from these phrases automatically. The one
exception: include it only when the text pairs it with an additional strong universal
signal, e.g. "as used in this chapter\\b[^.]*\\bevery (?:person|profession)".

## Critical: prefer narrow over broad

Err on the side of specificity. It is better to miss a section than to
falsely classify a non-universal section as universal.

- "As used in this chapter" alone is TOO BROAD — it appears in nearly every
  chapter and does not indicate universal applicability. Only include it if the
  text consistently pairs it with a strong universal signal such as "every person",
  "any holder of a license", or "all occupations". Prefer the narrower combined
  form, e.g.:
    "as used in this chapter\\b[^.]*\\bevery (?:person|profession)"

- "This chapter/title applies only to the regulation of professions by
  [a specific department or agency]" is NOT universal — it scopes the chapter
  to one regulatory body, not all professions. Do NOT include these as
  universal_patterns. Leave them as undetermined so they surface in triage.

- Do not add trigger_patterns for generic verbs like "regulated under" or
  "issued under" unless the anchor text clearly uses them to enumerate
  practice-act chapter citations. Stick to "licensed under", "licensed to
  practice", "licensed pursuant to", and close variants.

{_FEW_SHOT}"""


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_anchor_sections(state: str) -> list[dict]:
    """Load umbrella_text JSON and return anchor sections only."""
    src = UMBRELLA_TEXT_DIR / f"{state}.json"
    if not src.exists():
        raise SystemExit(f"Missing umbrella_text file: {src}")
    raw = json.loads(src.read_text())
    sections = raw.get("sections", [])
    anchors = [s for s in sections if ANCHOR_LABEL_RE.search(s.get("label", ""))]
    if not anchors:
        print(f"[warn] No anchor sections found for {state}; using first 20 sections", file=sys.stderr)
        anchors = sections[:20]
    return anchors


def _build_user_prompt(state: str, anchors: list[dict]) -> str:
    state_name = STATE_NAME_MAP.get(state, state)
    lines = [
        f"State: {state} ({state_name})",
        "",
        "Below are the anchor sections (Applicability / Definitions / Scope) from",
        f"this state's umbrella occupational licensing statute. Propose StateScopeRules",
        f"regex patterns for {state}.",
        "",
        "ANCHOR SECTIONS:",
        "=" * 60,
    ]
    for s in anchors:
        lines.append(f"\n--- {s.get('label', 'Unknown')} ---")
        text = s.get("text", "")
        if len(text) > MAX_TEXT_PER_SECTION:
            text = text[:MAX_TEXT_PER_SECTION] + "\n[...truncated...]"
        lines.append(text)
    lines.append("=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def _get_client() -> anthropic.Anthropic:
    import os
    api_key = os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    return anthropic.Anthropic(api_key=api_key)


def _tool_schema() -> dict:
    return {
        "name": "propose_scope_rules",
        "description": (
            "Propose StateScopeRules regex patterns for a state's umbrella "
            "occupational licensing statute."
        ),
        "input_schema": ScopeRulesProposal.model_json_schema(),
    }


def call_llm(state: str, anchors: list[dict]) -> tuple[ScopeRulesProposal, object]:
    """Call Claude to propose scope rules. Returns (proposal, raw_response)."""
    client = _get_client()

    print(f"Calling Claude for {state} ({len(anchors)} anchor sections)…")

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8192,
        tools=[_tool_schema()],
        tool_choice={"type": "tool", "name": "propose_scope_rules"},
        messages=[{"role": "user", "content": _build_user_prompt(state, anchors)}],
        system=_build_system_prompt(),
    )

    tool_block = next((b for b in response.content if b.type == "tool_use"), None)
    if tool_block is None:
        raise SystemExit(
            f"Claude did not return a tool_use block.\n"
            f"stop_reason={response.stop_reason!r}\n"
            f"content types: {[b.type for b in response.content]}"
        )

    return ScopeRulesProposal(**tool_block.input), response


def refine_llm(
    state: str,
    anchors: list[dict],
    initial_response: object,
    undetermined: list[dict],
) -> ScopeRulesProposal:
    """Send undetermined sections back to the LLM for one refinement pass."""
    client = _get_client()

    tool_block = next(b for b in initial_response.content if b.type == "tool_use")

    lines = [
        f"The walker ran with those proposed rules for {state}.",
        f"{len(undetermined)} sections ended up undetermined (after excluding profession-specific ones).",
        "",
        "Here are those sections — review their text and refine the patterns if any",
        "of them should be universal or enumerated. If they genuinely cannot be scoped",
        "from the anchor text, keep the patterns as-is.",
        "",
    ]
    for s in undetermined:
        lines.append(f"--- {s['label']} ({s['umbrella_chapter_slug']}) ---")
        lines.append(s["text"])
        lines.append("")

    print(f"  Refining — sending {len(undetermined)} undetermined sections back to Claude…")

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=8192,
        tools=[_tool_schema()],
        tool_choice={"type": "tool", "name": "propose_scope_rules"},
        messages=[
            {"role": "user", "content": _build_user_prompt(state, anchors)},
            {"role": "assistant", "content": initial_response.content},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_block.id, "content": "OK"},
                {"type": "text", "text": "\n".join(lines)},
            ]},
        ],
        system=_build_system_prompt(),
    )

    new_block = next((b for b in response.content if b.type == "tool_use"), None)
    if new_block is None:
        raise SystemExit("Claude did not return a tool_use block in refinement pass.")

    return ScopeRulesProposal(**new_block.input)


# ---------------------------------------------------------------------------
# In-memory walker (no file manipulation)
# ---------------------------------------------------------------------------

def proposal_to_rules(
    proposal: ScopeRulesProposal,
    excluded_chapter_slugs: set[str] | None = None,
) -> object:
    """Convert a ScopeRulesProposal to a StateScopeRules for in-memory use."""
    from discover._scope_rules import StateScopeRules as _StateScopeRules
    return _StateScopeRules(
        universal_patterns=tuple(
            (re.compile(p.pattern, re.I), p.target)
            for p in proposal.universal_patterns
        ),
        trigger_patterns=tuple(
            re.compile(p, re.I) for p in proposal.trigger_patterns
        ),
        chapter_cite_pattern=re.compile(proposal.chapter_cite_pattern, re.I),
        section_cite_pattern=re.compile(proposal.section_cite_pattern, re.I),
        slug_prefix=proposal.slug_prefix,
        range_chapter_pattern=(
            re.compile(proposal.range_chapter_pattern, re.I)
            if proposal.range_chapter_pattern else None
        ),
        profession_name_trigger_patterns=tuple(
            re.compile(p, re.I) for p in proposal.profession_name_trigger_patterns
        ),
        excluded_chapter_slugs=tuple(sorted(excluded_chapter_slugs or [])),
    )


def run_walker_in_memory(
    state: str,
    proposal: ScopeRulesProposal,
    excluded_chapter_slugs: set[str] | None = None,
) -> dict | None:
    """Run the scope walker with proposed rules injected in-process.

    Temporarily adds the proposed rules to STATE_RULES (the shared mutable dict),
    calls assign_for_state(), then restores the original entry. No files are touched.
    Returns None if the walker can't run (e.g. no profession_index for this state).
    """
    try:
        import discover.assign_umbrella_scope as walker_mod
    except ImportError as e:
        print(f"[warn] Could not import walker: {e}", file=sys.stderr)
        return None

    from discover._scope_rules import STATE_RULES as _STATE_RULES

    rules = proposal_to_rules(proposal, excluded_chapter_slugs)
    original = _STATE_RULES.get(state)
    _STATE_RULES[state] = rules

    # Suppress walker's logging during internal check
    walker_logger = logging.getLogger("assign_umbrella_scope")
    prev_level = walker_logger.level
    walker_logger.setLevel(logging.CRITICAL)

    try:
        result = walker_mod.assign_for_state(state)
    except SystemExit as e:
        print(f"[warn] Walker could not run for {state}: {e}", file=sys.stderr)
        result = None
    finally:
        walker_logger.setLevel(prev_level)
        if original is None:
            _STATE_RULES.pop(state, None)
        else:
            _STATE_RULES[state] = original

    return result


def detect_fully_undetermined_chapters(walker_result: dict) -> set[str]:
    """Return chapter slugs where every section is undetermined.

    These are almost always discover false positives (building codes, admin
    procedure acts, etc.) rather than scope rule failures.
    """
    from collections import defaultdict
    by_chap: dict[str, list[str]] = defaultdict(list)
    for s in walker_result["sections"]:
        by_chap[s["umbrella_chapter_slug"]].append(s["scope_source"])
    return {
        chap for chap, sources in by_chap.items()
        if all(src == "undetermined" for src in sources)
    }


def get_undetermined_with_text(
    state: str,
    walker_result: dict,
    excluded_slugs: set[str] | None = None,
) -> list[dict]:
    """Return non-narrow undetermined sections (excluding fully-undetermined
    chapters that are already slated for exclusion) with their text."""
    excluded_slugs = excluded_slugs or set()
    undetermined_urls = {
        s["url"] for s in walker_result["sections"]
        if s["scope_source"] == "undetermined"
        and s["umbrella_chapter_slug"] not in excluded_slugs
        and not NARROW_LABEL_HINTS.search(s.get("label", ""))
    }
    if not undetermined_urls:
        return []

    src = UMBRELLA_TEXT_DIR / f"{state}.json"
    raw = json.loads(src.read_text())

    result = []
    for s in raw.get("sections", []):
        if s.get("url") in undetermined_urls:
            text = s.get("text", "")
            result.append({
                "label": s.get("label", ""),
                "umbrella_chapter_slug": s.get("umbrella_chapter_slug", ""),
                "url": s.get("url", ""),
                "text": text[:MAX_TEXT_PER_UNDET] + ("…" if len(text) > MAX_TEXT_PER_UNDET else ""),
            })

    return result[:MAX_UNDET_IN_REFINEMENT]


# ---------------------------------------------------------------------------
# Code rendering
# ---------------------------------------------------------------------------

def render_rules_code(
    state: str,
    proposal: ScopeRulesProposal,
    excluded_chapter_slugs: set[str] | None = None,
) -> str:
    """Render the StateScopeRules Python source for this state."""
    state_name = STATE_NAME_MAP.get(state, state)

    def _r(pat: str) -> str:
        """Wrap a pattern string in a raw-string Python literal."""
        if '"' in pat:
            escaped = repr(pat)[1:-1]
            return f'"{escaped}"'
        return f'r"{pat}"'

    lines = [
        "",
        "",
        f"# {'−' * 75}",
        f"# {state_name}",
        f"# {'−' * 75}",
        f"{state}_RULES = StateScopeRules(",
        "    universal_patterns=(",
    ]

    for up in proposal.universal_patterns:
        lines.append(f"        (re.compile({_r(up.pattern)}, re.I), {up.target!r}),")

    lines.append("    ),")

    if proposal.trigger_patterns:
        lines.append("    trigger_patterns=(")
        for tp in proposal.trigger_patterns:
            lines.append(f"        re.compile({_r(tp)}, re.I),")
        lines.append("    ),")
    else:
        lines.append("    trigger_patterns=(),")

    lines.append(f"    chapter_cite_pattern=re.compile({_r(proposal.chapter_cite_pattern)}, re.I),")
    lines.append(f"    section_cite_pattern=re.compile({_r(proposal.section_cite_pattern)}, re.I),")

    if proposal.slug_prefix != "chapter":
        lines.append(f"    slug_prefix={proposal.slug_prefix!r},")

    if proposal.range_chapter_pattern:
        lines.append(
            f"    range_chapter_pattern=re.compile({_r(proposal.range_chapter_pattern)}, re.I),"
        )

    if proposal.profession_name_trigger_patterns:
        lines.append("    profession_name_trigger_patterns=(")
        for ptp in proposal.profession_name_trigger_patterns:
            lines.append(f"        re.compile({_r(ptp)}, re.I),")
        lines.append("    ),")

    if excluded_chapter_slugs:
        slugs_repr = ", ".join(repr(s) for s in sorted(excluded_chapter_slugs))
        lines.append(f"    # Auto-detected: 100% undetermined — not occupational licensing chapters")
        lines.append(f"    excluded_chapter_slugs=({slugs_repr},),")

    lines.append(")")
    return "\n".join(lines)


def print_proposal(state: str, proposal: ScopeRulesProposal, code: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"=== Proposed StateScopeRules for {state} ===")
    print("=" * 60)
    print(code)
    print("\n--- Rationale ---")
    print(proposal.rationale)
    print()


# ---------------------------------------------------------------------------
# Apply to _scope_rules.py
# ---------------------------------------------------------------------------

def apply_rules(state: str, code: str) -> None:
    """Append the new rules to _scope_rules.py and add to STATE_RULES dict."""
    content = SCOPE_RULES_PATH.read_text()

    if f'"{state}": {state}_RULES' in content:
        print(f"[warn] {state}_RULES already present in _scope_rules.py — skipping --apply",
              file=sys.stderr)
        return

    state_rules_re = re.compile(
        r"(STATE_RULES: dict\[str, StateScopeRules\] = \{)",
        re.MULTILINE,
    )
    m = state_rules_re.search(content)
    if not m:
        raise SystemExit("Could not locate STATE_RULES dict in _scope_rules.py")

    insert_pos = m.start()
    new_content = content[:insert_pos] + code + "\n\n\n" + content[insert_pos:]

    search_from = insert_pos + len(code) + 3
    closing_re = re.compile(r"^}\s*$", re.MULTILINE)
    m2 = closing_re.search(new_content, search_from)
    if not m2:
        raise SystemExit("Could not locate closing brace of STATE_RULES dict")

    state_entry = f'    "{state}": {state}_RULES,\n'
    new_content = new_content[: m2.start()] + state_entry + new_content[m2.start():]

    SCOPE_RULES_PATH.write_text(new_content)
    print(f"[apply] Appended {state}_RULES to {SCOPE_RULES_PATH.name}")
    print(f'[apply] Added "{state}": {state}_RULES to STATE_RULES')


# ---------------------------------------------------------------------------
# Run scope walker (writes official output to disk)
# ---------------------------------------------------------------------------

def run_scope_walker(state: str) -> None:
    """Run assign_umbrella_scope.py and print triage stats."""
    print(f"\n=== Walker triage for {state} ===")
    result = subprocess.run(
        [sys.executable, "-m", "pipeline.discover.assign_umbrella_scope", "--state", state],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        print("[error] assign_umbrella_scope failed:")
        stderr = result.stderr or "(no stderr)"
        print(stderr[-2000:])
        return
    for line in result.stdout.splitlines():
        if any(kw in line for kw in ["Wrote", "section", "scope_source", "triage"]):
            print(" ", line.strip())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="LLM-assisted StateScopeRules generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--state", required=True, help="Two-letter state abbreviation (e.g. NY)")
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Append the proposed rules to _scope_rules.py",
    )
    ap.add_argument(
        "--run",
        action="store_true",
        help="Write official umbrella_scope/<STATE>.json to disk (implies --apply has run)",
    )
    args = ap.parse_args()
    state = args.state.upper()

    anchors = load_anchor_sections(state)
    print(f"Loaded {len(anchors)} anchor sections for {state}")

    proposal, initial_response = call_llm(state, anchors)

    # Run walker in-memory to check quality and optionally refine
    print("Running walker check on proposed rules…")
    walker_result = run_walker_in_memory(state, proposal)
    excluded_slugs: set[str] = set()

    if walker_result is not None:
        # Detect 100%-undetermined chapters (discover false positives) and
        # exclude them before the refinement check so they don't pollute it.
        excluded_slugs = detect_fully_undetermined_chapters(walker_result)
        if excluded_slugs:
            print(f"  Auto-excluding {len(excluded_slugs)} fully-undetermined chapter(s): {sorted(excluded_slugs)}")
            walker_result = run_walker_in_memory(state, proposal, excluded_slugs)

        undetermined = get_undetermined_with_text(state, walker_result, excluded_slugs)
        n_undet = len(undetermined)
        counts = walker_result["scope_source_counts"] if walker_result else {}

        if n_undet > UNDETERMINED_THRESHOLD:
            print(f"  {n_undet} non-narrow undetermined sections — triggering refinement pass…")
            proposal = refine_llm(state, anchors, initial_response, undetermined)
            walker_result = run_walker_in_memory(state, proposal, excluded_slugs)
            if walker_result:
                counts = walker_result["scope_source_counts"]
                n_undet_after = len(get_undetermined_with_text(state, walker_result, excluded_slugs))
                print(f"  After refinement: {n_undet_after} non-narrow undetermined")
        else:
            print(f"  {n_undet} non-narrow undetermined — no refinement needed")

        if not counts:
            print(
                "\n[ERROR] Walker produced zero classified sections — the umbrella_text "
                "for this state may be from the wrong part of the code, or the "
                "profession_index has no matching chapters. Fix the upstream data "
                "before applying these rules.",
                file=sys.stderr,
            )
        print(f"  scope_source counts: {counts}")
    else:
        print("  (walker check skipped — no profession_index for this state yet)")

    code = render_rules_code(state, proposal, excluded_slugs)
    print_proposal(state, proposal, code)

    if args.apply:
        apply_rules(state, code)

    if args.run:
        if not args.apply:
            print("[warn] --run without --apply: running walker with existing rules (if any)")
        run_scope_walker(state)


if __name__ == "__main__":
    main()
