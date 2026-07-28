"""Sections we DO have, shipped, but unlabelled -- so nothing can point at them.

Measured 2026-07-28 across six professions: 1,206 quotes couldn't be highlighted, and
four states were 78% of them. AZ (80.3% miss) and OK (73.5%) ship sections whose
`citation` field is blank because their text doesn't open with a citation the way
`RS 37:3083 - Definitions` does. The law is present; it just has no address.

The Justia URL identifies the section, but the slug is NOT the citation -- AZ's
`32-1201` is, while OK's `59-328-3` carries a title prefix the citation (`328.3`)
omits -- so the section adopts the citation the evidence actually used.
"""

from __future__ import annotations

from pipeline.publish.build_frontend import backfill_citations_from_urls


def _sec(url, citation=""):
    return {"url": url, "citation": citation, "text": "body"}


def test_az_shape_bare_number_slug():
    """AZ: slug equals the citation."""
    secs = [_sec("https://law.justia.com/codes/arizona/title-32/section-32-1201/")]
    assert backfill_citations_from_urls(secs, ["32-1201"]) == 1
    assert secs[0]["citation"] == "32-1201"


def test_ok_shape_slug_carries_a_title_prefix_the_citation_omits():
    """OK: slug is `59-328-3`, the citation is `328.3` -- a suffix match, and the
    punctuation differs, so both sides are normalized."""
    secs = [_sec("https://law.justia.com/codes/oklahoma/title-59/section-59-328-3/")]
    assert backfill_citations_from_urls(secs, ["328.3"]) == 1
    assert secs[0]["citation"] == "328.3"


def test_already_labelled_sections_are_left_alone():
    secs = [_sec("https://law.justia.com/codes/arizona/title-32/section-32-1201/", "KEEP ME")]
    assert backfill_citations_from_urls(secs, ["32-1201"]) == 0
    assert secs[0]["citation"] == "KEEP ME"


def test_ambiguous_suffix_is_not_guessed():
    """`1201` suffix-matches both `32-1201` and `132-1201`; assigning either would be a
    coin flip, so neither is touched."""
    secs = [
        _sec("https://law.justia.com/codes/x/section-32-1201/"),
        _sec("https://law.justia.com/codes/x/section-132-1201/"),
    ]
    assert backfill_citations_from_urls(secs, ["1201"]) == 0
    assert all(not s["citation"] for s in secs)


def test_two_citations_claiming_one_section_is_not_guessed():
    """If more than one cited string uniquely lands on the same blank section, we cannot
    tell which one names it -- leave it blank rather than pick."""
    secs = [_sec("https://law.justia.com/codes/x/section-59-328-3/")]
    assert backfill_citations_from_urls(secs, ["328.3", "59-328-3"]) == 0
    assert not secs[0]["citation"]


def test_section_without_a_parseable_url_is_skipped():
    secs = [_sec("https://law.justia.com/codes/oklahoma/title-59/")]
    assert backfill_citations_from_urls(secs, ["328.3"]) == 0


def test_no_cited_strings_is_a_noop():
    secs = [_sec("https://law.justia.com/codes/x/section-32-1201/")]
    assert backfill_citations_from_urls(secs, []) == 0


def test_ny_shape_bare_number_nested_under_a_sub_article():
    """NY nests the bare section number with no `section-` prefix:
    .../article-130-1/sub-art-1/6501/ -- the umbrella general provisions."""
    secs = [_sec("https://law.justia.com/codes/new-york/edn/title-8/article-130-1/sub-art-1/6501/")]
    assert backfill_citations_from_urls(secs, ["6501"]) == 1
    assert secs[0]["citation"] == "6501"


def test_short_citations_are_ignored_as_promiscuous():
    """A 1-2 char citation suffix-matches almost anything, including non-section URLs."""
    secs = [_sec("https://law.justia.com/codes/new-york/edn/title-8/")]
    assert backfill_citations_from_urls(secs, ["8"]) == 0
    assert not secs[0]["citation"]
