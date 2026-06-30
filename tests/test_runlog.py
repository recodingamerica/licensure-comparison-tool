"""_runlog: best-effort cross-stage run record."""

from __future__ import annotations

import json

import pipeline._runlog as rl


def test_record_and_load(tmp_path, monkeypatch):
    monkeypatch.setattr(rl, "RUNLOG_PATH", tmp_path / ".run_log.json")
    rl.record_run("pull_text", profession="dietetics", states=5)
    log = rl.load_runlog()
    assert "pull_text" in log
    e = log["pull_text"]
    assert e["profession"] == "dietetics" and e["states"] == 5
    assert e["last_run"][:4].isdigit()       # ISO timestamp
    assert "git_sha" in e


def test_record_updates_in_place(tmp_path, monkeypatch):
    monkeypatch.setattr(rl, "RUNLOG_PATH", tmp_path / ".run_log.json")
    rl.record_run("clean_text", profession="a")
    rl.record_run("clean_text", profession="b")
    rl.record_run("trim_state", profession="c")
    log = rl.load_runlog()
    assert log["clean_text"]["profession"] == "b"   # latest wins
    assert set(log) == {"clean_text", "trim_state"}


def test_record_never_raises(tmp_path, monkeypatch):
    # An unwritable path must not propagate into the calling stage.
    monkeypatch.setattr(rl, "RUNLOG_PATH", tmp_path / "nope" / "x" / ".run_log.json")
    monkeypatch.setattr(rl, "_git_sha", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    rl.record_run("extract_state", profession="z")   # should swallow, not raise


def test_load_missing_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(rl, "RUNLOG_PATH", tmp_path / "absent.json")
    assert rl.load_runlog() == {}
