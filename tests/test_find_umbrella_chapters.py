"""Tests for find_umbrella_chapters candidate filtering.

The LLM call itself is mocked elsewhere; here we lock in the pre-filter
heuristic that trims oversized hierarchies (>600 chapters) down to a
manageable candidate set before sending to the model.
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from pipeline.discover.find_umbrella_chapters import find_for_state


@pytest.fixture
def fake_hierarchy(tmp_path, monkeypatch):
    """Stand up a fake HIERARCHY_DIR with one state's hierarchy."""
    from pipeline.discover import find_umbrella_chapters as fuc
    h_dir = tmp_path / "hierarchy"
    h_dir.mkdir()
    out_dir = tmp_path / "umbrella_chapters"
    out_dir.mkdir()
    monkeypatch.setattr(fuc, "HIERARCHY_DIR", h_dir)
    monkeypatch.setattr(fuc, "UMBRELLA_DIR", out_dir)
    return h_dir, out_dir


def _write_hierarchy(h_dir, state, chapters):
    (h_dir / f"{state}.json").write_text(json.dumps({"state": state, "chapters": chapters}))


def test_skips_when_no_hierarchy(fake_hierarchy):
    h_dir, out_dir = fake_hierarchy
    # No file written
    result = find_for_state("ZZ", model="m", force=False)
    assert result is None


def test_skips_when_zero_chapters(fake_hierarchy):
    h_dir, out_dir = fake_hierarchy
    _write_hierarchy(h_dir, "XY", [])
    result = find_for_state("XY", model="m", force=False)
    assert result is None


def test_large_hierarchy_filters_to_candidates(fake_hierarchy, monkeypatch):
    """When >600 chapters exist, only umbrella-suggestive labels go to the LLM."""
    h_dir, out_dir = fake_hierarchy
    chapters = []
    # 700 chapters with random labels
    for i in range(700):
        chapters.append({"slug": f"chapter-{i}", "label": f"Chapter {i} - Topic {i}", "url": "x"})
    # plus a few obvious umbrella candidates
    chapters.append({"slug": "ch-gen", "label": "Chapter G - General Provisions", "url": "x"})
    chapters.append({"slug": "ch-def", "label": "Chapter D - Definitions Applicable", "url": "x"})
    _write_hierarchy(h_dir, "XY", chapters)

    # Mock the LLM call
    fake_result = MagicMock()
    fake_result.umbrella_chapter_slugs = ["ch-gen", "ch-def"]
    with patch("pipeline.discover.find_umbrella_chapters.call_structured", return_value=fake_result):
        result = find_for_state("XY", model="m", force=False)

    assert result is not None
    assert set(result["umbrella_chapter_slugs"]) == {"ch-gen", "ch-def"}


def test_large_hierarchy_no_candidates_returns_empty(fake_hierarchy):
    """If filtering produces zero candidates, return empty without an LLM call."""
    h_dir, out_dir = fake_hierarchy
    chapters = [
        {"slug": f"chapter-{i}", "label": f"Chapter {i} - Specific Topic {i}", "url": "x"}
        for i in range(700)
    ]
    _write_hierarchy(h_dir, "XY", chapters)

    with patch("pipeline.discover.find_umbrella_chapters.call_structured") as mock_llm:
        result = find_for_state("XY", model="m", force=False)
        assert result is not None
        assert result["umbrella_chapter_slugs"] == []
        # Crucially: no LLM call should have happened
        mock_llm.assert_not_called()
