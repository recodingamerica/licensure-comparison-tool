# Hardcoded Config Audit — 2026-07-01

Scope: all `.py` under `pipeline/` (excluding `.venv/`, `__pycache__/`, `results/` JSON data),
`pipeline/results/batches/*.py`, `.scratch/*.py`. Excludes anything already externalized in
`config/limits.yaml`, `config/professions.yaml`, `config/state_structure.yaml`, `config/prompts.yaml`,
`config/loaders.py`, `config/sources.py`, `config/states.py`.

---

## SECURITY: No Secrets in Code (Clean)

No hard-coded tokens, passwords, or key values were found. All sensitive credentials are
read from environment variables (`ANTHROPIC_API_KEY`, `BLOB_READ_WRITE_TOKEN`,
`NY_OPENLEG_KEY`, `SCRAPERAPI_KEY`, `RESIDENTIAL_PROXY`). The `.env` files are not
committed. **One item to note for handoff:**

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/discover/_fetch.py:30` | `abigail.haddad@gmail.com` | Contact email in the crawler's `UA_BOT` User-Agent string | Move to config or env (`SCRAPE_CONTACT_EMAIL`); the Utah OPLR operator should use their own address |

---

## Category 1 — LLM Model IDs / Tiers

Every LLM call site hardcodes a model string. A handoff operator changing models, or
switching to a cheaper/faster tier, must touch ~14 files instead of one config entry.

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/_batch.py:26` | `claude-sonnet-4-6` | Batch API submission model | **Move to config** (new `config/models.yaml` or `limits.yaml:models`) |
| `pipeline/_llm.py:10` | `claude-sonnet-4-6` | Default for synchronous LLM calls | Move to config |
| `pipeline/map_prep/refresh.py:59` | `claude-sonnet-4-6` | Map-prep refresh | Move to config |
| `pipeline/map_prep/harmonize_universal.py:56` | `claude-sonnet-4-6` | Harmonization | Move to config |
| `pipeline/map_prep/bucket_text.py:96` | `claude-sonnet-4-6` | Bucket-text classification | Move to config |
| `pipeline/map_prep/run.py:42` | `claude-sonnet-4-6` | Map-prep run | Move to config |
| `pipeline/discover/audit_corpus.py:47` | `claude-sonnet-4-6` | Corpus audit | Move to config |
| `pipeline/discover/register_occupation.py:33` | `claude-sonnet-4-6` | Occupation registration | Move to config |
| `pipeline/analyze/gen_semantics.py:40` | `claude-sonnet-4-6` | Semantic label generation | Move to config |
| `pipeline/analyze/classify_novel_direction.py:48` | `claude-sonnet-4-6` | Novel direction classification | Move to config |
| `pipeline/extract/discover_schema.py:37` | `claude-sonnet-4-6` | Schema discovery default | Move to config |
| `pipeline/extract/extract_state.py:58` | `claude-sonnet-4-6` | State extraction default | Move to config |
| `pipeline/extract/recategorize_fields.py:28` | `claude-sonnet-4-6` | Field recategorization | Move to config |
| `pipeline/ingest/trim_state.py:48` | `claude-haiku-4-5-20251001` | Trim classifier (intentionally cheap) | Move to config (separate tier key) |
| `pipeline/extract/repair_unverified.py:47` | `claude-haiku-4-5-20251001` | Quote repair (cheap tier) | Move to config |
| `pipeline/extract/compare_models_new_fields.py:38` | `claude-haiku-4-5-20251001` | Model comparison (dev tool) | Leave — dev tooling |
| `pipeline/discover/suggest_scope_rules.py:65` | `claude-opus-4-7` | Scope rules (intentionally flagship) | Move to config |
| `pipeline/discover/llm_scope_fallback.py:64` | `claude-opus-4-7` | Scope fallback (flagship) | Move to config |

**Highest-value recommendation:** Add a `config/models.yaml` with three keys (`default`, `cheap`, `flagship`) that every call site reads. This is the single highest-value handoff change — a Utah OPLR operator paying their own API bill should be able to change all 16 call sites in one edit.

---

## Category 2 — URLs / Hosts / Endpoints

### Endpoints that belong in config

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/discover/probe_justia.py:33` | `http://localhost:9222` | CDP default URL | Already overridable via `JUSTIA_CDP_URL` env — acceptable; document in `config/models.yaml` or a new `config/env_vars.md` |
| `pipeline/discover/build_hierarchy.py:80` | `https://www.revisor.mn.gov/statutes/` | MN official fallback URL | Move to `targets.csv` (or `OFFICIAL_FALLBACKS` dict → `state_structure.yaml`) |
| `pipeline/discover/build_hierarchy.py:81` | `https://www.palegis.us/statutes/unconsolidated` | PA official fallback URL | Move to `targets.csv` / `state_structure.yaml` |

### Official-source host constants in pull_text.py (fine as-is)

These are tightly coupled to their respective parsers and are best left co-located with
the parser code they serve. They are NOT handoff risks because changing them would also
require parser changes. Listing for completeness:

`PA_LEGIS_HOST`, `UTAH_LE_HOST`, `SD_API_HOST`, `NV_HOST`, `CT_HOST` (`cga.ct.gov`),
`WA_HOST`, `ME_HOST`, `MO_HOST`, `MD_HOST`, `VT_HOST`, `MT_HOST`, `AZ_HOST`, `FL_HOST`
— all in `pipeline/ingest/pull_text.py`. **Leave as-is (mechanical).**

### Justia base URL inline references (fine as-is)

`"law.justia.com"` appears as a domain check string in `pull_text.py`, `audit_linkless_chapters.py`,
`umbrella_from_citations.py`, `_browse_tree.py`, `db/load.py`, `clean_text.py`. These are
predicate strings, not endpoints to configure. **Leave as-is.**

### NY OpenLeg API

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/ingest/pull_text.py:725` | `https://legislation.nysenate.gov/api/3` | NY OpenLeg REST API base | Leave — tightly coupled to the NY parser; version is part of the path |

---

## Category 3 — Hardcoded Absolute Paths

These all break the moment the repo is cloned to a different machine. This is the **most
urgent handoff issue** — the batch/scratch drivers are the operator's main tools for
large harvests.

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/results/batches/_cdp_grind.py:35` | `/Users/abigailhaddad/Documents/repos/utah` | `ROOT` path | Replace with `Path(__file__).resolve().parents[3]` (same pattern as `pipeline/paths.py`) |
| `pipeline/results/batches/_cdp_downstream.py:20` | `/Users/abigailhaddad/Documents/repos/utah` | `ROOT` path | Same fix |
| `pipeline/results/batches/_cdp_progress.py:7` | `/Users/abigailhaddad/Documents/repos/utah` | `ROOT` path | Same fix |
| `pipeline/results/batches/_cdp_xref_audit.py:22` | `/Users/abigailhaddad/Documents/repos/utah` | `ROOT` path | Same fix |
| `pipeline/results/batches/_cdp_grind.py:36` | `/Users/abigailhaddad/.../pipeline/.venv/bin/python` | `PY` path derived from `ROOT` | Self-heals once `ROOT` is fixed |
| `pipeline/results/batches/_cdp_downstream.py:21` | `/Users/abigailhaddad/.../pipeline/.venv/bin/python` | `PY` path | Self-heals |
| `pipeline/results/batches/_cdp_audit.py:19` | `/Users/abigailhaddad/Documents/repos/utah` | `ROOT` path | Same fix |
| `pipeline/results/batches/_cdp_umbrella_resolve.py:12` | `/Users/abigailhaddad/Documents/repos/utah` | `ROOT` path | Same fix |
| `pipeline/results/batches/_justia_repull.py:18` | `/Users/abigailhaddad/Documents/repos/utah` | `ROOT` path | Same fix |
| `.scratch/overnight_repull.py:30` | `Path("/Users/abigailhaddad/Documents/repos/utah")` | `ROOT` path | Same fix (`.scratch` scripts are operator tools) |

**Fix pattern** — replace each `ROOT = "/Users/abigailhaddad/Documents/repos/utah"` with:
```python
ROOT = Path(__file__).resolve().parents[N]  # adjust N per file depth
```
or import `from pipeline.paths import REPO_ROOT` if that constant is added to `paths.py`
(it currently has `PIPELINE_DIR` and `PIPELINE_ROOT`; `PIPELINE_ROOT` already exists and
equals the repo root).

### /tmp paths (acceptable)

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/ingest/pull_text.py:162` | `/tmp/justia_cdp_pull.lock` | CDP mutex lock file | Leave — `/tmp` is correct for a runtime lock |
| `pipeline/run_for_new_matches.py:25` | `/tmp/coverage_before.csv` | Coverage snapshot | Leave — explicit convention documented in `diff_coverage.py` |
| `pipeline/discover/diff_coverage.py:20` | `/tmp/coverage_before.csv` | Coverage snapshot | Leave |

---

## Category 4 — Hardcoded Profession / State Lists

### Lists that duplicate what `core_professions()` / `professions.yaml` already express

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/publish/build_state_browse.py:59–63` | 12-profession `PROFESSIONS` list | Controls which professions appear in the state-browse view | **Derive from `professions.yaml`** (or `core_professions()` + an explicit "browse-eligible" flag); currently drifts from the published set |
| `pipeline/publish/db/load.py:68–70` | 6-profession `PROFESSIONS` list | Controls which professions load into Postgres | Same — should derive from `core_professions()` or a DB-eligible flag |
| `pipeline/eval/corpus_status.py:64–67` | 7-profession `PUBLISHED` set | Controls `corpus_status umbrella` + published-flag logic | Move to `professions.yaml` as a `published: true` attribute; let `corpus_status` load it dynamically |
| `pipeline/results/batches/_cdp_grind.py:44–45` | 7-profession `PUBLISHED` set | Skips already-complete professions during harvest | Derive from `corpus_status` published set (once that's dynamic) or import from a shared constant |

**Note:** `pipeline/publish/cross_comparison_scorecard.py:141` already correctly uses
`PROFESSIONS = core_professions()` — that pattern should be applied to the three files
above.

### SPECIAL_TARGET_IDS and OFFICIAL_FALLBACKS in build_hierarchy.py

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/discover/build_hierarchy.py:71–76` | `SPECIAL_TARGET_IDS = {"NY": ..., "CA": ..., "IL": ..., "MD": ...}` | Which states get a non-default target-id from `targets.csv` | Move to `targets.csv` as a `is_default: true/false` column, or to `state_structure.yaml` |
| `pipeline/discover/build_hierarchy.py:79–82` | `OFFICIAL_FALLBACKS = {"MN": ..., "PA": ...}` | Official-source fallback for states Justia 404s | Move to `targets.csv` (these states already have entries; add a `hierarchy_override_url` column) |

---

## Category 5 — Timeouts / Retry Counts / Batch Sizes

Items below are mostly pure mechanics. Ones marked **candidate** are worth noting for
handoff because an operator tuning crawl speed or API costs would want to change them.

| File:line | Literal | What it is | Leave / Candidate |
|---|---|---|---|
| `pipeline/discover/_fetch.py:35` + `pipeline/ingest/pull_text.py:43` | `TIMEOUT = 25` | HTTP request timeout (seconds) | Leave — mechanical |
| `pipeline/ingest/pull_text.py:110` | `_UNBLOCK_TIMEOUT = 75` | Timeout for proxy/CDP fetches | Leave — mechanical |
| `pipeline/ingest/pull_text.py:283` | `CHALLENGE_WAIT = 360` | Seconds to wait for a human to re-solve a Cloudflare challenge | **Candidate** — an operator on a slow connection may need to increase; could go in `limits.yaml` |
| `pipeline/ingest/pull_text.py:186` | `3600` (1 h) | CDP lock abort threshold | Leave — safety net, not a tuning knob |
| `pipeline/_batch.py:52` | `POLL_INTERVAL_SECS = 30` | Batch API polling interval | Leave — mechanical |
| `pipeline/_llm.py:148` | `backoff_base: float = 1.5` | LLM retry backoff multiplier | Leave — mechanical |
| `pipeline/ingest/trim_state.py:50` | `MAX_RETRIES = 2` | LLM call retries | Leave — mechanical |
| `pipeline/extract/extract_state.py:59` | `MAX_RETRIES = 2` | LLM call retries | Leave — mechanical |
| `pipeline/extract/discover_schema.py:38` | `MAX_RETRIES = 2` | LLM call retries | Leave — mechanical |
| `pipeline/map_prep/run.py:193` | `APPLY_CHUNK_SIZE = 10` | Fields per map-prep apply call | Leave — tuned to 32k token budget |
| `pipeline/discover/expand_containers.py:70` | `CHECKPOINT_EVERY = 5` | CDP checkpoint frequency | Leave — mechanical |
| `pipeline/results/batches/_justia_repull.py:22` | `SECTION_CAP = 400` | Runaway guard for re-pull | **Candidate** — differs from grind's 5000; should be consistent or documented |
| `pipeline/results/batches/_cdp_grind.py:50` | `SECTION_CAP = 5000` | Runaway guard for main harvest | **Candidate** — tuned per context; note the inconsistency with repull's 400 |
| `.scratch/overnight_repull.py:33` | `GUARD = 1500` | Runaway guard for overnight pull | **Candidate** — third distinct value; all three should be reconciled |

---

## Category 6 — Thresholds / Magic Numbers with Policy Meaning

These numbers shape what output looks like or which results are surfaced. They are the
closest to true config (affects analysis conclusions, not just mechanics).

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/analyze/similarity.py:48` | `RARE_SHARE = 0.20` | Kind outlier: value held by ≤20% of states | **Move to `limits.yaml`** — determines what the UI labels "novel" |
| `pipeline/analyze/similarity.py:49` | `STRINGENCY_Z = 1.5` | Stringency outlier: \|z\| threshold | **Move to `limits.yaml`** |
| `pipeline/analyze/similarity.py:125` | `share <= 0.15` | Lower band for "very rare" in spread classification | Move to `limits.yaml` |
| `pipeline/analyze/similarity.py:127` | `share <= 0.33` | Upper band for "rare" | Move to `limits.yaml` |
| `pipeline/analyze/similarity.py:483` | `drivers[:8]` | Top-N similarity drivers shown per state | Move to `limits.yaml` or leave (display cap) |
| `pipeline/analyze/similarity.py:484` | `drive < 0.05` | Near-uniform driver cutoff | Move to `limits.yaml` |
| `pipeline/discover/mechanical_cross_ref.py:113` | `DENSITY = 8` | Cross-ref keyword hit count to call a corpus a "sibling" | **Move to `limits.yaml`** — affects which states get cross-ref mapped |
| `pipeline/discover/add_occupation.py:48` | `MIN_PUBLISH = 10` | States needed for auto-publish eligibility | Already mirrors `MIN_STATES_FOR_CORE` in `paths.py:33` — should be a single constant; consolidate in `limits.yaml` |
| `pipeline/paths.py:33` | `MIN_STATES_FOR_CORE = 10` | Core profession threshold | **Move to `limits.yaml`** — same value as `MIN_PUBLISH`; one source |
| `pipeline/publish/cross_comparison_scorecard.py:162` | `pct >= 0.8` | ✓ threshold in scorecard (≥80% states populated) | Leave — matches Atharv's PDF definition; changing it misaligns with the original |
| `pipeline/eval/corpus_status.py:229` | `n <= 2` (THIN) | Max sections for THIN classification | Move to `limits.yaml` |
| `pipeline/eval/corpus_status.py:229` | `medians.get(r["prof"], 0) >= 10` | Peer-median floor for THIN to apply | Move to `limits.yaml` |
| `pipeline/eval/corpus_status.py:135` | `< 2500` | Max chars for INDEX_ONLY classification | Move to `limits.yaml` |
| `pipeline/discover/migrate_mapping_overrides.py:58–59` | `MIN_ADDS = 150`, `MAX_ADDS = 310` | Tripwire range for one-time migration | Leave — one-time migration tool; values baked into the 2026-07-01 snapshot context |
| `pipeline/discover/harvest_occupations.py:204` | `default=3` | Min states for candidate occupation surfacing | Leave — CLI default, operator can override |
| `pipeline/extract/locate_quote.py:106` | `_MIN_SEGMENT_LEN = 8` | Minimum chars for a quote segment to be matched | Leave — mechanical text-matching floor |
| `pipeline/publish/state_similarity.py:176` | `scored[:3]` | Top-N novel states in state-level report | Leave — display formatting |

---

## Category 7 — Other Embedded Config

### Hardcoded date in file path

| File:line | Literal | What it is | Recommendation |
|---|---|---|---|
| `pipeline/discover/migrate_mapping_overrides.py:63` | `"mapping_migration_drift_2026-07-01.md"` | One-time migration report output path | Leave — this is a one-time migration script; the date is intentional |

### Contact email in UA string

See SECURITY section above (`pipeline/discover/_fetch.py:30`).

### Hardcoded `PUBLISHED` profession set duplicated in batch scripts

See Category 4 above. The grind's `PUBLISHED` set (`_cdp_grind.py:44`) differs from
`corpus_status.py`'s (`dietetics` included in `corpus_status`, absent in `build_state_browse`
since the state-browse list covers 12 professions). This inconsistency is a handoff risk.

---

## Prioritized "Should Externalize" Shortlist

Ordered by handoff risk (breaks-on-any-other-machine first, then policy-changing ones).

### P0 — Break on any non-Abigail machine (fix before handoff)

1. **7 files in `results/batches/`** + `1 file in .scratch/` — all have `ROOT = "/Users/abigailhaddad/..."`.
   Fix: replace each with `Path(__file__).resolve().parents[N]`.
   Files: `_cdp_grind.py`, `_cdp_downstream.py`, `_cdp_progress.py`, `_cdp_xref_audit.py`,
   `_cdp_audit.py`, `_cdp_umbrella_resolve.py`, `_justia_repull.py`, `.scratch/overnight_repull.py`.

2. **Contact email in UA string** — `pipeline/discover/_fetch.py:30` hardcodes
   `abigail.haddad@gmail.com` in the crawler's `User-Agent`. The Utah OPLR operator should
   replace this with their own contact.

### P1 — LLM model IDs (all 16 call sites)

3. **All `claude-*` model literals** — add `config/models.yaml`:
   ```yaml
   default: claude-sonnet-4-6       # most extraction and map-prep tasks
   cheap:   claude-haiku-4-5-20251001  # trim, quote repair (volume tasks)
   flagship: claude-opus-4-7        # scope rules, scope fallback (quality-critical)
   ```
   Then each call site does `load_models()["default"]`. A Utah OPLR operator on a budget
   can downgrade in one file.

### P2 — Published-profession list duplication (4 files out of sync)

4. **`PUBLISHED` / `PROFESSIONS` lists** in `build_state_browse.py`, `db/load.py`,
   `corpus_status.py`, `_cdp_grind.py`. These four lists differ from each other (different
   subsets, different lengths). Add a `published: true` flag to `professions.yaml` entries
   and let each consumer derive its list from that flag.

### P3 — Similarity / outlier thresholds (shape UI output)

5. **`RARE_SHARE = 0.20`, `STRINGENCY_Z = 1.5`, band thresholds `0.15`/`0.33`** in
   `pipeline/analyze/similarity.py` — move to `limits.yaml:similarity` section. These
   determine what gets labeled "novel" in the frontend. Utah OPLR may want to tune
   sensitivity.

6. **`DENSITY = 8`** in `mechanical_cross_ref.py` — moves to `limits.yaml:cross_ref`.
   Controls which states get cross-ref occupation mappings.

7. **`MIN_STATES_FOR_CORE` (paths.py) / `MIN_PUBLISH` (add_occupation.py)** — these are
   the same value (10) in two places. Consolidate into one `limits.yaml:discovery.min_states_for_core`
   entry.

### P4 — Corpus health thresholds

8. **`INDEX_ONLY` 2500-char limit** (`corpus_status.py:135`) and **THIN n ≤ 2**
   (`corpus_status.py:229`) — move to `limits.yaml:corpus_health` for operator visibility.

### Leave as-is (mechanical)

The following are intentionally NOT in config per the `limits.yaml` comment convention —
they are operational mechanics that don't determine what data survives:

- HTTP/CDP timeouts (`TIMEOUT = 25`, `_UNBLOCK_TIMEOUT = 75`, `CHALLENGE_WAIT = 360`, CDP 1h abort)
- Retry counts (`MAX_RETRIES = 2` in trim/extract/discover_schema)
- LLM backoff (`backoff_base = 1.5`)
- Batch poll interval (`POLL_INTERVAL_SECS = 30`)
- Apply chunk size (`APPLY_CHUNK_SIZE = 10`)
- CDP checkpoint (`CHECKPOINT_EVERY = 5`)
- Quote segment floor (`_MIN_SEGMENT_LEN = 8`)
- Scorecard 80% threshold (matches Atharv's PDF definition)
- `migrate_mapping_overrides.py` tripwire (one-time migration artifact)
- `/tmp` paths (correct for runtime locks and CLI conventions)
- Official-source host constants co-located with parsers

---

## Count Summary

| Category | Findings |
|---|---|
| 1 — LLM model IDs | 17 (16 production call sites + 1 dev tool left as-is) |
| 2 — URLs / hosts | 3 belong in config; ~15 official-source host constants left as-is |
| 3 — Hardcoded absolute paths | 8 in `results/batches/`, 1 in `.scratch/` |
| 4 — Profession / state lists | 4 hardcoded PROFESSIONS/PUBLISHED lists; 2 SPECIAL_TARGET_IDS maps |
| 5 — Timeouts / retry counts | 3 runaway-guard inconsistencies (candidate); rest leave as-is |
| 6 — Thresholds with policy meaning | 8 candidates for `limits.yaml`; 8 left as-is |
| 7 — Other | 1 contact email (handoff risk); 1 date-in-path (one-time, leave) |

**Single highest-value recommendation:** Fix the 8 `ROOT = "/Users/abigailhaddad/..."` literals
in `results/batches/` and `.scratch/overnight_repull.py` — these are the operator's primary
harvest tools and they will silently fail on any other machine, breaking the entire handoff
workflow before it starts.
