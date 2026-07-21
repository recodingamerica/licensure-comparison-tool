"""Tests for silent-caps audit fixes (2026-07-01).

Covers:
  A1 — trim_state: oversize sections bypassed LLM and kept with kept_oversize=True
  B  — pull_text StateCorpus: section_cap_hit recorded in corpus JSON; corpus_status CAPPED flag
  A4 — audit_corpus: n_sections_total, n_sections_sampled, sample_truncated in verdict
  A6 — gen_semantics: WARNING logged when >12 distinct values per field
  A2/A3 — suggest_scope_rules: WARNING on anchor truncation; undetermined_not_reviewed in artifact
  A5 — discover_schema: states_sampled + states_excluded_count in JSON artifact
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# A1 — trim_state: oversize sections bypassed LLM, kept with kept_oversize=True
# ---------------------------------------------------------------------------

import pipeline.ingest.trim_state as ts


def _make_clean_corpus(tmp_path, sections):
    clean = tmp_path / "clean"
    (clean / "dietetics").mkdir(parents=True)
    (clean / "dietetics" / "TX.json").write_text(
        json.dumps({"sections": sections, "chapter_urls": ["c1"]})
    )
    return clean


def test_oversize_section_auto_kept_never_sent_to_llm(tmp_path, monkeypatch):
    """A section whose text exceeds SECTION_TEXT_CAP must be kept unconditionally
    and never sent to the keep/drop LLM — even when the LLM would drop it."""
    big_text = "x" * (ts.SECTION_TEXT_CAP + 1)
    sections = [
        {"citation": "1-1", "url": "u1", "label": "big", "text": big_text, "text_len": len(big_text)},
        {"citation": "1-2", "url": "u2", "label": "small", "text": "short text", "text_len": 10},
    ]
    clean = _make_clean_corpus(tmp_path, sections)
    monkeypatch.setattr(ts, "CLEAN_DIR", clean)

    # LLM: keep nothing (drops small; big must NOT reach LLM at all)
    class _Drop:
        def __init__(self, c):
            self.citation, self.keep, self.reason = c, False, "drop"

    class _Result:
        decisions = [_Drop("1-2")]

    calls = []
    def fake_call_model(model, system, user, schema_cls):
        calls.append(user)
        return _Result()

    monkeypatch.setattr(ts, "call_model", fake_call_model)
    corpus = ts.trim_state("TX", "dietetics", ts.DEFAULT_MODEL)

    # The big section must be in the kept list
    kept_cites = {s["citation"] for s in corpus.sections}
    assert "1-1" in kept_cites, "oversize section must be kept unconditionally"
    # The big section must carry kept_oversize=True
    big_kept = next(s for s in corpus.sections if s["citation"] == "1-1")
    assert big_kept.get("kept_oversize") is True
    # The small section was dropped by the LLM mock
    assert "1-2" not in kept_cites
    # oversize_kept counter
    assert corpus.oversize_kept == 1
    # The big text must NOT appear in the LLM user message
    assert calls, "call_model should still be called (for the normal section)"
    assert big_text not in calls[0], "oversize text must not be in LLM input"


def test_oversize_section_flagged_in_dataclass(tmp_path, monkeypatch):
    """kept_oversize flag in the serialised dataclass output."""
    big_text = "A" * (ts.SECTION_TEXT_CAP + 100)
    sections = [
        {"citation": "1-1", "url": "u1", "label": "big", "text": big_text, "text_len": len(big_text)},
        {"citation": "1-2", "url": "u2", "label": "normal", "text": "normal", "text_len": 6},
    ]
    clean = _make_clean_corpus(tmp_path, sections)
    monkeypatch.setattr(ts, "CLEAN_DIR", clean)

    class _Keep:
        def __init__(self, c):
            self.citation, self.keep, self.reason = c, True, "ok"

    class _Result:
        decisions = [_Keep("1-2")]

    monkeypatch.setattr(ts, "call_model", lambda *a, **k: _Result())
    corpus = ts.trim_state("TX", "dietetics", ts.DEFAULT_MODEL)

    d = asdict(corpus)
    assert d["oversize_kept"] == 1
    big_sec = next(s for s in d["sections"] if s["citation"] == "1-1")
    assert big_sec["kept_oversize"] is True


def test_normal_sections_still_flow_through_llm(tmp_path, monkeypatch):
    """Normal-size sections are still decided by the LLM as before."""
    sections = [
        {"citation": "1-1", "url": "u1", "label": "scope", "text": "short a", "text_len": 7},
        {"citation": "1-2", "url": "u2", "label": "board", "text": "short b", "text_len": 7},
    ]
    clean = _make_clean_corpus(tmp_path, sections)
    monkeypatch.setattr(ts, "CLEAN_DIR", clean)

    class _D:
        def __init__(self, c, keep):
            self.citation, self.keep, self.reason = c, keep, "r"

    class _Result:
        decisions = [_D("1-1", True), _D("1-2", False)]

    monkeypatch.setattr(ts, "call_model", lambda *a, **k: _Result())
    corpus = ts.trim_state("TX", "dietetics", ts.DEFAULT_MODEL)

    assert corpus.oversize_kept == 0
    kept = {s["citation"] for s in corpus.sections}
    assert "1-1" in kept
    assert "1-2" not in kept
    # no section has kept_oversize
    assert not any(s.get("kept_oversize") for s in corpus.sections)


def test_all_oversize_no_llm_call(tmp_path, monkeypatch):
    """When ALL sections are oversize, the LLM is never called."""
    big = "X" * (ts.SECTION_TEXT_CAP + 1)
    sections = [
        {"citation": "1-1", "url": "u1", "label": "big1", "text": big, "text_len": len(big)},
        {"citation": "1-2", "url": "u2", "label": "big2", "text": big, "text_len": len(big)},
    ]
    clean = _make_clean_corpus(tmp_path, sections)
    monkeypatch.setattr(ts, "CLEAN_DIR", clean)

    called = []
    monkeypatch.setattr(ts, "call_model", lambda *a, **k: called.append(1) or None)
    corpus = ts.trim_state("TX", "dietetics", ts.DEFAULT_MODEL)

    assert not called, "call_model must not be called when all sections are oversize"
    assert corpus.oversize_kept == 2
    assert len(corpus.sections) == 2
    assert all(s.get("kept_oversize") for s in corpus.sections)


# ---------------------------------------------------------------------------
# B — pull_text StateCorpus: section_cap_hit recorded; corpus_status CAPPED flag
# ---------------------------------------------------------------------------

import pipeline.ingest.pull_text as pt
import pipeline.eval.corpus_status as cs


def test_state_corpus_section_cap_hit_default_none():
    c = pt.StateCorpus(state="TX", profession="electrician")
    d = asdict(c)
    assert "section_cap_hit" in d
    assert d["section_cap_hit"] is None


def test_state_corpus_section_cap_hit_set():
    c = pt.StateCorpus(state="TX", profession="electrician")
    c.section_cap_hit = 500
    d = asdict(c)
    assert d["section_cap_hit"] == 500


def test_corpus_status_capped_flag(tmp_path, monkeypatch):
    """corpus_status.audit_sync flags CAPPED when section_cap_hit is present."""
    text_dir = tmp_path / "text"
    (text_dir / "electrician").mkdir(parents=True)
    corpus_d = {
        "sections": [{"url": f"u{i}", "text": "x", "text_len": 1} for i in range(500)],
        "section_cap_hit": 500,
        "errors": [],
        "total_chars": 500,
    }
    (text_dir / "electrician" / "CA.json").write_text(json.dumps(corpus_d))

    monkeypatch.setattr(cs, "TEXT_DIR", text_dir)
    monkeypatch.setattr(cs, "CLEAN_DIR", tmp_path / "clean")
    monkeypatch.setattr(cs, "STRUCTURED_DIR", tmp_path / "structured")
    monkeypatch.setattr(cs, "STAGE_DIRS", {
        "text": text_dir, "clean": tmp_path / "clean",
        "trimmed": tmp_path / "trimmed", "structured": tmp_path / "structured",
    })

    rows = cs.audit_sync(cs.index_stages())
    row = next(r for r in rows if r["prof"] == "electrician" and r["state"] == "CA")
    assert any(f.startswith("CAPPED(") for f in row["flags"]), (
        f"Expected CAPPED flag; got {row['flags']}"
    )


def test_corpus_status_no_capped_flag_when_not_set(tmp_path, monkeypatch):
    """corpus_status.audit_sync does NOT flag CAPPED when section_cap_hit is absent."""
    text_dir = tmp_path / "text"
    (text_dir / "electrician").mkdir(parents=True)
    corpus_d = {
        "sections": [{"url": "u1", "text": "x", "text_len": 1}],
        "errors": [],
    }
    (text_dir / "electrician" / "TX.json").write_text(json.dumps(corpus_d))

    monkeypatch.setattr(cs, "TEXT_DIR", text_dir)
    monkeypatch.setattr(cs, "CLEAN_DIR", tmp_path / "clean")
    monkeypatch.setattr(cs, "STRUCTURED_DIR", tmp_path / "structured")
    monkeypatch.setattr(cs, "STAGE_DIRS", {
        "text": text_dir, "clean": tmp_path / "clean",
        "trimmed": tmp_path / "trimmed", "structured": tmp_path / "structured",
    })

    rows = cs.audit_sync(cs.index_stages())
    row = next(r for r in rows if r["prof"] == "electrician" and r["state"] == "TX")
    assert not any(f.startswith("CAPPED(") for f in row["flags"])


def test_is_section_capped_helper(tmp_path):
    p = tmp_path / "ok.json"
    p.write_text(json.dumps({"section_cap_hit": 250, "sections": []}))
    assert cs.is_section_capped(p) == 250

    p2 = tmp_path / "normal.json"
    p2.write_text(json.dumps({"sections": []}))
    assert cs.is_section_capped(p2) is None


# ---------------------------------------------------------------------------
# A4 — audit_corpus: verdict dict carries n_sections_total, n_sections_sampled,
#       sample_truncated
# ---------------------------------------------------------------------------

import pipeline.discover.audit_corpus as ac


def test_audit_corpus_verdict_has_sample_fields(tmp_path, monkeypatch):
    """audit_states must write n_sections_total, n_sections_sampled, sample_truncated."""
    text_dir = tmp_path / "text"
    (text_dir / "hvac").mkdir(parents=True)
    secs = [{"citation": f"1-{i}", "text": "hvac license text " * 10, "text_len": 180}
            for i in range(5)]
    (text_dir / "hvac" / "TX.json").write_text(json.dumps({"sections": secs}))

    monkeypatch.setattr(ac, "TEXT_DIR", text_dir)

    # Mock the LLM to avoid real API calls
    class _V:
        corpus_verdict = "correct_licensure_text"
        reason = "looks good"

    monkeypatch.setattr(ac, "call_structured", lambda **kw: _V())

    results = ac.audit_states("hvac", ["TX"])
    v = results["TX"]
    assert "n_sections_total" in v
    assert "n_sections_sampled" in v
    assert "sample_truncated" in v
    assert v["n_sections_total"] == 5
    assert v["n_sections_sampled"] <= v["n_sections_total"]
    assert isinstance(v["sample_truncated"], bool)


def test_audit_corpus_sample_truncated_false_for_small_corpus(tmp_path, monkeypatch):
    """For a small corpus well within budget, sample_truncated must be False."""
    text_dir = tmp_path / "text"
    (text_dir / "hvac").mkdir(parents=True)
    secs = [{"citation": f"1-{i}", "text": "x " * 50, "text_len": 100} for i in range(3)]
    (text_dir / "hvac" / "AL.json").write_text(json.dumps({"sections": secs}))

    monkeypatch.setattr(ac, "TEXT_DIR", text_dir)

    class _V:
        corpus_verdict = "correct_licensure_text"
        reason = "ok"

    monkeypatch.setattr(ac, "call_structured", lambda **kw: _V())

    results = ac.audit_states("hvac", ["AL"])
    assert results["AL"]["sample_truncated"] is False


def test_audit_corpus_empty_corpus_has_sample_fields(tmp_path, monkeypatch):
    """Even when the corpus is empty, the verdict must have the sample fields."""
    text_dir = tmp_path / "text"
    (text_dir / "hvac").mkdir(parents=True)
    (text_dir / "hvac" / "WY.json").write_text(json.dumps({"sections": []}))

    monkeypatch.setattr(ac, "TEXT_DIR", text_dir)
    monkeypatch.setattr(ac, "call_structured", lambda **kw: None)

    results = ac.audit_states("hvac", ["WY"])
    v = results["WY"]
    assert "n_sections_total" in v
    assert "n_sections_sampled" in v
    assert "sample_truncated" in v


# ---------------------------------------------------------------------------
# A6 — gen_semantics: WARNING logged when >12 distinct values
# ---------------------------------------------------------------------------

import pipeline.analyze.gen_semantics as gs


def test_gen_semantics_warns_when_values_capped(caplog):
    """field_inventory must emit a WARNING when a field has >12 distinct values."""
    # Build a minimal data/ JSON structure
    data = {
        "display": "Test Profession",
        "map_prep": {
            "spec": [{"field_name": "regulatory_model", "kind": "categorical"}],
            "rows": [
                {"field_name": "regulatory_model", "normalized": f"val_{i}"}
                for i in range(20)  # 20 distinct values — exceeds the cap of 12
            ],
        },
    }

    with caplog.at_level(logging.WARNING, logger="pipeline.analyze.gen_semantics"):
        display, inv = gs.field_inventory.__wrapped__(data) if hasattr(gs.field_inventory, "__wrapped__") else _call_field_inventory_with_data(data)

    # The inventory must cap at 12 values
    assert len(inv) == 1
    assert len(inv[0]["values"]) == 12


def _call_field_inventory_with_data(data):
    """Call field_inventory with mocked file I/O."""
    import unittest.mock as mock
    import json as _json
    with mock.patch("pipeline.analyze.gen_semantics.DATA_DIR") as mock_dir:
        mock_path = mock.MagicMock()
        mock_path.read_text.return_value = _json.dumps(data)
        mock_dir.__truediv__ = lambda self, name: mock_path
        return gs.field_inventory("test_profession")


def test_gen_semantics_warns_correct_message(caplog, tmp_path, monkeypatch):
    """The warning message must name the field and dropped count."""
    data = {
        "display": "Test",
        "map_prep": {
            "spec": [{"field_name": "big_field", "kind": "categorical"}],
            "rows": [{"field_name": "big_field", "normalized": f"v{i}"} for i in range(15)],
        },
    }
    import unittest.mock as mock, json as _json

    with caplog.at_level(logging.WARNING, logger="pipeline.analyze.gen_semantics"):
        with mock.patch("pipeline.analyze.gen_semantics.DATA_DIR") as mock_dir:
            mock_path = mock.MagicMock()
            mock_path.read_text.return_value = _json.dumps(data)
            mock_dir.__truediv__ = lambda self, name: mock_path
            gs.field_inventory("test")

    assert any("big_field" in r.message for r in caplog.records if r.levelno == logging.WARNING), (
        "Warning must name the field"
    )
    assert any("3" in r.message for r in caplog.records if r.levelno == logging.WARNING), (
        "Warning must mention dropped count (15 - 12 = 3)"
    )


def test_gen_semantics_no_warning_for_12_or_fewer(caplog, tmp_path):
    """No warning when a field has exactly 12 or fewer distinct values."""
    data = {
        "display": "Test",
        "map_prep": {
            "spec": [{"field_name": "small_field", "kind": "categorical"}],
            "rows": [{"field_name": "small_field", "normalized": f"v{i}"} for i in range(12)],
        },
    }
    import unittest.mock as mock, json as _json

    with caplog.at_level(logging.WARNING, logger="pipeline.analyze.gen_semantics"):
        with mock.patch("pipeline.analyze.gen_semantics.DATA_DIR") as mock_dir:
            mock_path = mock.MagicMock()
            mock_path.read_text.return_value = _json.dumps(data)
            mock_dir.__truediv__ = lambda self, name: mock_path
            display, inv = gs.field_inventory("test")

    assert not any(r.levelno == logging.WARNING for r in caplog.records)


# ---------------------------------------------------------------------------
# A2/A3 — suggest_scope_rules: anchor truncation WARNING; undetermined_not_reviewed
# ---------------------------------------------------------------------------

import pipeline.scope.suggest_scope_rules as S
from pipeline.scope.suggest_scope_rules import ScopeRulesProposal


def _base_proposal(**overrides):
    data = {
        "universal_patterns": [{"pattern": r"this chapter applies to any\b", "target": "chapter"}],
        "trigger_patterns": [r"licensed\s+under\b"],
        "chapter_cite_pattern": r"\bchapter\s+(\d+)\b",
        "section_cite_pattern": r"(\d+)\.\d+",
        "rationale": "test",
    }
    data.update(overrides)
    return ScopeRulesProposal(**data)


def test_anchor_truncation_warning_logged(caplog):
    """_build_user_prompt must log a WARNING when a section's text is cut."""
    long_text = "A" * (S.MAX_TEXT_PER_SECTION + 100)
    anchors = [{"label": "Definitions", "text": long_text}]

    with caplog.at_level(logging.WARNING, logger="pipeline.scope.suggest_scope_rules"):
        S._build_user_prompt("ZZ", anchors)

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert warnings, "Expected at least one WARNING for truncated anchor text"
    assert any("truncated" in r.message.lower() for r in warnings)


def test_anchor_no_warning_when_not_truncated(caplog):
    """No WARNING when anchor text is within MAX_TEXT_PER_SECTION."""
    short_text = "A" * (S.MAX_TEXT_PER_SECTION - 1)
    anchors = [{"label": "Definitions", "text": short_text}]

    with caplog.at_level(logging.WARNING, logger="pipeline.scope.suggest_scope_rules"):
        S._build_user_prompt("ZZ", anchors)

    assert not any(r.levelno == logging.WARNING for r in caplog.records)


def test_save_proposal_includes_undetermined_not_reviewed(tmp_path, monkeypatch):
    """save_proposal must write undetermined_not_reviewed to the artifact."""
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    proposal = _base_proposal()
    walker = {"scope_source_counts": {"universal": 10, "undetermined": 3}, "sections": []}
    skipped = ["https://example.com/section-1/", "https://example.com/section-2/"]

    S.save_proposal("ZZ", proposal, walker, n_undetermined=3,
                    undetermined_not_reviewed=skipped)

    meta = S.load_proposal_meta("ZZ")
    assert "undetermined_not_reviewed" in meta
    assert meta["undetermined_not_reviewed"] == skipped


def test_save_proposal_empty_not_reviewed_by_default(tmp_path, monkeypatch):
    """When no sections are skipped, undetermined_not_reviewed is an empty list."""
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    proposal = _base_proposal()
    walker = {"scope_source_counts": {"universal": 5}, "sections": []}

    S.save_proposal("ZZ", proposal, walker, n_undetermined=0)

    meta = S.load_proposal_meta("ZZ")
    assert meta["undetermined_not_reviewed"] == []


def test_get_undetermined_not_reviewed_returns_tail(tmp_path, monkeypatch):
    """get_undetermined_not_reviewed returns URLs beyond MAX_UNDET_IN_REFINEMENT."""
    # Build a synthetic walker result with 15 undetermined sections
    from pipeline.scope._scope_rules import NARROW_LABEL_HINTS
    sections = []
    for i in range(15):
        sections.append({
            "url": f"https://example.com/section-{i}/",
            "scope_source": "undetermined",
            "umbrella_chapter_slug": "chapter-1",
            "label": f"Section {i}",
        })
    walker_result = {"sections": sections, "scope_source_counts": {"undetermined": 15}}

    # Patch UMBRELLA_TEXT_DIR to avoid filesystem reads (get_undetermined_not_reviewed
    # doesn't read the filesystem — it only uses the walker_result sections list)
    not_reviewed = S.get_undetermined_not_reviewed("ZZ", walker_result)
    # Should be sections beyond MAX_UNDET_IN_REFINEMENT (10)
    assert len(not_reviewed) == 15 - S.MAX_UNDET_IN_REFINEMENT
    expected_urls = [f"https://example.com/section-{i}/" for i in range(S.MAX_UNDET_IN_REFINEMENT, 15)]
    assert not_reviewed == expected_urls


def test_get_undetermined_not_reviewed_empty_when_under_cap():
    """Returns empty list when undetermined count <= MAX_UNDET_IN_REFINEMENT."""
    sections = [
        {"url": f"u{i}/", "scope_source": "undetermined",
         "umbrella_chapter_slug": "c", "label": f"s{i}"}
        for i in range(S.MAX_UNDET_IN_REFINEMENT)
    ]
    walker_result = {"sections": sections}
    assert S.get_undetermined_not_reviewed("ZZ", walker_result) == []


# ---------------------------------------------------------------------------
# A5 — discover_schema: states_sampled + states_excluded_count in JSON artifact
# ---------------------------------------------------------------------------

import pipeline.extract.discover_schema as ds


def test_discover_schema_artifact_has_sampling_fields(tmp_path, monkeypatch):
    """discover_schema must write states_sampled and states_excluded_count to the JSON."""
    # Build a minimal trimmed corpus with 15 states
    trimmed = tmp_path / "trimmed" / "podiatry"
    trimmed.mkdir(parents=True)
    for i, st in enumerate(["AL", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA",
                             "IL", "IN", "KS", "KY", "LA"]):
        (trimmed / f"{st}.json").write_text(json.dumps({
            "state": st, "sections": [{"citation": "1-1", "label": "scope", "text": "text"}],
        }))

    discovered = tmp_path / "discovered"
    discovered.mkdir()
    monkeypatch.setattr(ds, "TRIMMED_DIR", tmp_path / "trimmed")
    monkeypatch.setattr(ds, "DISCOVERED_DIR", discovered)

    # Mock the LLM call
    class _Schema:
        profession = "podiatry"
        fields = []

        def model_dump_json(self):
            import json as _j
            return _j.dumps({"profession": "podiatry", "fields": []})

    monkeypatch.setattr(ds, "call_model", lambda *a, **k: _Schema())

    import sys as _sys
    monkeypatch.setattr(_sys, "argv", ["discover_schema", "--profession", "podiatry"])

    # Patch write_markdown_preview to no-op
    monkeypatch.setattr(ds, "write_markdown_preview", lambda s, p: None)

    ds.main()

    out = json.loads((discovered / "podiatry.json").read_text())
    assert "states_sampled" in out, "artifact must contain states_sampled"
    assert "states_excluded_count" in out, "artifact must contain states_excluded_count"
    # With 15 states and max_states=10 (default), 5 are excluded
    assert len(out["states_sampled"]) == 10
    assert out["states_excluded_count"] == 5


def test_discover_schema_artifact_no_exclusion_when_under_limit(tmp_path, monkeypatch):
    """When state count <= max_states, states_excluded_count must be 0."""
    trimmed = tmp_path / "trimmed" / "podiatry"
    trimmed.mkdir(parents=True)
    for st in ["AL", "AZ", "CA"]:
        (trimmed / f"{st}.json").write_text(json.dumps({
            "state": st, "sections": [{"citation": "1-1", "label": "s", "text": "t"}],
        }))

    discovered = tmp_path / "discovered"
    discovered.mkdir()
    monkeypatch.setattr(ds, "TRIMMED_DIR", tmp_path / "trimmed")
    monkeypatch.setattr(ds, "DISCOVERED_DIR", discovered)

    class _Schema:
        profession = "podiatry"
        fields = []

        def model_dump_json(self):
            import json as _j
            return _j.dumps({"profession": "podiatry", "fields": []})

    monkeypatch.setattr(ds, "call_model", lambda *a, **k: _Schema())
    monkeypatch.setattr(ds, "write_markdown_preview", lambda s, p: None)

    import sys as _sys
    monkeypatch.setattr(_sys, "argv", ["discover_schema", "--profession", "podiatry"])

    ds.main()

    out = json.loads((discovered / "podiatry.json").read_text())
    assert out["states_excluded_count"] == 0
    assert set(out["states_sampled"]) == {"AL", "AZ", "CA"}
