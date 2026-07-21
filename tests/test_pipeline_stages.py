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

def test_pull_adapter_flags_bad_delegates_stamping(monkeypatch):
    """_pull maps refresh_item results: OK/NOCHANGE → healthy; anything else → failure. All
    states are attempted (one bad cell doesn't abort the rest). Pull-provenance stamping now
    lives in refresh_item (folded into its OK commit), so the adapter itself never stamps."""
    results = {"UT": "OK", "ID": "NOCHANGE", "MT": "REGRESSION"}
    import pipeline.ingest.refresh_corpus as rc
    monkeypatch.setattr(rc, "build_worklist",
                        lambda profs, states: [(profs[0], s, [{"chapter_url": "u"}]) for s in sorted(states)])
    monkeypatch.setattr(rc, "refresh_item",
                        lambda p, s, rows, **k: {"result": results[s], "reason": ""})
    stamped = []
    monkeypatch.setattr(ps.provenance, "record", lambda stage, p, s=None: stamped.append((stage, p, s)))
    ok = ps._pull("med", ["UT", "ID", "MT"], {})
    assert ok is False            # MT regressed → overall failure
    assert stamped == []          # adapter delegates stamping to refresh_item


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


# --- adapter command wiring (the run_fn bodies the recorder tests bypass) ------
# These assert the exact subprocess commands the adapters emit — a wrong module name
# or flag here passes every recorder-based test above and only fails at runtime.

def _mods(cmds):
    """The `python -m X` module name from each recorded command list."""
    return [c[c.index("-m") + 1] for c in cmds if "-m" in c]


def test_clean_adapter_joins_states(monkeypatch):
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    ps._clean("optometry", ["UT", "ID"], {})
    assert _mods(cmds) == ["pipeline.ingest.clean_text"]
    c = cmds[0]
    assert c[c.index("--profession") + 1] == "optometry"
    assert c[c.index("--states") + 1] == "UT,ID"       # one grouped call, comma-joined


def test_trim_adapter_passes_strict(monkeypatch):
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    ps._trim("optometry", ["UT"], {"strict": True})
    assert _mods(cmds) == ["pipeline.ingest.trim_state"]
    assert "--strict" in cmds[0]
    cmds.clear()
    ps._trim("optometry", ["UT"], {})
    assert "--strict" not in cmds[0]


def test_mapprep_adapter_runs_run_then_bucket_text(monkeypatch):
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    assert ps._mapprep("optometry", None, {}) is True
    assert _mods(cmds) == ["pipeline.map_prep.run", "pipeline.map_prep.bucket_text"]


def test_mapprep_adapter_stops_if_run_fails(monkeypatch):
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or ("map_prep.run" not in " ".join(cmd)))
    assert ps._mapprep("optometry", None, {}) is False
    assert _mods(cmds) == ["pipeline.map_prep.run"]     # bucket_text NOT reached


def test_publish_adapter_gates_then_builds_then_stamps(monkeypatch):
    cmds, stamped = [], []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    monkeypatch.setattr(ps, "_consistency_violations", lambda prof: [])
    monkeypatch.setattr(ps.provenance, "record", lambda stage, p, s=None: stamped.append((stage, p)))
    assert ps._publish("optometry", None, {}) is True
    assert _mods(cmds) == ["pipeline.publish.build_frontend"]
    assert stamped == [("publish", "optometry")]        # publish stamped current on success


def test_publish_adapter_blocks_on_consistency_violation(monkeypatch):
    cmds, stamped = [], []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    monkeypatch.setattr(ps, "_consistency_violations",
                        lambda prof: [{"profession": prof, "state": "UT", "rule": "r", "detail": "d"}])
    monkeypatch.setattr(ps.provenance, "record", lambda *a, **k: stamped.append(a))
    assert ps._publish("optometry", None, {}) is False
    assert cmds == [] and stamped == []                 # never built, never stamped


def test_publish_adapter_payload_only_does_not_stamp(monkeypatch):
    cmds, stamped = [], []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    monkeypatch.setattr(ps, "_consistency_violations", lambda prof: [])
    monkeypatch.setattr(ps.provenance, "record", lambda *a, **k: stamped.append(a))
    assert ps._publish("optometry", None, {"payload_only": True}) is True
    assert "--payload-only" in cmds[0]
    assert stamped == []                                # incomplete output → NOT stamped current


def test_fanout_full_runs_all_stages(monkeypatch):
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    ps.run_fanout(["a", "b"], payload_only=False)
    mods = _mods(cmds)
    for m in ("pipeline.publish.generate_field_dictionary", "pipeline.analyze.similarity",
              "pipeline.analyze.classify_novel_direction", "pipeline.analyze.publish_analysis",
              "pipeline.publish.build_tag_sheet", "pipeline.publish.build_scope_capabilities",
              "pipeline.publish.cross_comparison_scorecard", "pipeline.publish.build_state_browse",
              "pipeline.publish.build_umbrella_browse"):
        assert m in mods, f"{m} missing from fanout"


def test_fanout_payload_only_skips_the_slow_browse_stages(monkeypatch):
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    ps.run_fanout(["a"], payload_only=True)
    mods = _mods(cmds)
    for skipped in ("pipeline.publish.cross_comparison_scorecard",
                    "pipeline.publish.build_state_browse", "pipeline.publish.build_umbrella_browse"):
        assert skipped not in mods                      # the CPU-hog stages are skipped
    assert "pipeline.publish.build_tag_sheet" in mods   # ...but the tag sheet still refreshes
