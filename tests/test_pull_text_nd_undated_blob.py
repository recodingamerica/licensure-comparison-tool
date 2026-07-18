"""extract_child_links: an ND inline_chapter_blob undated page must NOT be drilled
to a year copy.

ND serves each chapter's sections as inline dotted-marker TEXT on one page, not as
child section links. So extract_child_links finds no `sections` on the undated page
even when it is COMPLETE, and (before this guard) the year-selector branch drilled
the /<year>/ copy instead. Justia's dated snapshot can be INCOMPLETE — electrician/ND
undated chapter-43-09 has 43-09-01..34, but the /2024/ copy only ..26 — so the drill
silently dropped 8 tail sections. The guard: when the undated page is itself an
inline blob (looks_like_nd_blob), don't drill — the caller captures + splits it.
"""

from __future__ import annotations

from pipeline.ingest.pull_text import extract_child_links

ND_UNDATED = "https://law.justia.com/codes/north-dakota/title-43/chapter-43-09/"


def _nd_blob_page(*links: str) -> str:
    body = (
        '<div id="codes-content">'
        "<p>43-09-01. Definitions. " + "a" * 80 + "</p>"
        "<p>43-09-02. License required. " + "b" * 80 + "</p>"
        "<p>43-09-03. Fees and renewal. " + "c" * 80 + "</p>"
        "</div>"
    )
    return body + "".join(f'<a href="{h}">x</a>' for h in links)


def test_nd_inline_blob_undated_not_drilled_to_year():
    # Undated ND blob page whose only link is a self-year snapshot. The page HAS
    # content (inline dotted markers), so it must not be promoted to a year drill.
    html = _nd_blob_page("/codes/north-dakota/2024/title-43/chapter-43-09/")
    sections, inter = extract_child_links(html, ND_UNDATED)
    assert sections == []
    assert inter == []  # NOT drilled to the (possibly-incomplete) /2024/ copy


def test_non_blob_undated_still_drills_year():
    # A genuinely empty undated selector page (no inline blob) must still drill the
    # latest-year copy — the guard is specific to content-bearing blob pages.
    html = "".join(
        f'<a href="{h}">x</a>'
        for h in (
            "/codes/north-dakota/2023/title-43/chapter-43-09/",
            "/codes/north-dakota/2024/title-43/chapter-43-09/",
        )
    )
    sections, inter = extract_child_links(html, ND_UNDATED)
    assert sections == []
    assert [i["url"] for i in inter] == [
        "https://law.justia.com/codes/north-dakota/2024/title-43/chapter-43-09/"
    ]
