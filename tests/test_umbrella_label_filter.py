"""Tests for the umbrella label-filter logic added in issue #57.

Guards:
  1. _UMBRELLA_LABEL regex: keeps cross-cutting labels, including the reversed
     word-order fix ("Occupations and Professions").
  2. select_umbrella_chapters pure function: blessed slug kept, cached slug kept,
     manifest-drop wins over everything, unblessed non-matching label dropped.
  3. _apply_cap: 60 targets -> 50 kept + cap_hits entry; 40 -> passthrough.

IMPORTANT: pull_state_umbrella is NOT called in any test — it fetches from the
network. All tests exercise pure functions only.
"""

from __future__ import annotations

import pytest

import pipeline.discover.umbrella_from_citations as u
from pipeline.ingest.pull_umbrella_text import select_umbrella_chapters, _apply_cap


# ---------------------------------------------------------------------------
# 1. _UMBRELLA_LABEL regex
# ---------------------------------------------------------------------------

def test_regex_keeps_licensing_generally():
    assert u._UMBRELLA_LABEL.search("Chapter 1 - Licensing Generally")


def test_regex_keeps_reversed_word_order():
    # The word-order fix: "Occupations and Professions" (was only "Professions and Occupations")
    assert u._UMBRELLA_LABEL.search(
        "Article 1A. Procedure for Regulation of Occupations and Professions"
    )


def test_regex_keeps_general_provisions():
    assert u._UMBRELLA_LABEL.search("Chapter 1 - General Provisions")


def test_regex_keeps_uniform_licensing():
    assert u._UMBRELLA_LABEL.search("Article 1 - Uniform Licensing Act")


def test_regex_rejects_profession_specific():
    rejected = [
        "Chapter 26 - Nurses",
        "Chapter 11 - Dentists",
        "Article 240 - Medical Practice",
        "Chapter 64 - University of Arkansas",
        "Chapter 51 - Water and Wastewater",
    ]
    for label in rejected:
        assert not u._UMBRELLA_LABEL.search(label), f"should reject: {label!r}"


# ---------------------------------------------------------------------------
# 2. select_umbrella_chapters
# ---------------------------------------------------------------------------

def _ch(slug: str, label: str) -> dict:
    return {"slug": slug, "label": label, "url": f"https://example.com/{slug}/"}


def test_select_blessed_slug_kept_despite_non_matching_label():
    """IN article-0-5 case: slug is in manifest universal_chapters but label
    doesn't match the regex at all."""
    chapters = [_ch("article-0-5", "Applicability of Certain Provisions in IC 25-1")]
    manifest_blessed = {"article-0-5"}
    manifest_dropped: set[str] = set()
    kept, drop_log = select_umbrella_chapters(
        chapters, cached_slugs=set(), manifest_blessed=manifest_blessed,
        manifest_dropped=manifest_dropped,
    )
    assert len(kept) == 1
    assert kept[0]["slug"] == "article-0-5"
    assert drop_log == []


def test_select_cached_slug_kept_despite_non_matching_label():
    """Grandfather: a slug already in the cache (a human accepted it) is kept
    even if its label wouldn't pass the regex."""
    chapters = [_ch("chapter-99", "Practitioners Of Healing Arts")]
    # Assume this label doesn't match _UMBRELLA_LABEL
    assert not u._UMBRELLA_LABEL.search("Practitioners Of Healing Arts")
    cached_slugs = {"chapter-99"}
    kept, drop_log = select_umbrella_chapters(
        chapters, cached_slugs=cached_slugs, manifest_blessed=set(),
        manifest_dropped=set(),
    )
    assert len(kept) == 1
    assert drop_log == []


def test_select_manifest_drop_wins_over_label_match_and_cache():
    """manifest_dropped is authoritative: even a label-matching, cached slug is removed."""
    chapters = [_ch("chapter-1", "General Provisions")]
    # Label matches, slug is cached — but manifest drops it
    kept, drop_log = select_umbrella_chapters(
        chapters,
        cached_slugs={"chapter-1"},
        manifest_blessed=set(),
        manifest_dropped={"chapter-1"},
    )
    assert kept == []
    assert len(drop_log) == 1
    assert drop_log[0] == ("chapter-1", "General Provisions", "manifest-drop")


def test_select_unblessed_non_matching_label_dropped():
    """A chapter that doesn't match the regex, isn't blessed, and isn't cached
    is dropped with the correct reason."""
    chapters = [_ch("chapter-55", "Veterinarians")]
    assert not u._UMBRELLA_LABEL.search("Veterinarians")
    kept, drop_log = select_umbrella_chapters(
        chapters, cached_slugs=set(), manifest_blessed=set(), manifest_dropped=set(),
    )
    assert kept == []
    assert len(drop_log) == 1
    slug, label, reason = drop_log[0]
    assert slug == "chapter-55"
    assert label == "Veterinarians"
    assert reason == "no-label-match-and-not-blessed"


def test_select_mixed_batch():
    """Smoke test: a mix of keep/drop decisions is handled correctly."""
    chapters = [
        _ch("chapter-1", "General Provisions"),       # regex match → keep
        _ch("article-0-5", "Applicability of IC"),    # blessed → keep
        _ch("chapter-old", "Old Cached Chapter"),      # cached → keep
        _ch("chapter-bad", "Nurses"),                  # none → drop
        _ch("chapter-drop", "General Provisions"),     # manifest-drop wins even over regex
    ]
    manifest_blessed = {"article-0-5"}
    manifest_dropped = {"chapter-drop"}
    cached_slugs = {"chapter-old"}

    kept, drop_log = select_umbrella_chapters(
        chapters,
        cached_slugs=cached_slugs,
        manifest_blessed=manifest_blessed,
        manifest_dropped=manifest_dropped,
    )
    kept_slugs = {c["slug"] for c in kept}
    assert kept_slugs == {"chapter-1", "article-0-5", "chapter-old"}
    dropped_slugs = {entry[0] for entry in drop_log}
    assert dropped_slugs == {"chapter-bad", "chapter-drop"}
    reasons = {entry[0]: entry[2] for entry in drop_log}
    assert reasons["chapter-bad"] == "no-label-match-and-not-blessed"
    assert reasons["chapter-drop"] == "manifest-drop"


# ---------------------------------------------------------------------------
# 3. _apply_cap
# ---------------------------------------------------------------------------

def _targets(n: int) -> list[dict]:
    return [{"url": f"https://example.com/section-{i}/", "label": f"§ {i}"} for i in range(n)]


def test_apply_cap_over_limit():
    """60 targets → 50 kept, cap_hits populated."""
    targets = _targets(60)
    cap_hits: dict = {}
    result = _apply_cap(targets, slug="chapter-1", cap_hits=cap_hits)
    assert len(result) == 50
    assert "chapter-1" in cap_hits
    assert cap_hits["chapter-1"] == {"declared": 60, "kept": 50}


def test_apply_cap_under_limit():
    """40 targets → all kept, cap_hits empty."""
    targets = _targets(40)
    cap_hits: dict = {}
    result = _apply_cap(targets, slug="chapter-2", cap_hits=cap_hits)
    assert len(result) == 40
    assert cap_hits == {}


def test_apply_cap_exactly_at_limit():
    """Exactly 50 targets → no cap hit."""
    targets = _targets(50)
    cap_hits: dict = {}
    result = _apply_cap(targets, slug="chapter-3", cap_hits=cap_hits)
    assert len(result) == 50
    assert cap_hits == {}


def test_apply_cap_respects_custom_cap():
    """Custom cap argument works."""
    targets = _targets(10)
    cap_hits: dict = {}
    result = _apply_cap(targets, slug="chapter-x", cap_hits=cap_hits, cap=5)
    assert len(result) == 5
    assert cap_hits["chapter-x"] == {"declared": 10, "kept": 5}
