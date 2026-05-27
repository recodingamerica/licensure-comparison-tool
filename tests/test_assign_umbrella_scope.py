"""Regression tests for the umbrella scope walker (assign_umbrella_scope).

Two layers:

1. Unit tests for the leaf-section detector (`LEAF_SECTION_SEG`) and the
   group-key function (`_split_chap_part`). These guard the per-state URL
   shapes Justia uses — section-/statute-/rs-/bare-integer leaves are real
   sections; chapter-/title-/division- landing pages are not.

2. Golden characterization tests over the five validated states (UT, FL, CO,
   IA, WI). They freeze the current `scope_source_counts` so any walker change
   that shifts a known-good state's classification fails loudly. The FL case
   additionally pins the § 455.017 trap: chapter-455 is DBPR-scoped, NOT
   universal, and must stay undetermined (this exact property regressed once
   when an LLM-rules output was committed over the hand-tuned result).

The golden tests read the committed real data (umbrella_text + profession_index)
and skip if it's absent, so they don't fail in a data-less checkout.
"""

from __future__ import annotations

import pytest

from pipeline.discover.assign_umbrella_scope import (
    _split_chap_part,
    assign_for_state,
    UMBRELLA_TEXT_DIR,
)
from pipeline.discover._scope_rules import LEAF_SECTION_SEG


# ---------------------------------------------------------------------------
# Unit: LEAF_SECTION_SEG — which last-path-segments count as a leaf section
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("segment", [
    "section-58-1-102",   # UT / FL / CO standard
    "statute-622-005",    # NV / NE
    "rs-37-1",            # LA
    "12-30-101",          # CO bare cite leaf
    "7901",               # NY bare integer
    "section_1",          # underscore variant
    "s-1",                # abbreviated
])
def test_leaf_seg_matches_section_forms(segment):
    assert LEAF_SECTION_SEG.match(segment)


@pytest.mark.parametrize("segment", [
    "chapter-88",
    "chapter-1b",
    "title-58",
    "division-10",
    "part-3",
    "subchapter-4",
    "article-130-1",      # NY uses this as a banner/landing leaf, not a section
])
def test_leaf_seg_rejects_container_landings(segment):
    assert not LEAF_SECTION_SEG.match(segment)


# ---------------------------------------------------------------------------
# Unit: _split_chap_part — group key (chapter_slug, part) or None
# ---------------------------------------------------------------------------

def _sec(url, slug):
    return {"url": url, "umbrella_chapter_slug": slug}


def test_split_keeps_section_leaf():
    s = _sec("https://law.justia.com/codes/utah/title-58/chapter-1/section-58-1-102/", "chapter-1")
    assert _split_chap_part(s) == ("chapter-1", "NO_PART")


def test_split_keeps_statute_leaf():
    # Fix A: NV-style statute- leaf under a real chapter must be kept.
    s = _sec("https://law.justia.com/codes/nevada/chapter-622/statute-622-005/", "chapter-622")
    assert _split_chap_part(s) == ("chapter-622", "NO_PART")


def test_split_keeps_rs_leaf():
    # Fix A: LA-style rs- leaf (section-level umbrella, slug == leaf) kept.
    s = _sec("https://law.justia.com/codes/louisiana/revised-statutes/title-37/rs-37-1/", "rs-37-1")
    assert _split_chap_part(s) == ("rs-37-1", "NO_PART")


def test_split_drops_chapter_landing_page():
    # Banner/landing page (last segment is a container) — not a section.
    s = _sec("https://law.justia.com/codes/utah/title-58/chapter-88/", "chapter-88")
    assert _split_chap_part(s) is None


def test_split_extracts_part_token():
    s = _sec("https://law.justia.com/codes/utah/title-58/chapter-4/part-2/section-58-4-201/", "chapter-4")
    assert _split_chap_part(s) == ("chapter-4", "2")


def test_split_none_without_slug():
    assert _split_chap_part({"url": "https://x/section-1/"}) is None


def test_split_none_empty_url():
    assert _split_chap_part({"url": "", "umbrella_chapter_slug": "chapter-1"}) is None


# ---------------------------------------------------------------------------
# Golden: freeze scope_source_counts for the five validated states
# ---------------------------------------------------------------------------

GOLDEN_COUNTS = {
    "UT": {"anchor_universal": 3, "universal": 50, "inherited_enumeration": 14, "anchor_enumeration": 2},
    "FL": {"undetermined": 62, "anchor_enumeration": 3, "inherited_enumeration": 98},
    "CO": {"anchor_universal": 8, "universal": 23, "anchor_enumeration": 14, "inherited_enumeration": 20, "undetermined": 153},
    "IA": {"anchor_enumeration": 2, "inherited_enumeration": 117, "anchor_universal": 1, "universal": 19},
    "WI": {"anchor_enumeration": 6, "inherited_enumeration": 94},
}


@pytest.mark.parametrize("state,expected", GOLDEN_COUNTS.items())
def test_golden_scope_source_counts(state, expected):
    if not (UMBRELLA_TEXT_DIR / f"{state}.json").exists():
        pytest.skip(f"no committed umbrella_text for {state}")
    result = assign_for_state(state)
    assert result["scope_source_counts"] == expected


def test_fl_chapter_455_stays_undetermined():
    """§ 455.017 is DBPR-scoped, NOT universal. chapter-455 must stay fully
    undetermined — the property that regressed in commit b61e800."""
    if not (UMBRELLA_TEXT_DIR / "FL.json").exists():
        pytest.skip("no committed umbrella_text for FL")
    result = assign_for_state("FL")
    sources_455 = [
        s["scope_source"] for s in result["sections"]
        if s["umbrella_chapter_slug"] == "chapter-455"
    ]
    assert sources_455, "expected chapter-455 sections in FL umbrella_text"
    assert all(src == "undetermined" for src in sources_455)
