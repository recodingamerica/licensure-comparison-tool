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

    # Optional: trigger phrases that introduce an inline profession-name list
    # instead of a list of chapter citations. Iowa: "when applied to a
    # physician and surgeon, podiatric physician, ... means a person licensed
    # under this subtitle." When set, the walker scans the post-trigger
    # window for known profession terms (using each profession's `patterns`
    # and `enumeration_aliases` from professions.yaml).
    profession_name_trigger_patterns: tuple[re.Pattern, ...] = ()

    # Chapters that were incorrectly included in umbrella_text by the discover
    # step (e.g. building-safety codes, general administrative-procedure acts).
    # The walker skips every section whose umbrella_chapter_slug is in this set.
    # Set MANUALLY after review: suggest_scope_rules.py only *reports*
    # 100%-undetermined chapters as candidates (a 100%-undetermined chapter is
    # ambiguous — discover false positive vs. a chapter the rules failed to
    # match — so a human decides, see suggest_scope_rules.detect_fully_undetermined_chapters).
    excluded_chapter_slugs: tuple[str, ...] = ()

    scan_window: int = 3000


# A URL's last path segment looks like a leaf statute section (vs. a
# chapter/title/division landing page). Justia names leaf segments differently
# per state — `section-58-1-102` (UT/FL/CO), `statute-622-005` (NV/NE),
# `rs-37-1` (LA), bare integers (NY edn) — so we can't require a literal
# "/section-". Container landing pages like `chapter-88` / `title-58` deliberately
# do NOT match, so they're dropped from scope assignment.
#
# Imported from the shared, dependency-free _section_patterns (NOT re-declared) so
# this and pull_text can't drift — and importing it doesn't drag in the scraping
# stack (bs4/curl_cffi) the way importing pull_text would.
from pipeline.ingest._section_patterns import SECTION_SEG as LEAF_SECTION_SEG

# Cross-state regularities — these have looked the same in every umbrella
# text we've probed so far (UT, FL, CO, NE, MA).
ANCHOR_LABEL_RE = re.compile(
    r"(applicability|definitions|short title|"
    r"scope\s+of\s+(?:chapter|part|article|title)|"
    # "Application of [the/this] chapter/part/title/act" — a scope-defining
    # label (WA "18.235.020 - Application of chapter" enumerates which practice
    # acts the umbrella governs). Requires "of" so it won't match application
    # *process* labels like "Application for a license" / "Application fee".
    r"application\s+of\s+(?:the\s+|this\s+)?(?:chapter|part|article|title|act)|"
    r"\bscope$)",  # bare "Scope" at end of label — CO uses this form, e.g. "Section 12-20-101 - Scope"
    re.I,
)
# "As used in this <X>" or "For (the) purpose(s) of this <X>" — both flag
# the scope target of any enumeration that follows. `subtitle` is in here
# for Iowa (umbrella sits at the subtitle level, e.g. Title IV Subtitle 3).
# The walker maps `subtitle` to the `title` tier in scope selection.
AS_USED_RE = re.compile(
    r"(?:as\s+used\s+in|for\s+(?:the\s+)?purposes?\s+of)\s+this\s+(title|subtitle|chapter|part)",
    re.I,
)

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


# ---------------------------------------------------------------------------
# Iowa (Title IV Subtitle 3 — Health and Related Provisions; Chapter 147 is
# the cross-cutting umbrella for licensed health professions)
# ---------------------------------------------------------------------------
# Iowa doesn't enumerate practice acts by chapter number. Its scope is set
# inside § 147.1(3) as a single inline definition:
#
#   "Licensed" or "certified", when applied to a physician and surgeon,
#   podiatric physician, osteopathic physician and surgeon, ... or sign
#   language interpreter or transliterator means a person licensed under
#   this subtitle.
#
# The walker handles this by matching the trigger ("when applied to" /
# "means a person licensed"), scanning the post-trigger window, and looking
# up each comma-separated term in professions.yaml's `patterns` and
# `enumeration_aliases`. The "for the purpose of this subtitle:" line at the
# top of § 147.1 sets target=subtitle, which selects the title tier.
IA_RULES = StateScopeRules(
    universal_patterns=(
        # Ch 272C § 272C.1(6) enumerates 25+ boards via "Licensing board or
        # 'board' includes the following boards: a. ... b. ... c. ...".
        # Many of the boards in the list cite chapter 147 (which IS the
        # umbrella itself, not a practice act) so a chapter-citation scan
        # captures only the boards that have their own practice-act chapter
        # (~13 of 25). The chapter covers effectively all Iowa licensees,
        # so treat it as universal at chapter target.
        (re.compile(r"includes\s+the\s+following\s+boards", re.I), "chapter"),
    ),
    trigger_patterns=(),
    # IA Code uses bare "chapter NNN" with optional letter suffix, e.g.
    # "chapter 148C", "chapter 152D".
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+[a-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(\d+[a-z]?)\.\d+\b", re.I),
    profession_name_trigger_patterns=(
        re.compile(r"when\s+applied\s+to\b", re.I),
    ),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Wisconsin
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
WI_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"in chs?\.\s*440\s+to\s+480\b", re.I), 'title'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this subchapter applies to (?:any|every|all)\b[^.]*", re.I), 'part'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"credentialed\s+under\b", re.I),
        re.compile(r"granted\s+a\s+license\s+under\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bch(?:apter)?\.?\s+(\d+[A-Za-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\bs(?:ec(?:tion)?)?\.?\s+(\d+)\.\d+", re.I),
    range_chapter_pattern=re.compile(r"in chs?\.\s*(\d+)\s+to\s+(\d+)\b", re.I),
    # Auto-detected: 100% undetermined — not occupational licensing chapters
    excluded_chapter_slugs=('chapter-101', 'chapter-227',),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Missouri
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
MO_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"all state and political subdivision licensing authorities", re.I), 'chapter'),
        (re.compile(r"each state licensing authority", re.I), 'chapter'),
        (re.compile(r"any (?:occupation|profession|occupational or professional)", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:under|pursuant\s+to)\b", re.I),
        re.compile(r"licensure\s+of\b[^.]*\bpursuant\s+to\b", re.I),
        re.compile(r"regulated\s+pursuant\s+to\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+)\b", re.I),
    section_cite_pattern=re.compile(r"\b(?:section|sections|§|§§)\s*(\d+)\.\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# West Virginia
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
WV_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"every board[^.]*referred to in this chapter", re.I), 'title'),
        (re.compile(r"(?:each|all)\s+boards?\s+(?:or\s+licensing\s+authority\s+)?referred to in this chapter", re.I), 'title'),
        (re.compile(r"the\s+boards?\s+referred\s+to\s+in\s+this\s+chapter", re.I), 'title'),
        (re.compile(r"for the purposes of this chapter\b[^.]*", re.I), 'title'),
        (re.compile(r"this article applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|as|under|pursuant\s+to)\b", re.I),
        re.compile(r"boards\s+governing\s+licensing\s+under\s+the\s+following\s+sections", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\barticle\s+(\d+[a-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b30-(\d+[a-z]?)-\d+", re.I),
    slug_prefix='article',
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Tennessee
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
TN_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
        (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), 'part'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+[a-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(?:§\s*)?63-(\d+[a-z]?)-\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# New Mexico
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
NM_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"licensed pursuant to Chapter 61 NMSA 1978", re.I), 'chapter'),
        (re.compile(r"as used in the Uniform Licensing Act", re.I), 'chapter'),
        (re.compile(r"Uniform Licensing Act is applied by law", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bChapter\s+61,?\s+Article\s+(\d+[A-Za-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b61-(\d+[A-Za-z]?)-\d+", re.I),
    slug_prefix='article',
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Hawaii
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
HI_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"applicable to the professions and vocations required by law to be regulated", re.I), 'chapter'),
        (re.compile(r"as used in this chapter\b[^.]*\bevery (?:person|profession|vocation)", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+[a-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(?:section|§)\s*(\d+[A-Za-z]?)-\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Georgia
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
GA_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), 'part'),
        (re.compile(r"any\s+professional\s+licensing\s+board[^.]*this title", re.I), 'title'),
        (re.compile(r"established pursuant to this title", re.I), 'title'),
        (re.compile(r"\bany\s+professional\s+licensing\s+board\b", re.I), 'title'),
        (re.compile(r"\beach\s+professional\s+licensing\s+board\b", re.I), 'title'),
        (re.compile(r"\bthe\s+professional\s+licensing\s+boards\b", re.I), 'title'),
        (re.compile(r"\benforcement of this title\b", re.I), 'title'),
        (re.compile(r"examination\s+(?:required|given)\s+by\s+(?:any\s+|a\s+)?professional\s+licensing\s+board", re.I), 'title'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bChapter\s+(\d+[A-Za-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(?:Code\s+Section|§)\s*43-(\d+[A-Za-z]?)-", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# South Carolina
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SC_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
        (re.compile(r"as used in this title\b", re.I), 'title'),
        (re.compile(r"any holder of a license[^.]*under this title", re.I), 'title'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this article applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+[a-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(?:Section|§)\s*40-(\d+[a-z]?)-", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Idaho
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
ID_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"licensed or required to be licensed under this title", re.I), 'title'),
        (re.compile(r"any holder of a license[^.]*under this title", re.I), 'title'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|under|pursuant\s+to)\b", re.I),
        re.compile(r"established\s+in\b", re.I),
        re.compile(r"as\s+established\s+in\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+)\b", re.I),
    section_cite_pattern=re.compile(r"\b(\d+)-\d+\b", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Texas
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
TX_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this chapter applies to (?:any|every|all|each)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this chapter applies to each regulatory program", re.I), 'chapter'),
        (re.compile(r"apply to licensing and regulatory programs administered by the department", re.I), 'chapter'),
        (re.compile(r"this subchapter applies to (?:any|every|all|each)\b[^.]*", re.I), 'part'),
        (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), 'part'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|as|under)\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensing entities and health care practitioners under\b", re.I),
        re.compile(r"regulates a health care practitioner under\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bChapter\s+(\d+[A-Za-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(?:Section|Sec\.|§)\s*(\d+[A-Za-z]?)\.\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Washington
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
WA_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), 'part'),
        (re.compile('"[Hh]ealth professions?"\\s+means', re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"regulated\s+under\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
        re.compile(r"under\s+chapters?\b", re.I),
        re.compile(r"authority\s+under\s+this\s+chapter\s+in\s+relation\s+to", re.I),
        re.compile(r"jurisdiction\s+in\s+relation\s+to[^.]*\bprofessions?\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapters?\s+(\d+\.\d+[A-Za-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(?:RCW\s+)?(\d+\.\d+[A-Za-z]?)\.\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Maryland
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
MD_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
        (re.compile(r"this subtitle applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"any (?:individual|person) licensed or certified by a board under this article", re.I), 'title'),
        (re.compile(r"in this article the following words", re.I), 'title'),
        (re.compile(r"each unit shall (?:issue|credit|give)\b", re.I), 'title'),
        (re.compile(r"a unit may (?:issue|allow)\b[^.]*license", re.I), 'title'),
        (re.compile(r"service member,\s+veteran,?\s+(?:or|and)\s+military spouse", re.I), 'title'),
        (re.compile(r"list of the names of each unit that issues a license under this title", re.I), 'title'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|as|under|pursuant\s+to)\b", re.I),
        re.compile(r"licensed\s+or\s+certified\s+(?:by|under)\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bTitle\s+(\d+(?:\.\d+)?[A-Za-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\b(\d+(?:\.\d+)?[A-Za-z]?)-\d+", re.I),
    slug_prefix='title',
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Oregon
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
OR_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"any\s+state\s+board\s+or\s+commission\s+that\s+examines\s+applicants\s+for\s+licen[sc]e", re.I), 'chapter'),
        (re.compile(r"any\s+state\s+agency\s+or\s+licensing\s+board", re.I), 'chapter'),
        (re.compile(r"a\s+licensing\s+board,\s+commission\s+or\s+agency", re.I), 'chapter'),
        (re.compile(r"each\s+professional\s+licensing\s+and\s+advisory\s+board", re.I), 'chapter'),
        (re.compile(r"state\s+agency,\s+board\s+or\s+commission\s+has\s+the\s+power\s+to\s+issue\s+any\s+licen[sc]e", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|under|pursuant\s+to)\b", re.I),
        re.compile(r"apply\s+to\s+the\s+following\s+professional\s+licensing", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bORS\s+chapter\s+(\d+[A-Za-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\bORS\s+(\d+[A-Za-z]?)\.\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Indiana
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
IN_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"all occupational and professional licen[sc]ees?[^.]*regulated under the Indiana Code", re.I), 'title'),
        (re.compile(r"entities described in IC 25-0\.5-3 that regulate occupations or professions", re.I), 'title'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this article applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|as|under)\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+or\s+certified\s+under\b", re.I),
        re.compile(r"holds?\s+a\s+license,?\s+certificate,?\s+or\s+registration\s+under\b", re.I),
        re.compile(r"IC\s+25-1-1\.1-4\s+applies\s+to\b", re.I),
        re.compile(r"IC\s+25-1-2-2\.1\s+applies\s+to\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bIC\s+25-(\d+(?:\.\d+)?)\b", re.I),
    section_cite_pattern=re.compile(r"\bIC\s+25-(\d+(?:\.\d+)?)-", re.I),
    slug_prefix='article',
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Montana
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
MT_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this part governs the licensure[^.]*professions and occupations governed by this title", re.I), 'title'),
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), 'part'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+under\b", re.I),
        re.compile(r"licensed\s+pursuant\s+to\b", re.I),
        re.compile(r"licensed\s+to\s+practice\b", re.I),
        re.compile(r"regulated\s+under\s+Title\s+37\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\b(?:Title\s+37,?\s+)?[Cc]hapter\s+(\d+)\b", re.I),
    section_cite_pattern=re.compile(r"\b37-(\d+)-\d+\b", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Connecticut
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
CT_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this chapter applies to all agencies", re.I), 'chapter'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"this part applies to (?:any|every|all)\b[^.]*", re.I), 'part'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|as|under|pursuant\s+to)\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+[a-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"\bsection\s+(\d+[a-z]?)-\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# Nevada
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
NV_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"this title applies to (?:any|every|all)\b[^.]*", re.I), 'title'),
        (re.compile(r"any (?:person|holder of a license)[^.]*under this title", re.I), 'title'),
        (re.compile(r"this chapter applies to (?:any|every|all)\b[^.]*", re.I), 'chapter'),
        (re.compile(r"(?:any\s+)?(?:state\s+)?(?:agency|board|commission)[^.]*authority to regulate an occupation or profession pursuant to this title", re.I), 'chapter'),
        (re.compile(r"regulatory bod(?:y|ies)[^.]*(?:exempted\s+from\s+the\s+provisions\s+of\s+this\s+chapter|are\s+exempted\s+from\s+the\s+provisions)", re.I), 'chapter'),
        (re.compile(r"each regulatory body shall\b", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|as|under|pursuant\s+to)\b", re.I),
        re.compile(r"issued\s+pursuant\s+to\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+(\d+[A-Za-z]?)\s+of\s+NRS\b", re.I),
    section_cite_pattern=re.compile(r"\bNRS\s+(\d+[A-Za-z]?)\.\d+", re.I),
)




# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
# South Dakota
# −−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−
SD_RULES = StateScopeRules(
    universal_patterns=(
        (re.compile(r"any profession regulated under titles? 13 or 36", re.I), 'title'),
        (re.compile(r"regulated under title 36", re.I), 'title'),
        (re.compile(r"professional or occupational licensing board, commission, or agency set forth in title 36", re.I), 'title'),
        (re.compile(r"licensing board authorized in title 36", re.I), 'title'),
        (re.compile(r"any occupation licensed pursuant to title 36", re.I), 'title'),
        (re.compile(r"provisions of this chapter apply to (?:any|every|all)\b", re.I), 'chapter'),
        (re.compile(r"this chapter shall operate retroactively", re.I), 'chapter'),
    ),
    trigger_patterns=(
        re.compile(r"licensed\s+(?:to\s+practice|under|pursuant\s+to)\b", re.I),
        re.compile(r"regulated\s+under\b", re.I),
    ),
    chapter_cite_pattern=re.compile(r"\bchapter\s+36-(\d+[a-z]?)\b", re.I),
    section_cite_pattern=re.compile(r"§+\s*36-(\d+[a-z]?)-", re.I),
)


STATE_RULES: dict[str, StateScopeRules] = {
    "UT": UT_RULES,
    "FL": FL_RULES,
    "CO": CO_RULES,
    "IA": IA_RULES,
    "WI": WI_RULES,
    "MO": MO_RULES,
    "WV": WV_RULES,
    "TN": TN_RULES,
    "NM": NM_RULES,
    "HI": HI_RULES,
    "GA": GA_RULES,
    "SC": SC_RULES,
    "ID": ID_RULES,
    "TX": TX_RULES,
    "WA": WA_RULES,
    "MD": MD_RULES,
    "OR": OR_RULES,
    "IN": IN_RULES,
    "MT": MT_RULES,
    "CT": CT_RULES,
    "NV": NV_RULES,
    "SD": SD_RULES,
}
