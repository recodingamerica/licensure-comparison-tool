# NJ mapping repairs (#130) — what was actually wrong, and what changed

**Status: mappings fixed and re-pulled; extraction in progress.** Read the correction
first — the original plan for #130, and the `f49c11bc` commit message, both describe a
bug that does not exist, and prescribe a fix that would have made things worse.

---

## Correction 1 — five of the eight "broken" cells were never broken

#130 claimed a rebuild collapses five NJ cells to the whole of Title 45 (~2,500 sections)
because NJ Justia is flat and the label matcher hits the title.

A rebuild emits `title-45/` **with a `section_slug_pattern`** — the explicit-pattern form,
which is the legitimate second form of an NJ mapping. Those patterns were pinned in
`config/state_structure.yaml` under `NJ.professions.*` all along.

Resolved against the 2,285 title-45 section slugs in the committed hierarchy, both forms
give identical section sets, each matching the committed corpus exactly:

| cell | chapter form | pattern form | corpus |
|---|---|---|---|
| dentistry/NJ | 203 | 203 | 203 |
| dietetics/NJ | 129 | 129 | 129 |
| podiatry/NJ | 132 | 132 | 132 |
| public_accountancy/NJ | 149 | 149 | 149 |
| construction_trades/NJ | 22 | 22 | 22 |

The prescribed fix — exclude bare `title-45/`, re-add chapter nodes — would have been
net-negative: `exclude` matches on exact url, and the pattern node's url **is**
`https://law.justia.com/codes/new-jersey/title-45/`, so it would have deleted a working
`state_structure` pin and replaced it with a redundant `mapping_overrides` one.

## Correction 2 — "0 published cells changed" was the wrong success criterion

Keyed on `(url, via)`, it was unachievable: chapter-form and pattern-form are both
correct, so those cells differ by url form no matter what. Chasing it to zero is what
would have produced the churn it was meant to prevent.

Five more cells (`architecture/MA`, `hvac/AL|MD|NC|TX`) differ only because the committed
indexes held root-relative urls that `f49c11bc` normalized; MA also carries year-stamped
duplicates. Canonicalize scheme, host and year segments away and all five are identical.

**Compare resolved section SETS, not node urls.**

---

## What was actually broken

### a. Loose-section fallback (4 cells)

A profession with no `section_slug_pattern` fell back to whatever loose sections the label
matcher happened to hit:

| cell | index held | corpus held |
|---|---|---|
| electrician/NJ | 6 loose sections | 71 (chapter 5A) |
| plumbing/NJ | 2 loose sections | 37 (chapter 14C) |
| architecture/NJ | 15 loose sections | 148 |
| hvac/NJ | 4 loose sections | 42 |

electrician and plumbing were caught because their committed indexes still held
hand-written chapter nodes. **architecture and hvac were not** — their indexes were
already broken and nobody had re-pulled them, so the corpus was the only witness. A
routine re-pull would have collapsed 148 → 15 and 42 → 4. This class is invisible to an
index-vs-rebuild check: both sides agree on the wrong answer.

### b. `public_adjuster/OR` pointed at a dead url

Justia's Oregon is volume-scoped. The override held `oregon/chapter-744/` and overwrote
the committed index's working `volume-18/chapter-744/` on every rebuild. Fixed in place.

### c. Six cells were missing law that governs them by statute

NJ 45:1-2.1 "Applicability of act" enumerates the boards the **Uniform Enforcement Act**
covers, and names the Board of Examiners of Electrical Contractors, the State Board of
Examiners of Master Plumbers, the State Board of Examiners of Heating, Ventilating, Air
Conditioning and Refrigeration Contractors, the NJ State Board of Architects, and the
State Board of Professional Engineers and Land Surveyors. For construction_trades the
chain is exact: 45:5AAA-3 establishes the NJ State Board of Home Improvement and Home
Elevation Contractors, added to 45:1-2.1 by **the same 2023 c.237** that created 5AAA.

Chapter 1 carries the disciplinary grounds the individual chapters don't repeat —
`45:1-21 "Refusal to license or renew, grounds."` construction_trades/NJ had **zero**
disciplinary grounds before this.

The seven health/finance NJ cells already included 45:1. The six trades did not.
`public_adjuster/NJ` correctly stays out: Title 17, not a Title-45 board.

### d. architecture and professional_engineering were mutually over-broad

Both had near-identical chapter sets (3, 4B, 8, 14A, +26 for PE) because the label matcher
grabbed any chapter naming either trade. Split on which board each chapter establishes:

| chapter | what it is | goes to |
|---|---|---|
| 45:3 | NJ State Board of **Architects** | architecture |
| 45:8 | Board of **Professional Engineers, Land Surveyors** | professional_engineering |
| 45:4B | **Joint Committee of Architects and Engineers** | **both** — it governs the boundary between the two practices |
| 45:14A | professional **planners**; 45:14A-3 *exempts* architects, engineers, surveyors | neither |
| 45:26 | **Crane Operators** License Advisory Board | neither |

Both cells gained relevant law and shed irrelevant law at once: PE picked up 114 sections
of disciplinary grounds and dropped 77 about cranes and architects.

---

## Final state

| cell | before | after | delta |
|---|---|---|---|
| architecture/NJ | 148 | 169 | +45:1, −ch 8, −ch 14A |
| professional_engineering/NJ | 165 | 202 | +45:1, −ch 3, −ch 14A, −ch 26 |
| electrician/NJ | 71 | 185 | +45:1 |
| hvac/NJ | 42 | 156 | +45:1 |
| plumbing/NJ | 37 | 151 | +45:1 |
| construction_trades/NJ | 22 | 136 | +45:1 |

Every cell landed on its predicted count with the intended chapter composition, no thin
sections and no fetch errors. The four health cells resolve identically to before and were
not re-pulled.

All 13 NJ professions now run on ONE mechanism — `state_structure.yaml` patterns — instead
of three. That retired two now-redundant `mapping_overrides` blocks, including the 47-line
`professional_engineering/NJ` migration from `f49c11bc`; its nine `exclude` entries turned
out unnecessary once a pattern node replaces label matching.

### The overwrite guard did its job

architecture and PE fetched fully and then **refused to write**: `pull_text._is_regression`
blocks a pull that loses committed sections. The losses were the intended re-scoping (93
and 77 sections), but a guard cannot tell deliberate narrowing from a bad pull, so
refusing is correct. Overridden deliberately with `--force`.

---

## Guards added

`tests/test_match_profession.py::TestRebuildIsANoOp`, two tests:

1. **`test_rebuilding_does_not_change_published_mappings`** — rebuilds every published
   profession in memory and asserts no cell's resolved section set moves. Compares section
   sets, not urls. Verified red on the real regression (`electrician/NJ: 71 -> 6`).
2. **`test_nj_corpus_matches_what_the_index_maps`** — asserts each NJ cell's committed
   corpus is exactly what its mapping resolves to. This is the one that catches class (a)
   above, which the first test structurally cannot see. Verified red at
   `corpus 185 vs mapping 71 (corpus-only 114)`.

**Test 2 is NJ-scoped deliberately.** NJ is flat, so the mapping is a title url plus a
pattern and `hierarchy/NJ.json` is the complete flat section list — the pattern alone
resolves exactly. Elsewhere a pattern is relative to its node's chapter: matching it
against a whole state's hierarchy over-matches (MA repeats `section-43` across many
chapters of a title) and under-matches (OR's hierarchy is chapter-level, so no section
slug appears). Generalizing needs container-scoped resolution. The other states are not
broken — an earlier draft of this check reported 14 "mismatches" that were all artifacts
of resolving patterns without chapter scope.

`pipeline.eval.audit_mappings` already covers this bug class and *would* have caught the
original architecture/hvac breakage (133 strays against 15 mapped nodes), but nothing
gates on it for published cells. It also cannot see the new mapping style: the node url is
the whole title, so every section counts as "under a mapped chapter" and the pattern that
does the narrowing is invisible to it.

---

## The 45:1 question, settled by measurement

Adding chapter 1 looked like it might be redundant churn, because NJ had an umbrella that
was supposed to supply it. It was not redundant, and the reason matters:

`extract_state.load_umbrella_text` drops sections whose `scope_source` is `undetermined`
— "that's the loud failure path." **All 39 NJ umbrella sections were `undetermined`**, so
the function returned an empty string for every NJ profession. The umbrella was shipping
108KB of duplicate text into every payload while contributing **nothing** to extraction.

The evidence: chapter-1 quotes per cell went **0 → 3, 15, 14, 16, 14, 14** (76 total).
Zero before, in every one. These professions had none of the Uniform Enforcement Act.

The cost is real but smaller: practice-act quotes drift 295 → 277, and six fields dropped.
Investigating each rather than trusting the summary, four of the six are **corrections**:

- `electrician.age_minimum` / `moral_character_required` cited **45:5A-27**, which reads
  "An applicant seeking licensure to engage in the **alarm business** shall: (1) Be at
  least 18 years of age". NJ chapter 5A covers electrical contractors, alarm businesses
  and pool/spa contractors under one board — the old extraction attributed alarm-business
  requirements to electricians.
- `architecture` + `professional_engineering` `renewal_fee_usd` dropped in BOTH, which is
  a pattern, not variance. Chapter 1 carries the renewal-fee framework (45:1-7.1, 45:1-7.4)
  under which boards set fees by rule; the old value was the **$15** in 45:3-7, long
  superseded. Publishing "$15" as the architect renewal fee would have been misleading.

The remaining two (`electrician.apprentice_supervision_ratio`, `plumbing.national_association`)
are marginal captures, not clear regressions. No re-extract was run to chase them: that
would risk 76 good quotes to maybe recover one questionable field.

## NJ umbrella: retired

It was 100% chapter 1, a strict SUBSET of chapter 1 in all 13 title-45 corpora, never
injected into extraction, and for `public_adjuster` (title 17, not a 45:1-2.1 board) it
shipped law that does not apply. Removed `umbrella_text/`, `umbrella_scope/`,
`umbrella_scope_llm/` and `umbrella_chapters/` for NJ so the generator won't recreate it.

Corpus-based chapter 1 is also better for the UI: it ships real per-section citations that
resolve against the displayable-quote gate, where the umbrella shipped one opaque
`UMBRELLA / <chapter>` aggregate.

`build_frontend` additionally skips any umbrella section the profession's own corpus
already carries (both `row.sections` and browse) — general, not NJ-specific. This changes
payload content, so `CODE_VERSION['publish']` went 2 → 3.

## The publish path (learned the hard way)

`refresh_all` hardcodes `run_to("publish", p, start="verify")`, so it runs the LLM `verify`
and `map_prep` stages for every profession whose extract is stale — which is most of them.
Started on 39 professions, it modified `anesthesiologist_assistant/CO.json` (a profession
nobody touched) before being killed; that change was reverted.

**Use `--start publish` and scope to the professions actually on the site:**

```bash
python -m pipeline.pipeline_stages --queue <14 published> --target publish --start publish --yes
```

That runs `build_frontend` only — deterministic, no LLM, `$0` (neither `publish` nor
`fanout` has a `costs.yaml` entry). Do NOT run the full `fanout`: **26 of 39** professions
lack `field_semantics.yaml`, so it fires `gen_semantics` for each, plus `harmonize_universal`.
The two artifacts the freshness test needs — `build_scope_matrices` and
`cross_comparison_scorecard` — have their own LLM-free builders and can be run directly.

## Open

- **`construction_trades/MO`** — an 89-section corpus that is Missouri chapter 436,
  FRANCHISE law, under construction trades. The index has **no matched nodes** for the
  cell, so a re-pull reproduces nothing and extraction correctly returned an all-null
  record. Needs either a correct chapter or a verified-absence marking.
- **56 NO_MAPPING published cells** across all states (`audit_mappings`) — committed
  corpora a re-pull could not reproduce at all. MO above is one of them.
- **Duplicate override nodes** — rebuilds log `add url ... already present with a
  different dict` for `construction_trades` ID/UT/WV and `public_adjuster` MD.
- **`public_adjuster` AK / AR** — empty, undiagnosed. OR was empty because of the dead
  volume-less url fixed here, and needs a re-pull + re-extract to fill.
- **`land_surveying`** shares 45:8 with PE. Unpublished, not touched.
- **Pull provenance** for the six cells reads stale because `pull_text` was invoked by
  hand rather than through the runner. The corpora are verified correct; the stamps need
  settling.
