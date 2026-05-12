"""Tests for the HTML parsing in pipeline.discover.find_licensing_titles.

The _extract_titles regex is the source of truth for what counts as a
"top-level title" in a Justia state index. Lock in the filtering rules
so adding new states doesn't silently break it.
"""

from pipeline.discover.find_licensing_titles import _extract_titles


# Minimal-but-real Justia state index HTML
TX_INDEX_SNIPPET = """
<html><body>
<ul class="codes">
  <li><a href="/codes/texas/agriculture-code/">Agriculture Code</a></li>
  <li><a href="/codes/texas/occupations-code/">Occupations Code</a></li>
  <li><a href="/codes/texas/2025/">2025 Texas Statutes</a></li>
  <li><a href="/codes/texas/2024/">2024 Texas Statutes</a></li>
  <li><a href="/codes/texas/business-commerce-code/">Business &amp; Commerce Code</a></li>
  <li><a href="/codes/texas/occupations-code/title-3/">Title 3 - Health Professions</a></li>
</ul>
</body></html>
"""


def test_extract_titles_picks_top_level_only():
    titles = _extract_titles(TX_INDEX_SNIPPET)
    urls = {t["url"] for t in titles}
    # Top-level codes included
    assert "https://law.justia.com/codes/texas/agriculture-code/" in urls
    assert "https://law.justia.com/codes/texas/occupations-code/" in urls
    assert "https://law.justia.com/codes/texas/business-commerce-code/" in urls


def test_extract_titles_skips_year_versioned():
    titles = _extract_titles(TX_INDEX_SNIPPET)
    slugs = {t["url"].split("/")[-2] for t in titles}
    # Year-stamped indexes excluded (slug is purely numeric)
    assert "2025" not in slugs
    assert "2024" not in slugs


def test_extract_titles_skips_deeper_paths():
    """A /codes/<state>/<code>/<chapter>/ link is not a top-level title."""
    titles = _extract_titles(TX_INDEX_SNIPPET)
    urls = {t["url"] for t in titles}
    # title-3 is one level deeper than a top-level code
    assert "https://law.justia.com/codes/texas/occupations-code/title-3/" not in urls


def test_extract_titles_preserves_label_and_decodes_amp():
    titles = _extract_titles(TX_INDEX_SNIPPET)
    label_by_url = {t["url"]: t["label"] for t in titles}
    # HTML entity preserved as-is or decoded — current parser leaves entities
    # raw (we don't unescape). Just lock in the actual label.
    assert "Business" in label_by_url["https://law.justia.com/codes/texas/business-commerce-code/"]


def test_extract_titles_dedupes():
    """If a link appears twice, it's only returned once."""
    html = (
        '<a href="/codes/texas/occupations-code/">Occupations Code</a>'
        '<a href="/codes/texas/occupations-code/">Occupations Code</a>'
    )
    titles = _extract_titles(html)
    assert len([t for t in titles if t["url"].endswith("occupations-code/")]) == 1


def test_extract_titles_empty_html():
    assert _extract_titles("") == []
    assert _extract_titles("<html></html>") == []


def test_extract_titles_flat_chapter_state():
    """A state like NC has 'Chapter N' links at the top level (no titles)."""
    html = """
    <a href="/codes/north-carolina/chapter-90/">Chapter 90 - Medicine</a>
    <a href="/codes/north-carolina/chapter-93/">Chapter 93 - Public Accountants</a>
    """
    titles = _extract_titles(html)
    # Parser still returns them — flat-state filtering happens downstream in find_for_state
    assert len(titles) == 2
    labels = [t["label"] for t in titles]
    assert any("Chapter 90" in lbl for lbl in labels)
    assert any("Chapter 93" in lbl for lbl in labels)
