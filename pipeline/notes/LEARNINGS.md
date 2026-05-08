# Learnings

Running notes on quirks we hit, design choices we made, and tradeoffs that
were not obvious before we started. Updated as we go.

## Source coverage on Justia

Justia is free and structured but not uniformly complete. State-level coverage
gaps fall into a few buckets, listed in order of how solvable they are
without per-(state,profession) hand-curation:

- **Year-versioned root.** KY/OR/NV's `/codes/<state>/` page only lists
  year-stamped indexes (`/codes/kentucky/2024/`, etc.) — no chapters at the
  bare root. `build_hierarchy.crawl_chapters` now auto-detects this shape
  and re-fetches at the latest year. Once the year-versioned URL is
  reachable, label-match sees the real chapter list (KY has 750 chapters,
  NV 824) and finds profession-named chapters automatically.
- **Subtitled / volume layer.** AR/CO/CA/TX/OR insert a subtitle or volume
  between the title and the chapters. The hierarchy crawl stops at that
  layer and shows generic labels ("Subtitle 3 — Medical Professions"). When
  `state_structure.yaml` marks `layout: subtitled`, `build_hierarchy` drills
  one level deeper and flattens the result so chapters with descriptive
  labels ("Chapter 96 - PODIATRIC MEDICINE", "Chapter 90 - OPTOMETRISTS")
  show up for label-match.
- **Section-range within a bigger title.** AZ, OK, WI, LA show flat
  section lists (no chapter level on Justia for those states); each
  profession lives in a contiguous section range. Solved by
  `map_state_sections_v2.py`: fetch a body-excerpt cache once per state
  (~30 min wall time), then a single Sonnet call per state tags every
  section with the profession it covers. `match_profession` consumes
  `section_maps/<STATE>_v2.json` directly, so a new profession is auto-
  covered in any state with a v2 cache — no per-profession hand-curation.
- **Profession buried under parent chapter.** AL/AK/OH/VA regulate
  podiatry under "Medicine" or "Healing Arts" rather than as a standalone
  chapter. Label-match misses these. The labels-only chapter mapper
  (`map_state_chapters.py`) was tried as an automation hook and refused to
  assign these chapters to just one profession (correct behavior — the
  chapter covers many), so it adds nothing here. Hand-curated
  `state_structure.yaml` URL overrides remain the answer until we add
  body-excerpt context + multi-profession-per-chapter handling.
- **Recodified or repealed.** WV §30-11 was repealed in 1980; current law
  is in Medicine §30-3. CO renumbered podiatry from Article 32 to Article
  290 in 2019. Labels-only chapter mapping picks the historically-named
  (now repealed) chapter; this case also needs body excerpts. Hand-curated
  for now.
- **Genuinely missing or paywalled.** PA's Justia has only 5 nav-style
  chapters under Title 63 and no podiatry-specific URL. Needs a different
  source (the official PA Code or Westlaw). Documented as a coverage gap.
- **External sources.** MI / MN are on `mi_legis` / `revisor_mn` rather
  than Justia. Their hierarchy crawls and pull strategies are in
  `_fetch.py`; profession matching for them is hand-curated inside
  `state_structure.yaml`.

Net: with year-versioned + subtitled drill + v2 section maps, common
professions reach 46-47/50 states with no per-profession hand-curation.

## Hierarchy crawl quirks

- `build_hierarchy.crawl_chapters` runs three escalating extraction
  strategies in order, all driven by `state_structure.yaml`:
  1. If the root URL returns chapters → done.
  2. Else if the page only has year-stamped index links
     (`/codes/<state>/<YYYY>/`), pick the latest year and re-fetch.
  3. If `layout: subtitled`, drill each top-level entry's URL into its
     chapters and flatten the result.
- After those, the only remaining chapter-list misses are external sources
  (MI, MN), broken Justia (PA), and one-off layout quirks worth a yaml
  override.
- `section_fallback` extraction is detected automatically when chapter
  extraction returns nothing but section extraction does — typical for
  AZ, OK, WI, LA. `match_profession` resolves these via either a
  hand-curated `section_slug_pattern` or, preferably, a v2 section map.

## Pattern-matching the chapter label

- `medicine` matched too few states (22/50) because the exclude list was
  over-aggressive — it excluded podiatric/osteopathic/etc. but missed obvious
  Medicine chapters like NY's "Article 131 - Medicine" because they don't
  have an explicit "physicians" word. Pattern tuning is finicky.
- "construction trades" matched 4/50 because trades are usually licensed
  under building/construction code, not professional licensing. Low base
  match isn't a coverage gap — it's a structural difference between states.
- The Utah-derived `professions.yaml` is biased toward how Utah codes things;
  other states' framings (e.g. "Mental Health Counseling / MFT / Clinical
  Social Work" lumped together vs. separated) don't always map cleanly.

## LLM extraction observations

- **Sonnet 4.6 vs Haiku 4.5.** Haiku missed obvious in-corpus fields:
  CT's three-year residency, ME's CE topical requirements (which Sonnet
  correctly classified as topical, not as overall hours), KS/WA's annual
  renewal references. Sonnet's quote alignment is also better — 98.1%
  regex-validated for podiatry vs ~95% with Haiku.
- **Where Sonnet stays silent over guessing.** When a state's renewal
  language is *conditional* (CT mentions only annual renewal of *exempt
  licenses*) or has *multiple variants* (CT has both 2-year pre-2006 and
  3-year post-2006 residency), Sonnet leaves the field null rather than
  pick one. That's correct behavior — the source is genuinely ambiguous —
  but it shows up as a coverage gap.
- **Smart quotes/dashes/ellipses break naïve regex matching.** The first
  pass had ~5% unverified-evidence rate just because Justia uses curly
  quotes (`"`) and the LLM wrote ASCII (`"`). Normalizing typography +
  stripping all non-alphanumeric for the match dropped unverified to 1.9%.
- **Enum-typed fields fail when the LLM guesses outside the set.** SC's
  ankle-surgery residency requirement didn't fit any of the discovered
  enum values. We added a graceful recovery path: on Pydantic ValidationError,
  null-out the offending leaf and re-validate, instead of dropping the
  whole record.

## Architecture choices that paid off

- **Profession is always a parameter.** No string "podiatry" appears in
  code. Adding a profession is one entry in `professions.yaml` plus running
  the pipeline — no code changes. CPA was added with zero code edits.
- **Hierarchy is profession-agnostic.** One crawl per state, reused for
  every profession, cached on disk. We crawled 50 states once and run any
  number of profession matches against it.
- **Two-stage LLM extraction.** Pass 1b (schema discovery) over the whole
  corpus produces a typed field list — then pass 2 fills it per state.
  Means the field set adapts to what the profession actually has, vs
  hard-coding podiatry-specific fields up front.
- **Evidence wrappers + regex check.** Every leaf field carries
  `{value, quote, citation}`, and the quote is regex-validated against the
  cleaned source. Eliminates most hallucination — a fabricated value also
  needs a fabricated quote, which won't match the source.
- **Manual overrides are explicit, not magical.** When the auto-match
  fails for a (profession, state) pair, you write 3 lines in
  `manual_overrides.yaml` instead of monkey-patching code. The LLM
  classifier proposes them; humans confirm.

## Architecture choices that needed correction

- **Section-fallback mode initially flattened the data.** The first pass
  treated section_fallback states as having "chapters" that were actually
  individual sections — so AZ matched 5 podiatry-named sections instead of
  the full 50-section chapter. The section_slug_pattern fix recovered.
- **Trim was too aggressive on small corpora.** OK only had 6 cleaned
  sections; trim dropped 4 of them as administrative, leaving 2 sections
  that didn't include the substantive licensing rules. Trim works on
  larger corpora but a small-corpus fallback rule (keep everything when
  total is below N sections) would help. Not yet implemented.
- **Frontend's anatomical-scope chip was profession-specific.** Originally
  baked into the universal template; had to be moved to the modal so
  CPA's profile didn't show an empty Anatomical-scope column. General
  rule now: only universal fields land as table columns.

## Non-Justia sources we've validated

Once we hit the gap states, we probed alternate sources to assess
gettability. The picture differs sharply state to state.

- **MN — `revisor.mn.gov`** is the cleanest non-Justia source we found.
  Per-section URL pattern is `https://www.revisor.mn.gov/statutes/cite/153.NN`.
  Section content sits in a `.section` div with no JS rendering. Adding it
  was 28 lines of `section_url_list` in `manual_overrides.yaml` plus one
  selector in `extract_section_text()`. ~30 minutes total.

- **MI — `legislature.mi.gov`** is doable but uglier. Per-section URLs use
  a query string `?objectName=mcl-333-NNNNN`. The section content sits in
  a `div[class*="section"]` block. Section ranges have gaps (some numbers
  are skipped — repealed). We hand-listed the 15 podiatry sections from
  Part 180 of the Public Health Code. ~45 minutes total.

- **PA — `palegis.us`** turned out to be genuinely hard. The site is
  query-string-driven (`uconsCheck.cfm?...&act=375`) and our probes didn't
  surface podiatry-specific content even at the right act number. Probably
  needs Playwright + custom navigation, or a different source entirely
  (the human-compiled podiatry PDF used Westlaw). Documented as a deferred
  gap.

- **FindLaw** appeared to host state codes but is anti-scrape — returns a
  small wall page (~2.7 KB) for direct URL probes regardless of the path.
  Not a viable fallback.

- **Cornell LII** doesn't host state statutes. It has US Code, CFR, Wex
  glossary, and uniform laws. Useful for federal references but not for
  state-by-state extraction.

The pattern across these: most state legislatures publish per-section
HTML with stable URLs. Each one needs roughly an hour of investigation
to find the URL convention and the right CSS selector for the body. After
that, it slots into our pipeline as a `section_url_list` override + one
extra selector in `extract_section_text`.

## State structure index — what we found

Reorganizing per-(state, profession) overrides into a state-keyed
`state_structure.yaml` was a unifying move. The state-level facts —
`source: justia | revisor_mn | mi_legis | …` and `layout: chapter |
section_fallback | subtitled | external | broken` — apply to every
profession in that state. The per-profession entry just provides the
profession-specific URL or section pattern.

Once state structure is recorded, adding a profession to an existing
state is a one-line entry under the right state's `professions:` block.
Adding a state we've never seen requires figuring out source + layout
once; subsequent professions in that state slot in cheaply.

`manual_overrides.yaml` was deleted — `state_structure.yaml` is the
single source of truth.

## LLM-driven section mapping — v1 is risky, v2 with body excerpts works

For section_fallback states (AZ, OK, LA, WI), each profession lives in
a number range within a giant flat title (~1500–2000 sections). To
automate finding those ranges we built `map_state_sections.py`:

- **v1 (label-only)** — sends Sonnet `(slug, label)` per section + the
  46 profession registry, asks for per-profession section lists. Works
  when labels are descriptive ("§32-851 Practicing podiatry without
  license"). Fails when labels are generic.
  Concrete failure: LA Title 37 has §§37:611-629 = podiatry, but every
  section's label is generic ("Definitions", "License required",
  "Qualifications"). Sonnet labeled the entire range as opticianry.
  Lesson: labels alone aren't enough discrimination signal.

- **v2 (label + body excerpt)** — adds a one-time per-state bulk fetch
  of ~300 chars of body text per section, cached in
  `results/section_bodies/<STATE>.json`. Sonnet then sees the actual
  statutory text — "(1) 'Podiatry' or 'podiatric medicine' means the
  diagnosis or treatment, or holding out…" — and can disambiguate
  generic-labeled sections.
  Cost: one-time body fetch per state (~40 min serialized at
  PER_HOST_DELAY=1.2s for a 2000-section state; could parallelize),
  plus the same Sonnet call as v1.

The v1/v2 split is a useful reminder: LLMs without enough discrimination
signal will confidently output the wrong thing. Constraining the output
type (Pydantic Literal of valid slugs) catches hallucinated slugs but
not mislabels.

## Plain-English category labels (the advanced_tier saga)

Initially I hand-coded `FieldCategory` as an enum (`scope_inclusion`,
`advanced_tier`, `anatomy_or_procedure`, etc.) and constrained the
schema-discovery LLM to pick one. The labels were jargony and not
intuitive.

Fix in two steps:
1. `recategorize_fields.py` — surgical post-process that asks Sonnet to
   regroup an existing field list into 5–8 plain-English categories. No
   re-extraction needed; only the `category` value changes.
2. Updated `discover_schema.py` to drop the enum entirely. Future
   profession runs get LLM-named categories on first pass.

Result for podiatry: 8 hand-coded jargon categories →
7 LLM-named ones like *"what they can treat and where on the body"*,
*"surgery and procedures they can perform"*, *"ankle surgery
qualifications and limits"*, *"supervision and delegation"*.

Removing the enum guardrail was fine because the categories aren't
load-bearing for downstream code — they only group fields in the modal.

## Verifier tolerance: ellipsis-elided quotes

The first verifier rejected ~5% of LLM quotes because the LLM elided
non-contiguous segments with `...`:

  Original source: "Any person except a licensed podiatrist [...] who
  practices podiatry [a long clause about diploma fraud here] shall be
  guilty of a class D felony"
  LLM quote:       "Any person except a licensed podiatrist ... who
  practices podiatry ... shall be guilty of a class D felony"

The matcher rejected because the elided middle part (about diploma
fraud) didn't appear contiguously between the quoted phrases. It's
technically the LLM tightening a wordy source, not fabrication.

Fix: split the quote on `...` / `…` BEFORE normalization; require each
part to appear in order in the corpus. Lifted podiatry from 96.5% →
98.7% verified, CPA from 92.2% → 95.9%.

The remaining ~2% unverified are probably real LLM paraphrasing slips
or genuine misalignments — the matcher is now appropriately tolerant
without being too loose.

## Frontend evidence affordances

Each evidence quote in the modal got two affordances after the user
asked for source-clickability:

- `source ↗` — opens the actual section URL in a new tab (Justia /
  revisor.mn.gov / legislature.mi.gov / etc.). build_frontend.py threads
  the trimmed sections through to data.json keyed off the row's full
  record so each evidenceRow can find its source by citation.
- `in context` — toggles an inline panel showing the full section text
  with the quoted phrase wrapped in `<mark>` tags. Highlight matching
  is whitespace-flexible (`\s+` regex) so source line breaks don't
  break the match.

data.json grew from ~270 KB to ~3.4 MB because every state's trimmed
section text is now inline. Still small enough for static serving.

## Open work / known limits

- Admin code (CE rules, sub-regulation) lives outside statute on most
  states; `regs_targets.csv` is enumerated but not wired through the
  pipeline. Would close many of the visible "—" cells under CE hours.
- 3 states (PA, MN, MI) need either Westlaw access or a more invasive
  per-state scraper. Probably accept the gap for now.
- The `regulatory_model` field is a six-rung enum, but the LLM may need
  more guidance to distinguish "license" vs. "mandatory certification" —
  the line is fuzzy in some statutes.
