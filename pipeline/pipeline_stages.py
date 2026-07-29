"""The pipeline as ONE declarative stage table + one runner.

The chain `pull → clean → trim → schema → extract → mapprep → publish → fanout` ended up
re-encoded — in a different order, with a different apparatus — inside five separate
orchestrators (client/run, extract/re_extract_queue, publish/refresh_all,
ingest/refresh_corpus, discover/add_occupation). Stage order lived in five places; the
cost gate lived in one; "clean before trim" was an operator's job to get right.
(re_extract_queue is now just this module's `--queue` CLI; the others are thin callers.)

This module makes the chain the single source of truth. Each stage is one frozen
`Stage` record naming its scope, the engine that runs it (`run_fn`, a THIN adapter over
the existing stage module — no engine logic moves here), and how to tell if it's already
current (`fresh_fn`, almost always `provenance.check`). `run_to(target, ...)` walks the
ordered prefix and runs only the units that aren't current — so ordering is correct by
construction and a re-run after a partial failure never re-does finished work.

This is a list + a loop, deliberately NOT a DAG framework. The engines are unchanged;
the orchestrators become thin callers of `run_to`.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable

from pipeline import provenance
from pipeline.paths import STRUCTURED_DIR, REPO_ROOT, DISCOVERED_DIR
from pipeline.config.loaders import cost_for, load_limits

PY = sys.executable

# Per-profession Compare-tab tuning weights (gen_semantics output). Used as a
# self-heal guard in run_fanout so a new occupation gets semantics generated once,
# without re-running the LLM for occupations that already have (hand-editable) ones.
FIELD_SEMANTICS_DIR = REPO_ROOT / "pipeline" / "config" / "field_semantics"


# --- shared helpers (the ONE copy of each; the orchestrators had 4) ------------

def _sh(cmd: list[str], label: str, *, cwd: str | None = None) -> bool:
    """Echo and run one subprocess from the repo root; return success. The single
    subprocess-wrapper (client/run._run_cmd, refresh_all.run, add_occupation._run and
    re_extract_queue._run were four copies of this)."""
    print(f"\n=== {label} ===\n$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=cwd or str(REPO_ROOT))
    if r.returncode != 0:
        print(f"!! {label} FAILED (exit {r.returncode})", flush=True)
        return False
    return True


def confirm_if_paid(stage: str, n_units: int, yes: bool) -> None:
    """Gate a paid stage behind a typed 'yes' (skipped with --yes / when free). The
    per-unit price comes from config/costs.yaml via cost_for and the model it's priced
    against from models.yaml, so neither can silently drift from what the dashboard quotes.
    Free stages (cost 0) return immediately, so every path that reaches a paid stage now
    prompts identically — this was previously client/run-only."""
    per = cost_for(stage, 0.0)
    if per <= 0 or n_units <= 0:
        return
    from pipeline.config.loaders import model_for
    try:
        priced = f", using {model_for(stage)} at today's price"
    except Exception:
        priced = ""
    est = n_units * per
    print(f"\n{stage}: {n_units} unit(s)  ·  estimated cost ~${est:.2f} "
          f"(${per:.2f}/unit{priced} — changes if the model changes)")
    if yes:
        print("  --yes given, proceeding without prompt.")
        return
    try:
        answer = input('  Type "yes" to run this paid step: ')
    except EOFError:
        # Backgrounded/piped runs have no stdin: a bare input() dies with an ugly
        # traceback MID-CHAIN, stranding earlier stages half-done (2026-07-29: the
        # re-extract chain died at the trim prompt this way). Fail clean instead.
        sys.exit("  aborted — no stdin to confirm a paid stage (non-interactive run). "
                 "Re-run with --yes.")
    if answer.strip().lower() != "yes":
        sys.exit("  aborted — no charge incurred.")


def _live_pull_pids() -> list[str]:
    """PIDs of OTHER processes currently running a corpus pull (refresh_corpus /
    pull_text). Excludes this process and its parent, so the annual-refresh loop —
    which pulls and then calls run_to in the same process — never flags itself."""
    try:
        out = subprocess.run(
            ["pgrep", "-f", "pipeline[.]ingest[.](refresh_corpus|pull_text)"],
            capture_output=True, text=True, timeout=5)
    except Exception:
        return []
    own = {str(os.getpid()), str(os.getppid())}
    return [p for p in out.stdout.split() if p not in own]


def drop_current(stage: str, queue: dict[str, list[str]]
                 ) -> tuple[dict[str, list[str]], list[tuple[str, str]]]:
    """Drop cells already CURRENT for this (cell-scoped) stage, so a re-run after a partial
    failure never re-charges for cells that already succeeded. "current" (per provenance)
    means the output exists AND reflects today's corpus + recipe. Stale/unstamped/missing
    cells are kept. Returns (kept_queue, skipped_cells). Lifted from client/run so every
    caller drops-before-charging identically — the guard against money leaking on a re-run."""
    kept: dict[str, list[str]] = {}
    skipped: list[tuple[str, str]] = []
    for prof, states in queue.items():
        keep = [st for st in states if provenance.check(stage, prof, st) != "current"]
        skipped.extend((prof, st) for st in states if st not in keep)
        if keep:
            kept[prof] = keep
    return kept, skipped


# --- stage adapters (thin wrappers over the existing engines) ------------------

# A cell-stage adapter takes the FULL list of that profession's due states and runs them
# in one shot (the engine CLIs already accept `--states a,b,c`; extract submits one batch),
# so the runner stays one-subprocess/one-batch-per-profession-per-stage — efficient, and
# matching how client/run already invoked these. A profession-stage adapter ignores `unit`.

def _clean(prof: str, states: list[str], opts: dict) -> bool:
    return _sh([PY, "-m", "pipeline.ingest.clean_text", "--profession", prof,
                "--states", ",".join(states)], f"clean {prof} ({len(states)})")


def _trim(prof: str, states: list[str], opts: dict) -> bool:
    extra = ["--strict"] if opts.get("strict") else []
    return _sh([PY, "-m", "pipeline.ingest.trim_state", "--profession", prof,
                "--states", ",".join(states), *extra], f"trim {prof} ({len(states)})")


def _schema(prof: str, unit, opts: dict) -> bool:
    return _sh([PY, "-m", "pipeline.extract.discover_schema", "--profession", prof],
               f"schema {prof}")


def _extract(prof: str, states: list[str], opts: dict) -> bool:
    # Canonical extract engine = the Anthropic batch path (50% discount + preflight +
    # partial-failure reconcile). All of a profession's due states go in ONE batch. This
    # replaces add_occupation's sync extract_state; provenance makes the two engines'
    # structured/ outputs interchangeable (test_extract_normalize), so it's a safe swap.
    from pipeline.extract.extract_state_batch import submit, poll
    meta = submit({prof: states}, force=opts.get("force", False))
    res = poll(meta["batch_id"], wait=True)
    return bool(res and res.get("written"))


def _verify(prof: str, unit, opts: dict) -> bool:
    # Semantic negative-check: an explicit exclusion whose cited quote doesn't
    # actually establish the prohibition (a wrong red cell in the comparison grid)
    # is reverted to null. Runs right after extract so mapprep/publish downstream
    # ship the cleaned data. General + automatic — see extract.verify_negatives.
    # Stamped AFTER the run: verify rewrites structured/ in place, so the stamp
    # hashes the post-rewrite tree and stays current until the next re-extraction.
    ok = _sh([PY, "-m", "pipeline.extract.verify_negatives", "--profession", prof],
             f"verify_negatives {prof}")
    if ok:
        provenance.record("verify", prof)
    return ok


def _mapprep(prof: str, unit, opts: dict) -> bool:
    # map_prep produces THREE bucket artifacts, and all three must run here or the
    # front end silently ships blanks: per-field (text_buckets.json) AND the two
    # per-item passes — disciplinary_grounds (--per-item → disciplinary_categories)
    # and the discovered profession_specific list fields (--list-fields →
    # list_field_categories). The per-item passes were historically a manual
    # afterthought, so occupations added after the mature 7 shipped with empty
    # category columns (the 6 trades). Wiring them into the stage makes it
    # impossible to forget for a new occupation. Sparse fields self-skip.
    bt = ["pipeline.map_prep.bucket_text", prof]
    steps = [
        (["pipeline.map_prep.run", prof], f"map_prep {prof}"),
        (bt, f"bucket_text {prof}"),
        (bt + ["--per-item"], f"bucket_text --per-item {prof}"),
        (bt + ["--list-fields"], f"bucket_text --list-fields {prof}"),
    ]
    for mod_args, label in steps:
        if not _sh([PY, "-m", *mod_args], label):
            return False
    return True


def _publish(prof: str, unit, opts: dict) -> bool:
    """Build a profession's web payload. The cross-field consistency gate now lives HERE
    (it was a pre-loop pass in refresh_all) so EVERY publish path is gated identically:
    a record that violates the prompt's own invariants blocks that profession's publish."""
    if not opts.get("skip_consistency"):
        viols = _consistency_violations(prof)
        if viols:
            print(f"\n✗ consistency gate: {len(viols)} violation(s) in {prof} — NOT publishing.")
            for v in viols:
                print(f"   [{v['profession']}/{v['state']}] {v['rule']}: {v['detail']}")
            return False
    fe = ["--payload-only"] if opts.get("payload_only") else []
    if not _sh([PY, "-m", "pipeline.publish.build_frontend", "--profession", prof, *fe],
               f"build_frontend {prof}{' (payload-only)' if fe else ''}"):
        return False
    # In payload-only mode the per-state browse blobs are intentionally NOT rebuilt, so
    # the published output is incomplete — don't stamp it current, or a later full refresh
    # would wrongly skip it (mirrors refresh_all's old don't-record-the-fingerprint rule).
    if not opts.get("payload_only"):
        provenance.record("publish", prof)
    return True


def _consistency_violations(prof: str) -> list[dict]:
    """Cross-field consistency violations across a profession's structured records. A
    corrupt/unreadable record is itself a violation (it can't be checked, so it must not
    slip silently into publish)."""
    import json
    from pipeline._records import record_files
    from pipeline.eval.check_consistency import check_record
    viols: list[dict] = []
    for jf in record_files(STRUCTURED_DIR / prof):
        try:
            rec = json.loads(jf.read_text())
        except json.JSONDecodeError as e:
            viols.append({"profession": prof, "state": jf.stem,
                          "rule": "unreadable_json", "detail": str(e)[:120]})
            continue
        viols.extend(check_record(prof, jf.stem, rec))
    return viols


def _pull(prof: str, states: list[str], opts: dict) -> bool:
    """Re-pull each due state via refresh_corpus.refresh_item — the SAFE path (regression
    gate + health check + commit-iff-healthy), never the bare pull_text loop that
    re_extract_queue used. A cell whose result is OK/NOCHANGE has a healthy corpus and is
    stamped current; REGRESSION/PARTIAL/EMPTY/DEAD/NOFILE reverted → reported, run fails.

    NB: refresh_item COMMITS to git, so don't drive the pull stage while the annual refresh
    watchdog is running (index.lock race) — pause it first. In practice the pull stage is
    only reached by a full-chain run (start=None) or `--start pull`; the publish/client/
    add_occupation paths start later and never touch it."""
    from pipeline.ingest.refresh_corpus import refresh_item, build_worklist
    ok_all = True
    for (p, st, rows) in build_worklist([prof], set(states)):
        rec = refresh_item(p, st, rows, force=opts.get("pull_force", False),
                           cap=opts.get("cap"),
                           timeout_s=opts.get("pull_timeout") or load_limits()["refresh"]["item_timeout_seconds"],
                           run_id=opts.get("run_id"))
        result = rec.get("result")
        # refresh_item now stamps pull-provenance itself on OK/NOCHANGE (and commits it),
        # so the healthy path needs nothing here — just track the failures.
        if result not in ("OK", "NOCHANGE"):
            ok_all = False
            print(f"  pull {p}/{st}: {result} — {rec.get('reason', '')}", flush=True)
    return ok_all


# --- the declarative table -----------------------------------------------------

@dataclass(frozen=True)
class Stage:
    name: str
    scope: str                      # "cell" | "profession" | "global"
    run_fn: Callable[[str, str | None, dict], bool]
    cost_stage: str                 # config/costs.yaml key for confirm_if_paid (free → absent key → 0)

    def fresh(self, prof: str, state: str | None) -> str:
        """Freshness verdict for one unit. The global fanout stage isn't in the provenance
        contract (its freshness is "did any profession change" — the caller's call), so it
        always reads not-current and its run is gated by the caller instead."""
        if self.scope == "global":
            return "stale"
        if self.name not in ("pull", *provenance.STAGES, *provenance.PROF_STAGES):
            # A stage outside the provenance vocabulary is always due — never let it
            # reach provenance.check, which raises KeyError. (verify lived here until
            # 2026-07-29, which made EVERY chain spanning it crash; it now has a real
            # contract keyed on structured/. This guard stays for the next new stage.)
            return "stale"
        return provenance.check(self.name, prof, state)


# Order is defined ONCE, here. run_to() and every orchestrator read it; nothing else
# encodes "clean before trim". cost_stage is the costs.yaml key (only the LLM stages have
# one; the rest resolve to $0 in confirm_if_paid).
STAGES: tuple[Stage, ...] = (
    Stage("pull",    "cell",       _pull,    "pull"),
    Stage("clean",   "cell",       _clean,   "clean"),
    Stage("trim",    "cell",       _trim,    "trim"),
    Stage("schema",  "profession", _schema,  "schema"),
    Stage("extract", "cell",       _extract, "extract"),
    Stage("verify",  "profession", _verify,  "verify"),
    Stage("mapprep", "profession", _mapprep, "map_prep"),
    Stage("publish", "profession", _publish, "publish"),
    Stage("fanout",  "global",     lambda *_a: True, "fanout"),  # driven via run_fanout()
)

_BY_NAME = {s.name: s for s in STAGES}
_ORDER = {s.name: i for i, s in enumerate(STAGES)}


def _states_for(prof: str) -> list[str]:
    """The states a profession already has (its structured records) — the unit set a
    cell-scoped stage iterates when the caller didn't pin an explicit list."""
    d = STRUCTURED_DIR / prof
    if not d.exists():
        return []
    return sorted(f.stem for f in d.glob("*.json") if not f.name.startswith("_"))


def run_to(target: str, prof: str, states: list[str] | None = None, *,
           start: str | None = None, force: bool = False, yes: bool = False,
           dry_run: bool = False, opts: dict | None = None) -> dict:
    """Run the chain from `start` up to and including `target` for one profession, running
    only the units that aren't already current (unless `force`). Because it walks the
    ordered STAGES prefix, upstream can never run after downstream — the ordering footgun
    is gone.

    `start` selects the first stage to (maybe) run:
      - None      → the whole prefix from `pull` (the full-chain runners).
      - target    → ONLY the target stage (downstream tools that treat upstream as a
                    precondition, e.g. refresh_all's pure-publish rebuild).
      - "clean"   → skip `pull` — the no-pull paths (add_occupation: text already on disk).
    `dry_run` prints the ordered plan and spends nothing. Returns {plan, ran, skipped, ok}."""
    opts = opts or {}
    if target not in _ORDER:
        raise ValueError(f"unknown target stage {target!r}")
    ti = _ORDER[target]
    si = _ORDER[start] if start is not None else 0
    if si > ti:
        raise ValueError(f"start {start!r} is after target {target!r}")
    # `--start` SKIPS every earlier stage, so a stale one stays stale and the stage you
    # do run reads its output. That is exactly how nursing/DE came to be extracted from a
    # `clean/` built six days before its `text/` -- the corpus had been re-pulled, clean
    # was never re-run, and the model silently read the old copy while reporting success.
    # CLAUDE.md calls this the "re-extract gotcha"; prose doesn't fire at 2am, so say it
    # here. A warning rather than an error: replaying one stage over known-good input is
    # legitimate (that is what --start is FOR), we just refuse to be quiet about it.
    # A pull loop running in ANOTHER process can re-commit text/ underneath this run,
    # leaving whatever this run produces stale on arrival (the 2026-07-29 race: clean+
    # trim ran while a re-pull loop was mid-flight; the batch built on them was garbage).
    # Warn loudly rather than lock: preflight/provenance will still catch the staleness
    # at the next paid gate, and the annual-refresh loop legitimately pulls in-process.
    if not dry_run:
        pids = _live_pull_pids()
        if pids:
            print(f"\n!! WARNING: a corpus pull is RUNNING in another process "
                  f"(pid {', '.join(pids)}). text/ may change underneath this run and "
                  f"invalidate its outputs — prefer waiting for the pull to finish.\n",
                  flush=True)

    if si > 0 and not dry_run:
        cells = states if states is not None else _states_for(prof)
        behind = [
            (s, st.name) for s in cells for st in STAGES[:si]
            if st.scope == "cell" and st.fresh(prof, s) == "stale"
        ]
        if behind:
            shown = ", ".join(f"{prof}/{s} ({stage})" for s, stage in behind[:6])
            more = f" +{len(behind) - 6} more" if len(behind) > 6 else ""
            print(f"\n!! WARNING: --start={start} skips {len(behind)} STALE upstream stage(s): "
                  f"{shown}{more}\n"
                  f"   Their inputs changed since they last ran, so this run will read "
                  f"OUT-OF-DATE data.\n"
                  f"   Re-run from the earliest stale stage instead, or pass --force.\n",
                  flush=True)

    plan: list[tuple[str, list[str]]] = []
    ran: list[tuple[str, str, object, bool]] = []
    skipped: list[tuple[str, str, str | None]] = []
    for stage in STAGES[si:ti + 1]:
        if stage.scope == "global":
            continue                            # global stages are driven by run_fanout()

        if stage.scope == "cell":
            # One dispatch per profession over ALL its due states (the engine CLIs take
            # --states a,b,c; extract submits one batch). n_units = #states for the gate.
            cells = states if states is not None else _states_for(prof)
            due = [s for s in cells if force or stage.fresh(prof, s) != "current"]
            skipped.extend((stage.name, prof, s) for s in cells if s not in due)
            if not due:
                continue
            plan.append((stage.name, [f"{prof}/{s}" for s in due]))
            if dry_run:
                continue
            confirm_if_paid(stage.cost_stage, len(due), yes)
            ok = stage.run_fn(prof, due, opts)
            ran.append((stage.name, prof, due, ok))
        else:                                   # profession-scoped: one unit
            # An EXISTING discovered schema is a stable contract, not a recomputable
            # artifact: re-derivation is LLM churn (2026-07-29: nursing renamed 26 of its
            # 29 fields on a same-corpus re-derive), and every corpus repair flips schema
            # provenance stale — so freshness must never auto-trigger it, or a routine
            # re-extract leaves its states on a field set the rest of the profession
            # doesn't share. Re-derive only when the file is missing (a new profession)
            # or when schema is the explicit --target.
            if (stage.name == "schema" and target != "schema"
                    and (DISCOVERED_DIR / f"{prof}.json").exists()):
                skipped.append((stage.name, prof, None))
                continue
            # `--force` means "redo the CELLS I named", not "redo profession-wide
            # artifacts". Forcing a single state used to drag in `schema`, re-deriving
            # the whole profession's schema from a 10-state LLM sample -- so a one-cell
            # repair could leave that state extracted against a field set the other 49
            # don't share. Profession-scoped stages are forced only when the run covers
            # the whole profession, or when you named the stage as the explicit --target.
            forces_this_stage = force and (states is None or stage.name == target)
            if not forces_this_stage and stage.fresh(prof, None) == "current":
                skipped.append((stage.name, prof, None))
                continue
            plan.append((stage.name, [prof]))
            if dry_run:
                continue
            confirm_if_paid(stage.cost_stage, 1, yes)
            ok = stage.run_fn(prof, None, opts)
            ran.append((stage.name, prof, None, ok))

        if not ok:
            # Stop this profession's chain — a failed stage means downstream input is
            # missing/stale; re-running the same command resumes (current units skip).
            return {"plan": plan, "ran": ran, "skipped": skipped, "ok": False}
    return {"plan": plan, "ran": ran, "skipped": skipped, "ok": all(o for *_, o in ran)}


# --- the global fan-out (moved out of refresh_all: publish's deterministic tail) ---

def run_fanout(profs: list[str], *, payload_only: bool = False) -> list[tuple[str, bool]]:
    """Rebuild every site artifact that AGGREGATES across professions — tag sheet, scope
    capabilities, scorecard, state/umbrella browse, similarity/novel-direction analysis.
    Runs once per refresh (not per profession). This is the `fanout` stage's body, lifted
    from refresh_all so refresh_all is a thin caller.

    Two LLM steps run here, both wired in so a NEW occupation self-fills instead of
    shipping degraded (the orphan-producer bug class): `gen_semantics` per profession —
    GUARDED to only run when a profession lacks tuned Compare weights, so it never
    re-charges for existing (hand-editable) ones — and `harmonize_universal`, a
    cross-profession pass that aligns the shared universal-field bucket labels. Everything
    else is deterministic.

    `payload_only`: a tags/table/map-only change didn't touch browse, so skip the slow
    per-state browse + scorecard rebuild (~10× faster)."""
    results: list[tuple[str, bool]] = []
    for p in profs:                             # per-profession deterministic derivations
        _sh([PY, "-m", "pipeline.publish.generate_field_dictionary", "--profession", p],
            f"field_dictionary {p}")
    for p in profs:
        # Compare-tab tuning weights feed similarity below. Self-heal only: generate for a
        # profession that has none (a newly-added occupation); existing yaml is kept.
        if not (FIELD_SEMANTICS_DIR / f"{p}.yaml").exists():
            _sh([PY, "-m", "pipeline.analyze.gen_semantics", "--profession", p], f"gen_semantics {p}")
    for p in profs:
        _sh([PY, "-m", "pipeline.analyze.similarity", "--profession", p, "--json"], f"similarity {p}")
    if profs:
        # similarity rewrites results/analysis/ and drops `direction`, so re-stamp it
        # after similarity and before publish_analysis ships (cached by (field,value)).
        _sh([PY, "-m", "pipeline.analyze.classify_novel_direction", "--professions", ",".join(profs)],
            "classify_novel_direction")
    results.append(("publish_analysis",
                    _sh([PY, "-m", "pipeline.analyze.publish_analysis"], "publish_analysis")))
    results.append(("build_tag_sheet",
                    _sh([PY, "-m", "pipeline.publish.build_tag_sheet", "--upload"], "build_tag_sheet")))
    results.append(("build_scope_capabilities",
                    _sh([PY, "-m", "pipeline.publish.build_scope_capabilities", "--upload"],
                        "build_scope_capabilities")))
    results.append(("build_scope_matrices",
                    _sh([PY, "-m", "pipeline.publish.build_scope_matrices", "--upload"],
                        "build_scope_matrices")))
    if not payload_only:
        # Cross-profession bucket alignment for the shared universal fields (reads current
        # data, so re-running self-heals to cover every published profession). build_frontend
        # consumes universal_buckets.json, so a brand-new occupation picks up the harmonized
        # labels on the NEXT rebuild — one-cycle lag, then correct.
        results.append(("harmonize_universal",
                        _sh([PY, "-m", "pipeline.map_prep.harmonize_universal"], "harmonize_universal")))
        results.append(("scorecard",
                        _sh([PY, "-m", "pipeline.publish.cross_comparison_scorecard", "--upload"], "scorecard")))
        results.append(("build_state_browse",
                        _sh([PY, "-m", "pipeline.publish.build_state_browse"], "build_state_browse")))
        results.append(("build_umbrella_browse",
                        _sh([PY, "-m", "pipeline.publish.build_umbrella_browse"], "build_umbrella_browse")))
        # Downloads (per-occupation + per-state Excel) depend on the payloads + state browse
        # blobs above, so they run last. Uploads are content-hash skipped → cheap when unchanged.
        results.append(("build_downloads",
                        _sh([PY, "-m", "pipeline.publish.build_downloads"], "build_downloads")))
    return results


# --- CLI: run the chain over a queue (replaces extract/re_extract_queue) --------

def main() -> None:
    """Run the chain to `--target` over a `{profession: [states]}` queue (or a single
    --profession/--states). Replaces re_extract_queue's queue runner: it defaults to
    start='clean' (text must already be on disk — bare pull is retired; re-pull via
    refresh_corpus), runs clean→trim→schema→extract in one batch per profession, and each
    paid stage hits the shared cost gate."""
    import argparse
    import json
    from pathlib import Path

    ap = argparse.ArgumentParser(description="Run the pipeline chain over a queue of {profession: [states]}.")
    src = ap.add_argument_group("what to run (one of)")
    src.add_argument("--queue", help="JSON file: {profession: [states]}")
    src.add_argument("--profession", help="a single profession (with --states)")
    ap.add_argument("--states", default="", help="comma-separated states for --profession")
    ap.add_argument("--target", default="extract", choices=[s.name for s in STAGES],
                    help="run the chain up to this stage (default: extract)")
    ap.add_argument("--start", default="clean", choices=[s.name for s in STAGES],
                    help="first stage to run (default: clean — skips the retired bare pull)")
    ap.add_argument("--force", action="store_true", help="re-run even cells that are already current")
    ap.add_argument("--yes", action="store_true", help="skip the paid-stage cost confirmations")
    ap.add_argument("--dry-run", action="store_true", help="print the ordered plan, spend nothing")
    args = ap.parse_args()

    if args.queue:
        queue = json.loads(Path(args.queue).read_text())
    elif args.profession:
        queue = {args.profession: [s.strip() for s in args.states.split(",") if s.strip()]}
    else:
        ap.error("pass --queue FILE or --profession NAME [--states a,b,c]")

    failures = []
    for prof, states in queue.items():
        res = run_to(args.target, prof, states or None, start=args.start,
                     force=args.force, yes=args.yes, dry_run=args.dry_run)
        if args.dry_run:
            for stage, units in res["plan"]:
                print(f"  {stage}: {', '.join(units)}")
        elif not res["ok"]:
            failures.append(prof)
    if failures:
        sys.exit(f"failed: {failures} — fix the error(s) above and re-run (current cells skip).")


if __name__ == "__main__":
    main()
