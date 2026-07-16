"""Tests for refresh_corpus — the durable annual Justia re-pull.

No network / pull_state-for-real: pull_state is monkeypatched to return fixture
corpora, the startup liveness check (justia_reachable) is monkeypatched, and git
is exercised in a real temp repo (per-item commit path). Covers the 2026-07-16
rewrite:

  * per-chapter completeness  -> a mapped-but-empty chapter is PARTIAL, not committed
  * ONE shrink guard          -> a pull that loses error-free sections is a REGRESSION
                                 (held back), unless --force accepts it
  * real-fetch detection      -> an unchanged file is NOCHANGE (does NOT trip the breaker)
  * circuit breaker           -> only consecutive FETCH FAILURES (empty/dead) abort;
                                 unchanged (NOCHANGE) corpora do not
  * untracked revert          -> a bad first-time pull's file is DELETED, not left on disk
  * diff report               -> written on abort too; held-back rows surface
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
    monkeypatch.setattr(rc, "LOGS_DIR", results / "logs")  # keep summary files out of the real tree
    # source is "reachable" unless a test overrides; never probe urls for real.
    monkeypatch.setattr(rc, "justia_reachable", lambda *a, **k: True)
    monkeypatch.setattr(rc, "_classify_empty", lambda urls: {u: "LIVE" for u in urls})
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


def _cite(u):
    return "/".join(u.rstrip("/").split("/")[-2:])  # distinct per (chapter, section)


def _sections(urls):
    # distinct citation + text per section so the content-aware regression logic
    # (citation-keyed, then text-keyed) is actually exercised.
    return [Section(url=u, label=f"L {_cite(u)}", citation=_cite(u),
                    text=f"body of {_cite(u)}", text_len=8) for u in urls]


def _corpus(state, prof, chapter_urls, urls):
    secs = _sections(urls)
    return StateCorpus(state=state, profession=prof, chapter_urls=chapter_urls,
                       sections=secs, total_chars=sum(len(s.text) for s in secs))


CH = "https://law.justia.com/codes/x/title-1/chapter-1/"
CH2 = "https://law.justia.com/codes/x/title-1/chapter-2/"


# ---------------------------------------------------------------------------
# Per-chapter completeness
# ---------------------------------------------------------------------------
class TestPerChapterCompleteness:
    def test_empty_mapped_chapter_is_partial_not_committed(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [
            {"url": CH, "label": "A", "slug": "chapter-1"},
            {"url": CH2, "label": "B", "slug": "chapter-2"},
        ]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH, CH2], [CH + "s1", CH2 + "s1"])))
        # New pull: chapter 2 contributes ZERO sections (partial), total > 0.
        new = _corpus("CA", "med", [CH, CH2], [CH + "s1", CH + "s2", CH + "s3"])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: new)

        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}, {"chapter_url": CH2}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "PARTIAL"
        assert CH2 in rec["empty_chapters"]
        # Reverted: the committed file is still the seed (2 sections).
        on_disk = json.loads((text_dir / "med" / "CA.json").read_text())
        assert len(on_disk["sections"]) == 2

    def test_all_chapters_populated_commits_ok(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}, {"url": CH2}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH, CH2], [CH + "s1"])))
        new = _corpus("CA", "med", [CH, CH2], [CH + "s1", CH + "s2", CH2 + "s1"])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: new)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}, {"chapter_url": CH2}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "OK"
        assert rec["prev"] == 1 and rec["new"] == 3
        show = subprocess.run(["git", "show", "HEAD:pipeline/results/text/med/CA.json"],
                              cwd=root, capture_output=True, text=True)
        assert len(json.loads(show.stdout)["sections"]) == 3

    def test_empty_with_dead_link_is_dead(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], []))  # 0 sections
        monkeypatch.setattr(rc, "_classify_empty", lambda urls: {u: "DEAD_404" for u in urls})
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "DEAD"
        assert rec["url_health"][CH] == "DEAD_404"

    def test_empty_with_live_link_is_empty_not_dead(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], []))
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "EMPTY"  # live link, just no matching sections

    def test_all_errored_sections_is_empty_not_committed(self, repo, monkeypatch):
        # A pull whose sections all carry an error has 0 error-free sections — the
        # ok-count gate catches it even though len(sections) > 0.
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1"])))
        errored = StateCorpus(state="CA", profession="med", chapter_urls=[CH],
                              sections=[Section(url=CH + "s1", label="l", citation="c",
                                                text="", text_len=0, error="fetch failed")],
                              total_chars=0)
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: errored)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] in ("EMPTY", "DEAD")
        on_disk = json.loads((text_dir / "med" / "CA.json").read_text())
        assert len(on_disk["sections"]) == 1  # seed preserved


# ---------------------------------------------------------------------------
# Shrink guard (the rewrite's headline fix)
# ---------------------------------------------------------------------------
class TestRegressionGuard:
    def test_shrink_is_regression_not_committed(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + f"s{i}" for i in range(5)])))
        # Pull collapses 5 -> 1 sections (each chapter still non-empty, so the
        # per-chapter gate passes) — the regression gate must catch it.
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], [CH + "s0"]))
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "REGRESSION"
        assert "missing from the new pull" in rec["reason"]  # 4 sections genuinely gone
        assert rec["attempts"] == 1  # clean pull -> trusted, not re-fetched
        on_disk = json.loads((text_dir / "med" / "CA.json").read_text())
        assert len(on_disk["sections"]) == 5  # seed preserved, shrink NOT committed

    def test_renumbering_commits_not_held_back(self, repo, monkeypatch):
        # Justia renumbers a section: same TEXT, new citation. Content is preserved,
        # so it must COMMIT (a legit update), not be held back as a regression.
        root, idx_dir, text_dir = repo

        def mk(secs):  # secs: [(url, citation, text)]
            return StateCorpus(
                state="CA", profession="med", chapter_urls=[CH],
                sections=[Section(url=u, label="l", citation=c, text=t, text_len=len(t))
                          for (u, c, t) in secs],
                total_chars=sum(len(t) for _, _, t in secs))

        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        committed = mk([(CH + "s1", "ch-1/s1", "aaa body one"),
                        (CH + "s2", "ch-1/s2", "bbb body two")])
        _commit_corpus(root, text_dir, "med", "CA", asdict(committed))
        # s2 renumbered to s2b — same text "bbb body two", new citation/url.
        renumbered = mk([(CH + "s1", "ch-1/s1", "aaa body one"),
                         (CH + "s2b", "ch-1/s2b", "bbb body two")])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: renumbered)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "OK"  # content preserved -> committed, not REGRESSION

    def test_transient_fetch_error_is_retried(self, repo, monkeypatch):
        # A transient shows up as a FETCH ERROR on a section; that IS retried, and
        # the clean second attempt is what counts. (A clean-but-short pull is not
        # retried — that's the content gate's job — so the transient signal is the
        # error, not a bare count shortfall.)
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1", CH + "s2"])))
        calls = {"n": 0}
        def flaky(state, prof, rows, cap):
            calls["n"] += 1
            c = _corpus("CA", "med", [CH], [CH + "s1", CH + "s2"])
            if calls["n"] == 1:
                c.sections[1].error = "cloudflare challenge"  # s2 transiently failed
                c.sections[1].text = ""
            return c
        monkeypatch.setattr(rc.pull_text, "pull_state", flaky)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "NOCHANGE"   # the clean retry matches committed
        assert rec["attempts"] >= 2          # the errored first attempt was retried
        assert calls["n"] >= 2

    def test_clean_short_pull_is_not_retried(self, repo, monkeypatch):
        # A clean pull that's merely shorter than committed must NOT be re-fetched —
        # the content gate decides. (Regression from the WY run: retrying clean short
        # pulls tripled the annual run's time on every genuine removal.)
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1", CH + "s2", CH + "s3"])))
        calls = {"n": 0}
        def short(state, prof, rows, cap):
            calls["n"] += 1
            return _corpus("CA", "med", [CH], [CH + "s1", CH + "s2"])  # clean, 2 of 3
        monkeypatch.setattr(rc.pull_text, "pull_state", short)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "REGRESSION"
        assert calls["n"] == 1  # exactly one pull — no wasted re-fetches

    def test_force_accepts_regression(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + f"s{i}" for i in range(5)])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], [CH + "s0"]))
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=True, cap=None, timeout_s=60)
        assert rec["result"] == "OK"
        show = subprocess.run(["git", "show", "HEAD:pipeline/results/text/med/CA.json"],
                              cwd=root, capture_output=True, text=True)
        assert len(json.loads(show.stdout)["sections"]) == 1  # shrink accepted


# ---------------------------------------------------------------------------
# First-time (untracked) pulls
# ---------------------------------------------------------------------------
class TestUntrackedRevert:
    def test_untracked_empty_pull_file_is_deleted(self, repo, monkeypatch):
        # No prior commit: a first-time EMPTY pull must DELETE its file, not leave
        # it on disk (git checkout is a no-op on an untracked path).
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], []))
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "EMPTY"
        assert not (text_dir / "med" / "CA.json").exists()

    def test_untracked_healthy_pull_commits(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], [CH + "s1", CH + "s2"]))
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "OK"
        show = subprocess.run(["git", "show", "HEAD:pipeline/results/text/med/CA.json"],
                              cwd=root, capture_output=True, text=True)
        assert len(json.loads(show.stdout)["sections"]) == 2


# ---------------------------------------------------------------------------
# Real-fetch detection
# ---------------------------------------------------------------------------
class TestRealFetchDetection:
    def test_unchanged_file_is_nochange(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        seed = asdict(_corpus("CA", "med", [CH], [CH + "s1", CH + "s2"]))
        _commit_corpus(root, text_dir, "med", "CA", seed)
        same = _corpus("CA", "med", [CH], [CH + "s1", CH + "s2"])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: same)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "NOCHANGE"

    def test_schema_drift_only_is_nochange_not_committed(self, repo, monkeypatch):
        # The committed corpus was serialized before StateCorpus gained a field
        # (e.g. source_unavailable). A re-pull with identical sections re-serializes
        # byte-differently — but it must be NOCHANGE, not a spurious "updated" commit.
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        seed = asdict(_corpus("CA", "med", [CH], [CH + "s1", CH + "s2"]))
        seed.pop("source_unavailable", None)  # older serialization, missing the field
        _commit_corpus(root, text_dir, "med", "CA", seed)
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], [CH + "s1", CH + "s2"]))
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "NOCHANGE"
        # The corpus file is unchanged vs HEAD — the byte-only rewrite was discarded,
        # no spurious commit. (The uncommitted test index is unrelated fixture state.)
        st = subprocess.run(["git", "status", "--porcelain", "--",
                             "pipeline/results/text/med/CA.json"],
                            cwd=root, capture_output=True, text=True)
        assert st.stdout.strip() == ""


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------
class TestCircuitBreaker:
    def test_unchanged_corpora_do_not_trip_breaker(self, repo, monkeypatch):
        # The key rewrite: a normal annual refresh where every state is unchanged
        # (NOCHANGE) must COMPLETE, not abort after 3.
        root, idx_dir, text_dir = repo
        states = ["CA", "IN", "TX", "NY"]
        _write_index(idx_dir, "med", {s: {"matched": [{"url": CH}]} for s in states})
        for s in states:
            _commit_corpus(root, text_dir, "med", s,
                           asdict(_corpus(s, "med", [CH], [CH + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda state, prof, rows, cap: _corpus(state, "med", [CH], [CH + "s1"]))
        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                        breaker=3, run_id="t", chrome_check=lambda: True)
        assert "aborted" not in status
        assert len(status["items"]) == 4
        assert all(i["result"] == "NOCHANGE" for i in status["items"].values())

    def test_consecutive_fetch_failures_abort(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        states = ["CA", "IN", "TX", "NY"]
        _write_index(idx_dir, "med", {s: {"matched": [{"url": CH}]} for s in states})
        for s in states:
            _commit_corpus(root, text_dir, "med", s,
                           asdict(_corpus(s, "med", [CH], [CH + "s1"])))
        # Every pull comes back empty -> EMPTY (a genuine fetch failure).
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda state, prof, rows, cap: _corpus(state, "med", [CH], []))
        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                        breaker=3, run_id="t", chrome_check=lambda: True)
        assert "aborted" in status
        assert "fetch failures" in status["aborted"]
        assert len(status["items"]) == 3  # stopped at the 3rd; 4th never attempted

    def test_summary_file_written(self, repo, monkeypatch):
        # The plain-English summary persists to a file (walk-away-and-come-back).
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda *a, **k: _corpus("CA", "med", [CH], [CH + "s1"]))
        rc.run(["med"], set(), force=False, cap=None, timeout_s=60, breaker=3,
               run_id="sumtest", chrome_check=lambda: True)
        summ = rc.LOGS_DIR / "refresh_sumtest_summary.txt"
        assert summ.exists()
        assert "Refresh summary" in summ.read_text()
        assert "1 unchanged" in summ.read_text()

    def test_estimate_seconds_positive(self, repo):
        # A worklist estimate is a positive number (rough, but non-zero).
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        work = rc.build_worklist(["med"], set())
        assert rc._estimate_seconds(work) > 0

    def test_diff_report_written_on_abort(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        states = ["CA", "IN", "TX"]
        _write_index(idx_dir, "med", {s: {"matched": [{"url": CH}]} for s in states})
        for s in states:
            _commit_corpus(root, text_dir, "med", s,
                           asdict(_corpus(s, "med", [CH], [CH + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda state, prof, rows, cap: _corpus(state, "med", [CH], []))
        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                        breaker=3, run_id="t", chrome_check=lambda: True)
        assert "diff_report" in status  # report written even though the run aborted
        assert (root / "docs" / "reports" / "refresh_diff_t.md").exists()


# ---------------------------------------------------------------------------
# Resume
# ---------------------------------------------------------------------------
class TestResume:
    def test_resume_skips_settled_reattempts_failures(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]},
                                      "IN": {"matched": [{"url": CH}]}})
        for s in ("CA", "IN"):
            _commit_corpus(root, text_dir, "med", s,
                           asdict(_corpus(s, "med", [CH], [CH + "s1"])))

        # Run 1: CA comes back empty (held back), IN unchanged (settled).
        def pull1(state, prof, rows, cap):
            if state == "CA":
                return _corpus("CA", "med", [CH], [])
            return _corpus("IN", "med", [CH], [CH + "s1"])
        monkeypatch.setattr(rc.pull_text, "pull_state", pull1)
        rc.run(["med"], set(), force=False, cap=None, timeout_s=60, breaker=3,
               run_id="r", chrome_check=lambda: True)

        # Run 2 with --resume: IN is settled → must NOT be re-pulled; CA re-attempted.
        pulled = []
        def pull2(state, prof, rows, cap):
            pulled.append(state)
            return _corpus(state, "med", [CH], [CH + "s1", CH + "s2"])  # healthy now
        monkeypatch.setattr(rc.pull_text, "pull_state", pull2)
        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60, breaker=3,
                        run_id="r", resume=True, chrome_check=lambda: True)

        assert pulled == ["CA"]  # only the previously-failed cell re-attempted
        assert status["items"]["med:CA"]["result"] == "OK"
        assert status["items"]["med:IN"]["result"] == "NOCHANGE"  # carried from run 1
        # Both corpora still counted in the summary state.
        assert len(status["items"]) == 2


# ---------------------------------------------------------------------------
# Timeout
# ---------------------------------------------------------------------------
class TestItemTimeout:
    def test_item_timeout_aborts_cleanly_with_report(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]},
                                      "IN": {"matched": [{"url": CH}]}})
        for s in ("CA", "IN"):
            _commit_corpus(root, text_dir, "med", s,
                           asdict(_corpus(s, "med", [CH], [CH + "s1"])))

        def boom(*a, **k):
            raise rc._ItemTimeout("pull_state exceeded 60s wall clock (genuine hang)")
        monkeypatch.setattr(rc, "refresh_item", boom)

        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                        breaker=3, run_id="t", chrome_check=lambda: True)
        assert "aborted" in status
        assert "timeout" in status["aborted"].lower()
        assert "diff_report" in status
        assert len(status["items"]) == 1  # aborted on the first item


# ---------------------------------------------------------------------------
# Diff report
# ---------------------------------------------------------------------------
class TestDiffReport:
    def test_vanished_chapter_flagged_recodification(self):
        old = {"sections": [{"url": CH + "s1"}, {"url": CH2 + "s1"}]}
        new = {"sections": [{"url": CH + "s1"}]}
        diff = rc.diff_one(old, new)
        assert "codes/x/title-1/chapter-2" in diff["vanished_chapters"]
        assert rc.classify(diff) == "likely recodification (chapter vanished)"

    def test_grown_corpus_is_grew(self):
        old = {"sections": [{"url": CH + "s1"}]}
        new = {"sections": [{"url": CH + "s1"}, {"url": CH + "s2"}, {"url": CH + "s3"}]}
        diff = rc.diff_one(old, new)
        assert diff["delta"] == 2
        assert rc.classify(diff) == "grew"

    def test_shrunk_chapter_flagged_suspicious(self):
        old = {"sections": [{"url": CH + f"s{i}"} for i in range(10)]}
        new = {"sections": [{"url": CH + "s0"}]}
        diff = rc.diff_one(old, new)
        assert diff["shrunk_chapters"]
        assert rc.classify(diff) == "suspicious shrink (chapter dropped >30%)"

    def test_held_back_regression_row_surfaces(self, repo):
        # A held-back (reverted) REGRESSION item must appear in the report, sourced
        # from its recorded prev/new (on-disk == prior, so a diff would show nothing).
        status = {"items": {"med:CA": {
            "profession": "med", "state": "CA", "result": "REGRESSION",
            "prev": 5, "new": 1, "reason": "new pull has 1 ok sections vs 5 committed",
        }}}
        report = rc.write_diff_report(status, "runX")
        md = report.read_text()
        assert "held back — suspicious shrink" in md
        assert "med/CA" in md
        assert "1 ok sections vs 5" in md


# ---------------------------------------------------------------------------
# Progress display
# ---------------------------------------------------------------------------
class TestProgress:
    def test_line_mode_emits_one_line_per_cell(self, monkeypatch):
        import io
        from collections import Counter
        buf = io.StringIO()
        monkeypatch.setattr(rc, "_OUT", buf)
        p = rc._Progress(2, use_bar=False)
        p.update("med:CA", "NOCHANGE", Counter({"NOCHANGE": 1}), 0)
        p.update("med:IN", "OK", Counter({"NOCHANGE": 1, "OK": 1}), 0)
        p.close()
        out = buf.getvalue()
        assert "[1/2] med:CA → NOCHANGE" in out
        assert "[2/2] med:IN → OK" in out
        assert "1 unchanged, 1 updated" in out

    def test_bar_mode_writes_anomalies_and_survives(self, monkeypatch):
        import io
        from collections import Counter
        buf = io.StringIO()
        monkeypatch.setattr(rc, "_OUT", buf)
        p = rc._Progress(2, use_bar=True)  # tqdm to a non-tty buffer
        if p.bar is None:  # tqdm not installed — nothing to assert
            return
        p.update("med:CA", "OK", Counter({"OK": 1}), 0)          # anomaly -> written above bar
        p.update("med:IN", "NOCHANGE", Counter({"OK": 1, "NOCHANGE": 1}), 0)
        p.close()
        assert "med:CA → OK" in buf.getvalue()


# ---------------------------------------------------------------------------
# --force safety guard (CLI)
# ---------------------------------------------------------------------------
class TestForceScopeGuard:
    def test_force_with_all_professions_is_rejected(self):
        # The blanket-override footgun: --force + --all-professions must error out
        # (argparse SystemExit) rather than mass-accept every shrink.
        with pytest.raises(SystemExit):
            rc.main(["--all-professions", "--force"])

    def test_force_with_single_profession_is_allowed(self, repo, monkeypatch):
        # Scoped --force is fine (no SystemExit from the guard). Stub the run so no
        # network happens; we only assert the guard didn't reject the invocation.
        called = {"ran": False}
        monkeypatch.setattr(rc, "run", lambda *a, **k: called.__setitem__("ran", True) or {})
        rc.main(["--profession", "med", "--states", "CA", "--force", "--run-id", "t"])
        assert called["ran"] is True


# ---------------------------------------------------------------------------
# Startup liveness abort
# ---------------------------------------------------------------------------
class TestStartupLivenessAbort:
    def test_unreachable_source_aborts_without_pulling(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1"])))

        def boom(*a, **k):
            raise AssertionError("pull_state must NOT run when the source is unreachable")
        monkeypatch.setattr(rc.pull_text, "pull_state", boom)

        status = rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                        breaker=3, run_id="t", chrome_check=lambda: False)
        assert "aborted" in status
        assert "not reachable" in status["aborted"].lower()


# ---------------------------------------------------------------------------
# A hard pull error propagates (Scrapling self-retries at the fetch layer; a hard
# failure aborts the run loudly rather than committing bad data).
# ---------------------------------------------------------------------------
class TestPullErrorPropagates:
    def test_hard_pull_error_propagates(self, repo, monkeypatch):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        _commit_corpus(root, text_dir, "med", "CA",
                       asdict(_corpus("CA", "med", [CH], [CH + "s1"])))

        def dead(*a, **k):
            raise RuntimeError("scrapling session died")
        monkeypatch.setattr(rc.pull_text, "pull_state", dead)

        with pytest.raises(RuntimeError, match="scrapling session died"):
            rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                   breaker=3, run_id="t", chrome_check=lambda: True)
