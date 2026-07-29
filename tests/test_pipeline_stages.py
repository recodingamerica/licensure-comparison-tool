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
    assert stages_run == ["pull", "clean", "trim", "schema", "extract", "verify", "mapprep", "publish"]
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


def test_force_on_named_states_does_not_redo_profession_stages(rec):
    """`--force` on ONE state must not re-derive profession-wide artifacts.

    schema is profession-scoped and LLM-derived from a 10-state sample. Forcing a
    single-cell repair used to drag it in, which could leave that one state extracted
    against a field set the other 49 don't share.
    """
    rec["fresh"][("schema", "med", None)] = "current"
    ps.run_to("extract", "med", ["UT"], yes=True, force=True)
    assert [c[0] for c in rec["calls"] if c[0] == "schema"] == []
    # the named cell IS still forced
    assert ["UT"] in [c[2] for c in rec["calls"] if c[0] == "extract"]


def test_force_over_whole_profession_still_redoes_profession_stages(rec):
    """No states named = the whole profession, so profession-wide stages are in scope.
    (schema is the exception — see the derived-once tests below — so assert on verify,
    which follows the normal profession-scope force rule.)"""
    rec["fresh"][("verify", "med", None)] = "current"
    ps.run_to("verify", "med", yes=True, force=True)
    assert [c[0] for c in rec["calls"] if c[0] == "verify"] == ["verify"]


def test_force_with_explicit_schema_target_is_the_escape_hatch(rec):
    """Naming the stage as --target means you asked for it, states notwithstanding."""
    rec["fresh"][("schema", "med", None)] = "current"
    ps.run_to("schema", "med", ["UT"], start="schema", yes=True, force=True)
    assert [c[0] for c in rec["calls"]] == ["schema"]


# --- schema is derived ONCE, never auto-re-derived (2026-07-29) --------------------
# Re-derivation is LLM churn: nursing renamed 26 of its 29 fields on a same-corpus
# re-derive, and every corpus repair flips schema provenance stale — so TWO batches in
# one day extracted against a schema the repo didn't have. An existing schema file must
# only be re-derived when schema is the explicit --target; staleness and --force must
# never trigger it.

def test_schema_not_rerun_when_stale_but_file_exists(rec, monkeypatch, tmp_path):
    (tmp_path / "med.json").write_text("{}")
    monkeypatch.setattr(ps, "DISCOVERED_DIR", tmp_path)
    rec["fresh"][("schema", "med", None)] = "stale"     # corpus repair flipped it stale
    ps.run_to("extract", "med", yes=True)
    assert [c[0] for c in rec["calls"] if c[0] == "schema"] == []
    assert "extract" in [c[0] for c in rec["calls"]]    # the chain still reaches extract


def test_schema_not_rerun_even_by_whole_profession_force(rec, monkeypatch, tmp_path):
    (tmp_path / "med.json").write_text("{}")
    monkeypatch.setattr(ps, "DISCOVERED_DIR", tmp_path)
    rec["fresh"][("schema", "med", None)] = "stale"
    ps.run_to("extract", "med", yes=True, force=True)   # no states named = whole profession
    assert [c[0] for c in rec["calls"] if c[0] == "schema"] == []


def test_schema_derived_when_file_missing(rec, monkeypatch, tmp_path):
    monkeypatch.setattr(ps, "DISCOVERED_DIR", tmp_path)  # empty dir — new profession
    ps.run_to("extract", "med", yes=True)
    assert "schema" in [c[0] for c in rec["calls"]]


def test_schema_explicit_target_rederives_existing_file(rec, monkeypatch, tmp_path):
    (tmp_path / "med.json").write_text("{}")
    monkeypatch.setattr(ps, "DISCOVERED_DIR", tmp_path)
    rec["fresh"][("schema", "med", None)] = "stale"
    ps.run_to("schema", "med", start="schema", yes=True)
    assert [c[0] for c in rec["calls"]] == ["schema"]


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
    assert [name for name, _ in res["plan"]] == ["pull", "clean", "trim", "schema", "extract", "verify", "mapprep", "publish"]


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


def test_mapprep_runs_all_three_bucket_passes(monkeypatch):
    # Regression guard: the front end's disciplinary_categories / list_field_categories
    # columns come from the per-item bucket passes. If the stage only runs plain
    # bucket_text (per-field), new occupations ship with those columns blank — exactly
    # what happened to the 6 trades. Assert all three passes fire.
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    assert ps._mapprep("plumbing", None, {}) is True
    assert _mods(cmds) == [
        "pipeline.map_prep.run",
        "pipeline.map_prep.bucket_text",   # per-field  -> text_buckets.json
        "pipeline.map_prep.bucket_text",   # --per-item -> disciplinary_categories
        "pipeline.map_prep.bucket_text",   # --list-fields -> list_field_categories
    ]
    flags = [c[-1] for c in cmds]
    assert "--per-item" in flags and "--list-fields" in flags


def test_mapprep_halts_if_a_bucket_pass_fails(monkeypatch):
    # A failing per-item pass must fail the stage, not silently ship blank columns.
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: "--per-item" not in cmd)
    assert ps._mapprep("plumbing", None, {}) is False


def test_fanout_wires_harmonize_universal(monkeypatch, tmp_path):
    # Orphan-producer regression: harmonize_universal must run in the full fanout, or a
    # new occupation's universal-field bucket labels never get cross-profession aligned.
    monkeypatch.setattr(ps, "FIELD_SEMANTICS_DIR", tmp_path)  # avoid gen_semantics noise
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    ps.run_fanout(["medicine"], payload_only=False)
    assert "pipeline.map_prep.harmonize_universal" in _mods(cmds)


def test_fanout_skips_harmonize_and_browse_when_payload_only(monkeypatch, tmp_path):
    monkeypatch.setattr(ps, "FIELD_SEMANTICS_DIR", tmp_path)
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    ps.run_fanout(["medicine"], payload_only=True)
    assert "pipeline.map_prep.harmonize_universal" not in _mods(cmds)  # heavy pass skipped


def test_fanout_gen_semantics_only_for_occupations_missing_it(monkeypatch, tmp_path):
    # Self-heal guard: generate Compare weights only for a profession that lacks them
    # (a new occupation); never re-charge the LLM for one that already has (editable) yaml.
    monkeypatch.setattr(ps, "FIELD_SEMANTICS_DIR", tmp_path)
    (tmp_path / "medicine.yaml").write_text("fields: {}")   # medicine HAS semantics
    cmds = []
    monkeypatch.setattr(ps, "_sh", lambda cmd, label, **k: cmds.append(cmd) or True)
    ps.run_fanout(["medicine", "plumbing"], payload_only=True)  # plumbing.yaml absent
    gen_profs = [c[-1] for c in cmds if "pipeline.analyze.gen_semantics" in c]
    assert gen_profs == ["plumbing"]   # plumbing generated, medicine skipped


def test_pull_uses_config_timeout_not_a_hardcode(monkeypatch):
    # The 900 default was a leftover; the pull stage must read the item-timeout from config.
    import pipeline.ingest.refresh_corpus as rc
    captured = {}
    monkeypatch.setattr(rc, "build_worklist", lambda profs, states: [("med", "UT", [])])
    monkeypatch.setattr(rc, "refresh_item",
                        lambda p, st, rows, **k: captured.update(timeout_s=k["timeout_s"]) or {"result": "OK"})
    monkeypatch.setattr(ps, "load_limits", lambda: {"refresh": {"item_timeout_seconds": 1801}})
    ps._pull("med", ["UT"], {})   # opts carries no pull_timeout
    assert captured["timeout_s"] == 1801


# --- stale upstream warning (2026-07-28) -------------------------------------------
# `--start` skips earlier stages, so a stale one STAYS stale and the stage you do run
# reads its output. nursing/DE was extracted from a clean/ built six days before its
# text/: the corpus had been re-pulled, clean was never re-run, and the model silently
# read the old copy while the run reported success. Measured across the 13 published
# professions the same day: 178 of 635 cells had a stale clean stage.

def test_start_warns_when_it_skips_a_stale_upstream_stage(rec, capsys):
    rec["fresh"][("clean", "med", "UT")] = "stale"
    ps.run_to("extract", "med", ["UT"], start="extract", yes=True)
    err = capsys.readouterr().out
    assert "STALE upstream" in err
    assert "med/UT (clean)" in err


def test_no_warning_when_upstream_is_current(rec, capsys):
    for stage in ("pull", "clean", "trim"):
        rec["fresh"][(stage, "med", "UT")] = "current"
    ps.run_to("extract", "med", ["UT"], start="extract", yes=True)
    assert "STALE upstream" not in capsys.readouterr().out


def test_no_warning_when_starting_from_the_beginning(rec, capsys):
    """Nothing is skipped, so nothing can be silently stale."""
    rec["fresh"][("clean", "med", "UT")] = "stale"
    ps.run_to("extract", "med", ["UT"], yes=True)
    assert "STALE upstream" not in capsys.readouterr().out
