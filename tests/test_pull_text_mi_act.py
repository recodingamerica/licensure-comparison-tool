"""MI act-level containers must be drilled, not saved as a lone leaf (issue #8).

Michigan's Justia layout nests sections under an ACT container page whose slug is
`statute-act-<n>-of-<year>` (e.g. chapter-487/statute-act-250-of-2006/). That slug
matches the broad `statute[-_]` arm of SECTION_SEG, so it was mistaken for a leaf
section: the puller fetched the act page itself and captured only its preamble
("AN ACT to ...", n=1) instead of drilling its section children. Genuine leaf
slugs (`statute-637-005` in NV/NE) have a DIGIT after `statute-` and must still be
treated as sections. See pull_text._STATUTE_CONTAINER.
"""

from __future__ import annotations

from pipeline.ingest.pull_text import extract_child_links, is_section_url

MI_ACT = "https://law.justia.com/codes/michigan/chapter-487/statute-act-250-of-2006/"
MI_CHAPTER = "https://law.justia.com/codes/michigan/chapter-487/"


def _page(*hrefs):
    return "".join(f'<a href="{h}">x</a>' for h in hrefs)


def test_mi_act_container_is_not_a_section_url():
    assert is_section_url(MI_ACT) is False
    # ...and the executive-reorganization-order variant is also a container.
    assert is_section_url(
        "https://law.justia.com/codes/michigan/chapter-330/statute-e-r-o-no-1996-1/"
    ) is False


def test_nv_ne_statute_leaves_still_sections():
    assert is_section_url(
        "https://law.justia.com/codes/nevada/chapter-637/statute-637-005/"
    ) is True
    assert is_section_url(
        "https://law.justia.com/codes/nebraska/chapter-38/statute-38-117-01/"
    ) is True


def test_chapter_page_routes_act_container_to_intermediates():
    # A MI chapter page links to its act container(s). Those must be drilled,
    # not returned as leaf sections.
    html = _page("/codes/michigan/chapter-487/statute-act-250-of-2006/")
    sections, inter = extract_child_links(html, MI_CHAPTER)
    assert sections == []
    assert [i["slug"] for i in inter] == ["statute-act-250-of-2006"]


def test_act_page_section_children_still_leaves():
    # Inside the act page, the real section leaves keep being classified as
    # sections (they have a digit after `statute-`... actually they are
    # `section-...` slugs) — the container guard must not swallow them.
    html = _page(
        "/codes/michigan/chapter-487/statute-act-250-of-2006/section-487-1001/",
        "/codes/michigan/chapter-487/statute-act-250-of-2006/section-487-1002/",
    )
    sections, inter = extract_child_links(html, MI_ACT)
    assert [s["slug"] for s in sections] == ["section-487-1001", "section-487-1002"]
    assert inter == []
