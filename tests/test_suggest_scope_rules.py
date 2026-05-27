"""Tests for ScopeRulesProposal validation in suggest_scope_rules.

The LLM returns the proposal as tool_use JSON, and it occasionally emits list
fields in shapes Pydantic rejects. These coercions normalize the common
malformations before validation, so a generation run doesn't crash on a
recoverable formatting quirk. Each test pins a real failure seen in the wild.
"""

from __future__ import annotations

import argparse

import pytest

import pipeline.discover.suggest_scope_rules as S
from pipeline.discover.suggest_scope_rules import ScopeRulesProposal


def _base(**overrides):
    data = {
        "universal_patterns": [{"pattern": r"this chapter applies to any\b", "target": "chapter"}],
        "trigger_patterns": [r"licensed\s+under\b"],
        "chapter_cite_pattern": r"\bchapter\s+(\d+)\b",
        "section_cite_pattern": r"(\d+)\.\d+",
        "rationale": "test",
    }
    data.update(overrides)
    return data


def test_normal_dict_form_validates():
    p = ScopeRulesProposal(**_base())
    assert p.universal_patterns[0].target == "chapter"
    assert p.trigger_patterns == [r"licensed\s+under\b"]


def test_trigger_patterns_as_json_string():
    # Seen on HI/NC: a list field arrives as a JSON-encoded string.
    p = ScopeRulesProposal(**_base(trigger_patterns=r'["licensed\\s+under\\b", "licensed\\s+to\\s+practice\\b"]'))
    assert p.trigger_patterns == [r"licensed\s+under\b", r"licensed\s+to\s+practice\b"]


def test_universal_patterns_as_pair_lists():
    # Seen on LA/OR/RI: entries arrive as [pattern, target] pairs (mimicking
    # the few-shot tuple notation) instead of {pattern, target} objects.
    p = ScopeRulesProposal(**_base(universal_patterns=[
        [r"each board\b[^.]*under this title", "title"],
        [r"any state board\b", "chapter"],
    ]))
    assert [u.target for u in p.universal_patterns] == ["title", "chapter"]
    assert p.universal_patterns[0].pattern == r"each board\b[^.]*under this title"


def test_universal_patterns_as_json_string_of_pairs():
    p = ScopeRulesProposal(**_base(universal_patterns='[["this title applies to any\\\\b", "title"]]'))
    assert p.universal_patterns[0].target == "title"


def test_invalid_regex_still_rejected():
    with pytest.raises(Exception):
        ScopeRulesProposal(**_base(chapter_cite_pattern=r"(unbalanced"))


# ---------------------------------------------------------------------------
# Proposal persistence: --apply must replay the validated proposal exactly
# ---------------------------------------------------------------------------

def test_save_load_proposal_round_trips(tmp_path, monkeypatch):
    import pipeline.discover.suggest_scope_rules as S
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)

    proposal = ScopeRulesProposal(**_base(
        universal_patterns=[{"pattern": r"this title applies to any\b", "target": "title"}],
        trigger_patterns=[r"licensed\s+under\b", r"licensed\s+to\s+practice\b"],
    ))
    walker_result = {"scope_source_counts": {"universal": 40, "undetermined": 3}}
    S.save_proposal("ZZ", proposal, walker_result)

    loaded = S.load_proposal("ZZ")
    assert loaded is not None
    # The rendered code must be byte-identical — that's the guarantee that
    # --apply writes the same rules the walker validated.
    assert S.render_rules_code("ZZ", loaded) == S.render_rules_code("ZZ", proposal)
    assert S.load_proposal_meta("ZZ")["scope_source_counts"] == {"universal": 40, "undetermined": 3}


def test_load_proposal_none_when_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    assert S.load_proposal("ZZ") is None
    assert S.load_proposal_meta("ZZ") == {}


# ---------------------------------------------------------------------------
# Status classification
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("walker_result,n_undet,expected", [
    (None, 0, S.STATUS_NO_INDEX),
    ({"scope_source_counts": {"undetermined": 5}}, 5, S.STATUS_ZERO),
    ({"scope_source_counts": {"universal": 10, "undetermined": 9}}, 8, S.STATUS_REVIEW),
    ({"scope_source_counts": {"universal": 10, "undetermined": 2}}, 2, S.STATUS_CLEAN),
])
def test_classify_status(walker_result, n_undet, expected):
    assert S.classify_status(walker_result, n_undet) == expected


# ---------------------------------------------------------------------------
# Target resolution (--state / --states / --all-unapplied)
# ---------------------------------------------------------------------------

def test_resolve_targets_single():
    ns = argparse.Namespace(state="ny", states=None, all_unapplied=False)
    assert S.resolve_targets(ns) == ["NY"]


def test_resolve_targets_list():
    ns = argparse.Namespace(state=None, states="ny, oh ,tx", all_unapplied=False)
    assert S.resolve_targets(ns) == ["NY", "OH", "TX"]


def test_resolve_targets_all_unapplied(monkeypatch):
    monkeypatch.setattr(S, "_states_with_umbrella_text", lambda: ["AK", "MO", "TX"])
    monkeypatch.setattr(S, "_applied_states", lambda: {"MO"})
    ns = argparse.Namespace(state=None, states=None, all_unapplied=True)
    assert S.resolve_targets(ns) == ["AK", "TX"]


# ---------------------------------------------------------------------------
# do_generate orchestration (LLM mocked) — reuse / generate / refine / error
# ---------------------------------------------------------------------------

def _walker(counts, sections=None):
    return {"scope_source_counts": counts, "sections": sections or []}


def test_do_generate_reuses_saved_without_llm(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    S.save_proposal("ZZ", ScopeRulesProposal(**_base()),
                    _walker({"universal": 5}, [{"umbrella_chapter_slug": "c", "scope_source": "universal"}]), 0)
    called = []
    monkeypatch.setattr(S, "call_llm", lambda *a, **k: called.append(1))
    r = S.do_generate("ZZ", regenerate=False)
    assert r.reused and r.status == S.STATUS_CLEAN
    assert not called  # no LLM call on reuse


def test_do_generate_generates_and_saves(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    monkeypatch.setattr(S, "load_anchor_sections", lambda st: [{"label": "Definitions", "text": "x"}])
    prop = ScopeRulesProposal(**_base())
    monkeypatch.setattr(S, "call_llm", lambda st, anchors, model=None: (prop, object()))
    monkeypatch.setattr(S, "run_walker_in_memory",
                        lambda st, p, *a, **k: _walker({"universal": 30, "undetermined": 2},
                                                       [{"umbrella_chapter_slug": "c", "scope_source": "universal"}]))
    monkeypatch.setattr(S, "get_undetermined_with_text", lambda st, wr: [{"x": 1}] * 2)  # < threshold
    r = S.do_generate("ZZ", regenerate=True)
    assert r.status == S.STATUS_CLEAN and r.classified == 30 and not r.reused
    assert (tmp_path / "ZZ.json").exists()


def test_do_generate_triggers_refinement(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    monkeypatch.setattr(S, "load_anchor_sections", lambda st: [{"label": "Definitions", "text": "x"}])
    prop = ScopeRulesProposal(**_base())
    monkeypatch.setattr(S, "call_llm", lambda st, anchors, model=None: (prop, object()))
    monkeypatch.setattr(S, "run_walker_in_memory",
                        lambda st, p, *a, **k: _walker({"universal": 10, "undetermined": 9},
                                                       [{"umbrella_chapter_slug": "c", "scope_source": "universal"}]))
    monkeypatch.setattr(S, "get_undetermined_with_text", lambda st, wr: [{"x": 1}] * 8)  # > threshold
    refined = []
    monkeypatch.setattr(S, "refine_llm",
                        lambda st, anchors, resp, undet, model=None: refined.append(1) or prop)
    r = S.do_generate("ZZ", regenerate=True)
    assert refined == [1]  # refinement fired
    assert r.status == S.STATUS_REVIEW


def test_do_generate_error_is_captured(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    monkeypatch.setattr(S, "load_anchor_sections", lambda st: [{"label": "x", "text": "y"}])
    def boom(*a, **k):
        raise RuntimeError("kaboom")
    monkeypatch.setattr(S, "call_llm", boom)
    r = S.do_generate("ZZ", regenerate=True)
    assert r.status == S.STATUS_ERROR and "kaboom" in r.error
