# Umbrella + Justia completeness plan — 2026-07-01

The harvest workstream: pull the shared/umbrella law and section-nested law the
per-profession chapter map misses, and get it categorized (scoped to professions)
so extraction actually uses it. Distinct from `refresh_corpus` (Task 2), which
re-pulls what the map already knows; this plan GROWS the map. Both feed the frozen
snapshot Utah consumes.

Ground rules carried over: ONE CDP pull process at a time; commit before/after
pulls; every new mapping decision lands in `mapping_overrides.yaml` or a state
scope manifest (never in generated output); "has a corpus ≠ has the law".

## U0. Reconcile the label filter (BLOCKING — issue #57)

The `pull_umbrella_text --label-filter` re-pull (reverted 2026-07-01) dropped
chapters the scope goldens bless as real signal (IN article-0.5, SD 36-2/2a,
CO licenses) and showed cap-truncation fingerprints (IN/TN/MT at exactly the
50-section cap). Before ANY new umbrella pulling:

1. Diff the filter's admitted-label set against the golden-blessed chapters in
   `tests/test_assign_umbrella_scope.py` GOLDEN_COUNTS + the state_scope manifests.
   Each disagreement is either a filter fix (admit the label) or a deliberate
   policy change (update golden + manifest, with the change in the commit message).
2. Fix the cap: raise the per-chapter section cap or page through, and make a
   cap-hit a LOUD warning recorded in the corpus (a silently truncated umbrella
   chapter looks complete and isn't). TN chapter-1 sitting at exactly 50 is
   probably truncated today.
3. Acceptance: re-pull the 9 reverted states; goldens pass (or are deliberately
   updated); no chapter at exactly the cap without a warning.

## U1. Pull the known citation backlog

`corpus_status umbrella` detects chapters that extracted records CITE but nobody
pulled (~122 chapters nationwide as of Jun-30 — re-derive the current number).
The loop, all existing tools:

```
corpus_status umbrella --min-refs N --min-profs M     # detect + queue
umbrella_from_citations                               # map citations → Justia URLs (two-factor)
pull_umbrella_text --label-filter --force             # after U0 fixes; CDP Chrome up
git commit                                            # per state or per batch
```

Effort: pulling is cheap (CDP); the human step is eyeballing the two-factor
output for false umbrellas (the citation signal alone flags profession chapters —
documented, don't trust it).

## U2. Categorize: scope every pulled umbrella chapter

An umbrella chapter is only useful if extraction knows WHICH professions inherit
it. The mechanism (already built, LLM-free-first):

- `assign_umbrella_scope` walks the chapter text for scope signals
  (universal vs enumerated professions).
- Where the walker can't tell (undetermined), the per-state manifest in
  `config/state_scope/<ST>.yaml` declares it by hand — this is the preferred
  override surface (2026-05-28 pivot), same philosophy as mapping_overrides.
- The golden counts in `test_assign_umbrella_scope.py` are the acceptance gate;
  every new state that gets umbrella text should gain a golden entry once its
  scope assignment is reviewed. That's how the goldens grow instead of rot.

Working definition of done per state: zero `undetermined` scope-source counts,
or each remaining undetermined consciously waived in the manifest.

## U3. Re-extract affected pairs

Umbrella text is extraction CONTEXT — corpora on disk don't change, but any
(profession, state) whose state gained/changed umbrella text needs re-extraction
to benefit. Batch API (`extract_state_batch`), queue built from the list of
states touched in U1. This is the step that actually moves published data
(discipline/fees/hearings fields for centralized-discipline states).

## U4. Detection beyond citations (the umbrella chapters nobody cites)

Citations only find umbrellas that extracted text happens to reference. Two
cheap LLM-free detectors for the rest:

1. **Centralized-discipline heuristic** (documented pattern: MI/NE/NJ/CA):
   for each state, if discipline-related fields are empty/thin across MANY
   professions simultaneously, suspect an unpulled state-wide general-provisions
   chapter. Mechanical query over `structured/`; output is a review list.
2. **Umbrella coverage matrix** (`umbrella_coverage_matrix`): states whose
   umbrella_text is empty/thin relative to peers. A state where 40 professions
   extract fine but umbrella_text has 3 sections is a gap candidate.

Both produce worklists a human eyeballs against `hierarchy/<ST>.json` — the
labels ("Uniform Licensing", "General Provisions", "Professions and Occupations
Generally") are greppable.

## U5. Section-nested completeness (the other Justia stuff)

Same loop as public_adjuster, now config-safe end to end:

```
expand_containers --state XX --max-depth 2      # CDP; depth-expand broad chapters
match_sections --source hierarchy --profession P --write-targets
                                                # → mapping_overrides.yaml + index rebuild
pull_text --profession P --states XX            # then clean → trim → extract
```

Priority order for choosing (profession, state) targets:
1. `profession_index/_coverage.csv` missing-states column — professions with
   low state counts are either genuinely-unregulated (verify → verified_absences.yaml)
   or section-nested (this loop).
2. States whose hierarchy has NOT been depth-expanded (the expansion provenance
   is visible: nodes with `parent_chapter_url`) — expand the big flat titles first
   (insurance, occupations, health) since they hide the most nested professions.
3. `audit_corpus` wrong-chapter flags — a corpus that exists but is the wrong law.

## Sequencing against the other workstreams

| Order | Item | Depends on |
|---|---|---|
| 1 | U0 filter reconciliation | nothing (code + goldens work, no Chrome) |
| 2 | U1 citation-backlog pull | U0; a CDP Chrome session; R1/R2 committed |
| 3 | U2 scoping for newly pulled states | U1 |
| 4 | U3 re-extract affected pairs | U2; API budget |
| 5 | U4 detectors → more U1/U2/U3 rounds | first pass of U1-U3 |
| 6 | U5 section-nested loop | independent; interleave with umbrella rounds |

`refresh_corpus` (Task 2) should land before the BIG pulls so every new corpus
gets the year-diff treatment from day one, but U0 can start immediately.

## What Utah sees

None of this is Utah-facing work — it's map-growing, which stays with the
curator. Utah's snapshot simply gets richer: more umbrella context per state,
more professions with full coverage. The handoff artifacts (three commands,
frozen map) are unchanged by this plan.
