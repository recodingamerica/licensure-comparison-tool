"""The NJ flat-layout URL grammar — one source of truth for its three input forms.

The point of centralising is that a key derived from a chapter url, a section url, or
an (upper-case) citation all compare equal, so downstream census/attribution lookups
can't drift on case.
"""

from pipeline.ingest import nj_flat

CH = "https://law.justia.com/codes/new-jersey/title-45/chapter-5a/"
SEC = "https://law.justia.com/codes/new-jersey/title-45/section-45-5a-10/"
TITLE = "https://law.justia.com/codes/new-jersey/title-45/"


def test_all_three_forms_yield_the_same_lowercased_key():
    key = ("45", "5a")
    assert nj_flat.key_from_chapter_url(CH) == key
    assert nj_flat.key_from_section_url(SEC) == key
    assert nj_flat.key_from_citation("45:5A-10") == key           # upper-case citation
    assert nj_flat.key_from_citation("45:5A-10") == nj_flat.key_from_chapter_url(CH)


def test_chapter_url_round_trips_from_a_citation():
    key = nj_flat.key_from_citation("45:5AAA-1")
    assert key == ("45", "5aaa")
    assert nj_flat.chapter_url(key) == \
        "https://law.justia.com/codes/new-jersey/title-45/chapter-5aaa/"


def test_section_slug_re_scopes_to_its_chapter():
    r8 = nj_flat.section_slug_re(("45", "8"))
    assert r8.match("section-45-8-30")
    assert not r8.match("section-45-8a-1")      # 8 must not swallow 8a
    assert not r8.match("section-45-9-1")


def test_title_url_fallback():
    assert nj_flat.title_url_from_chapter_url(CH) == TITLE
    assert nj_flat.title_url_from_chapter_url(TITLE) is None
    assert nj_flat.title_url_from_chapter_url(SEC) is None


def test_non_matching_inputs_return_none():
    assert nj_flat.key_from_chapter_url("") is None
    assert nj_flat.key_from_chapter_url(TITLE) is None            # a title is not a chapter
    assert nj_flat.key_from_section_url(CH) is None
    assert nj_flat.key_from_citation("not a citation") is None
