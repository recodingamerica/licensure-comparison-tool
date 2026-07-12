"""extract_child_links: drill through plain-word sub-group pages.

Justia splits some chapters by a heading rather than a numbered subchapter —
e.g. MS title-73/chapter-13/{engineers,land-surveyors}/. Those sub-group pages
strictly extend the chapter path but don't match section-/subchapter- patterns,
so they were dropped and the chapter page got saved as a lone index leaf. This
locks in that they're now returned as intermediates to drill.
"""

from __future__ import annotations

from pipeline.ingest.pull_text import extract_child_links

BASE = "https://law.justia.com/codes/mississippi/title-73/chapter-13/"


def _page(*hrefs):
    return "".join(f'<a href="{h}">x</a>' for h in hrefs)


def test_plainword_subgroups_are_intermediates():
    html = _page(
        "/codes/mississippi/title-73/chapter-13/engineers/",
        "/codes/mississippi/title-73/chapter-13/land-surveyors/",
    )
    sections, inter = extract_child_links(html, BASE)
    assert sections == []
    assert {i["slug"] for i in inter} == {"engineers", "land-surveyors"}


def test_leaf_sections_still_sections():
    html = _page("/codes/mississippi/title-73/chapter-13/section-73-13-1/")
    sections, inter = extract_child_links(html, BASE)
    assert [s["slug"] for s in sections] == ["section-73-13-1"]
    assert inter == []


def test_sibling_chapter_not_drilled():
    # A link to another chapter (doesn't extend chapter-13) must be ignored.
    html = _page("/codes/mississippi/title-73/chapter-11/")
    sections, inter = extract_child_links(html, BASE)
    assert sections == [] and inter == []


# --- year-selector handling (IL-style undated pages) --------------------------

IL_UNDATED = "https://law.justia.com/codes/illinois/chapter-225/act-225-ilcs-70/"


def test_year_selector_page_drills_latest_year():
    """An UNDATED page whose only links are year snapshots of ITSELF (no sections)
    is a year-selector; drill the latest-year copy, which carries the section list."""
    html = _page(
        "/codes/illinois/2023/chapter-225/act-225-ilcs-70/",
        "/codes/illinois/2024/chapter-225/act-225-ilcs-70/",
    )
    sections, inter = extract_child_links(html, IL_UNDATED)
    assert sections == []
    assert [i["url"] for i in inter] == [
        "https://law.justia.com/codes/illinois/2024/chapter-225/act-225-ilcs-70/"
    ]  # latest year, not 2023


def test_year_selector_not_triggered_when_page_has_sections():
    """If the page has real sections, the self-year links are just dupes — dropped,
    NOT promoted (guards against regressing content pages)."""
    html = _page(
        "/codes/illinois/2024/chapter-225/act-225-ilcs-70/",  # self-year dupe
        "/codes/illinois/chapter-225/act-225-ilcs-70/section-5/",  # real section
    )
    sections, inter = extract_child_links(html, IL_UNDATED)
    assert [s["slug"] for s in sections] == ["section-5"]
    assert inter == []  # the self-year link was NOT promoted


def test_year_selector_no_loop_on_year_stamped_base():
    """On an already year-stamped base, self-year links must NOT be promoted —
    otherwise a /2024/ page drilling /2023/ drilling ... loops forever."""
    base = "https://law.justia.com/codes/illinois/2024/chapter-225/act-225-ilcs-70/"
    html = _page("/codes/illinois/2023/chapter-225/act-225-ilcs-70/")
    sections, inter = extract_child_links(html, base)
    assert sections == [] and inter == []
