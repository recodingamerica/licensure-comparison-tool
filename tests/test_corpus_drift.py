"""Tests for pipeline.eval.corpus_drift pure logic — the URL normalization that
decides whether a corpus chapter matches an index chapter. The file I/O
(audit_one over results/) isn't unit-tested; the fragile part is _chapter_key /
_covered, which must collapse section leaves to chapters WITHOUT over-stripping
chapter-level segments like "statute-act-297-of-1965" or "subtitle-4".
"""

import pipeline.eval.corpus_drift as cd


class TestHost:
    def test_relative_codes_path_is_justia(self):
        assert cd._host("/codes/michigan/chapter-338/") == "law.justia.com"

    def test_absolute_host(self):
        assert cd._host("https://mgaleg.maryland.gov/x") == "mgaleg.maryland.gov"


class TestChapterKey:
    def test_justia_section_leaf_collapses_to_chapter(self):
        assert (cd._chapter_key("https://law.justia.com/codes/minnesota/chapters-144-159/chapter-147/section-147-01/")
                == "law.justia.com/codes/minnesota/chapters-144-159/chapter-147")

    def test_part_and_section_both_stripped(self):
        assert (cd._chapter_key("https://law.justia.com/codes/utah/title-58/chapter-55/part-1/section-101/")
                == "law.justia.com/codes/utah/title-58/chapter-55")

    def test_umbrella_chapter_kept_distinct(self):
        # the UT chapter-1 umbrella must NOT collapse into chapter-55
        assert (cd._chapter_key("https://law.justia.com/codes/utah/title-58/chapter-1/part-2/section-501/")
                == "law.justia.com/codes/utah/title-58/chapter-1")

    def test_statute_act_segment_not_stripped(self):
        # "statute-act-297-of-1965" is a chapter-level node, not a leaf
        assert (cd._chapter_key("/codes/michigan/chapter-338/statute-act-297-of-1965/")
                == "law.justia.com/codes/michigan/chapter-338/statute-act-297-of-1965")

    def test_justia_version_suffix_leaf_stripped(self):
        # AZ scoped sections carry a -version-N suffix Justia sometimes adds
        assert (cd._chapter_key("https://law.justia.com/codes/arizona/title-32/section-32-1101-version-2/")
                == "law.justia.com/codes/arizona/title-32")

    def test_official_host_leaf_left_intact_is_fine(self):
        # official-host section filenames aren't collapsed — but audit_one skips
        # active-intercept states, so _chapter_key only needs Justia shapes right.
        k = cd._chapter_key("https://legislature.maine.gov/statutes/32/title32sec1101.html")
        assert k.startswith("legislature.maine.gov/statutes/32")


class TestOfficialSourceSkip:
    def test_ny_not_skipped_after_intercept_gated(self):
        # NY's is_ny_justia_url intercept was gated on source == ny_official
        # (NY flipped to Justia 2026-07-02), so NY is real drift again, not skipped.
        assert "NY" not in cd._active_official_sources()

    def test_active_source_state_skipped_but_retired_not(self):
        got = cd._active_official_sources()
        assert "WA" in got          # active source: wa_official
        assert "MN" not in got      # source retired/commented -> real drift detection


class TestCovered:
    def test_index_chapter_covers_more_granular_corpus_subchapter(self):
        idx = {"law.justia.com/codes/arkansas/title-17/subtitle-2/chapter-28"}
        corpus = "law.justia.com/codes/arkansas/title-17/subtitle-2/chapter-28/subchapter-1"
        assert cd._covered(corpus, idx)

    def test_unrelated_chapter_not_covered(self):
        idx = {"law.justia.com/codes/utah/title-58/chapter-55"}
        assert not cd._covered("law.justia.com/codes/utah/title-58/chapter-1", idx)

    def test_host_mismatch_not_covered(self):
        idx = {"law.justia.com/codes/maryland/business-occupations-and-professions/title-6"}
        assert not cd._covered("mgaleg.maryland.gov/mgawebsite/Laws/StatuteText", idx)
