"""The pull worker: every pull_state call runs in ONE persistent thread (so the
thread-affine Scrapling session stays put), with a wall-clock timeout, error
propagation, and a fresh worker after a timeout wedges the old one."""

import threading
import time

import pytest

import pipeline.ingest.refresh_corpus as rc


def _reset():
    rc._PULL_THREAD = None


def test_all_pulls_run_in_one_thread(monkeypatch):
    _reset()
    threads = []
    monkeypatch.setattr(rc.pull_text, "pull_state",
                        lambda *a: threads.append(threading.get_ident()) or {"sections": []})
    for _ in range(5):
        rc.pull_with_timeout("UT", "x", [], None, 5)
    assert len(set(threads)) == 1          # a single worker thread served every cell
    assert threads[0] != threading.get_ident()   # and it's NOT the caller thread


def test_result_and_error_propagate(monkeypatch):
    _reset()
    monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a: {"sections": [1, 2]})
    assert rc.pull_with_timeout("UT", "x", [], None, 5) == {"sections": [1, 2]}

    _reset()
    def boom(*a):
        raise ValueError("pull failed")
    monkeypatch.setattr(rc.pull_text, "pull_state", boom)
    with pytest.raises(ValueError, match="pull failed"):
        rc.pull_with_timeout("UT", "x", [], None, 5)


def test_timeout_raises_and_gives_fresh_worker_next_time(monkeypatch):
    _reset()
    monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a: time.sleep(3) or {"sections": []})
    with pytest.raises(rc._ItemTimeout):
        rc.pull_with_timeout("UT", "x", [], None, 0.2)
    assert rc._PULL_THREAD is None          # wedged worker orphaned

    # the next call must NOT inherit the wedged worker's stale result
    monkeypatch.setattr(rc.pull_text, "pull_state", lambda *a: {"sections": ["fresh"]})
    assert rc.pull_with_timeout("UT", "x", [], None, 5) == {"sections": ["fresh"]}
    _reset()
