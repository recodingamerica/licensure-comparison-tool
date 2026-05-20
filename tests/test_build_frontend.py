"""Tests for build_frontend's credential_type/is_mandatory derivation.

The build_frontend layer derives the orthogonal (credential_type, is_mandatory)
view from the legacy single-axis regulatory_model when the new fields aren't
directly populated. Lock in this back-compat behavior so existing podiatry
data gets the new columns for free.
"""

import pytest

from pipeline.publish.build_frontend import (
    _derive_credential_and_mandatory,
    normalize_citation,
)


class TestDerivationFromLegacyRegulatoryModel:
    @pytest.mark.parametrize("rm, expected", [
        ("license",                  ("license", True)),
        ("mandatory_certification",  ("certification", True)),
        ("voluntary_certification",  ("certification", False)),
        ("registration",             ("registration", True)),
        ("market_forces",            ("none", False)),
        ("exemption",                ("exemption", None)),
    ])
    def test_each_rung_derives_correctly(self, rm, expected):
        lic = {"regulatory_model": {"value": rm, "quote": "q", "citation": "c"}}
        assert _derive_credential_and_mandatory(lic) == expected

    def test_missing_regulatory_model_returns_none(self):
        assert _derive_credential_and_mandatory({}) == (None, None)

    def test_invalid_regulatory_model_value_returns_none(self):
        lic = {"regulatory_model": {"value": "not_a_real_rung", "quote": "q", "citation": "c"}}
        assert _derive_credential_and_mandatory(lic) == (None, None)


class TestDirectFieldsPreferred:
    """If a future extraction populates credential_type + is_mandatory directly,
    we use those rather than re-deriving from regulatory_model."""

    def test_direct_credential_type_overrides_derivation(self):
        lic = {
            "regulatory_model": {"value": "license", "quote": "q", "citation": "c"},
            "credential_type": {"value": "registration", "quote": "q2", "citation": "c2"},
            "is_mandatory": {"value": False, "quote": "q3", "citation": "c3"},
        }
        assert _derive_credential_and_mandatory(lic) == ("registration", False)

    def test_direct_partial_population(self):
        """If only one of the new fields is populated, the other comes from that
        same record (not from re-deriving regulatory_model)."""
        lic = {
            "regulatory_model": {"value": "license", "quote": "q", "citation": "c"},
            "credential_type": {"value": "license", "quote": "q2", "citation": "c2"},
            # is_mandatory absent
        }
        ct, im = _derive_credential_and_mandatory(lic)
        assert ct == "license"
        assert im is None  # we don't half-derive


class TestNormalizeCitation:
    """`normalize_citation` cleans up the LLM's per-state citation strings
    so the published JSON ships a consistent display form. Idempotent."""

    @pytest.mark.parametrize("raw, want", [
        # Bracketed (KY style)
        ("[314.031]",                            "314.031"),
        ("[34-24-704]",                          "34-24-704"),
        # Trailing period only
        ("32-827.",                              "32-827"),
        ("Section 2474.",                        "Section 2474"),
        # `§ NN. Title` (Vermont style) — strip the title, keep the section
        ("§ 324. Prohibitions; penalties",        "§ 324"),
        ("§ 1721. Definitions",                   "§ 1721"),
        # `§ 324.5` is a sub-section, NOT a title — leave it alone
        ("§ 324.5",                               "§ 324.5"),
        # `Section NN - Title -- ...` (Utah / Nebraska style)
        ("Section 301 - License required -- License classifications.",
         "Section 301"),
        ("Section 302 - Qualifications to practice podiatry.",
         "Section 302"),
        # ` -- ` separator alone
        ("65-2002 -- Definitions",                "65-2002"),
        # UMBRELLA prefix preserved, but body cleaned
        ("UMBRELLA / 38-167 - Boards; designated; change in name; effect.",
         "UMBRELLA / 38-167"),
        # Clean inputs pass through unchanged (idempotent)
        ("311.400",                               "311.400"),
        ("RS 37:912",                             "RS 37:912"),
        ("20-50a",                                "20-50a"),
        # Empty / whitespace
        ("",                                      ""),
        ("   ",                                   ""),
    ])
    def test_normalize(self, raw, want):
        assert normalize_citation(raw) == want

    def test_idempotent(self):
        """Applying twice yields the same result as applying once."""
        for raw in [
            "[314.031]",
            "§ 324. Prohibitions",
            "Section 301 - License required",
            "UMBRELLA / 38-167 - Boards",
        ]:
            once = normalize_citation(raw)
            twice = normalize_citation(once)
            assert once == twice
