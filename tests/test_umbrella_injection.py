"""Tests for the umbrella-text loader in extract_state.

Confirms:
  - Missing umbrella file → returns ''
  - Present umbrella file → returns a single concatenated text block with
    per-section markers
"""

import json
from pathlib import Path

import pytest


@pytest.fixture
def fake_umbrella(tmp_path, monkeypatch):
    from pipeline.extract import extract_state as es
    umb_dir = tmp_path / "umbrella_text"
    umb_dir.mkdir()
    # Point the loader at this dir
    monkeypatch.setattr(es, "RESULTS_DIR", tmp_path)
    return umb_dir


def test_returns_empty_when_no_umbrella_file(fake_umbrella):
    from pipeline.extract.extract_state import load_umbrella_text
    assert load_umbrella_text("XX") == ""


def test_returns_empty_when_no_sections(fake_umbrella):
    umb_dir = fake_umbrella
    (umb_dir / "XX.json").write_text(json.dumps({"state": "XX", "sections": []}))
    from pipeline.extract.extract_state import load_umbrella_text
    assert load_umbrella_text("XX") == ""


def test_concatenates_sections(fake_umbrella):
    umb_dir = fake_umbrella
    rec = {
        "state": "XX",
        "sections": [
            {"label": "1-101", "text": "Definitions section text", "umbrella_chapter_label": "General Provisions"},
            {"label": "1-102", "text": "Board composition text", "umbrella_chapter_label": "General Provisions"},
        ],
    }
    (umb_dir / "XX.json").write_text(json.dumps(rec))
    from pipeline.extract.extract_state import load_umbrella_text
    out = load_umbrella_text("XX")
    assert "Definitions section text" in out
    assert "Board composition text" in out
    assert "UMBRELLA" in out  # marker for the model to see


def test_label_truncated_to_60(fake_umbrella):
    umb_dir = fake_umbrella
    long_label = "A" * 100
    rec = {
        "state": "XX",
        "sections": [
            {"label": "1-101", "text": "x", "umbrella_chapter_label": long_label},
        ],
    }
    (umb_dir / "XX.json").write_text(json.dumps(rec))
    from pipeline.extract.extract_state import load_umbrella_text
    out = load_umbrella_text("XX")
    # Label gets truncated to 60 chars in the marker
    assert "A" * 60 in out
    assert "A" * 65 not in out
