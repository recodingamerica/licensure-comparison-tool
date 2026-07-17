"""A flat-layout (NJ) chapter url that Justia does NOT redirect to its title page.

NJ has no chapter pages: sections sit flat under the title. A mapped chapter url
(…/title-45/chapter-5a/) only works because Justia 301s it to the title page. Some
chapters 404 instead — construction_trades/NJ (45:5AAA) pulled 0 sections and the
whole cell reverted EMPTY. The walk must reach the title page on its own rather
than depend on the redirect.
"""

import pipeline.ingest.pull_text as pt

CHAPTER = "https://law.justia.com/codes/new-jersey/title-45/chapter-5aaa/"
TITLE = "https://law.justia.com/codes/new-jersey/title-45/"

# The real title page: this chapter's sections plus ~2,200 belonging to others.
TITLE_HTML = """
  <a href="/codes/new-jersey/title-45/section-45-5aaa-1/">45:5AAA-1 Definitions</a>
  <a href="/codes/new-jersey/title-45/section-45-5aaa-2/">45:5AAA-2 Registration</a>
  <a href="/codes/new-jersey/title-45/section-45-5a-1/">45:5A-1 (a DIFFERENT chapter)</a>
  <a href="/codes/new-jersey/title-45/section-45-9-14-5/">45:9-14.5 (another chapter)</a>
"""


def _fetches(monkeypatch, responses):
    """Stub fetch() with url -> (status, html, err); record the call order."""
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return responses.get(url, (404, None, None))

    monkeypatch.setattr(pt, "fetch", fake_fetch)
    monkeypatch.setattr(pt, "polite_sleep", lambda: None)
    return calls


def test_404_chapter_recovers_this_chapters_sections_from_title_page(monkeypatch):
    calls = _fetches(monkeypatch, {
        CHAPTER: (404, None, None),
        TITLE: (200, TITLE_HTML, None),
    })

    sections, err = pt.collect_section_targets(CHAPTER, "Home Improvement", "chapter-5aaa", 0)

    assert err is None
    urls = [s["url"] for s in sections]
    assert sum("section-45-5aaa-" in u for u in urls) == 2   # this chapter, both sections
    assert not any("section-45-5a-1" in u for u in urls)     # sibling chapter excluded
    assert not any("section-45-9-14-5" in u for u in urls)   # ditto — not the whole title
    assert calls == [CHAPTER, TITLE]                         # title tried only after the 404


def test_redirecting_chapter_is_untouched(monkeypatch):
    # The 301 case: fetch already returns the title page's html for the chapter url.
    calls = _fetches(monkeypatch, {CHAPTER: (200, TITLE_HTML, None)})

    sections, err = pt.collect_section_targets(CHAPTER, "Home Improvement", "chapter-5aaa", 0)

    assert err is None
    assert len(sections) == 2
    assert calls == [CHAPTER]                                # no extra fetch


def test_dead_chapter_on_a_normal_state_still_errors(monkeypatch):
    # Non-flat state: the title page has no flat sections for this chapter, so the
    # original fetch failure stands rather than being masked.
    url = "https://law.justia.com/codes/utah/title-58/chapter-99/"
    calls = _fetches(monkeypatch, {
        url: (404, None, None),
        "https://law.justia.com/codes/utah/title-58/": (
            200, '<a href="/codes/utah/title-58/chapter-1/section-1/">58-1-1</a>', None),
    })

    sections, err = pt.collect_section_targets(url, "Nope", "chapter-99", 0)

    assert sections == []
    assert err and "404" in err
    assert len(calls) == 2


def test_unfetchable_title_page_reports_the_chapter_failure(monkeypatch):
    _fetches(monkeypatch, {CHAPTER: (404, None, None), TITLE: (500, None, None)})

    sections, err = pt.collect_section_targets(CHAPTER, "Home Improvement", "chapter-5aaa", 0)

    assert sections == []
    assert err and CHAPTER in err


def test_flat_title_url_shape():
    assert pt._flat_title_url(CHAPTER) == TITLE
    assert pt._flat_title_url(TITLE) is None                  # a title is not a chapter
    assert pt._flat_title_url(
        "https://law.justia.com/codes/new-jersey/title-45/section-45-5aaa-1/") is None
