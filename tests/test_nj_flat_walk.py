"""NJ layout: a chapter URL redirects to its title page, which nests sections flat
under the title (section-<title>-<chaptertoken>-…). extract_child_links must collect
THIS chapter's sections (not the whole title) despite the literal chapter slug being
absent from their paths."""

from pipeline.ingest.pull_text import extract_child_links

BASE = "https://law.justia.com/codes/new-jersey/title-26/chapter-2k/"
HTML = """
  <a href="/codes/new-jersey/title-26/section-26-2k-10/">26:2K-10 Findings</a>
  <a href="/codes/new-jersey/title-26/section-26-2k-11/">26:2K-11 Definitions</a>
  <a href="/codes/new-jersey/title-26/section-26-2k-12.1/">26:2K-12.1 Board</a>
  <a href="/codes/new-jersey/title-26/section-26-1-5/">26:1-5 (a DIFFERENT chapter)</a>
  <a href="/codes/new-jersey/title-26/chapter-1/">Chapter 1</a>
"""


def test_collects_this_chapters_flat_sections_only():
    sections, _ = extract_child_links(HTML, BASE)
    urls = [s["url"] for s in sections]
    assert sum("section-26-2k-" in u for u in urls) == 3     # all three 2K sections
    assert not any("section-26-1-5" in u for u in urls)      # other chapter excluded
    assert not any("chapter-1" in u for u in urls)           # sibling chapter excluded


def test_normal_chapter_layout_still_works():
    # A conventional chapter→section page (slug appears in the path) is unaffected.
    base = "https://law.justia.com/codes/x/title-1/chapter-5/"
    html = ('<a href="/codes/x/title-1/chapter-5/section-1/">S1</a>'
            '<a href="/codes/x/title-1/chapter-9/section-1/">other</a>')
    sections, _ = extract_child_links(html, base)
    urls = [s["url"] for s in sections]
    assert any("chapter-5/section-1" in u for u in urls)
    assert not any("chapter-9" in u for u in urls)
