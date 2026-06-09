# Field audit — education, experience, licensing authority, discipline, scope

Working doc for the 5-field methodology pass. Originally written 2026-06-01
against May-29 baseline data; **updated 2026-06-02 with post-YAML-cleanup
numbers** after the 2026-06-01/02 session re-extracted 67+ (state, profession)
pairs with corrected corpora across MI/NE/NJ/CA/WA/NY/MN.

Scope: the 5 fields named in the task —
**education (min. degree), professional experience, licensing authority,
discipline, scope of practice**. Universal-base fields only; per-profession
discovered fields are out of scope here.

Data source: 6 professions × 43–50 states. Includes the
[[centralized-discipline-pattern]] umbrella fixes that flipped MI medicine
0→20, NY all-professions 0→14, WA nursing 5→24, etc. The May-30 schema
additions (`alternative_regulation`, Obama-2015 certification wording)
are populated on every re-extracted record.

Population rates below come from `pipeline/results/structured/<profession>/*.json`,
treating an Evidence-wrapped field as "populated" if it is non-null. They are
not corrected for the [[feedback_no_llm_confidence]] rule — a populated
Evidence node may still be `unverified: true` if the quote didn't match the
source. Current unverified rate is 0.4% (17 of 4,200 cells).

## Gap matrix headline (2026-06-02)

| | now | session start (2026-05-29) |
|---|---:|---:|
| populated | 3,259 (77.6%) | 2,939 (70.0%) |
| null | 854 (20.3%) | 928 (22.1%) |
| not_licensed | 56 (1.3%) | 252 (6.0%) |
| no_record | 14 (0.3%) | 70 (1.7%) |
| unverified | 17 (0.4%) | 11 (0.3%) |

+320 cells flipped from null/not_licensed/no_record → populated — all from
YAML cleanup (new chapter matches in 8 states + per-profession section
overrides) and the centralized-discipline umbrella patches, no schema
changes. Disciplinary_grounds counts are now in the healthy 10–60 range
across all 6 × 50 grid (median 17).

## Per-field population rates (2026-06-02)

| field | podiatry | medicine | nursing | dentistry | optometry | public_accountancy |
|---|---|---|---|---|---|---|
| edu.degree_required | 49/49 | 46/50 | 49/49 | 48/49 | 48/49 | 46/49 |
| edu.accrediting_body | 41/49 | 42/50 | 25/49 | 47/49 | 33/49 | 21/49 |
| exp.required (=true) | 40/49 | 43/50 | **5/49** | **4/49** | **4/49** | 47/49 |
| exp.duration | 34/49 | 39/50 | **5/49** | **6/49** | **3/49** | 47/49 |
| exp.kind | 40/49 | 43/50 | **5/49** | **6/49** | **3/49** | 48/49 |
| auth.issuing_authority (legacy) | 49/49 | 48/50 | 49/49 | 49/49 | 49/49 | 48/49 |
| auth.regulatory_authority.name | 49/49 | 48/50 | 49/49 | 49/49 | 49/49 | 46/49 |
| auth.regulatory_authority.type | 49/49 | 48/50 | 49/49 | 49/49 | 49/49 | 46/49 |
| auth.regulatory_authority.umbrella_agency | 25/49 | 22/50 | 19/49 | 22/49 | 21/49 | 15/49 |
| discipline.grounds (≥1) | 48/49 | 47/50 | 48/49 | 49/49 | 49/49 | 47/49 |
| scope.definition_quote | 49/49 | 45/50 | 49/49 | 48/49 | 49/49 | 43/49 |
| scope.methods_authorized | 49/49 | 44/50 | 47/49 | 47/49 | 49/49 | 46/49 |
| scope.drug_authority | 37/49 | 38/50 | 43/49 | 43/49 | 49/49 | 0/49 |
| scope.scope_protection | 49/49 | 47/50 | 49/49 | 48/49 | 49/49 | 48/49 |
| altreg.bonding_required | 0/49 | 1/50 | 1/49 | 0/49 | 0/49 | 0/49 |
| altreg.insurance_required | 1/49 | 4/50 | 4/49 | 0/49 | 0/49 | 1/49 |
| altreg.establishment_regulation | 0/49 | 1/50 | 1/49 | 4/49 | 0/49 | 8/49 |

**disciplinary_grounds average per state:**
podiatry 16.1, medicine 24.7, nursing 15.2, dentistry 19.4, optometry 15.3, public_accountancy 10.7

The structural patterns from the original audit hold:
- `exp.*` strongly split by profession (residency-requiring vs not)
- `umbrella_agency` ~30-50% (standalone boards don't sit inside a parent)
- `accrediting_body` varies (some statutes name CODA/CCNE; others just say "board-approved")
- `scope.drug_authority` correctly 0/49 for CPA

The May-30 schema additions (`alternative_regulation.*`) populate
sparsely — these are all heavyweight licensed professions, so bonding /
insurance / establishment regulation rarely apply (the most: CPA
establishment_regulation at 8/49, matching firm-licensure provisions, and
dentistry establishment_regulation at 4/49 for dental-office licensure).
These fields will populate more when we extend to title-only / cert-only
professions like dietitians, athletic trainers, cosmetology.

---

## ORIGINAL AUDIT (2026-06-01) — pre-cleanup numbers below preserved as historical context

The per-field detail sections that follow were written against the May 29
baseline data (43-49 of 50 states per profession). The schemas, gaps, and
methodology proposals are still valid; specific counts in the tables below
have shifted as documented in the headline above.

---

## 1. Education

### What we capture today

`LicensureRequirements.education: EducationRequirement | None`
(`pipeline/extract/standard_model.py:283`, `:388`)

Two sub-fields, both Evidence-wrapped strings, both free-form:

- `education.degree_required: StrEvidence` — free text, e.g.
  `"Doctor of Podiatric Medicine from a podiatry school or college accredited
  by the Council on Podiatric Medical Education"`
- `education.accrediting_body: StrEvidence` — free text, e.g.
  `"Council on Podiatric Medical Education"`

No enum, no normalized degree-level taxonomy, no separate "years of education"
integer. The prompt (`pipeline/config/prompts.yaml`) does not list this field
under explicit instructions — the LLM populates it from the schema description
alone.

### Population rates (state-level, populated / total)

| field | podiatry | medicine | nursing | dentistry | optometry | public_accountancy |
|---|---|---|---|---|---|---|
| `degree_required` | 48/49 | 37/43 | 46/47 | 43/46 | 45/47 | 40/45 |
| `accrediting_body` | 40/49 | 32/43 | 20/47 | 43/46 | 31/47 | 16/45 |

`degree_required` lands ~90–98%. `accrediting_body` ranges 35–94% — varies
by how prescriptive the profession's statutes are (dentistry's CODA, podiatry's
CPME are near-universal; nursing and CPA are often "board-approved program"
without naming a body).

### Structural limits

1. **No degree-level normalization.** Filtering "all states requiring a
   doctoral degree" requires LLM-parsing the free-text value or hand-mapping.
   The same degree appears in different wording across states.
2. **No "years of education" integer.** Some statutes say "5 years post-secondary"
   instead of a degree name; we capture that in the free text but can't
   sort/filter on it.
3. **No distinction between minimum and typical.** Some statutes name a
   minimum (HS + N years) plus a "or a degree from an accredited program"
   alternative. We capture one path, picked by the LLM.
4. **Pre-degree education (high school, secondary, prerequisites) collapses
   into `degree_required`.** No separate field.

### Tagging proposals

Apply [[user_preferences]] (enum for cross-state comparison fields, narrative
for descriptive). Candidates:

- **`degree_level: Enum`** — `none / hs_diploma / associates / bachelors /
  masters / doctoral / professional_doctorate / other`. Cross-state filterable.
  Free-form `degree_required` stays as descriptive backing.
- **`accrediting_body_kind: Enum`** — `none / state_board_approved / named_national_body /
  cms_aoa_equivalent`. Distinguishes "the state board approves programs" from
  "the statute names CPME/CODA/CCNE."

Both are derivable from the existing free-text values via a cheap one-pass
LLM normalization (similar to the existing `map_prep` two-pass normalization
pattern, see [[web_stack_notes]]). No re-extraction needed for the existing 6.

---

## 2. Professional experience (post-degree)

### What we capture today

`LicensureRequirements.post_degree_experience: PostDegreeExperience | None`
(`standard_model.py:288`, `:389`)

- `required: BoolEvidence`
- `duration: StrEvidence` — free text, units vary (`"24 months"`, `"1 year"`,
  `"2,000 hours"`)
- `kind: StrEvidence` — free text (`"podiatric residency"`,
  `"accounting work experience"`, `"AXP"`)

No enum, no separate hours integer, no supervision-structure decomposition.

### Population rates

| field | podiatry | medicine | nursing | dentistry | optometry | public_accountancy |
|---|---|---|---|---|---|---|
| `required` (=true) | 39/49 | 35/43 | **3/47** | **2/46** | **3/47** | 40/45 |
| `duration` | 34/49 | 33/43 | **3/47** | **3/46** | **3/47** | 39/45 |
| `kind` | 39/49 | 35/43 | **3/47** | **3/46** | **3/47** | 40/45 |

Strongly profession-dependent. Podiatry / medicine / CPA require post-degree
experience in essentially every state. Nursing / dentistry / optometry
essentially never. That's not extraction failure — it's the truth: these
professions gate on the degree itself, not on a residency.

This is exactly the [[reliable-detection-ok]] case: 44 of 47 nursing nulls are
the right answer.

### Structural limits

1. **`duration` is unparseable across professions.** Compare 24 months /
   1 year / 2,000 hours / "1 year and 1,800 hours."
2. **`kind` is unbounded free text.** No way to filter "all residency
   states" without an LLM normalization pass.
3. **No "supervision required" sub-field.** Statutes often distinguish
   supervised vs. independent experience; we don't.
4. **Cannot distinguish "experience required for licensure" from "experience
   required for an advanced credential" (e.g. APRN).** The model is flat.

### Tagging proposals

- **`kind_enum: Enum`** — `residency / supervised_practice / work_experience /
  apprenticeship / fellowship / none / other`. Same one-pass LLM
  normalization as education.
- **`duration_hours: int | None`** + **`duration_months: int | None`** —
  derived from the free-text `duration` by parsing. Statutes that say "X
  hours OR Y months" populate both. Sortable, filterable, comparable.
- Keep `duration` and `kind` free-text as the verbatim backing.

---

## 3. Licensing authority

### What we capture today

Two parallel representations:

1. **Legacy free-text**: `LicensureRequirements.issuing_authority: StrEvidence`
   (`standard_model.py:376`) — kept for back-compat.
2. **Structured**: `LicensureRequirements.regulatory_authority: RegulatoryAuthority`
   (`standard_model.py:216`, `:377`) with three fields:
   - `name: StrEvidence` — canonical name of the immediate authority
   - `type: AuthorityTypeEvidence` — enum: `standalone_board / shared_board /
     division / department / joint / other` (`standard_model.py:190`)
   - `umbrella_agency: StrEvidence | None` — higher-level agency, null when
     the immediate authority is itself top-level

This is the **best-developed of the 5 fields** — already has an enum, already
has structural decomposition, already in the prompt
(`prompts.yaml:177-200`).

### Population rates

| field | podiatry | medicine | nursing | dentistry | optometry | public_accountancy |
|---|---|---|---|---|---|---|
| legacy `issuing_authority` | 49/49 | 40/43 | 46/47 | 46/46 | 46/47 | 43/45 |
| `regulatory_authority.name` | 49/49 | 40/43 | 46/47 | 46/46 | 46/47 | 41/45 |
| `regulatory_authority.type` | 49/49 | 40/43 | 46/47 | 46/46 | 46/47 | 41/45 |
| `regulatory_authority.umbrella_agency` | 22/49 | 18/43 | 19/47 | 21/46 | 22/47 | 15/45 |

Name + type populate at near-100% wherever the chapter exists.
`umbrella_agency` is much sparser (33–48%) — this is structural reality, not
a gap. Standalone boards in many states don't sit inside a department.

### Structural limits

1. **`name` is free-form `StrEvidence`** — no canonical agency taxonomy. "State
   Board of Podiatry" in MO and "Missouri Board of Podiatric Medicine" appear
   as different strings. Cross-state queries like "all states where podiatry
   sits under the medical board" require LLM-clustering or hand mapping.
2. **`umbrella_agency.value` is also free-form.** Same problem at the
   department level: "Division of Professional Licensing, Department of
   Commerce" vs. "Department of Commerce — Professional Licensing Division"
   vs. "DOPL within DOC" are the same entity.
3. **No "shared with which professions" relation.** When `type=shared_board`,
   the statute usually names siblings ("medicine, osteopathy, podiatry") but
   we don't capture them as a list.

### Tagging proposals

- **Canonical agency display normalization** — one-shot LLM pass per state
  that maps the free-text `name` and `umbrella_agency` values across all
  professions in that state to a canonical short form. Same pattern as
  `map_prep` choropleth normalization. This is high-value because the
  same agency appears across many (state, profession) pairs and currently
  shows up as N distinct strings.
- **`siblings: list[str]`** on `RegulatoryAuthority` when `type=shared_board`
  — name the other professions the board governs, populated from the
  umbrella corpus. Surfaces "podiatry is governed by the Board of Healing
  Arts which also governs medicine + osteopathy."

The enum coverage on `type` is the right shape already.

---

## 4. Discipline

### What we capture today

`LicensureRequirements.disciplinary_grounds: list[DisciplinaryGround]`
(`standard_model.py:173`, `:468`)

Each ground is:
- `short_label: str` — snake_case key (e.g. `fraud_in_obtaining_license`)
- `description: str` — one-line plain-English description
- `quote: str`
- `citation: str`

`short_label` is generated *per-state by the LLM* with no shared vocabulary
across states. Two states with identical grounds get different short_labels.

### Population rates (states with ≥1 ground, and per-state count)

| | podiatry | medicine | nursing | dentistry | optometry | public_accountancy |
|---|---|---|---|---|---|---|
| any grounds (≥1) | 46/49 | 39/43 | 44/47 | 45/46 | 46/47 | 42/45 |
| avg grounds per state | 14.5 | 24.0 | 14.0 | 19.2 | 14.5 | 10.4 |

Universal coverage (~92–98% of states). Medicine has by far the longest lists
(24 average) because medical practice acts enumerate more conduct.

### Structural limits

This is **the field with the largest cross-state comparability gap.**

1. **`short_label` has no controlled vocabulary.** "fraud_in_obtaining_license"
   in one state may be "obtaining_license_by_fraud" in another, with
   identical statutory meaning. Filtering "all states with a fraud ground"
   requires LLM clustering after the fact.
2. **No category enum.** Common categories — fraud, criminal conviction,
   substance abuse, incompetence, unprofessional conduct, regulatory
   violation, mental/physical incapacity, fee/CE non-compliance — are not
   typed. Each is just a free-form short_label.
3. **No severity tier / sanction outcome.** Statutes typically pair grounds
   with possible sanctions (suspension, revocation, fine, reprimand,
   probation). We capture the ground but not the sanction structure.
4. **Process is not captured at all.** Who initiates, complainant rights,
   hearing procedure, burden of proof, appeal route — none of this is in
   the schema.

### Tagging proposals

- **`category: Enum`** added to `DisciplinaryGround` — small bounded
  vocabulary (~8–10 categories: `fraud / criminal_conviction /
  substance_abuse / incompetence / unprofessional_conduct / regulatory_violation /
  incapacity / fee_or_ce_noncompliance / other`). Derivable from the
  existing `description` field by a one-pass LLM normalization.
- **`sanctions_available: list[Enum]`** at the `LicensureRequirements`
  level (not per-ground; statutes typically list sanctions once and apply
  them to any ground). Values: `revocation / suspension / probation /
  reprimand / fine / restriction / surrender`.
- **`process: DisciplinaryProcess | None`** — new sub-structure if we want
  to capture process; substantive scope expansion, defer until we know
  Utah OPLR wants it.

The `category` enum is the highest-value cheap win — it makes the existing
6,000+ disciplinary_grounds rows queryable without re-extraction.

---

## 5. Scope of practice

### What we capture today

Two layers:

**Universal `ScopeOfPractice`** (`standard_model.py:485`):
- `definition_quote: StrEvidence` — verbatim statutory definition
- `methods_authorized: StrListEvidence` — e.g. `["medical", "surgical",
  "mechanical"]`
- `drug_authority: StrEvidence` — free text

**Universal flag** under `LicensureRequirements`:
- `scope_protection: BoolEvidence` — is performing the scope without a
  license prohibited? (vs. `title_protection` which is about the title)

**Per-profession discovered** — most scope detail lives here. Each profession's
pass-1b LLM defines its own scope-related narrative fields (e.g. podiatry has
`anatomical_scope`, `medication_authority`, `surgical_authority`,
`alternative_regulation` etc. as discovered fields). These are out of scope
for this audit.

### Population rates (universal scope fields)

| field | podiatry | medicine | nursing | dentistry | optometry | public_accountancy |
|---|---|---|---|---|---|---|
| `definition_quote` | 47/49 | 35/43 | 45/47 | 44/46 | 46/47 | 36/45 |
| `methods_authorized` | 47/49 | 34/43 | 42/47 | 43/46 | 46/47 | 39/45 |
| `drug_authority` | 34/49 | 28/43 | 39/47 | 40/46 | 46/47 | 0/45 |
| `scope_protection` (any value) | 49/49 | 39/43 | 46/47 | 45/46 | 46/47 | 43/45 |

`drug_authority` correctly = 0 for public accountancy. Otherwise well-populated.

### Structural limits

1. **`methods_authorized` is `list[str]` with no controlled vocabulary.** Cross-
   profession comparison ("which professions have surgical authority?")
   requires LLM clustering.
2. **`definition_quote` is one verbatim quote.** Many statutes spread the
   scope definition across multiple subsections; we pick one. Per-section
   scope evidence is the umbrella-scope pipeline's job, not this field.
3. **No structural decomposition of scope.** Anatomical region, modality,
   patient-class, setting, and authority over allied workers are all flattened
   into the definition_quote + methods_authorized + the per-profession
   discovered fields. The per-profession discovery does decompose this, but
   inconsistently across professions.
4. **Scope_protection is a single bool.** A state may protect *part* of the
   scope (e.g. surgery) while leaving the rest unprotected. We can't express
   that.

### Tagging proposals

- **`methods_authorized` keep free-form list, but add `method_categories: list[Enum]`** — `diagnosis / treatment / surgery / prescription / mechanical /
   physical_therapy / counseling / other`. Derivable from the existing
   `methods_authorized` strings via one-pass LLM normalization. Filterable
   cross-profession.
- **`scope_protection_partial: BoolEvidence | None`** — true if the state
   protects only part of the scope. Optional; complicates the simple
   `scope_protection` bool.
- **Cross-state scope decomposition (anatomical / modality / drug / setting)
  is a substantial schema expansion** — defer until we know Utah OPLR wants
  to consume it. This is the per-profession discovery layer's job today.

---

## What already exists — `map_prep/bucket_text.py`

Most of the "tagging proposals" above already exist as the `bucket_text`
Pass 3 (`pipeline/map_prep/bucket_text.py`). It reads each profession's
`map_prep/<profession>/spec.json`, finds all fields marked `not_mappable`
(free text), and asks Sonnet 4.6 to produce 3–7 buckets per field with a
per-state assignment. It has been **run for all 6 extracted professions**;
outputs live in `pipeline/results/map_prep/<profession>/text_buckets.json`.

What's already bucketed (counts are buckets-per-profession):

| field | already-bucketed? |
|---|---|
| `licensure.education.degree_required` | yes (5 buckets, podiatry) |
| `licensure.education.accrediting_body` | yes (5) |
| `licensure.post_degree_experience.kind` | yes (4) |
| `licensure.post_degree_experience.duration` | yes (5) |
| `licensure.issuing_authority` | yes (4) |
| `licensure.regulatory_authority.name` | yes (4) |
| `licensure.regulatory_authority.umbrella_agency` | yes (5) |
| `licensure.disciplinary_grounds` | yes (6) |
| `scope.methods_authorized` | yes (6) |
| `scope.drug_authority` | yes (5) |

So the per-field one-pass normalization machinery is already built and run.
The "tagging proposals" in the sections above mostly land *on top of*
existing bucket sets, not as net-new work.

### Two real remaining gaps in this layer

1. **Buckets are produced per profession, not harmonized across professions.**
   Podiatry's `Fraud & Misrepresentation` bucket and medicine's same-named
   bucket are independent LLM choices. They happen to line up well here but
   nothing in the pipeline enforces it. Cross-profession queries ("all
   professions where state X has a fraud ground") need a harmonization pass
   that takes the 6 per-profession bucket sets and produces a unified
   vocabulary.
2. **`disciplinary_grounds` is bucketed per state, not per ground.** The raw
   value fed to the LLM is the whole list of 14–24 grounds for a state
   stringified together; the LLM picks one bucket label for the state. That
   answers "what flavor of discipline statute is this," not "does this state
   include a fraud ground? a CE-noncompliance ground?" The latter — which is
   probably the more useful query for UORF cross-state work — needs
   per-ground assignment. Implementation tweak: `_collect_per_state` would
   need to fan out a `list[BaseModel]` field into one row per item.

## Cross-cutting observations

1. **Three of the 5 fields already have enums; two don't.** Licensing authority
   (`AuthorityType`) and scope (`scope_protection` bool) have controlled
   vocabularies. Education, experience, and discipline do not — but all three
   have `bucket_text` outputs, which functions as a derived enum at the
   per-profession layer.
2. **The remaining "schema work" is now narrower than I first wrote.** Two
   passes worth doing:
   - **Cross-profession bucket harmonization** — one meta-pass that takes the
     6 per-profession bucket sets per field and produces a unified vocabulary
     + a re-mapping from each per-profession bucket into it.
   - **Per-ground discipline bucketing** — modify `bucket_text` to handle
     list-of-objects fields by fanning out one row per item, then re-run on
     `disciplinary_grounds`. Outputs one bucket label per (state, ground).
3. **None of this requires re-extracting the existing 6 professions.** All
   operates on already-extracted free-text values + already-produced bucket
   sets.
4. **`umbrella_agency` and `accrediting_body` low populations are real, not
   extraction misses.** Don't try to force them up.
5. **Discipline is the field where Utah OPLR almost certainly wants more
   structure than we provide today**, given that disciplinary regime is part
   of the UORF "what does the state actually do" picture. The per-ground
   bucketing tweak is the highest-leverage move.

## Overlap with the May 30 pending changes

[[pending-extraction-changes]] added `alternative_regulation` (3 bools) and
re-worded the `credential_type = certification` rung. Neither touches
education, experience, licensing authority, discipline, or scope. The existing
extractions are usable as-is for this audit.

## Open questions for the user

1. **Per-ground discipline bucketing — do it before stage 2?** Highest-leverage
   single change identified. Modify `bucket_text._collect_per_state` to
   fan out list-of-objects fields, re-run on `disciplinary_grounds` across
   the 6 professions. Cheap LLM cost (~6,300 grounds in batches; few dollars).
2. **Cross-profession bucket harmonization — when?** Meta-pass over the 6
   per-profession bucket sets per field, produces a unified vocabulary. Worth
   doing once dietetics is added so we harmonize 7 professions at once
   instead of doing 6 now and re-doing 7 later.
3. **`sanctions_available` and `process` for discipline — in scope, or out?**
   Process is a substantial schema expansion. Sanctions is cheaper; statutes
   typically list them once per chapter.
4. **`siblings` for shared boards — worth capturing?** Cleanest way to surface
   "podiatry sits under medicine in 7 states."

Next: stage 2 is dietetics extraction. Stage 3 is the gap matrix (populated /
null / unverified per (profession × state × field), with null classification).
