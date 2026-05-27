"""Tests for ScopeRulesProposal validation in suggest_scope_rules.

The LLM returns the proposal as tool_use JSON, and it occasionally emits list
fields in shapes Pydantic rejects. These coercions normalize the common
malformations before validation, so a generation run doesn't crash on a
recoverable formatting quirk. Each test pins a real failure seen in the wild.
"""

from __future__ import annotations

import pytest

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
    import pipeline.discover.suggest_scope_rules as S
    monkeypatch.setattr(S, "PROPOSALS_DIR", tmp_path)
    assert S.load_proposal("ZZ") is None
    assert S.load_proposal_meta("ZZ") == {}
