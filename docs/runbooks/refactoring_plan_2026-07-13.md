# Refactoring execution plan (2026-07-13)

Self-contained so a fresh session can execute after `/clear`. Assessment: the pipeline is in
good shape (25K LOC, 696 functions, 652 <60 lines, only 6 ≥150). This is opportunistic
cleanup + finishing the Jul-1 repo-diet, NOT a rewrite. Do the tiers in order; each tier is an
independent commit (or a few). **Gate every change on the full suite (`pipeline/.venv/bin/python
-m pytest -q`, currently 615 green) and, for stage code, a `verify` run of that stage.**

Baseline reference: `docs/reports/repo_diet_manifest_2026-07-01.md` (its DELETE/CONSOLIDATE
classifications, ~half already executed).

## Tier 1 — Dead-tool cleanup (mechanical, low-risk, do first)

Already deleted since Jul-1: llm_map_profession, audit_llm_candidates, cross_ref_siblings,
verify_gap_states, pull_regulations, probe_justia.

**Method (per module, don't pre-trust this list):** for each candidate run
`git grep -l <name> -- '*.py' '*.sh' 'docs/**' 'CLAUDE.md'`. If referenced ONLY by
repo_diet_manifest + its own file + (maybe) a dead test → delete file + test. If a runbook or
client script actually invokes it → keep (or fold per below).

1. **DELETE (confirmed abandoned):**
   - `pipeline/run_for_new_matches.py` + `tests/test_run_for_new_matches.py` — abandoned
     LLM-automap loop, no code importer. (Manifest DELETE.)
2. **CONSOLIDATE → `pipeline/eval/corpus_status.py` (the unified health check), or delete:**
   - `discover/audit_linkless_chapters.py` (169), `discover/diff_coverage.py` (78),
     `discover/survey_umbrella_states.py` (217), `discover/harvest_occupations.py` (270),
     `analyze/gen_semantics.py`. Each is a standalone QA/report script; move its one useful
     signal into corpus_status as a sub-report, then delete the standalone. If folding is more
     work than it's worth, just delete the ones with `docs_refs=0`
     (survey_umbrella_states, build_review_csv, check_summaries, dedupe_corpora, source_purity).
3. **TRIAGE (grep each, then keep/delete):** `extract/re_extract_queue.py`,
   `extract/repair_unverified.py`, `publish/build_gap_matrix.py`, `publish/build_review_csv.py`,
   `discover/umbrella_coverage_matrix.py`, `eval/check_summaries.py`, `eval/source_purity.py`,
   `ingest/dedupe_corpora.py`. **KEEP `eval/check_vs_oplr.py`** (live OPLR ground-truth harness).
- Expected removal: several hundred LOC. One commit: "Tier-1 refactor: finish repo-diet dead-tool cleanup".

## Tier 2 — Long-function decomposition (real logic; one function per commit)

Touch only where length == branching complexity. **SKIP `client/handoff_doc.py::build_markdown`
(358)** — it's one big injected-template f-string; decomposing hurts it.

1. **`publish/build_frontend.py::build` (261)** — highest value (most-edited publish path).
   Extract named helpers: rows assembly, column/preset config, blob write, browse-file trigger.
   Gate: suite + `python -m pipeline.publish.build_frontend` on one published profession, diff the
   emitted `data/<prof>.json` against pre-refactor (should be byte-identical).
2. **`ingest/pull_text.py::pull_state` (177)** — extract the drill-and-collect loop and the
   record-keeping into helpers; keep retry/over-broad logic intact. Gate: suite + one live
   `refresh_corpus --profession X --states Y` re-pull matches prior section count.
3. **`analyze/similarity.py::analyze` (224)** — FIRST confirm it's on an active path (the
   compare/novel-policies feature). If dormant, skip or move to Tier-1 delete instead.

## Tier 3 — Duplication (reactive; lowest priority)

1. **`ingest/pull_text.py::pull_state` vs `ingest/pull_umbrella_text.py::pull_state_umbrella`**
   (177 vs 154) — read both; if they share fetch/drill/record scaffolding, extract a shared
   `_pull_container(...)` core. Only if they've drifted / caused parallel bugs. Stable now → low urgency.
2. **Browse builders** `publish/build_state_browse.py` (359) + `build_umbrella_browse.py` (333)
   already import `_browse_tree.py` (207). Verify they're not re-implementing tree logic; if they
   are, push more into `_browse_tree`. Otherwise leave.

## Do NOT
- Rewrite the stage-dir pipeline (text→clean→trim→structured→publish) — it's clean.
- Touch the fetch layer — just de-CDP'd + Scrapling-consolidated 2026-07-13.
- Chase <60-line functions.

## Sequencing / safety
Tier 1 first (independent, safe) → Tier 2 one function per commit, each behind suite + a real
stage run → Tier 3 only if a bug motivates it. None blocks feature work. Commit direct to `main`
(repo convention). Run the suite before every commit.
