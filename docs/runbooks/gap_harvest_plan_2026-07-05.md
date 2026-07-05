# Gap-harvest plan — pulling the ~1,000 section-nested gaps (2026-07-05)

## What we're solving

Tier-3 absence reconciliation surfaced **1,061 likely-gap cells** across 51 professions:
a state has no corpus, no matching chapter label, yet the occupation is usually/always
state-licensed. A 12-cell Justia spot-check confirmed **11/12 are real gaps** (the law
is on Justia, we just don't have it); 1 was a genuine per-state absence (polygraph/AK).
Reports: `docs/reports/likely_gaps_2026-07-05.md`, `pipeline/results/gap_worklist.csv`.

Every confirmed gap is **section-nested** in a broad title — building_inspector in CA
Health & Safety Code, court_reporter in TX Government Code, money_transmitter in NY
Banking Law, forester in GA Conservation, etc.

## Root cause (proven, not guessed)

The harvest machinery already exists: `expand_containers` (depth-crawl broad titles into
their section tree) → `match_sections --write-targets` (LLM-free, writes pull targets) →
`pull_text` → clean → trim → extract. It **works** — but only **4% of the 1,061 gaps
resolve from the current expansion**.

Reason: `expand_containers._CONTAINER` (the regex deciding which titles to crawl) targets
occupational-code / insurance / health-*professions* titles only. Tested against the 11
validated gap titles, **8 are invisible to it**:

| Gap title | Crawled? |
|---|---|
| Insurance / Professional & Occupational Licenses | ✅ |
| Health and Safety Code, Government Code, Banking Law | ❌ |
| Conservation & Natural Resources, Regulation of Trade | ❌ |
| Weights & Measures, "Occupations-Professions" (OH), "Professions, Occupations and Businesses" (NV) | ❌ |

So the bottleneck is **crawl coverage, not matching**. The regex also has brittleness
(reversed/comma'd occupational titles miss).

## The pipeline (each stage, with real knobs)

1. **`expand_containers --states … --max-depth 2`** — CDP-bound (shares the debug Chrome
   via `/tmp/justia_cdp_pull.lock`; ONE process; `fetch.per_host_delay_seconds=3.0`).
   Whole-state granularity — no title selector. Idempotent (skips already-expanded
   containers), checkpoints every 5. Which chapters expand is decided purely by the
   `_CONTAINER`/`_SUBGROUP` label regexes.
2. **`match_sections --source hierarchy --profession X --write-targets`** — LLM-free.
   Writes located containers into `config/mapping_overrides.yaml` (source of truth) and
   regenerates `profession_index/X.json` with `via="section_match"`. Per-profession only.
3. **`pull_text --profession X`** — pulls every `matched` node incl. section_match targets
   automatically (no separate flag). CDP, one process, flock-guarded.
4. **clean → trim → discover_schema (if missing) → extract** — the LLM stages. Measured
   cost this session: **~$0.20/cell** (Haiku trim $0.05 + Sonnet batch extract $0.15),
   plus ~$1/profession one-time schema discovery for new professions.

## The hard tradeoff

- **Broaden `_CONTAINER` globally** to the topical titles → simple, but *over-crawls*:
  Government Code / Health & Safety are enormous; depth-2 across 50 states could be many
  thousands of fetches × 3s = **multi-day CDP**, most of it irrelevant sections.
- **Targeted** — only expand the specific (state,title) containers that hold a gap
  profession → precise, but needs to know the title per cell (numbers differ per state).
- **Search-driven** — the 12-cell validation used Justia search to find exact chapter URLs
  at 92% precision. Write those URLs directly as override targets, skip expansion crawl
  entirely. Precise, but ~1,000 searches + result→clean-URL parsing.

## Recommended plan — pilot first, then decide

### Phase 0 — PILOT (de-risk the CDP unknown) — ~1–2h CDP, LLM-free
- Broaden `_CONTAINER` to add: `banking|financial institutions|government code|
  conservation|natural resources|weights (and )?measures|trade|commerce|pharmac|
  \bhealth and safety\b` + fix reversed/comma'd occupational titles.
- Run `expand_containers --states CA,NY,GA,OH --force` (4 states covering the diverse
  topical titles).
- **Measure:** fetch count + wall-clock per state, and re-run `match_sections` → how many
  of those 4 states' gaps now resolve.
- **Decision gate:** extrapolate CDP time to 50 states. If tractable (< ~1 day), go Phase
  1. If it over-crawls, switch the topical-nested professions to the search-driven path
  and keep expansion only for the occupational/insurance titles it already handles well.

### Phase 1 — EXPANSION (CDP, the big unknown) — est. from pilot
`expand_containers` across all 50 states, broadened regex, caffeinated + unattended
(one process, Chrome open). Idempotent, so resumable.

### Phase 2 — MATCH (free, minutes)
`match_sections --source hierarchy --profession X --write-targets` for each of the 51 gap
professions. Review `section_match_candidates.md` before pulling.

### Phase 3 — PULL (CDP) — ~1,000 cells
`pull_text --profession X` per profession (one-state-per-process to dodge the Playwright
thread bug), caffeinated. Skips already-pulled. Commit per profession.

### Phase 4 — EXTRACT (LLM batch) — ~$210 + ~$40 schema discovery
clean → trim → discover_schema (new professions) → `extract_state_batch`. Consistency-
gated. Publishing (if wanted) is a separate free `build_frontend` per profession.

### Phase 5 — RECONCILE (free)
- Genuine absences (polygraph/AK) self-document: the pull returns 0 sections → record it.
- Mapping overlaps: dedupe professions that nest in a title we already pull
  (nurse_midwifery ⊂ Nursing) before counting them as new.
- `corpus_drift` + the consistency gate catch regressions.

## Cost / time summary

| Phase | Resource | Estimate |
|---|---|---|
| 0 Pilot | CDP | 1–2h |
| 1 Expansion | CDP | **unknown until pilot** (hours→days) |
| 2 Match | free | minutes |
| 3 Pull | CDP | ~1,000 cells, ~1 fetch-batch each (hours→a day) |
| 4 Extract | LLM | ~$210 + ~$40 schemas |
| 5 Reconcile | free | — |

**Bottleneck is CDP time, not dollars.** LLM is ~$250 total. The pilot exists to price
the CDP before committing.

## The ~1,000 is a FLOOR, not a ceiling — make the harvest a discovery flywheel

The Tier-3 gap list only counts blanks in professions ALREADY in our 86-taxonomy. It is
blind to occupations we've never named. Do NOT treat "pull the 1,000" as completeness —
that rebuilds the same blind spot. The locator hands us the fix for free:

1. Locate a known gap chapter (proven, 93%).
2. **Harvest its PARENT container's full child list** — one cheap fetch; many professions
   share a parent (all GA professions sit under Title 43 "Professions and Businesses"),
   so parents dedupe hard. This is the structural context the licensing-title-rooted
   hierarchy never captured.
3. **Classify siblings**: LLM-free pattern-match child labels against the 86-taxonomy →
   matched = possibly new gap cells; UNMATCHED labels = candidate NEW professions.
4. **Haiku-classify the unmatched** (reuse `scratchpad/classify_occs.py`, the pass that
   found EMT/optician/apiarist) → real licensed occupations get added to professions.yaml.
5. **Feed new professions back into the locator**; loop until a round surfaces nothing new
   (loop-until-dry, K=2 empty rounds).

This unifies the two approaches: search discovers WHICH titles actually hold professions
(across the whole state code), and those parent titles become the roots we enumerate for
unknowns — catching occupations the 86-taxonomy never had. Restates the CLAUDE.md north
star: "for every occupation, have every chapter that could regulate it, in every state."

Implication for counts: report the flywheel's discovered-new-professions per round and
never claim "complete" — claim "N rounds ran dry," which is honest.

## Guardrails (from CLAUDE.md + this session)
- ONE expand/pull process per Chrome (flock). Never two committing processes (git lock).
- Leave the debug Chrome open + solved; `caffeinate -disu` for unattended runs.
- One-state-per-process on pulls (Playwright cross-thread bug).
- ~8% of "gaps" are per-state absences — expect empty pulls; that's a correct result, not
  a failure. Don't loop on them.
