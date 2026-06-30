"""Tests for the pull_text runaway guard (#53 robustness).

pull_text --limit-sections defaults to 500: a whole-title over-match (a profession
mapped to a 2500-section state-government title) is capped + loudly FLAGGED rather
than silently pulling thousands of sections. This used to only exist in pull_all;
the CLI default was None until 2026-06-30, so a hand-pull could silently run away.

We stub pull_state (no network) and point the dir globals at tmp_path, then run
main() and check the cap that reaches pull_state + the flag log.
"""

import json

import pytest

import pipeline.ingest.pull_text as pt
from pipeline.ingest.pull_text import Section, StateCorpus


@pytest.fixture
def wired(tmp_path, monkeypatch):
    """Point index/output dirs at tmp_path and write a one-state profession index."""
    idx_dir = tmp_path / "profession_index"
    txt_dir = tmp_path / "text"
    idx_dir.mkdir()
    txt_dir.mkdir()
    monkeypatch.setattr(pt, "PROFESSION_INDEX_DIR", idx_dir)
    monkeypatch.setattr(pt, "TEXT_DIR", txt_dir)
    (idx_dir / "electrician.json").write_text(json.dumps({
        "by_state": {"CA": {"matched": [
            {"url": "https://law.justia.com/codes/california/chapter-1/", "label": "Ch 1"}
        ]}}
    }))
    return idx_dir, txt_dir


def _stub_pull_state(monkeypatch, n_sections):
    """Make pull_state return n_sections and record the cap it was handed."""
    seen = {}

    def fake(state, profession, rows, limit_sections):
        seen["cap"] = limit_sections
        secs = [Section(url=f"u{i}", label=f"l{i}", citation="", text="x", text_len=1)
                for i in range(n_sections)]
        return StateCorpus(state=state, profession=profession, sections=secs, total_chars=n_sections)

    monkeypatch.setattr(pt, "pull_state", fake)
    return seen


def _run(monkeypatch, argv):
    monkeypatch.setattr(pt.sys, "argv", ["pull_text", *argv])
    pt.main()


class TestRunawayGuard:
    def test_default_cap_is_500(self, wired, monkeypatch):
        seen = _stub_pull_state(monkeypatch, n_sections=10)
        _run(monkeypatch, ["--profession", "electrician"])
        assert seen["cap"] == 500

    def test_zero_disables_cap(self, wired, monkeypatch):
        seen = _stub_pull_state(monkeypatch, n_sections=10)
        _run(monkeypatch, ["--profession", "electrician", "--limit-sections", "0"])
        assert seen["cap"] is None

    def test_hitting_cap_flags_loudly(self, wired, monkeypatch, caplog):
        _stub_pull_state(monkeypatch, n_sections=500)  # exactly at the default cap
        with caplog.at_level("WARNING"):
            _run(monkeypatch, ["--profession", "electrician"])
        msg = caplog.text
        assert "hit the 500-section cap" in msg
        assert "runaway cap" in msg  # end-of-run summary line

    def test_under_cap_no_flag(self, wired, monkeypatch, caplog):
        _stub_pull_state(monkeypatch, n_sections=12)
        with caplog.at_level("WARNING"):
            _run(monkeypatch, ["--profession", "electrician"])
        assert "section cap" not in caplog.text

    def test_corpus_written(self, wired, monkeypatch):
        _, txt_dir = wired
        _stub_pull_state(monkeypatch, n_sections=3)
        _run(monkeypatch, ["--profession", "electrician"])
        out = txt_dir / "electrician" / "CA.json"
        assert out.exists()
        assert len(json.loads(out.read_text())["sections"]) == 3
