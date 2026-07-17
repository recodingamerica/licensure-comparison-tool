"""model_for reads every model from config/models.yaml — never a Python literal.

A stage with its own key gets that model; anything else gets the file's `default`;
a stage with no key AND no default (and no arg) fails loud rather than picking silently.
"""

import pytest

from pipeline.config import loaders


def test_own_key_wins(monkeypatch):
    monkeypatch.setattr(loaders, "load_models", lambda: {"default": "D", "trim": "T"})
    assert loaders.model_for("trim") == "T"


def test_falls_back_to_file_default(monkeypatch):
    monkeypatch.setattr(loaders, "load_models", lambda: {"default": "D"})
    assert loaders.model_for("map_prep") == "D"          # no map_prep key → default


def test_arg_default_beats_file_default(monkeypatch):
    monkeypatch.setattr(loaders, "load_models", lambda: {"default": "D"})
    assert loaders.model_for("whatever", "ARG") == "ARG"


def test_fail_loud_when_nothing_resolves(monkeypatch):
    monkeypatch.setattr(loaders, "load_models", lambda: {})   # no key, no default
    with pytest.raises(RuntimeError, match="no model configured"):
        loaders.model_for("trim")


def test_real_models_yaml_has_a_default():
    # The shipped file must define `default` so unlisted tools never fail loud in prod.
    assert loaders.load_models().get("default")
