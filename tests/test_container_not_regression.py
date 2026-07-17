"""A committed TITLE_STRAY corpus (only a container landing page) being replaced by
real leaf sections is an upgrade, not a regression — the guard must not block it."""

from pipeline.ingest.pull_text import _is_regression, _lost_sections


def _sec(url, cite, text):
    return {"url": url, "citation": cite, "text": text}


def test_container_page_replaced_by_real_sections_is_not_regression():
    old = {"sections": [_sec("https://law.justia.com/codes/new-jersey/title-26/chapter-2k/",
                             "Chapter 2K", "Chapter 2K - Emergency Medical Services")],
           "total_chars": 200000}
    new = {"sections": [_sec(f"https://law.justia.com/codes/new-jersey/title-26/section-26-2k-{i}/",
                             f"26:2K-{i}", f"section {i} text") for i in range(1, 89)],
           "total_chars": 150000}
    assert _lost_sections(old, new) == []          # the junk container page isn't "lost"
    assert _is_regression(new, old) is None         # so no regression — the upgrade commits


def test_real_section_removal_is_still_a_regression():
    old = {"sections": [_sec("https://law.justia.com/x/title-1/section-1/", "1", "a"),
                        _sec("https://law.justia.com/x/title-1/section-2/", "2", "b")],
           "total_chars": 2}
    new = {"sections": [_sec("https://law.justia.com/x/title-1/section-1/", "1", "a")],
           "total_chars": 1}
    assert _is_regression(new, old) is not None     # a genuine section drop still trips
