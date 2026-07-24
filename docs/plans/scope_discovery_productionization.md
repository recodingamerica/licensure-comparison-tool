# Plan — discovery-driven enumerated fields ("discover the union → per-state matrix")

## What this is
Turn a state-varying **free-text list** field into a **canonical enumerated vocabulary discovered
from the corpus** (no hardcoding), then evaluate **each item per state**. Answers Atharv #19 (scope
specificity), the #103/#104 three-state ask, and OPLR's "X states do A, Y do B" format — generalizably.

## Proven (prototype — scratchpad, NOT yet in pipeline)
- 3 occupations, 4 dimensions, all discovered-from-corpus, all three-state, all spot-checked accurate:
  - optometry **laser** (15 procedures) — TX/GA prohibitions propagate; GA diagnostic-vs-therapeutic split correct
  - optometry **injections** (20) — intraocular/intravitreal correctly 0-allow; GA "allowed except [list]" parsed per-item
  - **physical therapy** (28 interventions) — contested boundaries (spinal manip, dry needling, imaging) state-varying; acupuncture/chiro/surgery correctly prohibited
  - **dietetics** nutrition interventions — enteral/parenteral distinguished; CA prohibits parenteral
- Prototype: `scratchpad/scope_pipeline.py` (config-driven: occupation, dimension, trigger terms).
- Posted to #19 (laser only) framed as "might have a solution, exploring generalization."

## Two eval flavors (same discovery mechanism)
- **three-state** — scope procedures / prohibitions: `authorized / prohibited / not_addressed` + quote.
- **present/absent** — enumerable non-scope lists: does this state have item X.

## Fields that benefit (from the list-field audit)
- three-state: `scope.methods_authorized`, `laser_procedures_authorized`, `minor_surgical_procedures_authorized`,
  `scope_exclusions` (5 profs), `prohibited_procedures`.
- present/absent, HIGH OPLR value: **exemptions** (`exemptions_from_licensure`, `license_exemptions`,
  `exempted_occupations`), **`protected_titles`** (5 profs), `continuing_education_excluded_topics` (6),
  `license_tiers` (11), `disqualifying_criminal_offenses`, `authorized_practice_settings`, credential tiers.
- Precedent already in codebase: `disciplinary_grounds` → `disciplinary_categories` via `bucket_text`.

## Design decisions
1. **Dimension sourcing** → **(A) seed from existing list-fields** (cleaner/lower-risk) over (B) auto-discover
   new dimensions. The free-text list-fields already identify the dimensions.
2. **Rollout** → clinical-scope + OPLR-priority occupations first (optometry, PT, dietetics, podiatry,
   medicine, nursing), not all 30 (auctioneer/pawnbroker have no procedure scope).
3. **Eval flavor** is per-field metadata (three-state vs present/absent).

## Implementation (phased)
**Phase 1 — vocabulary discovery step** (`pipeline.discover.scope_vocab`, or extend `discover_schema`):
  for each list-field flagged enumerable, collect values across states → LLM canonical union (merge synonyms,
  distinguish real differences) → persist enum to `results/discovered/<prof>.json` (+ a `scope_vocab/<prof>.json`).
  Reuse `scratchpad/scope_pipeline.py::discover`.
**Phase 2 — extraction** (extend `extract_state`): for an enumerated field, classify each vocab item per state
  (three-state or present/absent) + verbatim quote, into the structured record. Batch API for cost.
**Phase 3 — display** (`build_frontend`): per-field heatmap/matrix; ties to the #103 three-state UI work.
**Phase 4 — rollout + validate**: run on the priority occupations; **validate dietetics exemptions +
  protected_titles against OPLR's scan** (the fields we couldn't cleanly match in #105 should now reconcile).

## Cost / risk
- More LLM tokens (evaluate N items/state) — use the batch API (`extract_state_batch`).
- Schema change → re-extract affected occupations. **Fits the [[project_extraction_quality_batch]]** — ships
  with the same deliberate re-extract pass, not piecemeal.
- Start behind a flag / one occupation before the full rollout.

## Validation targets
- optometry laser/injection matrices (done — accurate).
- dietetics `protected_titles` + exemptions reconcile with OPLR's dietitian scan.
- three-state (`Y`/`N`/`·`) all distinctly populated per field.
