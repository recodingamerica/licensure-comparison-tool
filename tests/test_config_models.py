"""models.yaml loader: per-stage model config with a built-in fallback."""
from __future__ import annotations

from pipeline.config import loaders


def test_model_for_reads_configured_stage(monkeypatch):
    monkeypatch.setattr(loaders, "load_models", lambda: {"trim": "some-model-x"})
    assert loaders.model_for("trim", "FALLBACK") == "some-model-x"


def test_model_for_falls_back_when_key_missing(monkeypatch):
    monkeypatch.setattr(loaders, "load_models", lambda: {"extract": "e"})
    assert loaders.model_for("trim", "FALLBACK") == "FALLBACK"


def test_model_for_falls_back_when_file_empty(monkeypatch):
    monkeypatch.setattr(loaders, "load_models", lambda: {})
    assert loaders.model_for("schema", "FALLBACK") == "FALLBACK"


def test_shipped_models_yaml_defines_the_three_paid_stages():
    """The committed config must cover every paid stage — a missing key would
    silently fall back to the module default and make the config a lie."""
    loaders.load_models.cache_clear()
    models = loaders.load_models()
    assert {"trim", "extract", "schema"} <= set(models)
    assert all(isinstance(v, str) and v for v in models.values())
