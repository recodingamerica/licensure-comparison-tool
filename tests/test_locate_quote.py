"""Tests for pipeline.extract.locate_quote — the single matcher that the
verifier (bool) and the frontend (spans) will both eventually share.

Once build_frontend.py emits quote_spans, the TS-side normalize code goes
away and divergence between Python and TS becomes impossible. These tests
lock in the contract: spans index into the ORIGINAL section text, work
across smart quotes and list markers, support ellipsis-elided quotes, and
return None when there's no honest highlight to paint.
"""

from __future__ import annotations

from pipeline.extract.locate_quote import (
    locate_quote_in_section,
    normalize_for_match,
    normalize_with_mapping,
    quote_in_corpus,
)


class TestNormalizeWithMapping:
    def test_basic_identity_for_simple_ascii(self):
        norm, idx = normalize_with_mapping("Hello World")
        assert norm == "hello world"
        # 1-to-1 mapping when no chars are dropped or expanded
        assert idx == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_list_marker_skipped_offsets_jump_over_it(self):
        text = "shall (1) comply with"
        norm, idx = normalize_with_mapping(text)
        assert norm == "shall comply with"
        # Walk the normalized text and confirm each non-space char in
        # `norm` round-trips to an equal char in the original.
        for i, c in enumerate(norm):
            if c != " ":
                assert text[idx[i]].lower() == c

    def test_smart_quote_normalizes_but_offsets_point_at_curly_char(self):
        text = "term ‘x’"  # term 'x' with curly quotes
        norm, idx = normalize_with_mapping(text)
        assert norm == "term x"
        # 'x' in normalized lands on the original 'x' position
        x_pos_norm = norm.index("x")
        assert text[idx[x_pos_norm]] == "x"

    def test_ellipsis_char_expands_to_three_dots_same_src_index(self):
        # The ellipsis char expands to "..." in normalization. The dots
        # then become spaces (non-alnum) and collapse — but each emitted
        # char inherits the original ellipsis position. This matters when
        # a quote contains a literal "..." that matches a "…" in the
        # source: spans must not point past the ellipsis position.
        text = "first…last"
        norm, idx = normalize_with_mapping(text)
        assert norm == "first last"
        # The single space between "first" and "last" must come from the
        # ellipsis position (index 5), NOT from after it.
        space_pos_norm = norm.index(" ")
        assert idx[space_pos_norm] == 5

    def test_whitespace_trimmed_leading_and_trailing(self):
        norm, idx = normalize_with_mapping("   hi there   ")
        assert norm == "hi there"
        # First normalized char is from somewhere in the original leading
        # whitespace region — specifically the first non-space char.
        assert norm[0] == "h"

    def test_unicode_letter_outside_ascii_becomes_space(self):
        # "é" isn't in SMART_MAP and isn't [a-z0-9 ], so it becomes a
        # space. Real-world: prevents stray accented chars from blocking
        # a match the legacy verifier would have allowed.
        norm, _ = normalize_with_mapping("café menu")
        assert norm == "caf menu"


class TestLocateQuoteInSection:
    def test_simple_substring_returns_one_span_that_slices_back(self):
        section = "The applicant must comply with this chapter."
        quote = "must comply with this chapter"
        spans = locate_quote_in_section(quote, section)
        assert spans is not None and len(spans) == 1
        s, e = spans[0]
        assert section[s:e] == "must comply with this chapter"

    def test_ellipsis_split_returns_two_ordered_spans(self):
        section = (
            "The board shall determine the qualifications of each "
            "applicant and shall issue a license to those who meet them."
        )
        quote = "board shall determine the qualifications ... issue a license"
        spans = locate_quote_in_section(quote, section)
        assert spans is not None and len(spans) == 2
        s1, e1 = spans[0]
        s2, e2 = spans[1]
        assert section[s1:e1] == "board shall determine the qualifications"
        assert section[s2:e2] == "issue a license"
        assert e1 < s2  # non-overlapping, in order

    def test_smart_quote_in_source_matches_ascii_quote(self):
        section = "the term ‘podiatrist’ means a person"
        quote = "the term 'podiatrist' means a person"
        spans = locate_quote_in_section(quote, section)
        assert spans is not None and len(spans) == 1
        s, e = spans[0]
        # The highlight covers the curly quotes in the rendered source —
        # that's intentional: the UI paints the original text.
        sliced = section[s:e]
        assert "podiatrist" in sliced
        assert sliced.startswith("the term")
        assert sliced.endswith("a person")

    def test_list_marker_inside_match_keeps_span_continuous(self):
        # The model dropped the "(1)" but the source has it. We want the
        # rendered highlight to be a single continuous mark covering the
        # marker — readers shouldn't see the highlight tear around it.
        section = "the applicant shall (1) hold a degree and comply"
        quote = "the applicant shall hold a degree and comply"
        spans = locate_quote_in_section(quote, section)
        assert spans is not None and len(spans) == 1
        s, e = spans[0]
        sliced = section[s:e]
        assert "(1)" in sliced
        assert sliced.startswith("the applicant shall")
        assert sliced.endswith("comply")

    def test_quote_not_in_section_returns_none(self):
        assert (
            locate_quote_in_section(
                "something else entirely that does not appear",
                "Only this short text is here.",
            )
            is None
        )

    def test_empty_quote_returns_none(self):
        assert locate_quote_in_section("", "some section text") is None

    def test_too_short_quote_returns_none(self):
        # Below the 8-char normalized threshold — not strong evidence.
        assert (
            locate_quote_in_section("board", "The board shall determine.")
            is None
        )

    def test_out_of_order_ellipsis_segments_return_none(self):
        section = "Apple first, then banana, then cherry."
        quote = "then cherry ... Apple first"
        assert locate_quote_in_section(quote, section) is None

    def test_repeated_phrase_picks_first_then_next_segment_after(self):
        # Two occurrences of "the board"; an ellipsis-split quote should
        # match the first occurrence, then resume looking AFTER that
        # match. This is the property quote_in_corpus also relies on.
        section = "the board may; later the board shall and the board can"
        quote = "the board may ... the board shall"
        spans = locate_quote_in_section(quote, section)
        assert spans is not None and len(spans) == 2
        s1, e1 = spans[0]
        s2, e2 = spans[1]
        assert section[s1:e1] == "the board may"
        assert section[s2:e2] == "the board shall"


class TestInlineListMarkersInQuote:
    """When the LLM quotes ACROSS a line-break-broken list, it tends to
    inline the marker (`chapter: 1. Practices…`). The matcher preserves
    bare-form line-start markers in the corpus so they survive normalization
    and the inline quote still matches. See locate_quote.py's comment on
    `_LIST_MARKER_AT_START_RE` for the measurement that justifies this."""

    def test_inline_marker_in_quote_matches_line_break_marker_in_corpus(self):
        # AZ 32-1261 dentistry shape: corpus puts list items on their own
        # lines; LLM joins them inline with a single space.
        corpus = normalize_for_match(
            "Except as otherwise provided a person is guilty of a class 6 "
            "felony who, without a valid license:\n"
            "1. Practices dentistry or any branch of dentistry."
        )
        quote = (
            "Except as otherwise provided a person is guilty of a class 6 "
            "felony who, without a valid license: 1. Practices dentistry"
        )
        assert quote_in_corpus(quote, corpus) is True


class TestQuoteInCorpus:
    """Bool API — kept so verifier can still ask "does this quote appear
    SOMEWHERE in the combined corpus" as a looser fallback when
    locate_quote_in_section returns None on a single section."""

    def test_simple_match_returns_true(self):
        corpus = normalize_for_match("The applicant must comply with this chapter.")
        assert quote_in_corpus("must comply with this chapter", corpus) is True

    def test_paraphrase_returns_false(self):
        corpus = normalize_for_match("the doctor of podiatric medicine in this state")
        # word reordering — not verbatim
        assert quote_in_corpus("in this state the doctor of podiatric medicine", corpus) is False

    def test_ellipsis_in_order_returns_true(self):
        corpus = normalize_for_match(
            "The board shall determine the qualifications of each "
            "applicant and shall issue a license to those who meet them."
        )
        assert (
            quote_in_corpus(
                "board shall determine the qualifications ... issue a license",
                corpus,
            )
            is True
        )

    def test_ellipsis_out_of_order_returns_false(self):
        corpus = normalize_for_match("Apple first, then banana, then cherry.")
        assert quote_in_corpus("then cherry ... Apple first", corpus) is False

    def test_empty_quote_returns_false(self):
        corpus = normalize_for_match("anything goes here")
        assert quote_in_corpus("", corpus) is False
