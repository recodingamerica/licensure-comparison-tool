"""Tests for pipeline.client.run — queue building from live status and the
paid-step cost gate. The subprocess/batch orchestration itself is exercised
manually; here we lock down the pure logic that decides what runs and whether
money gets spent."""

import builtins

import pytest

from pipeline.client import run


# --- _queue_for_professions (replaces the old downloaded-file queue) ----------

def _fake_status(professions):
    """professions: {name: {state: run_bool}}"""
    return {"professions": {
        name: {"states": {st: {"run": r} for st, r in states.items()}}
        for name, states in professions.items()
    }}


def test_queue_for_professions_includes_only_runnable_states(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_status(
        {"court_reporter": {"UT": True, "ID": False, "MT": True}}))
    assert run._queue_for_professions(["court_reporter"]) == {"court_reporter": ["UT", "MT"]}


def test_queue_for_professions_unknown_profession_exits(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_status({"a": {"UT": True}}))
    with pytest.raises(SystemExit):
        run._queue_for_professions(["not_a_real_profession"])


def test_queue_for_professions_all_non_runnable_exits(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_status(
        {"a": {"UT": False, "ID": False}}))
    with pytest.raises(SystemExit):
        run._queue_for_professions(["a"])


def test_queue_for_professions_skips_profession_with_nothing_runnable(monkeypatch, capsys):
    # "a" has work, "b" doesn't — "b" is dropped with a note, not a hard failure,
    # since "a" alone still makes the queue non-empty.
    monkeypatch.setattr(run, "build_status", lambda: _fake_status(
        {"a": {"UT": True}, "b": {"CA": False}}))
    queue = run._queue_for_professions(["a", "b"])
    assert queue == {"a": ["UT"]}
    assert "b" in capsys.readouterr().out


# --- _queue_by_stage (clean/trim — schema-independent) ------------------------

def _fake_stage_status(professions):
    """professions: {name: {state: (stage, fresh_or_None)}}"""
    return {"professions": {
        name: {"states": {
            st: {"stage": stage, **({"fresh": fresh} if fresh else {})}
            for st, (stage, fresh) in states.items()
        }}
        for name, states in professions.items()
    }}


def test_queue_by_stage_includes_matching_stages_only(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_stage_status(
        {"a": {"UT": ("pulled", None), "ID": ("done", "current"), "MT": ("cleaned", None)}}))
    queue = run._queue_by_stage(["a"], {"pulled", "cleaned"})
    assert queue == {"a": ["UT", "MT"]}


def test_queue_by_stage_includes_stale_done_cells_regardless_of_stage_set(monkeypatch):
    # A stale "done" cell needs the whole chain re-run, even though its stage is
    # "done" and "done" isn't in the requested stage set.
    monkeypatch.setattr(run, "build_status", lambda: _fake_stage_status(
        {"a": {"UT": ("done", "stale")}}))
    queue = run._queue_by_stage(["a"], {"pulled", "cleaned", "trimmed"})
    assert queue == {"a": ["UT"]}


def test_queue_by_stage_schema_less_profession_still_included(monkeypatch):
    # The whole point: an occupation with no schema yet (which _queue_for_professions
    # would exclude via cell["run"]) must still be reachable for clean/trim.
    monkeypatch.setattr(run, "build_status", lambda: _fake_stage_status(
        {"a": {"UT": ("cleaned", None)}}))
    queue = run._queue_by_stage(["a"], {"pulled", "cleaned", "trimmed"})
    assert queue == {"a": ["UT"]}


def test_queue_by_stage_unknown_profession_exits(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_stage_status({"a": {"UT": ("pulled", None)}}))
    with pytest.raises(SystemExit):
        run._queue_by_stage(["not_a_real_profession"], {"pulled"})


def test_queue_by_stage_all_non_matching_exits(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_stage_status(
        {"a": {"UT": ("done", "current")}}))
    with pytest.raises(SystemExit):
        run._queue_by_stage(["a"], {"pulled", "cleaned", "trimmed"})


def test_cells_counts_states():
    assert run._cells({"a": ["UT", "ID"], "b": ["CA"]}) == 3


# --- _professions_needing_schema (occupation-level, not per-cell) -------------

def _fake_schema_status(professions):
    """professions: {name: (has_schema, cost_schema)}"""
    return {"professions": {
        name: {"summary": {"has_schema": hs, "cost_schema": cs}}
        for name, (hs, cs) in professions.items()
    }}


def test_professions_needing_schema_includes_only_those_with_cost(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_schema_status(
        {"a": (False, 1.0), "b": (True, 0.0)}))
    assert run._professions_needing_schema(["a", "b"]) == ["a"]


def test_professions_needing_schema_unknown_profession_exits(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_schema_status({"a": (False, 1.0)}))
    with pytest.raises(SystemExit):
        run._professions_needing_schema(["not_a_real_profession"])


def test_professions_needing_schema_all_already_have_one_exits(monkeypatch):
    monkeypatch.setattr(run, "build_status", lambda: _fake_schema_status({"a": (True, 0.0)}))
    with pytest.raises(SystemExit):
        run._professions_needing_schema(["a"])


def test_professions_needing_schema_no_corpus_yet_exits(monkeypatch):
    # has_schema False AND cost_schema 0 -> no corpus pulled yet, nothing to discover from.
    monkeypatch.setattr(run, "build_status", lambda: _fake_schema_status({"a": (False, 0.0)}))
    with pytest.raises(SystemExit):
        run._professions_needing_schema(["a"])


# NB: the re-charge guard (drop_current) and the cost gate (confirm_if_paid) now live in
# pipeline.pipeline_stages and are tested in tests/test_pipeline_stages.py.


# --- _report_extract (never a blanket 'done') ---------------------------------

def test_report_extract_reports_partial_failure(capsys):
    result = {"written": [{"profession": "a", "state": "UT"}],
              "errored": [{"custom_id": "a__ID", "reason": "parse_or_validate_failed"}]}
    run._report_extract(requested=2, result=result, batch_id="b1")
    out = capsys.readouterr().out
    assert "1 of 2" in out and "a__ID" in out and "1 failed" in out


def test_report_extract_flags_preflight_dropped(capsys):
    # requested 3, but only 1 written + 0 errored => 2 were never submitted (preflight)
    run._report_extract(requested=3, result={"written": [{}], "errored": []}, batch_id="b1")
    out = capsys.readouterr().out
    assert "2 state(s) were not submitted" in out


def test_report_extract_handles_unfinished_batch(capsys):
    run._report_extract(requested=2, result=None, batch_id="b9")
    out = capsys.readouterr().out
    assert "not finished" in out and "b9" in out


# --- publish (per-occupation, not per-cell) -----------------------------------

def test_publish_requires_professions():
    import argparse
    with pytest.raises(SystemExit):
        run.cmd_publish(argparse.Namespace(professions="", deploy=False))


def test_publish_runs_build_frontend_per_profession(monkeypatch):
    built = []
    monkeypatch.setattr(run, "run_to", lambda target, prof, **k: built.append((target, prof)) or {"ok": True})
    import argparse
    run.cmd_publish(argparse.Namespace(professions="dentistry, podiatry", deploy=False, yes=False))
    assert built == [("publish", "dentistry"), ("publish", "podiatry")]  # publish adapter, each prof


def test_publish_deploy_aborts_without_typed_yes(monkeypatch):
    called = {"run_to": 0, "sh": 0}
    monkeypatch.setattr(run, "run_to", lambda *a, **k: called.__setitem__("run_to", called["run_to"] + 1) or {"ok": True})
    monkeypatch.setattr(run, "_sh", lambda *a, **k: called.__setitem__("sh", called["sh"] + 1) or True)
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    import argparse
    with pytest.raises(SystemExit):
        run.cmd_publish(argparse.Namespace(professions="dentistry", deploy=True, yes=False, all=False))
    assert called == {"run_to": 0, "sh": 0}  # nothing built or deployed when the deploy gate is declined


def test_publish_deploy_yes_builds_then_deploys_once(monkeypatch):
    built, deploys = [], []
    monkeypatch.setattr(run, "run_to", lambda target, prof, **k: built.append(prof) or {"ok": True})
    # fanout (cross-profession rebuild before the single deploy) is exercised in
    # pipeline_stages' own tests; stub it here so this test stays about the deploy gating.
    monkeypatch.setattr(run, "run_fanout", lambda profs, **k: [("fanout", True)])
    monkeypatch.setattr(run, "_sh", lambda cmd, label, **k: deploys.append(cmd) or True)
    prompted = {"asked": False}
    monkeypatch.setattr(builtins, "input",
                        lambda *_: prompted.__setitem__("asked", True) or "no")
    import argparse
    run.cmd_publish(argparse.Namespace(professions="dentistry,nursing", deploy=True, yes=True, all=False))
    assert prompted["asked"] is False                                    # --yes must not prompt
    assert built == ["dentistry", "nursing"]                             # each profession published, in order
    assert len(deploys) == 1 and "--prod" in " ".join(deploys[0])        # ONE vercel deploy at the end


# --- extract backend routing (claude batch vs litellm) ------------------------

def _extract_args(backend, model=None):
    import argparse
    return argparse.Namespace(redo=True, force=False, yes=True, backend=backend, model=model)


def test_cmd_extract_default_backend_submits_anthropic_batch(monkeypatch):
    """Default backend keeps the discounted Anthropic Message Batches path."""
    from pipeline.extract import extract_state_batch as esb
    seen = {"submit": 0, "litellm": 0, "model": None}
    monkeypatch.setattr(esb, "submit",
                        lambda queue, model, force: seen.__setitem__("submit", seen["submit"] + 1)
                        or seen.__setitem__("model", model) or {"batch_id": "b1"})
    monkeypatch.setattr(esb, "poll", lambda bid, wait: {"written": [], "errored": []})
    monkeypatch.setattr(esb, "run_litellm",
                        lambda *a, **k: seen.__setitem__("litellm", seen["litellm"] + 1))
    run.cmd_extract({"a": ["UT"]}, _extract_args("claude"))
    assert seen["submit"] == 1 and seen["litellm"] == 0
    assert isinstance(seen["model"], str) and seen["model"]  # defaulted to a real model, not None


def test_cmd_extract_litellm_backend_routes_to_run_litellm(monkeypatch):
    """--backend litellm runs the vendor-neutral path with the chosen model, never submit()."""
    from pipeline.extract import extract_state_batch as esb
    seen = {"submit": 0, "litellm": 0, "model": None}
    monkeypatch.setattr(esb, "run_litellm",
                        lambda queue, model, force: seen.__setitem__("litellm", seen["litellm"] + 1)
                        or seen.__setitem__("model", model)
                        or {"batch_id": "litellm-x", "written": [{"profession": "a", "state": "UT"}], "errored": []})
    monkeypatch.setattr(esb, "submit",
                        lambda *a, **k: seen.__setitem__("submit", seen["submit"] + 1))
    run.cmd_extract({"a": ["UT"]}, _extract_args("litellm", model="gpt-5"))
    assert seen["litellm"] == 1 and seen["submit"] == 0
    assert seen["model"] == "gpt-5"


# --- publish: skip-unchanged + parallel (2026-07-29) --------------------------------
# The build loop passed force=True, so every invocation rebuilt all 13 payloads even when
# one occupation had moved — ~90 minutes of wall clock, serial, for a one-cell change.

def _ns(**kw):
    import argparse
    base = dict(professions="dentistry, podiatry", deploy=False, yes=False,
                all=False, force=False, jobs=4)
    base.update(kw)
    return argparse.Namespace(**base)


def test_publish_skips_occupations_provenance_calls_current(monkeypatch):
    built = []
    monkeypatch.setattr(run, "run_to", lambda target, prof, **k: built.append(prof) or {"ok": True})
    monkeypatch.setattr(run.provenance, "check",
                        lambda stage, prof, state=None: "current" if prof == "dentistry" else "stale")
    run.cmd_publish(_ns())
    assert built == ["podiatry"], "an unchanged occupation must not pay for a rebuild"


def test_publish_force_rebuilds_everything(monkeypatch):
    built = []
    monkeypatch.setattr(run, "run_to", lambda target, prof, **k: built.append(prof) or {"ok": True})
    monkeypatch.setattr(run.provenance, "check", lambda *a, **k: "current")
    run.cmd_publish(_ns(force=True))
    assert sorted(built) == ["dentistry", "podiatry"]


def test_publish_builds_in_parallel(monkeypatch):
    """All payloads are submitted to the pool, not run one-after-another."""
    import threading
    seen, lock = [], threading.Lock()

    def fake(target, prof, **k):
        with lock:
            seen.append(prof)
        return {"ok": True}

    monkeypatch.setattr(run, "run_to", fake)
    monkeypatch.setattr(run.provenance, "check", lambda *a, **k: "stale")
    run.cmd_publish(_ns(professions="a,b,c,d", jobs=4))
    assert sorted(seen) == ["a", "b", "c", "d"]


def test_publish_does_not_deploy_when_a_payload_fails(monkeypatch):
    """A partial rebuild must never ship — half the site fresh, half stale is the exact
    inconsistency this command exists to prevent."""
    monkeypatch.setattr(run, "run_to",
                        lambda target, prof, **k: {"ok": prof != "podiatry"})
    monkeypatch.setattr(run.provenance, "check", lambda *a, **k: "stale")
    deployed = []
    monkeypatch.setattr(run, "_sh", lambda *a, **k: deployed.append(a) or True)
    with pytest.raises(SystemExit):
        run.cmd_publish(_ns(deploy=True, yes=True))
    assert deployed == []
