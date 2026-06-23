# Trades via official state sources — continuation plan (2026-06-23)

> ## ⏯ RESUME HERE (post-/clear handoff — read this first)
> **Big shift this session: Justia is pullable again via CDP-attach to a real
> Chrome (see [[project_official_source_migration]] memory). CDP-Justia is now the
> DEFAULT source — we no longer build bespoke official-source handlers.**
>
> **Background CDP crawl is (or was) RUNNING** — detached, survives /clear, writes
> to `pipeline/results/text/`. It pulls the 28 clean-chapter Justia states at a
> polite pace. Output log: `…/tasks/b472w3l75.output` (check `results/text/` dirs
> for actual progress; that path may be stale in a new session).
> - electrician: AL,AR,CO,GA,HI,IA,KY,MA,ND,NH,TX
> - plumbing: AL,AR,CO,GA,HI,IA,IN,KY,ND,NH,OR,SC,TX
> - hvac: AL,AR,DE,TX
>
> **To resume / run a CDP Justia pull:** user keeps a debug Chrome open —
> `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/chrome-justia-debug"`
> (visit a Justia page once, solve the challenge). Then:
> `JUSTIA_CDP_URL=http://localhost:9222 PULL_HOST_DELAY=7 pipeline/.venv/bin/python -m pipeline.ingest.pull_text --profession <P> --states <…> --force`
> ONE pull process at a time (one browser); never fire side commands at the same
> Chrome (extra tabs → reload chaos). It self-heals cf_clearance expiry: pauses
> ≤6 min for a re-solve, then resumes.
>
> **PENDING (in priority order):**
> 1. Let the crawl finish; **re-audit** all trade text (`blank-cite`, THIN<=2
>    sections = flat-title casualty, chrome-leak). Last audit: only LA+NJ
>    construction_trades flagged → already removed.
> 2. **Flat-title trio OK/LA/NJ** — flat on Justia itself (title-59 / title-37 /
>    title-45, 2000+ sections, no chapter). A whole-title pull is a RUNAWAY. Scope
>    each trade to a section range (`section_slug_pattern` on the title, AZ-podiatry
>    style) then pull via CDP. Hints from stray matches: elec OK§1698 plumb OK§1013
>    hvac OK§1850.8; LA plumb RS37:1361-1380 hvac RS37:1864/1973; NJ contractor 45:5AAA.
> 3. **clean → trim → extract** the whole new batch (batch API; ~$1-2), consistency
>    check (`pipeline.eval.check_consistency`), then commit.
>
> **Two extract batches were STUCK in_progress on Anthropic's side** (Medium tier +
> GA/SC/WV) — poll to write results when they land:
> `pipeline.extract.extract_state_batch poll msgbatch_01BvDXkRrEkHVUWaZt3MGsng`
> and `… msgbatch_01DqgHmD9adpmRtm5DG2s9Ko`.
>
> **Scope notes:** IL construction_trades = Petroleum Equipment Contractors
> (225 ILCS 729) — narrow, review. AZ hvac match (title-3/§3-727) is spurious — skip.

Self-contained handoff. Goal: pull **all four building trades** (construction_trades,
electrician, plumbing, hvac) for **as many states as possible**. Primary source is
now **Justia via CDP-attach** (universal); official state-legislature handlers
(below) are kept for states already done but no longer the default.

Branch: **`data/pull-all`** (off main). Commit when each state lands.

## Why we're doing it this way (settled facts — don't re-litigate)
- **Justia blocks AUTOMATED browsers** (curl_cffi, headless/headful/patchright
  launched Chromium — even slow + jittered from a clean home IP) with a
  Cloudflare challenge. The wall is **automation-fingerprint detection on the
  page**, NOT IP reputation or rate — so politeness/clean-IP alone does not help.
- **BUT Justia IS pullable via CDP-attach to the user's REAL Chrome** (2026-06-23
  breakthrough). Connect out-of-process to a Chrome the user starts with
  `--remote-debugging-port`; there's no in-page automation fingerprint, so the
  challenge clears. Set `JUSTIA_CDP_URL=http://localhost:9222` + `PULL_HOST_DELAY=7`
  and pull_text routes `law.justia.com` through it. The user solves the first
  challenge by hand; `cf_clearance` persists; on expiry the crawl PAUSES (≤6 min)
  for a re-solve then resumes. This makes the "JS-only" states (GA/NJ/TX/MA)
  reachable too — no SPA handlers needed. See [[project_official_source_migration]]
  for the full how-to. Committed corpora stay as-is; CDP is for NEW pulls.
- **Official state sites are also a path** — most serve plain HTML/JSON, no
  Cloudflare — and need no open browser, so they're preferred for chapter-
  structured states. CDP-Justia is the universal fallback for the rest.
- **Flat-title caveat:** OK (title-59), LA (title-37), NJ (title-45) are giant
  flat "Professions" titles — a whole-title CDP pull is a 2000+ section RUNAWAY.
  Scope each trade to a section range (AZ-podiatry `section_slug_pattern` style).
- Paid unblocker (ScraperAPI premium, ~$10) is wired in `fetch()` as the
  zero-manual-effort fallback. NY OpenLeg key is in `.env` (`NY_OPENLEG_KEY`).

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
`ny_openleg` (NY, API), `ct_official` (CT), `wa_official` (WA), `va_official` (VA),
`me_official`/`id_official`/`mo` (per-section-via-TOC: `pull_via_toc` core +
per-state body extractor), `md_official` (GetNext API walk, `pull_md`).

Trade coverage so far (all official sources):
- construction_trades: UT, NV, PA, CT, VA
- electrician: UT, SD, CT, WA, ME, ID, MD
- plumbing: UT, SD, CT, WA, ME, ID, MO, MD
- hvac: UT, CT, ID, MD

## NEXT STEP — the "Medium (nested/special)" cluster (RI/MT/AZ/FL/VT)
The per-section-via-TOC handler is BUILT and ME/ID/MO/MD are DONE (commit
"ME/ID/MO/MD per-section handlers …"). Reuse `pull_via_toc` for the per-section
shapes below; FL is whole-chapter; MD's GetNext walker (`pull_md`) is the model
for any other no-TOC API state. Gotchas learned: MO needed a per-PROFESSION url
(not a state template) so its dietetics section_slug_pattern stayed on Justia;
MD's GetNext content-negotiates (parse both bare-JSON and `<string>`-wrapped);
ID's section body is the `span.f11s` that OPENS with the section number (earlier
f11s spans are TITLE/CHAPTER headers).

### Done — per-section-via-TOC (ME/ID/MO) + GetNext (MD)
- **ME** (legislature.maine.gov): TOC `…/statutes/{T}/title{T}ch{N}sec0.html`,
  links `title{T}sec(\d+)\.html`, body `div.row.section-content`. electrician=T32
  Ch17, plumbing=T32 Ch49. (ME plumbing Ch49 is mostly REPEALED — clean drops them.)
- **ID** (legislature.idaho.gov): TOC `…/idstat/Title{T}/T{T}CH{N}/`, links
  `SECT({T}-[0-9]+[A-D]?)`, body = f11s opening with the section number. electrician=
  T54 Ch10, plumbing=Ch26, hvac=Ch50.
- **MO** (revisor.mo.gov): TOC `…/OneChapter.aspx?chapter={N}`, links anchored
  `PageSelect\.aspx\?section=({N}\.[0-9]+)`, body `div.norm`. plumbing=Ch 341.
- **MD** (mgaleg.maryland.gov): GetNext walk from `{title}-101`; article slug→code
  map (business-occupations-and-professions=`gbo`, business-regulation=`gbr`);
  body `div#StatuteText`. electrician=gbo T6, plumbing=gbo T12, hvac=gbr T9A.

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
NOTE: this list predates CDP-Justia and is now mostly OBSOLETE — CDP pulled
AK, AL, AR, CO, GA, HI, IA, IL, KY, MA, ND, SC (and more) cleanly. What actually
remains hard: MS, TN (LexisNexis cookie-wall) and any genuinely opaque/TOC-only
state CDP-Justia can't reach. Re-confirm a state is hard before treating it as
skip; use the paid unblocker only if CDP-Justia truly fails.

## KY is NOT PDF-backed — false alarm, KY is fully usable (resolved 2026-06-23)
The `section-227-160` page that *looked* PDF-only is a **"Repealed, 1954" stub**
with no body — just a catchline + history. Live KY sections (e.g. 227.200) carry
the **full statute text in the HTML**, after the "Download as PDF" button (which
Justia stamps on every page, repealed or not). The CDP crawl pulled KY electrician
fine: 127 sections, 97 kept after clean (30 repealed stubs dropped), real bodies.
**No PDF extractor is needed.** KY is a normal Justia state; treat other "PDF"
states in the skip list with the same skepticism before writing PDF code.

**Real issue the KY sample surfaced + FIXED:** Justia stamps per-section furniture
("Download as PDF", a "Universal Citation: / <ST> Code § X (YYYY)" block, and the
AALL "media-neutral citation…official citation." blurb) that was leaking into clean
text across *all* Justia states. Added strippers to `clean_text.clean_justia`
(JUSTIA_UNIVERSAL_CITATION, JUSTIA_MEDIA_NEUTRAL_BLURB, "Download as PDF" lonely
line, broadened the year-breadcrumb line to "…Statutes"). Verified surgical on
committed SC/WV (0 sections dropped; only the boilerplate lines removed). This
improves every Justia-sourced corpus on the next clean; published professions get
it whenever they're next refreshed (don't re-clean them in a trades session).

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
