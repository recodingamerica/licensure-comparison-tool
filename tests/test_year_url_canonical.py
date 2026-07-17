"""Year-version URL canonicalization has one state-agnostic implementation.

Three copies had drifted: pull_text stripped year segments for any state, but
extract_state's was hardcoded to `/codes/utah/\\d{4}/` — so year-versioned KY/OR/IL
sections never deduped there and could leak duplicate copies into the prompt. All
callers now share pipeline.ingest._section_patterns.canonical_year_url.
"""

from pipeline.ingest._section_patterns import canonical_year_url, YEAR_SEG
from pipeline.extract.extract_state import _canonical_url as extract_canon
from pipeline.discover.assign_umbrella_scope import dedupe_year_versions


def test_strips_year_for_any_state_not_just_utah():
    for st in ("utah", "kentucky", "oregon", "illinois", "new-jersey"):
        yr = f"https://law.justia.com/codes/{st}/2024/title-1/section-5/"
        no = f"https://law.justia.com/codes/{st}/title-1/section-5/"
        assert canonical_year_url(yr) == no
        assert canonical_year_url(no) == no          # idempotent


def test_extract_state_now_canonicalizes_non_utah():
    ky = "https://law.justia.com/codes/kentucky/2023/title-1/section-5/"
    assert extract_canon(ky) == "https://law.justia.com/codes/kentucky/title-1/section-5/"


def test_dedupe_keeps_one_per_canonical_preferring_no_year():
    secs = [
        {"url": "https://law.justia.com/codes/oregon/2023/title-1/section-5/"},
        {"url": "https://law.justia.com/codes/oregon/2024/title-1/section-5/"},
        {"url": "https://law.justia.com/codes/oregon/title-1/section-5/"},      # no-year
        {"url": "https://law.justia.com/codes/oregon/title-1/section-9/"},      # distinct
    ]
    kept = dedupe_year_versions(secs)
    urls = sorted(s["url"] for s in kept)
    assert urls == [
        "https://law.justia.com/codes/oregon/title-1/section-5/",   # no-year copy won
        "https://law.justia.com/codes/oregon/title-1/section-9/",
    ]


def test_year_seg_matches_only_bare_years():
    assert YEAR_SEG.match("2024") and YEAR_SEG.match("1998")
    assert not YEAR_SEG.match("title-2024") and not YEAR_SEG.match("204")
