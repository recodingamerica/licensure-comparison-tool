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
    # (e.g. "5a", "31b", "457"). The slug form is `<slug_prefix>-<group1>`.
    chapter_cite_pattern: re.Pattern

    # Section citations that resolve to a chapter (the chapter token is what
    # we look up in the reverse-index, not the section number).
    section_cite_pattern: re.Pattern

    # Prefix used to construct reverse-index slugs from cite tokens. UT and FL
    # use "chapter"; CO uses "article" (CO's profession_index slugs look like
    # `article-200` because that's how Justia names them).
    slug_prefix: str = "chapter"

    # Optional: pattern that matches a *range* of chapter cites in one go,
    # e.g. CO Article 30 § 12-30-101 says "applies to articles 200 to 315 of
    # this title 12". Group 1 = range start, Group 2 = range end. When matched,
    # the walker enumerates every integer in [start, end] and looks each up
    # as `<slug_prefix>-<n>`. Only the slugs that exist in the reverse-index
    # count. Treated as a chapter-target enumerated signal.
    range_chapter_pattern: re.Pattern | None = None

    scan_window: int = 3000


# Cross-state regularities — these have looked the same in every umbrella
# text we've probed so far (UT, FL, CO, NE, MA).
ANCHOR_LABEL_RE = re.compile(
    r"(applicability|definitions|short title|"
    r"scope\s+of\s+(?:chapter|part|article|title)|"
    r"\bscope$)",  # bare "Scope" at end of label — CO uses this form, e.g. "Section 12-20-101 - Scope"
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


# ---------------------------------------------------------------------------
# Colorado (Title 12 = Professions and Occupations Act)
# ---------------------------------------------------------------------------
# CO's umbrella is in Title 12, with three articles that scope themselves
# against the rest of the title:
#   Article 1   ("This article 1 applies to every article in this title 12")
#   Article 20  ("This article 20 applies to every article in this title 12
#                except articles 10 and 15")
#   Article 30  ("This article 30 applies to articles 200 to 315 of this
#                title 12") — health-care provisions; uses a range, not a list.
#
# The 153 Title 10 (Insurance) sections that the discover step also pulled in
# will not match these CO-specific universal phrases (different title number,
# different content) and will land in triage with `undetermined` scope —
# the right outcome for an upstream-cleanup item.
CO_RULES = StateScopeRules(
    universal_patterns=(
        # CO Article 1's wording. Match any article number; require "in this
        # title 12" to keep the Title 10 sections from accidentally matching.
        (re.compile(r"this article\s+\d+\s+applies to every article in this title\s+12", re.I), "title"),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
    ),
    # CO writes "article 200", "article 315" — no "Chapter" or "Title" prefix.
    chapter_cite_pattern=re.compile(r"\barticle\s+(\d+)\b", re.I),
    # CO section cites: "section 12-200-103", "12-30-101", etc. Middle token
    # is the article number — that's what we look up.
    section_cite_pattern=re.compile(r"\b(?:section\s+)?12-(\d+)-\d+\b", re.I),
    slug_prefix="article",
    # CO Article 30's range scope: "applies to articles 200 to 315 of this title 12".
    range_chapter_pattern=re.compile(
        r"applies\s+to\s+articles?\s+(\d+)\s+to\s+(\d+)\s+of\s+this\s+title\s+\d+",
        re.I,
    ),
)


STATE_RULES: dict[str, StateScopeRules] = {
    "UT": UT_RULES,
    "FL": FL_RULES,
    "CO": CO_RULES,
}
