# Trades via official state sources — continuation plan (2026-06-23)

Self-contained handoff. Goal: pull **all four building trades** (construction_trades,
electrician, plumbing, hvac) for **as many states as possible** from **official
state legislature sites** — NOT Justia (Cloudflare-blocks all our IPs).

Branch: **`data/pull-all`** (off main). Commit when each state lands.

## Why we're doing it this way (settled facts — don't re-litigate)
- **Justia hard-blocks every IP we have** (local + GitHub Actions + IPRoyal
  residential) with a Cloudflare "Just a moment" JS challenge. curl_cffi, headless
  + headful + patchright browsers, and free scraping-API trials all fail. A real
  headful browser + residential IP passed ONCE, then Cloudflare flagged repeated
  hits — unreliable for bulk. **Do not pull Justia.** Committed Justia corpora
  (7 published professions × 50 states) stay as-is.
- **Official state sites are the path** — most serve plain HTML/JSON, no Cloudflare.
- Paid unblocker (Bright Data / ScraperAPI premium, ~$10 for trades) is wired in
  `fetch()` but the user opted not to spend. Residential proxy (IPRoyal,
  `RESIDENTIAL_PROXY` in `.env`) works for non-Cloudflare JS-only sites via
  Playwright. NY OpenLeg key is in `.env` (`NY_OPENLEG_KEY`).

## Architecture (how a state gets added)
The Justia hierarchy still provides the profession→chapter MAP. We translate that
chapter to the state's official URL and fetch from there.

1. **`pipeline/config/state_structure.yaml`** — add a state block:
   - `source: <name>` + `chapter_url_template: "...{title}/{chapter}..."`.
   - `match_profession._official_url()` fills placeholders from the Justia path:
     `{title}/{chapter}/{section}` (zero-pad stripped, letter-suffix UPPER),
     `{x_lc}` (lower suffix, e.g. CT 393b), `{x_dot}` (hyphen→dot, e.g. WA 19.28,
     VA 54.1). Python format specs work too: `{chapter:0>3}` zero-pads.
2. **`pipeline/ingest/pull_text.py`** — add `is_<state>_url()` + a parser, and a
   dispatch branch in `pull_state()` (mirror the CT/WA/VA branches). Use
   `fetch()` for utf-8, `fetch_bytes()` (latin1, retries verify=False on SSL) for
   Word-export sites.
3. **`pipeline/ingest/clean_text.py`** — usually nothing (generic cleaner). Add a
   `SOURCE_CLEANERS` host entry only if the source needs special chrome-stripping.
4. Re-match + run the pipeline per (profession, state).

### Per-(profession,state) commands
```
P=electrician; S=WA
pipeline/.venv/bin/python -m pipeline.discover.match_profession --profession $P   # once per profession after config change
pipeline/.venv/bin/python -m pipeline.ingest.pull_text   --profession $P --states $S --force
pipeline/.venv/bin/python -m pipeline.ingest.clean_text  --profession $P            # cleans all states; check [$S]
pipeline/.venv/bin/python -m pipeline.ingest.trim_state  --profession $P --states $S
pipeline/.venv/bin/python -m pipeline.extract.extract_state --profession $P --states $S --force
```
New professions also need a schema first: `python -m pipeline.extract.discover_schema --profession $P`
(already done for the 4 trades).

## Done (handlers built + committed)
`utah_le` (UT, XML), `sd_api` (SD, JSON), `nv` (NV, whole-chapter HTML),
`ny_openleg` (NY, API), `ct_official` (CT), `wa_official` (WA), `va_official` (VA).

Trade coverage so far (all official sources):
- construction_trades: UT, NV, PA, CT, VA
- electrician: UT, SD, CT, WA
- plumbing: UT, SD, CT, WA
- hvac: UT, CT

## NEXT STEP — build the per-section-via-TOC handler
Most remaining states are "per-section": fetch a chapter TOC, extract the section
list, fetch each section. Build ONE general mechanism (config: toc_url_template,
section_link_regex, section_url_template) OR per-state handlers. Specs (all TESTED
by subagents, plain GET + browser UA, no JS unless noted):

### Per-section (easy-ish) — do these next
- **ME** (legislature.maine.gov, UTF-8): TOC `…/statutes/{T}/title{T}ch{N}sec0.html`,
  section links via regex `title{T}sec(\d+)\.html`; section URL
  `…/statutes/{T}/title{T}sec{n}.html`; body in `div.row.section-content`.
  electrician=Title 32 Ch 17, plumbing=Title 32 Ch 49.
- **ID** (legislature.idaho.gov, UTF-8): TOC `…/idstat/Title{T}/T{T}CH{N}/` (trailing
  slash), links regex `SECT{T}-[0-9]+[A-D]?`; section URL `…/T{T}CH{N}/SECT{T}-{n}/`;
  body in `span.f11s`. electrician=T54 Ch10, plumbing=Ch26, hvac=Ch50.
- **MO** (revisor.mo.gov, UTF-8, strip script/style): TOC
  `…/main/OneChapter.aspx?chapter={N}`, links regex `PageSelect\.aspx\?section=([0-9]+\.[0-9]+)`;
  section URL `…/main/OneSection.aspx?section={N.NNN}`. plumbing=Ch 341.
- **MD** (mgaleg.maryland.gov, UTF-8, strip scripts): no TOC page — walk the
  GetNext API: `GET /mgawebsite/api/Laws/GetNext?articleCode={code}&sectionCode={sec}&enactments=False`
  returns next section code; start at `{title}-101`, follow until empty. Section URL
  `…/Laws/StatuteText?article={code}&section={N}&enactments=false&archived=false`.
  electrician=article `gbo` Title 6, plumbing=`gbo` Title 12, hvac=`gbr` Title 9A.

### Medium (nested / special)
- **RI** (webserver.rilegislature.gov, **UTF-8 not latin1**): TOC
  `…/Statutes/TITLE{t}/{chap}/INDEX.HTM`, links regex `href="({chap}-[0-9.]+\.htm)"`
  (sections can be decimal, e.g. 5-65-7.1); section URL `…/TITLE{t}/{chap}/{sec}.HTM`.
  contractor=5-65, electrician=5-6, plumbing=5-20.
- **MT** (leg.mt.gov, UTF-8, strip scripts): PARTS layer —
  `…/bills/mca/title_{TTTT}/chapter_{CCCC}/parts_index.html` → `part_{PPPP}/sections_index.html`
  → `section_{SSSS}/{TTTT}-{CCCC}-{PPPP}-{SSSS}.html` (all 4-digit zero-pad; build
  URLs from index links, display number ≠ url number). electrician=Ch68, plumbing=Ch69.
- **AZ** (azleg.gov, UTF-8): title TOC `…/arsDetail/?title=32`; slice HTML from
  `id="chapter{N}"` to `id="chapter{N+1}"`, regex `ars/32/(\d+)\.htm`; section URL
  `…/ars/{T}/{NNNNN}.htm` (5-digit zero-pad on the post-hyphen number).
  Contractors = Title 32 **Chapter 10**, §§32-1101–32-1188. (AZ HVAC not separate.)
- **FL** (leg.state.fl.us, UTF-8): WHOLE-chapter, split on `<div class="Section">`
  (SectionNumber/Catchline/SectionBody spans; ignore the top index's SectionNumber
  spans). URL `…/index.cfm?App_mode=Display_Statute&URL={RANGE}/{CCCC}/{CCCC}.html`
  where CCCC=chapter zero-pad4, RANGE=`{lo:04d}-{hi:04d}`, lo=floor((chap-1)/100)*100,
  hi=lo+99 (489→0400-0499). contractor=Ch 489 (range math → needs a custom URL
  builder, not the plain template).
- **VT** (legislature.vermont.gov, UTF-8): per-section. Chapter page
  `…/statutes/chapter/{title}/{chap3}` is TOC-only; section links regex
  `statutes/section/{title}/{chap3}/(\d{5})`; section URL
  `…/statutes/section/{title}/{chap3}/{sec5}` (chap 3-digit, sec 5-digit zero-pad).
  contractor=Ch106, electrician=Ch15, plumbing=Ch39.

### JS-only (use IPRoyal proxy + headful Playwright — these AREN'T Cloudflare)
GA, MA, NJ, TX, WV — official sites are SPAs needing render. Investigate each
(undocumented JSON APIs often exist, e.g. Indiana's api.iga.in.gov). Trade chapters
exist for some; spec per-state before building.

### Hard / skip unless needed
AR, CO, HI, MS, TN (LexisNexis cookie-wall), and TOC-only/PDF/opaque states
(OR, WI, AK, AL, IA, ND, WY, OK, KY, LA, IL, NH, SC). Use the paid unblocker if
these become required.

## HVAC note
Only some states license HVAC separately (UT, CT, ID, MD have it). WA, AZ, VA fold
HVAC into general contractor registration — don't force a separate HVAC pull there.

## Gotchas
- Whole-chapter text splitters MUST anchor the section marker to THIS chapter's
  number AND to line-start (`(?m)^\s*`) or in-text cross-references create false/
  duplicate sections (bit us on WA/VA — fixed).
- After config change, re-run `match_profession` (per profession or all) before pull.
- `clean_text` count must equal `text` count or the corpus is stale (re-run clean).
- Revert test-pull artifacts for already-published professions (don't half-update).
