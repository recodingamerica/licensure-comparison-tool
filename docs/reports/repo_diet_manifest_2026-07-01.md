# Repo Diet Manifest — 2026-07-01

Prepared for Utah OPLR handoff. Read-only analysis; no files were modified.

## Decisions driving classification

1. **Justia-only fetching** — the 13 non-PA official-source fetch paths (UT, SD, NV, NY, CT, WA/VA whole-chapter, ME, ID, MO, MD, RI, VT, MT, AZ, FL) are dead code once refresh_corpus is the operator path. PA (`pa_legis`) is the sole exception — PA is not on Justia and its puller stays.
2. **LLM auto-mapping failed** — `llm_map_profession`, `map_state_chapters`, `map_state_sections`, `suggest_overrides`, `audit_llm_candidates` and the surrounding scaffold are superseded by hand-curated `state_structure.yaml` + new `mapping_overrides.yaml`. `apply_llm_candidates` was _just_ retargeted to write `mapping_overrides.yaml`; it is the live back-half of the operator loop and stays.
3. **Three-command operator surface** — `refresh_corpus` (to be built, replacing batch drivers), an extract orchestrator (replacing `pipeline/run.py` stub), and `refresh_all` (exists).
4. **Batch drivers in `results/batches/_*.py`** — replace by `refresh_corpus`; delete after Task 2.

---

## Summary table

| Package | Modules | OPERATOR | CURATION | CONSOLIDATE | DELETE | Notes |
|---|---|---|---|---|---|---|
| pipeline/ (root) | 11 | 8 | 0 | 0 | 3 | run.py stub + merged_scope + scope_sources |
| pipeline/config/ | 4 | 4 | 0 | 0 | 0 | all keep |
| pipeline/discover/ | 39 | 7 | 16 | 4 | 12 | largest DELETE pool |
| pipeline/ingest/ | 7 | 5 | 0 | 1 | 1 | pull_regulations = CONSOLIDATE |
| pipeline/extract/ | 10 | 5 | 0 | 3 | 2 | one-offs vs core |
| pipeline/eval/ | 5 | 3 | 1 | 1 | 0 | |
| pipeline/analyze/ | 5 | 4 | 0 | 1 | 0 | gen_semantics = CONSOLIDATE |
| pipeline/map_prep/ | 5 | 4 | 0 | 0 | 1 | run.py |
| pipeline/publish/ | 14 | 11 | 0 | 3 | 0 | state_similarity / build_gap_matrix / build_review_csv |
| pipeline/notes/archive/ | 2 | — | — | — | 2 | |
| results/batches/ | 7 | — | — | — | 7 (after Task 2) | |
| **.scratch/** | — | — | — | — | all (after Task 2) | scratch prep files |

**Estimated DELETE lines (immediate):** ~3 400 lines across 26 modules.
**After Task 2 (batch drivers + .scratch):** +696 lines.
**pull_text official-source dead code (kept in place for now; see note):** lines 508–1344, roughly 837 lines, 16 discrete blocks.

---

## pipeline/ (root modules)

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `_batch.py` | 217 | OPERATOR | extract_state_batch | — | Anthropic batch poller |
| `_env.py` | 22 | OPERATOR | 12+ modules | test_env.py | env loader |
| `_fetch_config.py` | 10 | OPERATOR | build_hierarchy, expand_hierarchy, fetch_section_bodies, pull_umbrella_text, find_licensing_titles | — | CDP delay constant |
| `_llm.py` | 220 | OPERATOR | extract_state + many discover | test_llm.py | structured LLM calls |
| `_prompts.py` | 32 | OPERATOR | extract_state, trim_state | — | prompt fragments |
| `_records.py` | 27 | OPERATOR | many publish / ingest | test_records.py | record_files helper |
| `_runlog.py` | 66 | OPERATOR | pull_text, clean_text, trim_state, extract_state, apply_verified_absences, build_frontend | test_runlog.py | run audit log |
| `paths.py` | 56 | OPERATOR | ~20 modules | test_yaml_loader.py | canonical path constants |
| `merged_scope.py` | 50 | OPERATOR | build_frontend, build_state_browse, build_umbrella_browse, umbrella_coverage_matrix, db/load | test_merged_scope.py, test_llm_scope_fallback.py, test_umbrella_coverage_matrix.py | merges walker+LLM umbrella scope; consumed by operator build tools |
| `scope_sources.py` | 84 | OPERATOR | build_frontend, build_state_browse, build_umbrella_browse, umbrella_coverage_matrix, db/load | test_scope_sources.py | canonical scope-source vocabulary; consumed by operator build tools |
| `run.py` | 29 | DELETE | none | none | Stub: `sys.exit("not yet implemented")`. Superseded by refresh_corpus (to be built). Safe to delete; zero imports. |
| `run_for_new_matches.py` | 108 | DELETE | none | test_run_for_new_matches.py | Workflow wrapper that diffs coverage CSVs before/after expand_hierarchy + match_profession runs. Only useful in an LLM-automap loop that was abandoned. **Test dies with it:** `tests/test_run_for_new_matches.py`. |

> **Note on merged_scope.py / scope_sources.py:** These are active operator dependencies (build_frontend, build_state_browse, build_umbrella_browse all import them). However, if the umbrella scope mechanism (`assign_umbrella_scope` → `suggest_scope_rules`) is retired at handoff, these modules would shrink to stubs. Mark OPERATOR for now.

---

## pipeline/config/

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `sources.py` | 18 | OPERATOR | clean_text (indirectly via host map) | — | URL→cleaner registry |
| `states.py` | 10 | OPERATOR | build_frontend, build_state_browse | — | ALL_STATES constant |
| `yaml_loader.py` | 56 | OPERATOR | _mapping_overrides, match_profession | test_yaml_loader.py | safe_load_unique guard |

---

## pipeline/discover/

### OPERATOR (7)

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `_extract.py` | 171 | OPERATOR | build_hierarchy, expand_hierarchy | — | Justia HTML link extractors; still needed for hierarchy crawls |
| `_fetch.py` | 112 | OPERATOR | build_hierarchy, expand_hierarchy, fetch_section_bodies, find_licensing_titles | — | CDP/requests fetch helper |
| `_mapping_overrides.py` | 158 | OPERATOR | apply_llm_candidates, match_profession | test_mapping_overrides.py | reads/writes mapping_overrides.yaml; match_profession and apply_llm_candidates both consume it |
| `build_hierarchy.py` | 271 | OPERATOR | (CLI only) | test_build_hierarchy.py | builds results/hierarchy/<STATE>.json; consumed by match_profession, expand_containers, umbrella_from_citations |
| `expand_containers.py` | 180 | CURATION | (CLI only) | — | depth-expand broad chapters so section-nested professions become visible; documented in CLAUDE.md |
| `match_profession.py` | 396 | OPERATOR | run_for_new_matches (dying), verify_index_reproducibility | test_match_profession.py, test_mapping_overrides.py | maps profession→chapter via patterns + mapping_overrides; core of pull target generation |

> expand_containers is CURATION not OPERATOR because it only runs when the operator is adding a new occupation or repairing a missing corpus. It does not run in the annual refresh_corpus path.

### CURATION (16)

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `_profession_reverse_index.py` | 51 | CURATION | assign_umbrella_scope, llm_scope_fallback, build_umbrella_browse | — | builds profession→section reverse map for umbrella scoping |
| `_scope_rules.py` | 693 | CURATION | suggest_scope_rules, assign_umbrella_scope | test_assign_umbrella_scope.py | per-state regex bundles for the umbrella-scope walker |
| `_state_scope_manifest.py` | 118 | CURATION | assign_umbrella_scope | — | per-state YAML overrides for the scope walker |
| `add_occupation.py` | 221 | CURATION | none | test_add_occupation.py | ONE-command add-occupation orchestrator; documented in handoff plan |
| `apply_llm_candidates.py` | 118 | CURATION | none | — | retargeted 2026-07-01: writes mapping_overrides.yaml from LLM candidate files. Keep — live back-half of the operator loop. |
| `assign_umbrella_scope.py` | 614 | CURATION | none | test_assign_umbrella_scope.py | scope walker; produces umbrella_scope/<STATE>.json consumed by build_frontend via merged_scope |
| `audit_corpus.py` | 190 | CURATION | none | — | post-pull correctness gate; flags wrong-chapter pulls; needed for adding new occupations |
| `expand_hierarchy.py` | 236 | CURATION | none | test_expand_hierarchy.py | depth-expands the hierarchy; run before expand_containers |
| `match_sections.py` | 244 | CURATION | none | test_match_sections.py | LLM-free section-title matcher for section-nested professions; CLAUDE.md documents it |
| `probe_justia.py` | 117 | CURATION | none | test_probe_justia.py | CDP Justia structure prober; useful debugging tool for finding chapters |
| `register_occupation.py` | 167 | CURATION | none | — | auto-drafts professions.yaml entry + parent_corpus; part of the add-occupation loop |
| `suggest_scope_rules.py` | 1116 | CURATION | none | test_suggest_scope_rules.py | LLM-generated StateScopeRules proposals; needed when adding states to umbrella scope |
| `umbrella_coverage_matrix.py` | 170 | CURATION | none | test_umbrella_coverage_matrix.py | materializes (state × profession) → umbrella-sections CSV; audit/QA tool |
| `umbrella_from_citations.py` | 171 | CURATION | none | test_umbrella_from_citations.py | maps cited chapters → Justia URLs for pull_umbrella_text; documented in CLAUDE.md |
| `verify_gap_states.py` | 82 | CURATION | none | — | second-pass LLM check of states marked not-licensed; imports llm_map_profession (dead module) |
| `llm_scope_fallback.py` | 418 | CURATION | none | test_llm_scope_fallback.py | LLM fallback for sections the scope walker can't determine; writes umbrella_scope_llm/<STATE>.json consumed by merged_scope |

> **Note on verify_gap_states.py:** imports `discover.llm_map_profession`, a DELETE target. If llm_map_profession is deleted, this module breaks at import time. Either fix its import or delete this module along with llm_map_profession.

### CONSOLIDATE (4)

These tools' useful output belongs in `corpus_status` (the unified health-check command) or in existing pipeline CLIs. They are not worth keeping as standalone scripts after handoff.

| module | lines | class | imported-by | tests | why / target |
|---|---|---|---|---|---|
| `audit_linkless_chapters.py` | 169 | CONSOLIDATE | none | — | Finds Justia chapters with no hyperlink; useful signal; **fold into corpus_status** |
| `diff_coverage.py` | 78 | CONSOLIDATE | none | — | Diffs coverage CSVs before/after expand; only needed in the LLM-automap loop context; **fold into corpus_status or delete** |
| `harvest_occupations.py` | 270 | CONSOLIDATE | none | — | Reports chapter-label variants and unknown-occupation candidates; useful for occupation discovery; **fold into add_occupation's discovery step** |
| `survey_umbrella_states.py` | 217 | CONSOLIDATE | none | — | Counts umbrella citation patterns per state; session-QA tool; **fold into corpus_status umbrella** |

### DELETE (12)

| module | lines | class | imported-by | tests | why it's safe to delete |
|---|---|---|---|---|---|
| `_llm_candidates/` path | — | DELETE | — | — | Results dir only; no module here |
| `apply_llm_candidates.py` is CURATION — see above | | | | | |
| `audit_llm_candidates.py` | 130 | DELETE | none | — | Guardrail for `llm_map_profession` candidate files; LLM auto-map failed and was superseded. Imports `llm_map_profession` (also deleting). Safe. |
| `cross_ref_siblings.py` | 200 | DELETE | none | — | LLM-confirms sibling-trade corpus reuse; superseded by `mechanical_cross_ref` (LLM-free). No imports. Safe. |
| `discover_occupations.py` | 154 | DELETE | none | — | LLM reads chapter structure to surface untracked occupations; replaced by `add_occupation` + `register_occupation`. No imports. Safe. |
| `fetch_section_bodies.py` | 115 | DELETE | none | — | Fetches section body excerpts to feed `map_state_sections`; that mapper is dead. Uses `_fetch.py`. Safe. |
| `find_licensing_titles.py` | 292 | DELETE | none | test_find_licensing_titles.py | Early LLM experiment: identify licensing titles per state; superseded by build_hierarchy. **Test dies: `tests/test_find_licensing_titles.py`**. |
| `find_umbrella_chapters.py` | 232 | DELETE | none | test_find_umbrella_chapters.py | Old LLM heuristic for finding umbrella chapters by label; superseded by `umbrella_from_citations` (citation-signal, LLM-free). **Test dies: `tests/test_find_umbrella_chapters.py`**. |
| `gap_loop.py` | 173 | DELETE | none | — | LLM audits empty fields vs pulled corpus; useful R&D but not an operator tool; no imports. Safe. |
| `harvest_state_sections.py` | 209 | DELETE | none | — | Scrapes MN/MI section URLs from official sources (revisor.mn.gov, legislature.mi.gov); those states now covered by Justia CDP or corpus_overrides; no imports. Safe. |
| `llm_map_profession.py` | 312 | DELETE | none | — | LLM occupation→chapter mapper (Pass 1); failed and superseded by match_profession + mapping_overrides. **Breaks verify_gap_states if deleted without fixing it**. |
| `map_state_chapters.py` | 206 | DELETE | none | — | LLM maps each chapter to a profession in batch; superseded by hand curation. No imports from outside. Safe. |
| `map_state_sections.py` | 183 | DELETE | none | — | LLM maps sections using cached body excerpts; dead (requires fetch_section_bodies which is also deleting). Safe. |
| `mechanical_cross_ref.py` | 321 | DELETE | none | test_mechanical_cross_ref.py | LLM-free keyword-density cross-ref. Good R&D; but `corpus_overrides.yaml` already captures all confirmed fills, making this tool read-only at this point. No pipeline imports. **Test dies: `tests/test_mechanical_cross_ref.py`**. |
| `suggest_overrides.py` | 237 | DELETE | none | — | LLM suggests which chapter covers a profession for states where label-match fails; superseded by mapping_overrides.yaml hand curation. No imports. Safe. |

> **Ambiguous: mechanical_cross_ref.py** — it is LLM-free and produced the corpus_overrides.yaml fills that closed most trades gaps. It has real value for future occupations. The argument for CURATION: its `--brute-force` mode auto-discovers new sibling fills. Mark owner-decision below.

---

## pipeline/ingest/

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `_trim_health.py` | 28 | OPERATOR | trim_state, preflight | test_trim_degraded.py | poison-detection helper |
| `clean_text.py` | 337 | OPERATOR | (CLI); corpus_profession_for used by nothing yet outside clean | test_corpus_overrides_loud.py | clean stage; reads corpus_overrides.yaml |
| `dedupe_corpora.py` | 99 | CURATION | none | test_dedupe_year_versions.py (partial; test actually imports pull_text) | content-based dedup for already-fetched corpora; needed occasionally after partial harvests |
| `pull_all.py` | 249 | OPERATOR | none | — | resumable batch puller (the corpus-pull driver); used for initial harvest and for refresh_corpus's predecessor |
| `pull_regulations.py` | 100 | CONSOLIDATE | none | — | Pulls admin-rules text via CDP; POC-level (known to miss sections); **fold into pull_text or refresh_corpus when admin-rules source is added** |
| `pull_text.py` | 1989 | OPERATOR | expand_containers, pull_all, pull_regulations, llm_map_profession (dying), results/batches | test_pull_text_drill.py, test_pull_text_runaway_guard.py, test_dedupe_year_versions.py | Core fetch engine. **See official-source analysis below.** |
| `pull_umbrella_text.py` | 214 | OPERATOR | none | test_umbrella_injection.py | pulls umbrella chapters; documented in CLAUDE.md |
| `trim_state.py` | 265 | OPERATOR | (CLI) | test_trim_degraded.py | trim stage |

### pull_text.py — official-source analysis

The file is 1 989 lines. Official-source blocks by line range:

| Block | Lines | State(s) | Keep or Cut |
|---|---|---|---|
| CDP/browser core (lines 96–441) | ~346 | Justia (all states) | **KEEP** — the Justia CDP path |
| PA legis (lines 442–506) | 65 | PA | **KEEP** — only non-Justia state |
| Utah le.utah.gov XML (508–596) | 89 | UT | **CUT** (UT is on Justia; official source was a workaround) |
| South Dakota JSON API (597–665) | 69 | SD | **CUT** |
| Nevada HTML (666–712) | 47 | NV | **CUT** |
| New York OpenLegislation (713–784) | 72 | NY | **CUT** |
| Connecticut HTML (785–814) | 30 | CT | **CUT** |
| WA/VA whole-chapter (815–852) | 38 | WA, VA | **CUT** |
| ME/ID/MO per-section-via-TOC (853–1032) | 180 | ME, ID, MO | **CUT** |
| Maryland GetNext walk (1033–1114) | 82 | MD | **CUT** |
| RI / VT (1115–1195) | 81 | RI, VT | **CUT** |
| Montana nested (1196–1261) | 66 | MT | **CUT** |
| Arizona title-page slice (1262–1321) | 60 | AZ | **CUT** |
| Florida whole-chapter (1322–1345) | 24 | FL | **CUT** |
| Illinois (Justia inline blob) (1346–1428) | 83 | IL | **KEEP** — this is a Justia path, not an official source |

**Estimated cut: ~838 lines** across 13 official-source blocks (UT, SD, NV, NY, CT, WA/VA, ME, ID, MO, MD, RI, VT, MT, AZ, FL). The corresponding `is_*_url` functions, parsers, and `pull_*` helpers all go.

The dispatch table in `pull_state()` (lines 1528–1845) references all these `is_*` checks; those branches also die. Rough net result: ~1 150 lines remain from 1 989.

> **Important:** corpora already fetched from official sources live in `results/text/` and are committed. Only the *fetch code* dies; the data is unaffected.

---

## pipeline/extract/

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `apply_verified_absences.py` | 107 | OPERATOR | (CLI) | test_verified_absences.py | reads verified_absences.yaml, writes market_forces records |
| `discover_schema.py` | 203 | OPERATOR | (CLI) | — | LLM discovers profession-specific fields; needed for any new profession |
| `extract_state.py` | 431 | OPERATOR | extract_state_batch, reverify_evidence, db/load | test_extract_normalize.py, test_umbrella_injection.py | core extractor |
| `extract_state_batch.py` | 392 | OPERATOR | re_extract_queue | — | Anthropic batch extractor |
| `locate_quote.py` | 412 | OPERATOR | extract_state, build_frontend, build_state_browse, db/load | test_locate_quote.py | quote verifier; core operator dep |
| `preflight.py` | 113 | OPERATOR | extract_state_batch | test_preflight.py | validates trimmed corpus before extract |
| `re_extract_queue.py` | 126 | OPERATOR | (CLI) | — | end-to-end re-extract queue runner |
| `standard_model.py` | 690 | OPERATOR | extract_state, extract_state_batch, build_frontend, db/load, build_review_csv, cross_comparison_scorecard | test_standard_model.py, test_integration_schema.py | the schema; core everywhere |
| `compare_models_new_fields.py` | 164 | CONSOLIDATE | none | — | One-off: Haiku vs Sonnet field-density comparison. Useful R&D; **fold into re_extract_queue or delete** after model choice is settled |
| `recategorize_fields.py` | 124 | CONSOLIDATE | none | — | One-off: relabels discovered field categories via LLM. Run once; **delete after next full schema freeze** |
| `repair_unverified.py` | 212 | CURATION | none | — | Re-prompts LLM to fix unverified quotes; periodic QA tool; no pipeline imports |
| `reverify_evidence.py` | 78 | CONSOLIDATE | none | — | Re-runs quote regex check against all structured records. Useful but one-shot; **fold into re_extract_queue** |

---

## pipeline/eval/

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `check_consistency.py` | 161 | OPERATOR | extract_state, refresh_all | — | cross-field invariant guard; called by refresh_all |
| `check_summaries.py` | 81 | CURATION | none | — | Guards per-stage _summary.json completeness; useful diagnostic; no imports from operator path |
| `check_vs_oplr.py` | 96 | OPERATOR | none | — | Validates UT extraction against OPLR ground truth; keep as the held-out-evaluation harness |
| `corpus_status.py` | 418 | OPERATOR | results/batches/_justia_repull.py | test_corpus_status.py | unified health-check; documented in CLAUDE.md |
| `verify_index_reproducibility.py` | 131 | CURATION | none | — | Acceptance gate: profession_index reproducible from committed inputs; run after any mapping change |

---

## pipeline/analyze/

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `classify_novel_direction.py` | 187 | OPERATOR | none (CLI → results/novel_direction_cache.json → publish_analysis) | — | tags novel policies; part of Compare UI pipeline |
| `gen_semantics.py` | 120 | CONSOLIDATE | none | — | One-shot: LLM generates per-profession field semantics yaml. Run once per profession; **fold into discover_schema or delete after all professions done** |
| `publish_analysis.py` | 62 | OPERATOR | none (CLI) | — | stages similarity analysis to Blob/web |
| `similarity.py` | 621 | OPERATOR | none (CLI → results/analysis/) | test_state_similarity.py | core similarity math; feeds Compare UI |

---

## pipeline/map_prep/

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `bucket_text.py` | 580 | OPERATOR | (CLI) | — | Pass 3 LLM bucketing of free-text fields |
| `harmonize_universal.py` | 206 | OPERATOR | (CLI) | — | cross-profession harmonization of universal bucket fields |
| `refresh.py` | 337 | OPERATOR | (CLI) | — | batched refresh of map_prep + bucket_text for many professions |
| `run.py` | 275 | DELETE | none | — | Two-pass LLM normalization (spec + apply). **Superseded by `refresh.py`** (which runs both passes via batches). No imports outside. Safe. |

---

## pipeline/publish/

| module | lines | class | imported-by | tests | why |
|---|---|---|---|---|---|
| `__init__.py` | 0 | OPERATOR | — | — | package marker |
| `_browse_tree.py` | 207 | OPERATOR | build_frontend, build_state_browse | test_browse_tree.py | tree builder for section browse |
| `_justia_clean.py` | 133 | OPERATOR | build_frontend, build_state_browse | test_justia_clean.py | strips Justia nav chrome from section text |
| `blob_upload.py` | 86 | OPERATOR | build_frontend, build_state_browse, build_tag_sheet, publish_analysis, cross_comparison_scorecard | — | Vercel Blob upload helper |
| `build_frontend.py` | 987 | OPERATOR | db/load | test_build_frontend.py | generates per-profession JSON payload |
| `build_gap_matrix.py` | 234 | CONSOLIDATE | none | — | Audit matrix for 5 gap fields; useful QA; **fold into corpus_status** |
| `build_review_csv.py` | 112 | CONSOLIDATE | none | — | Reviewer markup CSV; one-off QA; **fold into corpus_status or delete** |
| `build_state_browse.py` | 362 | OPERATOR | (CLI); called by refresh_all | — | per-state aggregate blob; part of operator surface |
| `build_tag_sheet.py` | 365 | OPERATOR | (CLI); called by refresh_all | — | tag-sheet blob; part of operator surface |
| `build_umbrella_browse.py` | 335 | OPERATOR | (CLI); called by refresh_all | — | umbrella browse blob; part of operator surface |
| `cross_comparison_scorecard.py` | 252 | CONSOLIDATE | none | — | Markdown scorecard comparing field population across professions; **fold into corpus_status or refresh_all** |
| `db/__init__.py` | 0 | OPERATOR | — | — | package marker |
| `db/load.py` | 631 | OPERATOR | none | — | ETL into Postgres; part of the publish surface |
| `generate_field_dictionary.py` | 360 | OPERATOR | (CLI); called by refresh_all | — | generates field dictionary docs |
| `refresh_all.py` | 219 | OPERATOR | (CLI) | — | orchestrates all downstream publish stages |
| `state_similarity.py` | 186 | CONSOLIDATE | none | test_state_similarity.py | early similarity reporter (markdown); superseded by analyze/similarity.py + publish_analysis; **fold into analyze/ or delete** |

---

## pipeline/notes/ and pipeline/logs/

| item | class | why |
|---|---|---|
| `notes/FIELDS.md`, `FIELD_AUDIT.md`, `LEARNINGS.md`, `PIPELINE_STATE.md` | OWNER-DECISION | Working notes; not code. Owner decides if they want to keep or clean up. |
| `notes/archive/podiatry_pdf_regression.py` (189 lines) | DELETE | One-off regression test for a now-resolved PDF issue. No imports from live code. |
| `notes/archive/trim_audit.py` (133 lines) | DELETE | One-off trim-stage audit script. No imports from live code. |
| `notes/archive/*.md` | DELETE | Archived reports; superseded. |
| `logs/` | OWNER-DECISION | Runtime log files. Keep for a few days post-handoff; then clean. Not code. |

---

## pipeline/results/batches/ (batch driver scripts)

All 7 scripts are DELETE-AFTER-TASK-2 (will be replaced by `refresh_corpus`).

| script | lines | class | imported-by | why |
|---|---|---|---|---|
| `_cdp_audit.py` | 81 | DELETE-AFTER-TASK-2 | none | imports `pull_text.bad_section_text`; CDP audit runner |
| `_cdp_downstream.py` | 135 | DELETE-AFTER-TASK-2 | none | runs clean→trim→extract after a CDP grind |
| `_cdp_grind.py` | 163 | DELETE-AFTER-TASK-2 | none | the main CDP pull-all driver; replaced by `pull_all.py` + `refresh_corpus` |
| `_cdp_progress.py` | 53 | DELETE-AFTER-TASK-2 | none | progress reporter for the grind |
| `_cdp_umbrella_resolve.py` | 82 | DELETE-AFTER-TASK-2 | none | resolves umbrella chapters via CDP |
| `_cdp_xref_audit.py` | 80 | DELETE-AFTER-TASK-2 | none | xref audit runner |
| `_justia_repull.py` | 102 | DELETE-AFTER-TASK-2 | none | imports `corpus_status.is_index_only`; targeted re-pull driver |

---

## .scratch/

All files under `.scratch/jul1_prep/` are session-scoped working files (JSON worklists, prep notes, queue files). DELETE-AFTER-TASK-2. No production code imports from `.scratch/`.

---

## pipeline/config/_disabled/

| file | class | why |
|---|---|---|
| `wa_disciplinary_umbrella.yaml` | OWNER-DECISION | The WA umbrella mechanism was shipped via a different path (state_scope/WA.yaml + `assign_umbrella_scope`). This file is the abandoned YAML attempt. Probably delete; owner should confirm it's not referenced. |

---

## docs/runbooks/

| file | class | why |
|---|---|---|
| `adding_a_new_occupation.md` | KEEP | Step-by-step operator runbook; references live tools (add_occupation, refresh_all, match_profession, build_hierarchy). Core handoff doc. |
| `automation_handoff_assessment.md` | KEEP | Honest stage-by-stage automation assessment; still accurate; useful for Utah OPLR. |
| `wa_umbrella_mechanism.md` | KEEP | Explains the WA supplementary-umbrella mechanism shipped 2026-06-30. |
| `verified_absences.md` | KEEP | Explains verified_absences.yaml and apply_verified_absences; operator needs this. |
| `occupation_coverage_handoff_plan.md` | KEEP | Pairs with adding_a_new_occupation; addresses post-handoff extension by OPLR. |
| `automation_refinements_plan_2026-06-26.md` | SUPERSEDED-DELETE | Planning doc for the gap_loop/pull_regulations/discover_occupations automation arc. Those tools are either dead or parked. Gap_loop not in operator surface. |
| `session_2026-06-30_handoff.md` | SUPERSEDED-DELETE | Session-state file from Jun 30. Now stale; superseded by MEMORY.md. |
| `trades_remaining_2026-06-24.md` | SUPERSEDED-DELETE | "What's left on trades" as of Jun 24; trades are now live. |
| `trades_gap_filling_playbook.md` | OWNER-DECISION | Documents cross_ref_siblings / mechanical_cross_ref / audit_corpus techniques. Useful reference if future occupations use the same playbook. Keep if those tools stay (see owner-decision on mechanical_cross_ref). |
| `trades_shape_model_2026-06-29.md` | OWNER-DECISION | Documents the data-model mismatch for trades regulatory shape (trades don't fit the standard licensing-regime model). Keep if the issue is unresolved at handoff. |

---

## Deletion order

### Can delete immediately (after Task-1 commits land)

1. `pipeline/run.py` — zero imports, zero tests, pure stub.
2. `pipeline/discover/audit_llm_candidates.py` — LLM auto-map dead; imports llm_map_profession (also going).
3. `pipeline/discover/cross_ref_siblings.py` — superseded by mechanical_cross_ref.
4. `pipeline/discover/discover_occupations.py` — superseded by add_occupation + register_occupation.
5. `pipeline/discover/fetch_section_bodies.py` — feeds dead map_state_sections only.
6. `pipeline/discover/find_licensing_titles.py` — early LLM experiment; **drops test_find_licensing_titles.py**.
7. `pipeline/discover/find_umbrella_chapters.py` — superseded by umbrella_from_citations; **drops test_find_umbrella_chapters.py**.
8. `pipeline/discover/gap_loop.py` — not operator surface; no imports.
9. `pipeline/discover/harvest_state_sections.py` — MN/MI official-source scraper; those states now Justia.
10. `pipeline/discover/llm_map_profession.py` — LLM auto-map failed; **breaks verify_gap_states** (fix or co-delete).
11. `pipeline/discover/map_state_chapters.py` — LLM chapter mapper; dead.
12. `pipeline/discover/map_state_sections.py` — LLM section mapper; dead.
13. `pipeline/discover/suggest_overrides.py` — LLM override suggester; superseded by mapping_overrides.yaml.
14. `pipeline/map_prep/run.py` — superseded by map_prep/refresh.py.
15. `pipeline/notes/archive/podiatry_pdf_regression.py` — no imports; archived.
16. `pipeline/notes/archive/trim_audit.py` — no imports; archived.
17. `docs/runbooks/automation_refinements_plan_2026-06-26.md`
18. `docs/runbooks/session_2026-06-30_handoff.md`
19. `docs/runbooks/trades_remaining_2026-06-24.md`

**Co-delete or fix:** If `llm_map_profession.py` is deleted, also delete or repair `verify_gap_states.py` (it imports `discover.llm_map_profession`). `run_for_new_matches.py` should be deleted simultaneously (it also belongs to the LLM-automap loop and carries `test_run_for_new_matches.py`).

### DELETE-AFTER-TASK-2 (once refresh_corpus ships)

- `pipeline/results/batches/_cdp_audit.py`, `_cdp_downstream.py`, `_cdp_grind.py`, `_cdp_progress.py`, `_cdp_umbrella_resolve.py`, `_cdp_xref_audit.py`, `_justia_repull.py`
- `.scratch/jul1_prep/` — entire directory.

### Pull_text official-source code (DELETE-AFTER-TASK-2, or in Task-1 if desired)

The 838 lines of official-source fetch blocks (UT, SD, NV, NY, CT, WA/VA, ME, ID, MO, MD, RI, VT, MT, AZ, FL) in `pull_text.py` can be cut safely — the data already exists in `results/text/`. Their removal requires editing `pull_state()` to drop the corresponding `if is_*_url` dispatch branches. No tests specifically exercise these paths (the pull_text tests are for `extract_child_links`, `_dedupe_year_versions`, and the runaway guard — all Justia paths).

---

## Tests that die with deletions

| test file | dies because | what to do |
|---|---|---|
| `tests/test_find_licensing_titles.py` | imports `discover.find_licensing_titles._extract_titles` (module deleted) | delete the test |
| `tests/test_find_umbrella_chapters.py` | imports `discover.find_umbrella_chapters.find_for_state` (module deleted) | delete the test |
| `tests/test_mechanical_cross_ref.py` | imports `discover.mechanical_cross_ref` — if mechanical_cross_ref is deleted | conditional on owner-decision |
| `tests/test_run_for_new_matches.py` | imports `pipeline.run_for_new_matches` (module deleted) | delete the test |
| `tests/test_state_similarity.py` | imports `publish.state_similarity` — if that module is deleted (currently CONSOLIDATE) | conditional on owner-decision |
| `tests/test_suggest_scope_rules.py` | imports `discover.suggest_scope_rules` — if that module is deleted (currently CURATION, keep) | no action needed |
| `tests/test_llm_scope_fallback.py` | imports `discover.llm_scope_fallback` — if that module is deleted (currently CURATION, keep) | no action needed |

---

## Needs-owner-decision (SHORT LIST)

Only 4 items are genuinely ambiguous. Everything else above is evidence-clear.

1. **`pipeline/discover/mechanical_cross_ref.py`** (321 lines, test: `test_mechanical_cross_ref.py`) — LLM-free keyword density cross-ref. All confirmed fills are already in `corpus_overrides.yaml`, so the tool is read-only now. If OPLR will add new occupations, the `--brute-force` mode is useful for discovering sibling fills automatically. **Recommend CURATION** if adding occupations is in scope; **DELETE** if not.

2. **`pipeline/discover/verify_gap_states.py`** (82 lines) — LLM second-pass check of states the automap marked not-licensed. Currently broken by its import of `llm_map_profession` (also a DELETE). If deleting llm_map_profession: co-delete this or fix the import. If CURATION is needed for future occupation gaps: fix the import to call `match_profession` or `llm_map_profession`'s logic directly. **Recommend co-delete with llm_map_profession.**

3. **`docs/runbooks/trades_gap_filling_playbook.md`** — documents techniques used to fill trades corpus gaps. Relevant if future occupations use the same gap-filling playbook (sibling cross-ref, audit_corpus, probe_justia). **Recommend KEEP** if the tools stay (audit_corpus, probe_justia are CURATION); otherwise superseded.

4. **`pipeline/config/_disabled/wa_disciplinary_umbrella.yaml`** — abandoned YAML attempt at the WA umbrella; the live mechanism is in `state_scope/WA.yaml`. Probably dead but owner should confirm before deleting.

---

## Surprising findings

1. **`run_for_new_matches.py` has a test** (`test_run_for_new_matches.py`) that will die when the module is deleted. The test exercises the coverage-diff logic; that logic has no other consumer.

2. **`merged_scope.py` and `scope_sources.py` are live operator dependencies** — `build_frontend`, `build_state_browse`, `build_umbrella_browse`, and `db/load` all import them. They were introduced as part of the umbrella scope infrastructure and look like experimental modules from the name, but they are not deletable without breaking the publish pipeline.

3. **`map_prep/run.py` is superseded** — `map_prep/refresh.py` handles the same work via Anthropic batches; `run.py` is the synchronous predecessor. Nothing imports it. Safe immediate delete.

4. **`apply_llm_candidates.py` was _just_ retargeted** (per git status at session start and the module's own docstring) to write `mapping_overrides.yaml` instead of `profession_index` directly. It is live curation infrastructure, not dead LLM-automap code — do not delete it.

5. **`pull_text.py` IL block (lines 1346–1428) is a Justia path**, not an official-source path — it handles the Justia whole-ILCS-act page shape. Keep it even in a Justia-only trim.

6. **`verify_gap_states.py` silently breaks if `llm_map_profession.py` is deleted** — it has a top-level import `from discover.llm_map_profession import ...`. Fix or co-delete.
