# Utah Licensing Pipeline — Status Writeup

**June 12, 2026**

Live site: utah-licensing.vercel.app (behind HTTP Basic Auth)

## Summary

Over the past week we shipped the feedback from the June 10 issues batch (disciplinary tagging, tag sheet usability, priority maps), validated our regulatory-model extraction against Utah OPLR's own published classifications (9 of 9 professions match, including 8 we had never extracted before), and made the publish pipeline incremental so data refreshes are fast and cheap. The new issues filed this week are all about state-level data gaps in dietetics and optometry, and they point to a common root cause we now understand: professions whose statutes don't live in a dedicated, findable chapter.

## Recent issues: where things stand

### Closed this week

**#18 — Disciplinary tagging and visibility.** Done. Disciplinary grounds now show as content tags per state rather than just a count. The table has a "Disciplinary categories" column with per-state chips (e.g., Regulatory 4, Fraud 2, False Advertising 1) that you can filter on, and the state detail panel groups each state's grounds under category subheaders.

**#20 — Tag sheet hover.** Done. The hover tooltip that disappeared when you moved the cursor is replaced: clicking a tag now pins a persistent side panel with the full per-state breakdown (every bucket, each state's underlying statute text), scrollable, with a Copy All button.

**#21 — Maps for optometry/dietetics priority fields.** Done. The map field dropdown now leads with a "Priority fields" group (Minimum Degree, Professional Experience, Licensing Authority, Scope of Practice), each as a categorical choropleth, plus a new "Scope breadth" group mapping how many distinct procedure categories each state authorizes. Discipline is intentionally not a single map — it's multi-valued per state — so it's surfaced through the tag sheet and the new table column instead.

### Open, with work done and a decision pending

**#19 — Scope of practice specificity.** Partially built: profession-specific scope tags (laser procedures, injections, etc.) are live, along with a table view toggle (Priority / Scope / Discipline / All views). Two things remain, and one is a decision rather than a task:

1. *The requested fine distinctions mostly aren't in the statutes.* The broad buckets work — trabeculoplasty (5 states), capsulotomy/YAG (6), peripheral iridotomy (3), injections (16). But no state statute distinguishes ALT from SLT (zero say "argon"), and no state subdivides intraocular injections into anterior-chamber vs. vitreal. The law regulates at the coarser level; coding finer categories would leave the cells blank.
2. *How we make categories at all.* Today every category is LLM-clustered from the actual statute text — automatic and generalizes across professions, but the granularity is chosen by the model, not validated against a standard. The alternative is hand-authoring fixed vocabularies for chosen high-value fields, which gives controlled categories but needs per-field curation and an owner. This is a deliberate choice we should make together rather than drift into.

### New this week: data-gap issues (#24, #25, #26)

These three issues, filed June 12, are about states that come up blank or nearly blank even though the law exists.

**#24 — Wrong gap label.** Dietetics gap states display "No Podiatry chapter found." The fallback label is hardcoded to the wrong profession. Small fix; not yet done.

**#25 — Dietitian gaps (~8 states).** A Claude-assisted source check found statute material we missed in FL, PA, WI, MI, MN, MO, and SC (CO genuinely has no credential — the 2025 bill was vetoed). The accompanying regs are mostly procedural detail (fees, CE logistics), so statutes remain the right target.

**#26 — Optometrist gaps (4 states).** Same exercise for optometry: MI, MN, PA, NY.

**The pattern behind both.** The gap states fail for identifiable structural reasons, not randomly:

- *Profession buried inside a shared code:* Michigan optometry is one "Part" inside the giant Public Health Code; Minnesota optometry shares chapter 148 with a dozen other health professions. There's no dedicated chapter for our crawler to key on.
- *Non-standard numbering:* Pennsylvania uses pamphlet-law numbering (63 P.S.) rather than a consolidated code chapter — this hits both dietetics and optometry the same way.
- *Fetch failures:* New York's Article 143 was actually located but the pull truncated after the table of contents — a crawling bug, not a discovery problem.
- *Credential housed under another board:* Pennsylvania dietetics lives in the Professional Nursing Law.

This matches what we documented earlier with Montana's Title 37-1 (a centralized cross-profession discipline chapter whose absence zeroed out disciplinary grounds in four professions). The fix direction we've already committed to — per-state scope manifests that declare which chapters cover which professions, rather than more regex or LLM guessing — covers most of these. The NY-style truncation is a separate scraper bug to fix on its own.

### Other open issues (unchanged this week)

Scraper issues for year-versioned statute pages in IL and ND and Michigan's act-level structure (#6, #7, #8); umbrella-scope findings and cross-profession bucket harmonization (#1, #14, #16); bucket-as-label in the profile table (#15); and the lit-review tracking issue (#17 — the review itself is done and written up in docs/lit_review/).

## What we shipped this week (June 9–12)

**Validation against Utah OPLR ground truth — 9/9 match.** Utah OPLR publishes periodic-review reports stating each occupation's current regulatory model. We built a harness comparing those classifications to our Utah extractions, then ran a genuine held-out test: 8 professions we had never extracted or tuned on (physician assistant, physical therapy, occupational therapy, respiratory care, acupuncture, athletic training, hearing instrument specialist, speech-language pathology/audiology). All 8 plus nursing match OPLR's classification — including the two trickiest cases, where OPLR *recommends* moving to mandatory certification but current law is still licensure, and our extraction correctly reads current law.

**Regulatory-model prompt fix.** Before the test, we re-anchored the classification rule on what the credential actually protects (scope of practice vs. title only), matching Utah OPLR's framework. Re-extracting all 42 dietetics states produced 7 corrections toward Utah's rule and zero regressions.

**Field Tag Sheet and Tags tab.** A per-profession sheet of content tags — the 5 priority fields on top, every other bucketed field below — live at /reports/tag-sheet and as a Tags tab on each profession page. Also fixed a robustness problem in the bucketing pass that was truncating large fields and timing out.

**Per-state content tags in the table and detail views** (PR #22, closing #18/#20/#21 and part of #19, described above).

**Faster, cheaper publishing.** The publish step now skips uploads whose content hasn't changed (incremental by content hash), logs honestly what was cached vs. uploaded, has a single no-LLM orchestrator to refresh everything, and a fast path for tags-only changes that skips regenerating the browse data (about 10x faster for that case).

**Housekeeping.** Repo reorganization (reports into docs/reports/, eval runners into pipeline/eval/), refreshed README, June 9 STATUS.md, and a re-extract of Washington optometry that was missing its umbrella discipline chapter.

## Coverage snapshot

Full 50-state extractions: dentistry, dietetics, medicine, nursing, optometry, podiatry, public accountancy (7 professions). Utah-only extractions for the 8 held-out validation professions listed above — expanding any of them to 50 states is a pipeline run away. Known coverage caveats are the data-gap states in #25/#26 and the scraper issues above.

## Likely next steps

1. Fix the mislabeled gap text (#24) — quick.
2. Fix the NY truncation scraper bug and re-pull.
3. Add per-state scope-manifest entries for the gap states in #25/#26 (MI, MN, PA, FL, WI, MO, SC for dietetics; MI, MN, PA for optometry) and re-extract.
4. Decide together on #19: stay fully LLM-clustered, or hand-author vocabularies for specific high-value fields — and if the latter, which fields and who owns them.
