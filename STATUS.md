# Status

Live site: https://utah-licensing.vercel.app (pw `utah`).
Pipeline shape and Postgres direction: see [ARCHITECTURE.md](ARCHITECTURE.md).

## Just shipped (June 9, 2026)

- **Field Tag Sheet + profile Tags tab.** `pipeline/publish/build_tag_sheet.py`
  reshapes the map_prep bucket output into a per-profession sheet — the 5
  priority fields (Min Degree, Prof Experience, Licensing Authority, Scope,
  Discipline) on top, every other bucketed field below. Live at
  `/reports/tag-sheet` and as a new **Tags** tab on `/professions/[id]`
  (`components/profile-tags.tsx`, additive — reads `tag_sheet.json`, no change
  to table/map/statutes). Hovering a tag shows its member states + the original
  text (raw_value for scalar, ground label for per-item discipline).
- **bucket_text robustness fix.** The pass made the LLM echo every input value
  back, truncating large scalar fields and timing out big per-item fields.
  Scalar now returns `{state,bucket}` only (raw_value re-attached our side);
  per-item designs the vocabulary once then assigns in 150-row chunks. Also
  fixed `map_prep/run.py` Evidence-leaf flatten (verifier annotations leaked
  `<field>.value/.quote/...` as bogus fields). All 7 professions leak-free.
- **regulatory_model prompt fix (Utah scope rule).** Anchored the rung on what
  the credential PROTECTS: mandatory_cert/license require scope_protection;
  title-only = voluntary_certification (right-to-title) even if the title is
  mandated. Matches Utah OPLR's framework. Re-extracted all 42 dietetics — 7
  corrections toward Utah's rule, 0 regressions (AK/CA/UT/VA/VT/WA
  mandatory_cert→voluntary_cert; HI was mislabeled license→voluntary_cert).
- **OPLR ground-truth harness.** Utah OPLR publishes per-profession periodic
  review reports (PDFs, oplr.utah.gov) stating each occupation's current model
  + recommendation. `docs/lit_review/oplr_ground_truth.csv` (9 professions) +
  `pipeline/eval/check_vs_oplr.py` compare Utah's current model to our UT
  extraction. nursing validates (license==license). Held-out test: 8 published
  professions (PA, PT, OT, respiratory, acupuncture, athletic training,
  hearing-instrument, SLP) extracted UT-only to check the prompt on data we
  never tuned on — all should read current law = license (hearing-instrument
  and SLP are the interesting cases: OPLR *recommends* a shift to mandatory
  cert, but current law is license).
- **Gap findings** (`gap_report.md`, `optometry_spot_check.md`): **Montana
  Title 37-1** is a cross-profession centralized-discipline gap (low/zero
  disciplinary grounds in dentistry, nursing, optometry, accountancy) — one
  per-state scope-manifest entry would fix 4+ professions. OK/PA/NC have
  deeper source-level gaps.

## Just shipped (May 29–31, 2026)

- **External lit review closed** (issue #17). Pulled Utah OPLR's own Dec
  2025 framework PDF, Obama 2015, CLEAR 2020, IJ License to Work 2nd ed,
  Archbridge SOLI, plus all 17 Knee OLLRP Excel files. Writeup in
  `docs/lit_review/README.md`; sources in `docs/lit_review/sources/`.
- **Confirmed our UORF ladder matches Utah OPLR's published framework**
  exactly — same 6 rungs (`market_forces` → `voluntary_certification` →
  `registration` → `exemption` → `mandatory_certification` → `license`),
  same low → high ordering. `standard_model.py:14`.
- **Schema + prompt changes** (`pipeline/extract/standard_model.py` +
  `pipeline/config/prompts.yaml`):
  - `credential_type → certification` now uses Obama 2015's "right-to-title"
    framing (anyone may do the work; only certificate holders may use the
    protected title).
  - New `LicensureRequirements.alternative_regulation` nested object with
    three Evidence-wrapped bools: `bonding_required`, `insurance_required`,
    `establishment_regulation_required`. Captures Obama's "alternatives to
    credentialing." Independent of `credential_type` — a state may license
    AND require bonding.
- **Existing 6 professions have `alternative_regulation: null`** until
  re-extracted. No UI surfacing yet (waiting on a profession that actually
  exercises the values).
- **Knee OLLRP found not to help us.** Spot-checked vs our optometry/UT
  record: same Title 58 citations, shallower schema (8 numeric vars vs our
  ~25 structured fields), stale (last data year = 2016). Files kept in
  `docs/lit_review/sources/knee/` for the record; no workflow built on them.

## Just shipped (May 20, 2026)

- **Compact membership as a universal column** — `build_frontend.py:_extract_compacts`
  pulls structured compact membership out of existing quote text via regex
  against known interstate licensure compact names. No new LLM. 34/47
  nursing states show NLC, 24/43 medicine show IMLC, dentistry/OH shows
  DDH-C. Data was already extracted weeks ago, just buried in the
  `profession_specific` discovered fields.
- **Profile table swapped from shadcn Table to AG Grid Community.**
  `ag-grid-react` + `ag-grid-community`, themeQuartz with tailwind-matched
  params. Per-column filter popovers via column-header click — the
  pull_usaspending interaction pattern. Custom `MulticheckFilter` React
  component for low-cardinality columns (the Enterprise Set Filter
  workalike, ~120 lines). Filter type is **auto-inferred per column** by
  scanning unique values across rows: ≤25 distinct → multicheck, else
  text/number. Chip bar above the table shows every active filter with ×
  to remove. Header min-widths computed from label length so labels
  never wrap or truncate.
- **All ~25 universal modal fields + every per-profession discovered field
  now registered as toggleable columns.** Default-hidden for non-default
  ones; users opt in via the "Columns ▾" dropdown. Custom popover (not
  Base UI's DropdownMenu — that crashed twice in earlier iterations).
- **State-detail switched from Dialog to shadcn Sheet.** Slide-in side
  panel from the right; table stays visible behind it. The panel's role
  shifted from "all data for this row" (duplicates the table) to
  "evidence drilldown" — verbatim statute quote + citation + "in context"
  highlight per claim. `state-detail-dialog.tsx` still exports
  `StateDetailDialog` for back-compat.
- **Universal-field labels match Atharv's cross-comparison vocabulary.**
  "Issuing authority" → "Licensing Authority", "Regulatory model" →
  "Regulation (UORF)", etc. No schema rename — display layer only, so
  the structured richness of `regulatory_authority` (name + type +
  umbrella_agency) isn't lost.
- **Credential type column hidden by default.** For the common
  `license × mandatory` case it duplicates Regulation (UORF). Users opt
  in via Columns ▾ to see the orthogonal decomposition. Cell renderer
  no longer shows the redundant "MANDATORY" annotation under "license"
  or "registration" — only "certification" actually has a meaningful
  mandatory/voluntary split.
- **Vercel npm install fixed** via `pipeline/publish/web/.npmrc` with
  `legacy-peer-deps=true`. `react-simple-maps@3.0.0`'s peer-dep range
  (`^16.8.0 || 17.x || 18.x`) conflicts with React 19; without the
  override `npm install` exits 1 on Vercel and the build dies before
  it ever reaches our code.

Also: a session-prep doc + artifacts live under `/tmp/` from this
morning's Atharv check-in — `may20_response.md`, `compact_membership.{md,csv}`,
`peer_sparseness.md`, `their_table_filled.md`. Useful for replaying the
"is the data already there?" story.

## Verification work — May 20 afternoon (#3 closed)

- **97.8% → 99.94% verified across all six professions** (204 unverified
  → 5 of 9,089 Evidence nodes). The residual 5 are real LLM
  stitching / paraphrase — Sonnet itself returns `null` on 3 of them.
- **`clean_text.py`**: now `html.unescape`s section text before the
  source-specific cleaners. KY and ND were the only states with raw
  `&quot;` / `&#039;` surviving from Justia; cleared 86 unverified
  flags. One-off migration applied the same decode to existing
  trimmed/clean/umbrella caches.
- **`clean_text.py`**: also strips `Page No. N` lines from chapter-blob
  renders (ND-only at the moment). Cleared 2 more.
- **`pipeline/extract/repair_unverified.py`** (new): for any Evidence
  still flagged, sends the cited section text + claim to the LLM and
  asks for a verbatim quote. Validates with `quote_in_corpus` before
  mutating. Haiku-then-Sonnet pass cleared 111 more. Total cost ~$0.75.
- **`locate_quote.py`**: tested bare-form line-start list-marker
  stripping (would fix ~26 quotes); rolled back — asymmetric with how
  the LLM inlines markers, broke ~74 currently-verified quotes. Left
  a comment explaining why.
- **`pipeline/_llm.py:call_structured`** now the single LLM-call
  helper. extract_state, trim_state, discover_schema, recategorize_fields,
  + 3 dead `_extract_json` copies in `discover/` all routed through it.
- **`pipeline/extract/standard_model.py:iter_evidence`** now the single
  Evidence-tree walker. 7 callsites consolidated (annotate_evidence,
  reverify_evidence._walk, repair_unverified, build_frontend ×3,
  build_review_csv).
- **`web`**: Evidence column renamed to **Unverified**. Cell blank when
  count is 0 so the few flagged rows stand out; row gets an amber
  left-border + soft amber fill via `.ag-row-unverified`. Header drops
  the verified-% stat; only shows `unverified quotes: N` when N > 0.

## Next — open priorities

### 0. UORF rung sort key (new, from issue #17 follow-up)

AG Grid "Regulation (UORF)" column currently sorts the rung names
alphabetically — backwards relative to Utah's least → most restrictive
ordering. Add an internal 0–5 ordinal derived from `regulatory_model`,
used as the column's sort comparator only. Never displayed (Utah's
framework is categorical and explicitly non-mechanistic).

### 1. Default-column tuning (still open from May 20)

The Columns ▾ dropdown exposes ~50-60 columns per profession (universal
+ per-profession discovered). Today the default-visible set is the 11
hand-picked columns from the pre-AG-Grid version. Worth a deliberate
pass picking the ~12-15 most informative defaults per profession,
possibly with a "compact view" / "expanded view" toggle.

Implementation note: each `ColDef` in `buildColumnDefs` has
`hide: true | false`. Currently most new universal + all discovered
columns are `hide: true`. Just flip the ones that should be defaults.
Could also persist user choice to URL state for shareable views.

## Earlier next-up items (still open, lower priority)

- Field-list one-pager (printable HTML or markdown enumerating all
  fields per profession — somewhat superseded by the Columns ▾
  dropdown but still useful as a static appendix)
- Regulations pipeline (Cornell LII) — admin code, not statute. Needed
  to answer "is there more info in regs than in statutes?"
- Utah-office comparison — blocked on them sending working data

## Reference

- Live site: https://utah-licensing.vercel.app (pw `utah`)
- Blob: `tf7defwrsanhzl3r.public.blob.vercel-storage.com/data/<profession>.json`
- Pipeline shape: [ARCHITECTURE.md](ARCHITECTURE.md)
- Reference repo: `/Users/abigailhaddad/Documents/repos/newyork`
- Entrypoints:
  - extract: `python -m pipeline.extract.extract_state --profession <p>`
  - re-verify quotes: `python -m pipeline.extract.reverify_evidence --profession <p>`
  - pull umbrella text: `python -m pipeline.ingest.pull_umbrella_text [--state XX]`
  - publish data only: `python -m pipeline.publish.build_frontend --profession <p>`
  - deploy web app: `cd pipeline/publish/web && npx vercel deploy --prod --yes`
    (preview without `--prod`)
- Web stack (since May 20): Next.js 16 + AG Grid Community + shadcn/ui
  (Base UI primitives) + Tailwind 4. See memory `web_stack_notes.md`.
