# Next steps — 2026-06-22

Supersedes `next_steps_2026-06-15.md`. Written as a clean handoff.

## Shipped this session (merged to main)

- **Compare tab / similarity-outlier feature** (PR #49). Per-occupation "what is each
  state like, where is it weird." One LLM step (`gen_semantics.py` → editable
  `config/field_semantics/<prof>.yaml`) codes field importance + value closeness;
  everything else is deterministic (`pipeline/analyze/similarity.py`): core-set
  overlap, per-state differs/same, controlled-vocabulary labels, templated notes (no
  LLM). Numbers-free, calm UI (`similarity-view.tsx`). Method + design doc:
  `docs/reports/similarity_outlier_analysis.md`.
- **PA held-out batch 2** (PR #48) — 29 professions wired + extracted (PA only).
- **Closed issues #2, #6, #14, #15** (verified done, evidence comments left).

## In flight

- **Production deploy** (`refresh_all --professions <7> --deploy`) running at write
  time. When it lands, the Compare tab is live at utah-licensing.vercel.app for the 7
  published professions. Verify via the built `public/data/analysis/<prof>.json` +
  the live Compare tab (prod is behind Vercel auth, so don't curl — load it).

## Pending (small, do next session)

1. **Compare-feature cleanup** (apply AFTER the deploy finishes; ~10 min):
   - Strip `kind_outliers` / `stringency_outliers` from the written analysis JSON and
     delete `KindOutlier`/`StringencyOutlier` + the two fields from `types.ts` — the UI
     reads `differs_on`/`typical_on` now, so these are unused payload bloat. Keep them in
     `analyze()`'s return for the CLI debug print (`--json` write strips them).
   - Refresh the stale `similarity.py` module docstring (lines ~11–14 still list
     kind/stringency as the primary outputs).
   - Ships on the *next* deploy; no re-deploy needed just for this (extra JSON fields
     are harmless on the live site).

## Key finding: Compare is scoped to fully-covered professions

Compare is a **cross-state** tool. The 7 published professions have 50 states each;
**every held-out profession has only PA (1 state)** — they were the PA-coverage project,
not full coverage. So they cannot get a meaningful Compare tab. Extending Compare to a
new profession = bringing it to full ~50-state coverage first (pull → clean → trim →
extract per state, the big deliberate effort). The Compare-specific add is trivial
(`gen_semantics` ~$0.10/prof + free math); the prerequisite (full extraction) is the
real cost. **Decision: Compare stays on the 7 covered professions.**

## Open work, prioritized

| Priority | Issue | What | Size |
|---|---|---|---|
| 1 | **#16** | Cross-profession bucket harmonization for universal fields — not started; cleanest discrete task (~20 universal fields × 1 LLM call). | S |
| 2 | **#8** | Audit MI section completeness across professions (dietetics gap fixed; broad sweep not done). | M |
| 3 | **#17** | Two doc one-liners remain (UORF sort already shipped): "Utah = Model E" line in STATUS.md; cosmetology lumping note. Then close. | XS |
| 4 | **#7** | ND year-version dedup mechanism exists; spot-check ND section counts vs statute, close if it suffices. | XS |
| 5 | **#19** | Optometry scope-narrowing fields shipped; confirm the dietetics half before closing. | S |
| — | **#1** | Largely superseded by the per-state `state_scope/*.yaml` manifest pivot — reframe or close as superseded (no UT.yaml / section-level applies-to was built). | reframe |
| — | **PR #43** | run.py orchestrator + GitHub Action — mergeable; only `VERCEL_TOKEN` repo secret outstanding (deploy-only; generate from Vercel dashboard, then merge + test-run). | unblock |

**Atharv-owned (#28, #33, #34, #35, #37):** all shipped with our status comments; his to
verify + close. Nothing for us.

**Larger / research:** Path 2 (annual statute refresh — overwrite-guard prereq done in
#47; remaining: throttled/resumable refresher + diff-driven re-extract). #35 point-3
(`degree_pegged_to_credential` flag) only if Atharv wants it.
