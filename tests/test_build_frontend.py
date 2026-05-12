"""Tests for build_frontend's credential_type/is_mandatory derivation.

The build_frontend layer derives the orthogonal (credential_type, is_mandatory)
view from the legacy single-axis regulatory_model when the new fields aren't
directly populated. Lock in this back-compat behavior so existing podiatry
data gets the new columns for free.
"""

import pytest

from pipeline.publish.build_frontend import _derive_credential_and_mandatory


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
