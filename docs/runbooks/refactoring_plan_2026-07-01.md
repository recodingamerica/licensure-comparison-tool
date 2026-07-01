# Refactoring plan — 2026-07-01

Companion to the repo diet (`docs/reports/repo_diet_manifest_2026-07-01.md`). The diet
deletes; this restructures what stays. Everything here serves the handoff goals:
Utah runs three commands (`refresh_corpus` / extract orchestrator / `refresh_all`),
Abigail keeps a small curation workshop, nothing else exists.

## Principles

1. **Refactor only what the three commands touch.** No speculative abstraction; a
   module nobody operates doesn't earn restructuring, it earns deletion.
2. **Every refactor lands with the tests that prove it moved, not changed.** The
   473-test suite is the safety net; behavior-preserving moves must keep it green
   without editing expectations.
3. **Boring beats clever.** This codebase outlives our attention span and gets
   maintained by strangers with low bandwidth. Flat, explicit, greppable.
4. **Deletion is the best refactor.** When a restructure and a deletion compete,
   check whether the thing needs to exist first.

## R1. Proper package imports (early, mechanical, unblocks everything)

Nearly every module does `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))`
followed by bare imports (`from paths import ...`, `from discover.x import ...`).
This breaks IDE navigation, makes module identity ambiguous in tests (the
match_sections test had to monkeypatch a module-object copy), and is why every
script must run from repo root.

- Convert to absolute package imports (`from pipeline.paths import ...`) everywhere;
  delete the sys.path hacks.
- Add a `pyproject.toml` with the package + dev deps (pytest) so `pip install -e .`
  is the whole setup story — this also feeds the Task-4 fresh-machine script.
- Purely mechanical; do it as one sweep with the suite as the gate.

## R2. One config loader (kills duplicated ad-hoc loading)

`load_professions()` / `load_state_structure()` / manifest loaders are re-implemented
or re-imported ad hoc across discover/, ingest/, eval/. One `pipeline/config/loaders.py`
exposing typed accessors (professions, state_structure, mapping_overrides,
corpus_overrides, verified_absences), all through `safe_load_unique`. Modules stop
reading YAML directly.

## R3. A real type for the mapping node (the core artifact is a dict soup)

Matched-node dicts flow from hierarchy → matcher → overrides → index JSON → pull rows
with optional keys (`via`, `source`, `justia_url`, `section_slug_pattern`,
`section_url_list`, `pa_keep_sections`) and no single definition. Introduce a
`MatchedNode` dataclass (or TypedDict) in one place; matcher, `_mapping_overrides`,
and `pull_text`'s row conversion use it. This is where silent key-drift bugs live
(the `via` vs `source` tag split was exactly this).

## R4. Split pull_text.py around the Task-2 source flip (~2,000 → ~3 × 400 lines)

After Task 2 flips the remaining official-source config to Justia and the dead
fetch paths are deleted (deferred diet item), decompose what's left:

- `ingest/fetch_justia.py` — CDP transport: session, flock, challenge pause/detect,
  polite delays. `refresh_corpus` imports this same transport (one implementation).
- `ingest/fetch_pa.py` — the one permanent exception (static legacy endpoint).
- `ingest/pull_text.py` — corpus assembly: index→rows, section iteration,
  overwrite-guard/regression check, summaries. No transport code.

Do the split *when building refresh_corpus*, not before — the refresh command is
the second consumer that proves the seam is right.

## R5. Stage runner for the orchestrators (Task 3)

`refresh_corpus`, the extract orchestrator, and `refresh_all` each need: run stages
in order, staleness detection (already in `corpus_status` — call it, don't re-derive),
fail-loud on poisoned inputs (preflight/trim_degraded), run logging. One small
`pipeline/stages.py` used by all three, instead of three hand-rolled loops.
The extract orchestrator fills the deleted `pipeline/run.py` slot and makes the
clean→trim→extract ordering footgun structurally impossible.

## R6. Operator gate consolidation (`pipeline doctor`)

`corpus_status`, `preflight`, `verify_index_reproducibility`, `check_consistency`
are four separate invocations an operator won't remember. One `python -m pipeline.doctor`
that runs all read-only gates and prints a single pass/fail report. The individual
tools remain (they're the implementation); doctor is the front door. This is also
the diet manifest's CONSOLIDATE bucket landing spot.

## R7. Publish path: config-derived, not hardcoded

`build_state_browse.py`'s `PROFESSIONS` list and the scorecard's `PROFESSION_LABELS`
derive from `professions.yaml` + `core_professions()` (already Task 3 scope; listed
here for completeness). `build_frontend.py` (987 lines) gets an internal split
(payload assembly / quote spans / blob upload) only if Task-3 work forces us in —
otherwise left alone per Principle 1.

## Sequencing

| When | What |
|---|---|
| Now (post-diet) | R1 imports sweep, R2 config loaders — both mechanical, suite-gated |
| With Task 2 (refresh_corpus) | complete the Justia source flip in config → delete deferred pull_text official code + batches drivers → R4 split; R3 MatchedNode (matcher is fresh in context) |
| With Task 3 (orchestrator) | R5 stage runner, R6 doctor, R7 publish derivations; delete run_for_new_matches.py once replaced |
| Task 4 (handoff docs) | pyproject-based setup story from R1; OPERATOR.md documents doctor + three commands |

## Not doing (decided against)

- Renaming/reshuffling `discover/` into submodules — churn without operator benefit;
  a package README listing the ~16 surviving tools does the job.
- Async/parallel fetching — ONE pull process per Chrome is a hard constraint;
  concurrency is a corruption vector here, not a win.
- Generalizing the extraction schema machinery — it works and nobody touches it.
- Postgres path (`publish/db/`) — parked until the handoff works end to end.
