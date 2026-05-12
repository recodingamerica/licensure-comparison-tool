"""Tests for the universal Pydantic pieces in pipeline.extract.standard_model.

The RegulatoryModel Enum and Evidence carriers are the API the LLM
schema sends to Anthropic. Locking in the values + validation behavior so a
refactor (adding CredentialType + is_mandatory per meeting Q1) doesn't
silently break the existing extraction shape.
"""

import pytest
from pydantic import ValidationError

from pipeline.extract.standard_model import (
    RegulatoryModel,
    RegulatoryModelEvidence,
    CredentialType,
    CredentialTypeEvidence,
    LicensureRequirements,
    StrEvidence,
    BoolEvidence,
    IntEvidence,
    StrListEvidence,
    REGULATORY_MODEL_DECOMPOSITION,
    decompose_regulatory_model,
)


class TestRegulatoryModelEnum:
    """The six UORF rungs are the user-facing taxonomy — value strings
    end up in JSON and become the keys downstream callers filter on."""

    def test_has_six_rungs(self):
        assert len(list(RegulatoryModel)) == 6

    @pytest.mark.parametrize("name, value", [
        ("MARKET_FORCES", "market_forces"),
        ("VOLUNTARY_CERTIFICATION", "voluntary_certification"),
        ("REGISTRATION", "registration"),
        ("EXEMPTION", "exemption"),
        ("MANDATORY_CERTIFICATION", "mandatory_certification"),
        ("LICENSE", "license"),
    ])
    def test_rung_value(self, name, value):
        assert getattr(RegulatoryModel, name).value == value

    def test_is_str_enum(self):
        """Should serialize as the string value (not 'RegulatoryModel.LICENSE')."""
        assert RegulatoryModel.LICENSE == "license"

    def test_invalid_value_rejected(self):
        with pytest.raises(ValidationError):
            RegulatoryModelEvidence(value="not_a_rung", quote="x", citation="y")


class TestEvidenceCarriers:
    def test_str_evidence_round_trip(self):
        ev = StrEvidence(value="Doctor of Podiatric Medicine", quote="DPM", citation="20-65")
        assert ev.value == "Doctor of Podiatric Medicine"
        d = ev.model_dump()
        assert d == {"value": "Doctor of Podiatric Medicine", "quote": "DPM", "citation": "20-65"}

    def test_bool_evidence_accepts_bool(self):
        ev = BoolEvidence(value=True, quote="q", citation="c")
        assert ev.value is True

    def test_int_evidence_rejects_non_numeric_string(self):
        with pytest.raises(ValidationError):
            IntEvidence(value="two", quote="q", citation="c")

    def test_bool_evidence_rejects_dict(self):
        # Pydantic coerces "yes"/"true"/1/"1" → bool; only outright non-bool-likes fail
        with pytest.raises(ValidationError):
            BoolEvidence(value={"some": "dict"}, quote="q", citation="c")

    def test_str_list_evidence(self):
        ev = StrListEvidence(value=["a", "b"], quote="q", citation="c")
        assert ev.value == ["a", "b"]


class TestCredentialTypeEnum:
    """Meeting Q1 decomposition: credential shape independent of mandatory bit."""

    def test_has_five_values(self):
        assert len(list(CredentialType)) == 5

    @pytest.mark.parametrize("name, value", [
        ("NONE", "none"),
        ("REGISTRATION", "registration"),
        ("CERTIFICATION", "certification"),
        ("LICENSE", "license"),
        ("EXEMPTION", "exemption"),
    ])
    def test_value(self, name, value):
        assert getattr(CredentialType, name).value == value

    def test_invalid_value_rejected(self):
        with pytest.raises(ValidationError):
            CredentialTypeEvidence(value="totally_made_up", quote="q", citation="c")


class TestRegulatoryModelDecomposition:
    """Every UORF rung must map to (CredentialType, is_mandatory) so back-compat
    derivation works when only one side of the schema is populated."""

    def test_every_rung_has_a_decomposition(self):
        assert set(REGULATORY_MODEL_DECOMPOSITION.keys()) == set(RegulatoryModel)

    @pytest.mark.parametrize("rung, expected", [
        (RegulatoryModel.LICENSE, (CredentialType.LICENSE, True)),
        (RegulatoryModel.MANDATORY_CERTIFICATION, (CredentialType.CERTIFICATION, True)),
        (RegulatoryModel.VOLUNTARY_CERTIFICATION, (CredentialType.CERTIFICATION, False)),
        (RegulatoryModel.REGISTRATION, (CredentialType.REGISTRATION, True)),
        (RegulatoryModel.MARKET_FORCES, (CredentialType.NONE, False)),
        (RegulatoryModel.EXEMPTION, (CredentialType.EXEMPTION, None)),
    ])
    def test_decompose(self, rung, expected):
        assert decompose_regulatory_model(rung) == expected

    def test_no_two_rungs_decompose_identically(self):
        """The 6 rungs should each be distinguishable in the (type, mandatory) plane."""
        seen = set()
        for rung, decomp in REGULATORY_MODEL_DECOMPOSITION.items():
            assert decomp not in seen, f"{rung} collides with another rung in decomposition"
            seen.add(decomp)


class TestLicensureRequirementsNewFields:
    """The new orthogonal fields are optional on existing records (don't break
    parsing the 80+ already-extracted state files) but accept the new shape."""

    def test_existing_data_without_new_fields_still_validates(self):
        # An old extraction with only regulatory_model populated should still parse
        rec = {
            "regulatory_model": {
                "value": "license",
                "quote": "must be licensed to practice",
                "citation": "20-65",
            },
            "title_protection": {"value": True, "quote": "x", "citation": "y"},
            "scope_protection": {"value": True, "quote": "x", "citation": "y"},
        }
        m = LicensureRequirements.model_validate(rec)
        assert m.regulatory_model.value == RegulatoryModel.LICENSE
        assert m.credential_type is None
        assert m.is_mandatory is None

    def test_new_fields_accept_orthogonal_population(self):
        rec = {
            "credential_type": {"value": "certification", "quote": "q", "citation": "c"},
            "is_mandatory": {"value": False, "quote": "voluntary cert", "citation": "c"},
            "title_protection": {"value": True, "quote": "x", "citation": "y"},
        }
        m = LicensureRequirements.model_validate(rec)
        assert m.credential_type.value == CredentialType.CERTIFICATION
        assert m.is_mandatory.value is False
        assert m.regulatory_model is None  # legacy not populated; that's fine


class TestRegulatoryAuthoritySchema:
    """Meeting Q2: structured representation of who regulates."""

    def test_authority_type_enum_values(self):
        from pipeline.extract.standard_model import AuthorityType
        expected = {"standalone_board", "shared_board", "division", "department", "joint", "other"}
        assert {a.value for a in AuthorityType} == expected

    def test_full_authority_record_validates(self):
        from pipeline.extract.standard_model import RegulatoryAuthority
        rec = {
            "name": {"value": "State Board of Podiatry", "quote": "q", "citation": "c"},
            "type": {"value": "standalone_board", "quote": "q", "citation": "c"},
            "umbrella_agency": {"value": "Department of Health", "quote": "q", "citation": "c"},
        }
        m = RegulatoryAuthority.model_validate(rec)
        assert m.name.value == "State Board of Podiatry"
        assert m.type.value == "standalone_board"
        assert m.umbrella_agency.value == "Department of Health"

    def test_standalone_board_with_no_umbrella(self):
        from pipeline.extract.standard_model import RegulatoryAuthority
        rec = {
            "name": {"value": "State Board of Public Accountancy", "quote": "q", "citation": "c"},
            "type": {"value": "standalone_board", "quote": "q", "citation": "c"},
            # umbrella_agency omitted → null
        }
        m = RegulatoryAuthority.model_validate(rec)
        assert m.umbrella_agency is None

    def test_invalid_authority_type_rejected(self):
        from pipeline.extract.standard_model import AuthorityTypeEvidence
        with pytest.raises(ValidationError):
            AuthorityTypeEvidence(value="invented_type", quote="q", citation="c")

    def test_licensure_accepts_authority_alongside_legacy_issuing_authority(self):
        """Both must coexist for back-compat."""
        rec = {
            "issuing_authority": {"value": "State Board of Podiatry", "quote": "q", "citation": "c"},
            "regulatory_authority": {
                "name": {"value": "State Board of Podiatry", "quote": "q", "citation": "c"},
                "type": {"value": "standalone_board", "quote": "q", "citation": "c"},
            },
        }
        m = LicensureRequirements.model_validate(rec)
        assert m.issuing_authority.value == "State Board of Podiatry"
        assert m.regulatory_authority.type.value == "standalone_board"
        assert m.regulatory_authority.umbrella_agency is None

    def test_legacy_records_still_work_without_authority(self):
        """Existing extracted records have no regulatory_authority field."""
        rec = {"issuing_authority": {"value": "State Board of Podiatry", "quote": "q", "citation": "c"}}
        m = LicensureRequirements.model_validate(rec)
        assert m.issuing_authority.value == "State Board of Podiatry"
        assert m.regulatory_authority is None
