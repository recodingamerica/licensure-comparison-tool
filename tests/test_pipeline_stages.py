"""Tests for pipeline.pipeline_stages — the declarative stage table + run_to runner.

Every stage's run_fn is monkeypatched to a recorder so no real engine/LLM/subprocess
runs; we assert on ORDER, freshness-gated selection, the paid cost gate, and that
dry-run / run_upstream behave.
"""
import builtins

import pytest

import pipeline.pipeline_stages as ps


@pytest.fixture
def rec(monkeypatch):
    """Replace every stage's run_fn with a recorder, and stub freshness + state discovery.
    Each recorded call is (stage, prof, unit) where unit is the states LIST for cell stages
    (one grouped dispatch per profession) or None for profession stages."""
    calls: list[tuple[str, str, object]] = []
    fresh_map: dict[tuple[str, str, str | None], str] = {}

    def make(name):
        def fn(prof, unit, opts):
            calls.append((name, prof, unit))
            return opts.get("_fail") != name  # let a test force a stage to fail
        return fn

    patched = tuple(
        ps.Stage(s.name, s.scope, make(s.name), s.cost_stage) if s.scope != "global" else s
        for s in ps.STAGES
    )
    monkeypatch.setattr(ps, "STAGES", patched)
    monkeypatch.setattr(ps, "_BY_NAME", {s.name: s for s in patched})
    monkeypatch.setattr(ps, "_ORDER", {s.name: i for i, s in enumerate(patched)})
    monkeypatch.setattr(ps.provenance, "check", lambda stage, p, s=None: fresh_map.get((stage, p, s), "missing"))
    monkeypatch.setattr(ps, "_states_for", lambda prof: ["UT", "ID"])
    return {"calls": calls, "fresh": fresh_map}


def test_run_to_walks_prefix_in_order(rec):
    res = ps.run_to("publish", "med", yes=True)
    stages_run = [c[0] for c in rec["calls"]]
    # full ordered prefix, ONE dispatch per stage (cell stages grouped over all states).
    # pull leads (it raises in real life — the reason refresh_all/add_occupation don't start there).
    assert stages_run == ["pull", "clean", "trim", "schema", "extract", "mapprep", "publish"]
    assert res["ok"] is True


def test_run_to_skips_current_units(rec):
    # clean is current for UT only → clean's one dispatch carries ID alone
    rec["fresh"][("clean", "med", "UT")] = "current"
    ps.run_to("publish", "med", yes=True)
    clean_units = [c[2] for c in rec["calls"] if c[0] == "clean"]
    assert clean_units == [["ID"]]  # UT dropped as current, single grouped call


def test_force_reruns_current_units(rec):
    rec["fresh"][("clean", "med", "UT")] = "current"
    ps.run_to("clean", "med", yes=True, force=True)
    clean_units = [c[2] for c in rec["calls"] if c[0] == "clean"]
    assert clean_units == [["UT", "ID"]]  # force ignores current, all states in one call


def test_start_at_target_runs_only_target(rec):
    res = ps.run_to("publish", "med", yes=True, start="publish")
    assert [c[0] for c in rec["calls"]] == ["publish"]  # no upstream
    assert res["ok"] is True


def test_start_at_clean_skips_pull(rec):
    ps.run_to("publish", "med", yes=True, start="clean")
    assert "pull" not in [c[0] for c in rec["calls"]]     # no-pull chain
    assert [c[0] for c in rec["calls"]][0] == "clean"


def test_start_after_target_raises(rec):
    with pytest.raises(ValueError):
        ps.run_to("clean", "med", start="publish")


def test_dry_run_records_plan_but_runs_nothing(rec):
    res = ps.run_to("publish", "med", dry_run=True)
    assert rec["calls"] == []                    # nothing executed
    assert [name for name, _ in res["plan"]] == ["pull", "clean", "trim", "schema", "extract", "mapprep", "publish"]


def test_failed_stage_halts_chain(rec):
    res = ps.run_to("publish", "med", yes=True, opts={"_fail": "trim"})
    stages_run = [c[0] for c in rec["calls"]]
    assert "trim" in stages_run and "schema" not in stages_run  # stopped at the failure
    assert res["ok"] is False


# --- the pull adapter (safe path over refresh_item) ---------------------------

def test_pull_adapter_stamps_healthy_and_flags_bad(monkeypatch):
    """_pull maps refresh_item results: OK/NOCHANGE → healthy (stamped current); anything
    else → failure. All states are attempted (one bad cell doesn't abort the rest)."""
    results = {"UT": "OK", "ID": "NOCHANGE", "MT": "REGRESSION"}
    monkeypatch.setattr(ps, "_pull", ps._pull)  # ensure real adapter
    import pipeline.ingest.refresh_corpus as rc
    monkeypatch.setattr(rc, "build_worklist",
                        lambda profs, states: [(profs[0], s, [{"chapter_url": "u"}]) for s in sorted(states)])
    monkeypatch.setattr(rc, "refresh_item",
                        lambda p, s, rows, **k: {"result": results[s], "reason": ""})
    stamped = []
    monkeypatch.setattr(ps.provenance, "record", lambda stage, p, s=None: stamped.append((stage, p, s)))
    ok = ps._pull("med", ["UT", "ID", "MT"], {})
    assert ok is False                                    # MT regressed → overall failure
    assert set(stamped) == {("pull", "med", "UT"), ("pull", "med", "ID")}  # only healthy cells stamped


# --- the cost gate ------------------------------------------------------------

def test_confirm_if_paid_free_stage_never_prompts(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: pytest.fail("must not prompt for a free stage"))
    ps.confirm_if_paid("publish", 5, yes=False)   # publish has no cost → returns silently


def test_confirm_if_paid_paid_stage_aborts_on_no(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    with pytest.raises(SystemExit):
        ps.confirm_if_paid("extract", 3, yes=False)


def test_confirm_if_paid_aborts_on_empty(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "")
    with pytest.raises(SystemExit):
        ps.confirm_if_paid("trim", 1, yes=False)


def test_confirm_if_paid_proceeds_on_yes_reply(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "  YES  ")   # case/space tolerant
    ps.confirm_if_paid("trim", 1, yes=False)      # no raise


def test_confirm_if_paid_yes_flag_skips_prompt(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: pytest.fail("must not prompt with yes=True"))
    ps.confirm_if_paid("extract", 3, yes=True)    # --yes → no prompt


def test_confirm_if_paid_names_the_model(monkeypatch, capsys):
    """The estimate names the model it's priced against — the cost is an API rate for that
    model, not a fixed cost of the step (so it can't silently go stale)."""
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    with pytest.raises(SystemExit):
        ps.confirm_if_paid("trim", 1, yes=False)
    from pipeline.config.loaders import model_for
    assert model_for("trim") in capsys.readouterr().out


# --- drop_current (the re-charge guard) ---------------------------------------

def test_drop_current_skips_only_current_cells(monkeypatch):
    fresh = {("a", "UT"): "current", ("a", "ID"): "missing",
             ("b", "CA"): "current", ("b", "NV"): "stale"}
    monkeypatch.setattr(ps.provenance, "check", lambda stage, p, s: fresh[(p, s)])
    kept, skipped = ps.drop_current("trim", {"a": ["UT", "ID"], "b": ["CA", "NV"]})
    assert kept == {"a": ["ID"], "b": ["NV"]}
    assert set(skipped) == {("a", "UT"), ("b", "CA")}


def test_drop_current_all_current_yields_empty_queue(monkeypatch):
    monkeypatch.setattr(ps.provenance, "check", lambda stage, p, s: "current")
    kept, skipped = ps.drop_current("extract", {"a": ["UT", "ID"]})
    assert kept == {} and set(skipped) == {("a", "UT"), ("a", "ID")}


def test_paid_stage_hits_cost_gate_before_running(rec, monkeypatch):
    """A paid upstream stage (extract) must reach confirm_if_paid before its run_fn — money
    can't leak past the gate."""
    gate_hits: list[tuple[str, int]] = []
    monkeypatch.setattr(ps, "confirm_if_paid",
                        lambda stage, n, yes: gate_hits.append((stage, n)))
    ps.run_to("extract", "med", yes=True)
    assert ("extract", 2) in gate_hits            # both states gated together, once


def test_no_money_leaks_current_cell_dropped_before_gate(rec, monkeypatch):
    """The core paid-path invariant: a CURRENT cell is dropped BEFORE the cost gate, so the
    gate is quoted (and the engine runs) only for the cells that genuinely need work — a
    re-run after a partial success never re-charges for the finished cell."""
    gate_hits: list[tuple[str, int]] = []
    monkeypatch.setattr(ps, "confirm_if_paid", lambda stage, n, yes: gate_hits.append((stage, n)))
    rec["fresh"][("extract", "med", "UT")] = "current"   # UT already extracted
    rec["fresh"][("extract", "med", "ID")] = "stale"     # ID needs re-extract
    ps.run_to("extract", "med", start="extract", yes=True)
    assert gate_hits == [("extract", 1)]                  # gated for the ONE due cell, not 2
    extract_units = [c[2] for c in rec["calls"] if c[0] == "extract"]
    assert extract_units == [["ID"]]                     # engine never ran for the current UT
