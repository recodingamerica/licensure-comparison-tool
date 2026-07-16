"""Every operator config file is read through safe_load_unique, so a duplicate
mapping key fails loud (pointing at the key) instead of being silently dropped
last-wins — the WA/VA/NV state_structure data-loss failure mode, closed for the
remaining files (professions / corpus_overrides / verified_absences)."""

import pytest
import yaml

import pipeline.config.loaders as loaders

# Two `medicine:` keys — plain yaml.safe_load would keep only the second.
DUP = "medicine:\n  a: 1\nmedicine:\n  b: 2\n"


def _point_config_at(tmp_path, monkeypatch, filename):
    (tmp_path / filename).write_text(DUP)
    monkeypatch.setattr(loaders, "CONFIG_DIR", tmp_path)


def test_professions_dup_key_raises(tmp_path, monkeypatch):
    _point_config_at(tmp_path, monkeypatch, "professions.yaml")
    with pytest.raises(yaml.YAMLError):
        loaders.load_professions()


def test_verified_absences_dup_key_raises(tmp_path, monkeypatch):
    _point_config_at(tmp_path, monkeypatch, "verified_absences.yaml")
    with pytest.raises(yaml.YAMLError):
        loaders.load_verified_absences()


def test_corpus_overrides_dup_key_raises(tmp_path, monkeypatch):
    # load_corpus_overrides wraps a YAMLError as RuntimeError ("unreadable").
    _point_config_at(tmp_path, monkeypatch, "corpus_overrides.yaml")
    with pytest.raises(RuntimeError):
        loaders.load_corpus_overrides()


def test_valid_professions_still_loads(tmp_path, monkeypatch):
    (tmp_path / "professions.yaml").write_text("medicine:\n  a: 1\nnursing:\n  b: 2\n")
    monkeypatch.setattr(loaders, "CONFIG_DIR", tmp_path)
    d = loaders.load_professions()
    assert set(d) == {"medicine", "nursing"}
