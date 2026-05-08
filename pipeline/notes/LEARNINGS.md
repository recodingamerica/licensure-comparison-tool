# Learnings

Running notes on quirks we hit, design choices we made, and tradeoffs that
were not obvious before we started. Updated as we go.

## Source coverage on Justia

Justia is free and structured but not uniformly complete. State-level coverage
gaps fall into a few buckets:

- **Profession buried under parent chapter.** Most common case. AL/AK/OH/VA
  regulate podiatry under "Medicine" or "Healing Arts" rather than as a
  standalone chapter. The label matcher misses these — the LLM-backed
  `suggest_overrides.py` finds them by reading chapter labels and proposing
  candidates for human review.
- **Section-range within a bigger chapter.** AZ, OK, KY, LA bury podiatry
  inside a much larger title or chapter (e.g. AZ Title 32 has 1500+ sections;
  podiatry is §§32-801..32-859). Solved by `section_slug_pattern` overrides.
- **Recodified or repealed.** WV §30-11 was repealed in 1980; the current
  law is in Medicine §30-3. CO renumbered podiatry from Article 32 to
  Article 290 in 2019. The original target URL on Justia returns the
  obsolete chapter, not the current one.
- **Justia layout differences.** NV's `title-54` parent doesn't list
  chapters at all, but `/codes/nevada/chapter-635/` works directly. AZ has
  no chapter-level URL — only sections.
- **Genuinely missing or paywalled.** PA's Justia has only 5 nav-style
  chapters under Title 63 and no podiatry-specific URL. Probably needs a
  different source (the official PA Code or Westlaw).

## Hierarchy crawl quirks

- Six states return `section_fallback` mode: AZ, OK, MI, WI, LA — and AZ/OK
  show 1500+ "chapters" which are actually individual sections at the title
  level. The hierarchy crawler can't distinguish a section-fallback from a
  real chapter list, so `match_profession.py` needs the `section_slug_pattern`
  mechanism for these.
- AR/CO/CA show "subtitles" or "divisions" at the level the crawl stopped at
  (one level shallow). A depth-2 crawl would expose the right chapter but
  costs ~50 minutes extra; we're handling them via direct chapter URLs in
  manual overrides instead.
- NV / PA / MN have hierarchy quality issues that need state-specific URL
  fixes in `targets.csv` (the configured parent URL is wrong for these).
- KY/WV had a working hierarchy but the matched chapter was thin or repealed
  — required overriding to a different chapter.

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

## Open work / known limits

- Admin code (CE rules, sub-regulation) lives outside statute on most
  states; `regs_targets.csv` is enumerated but not wired through the
  pipeline. Would close many of the visible "—" cells under CE hours.
- 3 states (PA, MN, MI) need either Westlaw access or a more invasive
  per-state scraper. Probably accept the gap for now.
- The `regulatory_model` field is a six-rung enum, but the LLM may need
  more guidance to distinguish "license" vs. "mandatory certification" —
  the line is fuzzy in some statutes.
