"""Tests for refresh_corpus — the durable annual Justia re-pull.

No network / pull_state-for-real: pull_state is monkeypatched to return fixture
corpora, the startup liveness check (justia_reachable) is monkeypatched, and git
is exercised in a real temp repo (per-item commit path). Covers the hardening
from docs/runbooks/cdp_repull_lessons_2026-07-02.md:

  * per-chapter completeness  -> a mapped-but-empty chapter is PARTIAL, not committed
  * real-fetch detection      -> an unchanged file is NOCHANGE
  * circuit breaker           -> 3 consecutive non-productive results aborts
  * diff report               -> a vanished chapter is "likely recodification"; growth is "grew"
  * startup liveness abort     -> an unreachable source aborts before any pull
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict

import pytest

import pipeline.ingest.refresh_corpus as rc
from pipeline.ingest.pull_text import Section, StateCorpus


# ---------------------------------------------------------------------------
# A real (tiny) git repo wired so RESULTS_DIR / TEXT_DIR / PROFESSION_INDEX_DIR
# point inside it, and refresh_corpus.ROOT is the repo root.
# ---------------------------------------------------------------------------
@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)

    results = root / "pipeline" / "results"
    idx_dir = results / "profession_index"
    text_dir = results / "text"
    idx_dir.mkdir(parents=True)
    text_dir.mkdir(parents=True)

    monkeypatch.setattr(rc, "ROOT", root)
    monkeypatch.setattr(rc, "RESULTS_DIR", results)
    monkeypatch.setattr(rc, "PROFESSION_INDEX_DIR", idx_dir)
    monkeypatch.setattr(rc, "TEXT_DIR", text_dir)
    # source is "reachable" unless a test overrides.
    monkeypatch.setattr(rc, "justia_reachable", lambda *a, **k: True)
    return root, idx_dir, text_dir


def _write_index(idx_dir, prof, by_state):
    (idx_dir / f"{prof}.json").write_text(json.dumps({"by_state": by_state}))


def _commit_corpus(root, text_dir, prof, state, corpus_dict):
    p = text_dir / prof / f"{state}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(corpus_dict, indent=2))
    rel = str(p.relative_to(root))
    subprocess.run(["git", "add", rel], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True)


def _sections(urls):
    return [Section(url=u, label="l", citation="c", text="x", text_len=1) for u in urls]


def _corpus(state, prof, chapter_urls, urls):
    return StateCorpus(state=state, profession=prof, chapter_urls=chapter_urls,
                       sections=_sections(urls), total_chars=len(urls))


# ---------------------------------------------------------------------------
# Per-chapter completeness
# ---------------------------------------------------------------------------
class TestPerChapterCompleteness:
    def test_empty_mapped_chapter_is_partial_not_committed(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch_a = "https://law.justia.com/codes/x/title-1/chapter-1/"
        ch_b = "https://law.justia.com/codes/x/title-1/chapter-2/"
        _write_index(idx_dir, "med", {"CA": {"matched": [
            {"url": ch_a, "label": "A", "slug": "chapter-1"},
            {"url": ch_b, "label": "B", "slug": "chapter-2"},
        ]}})
        # Seed a prior corpus so there's a HEAD to revert to.
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [ch_a, ch_b], [ch_a + "s1"])))

        # New pull: chapter B contributes ZERO sections (partial), total > 0.
        new = _corpus("CA", "med", [ch_a, ch_b],
                      [ch_a + "s1", ch_a + "s2", ch_a + "s3"])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: new)

        rec = rc.refresh_item("med", "CA",
                              [{"chapter_url": ch_a}, {"chapter_url": ch_b}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "PARTIAL"
        assert ch_b in rec["empty_chapters"]
        # Reverted: the committed file is still the seed (1 section), uncommitted.
        on_disk = json.loads((text_dir / "med" / "CA.json").read_text())
        assert len(on_disk["sections"]) == 1

    def test_all_chapters_populated_commits_ok(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch_a = "https://law.justia.com/codes/x/title-1/chapter-1/"
        ch_b = "https://law.justia.com/codes/x/title-1/chapter-2/"
        _write_index(idx_dir, "med", {"CA": {"matched": [
            {"url": ch_a}, {"url": ch_b}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [ch_a, ch_b], [ch_a + "s1"])))
        new = _corpus("CA", "med", [ch_a, ch_b],
                      [ch_a + "s1", ch_a + "s2", ch_b + "s1"])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: new)
        rec = rc.refresh_item("med", "CA",
                              [{"chapter_url": ch_a}, {"chapter_url": ch_b}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "OK"
        assert rec["prev"] == 1 and rec["new"] == 3
        # Committed: HEAD now has the 3-section corpus, working tree clean.
        show = subprocess.run(["git", "show", "HEAD:pipeline/results/text/med/CA.json"],
                              cwd=root, capture_output=True, text=True)
        assert len(json.loads(show.stdout)["sections"]) == 3

    def test_empty_with_dead_link_is_dead(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch = "https://law.justia.com/codes/x/title-1/chapter-1/"
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": ch}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [ch], [ch + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [ch], []))  # 0 sections
        monkeypatch.setattr(rc, "_classify_empty", lambda urls: {u: "DEAD_404" for u in urls})
        rec = rc.refresh_item("med", "CA", [{"chapter_url": ch}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "DEAD"
        assert rec["url_health"][ch] == "DEAD_404"

    def test_empty_with_live_link_is_empty_not_dead(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch = "https://law.justia.com/codes/x/title-1/chapter-1/"
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": ch}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [ch], [ch + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [ch], []))
        monkeypatch.setattr(rc, "_classify_empty", lambda urls: {u: "LIVE" for u in urls})
        rec = rc.refresh_item("med", "CA", [{"chapter_url": ch}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "EMPTY"  # live link, just no matching sections


# ---------------------------------------------------------------------------
# Real-fetch detection
# ---------------------------------------------------------------------------
class TestRealFetchDetection:
    def test_unchanged_file_is_nochange(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch = "https://law.justia.com/codes/x/title-1/chapter-1/"
        seed = asdict(_corpus("CA", "med", [ch], [ch + "s1", ch + "s2"]))
        _commit_corpus(root, text_dir, "med", "CA", seed)
        # Pull returns a corpus IDENTICAL to what's committed -> no real fetch.
        same = _corpus("CA", "med", [ch], [ch + "s1", ch + "s2"])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: same)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": ch}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "NOCHANGE"


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------
class TestCircuitBreaker:
    def test_three_consecutive_nonproductive_aborts(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch = "https://law.justia.com/codes/x/title-1/chapter-1/"
        states = ["CA", "IN", "TX", "NY"]
        _write_index(idx_dir, "med", {s: {"matched": [{"url": ch}]} for s in states})
        # Each state seeded with an IDENTICAL corpus so every re-pull is NOCHANGE.
        for s in states:
            _commit_corpus(root, text_dir, "med", s,
                           asdict(_corpus(s, "med", [ch], [ch + "s1"])))

        def same_corpus(state, prof, rows, cap):
            return _corpus(state, "med", [ch], [ch + "s1"])
        monkeypatch.setattr(rc.pull_text, "pull_state", same_corpus)

        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                        breaker=3, run_id="t", chrome_check=lambda: True)
        assert "aborted" in status
        assert "consecutive" in status["aborted"]
        # Stopped at the 3rd item; the 4th was never attempted.
        assert len(status["items"]) == 3


# ---------------------------------------------------------------------------
# Diff report
# ---------------------------------------------------------------------------
class TestDiffReport:
    def test_vanished_chapter_flagged_recodification(self):
        old = {"sections": [
            {"url": "https://law.justia.com/codes/x/title-1/chapter-1/s1"},
            {"url": "https://law.justia.com/codes/x/title-1/chapter-2/s1"},
        ]}
        new = {"sections": [
            {"url": "https://law.justia.com/codes/x/title-1/chapter-1/s1"},
        ]}
        diff = rc.diff_one(old, new)
        assert "codes/x/title-1/chapter-2" in diff["vanished_chapters"]
        assert rc.classify(diff) == "likely recodification (chapter vanished)"

    def test_grown_corpus_is_grew(self):
        old = {"sections": [{"url": "https://law.justia.com/codes/x/title-1/chapter-1/s1"}]}
        new = {"sections": [
            {"url": "https://law.justia.com/codes/x/title-1/chapter-1/s1"},
            {"url": "https://law.justia.com/codes/x/title-1/chapter-1/s2"},
            {"url": "https://law.justia.com/codes/x/title-1/chapter-1/s3"},
        ]}
        diff = rc.diff_one(old, new)
        assert diff["delta"] == 2
        assert rc.classify(diff) == "grew"

    def test_shrunk_chapter_flagged_suspicious(self):
        old = {"sections": [{"url": f"https://law.justia.com/codes/x/title-1/chapter-1/s{i}"}
                            for i in range(10)]}
        new = {"sections": [{"url": "https://law.justia.com/codes/x/title-1/chapter-1/s0"}]}
        diff = rc.diff_one(old, new)
        assert diff["shrunk_chapters"]
        assert rc.classify(diff) == "suspicious shrink (chapter dropped >30%)"

    def test_report_renders_grouped_by_severity(self):
        rows = [
            {"profession": "med", "state": "CA",
             "diff": rc.diff_one(
                 {"sections": [{"url": "https://law.justia.com/codes/x/title-1/chapter-2/s1"}]},
                 {"sections": []}),
             "severity": "likely recodification (chapter vanished)"},
        ]
        md = rc.render_diff_report(rows, "runX")
        assert "# Refresh diff report — runX" in md
        assert "likely recodification (chapter vanished)" in md
        assert "med/CA" in md


# ---------------------------------------------------------------------------
# Startup liveness abort
# ---------------------------------------------------------------------------
class TestStartupLivenessAbort:
    def test_unreachable_source_aborts_without_pulling(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch = "https://law.justia.com/codes/x/title-1/chapter-1/"
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": ch}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [ch], [ch + "s1"])))

        called = {"pull": False}
        def boom(*a, **k):
            called["pull"] = True
            raise AssertionError("pull_state must NOT run when the source is unreachable")
        monkeypatch.setattr(rc.pull_text, "pull_state", boom)

        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                        breaker=3, run_id="t", chrome_check=lambda: False)
        assert "aborted" in status
        assert "not reachable" in status["aborted"].lower()
        assert called["pull"] is False


# ---------------------------------------------------------------------------
# A pull error propagates (no more CDP-death retry — Scrapling self-retries at
# the fetch layer; a hard pull failure aborts the run loudly rather than
# committing bad data).
# ---------------------------------------------------------------------------
class TestPullErrorPropagates:
    def test_hard_pull_error_propagates(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        ch = "https://law.justia.com/codes/x/title-1/chapter-1/"
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": ch}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [ch], [ch + "s1"])))

        def dead(*a, **k):
            raise RuntimeError("scrapling session died")
        monkeypatch.setattr(rc.pull_text, "pull_state", dead)

        with pytest.raises(RuntimeError, match="scrapling session died"):
            rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                   breaker=3, run_id="t", chrome_check=lambda: True)
