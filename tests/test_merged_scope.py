"""Tests for the shared merged-scope loader (walker + Pass-3 LLM overlay)."""

from __future__ import annotations

import json

import pytest


@pytest.fixture
def fake_dirs(tmp_path, monkeypatch):
    import pipeline.merged_scope as ms  # top-level module the consumers import from
    sd = tmp_path / "scope"; sd.mkdir()
    ld = tmp_path / "scope_llm"; ld.mkdir()
    monkeypatch.setattr(ms, "UMBRELLA_SCOPE_DIR", sd)
    monkeypatch.setattr(ms, "UMBRELLA_SCOPE_LLM_DIR", ld)
    return sd, ld


def test_load_none_when_no_walker_output(fake_dirs):
    from pipeline.merged_scope import load_merged_scope
    assert load_merged_scope("ZZ") is None


def test_load_walker_only_marks_walker(fake_dirs):
    from pipeline.merged_scope import load_merged_scope
    sd, ld = fake_dirs
    (sd / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "scope_source": "universal"},
        {"url": "u2", "scope_source": "undetermined"},
    ]}))
    data = load_merged_scope("XX")
    methods = {s["url"]: s["scope_method"] for s in data["sections"]}
    assert methods == {"u1": "walker", "u2": "walker"}


def test_load_overlays_llm_onto_undetermined(fake_dirs):
    from pipeline.merged_scope import load_merged_scope, merged_scope_by_url
    sd, ld = fake_dirs
    (sd / "XX.json").write_text(json.dumps({"sections": [
        {"url": "u1", "scope_source": "undetermined", "applies_to_professions": None},
        {"url": "u2", "scope_source": "universal", "applies_to_professions": None},
    ]}))
    (ld / "XX.json").write_text(json.dumps({"decisions": [
        {"url": "u1", "scope_source": "inherited_enumeration",
         "applies_to_professions": ["nursing"], "scope_evidence": "ev"},
    ]}))
    by_url = merged_scope_by_url("XX")
    assert by_url["u1"]["scope_source"] == "inherited_enumeration"
    assert by_url["u1"]["applies_to_professions"] == ["nursing"]
    assert by_url["u1"]["scope_method"] == "llm"
    assert by_url["u2"]["scope_method"] == "walker"


def test_merged_scope_by_url_empty_when_missing(fake_dirs):
    from pipeline.merged_scope import merged_scope_by_url
    assert merged_scope_by_url("ZZ") == {}
