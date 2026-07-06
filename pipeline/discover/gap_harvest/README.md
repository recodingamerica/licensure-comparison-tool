# Gap harvest + discovery flywheel

Finds and pulls the licensing law for professions that live **section-nested inside a broad
topical title** (building_inspector in Health & Safety, court_reporter in Government Code,
money_transmitter in Banking) — the ones the hierarchy crawl can't reach because
`build_hierarchy` roots each state at its ONE licensing title, so anything in another title
is outside the crawl. Then grows the profession list itself.

## Modules (all share `_common.py` — state slugs, the web_search locator, URL hygiene, paths)

| Module | What it does | Run |
|---|---|---|
| `locate` | web_search finds each (prof, state)'s Justia chapter URL (NO CDP). Modes: `--gaps`, `--recover-nulls`, `--profession X --states …` | `python -m pipeline.discover.gap_harvest.locate --gaps` |
| `reuse` | copies sections from corpora we already hold when a located chapter overlaps — no re-fetch | `python -m pipeline.discover.gap_harvest.reuse` |
| `cleanup` | detects DEAD (404-stored) + WRONG_LEVEL (section-url) pulled cells; `--relocate` re-finds them | `python -m …gap_harvest.cleanup [--relocate]` |
| `discover` | mines chapter labels for occupations not in the taxonomy → Haiku classifies (the flywheel) | `python -m …gap_harvest.discover` |

Data lives in `results/gap_harvest/` (override `GAP_HARVEST_DIR`): `tier3_absence.json` (the
gap list), `locator_results.json` (located URLs), `pull_worklist.json`, `reused.json`,
`relocate_worklist.json`, `discovered_occupations.json`.

The **pull** itself uses the existing CDP stack (`refresh_corpus`), driven by `gap_pull.sh`:
ONE state per process (Playwright cross-thread bug), flock-guarded (one Chrome), skips
already-pulled (resumable), commits per profession, `caffeinate -disu`.

## End-to-end recipe

```
1. discover / tier-3      → results/gap_harvest/tier3_absence.json   (the gap list)
2. locate  --gaps         → locator_results.json     (web_search, ~93% live)
3. locate  --recover-nulls→ recover exemption chapters the strict pass skipped
4. write targets          → config/mapping_overrides.yaml (via=gap_locator) + rebuild indexes
5. reuse                  → copy ~1/3 from existing corpora; rest → pull_worklist.json
6. gap_pull.sh            → CDP pull the rest (one state/process, resumable)
7. cleanup --relocate     → fix the ~1% dead + wrong-level, re-pull
8. clean → trim → discover_schema → extract_state_batch   (consistency-gated)
```

## The ~1,000 is a FLOOR — the flywheel

Tier-3 only counts blanks in professions we ALREADY name. `discover` mines statute structure
for UNKNOWN occupations → add the real ones to professions.yaml → `locate --profession` →
pull. Each round's new corpora surface more unknowns. **Loop until a round finds <~5 new
in-scope occupations.** Proven: found pest_control (licensed in all 50 states, we'd missed
it) + 7 others. Attorneys/bar admission are court-regulated — out of OPLR scope, exclude.

## Gotchas

- Needs the `web_search` tool on the Anthropic key — probe once (absent in some headless runs).
- ONE CDP process at a time; never two committing git processes at once.
- HTTP 200 is meaningless on Justia — gate located URLs through `verify_urls` (and `cleanup`
  catches 404s the pull stored as a 1-section corpus).
- Full plan + cost model (~$0.20/cell extract; CDP time is the real constraint):
  `docs/runbooks/gap_harvest_plan_2026-07-05.md`.
