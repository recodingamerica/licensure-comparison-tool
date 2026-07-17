"""A year-version copy of the current page must never be followed as a child — in
EITHER direction. ND inline-blob chapters have 0 section links but do link to their
year copies; the undated↔year bounce looped 44× → depth cap → EMPTY."""

from pipeline.ingest.pull_text import extract_child_links

UNDATED = "https://law.justia.com/codes/north-dakota/title-4-1/chapter-4-1-16/"
YEAR = "https://law.justia.com/codes/north-dakota/2024/title-4-1/chapter-4-1-16/"


def test_year_page_does_not_drill_the_undated_self_copy():
    # The loop case: on the 2024 page, the undated copy's link has NO year segment,
    # so it used to be classified as a drillable INTERMEDIATE → undated → 2024 → …
    html = '<a href="/codes/north-dakota/title-4-1/chapter-4-1-16/">Undated version</a>'
    sections, intermediates = extract_child_links(html, YEAR)
    assert sections == [] and intermediates == []      # self-copy skipped, no drill


def test_undated_page_still_drills_its_year_copy():
    # Year-selector behaviour preserved: an undated page whose only link is a year copy
    # drills that copy (so year-only states still resolve).
    html = '<a href="/codes/north-dakota/2024/title-4-1/chapter-4-1-16/">2024 edition</a>'
    sections, intermediates = extract_child_links(html, UNDATED)
    assert sections == []
    assert len(intermediates) == 1 and "2024" in intermediates[0]["url"]


def test_real_sections_still_collected():
    # A normal chapter→section link (different canonical path) is unaffected.
    base = "https://law.justia.com/codes/x/title-1/chapter-5/"
    html = ('<a href="/codes/x/title-1/chapter-5/section-5-1/">S1</a>'
            '<a href="/codes/x/title-1/chapter-5/section-5-2/">S2</a>')
    sections, _ = extract_child_links(html, base)
    assert sum("section-5-" in s["url"] for s in sections) == 2


def test_other_year_copy_from_a_year_page_also_skipped():
    # 2024 page linking to the 2023 copy (both year-stamped) — also a self-copy, skip it.
    html = '<a href="/codes/north-dakota/2023/title-4-1/chapter-4-1-16/">2023</a>'
    sections, intermediates = extract_child_links(html, YEAR)
    assert intermediates == []
