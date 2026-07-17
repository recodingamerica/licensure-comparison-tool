"""Tests for repair_nj_mappings' owns-vs-nested discrimination.

Justia publishes NJ flat: 2,286 sections under title-45 and no chapter pages at all, so
a chapter has a number but no name. The repair remaps a cell's mapping to chapter URLs,
which is right for a profession that OWNS its chapter and wrong for the dozen that live
as a handful of sections INSIDE title-45 chapter-9 (Board of Medical Examiners, 336
sections) -- remapping those both over-broadens them and trips pull_text's over-broad
guard, which zeroes the cell outright.
"""
import pipeline.discover.repair_nj_mappings as r

CH9 = "https://law.justia.com/codes/new-jersey/title-45/chapter-9/"
CH5A = "https://law.justia.com/codes/new-jersey/title-45/chapter-5a/"


def _sec(chapter, n):
    return f"https://law.justia.com/codes/new-jersey/title-45/section-45-{chapter}-{n}/"


def _census(**chapters):
    """{'9': 336, '5a': 71} -> {(title, token): {section urls}}"""
    return {("45", tok): {_sec(tok, i) for i in range(n)} for tok, n in chapters.items()}


def test_nested_profession_keeps_its_section_list(monkeypatch):
    """chiropractic is 10 sections of chapter-9's 336 -> nested, don't remap."""
    monkeypatch.setattr(r, "_corpus_sections",
                        lambda p: [{"url": _sec("9", i)} for i in range(10)])
    assert r._nested_chapters("chiropractic", [CH9], _census(**{"9": 336})) == {CH9}


def test_owning_profession_is_remapped(monkeypatch):
    """medicine holds 332 of chapter-9's 336 -> owns it, remap to the chapter URL."""
    monkeypatch.setattr(r, "_corpus_sections",
                        lambda p: [{"url": _sec("9", i)} for i in range(332)])
    assert r._nested_chapters("medicine", [CH9], _census(**{"9": 336})) == set()


def test_small_chapter_is_never_judged(monkeypatch):
    """Below the guard's ceiling an over-broad remap can't zero a cell, so this tool
    leaves the scoping call alone -- electrician owns all 71 of chapter-5a anyway."""
    monkeypatch.setattr(r, "_corpus_sections", lambda p: [{"url": _sec("5a", 0)}])
    assert r._nested_chapters("electrician", [CH5A], _census(**{"5a": 71})) == set()


def test_mixed_cell_drops_only_the_nested_chapter(monkeypatch):
    """pharmacy owns chapter-5a but merely sits in chapter-9: keep 5a, nest 9."""
    monkeypatch.setattr(r, "_corpus_sections", lambda p: (
        [{"url": _sec("9", i)} for i in range(2)] + [{"url": _sec("5a", i)} for i in range(71)]))
    census = _census(**{"9": 336, "5a": 71})
    assert r._nested_chapters("pharmacy", [CH9, CH5A], census) == {CH9}


def test_retained_nodes_are_the_nested_chapters_sections():
    """A declined chapter's original curated section nodes survive the rewrite."""
    matched = [{"url": _sec("9", 1)}, {"url": _sec("9", 2)}, {"url": _sec("5a", 1)}]
    assert r._retained_nodes(matched, {CH9}) == [{"url": _sec("9", 1)}, {"url": _sec("9", 2)}]


def test_census_derives_chapter_sizes_with_no_fetch():
    """The committed NJ hierarchy is the whole flat section list, so chapter sizes are
    a local computation -- chapter-9 really is 336 sections (matches the live page)."""
    census = r._chapter_census()
    assert len(census[("45", "9")]) == 336
    assert len(census[("45", "1")]) == 114
