"""Tests for pipeline.provenance — the content-hash freshness mechanism. Everything runs
against tmp stage dirs so no real corpus is touched; recipe_hash's cache is cleared around
each test since it's lru_cached."""

import json

import pytest

from pipeline import provenance as pv


@pytest.fixture
def env(tmp_path, monkeypatch):
    text, clean, trim, struct = (tmp_path / d for d in ("text", "clean", "trim", "struct"))
    prov, disc = tmp_path / "prov", tmp_path / "disc"
    monkeypatch.setattr(pv, "_IN", {"clean": text, "trim": clean, "extract": trim})
    monkeypatch.setattr(pv, "_OUT", {"clean": clean, "trim": trim, "extract": struct})
    monkeypatch.setattr(pv, "PROV_DIR", prov)
    monkeypatch.setattr(pv, "DISCOVERED_DIR", disc)
    pv.recipe_hash.cache_clear()
    yield {"text": text, "clean": clean, "trim": trim, "struct": struct, "disc": disc}
    pv.recipe_hash.cache_clear()


def _write(d, prof, state, payload):
    (d / prof).mkdir(parents=True, exist_ok=True)
    (d / prof / f"{state}.json").write_text(json.dumps(payload))


# --- single-stage check states ------------------------------------------------

def test_missing_when_no_output(env):
    assert pv.check("clean", "x", "UT") == "missing"


def test_unstamped_when_output_but_no_provenance(env):
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    assert pv.check("clean", "x", "UT") == "unstamped"


def test_current_after_record(env):
    _write(env["text"], "x", "UT", {"sections": [1, 2]})
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    pv.record("clean", "x", "UT")
    assert pv.check("clean", "x", "UT") == "current"


def test_stale_when_input_changes(env):
    _write(env["text"], "x", "UT", {"sections": [1, 2]})
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    pv.record("clean", "x", "UT")
    _write(env["text"], "x", "UT", {"sections": [1, 2, 3]})  # corpus re-pulled → changed
    assert pv.check("clean", "x", "UT") == "stale"


def test_stale_when_recipe_changes(env, monkeypatch):
    _write(env["text"], "x", "UT", {"sections": [1]})
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    pv.record("clean", "x", "UT")
    monkeypatch.setitem(pv.CODE_VERSION, "clean", 999)
    pv.recipe_hash.cache_clear()
    assert pv.check("clean", "x", "UT") == "stale"


def test_input_provenance_key_ignored_in_hash(env):
    """A stage output that happens to carry an inlined _provenance key must hash the same
    as one without it, so a downstream stage's input_hash is stable."""
    _write(env["text"], "x", "UT", {"sections": [1]})
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    pv.record("clean", "x", "UT")
    # trim's input is the clean file; re-write it WITH an inline _provenance key, same payload
    (env["clean"] / "x" / "UT.json").write_text(json.dumps({"sections": ["a"], "_provenance": {"z": 1}}))
    _write(env["trim"], "x", "UT", {"sections": ["b"]})
    pv.record("trim", "x", "UT")
    # adding _provenance to the clean file must not make trim look stale
    assert pv.check("trim", "x", "UT") == "current"


# --- whole-cell freshness -----------------------------------------------------

def _full_chain(env):
    _write(env["disc"], "x", "x", {"fields": []})  # a schema so extract recipe is stable
    # rename: discovered file is <prof>.json, not <prof>/<state>
    (env["disc"] / "x.json").write_text(json.dumps({"fields": []}))
    _write(env["text"], "x", "UT", {"sections": [1]})
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    _write(env["trim"], "x", "UT", {"sections": ["b"]})
    _write(env["struct"], "x", "UT", {"licensure": {}})
    for s in pv.STAGES:
        pv.record(s, "x", "UT")


def test_cell_freshness_current(env):
    _full_chain(env)
    assert pv.cell_freshness("x", "UT") == ("current", None)


def test_cell_freshness_reports_earliest_stale(env):
    _full_chain(env)
    _write(env["text"], "x", "UT", {"sections": [9, 9]})  # earliest input changed
    assert pv.cell_freshness("x", "UT") == ("stale", "clean")


def test_cell_freshness_unstamped_if_any_stage_unstamped(env):
    _full_chain(env)
    (pv._prov_path("x", "UT")).write_text(json.dumps({"clean": pv.stamp("clean", "x", "UT")}))
    # trim/extract stamps now gone → not stale (hashes not compared), just unstamped
    assert pv.cell_freshness("x", "UT") == ("unstamped", None)


def test_recipe_models_match_stage_defaults():
    """provenance and each stage now BOTH read their model from config/models.yaml (via
    model_for), so they can no longer drift by hand-copy. This confirms they resolve the
    SAME model per stage — a mismatch would make freshness silently misjudge every cell."""
    from pipeline.ingest.trim_state import DEFAULT_MODEL as TRIM
    from pipeline.extract.extract_state import DEFAULT_MODEL as EXTRACT
    assert pv._model_for_stage("trim") == TRIM
    assert pv._model_for_stage("extract") == EXTRACT


def test_last_stamped_returns_latest(env):
    _write(env["text"], "x", "UT", {"sections": [1]})
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    pv.record("clean", "x", "UT")
    assert pv.last_stamped("x", "UT") is not None
    assert pv.last_stamped("x", "ZZ") is None
