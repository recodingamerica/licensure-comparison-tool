"""Per-state regex bundles consumed by `assign_umbrella_scope.py`.

Each `StateScopeRules` instance is the only state-specific knob the scope
walker needs: what universal-applicability phrasing looks like, what
phrases trigger a practice-act enumeration, and how that state writes
chapter/section citations.

The walker itself is state-agnostic. Adding a new state means adding one
entry to `STATE_RULES`, not changing any control flow.

A few cross-state regularities live in this module too (the anchor-label
detector and the `As used in this <title|chapter|part>` target detector)
because every state we've probed uses these without variation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class StateScopeRules:
    # (pattern, scope_target). Scope target = "title" | "chapter" | "part" — the
    # specificity at which the universal scope claim applies. Order matters:
    # more-specific phrasings first.
    universal_patterns: tuple[tuple[re.Pattern, str], ...]

    # Phrases that introduce a list of practice-act citations
    # (e.g. "licensed under", "licensed to practice"). When the walker finds
    # one of these inside an anchor section, it scans the next `scan_window`
    # characters for chapter/section citations.
    trigger_patterns: tuple[re.Pattern, ...]

    # How this state writes chapter citations. Group 1 = the chapter token
    # (e.g. "5a", "31b", "457"). The slug form is `chapter-<group1>`.
    chapter_cite_pattern: re.Pattern

    # Section citations that resolve to a chapter (the chapter token is what
    # we look up in the reverse-index, not the section number).
    section_cite_pattern: re.Pattern

    scan_window: int = 3000


# Cross-state regularities — these have looked the same in every umbrella
# text we've probed so far (UT, FL, CO, NE, MA).
ANCHOR_LABEL_RE = re.compile(
    r"(applicability|definitions|short title|scope of (?:chapter|part|article|title))",
    re.I,
)
AS_USED_RE = re.compile(r"as used in this (title|chapter|part)", re.I)

# Section-label keywords that hint a section narrows to specific professions.
# Used only to flag for triage; the walker doesn't act on these in the first
# pass (sections still inherit chapter default).
NARROW_LABEL_HINTS = re.compile(
    r"(psychiatr|prescrib|pharmac|nurse|dentist|optometr|physician|osteopath|"
    r"podiatr|veterinar|cosmetic medical|naturopath|chiropract|midwif|"
    r"physical therap|occupational therap|psycholog|massage|funeral|accountan|"
    r"architect|engineer|surveyor|interior design)",
    re.I,
)


# ---------------------------------------------------------------------------
# Utah (Title 58, the canonical practice-act title; plus Ch 1b in Title 13)
# ---------------------------------------------------------------------------
UT_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), "title"),
        (re.compile(r"as used in this title\b", re.I), "title"),
        (re.compile(r"any holder of a license[^.]*under this title", re.I), "title"),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), "chapter"),
        (re.compile(r"applies to (?:any|every) regulation of an occupation", re.I), "chapter"),
        (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), "part"),
    ),
    trigger_patterns=(
        # "licensed to practice:" (UT Ch 4a § 102), "licensed under" (cross-cuts),
        # "licensed as" (UT Ch 88 § 201 — "is currently licensed as ... under Chapter X").
        re.compile(r"licensed\s+(?:to\s+practice|as|under)\b", re.I),
    ),
    # "Title 58, Chapter 5a" / "Chapter 5a" — single lowercase letter suffix optional.
    chapter_cite_pattern=re.compile(r"\b(?:Title\s+58,?\s+)?Chapter\s+(\d+[a-z]?)\b", re.I),
    # "Section 58-31b-301" / "Subsection 58-17b-102(2)(d)" — chapter token in group 1.
    section_cite_pattern=re.compile(r"\b(?:Sub)?[Ss]ection\s+58-(\d+[a-z]?)-"),
)


# ---------------------------------------------------------------------------
# Florida (Ch 455 = DBPR universal; Ch 456 = DOH health professions)
# ---------------------------------------------------------------------------
# Note on FL § 455.017's "applies only to the regulation of professions by the
# department": that's DBPR-scoped, not universal in our sense (DBPR ≠ DOH).
# Intentionally not listed as universal — surfaces as UNDETERMINED in triage so
# we can decide together whether to narrow it to DBPR professions or just
# include it broadly.
FL_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), "chapter"),
        (re.compile(r"as used in this chapter\b[^.]*\bevery (?:person|profession)", re.I), "chapter"),
    ),
    trigger_patterns=(
        # FL § 456.001(4): "any person licensed under chapter 457; chapter 458; ..."
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
    ),
    # FL uses bare "chapter NNN" (no "Title X," prefix). Slug form is `chapter-NNN`.
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+)\b", re.I),
    # FL section cite: "s. 456.001", "§ 456.001(4)" — chapter token = "456".
    section_cite_pattern=re.compile(r"(?:§|s\.)\s*(\d+)\.\d+", re.I),
)


STATE_RULES: dict[str, StateScopeRules] = {
    "UT": UT_RULES,
    "FL": FL_RULES,
}
