# Gap harvest + discovery flywheel (built 2026-07-05/06)

Finds and pulls the licensing law for professions that live **section-nested inside a
broad topical title** (building_inspector in Health & Safety, court_reporter in Government
Code, money_transmitter in Banking) — the ones `build_hierarchy`/`expand_containers` can't
reach because the hierarchy is rooted at each state's *single* licensing title, so anything
in another title is outside the crawl. Then grows the profession list itself.

## Why the hierarchy crawl doesn't reach these

`build_hierarchy` roots each state at its ONE "licensing parent URL" (config/targets.csv,
e.g. CA = Business & Professions Code). Professions housed in other titles (Banking, Gov,
Conservation, HSC…) are structurally invisible — proven: 96% of the Tier-3 gaps did not
resolve from even a broadened `expand_containers`. So we locate by **search**, not crawl.

## The pipeline (each step, in order)

1. **Tier-3 absence recon** → the gap list. `classify_occs.py`-style: for each profession
   with blank cells, Haiku rates state-licensing prevalence (ALWAYS/USUALLY/…); blanks in
   usually-licensed professions = likely gaps. Output: `results/gap_tier3_absence.json`
   (`likely_gap` / `likely_absent` / `sometimes`). ~1,061 likely-gap cells.

2. **Search-driven locator** — `locator_full.py`. Anthropic `web_search` tool (server-side,
   NO CDP) scoped to law.justia.com finds each cell's chapter URL, or null if unlicensed.
   Concurrent (10), checkpointed/resumable. Slug-normalizer fixes dot→hyphen. ~93% of URLs
   verify LIVE; nulls are correct absences (opticians unlicensed in ~22 states, commercial
   bail banned in IL/OR/WI/KY). Output: `results/gap_locator_results.json`.

3. **Null-recovery** — `null_recovery.py`. Re-runs ONLY the nulls with a looser prompt
   ("chapter that addresses it incl. exemption/certification, not just licensure"). Recovers
   exemption chapters (UT optician → Optometry Act) the strict pass skipped. Truly-absent
   states stay null. NOTE: recovered set overlaps existing corpora — review before pulling.

4. **Write targets** — add each located url as a `via=gap_locator` node to
   `config/mapping_overrides.yaml` (batch-write once, not per-call), then
   `match_profession.rebuild_and_write(prof)` regenerates `profession_index/<prof>.json`.

5. **Reuse existing corpora** — `reuse_corpus.py`. ~1/3 of located chapters were ALREADY
   fetched for another profession in that state (osteo → the medicine act we have). Copy
   those sections instead of re-fetching. LLM-free, instant. Cut the pull from 772 → 510.

6. **Pull** — `gap_pull.sh`. Self-healing CDP pull of what's left. ONE state per process
   (Playwright cross-thread bug), flock-guarded (ONE Chrome), skips already-pulled
   (resumable), commits per profession, waits out Chrome-down. `caffeinate -disu`. ~2.8
   min/cell (challenges + big chapters). 0 empties = every located URL hit real law.

7. **Extract** — clean → trim → discover_schema (if missing) → `extract_state_batch`.
   ~$0.20/cell. Consistency-gated. Publishing is a separate free `build_frontend`.

## The discovery flywheel (the ~1,000 is a FLOOR)

Tier-3 only counts blanks in professions we ALREADY name. To find UNKNOWN occupations:
- `classify_occs.py` mines all chapter/section labels for occupation names not in the
  taxonomy → Haiku classifies real-occupation vs boilerplate. Proven: found pest_control
  (licensed in ALL 50 states, we'd missed it) + 7 others in one pass.
- Add them to professions.yaml → run the locator on them (`new_occ_locate.py` pattern) →
  pull → extract. Each round's new corpora surface MORE unknowns next round.
- **Loop until a round finds <~5 new in-scope occupations** ("effectively dry"). Attorneys/
  bar admission are court-regulated — out of OPLR scope, exclude.

## Paths / gotchas

- These scripts were authored with hardcoded session-scratchpad I/O paths (`/private/tmp/
  claude-.../scratchpad`). Repoint the `SP=` constant to a working dir before re-running.
- Data snapshots preserved in-repo: `results/gap_tier3_absence.json`,
  `results/gap_locator_results.json`, `results/gap_located_targets.json`,
  `results/gap_worklist.csv`, `docs/reports/likely_gaps_2026-07-05.md`.
- Requires `web_search` on the Anthropic key (probe once — it may be absent in headless/cron).
- ONE CDP process at a time. Never two committing git processes at once.
- Full plan + cost model: `docs/runbooks/gap_harvest_plan_2026-07-05.md`.
