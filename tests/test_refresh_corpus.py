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
from pathlib import Path

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
    # refresh_item now folds pull-provenance into its OK commit — point provenance +
    # the index loader at the SAME tmp tree so stamps land under this repo, not the real one.
    from pipeline import provenance as pv
    import pipeline.config.loaders as loaders
    monkeypatch.setattr(pv, "PROV_DIR", results / "provenance")
    monkeypatch.setattr(pv, "TEXT_DIR", text_dir)
    monkeypatch.setattr(loaders, "PROFESSION_INDEX_DIR", idx_dir)
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


def _committed_files(root, ref="HEAD"):
    out = subprocess.run(["git", "show", "--name-only", "--format=", ref],
                         cwd=root, capture_output=True, text=True, check=True)
    return {line for line in out.stdout.split("\n") if line}


def test_commit_does_not_sweep_unrelated_staged_work(repo):
    """commit() must commit ONLY its own paths.

    A bare `git commit` commits the WHOLE index. This crawl runs unattended for hours,
    so anything staged meanwhile by a person or another tool gets silently absorbed into
    a "data: refresh" commit that claims to be a corpus update. That really happened
    (2026-07-27): four unrelated file deletions landed inside one corpus commit.
    """
    root, _idx, text_dir = repo
    (root / "seed.txt").write_text("seed")
    subprocess.run(["git", "add", "seed.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True)

    # Someone else's work, staged in this repo but nothing to do with the corpus.
    unrelated = root / "unrelated.txt"
    unrelated.write_text("do not commit me")
    subprocess.run(["git", "add", "unrelated.txt"], cwd=root, check=True)

    corpus = text_dir / "nursing" / "UT.json"
    corpus.parent.mkdir(parents=True, exist_ok=True)
    corpus.write_text(json.dumps({"sections": []}))

    rc.commit(corpus, "data: refresh nursing/UT — 0->0 sections")

    committed = _committed_files(root)
    assert "pipeline/results/text/nursing/UT.json" in committed
    assert "unrelated.txt" not in committed, (
        f"commit() swept unrelated staged work into a corpus commit: {committed}")
    # ...and it is left staged for its real owner, not silently discarded.
    staged = subprocess.run(["git", "diff", "--cached", "--name-only"],
                            cwd=root, capture_output=True, text=True, check=True).stdout
    assert "unrelated.txt" in staged


def test_commit_includes_extra_paths_in_one_commit(repo):
    """The pull-provenance stamp must still land in the SAME commit as its corpus —
    path-scoping the commit must not drop it."""
    root, _idx, text_dir = repo
    (root / "seed.txt").write_text("seed")
    subprocess.run(["git", "add", "seed.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True)

    corpus = text_dir / "nursing" / "UT.json"
    corpus.parent.mkdir(parents=True, exist_ok=True)
    corpus.write_text(json.dumps({"sections": []}))
    stamp = root / "pipeline" / "results" / "provenance" / "nursing" / "UT.json"
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(json.dumps({"stage": "pull"}))

    rc.commit(corpus, "data: refresh nursing/UT — 0->0 sections", stamp)

    committed = _committed_files(root)
    assert "pipeline/results/text/nursing/UT.json" in committed
    assert "pipeline/results/provenance/nursing/UT.json" in committed


class TestBookmarkDurability:
    """The resume bookmark must survive a crash and a reboot.

    Both guarantees lived in an external watchdog script until 2026-07-27. Kill the
    terminal and you lost them, which is how a reboot cost a run's progress.
    """

    def _setup(self, repo, monkeypatch, states):
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {s: {"matched": [{"url": CH}]} for s in states})
        for s in states:
            _commit_corpus(root, text_dir, "med", s,
                           asdict(_corpus(s, "med", [CH], [CH + "s1"])))
        monkeypatch.setattr(rc.pull_text, "pull_state",
                            lambda state, prof, rows, cap: _corpus(state, "med", [CH], [CH + "s1"]))
        return root

    def test_bookmark_write_is_atomic(self, repo, monkeypatch):
        """A crash mid-write must leave the PREVIOUS bookmark intact, never a truncated
        one — a truncated bookmark parses as None and silently restarts the run at zero."""
        self._setup(repo, monkeypatch, ["CA", "IN", "TX", "NY"])
        rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
               breaker=3, run_id="t", chrome_check=lambda: True)
        status_path = rc._status_path("t")
        good = status_path.read_text()

        # Simulate the machine dying partway through writing the next bookmark: every
        # write lands half its bytes and then fails. Deliberately NOT keyed on a .tmp
        # filename — the old non-atomic _save() wrote straight to status_path, so this
        # truncates the real bookmark there and the assertions below catch it.
        real_write = Path.write_text

        def die_mid_write(self, data, *a, **k):
            real_write(self, data[: len(data) // 2])
            raise OSError("simulated crash mid-write")

        monkeypatch.setattr(Path, "write_text", die_mid_write)
        with pytest.raises(OSError):
            rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
                   breaker=3, run_id="t", chrome_check=lambda: True)
        monkeypatch.undo()

        assert status_path.read_text() == good, "crash mid-write corrupted the bookmark"
        assert json.loads(status_path.read_text())["items"], "bookmark no longer parses"

    def test_bookmark_is_git_checkpointed_without_sweeping(self, repo, monkeypatch):
        """The run commits its own bookmark (so a reboot can't lose it) and that commit
        must not absorb unrelated staged work."""
        root = self._setup(repo, monkeypatch, ["CA", "IN"])
        monkeypatch.setattr(rc, "CHECKPOINT_EVERY_CELLS", 1)

        unrelated = root / "unrelated.txt"
        unrelated.write_text("someone else's staged work")
        subprocess.run(["git", "add", "unrelated.txt"], cwd=root, check=True)

        rc.run(["med"], set(), force=False, cap=None, timeout_s=60,
               breaker=3, run_id="t", chrome_check=lambda: True)

        log = subprocess.run(["git", "log", "--oneline"], cwd=root,
                             capture_output=True, text=True, check=True).stdout
        assert "checkpoint t bookmark" in log, f"bookmark was never checkpointed:\n{log}"

        checkpoints = subprocess.run(
            ["git", "log", "--format=%H", "--grep", "checkpoint t bookmark"],
            cwd=root, capture_output=True, text=True, check=True).stdout.split()
        for sha in checkpoints:
            assert "unrelated.txt" not in _committed_files(root, sha), \
                "a bookmark checkpoint swept unrelated staged work"


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

    def test_furniture_only_change_is_nochange(self, repo, monkeypatch):
        # The committed corpus and the new pull carry the SAME statute but DIFFERENT
        # Justia furniture — a bumped version-list year + a fresh annotation apparatus.
        # Change-detection compares CLEANED text, so this is NOCHANGE (not re-committed),
        # even though the raw bytes differ. Regression guard for the 2026-07-18 CO chrome
        # auto-commit.
        root, idx_dir, text_dir = repo

        def mk(secs):
            return StateCorpus(
                state="CA", profession="med", chapter_urls=[CH],
                sections=[Section(url=u, label="l", citation=c, text=t, text_len=len(t))
                          for (u, c, t) in secs],
                total_chars=sum(len(t) for _, _, t in secs))

        _write_index(idx_dir, "med", {"CA": {"matched": [{"url": CH}]}})
        statute = "A person shall not practice without a license."
        old = mk([(CH + "s1", "ch-1/s1",
                   f"Go to Other Versions\n2024 Colorado Rev. Stat.\nView All Versions\n{statute}")])
        _commit_corpus(root, text_dir, "med", "CA", asdict(old))
        # New pull: newer version year + a Colorado annotation apparatus appended.
        new = mk([(CH + "s1", "ch-1/s1",
                   f"Go to Other Versions\n2025 Colorado Rev. Stat.\nView All Versions\n{statute}\n"
                   "Annotations\nHierarchy Notes:\nC.R.S. Title 12\nANNOTATION\nSmith v. Board.")])
        monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a, **k: new)
        rec = rc.refresh_item("med", "CA", [{"chapter_url": CH}],
                              force=False, cap=None, timeout_s=60)
        assert rec["result"] == "NOCHANGE", rec

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

    def test_source_unavailable_node_excluded_from_worklist(self, repo):
        # A source_unavailable node is an ACCEPTED gap (regulated but no Justia/PA
        # statute — e.g. admin-code-only). Refreshing it re-fetches a general page
        # that yields 0 fields and can hang past the item timeout, aborting the whole
        # annual run. It must be dropped from the worklist. A state whose ONLY node is
        # source_unavailable disappears entirely; a normal state stays.
        root, idx_dir, text_dir = repo
        _write_index(idx_dir, "med", {
            "CA": {"matched": [{"url": CH}]},
            "OK": {"matched": [{"url": CH2, "source_unavailable": {"reason": "admin-code only"}}]},
        })
        work = rc.build_worklist(["med"], set())
        states = {state for _p, state, _r in work}
        assert states == {"CA"}, states

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


class TestReviewVerdict:
    """The held-cell verdict badge on the --review page (_section_diff), computed on
    ERROR-FREE citation overlap between the committed corpus and the rejected candidate."""

    def _commit(self, repo, cits):
        root, _idx, text_dir = repo
        _commit_corpus(root, text_dir, "med", "CA",
                       {"sections": [{"citation": c, "url": f"https://j/{c}", "text": "x"} for c in cits]})

    def test_flake_on_low_overlap(self, repo):
        self._commit(repo, ["a", "b", "c"])                       # candidate shares none → wrong page
        cand = {"sections": [{"citation": "x"}, {"citation": "y"}]}
        assert rc._section_diff(cand, "med", "CA")["verdict"] == "FETCH_FLAKE"

    def test_flake_on_fetch_errors(self, repo):
        self._commit(repo, ["a", "b"])
        cand = {"sections": [{"citation": "a"}, {"citation": "b", "error": "boom"}]}
        assert rc._section_diff(cand, "med", "CA")["verdict"] == "FETCH_FLAKE"

    def test_growth_on_clean_superset(self, repo):
        self._commit(repo, ["a", "b"])                            # kept all + added more
        cand = {"sections": [{"citation": "a"}, {"citation": "b"}, {"citation": "c"}]}
        assert rc._section_diff(cand, "med", "CA")["verdict"] == "GROWTH"

    def test_change_on_high_overlap_small_drop(self, repo):
        self._commit(repo, ["a", "b", "c", "d", "e"])             # kept 4/5, dropped one
        cand = {"sections": [{"citation": c} for c in ("a", "b", "c", "d")]}
        assert rc._section_diff(cand, "med", "CA")["verdict"] == "CHANGE"

    def test_committed_junk_sections_dont_mask_a_cleaner_growth(self, repo):
        # committed carries errored junk; the cleaner candidate must read GROWTH, not shrink.
        root, _idx, text_dir = repo
        _commit_corpus(root, text_dir, "med", "CA", {"sections":
            [{"citation": "a", "url": "u", "text": "x"}, {"citation": "b", "url": "u", "text": "x"}]
            + [{"citation": f"junk{i}", "error": "boom"} for i in range(20)]})
        cand = {"sections": [{"citation": c, "url": "u", "text": "x"} for c in ("a", "b", "c")]}
        assert rc._section_diff(cand, "med", "CA")["verdict"] == "GROWTH"


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


# ---------------------------------------------------------------------------
# --until-done: the in-process auto-relaunch loop that replaced the external
# annual-refresh watchdog. run() is mocked so no real fetching happens; we only
# assert the loop's control flow (converge / no-progress stop / max-passes).
# ---------------------------------------------------------------------------
class TestRunUntilDone:
    def _wire(self, monkeypatch, worklist, status_sequence):
        """build_worklist returns a fixed 3-cell worklist; run() returns each
        status in status_sequence in turn, recording how many times it was called."""
        monkeypatch.setattr(rc, "build_worklist", lambda profs, states: worklist)
        calls = {"n": 0}

        def fake_run(*a, **k):
            i = calls["n"]
            calls["n"] += 1
            return status_sequence[min(i, len(status_sequence) - 1)]

        monkeypatch.setattr(rc, "run", fake_run)
        return calls

    @staticmethod
    def _status(done_keys):
        return {"items": {k: {"result": "OK"} for k in done_keys}}

    WORK = [("med", "UT", []), ("med", "CO", []), ("law", "UT", [])]

    def test_converges_and_stops(self, monkeypatch):
        # pass 1 settles one cell, pass 2 settles the rest -> stop after pass 2.
        seq = [self._status(["med:UT"]),
               self._status(["med:UT", "med:CO", "law:UT"])]
        calls = self._wire(monkeypatch, self.WORK, seq)
        rc.run_until_done([], set(), timeout_s=60, breaker=3, run_id="t")
        assert calls["n"] == 2

    def test_no_progress_guard_stops(self, monkeypatch):
        # every pass settles the same single cell -> second pass makes no progress -> stop.
        seq = [self._status(["med:UT"])]
        calls = self._wire(monkeypatch, self.WORK, seq)
        rc.run_until_done([], set(), timeout_s=60, breaker=3, run_id="t")
        assert calls["n"] == 2  # pass 1 (rem 2), pass 2 (rem still 2) -> stop

    def test_max_passes_bounds_the_loop(self, monkeypatch):
        # a pass that keeps reducing by one but never reaches 0 is capped by max_passes.
        seq = [self._status(["med:UT"]), self._status(["med:UT"])]
        # first pass rem=2, then force strict monotonic decrease via a growing set:
        seq = [self._status(list({"med:UT", "med:CO", "law:UT"})[:1]),
               self._status(list({"med:UT", "med:CO", "law:UT"})[:2])]
        calls = self._wire(monkeypatch, self.WORK, seq)
        rc.run_until_done([], set(), timeout_s=60, breaker=3, run_id="t", max_passes=2)
        assert calls["n"] == 2  # capped

    def test_remaining_to_attempt_counts_unsettled(self):
        status = {"items": {"med:UT": {"result": "OK"},
                            "med:CO": {"result": "REGRESSION"}}}
        # OK is settled; a held result also counts as skip (won't be retried by --skip-held);
        # law:UT is neither -> 1 remaining.
        monkey_work = [("med", "UT", []), ("med", "CO", []), ("law", "UT", [])]
        import unittest.mock as m
        with m.patch.object(rc, "build_worklist", lambda p, s: monkey_work):
            assert rc._remaining_to_attempt(status, [], set()) == 1

    def test_transient_startup_abort_is_retried_not_no_progress(self, monkeypatch):
        # A pass that aborts on the startup liveness check (attempted nothing) must
        # NOT trip the no-progress guard — it's transient. Two blips, then it settles.
        seq = [{"startup_unreachable": True},
               {"startup_unreachable": True},
               self._status(["med:UT", "med:CO", "law:UT"])]
        calls = self._wire(monkeypatch, self.WORK, seq)
        monkeypatch.setattr(rc.time, "sleep", lambda *_a: None)  # no real backoff wait
        rc.run_until_done([], set(), timeout_s=60, breaker=3, run_id="t")
        assert calls["n"] == 3  # retried both blips, then converged — not stopped at pass 2

    def test_startup_unreachable_gives_up_after_limit(self, monkeypatch):
        # Justia down for good: retry up to the limit, then give up (don't loop forever).
        calls = self._wire(monkeypatch, self.WORK, [{"startup_unreachable": True}])
        monkeypatch.setattr(rc.time, "sleep", lambda *_a: None)
        monkeypatch.setattr(rc, "load_limits",
                            lambda: {"refresh": {"startup_retry_limit": 3, "startup_retry_seconds": 0}})
        rc.run_until_done([], set(), timeout_s=60, breaker=3, run_id="t")
        assert calls["n"] == 3  # 3 consecutive unreachable -> give up


# ---------------------------------------------------------------------------
# empty_chapters: a repealed/reserved SECTION in a section-range mapping (MA G.L.
# Ch 112: each profession maps a slice of individual sections) must NOT count as a
# failed chapter → no false PARTIAL. Only a whole CHAPTER container coming back empty
# is a partial-pull signal.
# ---------------------------------------------------------------------------
def test_empty_chapters_ignores_section_level_gaps():
    base = "https://law.justia.com/codes/massachusetts/part-i/title-xvi/chapter-112"
    # MA-style: four mapped SECTION nodes; two of them repealed (no pulled section).
    section_nodes = [f"{base}/section-73a/", f"{base}/section-73c/",   # 73c repealed → empty
                     f"{base}/section-74/",  f"{base}/section-75z/"]   # 75z repealed → empty
    pulled = [{"url": f"{base}/section-73a/"}, {"url": f"{base}/section-74/"}]
    assert rc.empty_chapters(section_nodes, pulled) == []   # gaps ignored, no PARTIAL


def test_empty_chapters_still_flags_an_empty_chapter_container():
    a = "https://law.justia.com/codes/wa/title-18/chapter-18-79/"
    b = "https://law.justia.com/codes/wa/title-18/chapter-18-80/"   # this one pulls nothing
    pulled = [{"url": f"{a}section-18-79-010/"}]
    assert rc.empty_chapters([a, b], pulled) == [b]   # a real empty CHAPTER still holds
