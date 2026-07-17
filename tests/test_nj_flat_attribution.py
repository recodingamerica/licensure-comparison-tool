"""Attributing NJ flat sections to their mapped chapter.

NJ nests sections flat under the title (…/title-45/section-45-8-30/), which does
NOT prefix-match its chapter url (…/title-45/chapter-8/). Without flat-slug
attribution, sections_per_chapter counts every NJ chapter as empty, so a healthy
multi-chapter NJ pull is falsely held PARTIAL and reverted. land_surveying/NJ
(chapters 8 + 14a, 93 real sections) was the live case.
"""

from pipeline.ingest.refresh_corpus import sections_per_chapter, empty_chapters

CH8 = "https://law.justia.com/codes/new-jersey/title-45/chapter-8/"
CH14A = "https://law.justia.com/codes/new-jersey/title-45/chapter-14a/"


def _sec(slug):
    return {"url": f"https://law.justia.com/codes/new-jersey/title-45/{slug}/"}


def test_flat_sections_attributed_to_their_chapter():
    sections = [_sec("section-45-8-30"), _sec("section-45-8-35"),
                _sec("section-45-14a-1"), _sec("section-45-14a-2"), _sec("section-45-14a-3")]
    counts = sections_per_chapter([CH8, CH14A], sections)
    assert counts[CH8] == 2
    assert counts[CH14A] == 3
    assert empty_chapters([CH8, CH14A], sections) == []   # nothing falsely flagged empty


def test_chapter_token_8_does_not_swallow_8a():
    # section-45-8a-1 belongs to chapter 8a, not chapter 8.
    CH8A = "https://law.justia.com/codes/new-jersey/title-45/chapter-8a/"
    sections = [_sec("section-45-8-30"), _sec("section-45-8a-1")]
    counts = sections_per_chapter([CH8, CH8A], sections)
    assert counts[CH8] == 1
    assert counts[CH8A] == 1


def test_genuinely_empty_flat_chapter_still_flagged():
    sections = [_sec("section-45-8-30"), _sec("section-45-8-35")]
    assert empty_chapters([CH8, CH14A], sections) == [CH14A]   # 14a really contributed nothing


def test_normal_nested_chapters_unaffected():
    # A conventional prefix-nesting state still attributes by path.
    a = "https://law.justia.com/codes/x/title-1/chapter-5/"
    b = "https://law.justia.com/codes/x/title-1/chapter-9/"
    secs = [{"url": "https://law.justia.com/codes/x/title-1/chapter-5/section-1/"},
            {"url": "https://law.justia.com/codes/x/title-1/chapter-9/section-2/"}]
    counts = sections_per_chapter([a, b], secs)
    assert counts[a] == 1 and counts[b] == 1
