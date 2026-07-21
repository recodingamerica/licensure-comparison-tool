"""Tests for the held-cell triage classifier (pipeline.ingest.triage_held)."""

import json

import pytest

from pipeline.ingest import triage_held as th


def _sec(cit, error=False):
    return {"citation": cit, "url": f"https://j/{cit}", "text": "x", "error": error}


@pytest.fixture
def env(tmp_path, monkeypatch):
    results, text = tmp_path / "results", tmp_path / "text"
    (results / "pending_review" / "r").mkdir(parents=True)
    monkeypatch.setattr(th, "RESULTS_DIR", results)
    monkeypatch.setattr(th, "TEXT_DIR", text)
    return results, text


def _held(results, text, prof, st, committed_cits, cand_secs):
    (text / prof).mkdir(parents=True, exist_ok=True)
    (text / prof / f"{st}.json").write_text(json.dumps(
        {"sections": [_sec(c) for c in committed_cits]}))
    (results / "pending_review" / "r" / f"{prof}__{st}.json").write_text(json.dumps(
        {"profession": prof, "state": st, "new_corpus": {"sections": cand_secs}}))


def test_flake_when_low_overlap(env):
    results, text = env
    # candidate shares none of the committed citations → wrong page / truncation
    _held(results, text, "hvac", "NC", ["87-16", "87-17"], [_sec("87-52"), _sec("87-53")])
    (row,) = th.triage("r")
    assert row["verdict"] == "FETCH_FLAKE"


def test_flake_when_candidate_has_fetch_errors(env):
    results, text = env
    _held(results, text, "p", "ST", ["a", "b"], [_sec("a"), _sec("b", error=True)])
    (row,) = th.triage("r")
    assert row["verdict"] == "FETCH_FLAKE"


def test_growth_when_superset(env):
    results, text = env
    # kept all committed citations AND added more → more complete
    _held(results, text, "medicine", "WA", ["a", "b"], [_sec("a"), _sec("b"), _sec("c")])
    (row,) = th.triage("r")
    assert row["verdict"] == "GROWTH"


def test_change_when_high_overlap_small_drop(env):
    results, text = env
    # kept 4/5 committed citations, dropped one → genuine repeal or transient
    _held(results, text, "medicine", "TN", ["a", "b", "c", "d", "e"],
          [_sec("a"), _sec("b"), _sec("c"), _sec("d")])
    (row,) = th.triage("r")
    assert row["verdict"] == "CHANGE"
