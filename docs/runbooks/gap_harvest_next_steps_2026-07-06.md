# Gap harvest — next steps (handoff, 2026-07-06)

Pick up here. The search-driven gap harvest is mid-pull; everything downstream is built,
clean, and committed. Package: `pipeline/discover/gap_harvest/` (README = module map).

## State at handoff

- **Main pull RUNNING** (detached, survives a session clear): ~214/510 cells pulled.
  Reused 261 more with no fetch. 0 empties, ~1% dead (cleanup handles it). ~2.8 min/cell.
- **All 50 gap professions have extraction schemas** (`results/discovered/`).
- **Code**: consolidated into a clean package (`_common`, `locate`, `reuse`, `cleanup`,
  `discover`, `coverage`, `gap_pull.sh`). Nothing else imports it.
- **Data** (committed, `results/gap_harvest/`): `tier3_absence.json` (1,061 gaps),
  `locator_results.json` (772 located + 128 recovered + 161 absent), `pull_worklist.json`
  (510), `reused.json` (261), `relocate_worklist.json`, `dead_cells.json`.
- **8 flywheel professions PARKED** in professions.yaml (pest_control, outfitter_guide,
  asbestos_abatement, meat_inspector, boxer, hawker_peddler, septage_pumper,
  managing_general_agent) — located but not pulled; do them in the flywheel round below.
- Status issue for Atharv: **#58**. Full plan: `gap_harvest_plan_2026-07-05.md`.

## How to check / resume the pull

Needs the debug Chrome up at `127.0.0.1:9222` (solved once). Check:
```
pgrep -f gap_pull.sh                      # running?
python -c "import json,os; wl=json.load(open('pipeline/results/gap_harvest/pull_worklist.json')); \
print(sum(1 for p in wl for s in wl[p] if os.path.exists(f'pipeline/results/text/{p}/{s}.json')),'/',sum(len(v) for v in wl.values()))"
```
If stopped before done, resume (idempotent — skips already-pulled, commits per profession):
```
caffeinate -disu bash pipeline/discover/gap_harvest/gap_pull.sh
```

## Next steps, in order

1. **Finish the pull** (wait, or resume as above). Done when the count hits ~510
   (minus genuine dead URLs).

2. **Cleanup dead + wrong-level cells:**
   ```
   python -m pipeline.discover.gap_harvest.cleanup            # report
   python -m pipeline.discover.gap_harvest.cleanup --relocate # re-find them (web_search)
   ```
   Then re-write targets for the relocated cells and re-pull them (small set).

3. **Extract the gap corpora.** For every profession with new gap corpus:
   `clean_text → trim_state → extract_state_batch submit --queue <queue>`. Build the queue
   as {profession: [states with text but no structured record]}. Consistency-gated — if the
   gate flags cells, re-extract just those (see the Jul-5 republish for the pattern).
   Budget ~$0.20/cell (~$150–210 for the full harvest).

4. **De-dupe year-versioned corpora (optional tidy).** `corpus_drift` shows ~90 cells with
   duplicate year-versioned chapters (benign, 0 HOST_DRIFT). Apply
   `pull_text._dedupe_year_versions()` to those `sections` in place, then re-clean/trim/extract
   the affected cells. Low priority.

5. **Publish (product decision).** Only the original 7 professions are live. Making a
   held-out gap profession visible is a separate `build_frontend --profession X` (free,
   deterministic) — decide with the team which to surface.

6. **Flywheel round (grow the census).**
   ```
   python -m pipeline.discover.gap_harvest.discover           # find unknown occupations
   # add the real in-scope ones to professions.yaml
   python -m pipeline.discover.gap_harvest.locate --profession X --states …   # for each new one
   # write targets -> reuse -> pull -> extract
   ```
   Loop until a round finds <~5 new in-scope occupations. Exclude court-regulated
   (attorney/bar admission). The 8 parked professions are the current round's pull backlog.

## Deferred decisions

- The **128 recovered nulls** (exemption/certification chapters) — many overlap corpora we
  already have; review before spending pulls on them.
- Which held-out professions to **publish**.
- **Disk** (unrelated to utah): user to clear ~19 GB of caches (`~/Library/Caches`, `~/.cache`).

## Guardrails
- ONE CDP process at a time; never two committing git processes at once (lock-retry the commit).
- `web_search` tool must be on the Anthropic key (absent in some headless runs).
- Batch extraction is the default for re-runs (durable, ~50% cheaper).
