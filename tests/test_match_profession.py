"""Tests for pipeline.discover.match_profession.label_matches.

The label matcher is the load-bearing piece of every (state, profession) pair
that doesn't have a hand-curated override. Locks in:
  - pattern matching is case-insensitive
  - excludes always beat patterns (per-profession excludes)
  - the universal `(Repealed.)` filter applies to every profession (added
    after NM CPA hit Articles 28 + 28A repealed alongside the live 28B)
"""

from pipeline.discover.match_profession import (
    label_matches,
    _umbrella_nodes_for,
    _official_url,
)


CPA_PATTERNS = ["accountant", "accountancy", "public accounting", "certified public account"]
PODIATRY_PATTERNS = ["podiatry", "podiatric", "chiropodist"]


class TestPatternBasics:
    def test_pattern_substring_matches(self):
        assert label_matches("Chapter 12 - ACCOUNTANTS", CPA_PATTERNS, [])

    def test_case_insensitive(self):
        assert label_matches("chapter 1 - ACCOUNTANTS", CPA_PATTERNS, [])
        assert label_matches("CHAPTER 1 - accountants", CPA_PATTERNS, [])

    def test_no_pattern_match(self):
        assert not label_matches("Chapter 99 - Money of Account and Interest", PODIATRY_PATTERNS, [])

    def test_empty_label(self):
        assert not label_matches("", CPA_PATTERNS, [])


class TestExcludes:
    def test_exclude_beats_pattern(self):
        assert not label_matches(
            "Article 99 - Public Health Accounting",
            CPA_PATTERNS,
            excludes=["public health"],
        )

    def test_exclude_is_case_insensitive(self):
        assert not label_matches(
            "Article 99 - PUBLIC HEALTH Accounting",
            CPA_PATTERNS,
            excludes=["public health"],
        )

    def test_no_excludes_no_effect(self):
        assert label_matches("Chapter 1 - Accountants", CPA_PATTERNS, excludes=[])


class TestRepealedUniversalExclude:
    """`(Repealed.)` and variants must filter out for ALL professions.

    Locked in 2026-05-12 after NM CPA returned 3 matches (Articles 28, 28A,
    28B) where two were repealed but the live one was the third — extract
    choked on the empty repealed-text trims.
    """

    def test_repealed_with_period(self):
        # NM-style: "Article 28 - Public Accountants (Repealed.)"
        assert not label_matches("Article 28 - Public Accountants (Repealed.)", CPA_PATTERNS, [])

    def test_repealed_no_period(self):
        assert not label_matches("Chapter 12 - Accountants (Repealed)", CPA_PATTERNS, [])

    def test_repealed_brackets(self):
        assert not label_matches("Chapter 12 - Accountants [Repealed]", CPA_PATTERNS, [])

    def test_repealed_case_insensitive(self):
        assert not label_matches("Article 28 - PODIATRISTS (REPEALED.)", PODIATRY_PATTERNS, [])

    def test_live_version_still_matches(self):
        """The whole point: the active sibling shouldn't be filtered."""
        assert label_matches("Article 28B - 1999 Public Accountancy Act", CPA_PATTERNS, [])

    def test_repealed_applies_even_with_no_pattern_excludes(self):
        # Even if the profession has no `excludes`, repealed still drops
        assert not label_matches("Chapter 30-11 - Podiatry (Repealed.)", PODIATRY_PATTERNS, excludes=[])


class TestUmbrellaNodes:
    """State-level additive umbrella chapters (e.g. WA Ch 18.130 for every WA
    health profession). See docs/runbooks/wa_umbrella_mechanism.md."""

    WA_UMBRELLA = {
        "umbrella": {
            "professions": ["medicine", "nursing", "podiatry"],
            "chapters": [{
                "url": "https://law.justia.com/codes/washington/title-18/chapter-18-130/",
                "label": "WA Ch 18.130 — Uniform Disciplinary Act",
            }],
        }
    }
    WA_TEMPLATE = "https://app.leg.wa.gov/RCW/default.aspx?cite={chapter_dot}&full=true"

    def test_in_scope_profession_gets_node(self):
        nodes = _umbrella_nodes_for(self.WA_UMBRELLA, "medicine", existing_urls=set())
        assert len(nodes) == 1
        assert "18-130" in nodes[0]["url"]
        assert nodes[0]["via"] == "state_structure_umbrella"

    def test_out_of_scope_profession_gets_nothing(self):
        assert _umbrella_nodes_for(self.WA_UMBRELLA, "architecture", set()) == []

    def test_no_umbrella_block(self):
        assert _umbrella_nodes_for({"source": "wa_official"}, "medicine", set()) == []

    def test_already_matched_url_skipped(self):
        url = "https://law.justia.com/codes/washington/title-18/chapter-18-130/"
        assert _umbrella_nodes_for(self.WA_UMBRELLA, "medicine", existing_urls={url}) == []

    def test_template_rewrites_umbrella_to_official_source(self):
        # The umbrella node carries a Justia chapter url; the WA template must
        # rewrite it to the official cite= url (so it's fetched from wa.gov, not
        # Cloudflare-blocked Justia).
        node = _umbrella_nodes_for(self.WA_UMBRELLA, "nursing", set())[0]
        official = _official_url(self.WA_TEMPLATE, node["url"])
        assert official == "https://app.leg.wa.gov/RCW/default.aspx?cite=18.130&full=true"
