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
