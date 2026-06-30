"""clean_text.corpus_from_overrides must fail LOUD on a malformed overrides file.

A silently-empty return would disable every sibling-corpus borrow run-wide,
producing false gaps. Missing file is still legitimately empty.
"""

from __future__ import annotations

import pytest

import pipeline.ingest.clean_text as ct


def test_missing_file_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(ct, "CONFIG_DIR", tmp_path)  # no corpus_overrides.yaml here
    assert ct.corpus_from_overrides("hvac") == {}


def test_malformed_yaml_raises(tmp_path, monkeypatch):
    (tmp_path / "corpus_overrides.yaml").write_text("hvac: [unterminated\n  : :::")
    monkeypatch.setattr(ct, "CONFIG_DIR", tmp_path)
    with pytest.raises(RuntimeError):
        ct.corpus_from_overrides("hvac")


def test_valid_yaml_loads(tmp_path, monkeypatch):
    (tmp_path / "corpus_overrides.yaml").write_text("hvac:\n  TN: construction_trades\n")
    monkeypatch.setattr(ct, "CONFIG_DIR", tmp_path)
    assert ct.corpus_from_overrides("hvac") == {"TN": "construction_trades"}
