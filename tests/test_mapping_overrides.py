"""Tests for pipeline.discover._mapping_overrides and the match_state parent_chapter_url fix.

Covers:
  - apply_mapping_overrides: exclude drops a node; verbatim add appends a node;
    same-url-different-dict triggers a warning AND appends; dict-equal same-url is skipped.
  - write_mapping_overrides / add_override_entry / add_exclude_entry: deterministic
    YAML round-trip; idempotency.
  - match_state (match_profession): nodes with parent_chapter_url are skipped.
  - write_targets (match_sections): new behavior — YAML entries created, rebuilt index
    contains the node; dedup via base-index check.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from pipeline.discover._mapping_overrides import (
    apply_mapping_overrides,
    write_mapping_overrides,
    add_override_entry,
    add_exclude_entry,
)
from pipeline.discover.match_profession import match_state


# ---------------------------------------------------------------------------
# apply_mapping_overrides
# ---------------------------------------------------------------------------

class TestApplyMappingOverrides:
    BASE_NODE = {"label": "Ch 1 - Accountants", "url": "https://j.com/ch1/", "slug": "ch1"}
    OTHER_NODE = {"label": "Ch 2 - Misc", "url": "https://j.com/ch2/", "slug": "ch2"}

    def test_exclude_drops_node(self):
        overrides = {"public_accountancy": {"TX": {"exclude": ["https://j.com/ch1/"]}}}
        result = apply_mapping_overrides(
            "public_accountancy", "TX", [self.BASE_NODE, self.OTHER_NODE], overrides
        )
        urls = [n["url"] for n in result]
        assert "https://j.com/ch1/" not in urls
        assert "https://j.com/ch2/" in urls

    def test_add_appends_node_verbatim(self):
        new_node = {"label": "Ch 3 - CPA", "url": "https://j.com/ch3/", "slug": "ch3",
                    "via": "missed_match_recall"}
        overrides = {"public_accountancy": {"TX": {"add": [new_node]}}}
        result = apply_mapping_overrides("public_accountancy", "TX", [self.BASE_NODE], overrides)
        assert len(result) == 2
        assert result[-1] == new_node

    def test_dict_equal_same_url_is_skipped(self):
        existing = {"label": "Ch 1", "url": "https://j.com/ch1/", "slug": "ch1",
                    "via": "missed_match_recall"}
        overrides = {"prof": {"AK": {"add": [dict(existing)]}}}
        result = apply_mapping_overrides("prof", "AK", [existing], overrides)
        assert len(result) == 1  # not duplicated

    def test_same_url_different_dict_warns_and_appends(self, caplog):
        import logging
        existing = {"label": "Ch 1", "url": "https://j.com/ch1/", "slug": "ch1"}
        add_node = {"label": "Ch 1 RENAMED", "url": "https://j.com/ch1/", "slug": "ch1",
                    "via": "missed_match_recall"}
        overrides = {"prof": {"AK": {"add": [add_node]}}}
        with caplog.at_level(logging.WARNING, logger="mapping_overrides"):
            result = apply_mapping_overrides("prof", "AK", [existing], overrides)
        assert len(result) == 2
        assert any("different dict" in r.message for r in caplog.records)

    def test_no_overrides_returns_unchanged(self):
        result = apply_mapping_overrides("prof", "AK", [self.BASE_NODE], {})
        assert result == [self.BASE_NODE]

    def test_missing_profession_state_returns_unchanged(self):
        overrides = {"other_prof": {"AK": {"exclude": ["https://j.com/ch1/"]}}}
        result = apply_mapping_overrides("prof", "AK", [self.BASE_NODE], overrides)
        assert result == [self.BASE_NODE]


# ---------------------------------------------------------------------------
# write_mapping_overrides / add_override_entry / add_exclude_entry (YAML I/O)
# ---------------------------------------------------------------------------

class TestYamlRoundTrip:
    def test_deterministic_sort_professions_and_states(self, tmp_path):
        overrides_path = tmp_path / "mapping_overrides.yaml"
        data = {
            "zzz_prof": {"TX": {"add": [{"url": "u1", "label": "L1"}]}},
            "aaa_prof": {"NY": {"add": [{"url": "u2", "label": "L2"}]}},
        }
        with patch("pipeline.discover._mapping_overrides.OVERRIDES_PATH", overrides_path):
            write_mapping_overrides(data)
        text = overrides_path.read_text()
        # professions sorted alphabetically
        assert text.index("aaa_prof") < text.index("zzz_prof")

    def test_exclude_before_add_within_state(self, tmp_path):
        overrides_path = tmp_path / "mapping_overrides.yaml"
        data = {"prof": {"TX": {
            "add": [{"url": "u1", "label": "L"}],
            "exclude": ["https://j.com/old/"],
        }}}
        with patch("pipeline.discover._mapping_overrides.OVERRIDES_PATH", overrides_path):
            write_mapping_overrides(data)
        text = overrides_path.read_text()
        assert text.index("exclude") < text.index("add")

    def test_empty_entries_dropped(self, tmp_path):
        overrides_path = tmp_path / "mapping_overrides.yaml"
        data = {"prof": {"TX": {}, "AK": {"add": []}}}
        with patch("pipeline.discover._mapping_overrides.OVERRIDES_PATH", overrides_path):
            write_mapping_overrides(data)
        loaded = yaml.safe_load(overrides_path.read_text())
        assert loaded is None or "prof" not in (loaded or {})


class TestAddOverrideEntry:
    def test_adds_new_node(self, tmp_path):
        overrides_path = tmp_path / "mapping_overrides.yaml"
        node = {"url": "https://j.com/ch1/", "label": "Ch 1", "slug": "ch1",
                "via": "missed_match_recall"}
        with patch("pipeline.discover._mapping_overrides.OVERRIDES_PATH", overrides_path):
            add_override_entry("prof", "TX", node)
            data = yaml.safe_load(overrides_path.read_text())
        assert data["prof"]["TX"]["add"][0] == node

    def test_idempotent_same_node_twice(self, tmp_path):
        overrides_path = tmp_path / "mapping_overrides.yaml"
        node = {"url": "https://j.com/ch1/", "label": "Ch 1", "slug": "ch1",
                "via": "missed_match_recall"}
        with patch("pipeline.discover._mapping_overrides.OVERRIDES_PATH", overrides_path):
            add_override_entry("prof", "TX", node)
            add_override_entry("prof", "TX", node)
            data = yaml.safe_load(overrides_path.read_text())
        assert len(data["prof"]["TX"]["add"]) == 1  # not duplicated


class TestAddExcludeEntry:
    def test_adds_exclude_url(self, tmp_path):
        overrides_path = tmp_path / "mapping_overrides.yaml"
        with patch("pipeline.discover._mapping_overrides.OVERRIDES_PATH", overrides_path):
            add_exclude_entry("prof", "TX", "https://j.com/old/")
            data = yaml.safe_load(overrides_path.read_text())
        assert "https://j.com/old/" in data["prof"]["TX"]["exclude"]

    def test_idempotent_same_url_twice(self, tmp_path):
        overrides_path = tmp_path / "mapping_overrides.yaml"
        with patch("pipeline.discover._mapping_overrides.OVERRIDES_PATH", overrides_path):
            add_exclude_entry("prof", "TX", "https://j.com/old/")
            add_exclude_entry("prof", "TX", "https://j.com/old/")
            data = yaml.safe_load(overrides_path.read_text())
        assert data["prof"]["TX"]["exclude"].count("https://j.com/old/") == 1


# ---------------------------------------------------------------------------
# match_state: parent_chapter_url nodes must be skipped
# ---------------------------------------------------------------------------

class TestMatchStateSkipsLeafSections:
    """match_state must not match nodes that expand_containers appended —
    those carry parent_chapter_url and are match_sections' domain."""

    PROF_DEF = {"patterns": ["podiatry", "podiatric"], "excludes": []}

    def _state_record(self, chapters):
        return {"state": "FL", "chapters": chapters}

    def test_chapter_node_without_parent_url_is_matched(self):
        record = self._state_record([
            {"label": "Chapter 461 - Podiatric Medicine", "url": "https://j.com/ch461/",
             "slug": "chapter-461"},
        ])
        result = match_state(self.PROF_DEF, record)
        assert len(result) == 1
        assert result[0]["url"] == "https://j.com/ch461/"

    def test_leaf_section_with_parent_chapter_url_is_skipped(self):
        record = self._state_record([
            {"label": "461.001 Podiatric medicine license", "url": "https://j.com/ch461/461-001/",
             "slug": "461-001", "parent_chapter_url": "https://j.com/ch461/"},
        ])
        result = match_state(self.PROF_DEF, record)
        assert result == []

    def test_mixed_chapter_and_leaf_only_chapter_matched(self):
        record = self._state_record([
            {"label": "Chapter 461 - Podiatric Medicine", "url": "https://j.com/ch461/",
             "slug": "chapter-461"},
            {"label": "461.001 Podiatric medicine license", "url": "https://j.com/ch461/461-001/",
             "slug": "461-001", "parent_chapter_url": "https://j.com/ch461/"},
        ])
        result = match_state(self.PROF_DEF, record)
        assert len(result) == 1
        assert result[0]["url"] == "https://j.com/ch461/"

    def test_falsy_parent_chapter_url_not_skipped(self):
        # parent_chapter_url: "" or None should NOT be treated as truthy — node is kept
        record = self._state_record([
            {"label": "Chapter 461 - Podiatric Medicine", "url": "https://j.com/ch461/",
             "slug": "chapter-461", "parent_chapter_url": ""},
        ])
        result = match_state(self.PROF_DEF, record)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# write_targets (match_sections): new YAML-based behavior
# ---------------------------------------------------------------------------

import pipeline.discover.match_sections as ms


class TestWriteTargetsNewBehavior:
    """write_targets must:
    - write add nodes to mapping_overrides.yaml (not directly to index JSON)
    - tag nodes via='section_match'
    - skip urls already in the freshly-regenerated base index
    - call rebuild_and_write when anything was added
    """

    def test_writes_yaml_entry_and_rebuilds(self, tmp_path, monkeypatch):
        # hierarchy_targets returns one new container
        monkeypatch.setattr(ms, "hierarchy_targets",
                            lambda prof, st: {"https://j.com/ch626/": "Part VI Adjusters"}
                            if st == "FL" else {})

        rebuilt = []
        added: list[tuple] = []  # (profession, state, node) captures

        def fake_rebuild_index(prof, mapping_overrides=None):
            # Return empty base (no existing matches) so the url is new
            return {"by_state": {"FL": {"matched": []}}}

        def fake_rebuild_and_write(prof):
            rebuilt.append(prof)

        def fake_add_override_entry(profession, state, node):
            added.append((profession, state, node))

        monkeypatch.setattr(ms, "rebuild_index", fake_rebuild_index)
        monkeypatch.setattr(ms, "rebuild_and_write", fake_rebuild_and_write)
        monkeypatch.setattr(ms, "add_override_entry", fake_add_override_entry)

        written = ms.write_targets("public_adjuster", ["FL", "GA"])

        assert "FL" in written
        assert written["FL"] == ["Part VI Adjusters"]
        # add_override_entry was called with the right node (via='section_match')
        assert len(added) == 1
        prof, st, node = added[0]
        assert prof == "public_adjuster"
        assert st == "FL"
        assert node["url"] == "https://j.com/ch626/"
        assert node["via"] == "section_match"
        # rebuild was called once
        assert rebuilt == ["public_adjuster"]

    def test_skips_url_already_in_base_index(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ms, "hierarchy_targets",
                            lambda prof, st: {"https://j.com/ch626/": "Part VI"}
                            if st == "FL" else {})

        def fake_rebuild_index(prof, mapping_overrides=None):
            # URL already present in base
            return {"by_state": {"FL": {"matched": [
                {"url": "https://j.com/ch626/", "label": "Part VI"}
            ]}}}

        added: list = []
        monkeypatch.setattr(ms, "rebuild_index", fake_rebuild_index)
        monkeypatch.setattr(ms, "rebuild_and_write", lambda prof: None)
        monkeypatch.setattr(ms, "add_override_entry", lambda prof, st, node: added.append(node))

        written = ms.write_targets("public_adjuster", ["FL"])
        assert written == {}  # nothing new to write
        assert added == []   # add_override_entry was never called

    def test_dedup_within_same_run(self, tmp_path, monkeypatch):
        """URL already in existing_urls set within a single write_targets call
        must not be passed to add_override_entry twice (guard in write_targets loop)."""
        # Simulate two different urls mapped to the same state by hierarchy_targets
        # but one url repeated — write_targets uses a local existing_urls set to dedup.
        calls: list[str] = []

        def fake_hierarchy_targets(prof, st):
            if st == "FL":
                return {
                    "https://j.com/ch1/": "Part I",
                    "https://j.com/ch1/": "Part I duplicate",  # noqa: F601 — intentional: tests Python dict dedup
                }
            return {}

        def fake_rebuild_index(prof, mapping_overrides=None):
            return {"by_state": {}}

        def fake_add_override_entry(profession, state, node):
            calls.append(node["url"])

        monkeypatch.setattr(ms, "hierarchy_targets", fake_hierarchy_targets)
        monkeypatch.setattr(ms, "rebuild_index", fake_rebuild_index)
        monkeypatch.setattr(ms, "rebuild_and_write", lambda prof: None)
        monkeypatch.setattr(ms, "add_override_entry", fake_add_override_entry)

        ms.write_targets("public_adjuster", ["FL"])
        assert calls.count("https://j.com/ch1/") == 1  # no duplicates
