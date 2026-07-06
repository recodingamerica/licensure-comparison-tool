# Runbook — adding a new occupation (end-to-end, statute → live frontend)

What it takes to take a profession from "not in the system" to a fully-functional
page on the published site. Ordered; each stage reads the previous stage's output.
The cheap/deterministic stages are safe to re-run; the **LLM stages** (extract,
map_prep) cost money and run deliberately.

> TL;DR for a profession that already has a `professions.yaml` entry and pulled
> corpora (like the 4 trades): **map_prep → edit `build_state_browse.py` → `refresh_all --professions … --deploy`.** Everything earlier is already done.

---

## 0. Register the profession (config — one-time)
- **`pipeline/config/professions.yaml`** — add an entry: `display`, `abbrev`
  (3-letter badge), `family` (health | building_design | business | public_safety),
  `patterns` (substrings that match state chapter labels), optional `excludes` /
  `enumeration_aliases`. This is the **single source of truth** — the frontend reads
  display names, families, and the profession list from here (via the published
  blobs); no per-profession code/routes are needed (routes are dynamic `[id]`).
- **`pipeline/config/state_structure.yaml`** — only for states that need a per-state
  override (flat-title section ranges via `section_slug_pattern`, official-source URL
  templates, umbrella scoping). See the OK/LA trade entries for the pattern.

## 1. Match → profession_index (deterministic, no LLM, no fetch)
- `python -m pipeline.discover.match_profession --profession <P>` builds
  `results/profession_index/<P>.json` (which chapter/section each state maps to),
  applying `state_structure.yaml` and `config/mapping_overrides.yaml` overrides.
- **Re-running is safe.** Manual mapping decisions live in
  `pipeline/config/mapping_overrides.yaml` — they are applied as the last
  transformation in every build, so re-running the matcher never wipes them.
  **Hand-edit the YAML, never the index JSON** (index JSON is a generated
  artifact), then re-run:
  `python -m pipeline.discover.match_profession --profession <P>`.
  Gate: `pipeline/.venv/bin/python -m pipeline.eval.verify_index_reproducibility`.

## 2. Pull the statute text (Justia/official — the fragile stage)
- `python -m pipeline.ingest.pull_text --profession <P> --states <…> --limit-sections 250`
  writes `results/text/<P>/<state>.json`. Committed to git (no remote bucket).
- **ONE pull per CDP Chrome** — concurrent Justia pulls garble corpora into
  1-section "partials". Now guarded by a flock; still verify counts and use
  `/tmp/guarded_repull.sh P STATE MIN` (restore-HEAD-and-retry) for re-pulls.
  See [[reference_concurrent_pull_corruption]], [[official_source_migration]].
- For a broad multi-profession harvest use `pipeline/results/batches/_cdp_grind.py`.

## 3. Umbrella merge (completeness — discipline/general-provisions)
- Many licensing chapters live under an umbrella whose **shared general-provisions**
  (definitions, board powers, discipline) sit in a separate chapter. If a state's
  record lacks discipline/enforcement, suspect an un-merged umbrella.
  See [[reference_centralized_discipline_pattern]].
- Detect: `pipeline.discover.mechanical_cross_ref` → candidates; resolve umbrella
  URLs with `pipeline.discover.umbrella_from_citations` (then `pipeline.ingest.pull_umbrella_text`);
  the general-provisions chapter is merged into the
  trade corpus (`_umbrella_inject.json` records what was injected). Container map:
  `docs/reports/umbrella_containers_2026-06-24.json` (17 states).

## 4. clean → trim → extract  (extract = LLM)
- `python -m pipeline.ingest.clean_text  --profession <P> [--states …]`  → `clean/`
- `python -m pipeline.ingest.trim_state  --profession <P> [--states …]`  → `trimmed/` (LLM drops irrelevant sections)
- `python -m pipeline.extract.discover_schema --profession <P>` (once) → `discovered/<P>.json`
- `python -m pipeline.extract.extract_state --profession <P> --states <…> [--force]` → `structured/<P>/`
  (for >2 states use `pipeline.extract.extract_state_batch` — ~50% cheaper, durable).
- ⚠️ **Always run clean before trim/extract** after re-pulling, or `clean/` stays
  stale and the new text never reaches the model. See [[reference_pipeline_stage_order]].
- Gate: `python -m pipeline.eval.check_consistency` must be 0 violations.
- A profession becomes "core" (auto-published) once it has **≥10** extracted states
  (`core_professions()` in `pipeline/paths.py`). States that aren't licensed get no
  record — that's correct, not a gap.

## 5. map_prep — choropleth + tag normalization (LLM)
- `python -m pipeline.map_prep.run <P>` (2-pass: spec, then apply) →
  `results/map_prep/<P>/`. Optional for publishing (the Map tab degrades gracefully
  if absent) but needed for the choropleth + tag-sheet inclusion, i.e. parity with
  the 7 already-published professions.

## 6. Build payloads + publish (deterministic)
- **Required edit:** `pipeline/publish/build_state_browse.py` `PROFESSIONS` list —
  add the new profession (this is the one hardcoded list; per-state browse needs it).
- **Optional:** `pipeline/publish/web/src/app/reports/scorecard/page.tsx`
  `PROFESSION_LABELS` — add a short label (else the scorecard shows the raw key).
- `python -m pipeline.publish.refresh_all --professions <P …> [--deploy]`
  builds `web/public/data/<P>.json` + per-state browse, scorecard, tag sheet, state
  browse, uploads to Vercel Blob, and (`--deploy`) runs `npx vercel --prod` from
  `pipeline/publish/web/`. Gates on `check_consistency`. `core_professions()` makes
  scorecard/tag-sheet auto-include the new profession.

## What does NOT need changing (frontend is dynamic)
- No web routes, no profession dropdown code, no display-name code outside
  `professions.yaml` + the optional scorecard label map. `/professions.json` and
  `/states.json` are regenerated from the blobs at prebuild.

---
## DX cheat-sheet — the two handoff workflows (commands)

### A. Tweak a prompt → re-run a profession
1. Edit `pipeline/config/prompts.yaml` (the extraction rules).
2. Re-run the LLM stages for the profession (clean→trim→extract, batch):
   `printf '{"%s": %s}' optometry '["AK","AL",...]' > /tmp/q.json`
   `python -m pipeline.extract.re_extract_queue --queue /tmp/q.json`
   (single state: `python -m pipeline.extract.extract_state --profession optometry --states AK --force`)
3. Gate: `python -m pipeline.eval.check_consistency` (0 violations).
4. Publish: `python -m pipeline.publish.refresh_all --professions optometry --deploy`.

---
### Quick checklist
1. `professions.yaml` entry exists  2. matched → `profession_index`
3. text pulled (+ umbrella merged)  4. clean→trim→extract, ≥10 states, consistency clean
5. `map_prep.run <P>`  6. add to `build_state_browse.py` PROFESSIONS (+ scorecard label)
7. `refresh_all --professions <P …> --deploy`  8. verify on the live site
