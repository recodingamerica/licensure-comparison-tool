"""Tests for pipeline._env.load_env.

Lock in the CLAUDE_API_KEY → ANTHROPIC_API_KEY fallback so future pipeline
scripts that import load_env() pick up the right env regardless of whether
the project .env uses the Anthropic-canonical name or the workspace name.
"""

import os
import importlib
import pytest


@pytest.fixture
def fresh_env(monkeypatch):
    """Wipe both API key env vars before each test so the fallback is observable."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
    # Force re-import of _env so its module-level state (none, but safety) is clean
    if "pipeline._env" in importlib.sys.modules:
        importlib.reload(importlib.sys.modules["pipeline._env"])
    yield


class TestLoadEnvFallback:
    def test_claude_key_propagates_to_anthropic_key(self, fresh_env, monkeypatch):
        monkeypatch.setenv("CLAUDE_API_KEY", "sk-test-claude-only")
        from pipeline._env import load_env

        load_env()
        assert os.environ["ANTHROPIC_API_KEY"] == "sk-test-claude-only"

    def test_existing_anthropic_key_is_preserved(self, fresh_env, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-existing")
        monkeypatch.setenv("CLAUDE_API_KEY", "sk-test-shouldnt-override")
        from pipeline._env import load_env

        load_env()
        # The existing ANTHROPIC_API_KEY wins
        assert os.environ["ANTHROPIC_API_KEY"] == "sk-test-existing"

    def test_idempotent(self, fresh_env, monkeypatch):
        """Calling load_env twice should not error or double-set."""
        monkeypatch.setenv("CLAUDE_API_KEY", "sk-test-claude-only")
        from pipeline._env import load_env

        load_env()
        load_env()
        assert os.environ["ANTHROPIC_API_KEY"] == "sk-test-claude-only"
