# Pipeline state — where we are, what's solid, what's optional

The goal is a pipeline where adding a new occupation to `professions.yaml`
produces solid coverage on the **majority of states** with no
per-occupation hand-curation. 50/50 is not the target; ~40-of-50 well is
the bar.

## What works hands-off for any new occupation

Adding a new profession today walks through these stages without
profession-specific tuning:

| Stage                          | What it does                                                                                                                    | Per-occupation work? |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- | -------------------- |
| `match_profession`             | Scan every state's hierarchy + chapter maps, find the matching chapter via label patterns and the LLM-mapped chapter classifier | None                 |
| `pull_text`                    | Fetch chapter & section text from Justia / external sources                                                                     | None                 |
| `clean_text`                   | Strip Justia chrome, normalize whitespace                                                                                       | None                 |
| `trim_state`                   | Drop administrative-procedure sections, keep scope + licensure                                                                  | None                 |
| `discover_schema`              | LLM derives 20-40 profession-specific Pydantic fields from a state sample                                                       | None                 |
| `extract_state`                | Per-state extraction against the composed (universal + discovered) model                                                        | None                 |
| `publish.build_frontend`       | Aggregate to `data/<profession>.json`, upload to Vercel Blob, push to live site                                                 | None                 |

### Universal infra already built (covers every profession)

- **Multi-title hierarchy expansion**: each state's hierarchy contains
  every licensing-relevant title, not just the one the original config
  targeted. A new profession in (e.g.) the Insurance Code or Business
  Occupations Code is reachable without YAML edits.
- **Chapter-mapper**: LLM classifies the chapter list per state once.
  Output covers every current and future profession in that state. One
  LLM call per state, ~40 of 50 states have maps; sweep can rerun.
- **Universal (Repealed.) exclude**: filters chapters whose label
  contains `(Repealed)` / `[Repealed]` etc. so we don't try to extract
  from dead law.
- **Umbrella context injection**: pulled umbrella chapters (definitions,
  board-composition rules, general licensing procedures) per state are
  injected as supplemental context when extracting any profession.
- **Schema decomposition (meeting Q1/Q2)**: every extraction populates
  the orthogonal `credential_type` × `is_mandatory` Enums, plus
  structured `regulatory_authority.{name, type, umbrella_agency}` —
  consistent across all professions and states.
- **Form-of-regulation derivation**: published rows surface
  `credential_type` + `is_mandatory` derived from the legacy
  `regulatory_model` even on records that pre-date the new prompt.

## State coverage tiers

Adding a new occupation produces these tiers automatically:

- **Tier 1 — fully automatic (≈37 of 50 states).** Justia-hosted, chapter
  layout. The new occupation gets matched, pulled, and extracted with no
  intervention.
- **Tier 2 — automatic if `section_maps_v2` exists (5 states: AZ, OK,
  WI, LA, KS).** Flat-section-list Justia layout. We have v2 section
  maps for some of these (already covering any new profession); others
  need a one-time `fetch_section_bodies` + `map_state_sections_v2` run.
  When run, the result auto-covers every current + future profession.
- **Tier 3 — needs per-profession hand-curation (MI, MN).** External
  sources (revisor.mn.gov, legislature.mi.gov). Hand-curated
  `section_url_list` per profession in `state_structure.yaml`. New
  professions need someone to find the chapter once.
- **Tier 4 — structural gap (PA).** Justia has nothing useful for
  licensing chapters in PA. Would need a different source
  (palegis.us API, official PA Code, Westlaw).

## What's optional polish vs what's structural

### Optional (not blocking) — we already deliver a "solid majority"

These would improve coverage from ~40 → ~50 but aren't required for a
useful product. Each is one-time-per-state, not per-profession.

- Backfill v2 section maps for the 2-3 Tier-2 states that don't have
  them yet (~1 hour each, one-time).
- LLM-driven section discovery for MI / MN — same pattern as Justia
  chapter maps but adapted to those sites' structure (~1 day project,
  one-time).
- PA: try palegis.us or pivot to the official PA Code. Investigate
  whether a workable source exists at all (~half day to scope).

### Structural — needed for new-occupation flow to work cleanly

These are wired up. No outstanding items.

- Multi-title state hierarchies ✓
- Chapter-level LLM classifier ✓
- Universal repealed exclude ✓
- Schema discovery with sampling for large corpora ✓
- Quote verification against both practice-act + umbrella text ✓
- Auto-redeploy on publish ✓

## What the "add a new occupation" workflow looks like

```
# 1. Add the profession to config/professions.yaml
#    (display name, label patterns, ONET code)

# 2. Match against existing state hierarchies
python -m pipeline.discover.match_profession --profession <new_prof>

# 3. Inspect coverage — how many states matched
cat pipeline/results/profession_index/_coverage.csv | grep <new_prof>

# 4. Run the rest of the pipeline
python -m pipeline.ingest.pull_text --profession <new_prof>
python -m pipeline.ingest.clean_text --profession <new_prof>
python -m pipeline.ingest.trim_state --profession <new_prof>
python -m pipeline.extract.discover_schema --profession <new_prof> --max-states 5
python -m pipeline.extract.extract_state --profession <new_prof>
python -m pipeline.publish.build_frontend --profession <new_prof> --deploy
```

End-to-end runtime for ~40 states: roughly 1-2 hours wall clock, mostly
LLM call time. No human attention needed during the run.

If `match_profession` returns a number that's lower than expected, the
debugging path is:

1. Check `profession_index/<new_prof>.json` for partial matches.
2. If a chapter is mismatched, the LLM chapter-mapper missed something —
   re-run `map_state_chapters` for that state (`--force`) or tweak the
   profession's label patterns in `professions.yaml`.
3. If a state is fully unmatched, check whether it's a Tier 2/3/4 state
   from the table above.

## What we have proven

- **Podiatry** (seeded): 49/50 states extracted, 36 profession-specific
  fields, 97.6% quote-verification rate.
- **Public Accountancy (CPA)**: 44/50 — built end-to-end from the same
  infra with zero CPA-specific hand-curation (state_structure.yaml entries
  are profession-agnostic). Three of the remaining gaps are Tier 3/4.
- **Medicine**: 44/50 — same story. Discovered 21 profession-specific
  fields (foreign-medical-graduate requirements, opioid-prescribing
  limits, pain-management education, etc.). 95.8% quote-verification.

Each subsequent profession reuses the same machinery. The marginal
cost of adding profession #4, #5, #46 is a few hours of LLM time and
no engineering work.
