"""Tests for config.yaml_loader (duplicate-key-detecting YAML load).

yaml.safe_load silently keeps the LAST of two same-named keys, which once let
a whole second `WA:` block (the disciplinary-umbrella config) get silently
dropped from state_structure.yaml. These lock in:
  - safe_load_unique raises on a duplicate mapping key (top-level and nested)
  - it otherwise behaves like a normal safe_load
  - the live config files actually parse clean (regression guard against a new
    duplicate state key sneaking back in)
"""

import pytest
import yaml

from pipeline.config.yaml_loader import safe_load_unique, load_yaml_file
from pipeline.paths import CONFIG_DIR


class TestDuplicateDetection:
    def test_raises_on_duplicate_top_level_key(self):
        text = "WA:\n  source: justia\nWA:\n  source: wa_official\n"
        with pytest.raises(yaml.constructor.ConstructorError) as exc:
            safe_load_unique(text)
        assert "duplicate key" in str(exc.value)
        assert "'WA'" in str(exc.value)

    def test_raises_on_duplicate_nested_key(self):
        text = "WA:\n  professions:\n    hvac: {a: 1}\n    hvac: {a: 2}\n"
        with pytest.raises(yaml.constructor.ConstructorError):
            safe_load_unique(text)

    def test_accepts_unique_keys(self):
        text = "WA:\n  source: wa_official\nVA:\n  source: va_official\n"
        data = safe_load_unique(text)
        assert data == {
            "WA": {"source": "wa_official"},
            "VA": {"source": "va_official"},
        }

    def test_load_yaml_file_missing_returns_empty(self, tmp_path):
        assert load_yaml_file(tmp_path / "does_not_exist.yaml") == {}


class TestLiveConfigsParse:
    @pytest.mark.parametrize("name", ["state_structure.yaml", "professions.yaml"])
    def test_no_duplicate_keys_in_committed_config(self, name):
        # Regression guard: a re-introduced duplicate state/profession key would
        # otherwise be silently dropped. This makes the test suite catch it.
        path = CONFIG_DIR / name
        if not path.exists():
            pytest.skip(f"{name} not present")
        safe_load_unique(path.read_text())  # raises if a duplicate key exists
