"""Tests for the shared umbrella scope_source semantics."""

from __future__ import annotations

import pytest

from pipeline.scope.scope_sources import (
    CLASSIFIED_SOURCES,
    METHOD_LLM,
    METHOD_WALKER,
    is_classified,
    is_enumeration,
    is_universal,
    overlay_llm_decisions,
    professions_for,
)


@pytest.mark.parametrize("src,uni,enum,classified", [
    ("universal", True, False, True),
    ("anchor_universal", True, False, True),
    ("anchor_enumeration", False, True, True),
    ("inherited_enumeration", False, True, True),
    ("undetermined", False, False, False),
    (None, False, False, False),
    ("", False, False, False),
])
def test_predicates(src, uni, enum, classified):
    assert is_universal(src) is uni
    assert is_enumeration(src) is enum
    assert is_classified(src) is classified


def test_classified_sources_is_union():
    assert set(CLASSIFIED_SOURCES) == {
        "universal", "anchor_universal", "anchor_enumeration", "inherited_enumeration",
    }


def test_professions_for_universal_returns_all():
    assert professions_for("universal", None, ["a", "b", "c"]) == ["a", "b", "c"]
    # all_professions may be a dict-keys view (db/load passes profession_ids.keys())
    assert professions_for("anchor_universal", ["ignored"], {"x": 1, "y": 2}.keys()) == ["x", "y"]


def test_professions_for_enumeration_returns_list():
    assert professions_for("inherited_enumeration", ["podiatry", "nursing"], ["a"]) == ["podiatry", "nursing"]
    assert professions_for("anchor_enumeration", None, ["a"]) == []  # empty enumeration, not None


def test_professions_for_undetermined_returns_none():
    # None (not []) so callers can distinguish "skip" from "empty enumeration".
    assert professions_for("undetermined", ["x"], ["a", "b"]) is None
    assert professions_for(None, None, ["a"]) is None


def test_overlay_fills_undetermined_with_llm():
    sections = [
        {"url": "u1", "scope_source": "undetermined", "applies_to_professions": None},
        {"url": "u2", "scope_source": "universal", "applies_to_professions": None},
    ]
    llm = {"u1": {"scope_source": "inherited_enumeration",
                  "applies_to_professions": ["nursing"], "scope_evidence": "ev"}}
    overlay_llm_decisions(sections, llm)
    assert sections[0]["scope_source"] == "inherited_enumeration"
    assert sections[0]["applies_to_professions"] == ["nursing"]
    assert sections[0]["scope_method"] == METHOD_LLM
    # walker-classified section untouched, tagged walker
    assert sections[1]["scope_source"] == "universal"
    assert sections[1]["scope_method"] == METHOD_WALKER


def test_overlay_does_not_touch_already_classified_even_if_llm_present():
    sections = [{"url": "u1", "scope_source": "universal", "applies_to_professions": None}]
    llm = {"u1": {"scope_source": "inherited_enumeration", "applies_to_professions": ["x"]}}
    overlay_llm_decisions(sections, llm)
    assert sections[0]["scope_source"] == "universal"  # walker wins; only undetermined gets overlaid
    assert sections[0]["scope_method"] == METHOD_WALKER


def test_overlay_no_llm_marks_all_walker():
    sections = [{"url": "u1", "scope_source": "undetermined"}]
    overlay_llm_decisions(sections, {})
    assert sections[0]["scope_method"] == METHOD_WALKER
    assert sections[0]["scope_source"] == "undetermined"
