"""The pipeline as ONE declarative stage table + one runner.

The chain `pull → clean → trim → schema → extract → mapprep → publish → fanout` ended up
re-encoded — in a different order, with a different apparatus — inside five separate
orchestrators (client/run, extract/re_extract_queue, publish/refresh_all,
ingest/refresh_corpus, discover/add_occupation). Stage order lived in five places; the
cost gate lived in one; "clean before trim" was an operator's job to get right.

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

import subprocess
import sys
from dataclasses import dataclass
from typing import Callable

from pipeline import provenance
from pipeline.paths import STRUCTURED_DIR, PIPELINE_ROOT
from pipeline.config.loaders import cost_for

PY = sys.executable
REPO_ROOT = PIPELINE_ROOT.parent


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
    if input('  Type "yes" to run this paid step: ').strip().lower() != "yes":
        sys.exit("  aborted — no charge incurred.")


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


def _mapprep(prof: str, unit, opts: dict) -> bool:
    ok = _sh([PY, "-m", "pipeline.map_prep.run", prof], f"map_prep {prof}")
    return ok and _sh([PY, "-m", "pipeline.map_prep.bucket_text", prof], f"bucket_text {prof}")


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
    # Adopted as a runner stage in Phase 5 (wraps refresh_corpus.refresh_item). Until then
    # nothing starts the chain at `pull` (refresh_all starts at publish; add_occupation at
    # clean; client/run at its own stage), so it's never hit.
    raise NotImplementedError("pull is wired into the runner in Phase 5")


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
            if not force and stage.fresh(prof, None) == "current":
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
    All deterministic, NO LLM. Runs once per refresh (not per profession). This is the
    `fanout` stage's body, lifted verbatim from refresh_all so refresh_all is a thin caller.

    `payload_only`: a tags/table/map-only change didn't touch browse, so skip the slow
    per-state browse + scorecard rebuild (~10× faster)."""
    results: list[tuple[str, bool]] = []
    for p in profs:                             # per-profession deterministic derivations
        _sh([PY, "-m", "pipeline.publish.generate_field_dictionary", "--profession", p],
            f"field_dictionary {p}")
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
    if not payload_only:
        results.append(("scorecard",
                        _sh([PY, "-m", "pipeline.publish.cross_comparison_scorecard", "--upload"], "scorecard")))
        results.append(("build_state_browse",
                        _sh([PY, "-m", "pipeline.publish.build_state_browse"], "build_state_browse")))
        results.append(("build_umbrella_browse",
                        _sh([PY, "-m", "pipeline.publish.build_umbrella_browse"], "build_umbrella_browse")))
    return results
