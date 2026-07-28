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


# --- the 4 new stages: pull (cell) + schema/mapprep/publish (profession) ------

@pytest.fixture
def penv(tmp_path, monkeypatch):
    """Env for the profession-scoped + pull stages: monkeypatch every dir input_hash /
    _out_exists reference directly (these stages don't go through _IN/_OUT)."""
    dirs = {name: tmp_path / name for name in
            ("text", "trimmed", "structured", "mapprep", "discovered", "web", "prov")}
    monkeypatch.setattr(pv, "TEXT_DIR", dirs["text"])
    monkeypatch.setattr(pv, "TRIMMED_DIR", dirs["trimmed"])
    monkeypatch.setattr(pv, "STRUCTURED_DIR", dirs["structured"])
    monkeypatch.setattr(pv, "MAP_PREP_DIR", dirs["mapprep"])
    monkeypatch.setattr(pv, "DISCOVERED_DIR", dirs["discovered"])
    monkeypatch.setattr(pv, "WEB_PUBLIC_DIR", dirs["web"])
    monkeypatch.setattr(pv, "PROV_DIR", dirs["prov"])
    pv.recipe_hash.cache_clear()
    yield dirs
    pv.recipe_hash.cache_clear()


def _wr(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload))


def test_schema_is_profession_scoped_and_tracks_trimmed(penv):
    # schema output exists but no stamp yet -> unstamped (NEVER stale — the safety invariant)
    _wr(penv["trimmed"] / "x" / "UT.json", {"sections": ["a"]})
    _wr(penv["discovered"] / "x.json", {"fields": []})
    assert pv.check("schema", "x") == "unstamped"
    # stamp it -> current; the stamp lands in the shared per-profession file
    pv.record("schema", "x")
    assert pv.check("schema", "x") == "current"
    assert (penv["prov"] / "x" / "_profession.json").exists()
    # a change to ANY trimmed state flips schema stale (its input is the whole dir)
    _wr(penv["trimmed"] / "x" / "UT.json", {"sections": ["a", "b"]})
    assert pv.check("schema", "x") == "stale"


def test_publish_tracks_structured_and_mapprep(penv):
    _wr(penv["structured"] / "x" / "UT.json", {"licensure": {}})
    (penv["mapprep"] / "x").mkdir(parents=True)
    _wr(penv["mapprep"] / "x" / "normalized.json", {"rows": []})
    _wr(penv["web"] / "data" / "x.json", {"payload": 1})
    pv.record("publish", "x")
    assert pv.check("publish", "x") == "current"
    # a map_prep change invalidates publish
    _wr(penv["mapprep"] / "x" / "normalized.json", {"rows": [1]})
    assert pv.check("publish", "x") == "stale"


def test_publish_missing_when_no_payload(penv):
    _wr(penv["structured"] / "x" / "UT.json", {"licensure": {}})
    assert pv.check("publish", "x") == "missing"


def test_pull_tracks_index_slice(penv, monkeypatch):
    import pipeline.config.loaders as loaders
    idx = {"by_state": {"UT": {"matched": [{"url": "u1"}]}}}
    monkeypatch.setattr(loaders, "load_profession_index", lambda prof: idx)
    monkeypatch.setattr(loaders, "matched_for", lambda index, st: index["by_state"].get(st, {}).get("matched"))
    _wr(penv["text"] / "x" / "UT.json", {"sections": [1]})
    pv.record("pull", "x", "UT")
    assert pv.check("pull", "x", "UT") == "current"
    # remapping the state's chapter urls flips pull stale
    idx["by_state"]["UT"]["matched"] = [{"url": "u2"}]
    assert pv.check("pull", "x", "UT") == "stale"


def test_record_returns_stamp_path(env):
    """record() returns the stamp file it wrote, so a git-committing caller (refresh_item)
    can commit the stamp alongside its output."""
    _write(env["text"], "x", "UT", {"sections": [1]})
    _write(env["clean"], "x", "UT", {"sections": ["a"]})
    p = pv.record("clean", "x", "UT")
    assert p == pv._prov_path_for("clean", "x", "UT") and p.exists()


def test_backfill_pull_stamps_every_corpus_cell(penv, monkeypatch):
    """backfill-pull baselines pull-provenance for every committed corpus, skipping a state
    with no index slice and the _summary sidecar — the annual crawl keeps it current after."""
    import pipeline.config.loaders as loaders
    idx = {"by_state": {"UT": {"matched": [{"url": "u1"}]},
                        "CO": {"matched": [{"url": "u2"}]},
                        "ZZ": {"matched": []}}}          # no chapters -> no slice
    monkeypatch.setattr(loaders, "load_profession_index", lambda prof: idx)
    monkeypatch.setattr(loaders, "matched_for", lambda index, st: index["by_state"].get(st, {}).get("matched"))
    for st in ("UT", "CO", "ZZ"):
        _wr(penv["text"] / "x" / f"{st}.json", {"sections": [1]})
    _wr(penv["text"] / "x" / "_summary.json", {"meta": 1})   # underscore sidecar -> skipped
    assert pv._backfill_pull() == 2                          # UT + CO only
    assert pv.check("pull", "x", "UT") == "current"
    assert pv.check("pull", "x", "CO") == "current"
    assert pv.check("pull", "x", "ZZ") == "unstamped"        # skipped, no slice to key on


# --- freshness must not key on a NON-DETERMINISTIC stage's output (2026-07-28) -------
# `extract`'s input hash used to be the hash of `trimmed/`. trim is an LLM stage, so
# re-running it reshuffles which sections it keeps even when the corpus is byte-identical
# (dentistry/IN: +53 / -62 on a re-trim of unchanged law). Every reshuffle invalidated the
# extract, so "stale" came to mean "an LLM stage churned" rather than "the law changed":
# 28% of published cells read stale, implying ~214 re-extractions (~$32), when only ~15
# had had their corpus change at all.

def test_retrimming_unchanged_law_does_not_invalidate_extract(env):
    """The whole point: trim RUNNING again is not a reason to re-extract."""
    _write(env["text"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["clean"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["trim"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["struct"], "p", "UT", {"field": 1})
    pv.record("extract", "p", "UT")
    assert pv.check("extract", "p", "UT") == "current"

    # trim re-runs and picks a different (equally valid) subset — corpus untouched
    _write(env["trim"], "p", "UT", {"sections": [{"text": "the law"}, {"text": "extra"}]})
    assert pv.check("extract", "p", "UT") == "current"


def test_changed_law_still_invalidates_extract(env):
    """...but a real corpus change must still propagate."""
    _write(env["text"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["clean"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["trim"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["struct"], "p", "UT", {"field": 1})
    pv.record("extract", "p", "UT")
    assert pv.check("extract", "p", "UT") == "current"

    _write(env["clean"], "p", "UT", {"sections": [{"text": "the law, AMENDED"}]})
    assert pv.check("extract", "p", "UT") == "stale"


def test_changing_trims_recipe_still_invalidates_extract(env, monkeypatch):
    """Crossing a non-deterministic stage folds in its RECIPE, so a prompt/model/code
    change to trim reaches extract even though trim's output is not the key."""
    _write(env["text"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["clean"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["trim"], "p", "UT", {"sections": [{"text": "the law"}]})
    _write(env["struct"], "p", "UT", {"field": 1})
    pv.record("extract", "p", "UT")
    assert pv.check("extract", "p", "UT") == "current"

    monkeypatch.setitem(pv.CODE_VERSION, "trim", pv.CODE_VERSION["trim"] + 1)
    pv.recipe_hash.cache_clear()
    assert pv.check("extract", "p", "UT") == "stale"


def test_trim_still_keys_on_cleans_output(env):
    """clean is deterministic, so trim keys on it directly — no walk-back, no recipes."""
    _write(env["text"], "p", "UT", {"sections": [{"text": "raw"}]})
    _write(env["clean"], "p", "UT", {"sections": [{"text": "cleaned"}]})
    _write(env["trim"], "p", "UT", {"sections": [{"text": "cleaned"}]})
    pv.record("trim", "p", "UT")
    assert pv.check("trim", "p", "UT") == "current"
    _write(env["clean"], "p", "UT", {"sections": [{"text": "cleaned DIFFERENTLY"}]})
    assert pv.check("trim", "p", "UT") == "stale"
