"""Tests for the quote-verification normalizer in extract_state.

The normalizer's job is to accept verbatim quotes even when the source has
typography variations and list-enumeration markers. It must NOT accept
paraphrases — if the model invented or reordered words, that should still
fail verification.
"""

import pytest

from pipeline.extract.extract_state import (
    _normalize_for_match,
    apply_derived_regulatory_model,
    quote_in_corpus,
)


class TestEnumerationStripping:
    """Real failure mode (May 2026): model quotes a list as prose, dropping
    the '(1)', '(2)', '(a)', '(i)' markers. Verbatim content; just no list
    numbers. Verification needs to accept these."""

    def test_list_with_numeric_markers_matches(self):
        corpus = "consent to the personal jurisdiction of the board (2) agree to comply with this chapter"
        quote = "consent to the personal jurisdiction of the board; agree to comply with this chapter"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc

    def test_list_with_roman_markers_matches(self):
        corpus = "has one year's experience that (i) meets the requirements (ii) is in any type of service"
        quote = "Has one year's experience that: Meets the requirements"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc

    def test_list_with_letter_markers_matches(self):
        corpus = "a person shall not without an active certificate of certified public accountant (a) as an independent auditor"
        quote = "A person shall not without an active certificate of certified public accountant: As an independent auditor"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc


class TestParaphrasesStillFail:
    """The enumeration fix must NOT make actual paraphrases pass."""

    def test_word_reorder_fails(self):
        corpus = "the doctor of podiatric medicine in this state"
        # Words moved around — not a verbatim quote
        quote = "in this state the doctor of podiatric medicine"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        # quote shouldn't be a substring of corpus after normalization
        assert nq not in nc

    def test_invented_word_fails(self):
        corpus = "the board shall license the applicant"
        quote = "the board must license every applicant"  # 'must' / 'every' are not in source
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq not in nc

    def test_summarization_fails(self):
        corpus = "graduation from a legally chartered school of podiatry approved by the board"
        quote = "graduation from a board-approved podiatry school"  # rewrite
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq not in nc


class TestTypographyAndCase:
    def test_smart_quotes_match_ascii(self):
        corpus = "the term ‘podiatrist’ means a person"  # curly quotes
        quote = "the term 'podiatrist' means a person"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc

    def test_em_dash_matches_hyphen(self):
        corpus = "podiatric medicine — the diagnosis and treatment"
        quote = "podiatric medicine - the diagnosis and treatment"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc

    def test_lowercase_matches_upper(self):
        corpus = "DEFINITIONS. As used in this chapter"
        quote = "Definitions. As used in this chapter"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc


class TestEnumStrippingEdgeCases:
    def test_parenthesized_three_digit_marker_stripped(self):
        corpus = "the licensee shall (99) keep records of all transactions"
        quote = "the licensee shall keep records of all transactions"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc

    def test_nested_parenthesized_markers_stripped(self):
        corpus = "the applicant shall (a)(1) hold a degree (b)(2) pay fees"
        quote = "the applicant shall hold a degree pay fees"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc


class TestArticleSwapStillFails:
    """Critical regression: stripping list markers must NOT also strip bare
    English words like 'a' or 'i'. A model that paraphrases 'the doctor' as
    'a doctor' should still fail verification."""

    def test_article_swap_a_vs_the(self):
        corpus = "the doctor of medicine shall apply"
        quote = "a doctor of medicine shall apply"  # paraphrase
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        # 'a' is a real word here, not a list marker — must NOT match
        assert nq not in nc

    def test_pronoun_i_not_stripped(self):
        corpus = "the applicant shall affirm i have read this chapter"
        quote = "the applicant shall affirm have read this chapter"  # dropped 'i'
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        # 'i' is a real word here (pronoun), shouldn't be stripped
        assert nq not in nc

    def test_legal_citation_roman_not_stripped(self):
        """NH-style citation 'RSA 318-B:10, IX.' — the IX is a subsection
        of the cited law, NOT a list marker for OUR text. Must not strip."""
        corpus = "procedures pursuant to RSA 318-B:10, IX. as amended"
        quote = "procedures pursuant to RSA 318-B:10, IX."
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        # Quote should still match — IX is preserved in both
        assert nq in nc
        # And IX should still be in the normalized form
        assert "ix" in nc

    def test_legal_citation_numbered_part_not_stripped(self):
        """MT-style 'Title 2, chapter 15, part 17' — these numbers are
        part of a citation, not list markers."""
        corpus = "the department provided for in Title 2, chapter 15, part 17"
        quote = "the department provided for in Title 2, chapter 15, part 17"
        nc = _normalize_for_match(corpus)
        nq = _normalize_for_match(quote)
        assert nq in nc
        # Specifically: "part 17" should survive
        assert "part 17" in nc


class TestDerivedRegulatoryModelClearsOrphanedQuote:
    """issue #62: the rung is derived from credential_type + scope_protection rather
    than trusting the model's pick. When that override changes the value, the model's
    quote justified the OLD value — left in place it renders in the state-detail Sheet
    as a sky-blue "verified" card arguing against its own value.
    """

    def _record(self, model_pick, credential, scope_protected):
        return {"licensure": {
            "regulatory_model": {
                "value": model_pick,
                "quote": "It shall be unlawful for any individual to represent oneself as an "
                         "emergency medical service provider unless such individual holds a "
                         "valid certificate as such under this act.",
                "citation": "65-6150",
            },
            "credential_type": {"value": credential, "quote": "...certificate...", "citation": "65-6129"},
            "scope_protection": {"value": scope_protected, "quote": "...", "citation": "65-6150"},
        }}

    def test_override_clears_quote_and_flags_derived(self):
        # The real EMT/KS case from the issue: model says "license", but
        # certification + no scope protection derives voluntary_certification.
        rec = self._record("license", "certification", False)
        apply_derived_regulatory_model(rec, "KS")
        rm = rec["licensure"]["regulatory_model"]
        assert rm["value"] != "license", "derivation did not override the model's pick"
        assert rm["quote"] == "", "orphaned quote survived the override"
        assert rm["citation"] == ""
        assert rm["derived"] is True

    def test_supporting_fields_keep_their_own_evidence(self):
        """No evidence is lost: the rung's inputs still carry their quotes."""
        rec = self._record("license", "certification", False)
        apply_derived_regulatory_model(rec, "KS")
        lic = rec["licensure"]
        assert lic["credential_type"]["quote"]
        assert lic["scope_protection"]["citation"]

    def test_no_override_leaves_the_quote_intact(self):
        """When the model's pick already agrees with the derivation there is no
        orphan — the quote genuinely supports the value and must survive."""
        rec = self._record("license", "license", True)
        before = rec["licensure"]["regulatory_model"]["quote"]
        apply_derived_regulatory_model(rec, "UT")
        rm = rec["licensure"]["regulatory_model"]
        assert rm["quote"] == before, "a still-valid quote was cleared"
        assert "derived" not in rm
