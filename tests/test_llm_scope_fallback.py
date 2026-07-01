"""Tests for Pass 3 (LLM scope fallback) — the pure logic only (no LLM calls):
decision→entry mapping, walker/LLM merge, and undetermined extraction.
"""

from __future__ import annotations

import json

import pytest

import pipeline.discover.llm_scope_fallback as P
from pipeline.discover.llm_scope_fallback import SectionDecision, _to_scope_entry


VALID = {"podiatry", "nursing", "medicine"}


def test_universal_is_not_an_allowed_decision():
    # Pass 3 must never assert universal — that's the walker's job. The schema
    # rejects it, so the model can't promote a section to all-professions.
    with pytest.raises(Exception):
        SectionDecision(url="u", scope="universal", evidence="x")


def test_decision_specific_with_valid_profs():
    e = _to_scope_entry(SectionDecision(url="u", scope="specific", professions=["podiatry", "nursing"], evidence="x"), VALID)
    assert e["scope_source"] == "inherited_enumeration"
    assert e["applies_to_professions"] == ["nursing", "podiatry"]


def test_decision_specific_filters_unknown_profs():
    e = _to_scope_entry(SectionDecision(url="u", scope="specific", professions=["nursing", "made_up"], evidence="x"), VALID)
    assert e["applies_to_professions"] == ["nursing"]


def test_decision_specific_with_no_valid_profs_becomes_undetermined():
    e = _to_scope_entry(SectionDecision(url="u", scope="specific", professions=["made_up"], evidence="x"), VALID)
    assert e["scope_source"] == "undetermined"
    assert e["applies_to_professions"] is None


def test_decision_undetermined():
    e = _to_scope_entry(SectionDecision(url="u", scope="undetermined", evidence=""), VALID)
    assert e["scope_source"] == "undetermined"


@pytest.fixture
def fake_dirs(tmp_path, monkeypatch):
    import pipeline.merged_scope as ms  # top-level module merge_scope() delegates to
    sd = tmp_path / "scope"; sd.mkdir()
    ld = tmp_path / "scope_llm"; ld.mkdir()
    td = tmp_path / "text"; td.mkdir()
    # undetermined_sections reads P's dirs; merge_scope delegates to merged_scope
    monkeypatch.setattr(P, "UMBRELLA_SCOPE_DIR", sd)
    monkeypatch.setattr(P, "UMBRELLA_SCOPE_LLM_DIR", ld)
    monkeypatch.setattr(P, "UMBRELLA_TEXT_DIR", td)
    monkeypatch.setattr(ms, "UMBRELLA_SCOPE_DIR", sd)
    monkeypatch.setattr(ms, "UMBRELLA_SCOPE_LLM_DIR", ld)
    return sd, ld, td


def test_undetermined_sections_joins_text(fake_dirs):
    sd, ld, td = fake_dirs
    (sd / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "label": "Defs", "umbrella_chapter_slug": "c1", "scope_source": "undetermined"},
        {"url": "u2", "label": "Other", "umbrella_chapter_slug": "c1", "scope_source": "universal"},
    ]}))
    (td / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "text": "the section text"}, {"url": "u2", "text": "other"},
    ]}))
    got = P.undetermined_sections("XX")
    assert len(got) == 1
    assert got[0]["url"] == "u1" and got[0]["text"] == "the section text"


def test_merge_overlays_llm_onto_undetermined(fake_dirs):
    sd, ld, td = fake_dirs
    (sd / "XX.json").write_text(json.dumps({"state": "XX", "sections": [
        {"url": "u1", "umbrella_chapter_slug": "c1", "scope_source": "undetermined", "applies_to_professions": None},
        {"url": "u2", "umbrella_chapter_slug": "c1", "scope_source": "universal", "applies_to_professions": None},
    ]}))
    (ld / "XX.json").write_text(json.dumps({"decisions": [
        {"url": "u1", "scope_source": "inherited_enumeration", "applies_to_professions": ["nursing"],
         "scope_evidence": "ev", "scope_method": "llm"},
    ]}))
    merged = P.merge_scope("XX")
    by_url = {s["url"]: s for s in merged["sections"]}
    # u1 was undetermined → overlaid with the LLM decision + provenance
    assert by_url["u1"]["scope_source"] == "inherited_enumeration"
    assert by_url["u1"]["applies_to_professions"] == ["nursing"]
    assert by_url["u1"]["scope_method"] == "llm"
    # u2 was walker-classified → untouched, provenance defaults to walker
    assert by_url["u2"]["scope_source"] == "universal"
    assert by_url["u2"]["scope_method"] == "walker"


def test_audit_flags_ungrounded_no_citation(fake_dirs, monkeypatch):
    sd, ld, td = fake_dirs
    # text: chapter c1 names "nursing" but never "podiatry"
    (td / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "umbrella_chapter_slug": "c1", "text": "the practice of nursing in this chapter"},
    ]}))
    # LLM enumerated podiatry (not in text) with NO citation in evidence -> flagged;
    # nursing (in text) -> not flagged.
    (ld / "XX.json").write_text(json.dumps({"decisions": [
        {"url": "u1", "scope_source": "inherited_enumeration",
         "applies_to_professions": ["nursing", "podiatry"], "scope_evidence": "registered nurses and others"},
    ]}))
    monkeypatch.setattr(P, "_profession_terms_by_id",
                        lambda: {"nursing": ["nursing", "nurse"], "podiatry": ["podiatry", "podiatric"]})
    cands = P.audit_enumerations("XX")
    assert len(cands) == 1
    assert cands[0]["ungrounded_professions"] == ["podiatry"]  # nursing grounded, podiatry not


def test_audit_skips_when_evidence_has_citation(fake_dirs, monkeypatch):
    sd, ld, td = fake_dirs
    (td / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "umbrella_chapter_slug": "c1", "text": "applies to chapter 474"},
    ]}))
    (ld / "XX.json").write_text(json.dumps({"decisions": [
        {"url": "u1", "scope_source": "inherited_enumeration",
         "applies_to_professions": ["veterinary"], "scope_evidence": "licensed under chapter 474"},
    ]}))
    monkeypatch.setattr(P, "_profession_terms_by_id", lambda: {"veterinary": ["veterinary", "veterinarian"]})
    # evidence cites "chapter 474" -> cite-based mapping, not flagged even though
    # 'veterinary' isn't in the text
    assert P.audit_enumerations("XX") == []


def test_merge_without_llm_file_marks_all_walker(fake_dirs):
    sd, ld, td = fake_dirs
    (sd / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "scope_source": "undetermined"},
    ]}))
    merged = P.merge_scope("XX")
    assert merged["sections"][0]["scope_method"] == "walker"
    assert merged["sections"][0]["scope_source"] == "undetermined"  # unchanged
