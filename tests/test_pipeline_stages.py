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
    Tests set fresh_map / states per case."""
    calls: list[tuple[str, str, str | None]] = []
    fresh_map: dict[tuple[str, str, str | None], str] = {}

    def make(name):
        def fn(prof, state, opts):
            calls.append((name, prof, state))
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
    # full ordered prefix; cell stages fan over both states, profession stages run once.
    # pull leads (it raises in real life — the reason refresh_all uses run_upstream=False).
    assert stages_run == ["pull", "pull", "clean", "clean", "trim", "trim", "schema",
                          "extract", "extract", "mapprep", "publish"]
    assert res["ok"] is True


def test_run_to_skips_current_units(rec):
    # clean is current for UT only → clean runs for ID alone; everything else missing → runs
    rec["fresh"][("clean", "med", "UT")] = "current"
    ps.run_to("publish", "med", yes=True)
    clean_states = [c[2] for c in rec["calls"] if c[0] == "clean"]
    assert clean_states == ["ID"]  # UT skipped as current


def test_force_reruns_current_units(rec):
    rec["fresh"][("clean", "med", "UT")] = "current"
    ps.run_to("clean", "med", yes=True, force=True)
    clean_states = sorted(c[2] for c in rec["calls"] if c[0] == "clean")
    assert clean_states == ["ID", "UT"]  # force ignores current


def test_run_upstream_false_runs_only_target(rec):
    res = ps.run_to("publish", "med", yes=True, run_upstream=False)
    assert [c[0] for c in rec["calls"]] == ["publish"]  # no upstream
    assert res["ok"] is True


def test_dry_run_records_plan_but_runs_nothing(rec):
    res = ps.run_to("publish", "med", dry_run=True)
    assert rec["calls"] == []                    # nothing executed
    assert [name for name, _ in res["plan"]] == ["pull", "clean", "trim", "schema", "extract", "mapprep", "publish"]


def test_failed_stage_halts_chain(rec):
    res = ps.run_to("publish", "med", yes=True, opts={"_fail": "trim"})
    stages_run = [c[0] for c in rec["calls"]]
    assert "trim" in stages_run and "schema" not in stages_run  # stopped at the failure
    assert res["ok"] is False


# --- the cost gate ------------------------------------------------------------

def test_confirm_if_paid_free_stage_never_prompts(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: pytest.fail("must not prompt for a free stage"))
    ps.confirm_if_paid("publish", 5, yes=False)   # publish has no cost → returns silently


def test_confirm_if_paid_paid_stage_aborts_on_no(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: "no")
    with pytest.raises(SystemExit):
        ps.confirm_if_paid("extract", 3, yes=False)


def test_confirm_if_paid_yes_flag_skips_prompt(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda *_: pytest.fail("must not prompt with yes=True"))
    ps.confirm_if_paid("extract", 3, yes=True)    # --yes → no prompt


def test_paid_stage_hits_cost_gate_before_running(rec, monkeypatch):
    """A paid upstream stage (extract) must reach confirm_if_paid before its run_fn — money
    can't leak past the gate."""
    gate_hits: list[tuple[str, int]] = []
    monkeypatch.setattr(ps, "confirm_if_paid",
                        lambda stage, n, yes: gate_hits.append((stage, n)))
    ps.run_to("extract", "med", yes=True)
    assert ("extract", 2) in gate_hits            # both states gated together, once
