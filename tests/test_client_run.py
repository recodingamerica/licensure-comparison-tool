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


# --- _drop_current (the re-charge guard) --------------------------------------

def test_drop_current_skips_only_current_cells(monkeypatch):
    """A re-run after a partial failure must not re-charge for cells already current;
    stale/unstamped/missing cells are kept."""
    fresh = {("a", "UT"): "current", ("a", "ID"): "missing",
             ("b", "CA"): "current", ("b", "NV"): "stale"}
    monkeypatch.setattr(run.provenance, "check", lambda stage, p, s: fresh[(p, s)])
    kept, skipped = run._drop_current("trim", {"a": ["UT", "ID"], "b": ["CA", "NV"]})
    assert kept == {"a": ["ID"], "b": ["NV"]}
    assert set(skipped) == {("a", "UT"), ("b", "CA")}


def test_drop_current_all_current_yields_empty_queue(monkeypatch):
    monkeypatch.setattr(run.provenance, "check", lambda stage, p, s: "current")
    kept, skipped = run._drop_current("extract", {"a": ["UT", "ID"]})
    assert kept == {} and set(skipped) == {("a", "UT"), ("a", "ID")}


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


# --- _confirm (the cost gate) -------------------------------------------------

def test_confirm_names_the_model(monkeypatch, capsys):
    """The printed estimate must name the model it's priced against — the cost is an
    Anthropic rate for that model, not a fixed cost of the step."""
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    with pytest.raises(SystemExit):
        run._confirm("trim", {"a": ["UT"]}, 0.05, "claude-haiku-4-5-20251001", yes=False)
    assert "claude-haiku-4-5-20251001" in capsys.readouterr().out


def test_confirm_yes_flag_skips_prompt(monkeypatch):
    seen = {"prompted": False}
    monkeypatch.setattr(builtins, "input",
                        lambda *_: seen.__setitem__("prompted", True) or "no")
    run._confirm("trim", {"a": ["UT"]}, 0.05, "claude-haiku-4-5-20251001", yes=True)
    assert seen["prompted"] is False  # --yes must not prompt


def test_confirm_aborts_on_no(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    with pytest.raises(SystemExit):
        run._confirm("trim", {"a": ["UT"]}, 0.05, "claude-haiku-4-5-20251001", yes=False)


def test_confirm_aborts_on_empty(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "")
    with pytest.raises(SystemExit):
        run._confirm("trim", {"a": ["UT"]}, 0.05, "claude-haiku-4-5-20251001", yes=False)


def test_confirm_proceeds_on_yes(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "  YES  ")  # case/space tolerant
    run._confirm("trim", {"a": ["UT"]}, 0.05, "claude-haiku-4-5-20251001", yes=False)  # no raise


# --- publish (per-occupation, not per-cell) -----------------------------------

def test_publish_requires_professions():
    import argparse
    with pytest.raises(SystemExit):
        run.cmd_publish(argparse.Namespace(professions="", deploy=False))


def test_publish_runs_build_frontend_per_profession(monkeypatch):
    calls = []
    monkeypatch.setattr(run.subprocess, "run",
                        lambda cmd, **k: calls.append(cmd) or type("R", (), {"returncode": 0})())
    import argparse
    run.cmd_publish(argparse.Namespace(professions="dentistry, podiatry", deploy=False, yes=False))
    profs = [c[c.index("--profession") + 1] for c in calls]
    assert profs == ["dentistry", "podiatry"]
    assert all(any("build_frontend" in part for part in c) for c in calls)


def test_publish_deploy_aborts_without_typed_yes(monkeypatch):
    calls = []
    monkeypatch.setattr(run.subprocess, "run",
                        lambda cmd, **k: calls.append(cmd) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    import argparse
    with pytest.raises(SystemExit):
        run.cmd_publish(argparse.Namespace(professions="dentistry", deploy=True, yes=False))
    assert calls == []  # nothing built or deployed when the deploy gate is declined


def test_publish_deploy_yes_flag_skips_prompt_and_passes_deploy(monkeypatch):
    calls = []
    monkeypatch.setattr(run.subprocess, "run",
                        lambda cmd, **k: calls.append(cmd) or type("R", (), {"returncode": 0})())
    prompted = {"asked": False}
    monkeypatch.setattr(builtins, "input",
                        lambda *_: prompted.__setitem__("asked", True) or "no")
    import argparse
    run.cmd_publish(argparse.Namespace(professions="dentistry", deploy=True, yes=True))
    assert prompted["asked"] is False           # --yes must not prompt
    assert any("--deploy" in c for c in calls)   # deploy flag threaded to build_frontend
