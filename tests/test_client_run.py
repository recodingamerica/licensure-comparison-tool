"""Tests for pipeline.client.run — queue validation and the paid-step cost gate.
The subprocess/batch orchestration itself is exercised manually; here we lock down
the pure logic that decides what runs and whether money gets spent."""

import builtins

import pytest

from pipeline.client import run


# --- _load_queue --------------------------------------------------------------

def test_load_queue_good(tmp_path):
    p = tmp_path / "q.json"
    p.write_text('{"court_reporter": ["UT", "ID"]}')
    assert run._load_queue(str(p)) == {"court_reporter": ["UT", "ID"]}


def test_load_queue_drops_empty_state_lists(tmp_path):
    p = tmp_path / "q.json"
    p.write_text('{"a": ["UT"], "b": []}')
    assert run._load_queue(str(p)) == {"a": ["UT"]}


def test_load_queue_missing_file_exits(tmp_path):
    with pytest.raises(SystemExit):
        run._load_queue(str(tmp_path / "nope.json"))


def test_load_queue_bad_json_exits(tmp_path):
    p = tmp_path / "q.json"
    p.write_text("{not valid json")
    with pytest.raises(SystemExit):
        run._load_queue(str(p))


def test_load_queue_wrong_shape_exits(tmp_path):
    p = tmp_path / "q.json"
    p.write_text('{"a": "UT"}')  # value must be a list
    with pytest.raises(SystemExit):
        run._load_queue(str(p))


def test_load_queue_all_empty_exits(tmp_path):
    p = tmp_path / "q.json"
    p.write_text('{"a": []}')
    with pytest.raises(SystemExit):
        run._load_queue(str(p))


def test_cells_counts_states():
    assert run._cells({"a": ["UT", "ID"], "b": ["CA"]}) == 3


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

def test_confirm_yes_flag_skips_prompt(monkeypatch):
    seen = {"prompted": False}
    monkeypatch.setattr(builtins, "input",
                        lambda *_: seen.__setitem__("prompted", True) or "no")
    run._confirm("trim", {"a": ["UT"]}, 0.05, yes=True)
    assert seen["prompted"] is False  # --yes must not prompt


def test_confirm_aborts_on_no(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    with pytest.raises(SystemExit):
        run._confirm("trim", {"a": ["UT"]}, 0.05, yes=False)


def test_confirm_aborts_on_empty(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "")
    with pytest.raises(SystemExit):
        run._confirm("trim", {"a": ["UT"]}, 0.05, yes=False)


def test_confirm_proceeds_on_yes(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "  YES  ")  # case/space tolerant
    run._confirm("trim", {"a": ["UT"]}, 0.05, yes=False)  # returns without raising


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
