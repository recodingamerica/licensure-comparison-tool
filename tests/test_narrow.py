"""Tests for pipeline.discover.gap_harvest.narrow — the over-broad target auto-narrower.

Locks the pure decision logic (the CDP walk is exercised separately with Chrome up):
  - whole-title URLs are over-broad; a named large chapter that matches the profession is NOT
  - a sub-part whose label names the profession short-circuits to that part
  - leaf title-matches range-FILL between min/max so gap sections come along
  - no anchor at all → None (candidate absence, flagged not dropped)
"""
import pipeline.discover.gap_harvest.narrow as N


# --- whole_title / is_over_broad -------------------------------------------------
def test_whole_title_detection():
    assert N.whole_title("https://law.justia.com/codes/louisiana/revised-statutes/title-40/")
    assert N.whole_title("https://law.justia.com/codes/north-dakota/title-64")
    assert not N.whole_title("https://law.justia.com/codes/kentucky/chapter-164/")
    # a subtitle UNDER a title is not the whole title
    assert not N.whole_title("https://law.justia.com/codes/maryland/agriculture/title-11/subtitle-2/")


def test_over_broad_spares_legit_named_chapter():
    pats = ["medical practice", "physician"]
    # big corpus but the chapter label matches the profession → NOT over-broad
    assert N.is_over_broad("…/chapter-2052/", "Medical Practice Act", pats, [], corpus_n=513) is None
    # big corpus + label does NOT match → over-broad
    assert N.is_over_broad("…/title-40/x/", "Public Health and Safety", pats, [], corpus_n=513) \
        == "huge_corpus_label_mismatch"
    # whole-title URL flagged regardless of size
    assert N.is_over_broad("…/title-40/", "Part II Emergency Medical Personnel", pats, [], None) \
        == "whole_title"
    # small corpus, no match → fine (short real chapter)
    assert N.is_over_broad("…/chapter-11/", "Public Weighmasters", ["weighmaster"], [], 8) is None


# --- section_key ---------------------------------------------------------------
def test_section_key_parses_varied_slugs():
    assert N.section_key(".../section-164-6901/") == (164, 6901)
    assert N.section_key(".../rs-40-1133-1/") == (40, 1133, 1)
    assert N.section_key(".../statute-44-9204/") == (44, 9204)
    assert N.section_key(".../part-ii/") is None  # no trailing number → unparseable


# --- scope_from_children -------------------------------------------------------
def test_named_subpart_short_circuits():
    # EMT-style: a Part whose label names the profession → pull that whole part
    children = [
        {"label": "Part I - General", "url": "http://j/t40/part-1/"},
        {"label": "Part II - Emergency Medical Personnel", "url": "http://j/t40/part-2/"},
    ]
    pats = ["emergency medical personnel", "paramedic"]
    got = N.scope_from_children(children, pats, [])
    assert got == {"url": "http://j/t40/part-2/", "label": "Part II - Emergency Medical Personnel"}


def test_leaf_matches_range_fill_includes_gap_section():
    # athlete-agent-style flat chapter: two hits anchor a range; a non-matching section
    # BETWEEN them (a definitions/penalty section) is pulled in by the range-fill.
    children = [
        {"label": "164.6899 - Unrelated university section", "url": "http://j/ch164/section-164-6899/"},
        {"label": "164.6903 - Registration as athlete agent required", "url": "http://j/ch164/section-164-6903/"},
        {"label": "164.6910 - Fees", "url": "http://j/ch164/section-164-6910/"},          # gap, no pattern
        {"label": "164.6935 - Uniform athlete agents act; citation", "url": "http://j/ch164/section-164-6935/"},
        {"label": "164.7100 - Scholarship program", "url": "http://j/ch164/section-164-7100/"},  # out of range
    ]
    pats = ["athlete agent", "uniform athlete agents"]
    got = N.scope_from_children(children, pats, [])
    urls = got["section_url_list"]
    assert "http://j/ch164/section-164-6903/" in urls
    assert "http://j/ch164/section-164-6910/" in urls   # gap section range-filled
    assert "http://j/ch164/section-164-6935/" in urls
    assert "http://j/ch164/section-164-6899/" not in urls   # below range
    assert "http://j/ch164/section-164-7100/" not in urls   # above range


def test_scattered_hits_pick_densest_cluster_not_whole_chapter():
    # A broad insurance chapter name-drops "insurance producer" in a few scattered
    # sections; the real Producers Licensing Act is a tight contiguous run. Only that
    # run is captured — NOT everything between the first and last scattered mention.
    children = [{"label": "44-101 - insurance producer in unfair practices",
                 "url": "http://j/c44/statute-44-101/"}]
    for n in range(200, 220):                       # 20 unrelated spacers
        children.append({"label": f"44-{n} - unrelated", "url": f"http://j/c44/statute-44-{n}/"})
    for n in (4047, 4048, 4049, 4050, 4055):        # the act — contiguous hits
        children.append({"label": f"44-{n} - insurance producer licensing",
                         "url": f"http://j/c44/statute-44-{n}/"})
    children.append({"label": "44-4051 - fees", "url": "http://j/c44/statute-44-4051/"})  # gap
    for n in range(5000, 5010):                     # more spacers
        children.append({"label": f"44-{n} - unrelated", "url": f"http://j/c44/statute-44-{n}/"})
    children.append({"label": "44-9204 - insurance producer reference",
                     "url": "http://j/c44/statute-44-9204/"})       # far lone hit

    urls = N.scope_from_children(children, ["insurance producer"], [])["section_url_list"]
    assert any("44-4047" in u for u in urls) and any("44-4055" in u for u in urls)
    assert any("44-4051" in u for u in urls)                # gap inside the act filled
    assert not any("44-101" in u for u in urls)             # scattered noise excluded
    assert not any("44-9204" in u for u in urls)
    assert len(urls) < 10                                   # the act, not the chapter


def test_no_anchor_is_absence():
    # weighmaster mapped to a wrong chapter whose sections never mention it → None
    children = [
        {"label": "189.010 - Traffic definitions", "url": "http://j/ch189/section-189-010/"},
        {"label": "189.223 - Weighing of vehicle by peace officer", "url": "http://j/ch189/section-189-223/"},
    ]
    assert N.scope_from_children(children, ["weighmaster"], []) is None


def test_excludes_veto_leaf_match():
    children = [{"label": "1 - Direct-entry midwife registration", "url": "http://j/c/section-1/"}]
    assert N.scope_from_children(children, ["midwife"], ["direct-entry"]) is None
