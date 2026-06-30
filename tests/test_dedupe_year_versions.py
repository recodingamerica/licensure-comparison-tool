"""_dedupe_year_versions: collapse Justia year-versioned section URLs.

This is the function behind the published text/clean section-count story (a
single section often appears under both /2021/ and /2023/ and unversioned). It
must keep exactly one per canonical path, prefer unversioned, else the highest
year, and preserve original order.
"""

from __future__ import annotations

from pipeline.ingest.pull_text import _dedupe_year_versions


def _items(*urls):
    return [{"url": u} for u in urls]


BASE = "https://law.justia.com/codes/texas"
SEC = "occupations-code/title-3/chapter-101/section-101-001"
SEC2 = "occupations-code/title-3/chapter-101/section-101-002"


def test_unversioned_beats_year():
    items = _items(f"{BASE}/2023/{SEC}/", f"{BASE}/{SEC}/")
    kept = [i["url"] for i in _dedupe_year_versions(items)]
    assert kept == [f"{BASE}/{SEC}/"]


def test_highest_year_when_no_unversioned():
    items = _items(f"{BASE}/2019/{SEC}/", f"{BASE}/2023/{SEC}/", f"{BASE}/2021/{SEC}/")
    kept = [i["url"] for i in _dedupe_year_versions(items)]
    assert kept == [f"{BASE}/2023/{SEC}/"]


def test_distinct_sections_both_kept():
    items = _items(f"{BASE}/2023/{SEC}/", f"{BASE}/2023/{SEC2}/")
    kept = {i["url"] for i in _dedupe_year_versions(items)}
    assert kept == {f"{BASE}/2023/{SEC}/", f"{BASE}/2023/{SEC2}/"}


def test_no_year_segments_untouched():
    items = _items(f"{BASE}/{SEC}/", f"{BASE}/{SEC2}/")
    kept = [i["url"] for i in _dedupe_year_versions(items)]
    assert kept == [f"{BASE}/{SEC}/", f"{BASE}/{SEC2}/"]


def test_original_order_preserved():
    # SEC2 appears first; dedup must not reorder survivors.
    items = _items(
        f"{BASE}/2023/{SEC2}/",
        f"{BASE}/2021/{SEC}/",
        f"{BASE}/{SEC}/",        # unversioned SEC — wins over 2021
    )
    kept = [i["url"] for i in _dedupe_year_versions(items)]
    assert kept == [f"{BASE}/2023/{SEC2}/", f"{BASE}/{SEC}/"]


def test_empty():
    assert _dedupe_year_versions([]) == []


def test_a_bare_year_in_citation_not_treated_as_segment():
    # A 4-digit number that is NOT its own path segment (e.g. part of a slug)
    # must not be stripped — only standalone /YYYY/ segments are year markers.
    u = f"{BASE}/occupations-code/title-3/chapter-2020/section-1/"
    kept = [i["url"] for i in _dedupe_year_versions(_items(u))]
    assert kept == [u]
