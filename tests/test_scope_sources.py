"""Tests for the shared umbrella scope_source semantics."""

from __future__ import annotations

import pytest

from pipeline.scope_sources import (
    CLASSIFIED_SOURCES,
    is_classified,
    is_enumeration,
    is_universal,
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
