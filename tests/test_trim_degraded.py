"""trim_state LLM-failure hardening: degraded flag + --strict.

Simulate the LLM call failing (call_model -> None) on a >1-section corpus (so
the single-section short-circuit doesn't apply) and assert:
  - default: data is kept, but trim_degraded=true and skipped reasons are the
    LLM-fail marker (so preflight flags it POISONED);
  - strict=True: TrimLLMError is raised and nothing is written.
"""

from __future__ import annotations

import pytest

import pipeline.ingest.trim_state as ts
from pipeline.ingest._trim_health import is_poisoned


def _sections():
    return [
        {"citation": "1-1", "url": "u1", "label": "scope", "text": "practice of x", "text_len": 13},
        {"citation": "1-2", "url": "u2", "label": "board", "text": "board of y", "text_len": 10},
    ]


@pytest.fixture
def clean_corpus(tmp_path, monkeypatch):
    clean = tmp_path / "clean"
    (clean / "dietetics").mkdir(parents=True)
    import json
    (clean / "dietetics" / "IA.json").write_text(json.dumps({"sections": _sections(), "chapter_urls": ["c1"]}))
    monkeypatch.setattr(ts, "CLEAN_DIR", clean)
    return clean


def test_degraded_flag_on_llm_failure(clean_corpus, monkeypatch):
    monkeypatch.setattr(ts, "call_model", lambda *a, **k: None)
    corpus = ts.trim_state("IA", "dietetics", ts.DEFAULT_MODEL)
    assert corpus is not None
    assert corpus.trim_degraded is True
    # data preserved (keep-everything fallback)
    assert len(corpus.sections) == 2
    # every skipped entry carries the LLM-fail reason → poisoned
    assert all(s["reason"] == ts.LLM_FAIL_REASON for s in corpus.skipped)
    from dataclasses import asdict
    assert is_poisoned(asdict(corpus)) is True


def test_strict_raises_and_writes_nothing(clean_corpus, monkeypatch):
    monkeypatch.setattr(ts, "call_model", lambda *a, **k: None)
    with pytest.raises(ts.TrimLLMError):
        ts.trim_state("IA", "dietetics", ts.DEFAULT_MODEL, strict=True)


def test_healthy_trim_not_degraded(clean_corpus, monkeypatch):
    # A real result: keep both sections, no degradation.
    class _Dec:
        def __init__(self, c, keep):
            self.citation, self.keep, self.reason = c, keep, "ok"

    class _Result:
        decisions = [_Dec("1-1", True), _Dec("1-2", True)]

    monkeypatch.setattr(ts, "call_model", lambda *a, **k: _Result())
    corpus = ts.trim_state("IA", "dietetics", ts.DEFAULT_MODEL)
    assert corpus.trim_degraded is False
    from dataclasses import asdict
    assert is_poisoned(asdict(corpus)) is False
