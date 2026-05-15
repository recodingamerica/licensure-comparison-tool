# Status

Live site: https://utah-licensing.vercel.app (pw `utah`).
Pipeline shape and Postgres direction: see [ARCHITECTURE.md](ARCHITECTURE.md).

## Just shipped

- **Quote-highlight parity** — replaced the two-matcher setup with a single
  Python matcher (`pipeline/extract/locate_quote.py`) that emits character
  offsets onto each Evidence node. Frontend just slices the rendered
  section text. No TS-side regex; no parity drift. 174 Python tests pass.
- **Deep-link to the actual quoted clause** — citation links in the modal
  now use URL Text Fragments (`#:~:text=...`), so clicking lands on the
  quoted paragraph on Justia in Chrome / Edge / Safari. Falls back to the
  bare section page in Firefox.
- **Umbrella text fetch in progress** — pulling cross-cutting "general
  provisions" chapters for 23 missing states, including UT itself. When
  finished, re-running `reverify_evidence` + `build_frontend` should pick
  up the widened corpus and add `quote_spans` for previously-unhighlighted
  umbrella-resident quotes. No LLM cost. No re-extraction yet.

## Next

### 1. Umbrella scope-tagging *(explicit next once the pull finishes)*

Problem: today `extract_state.load_umbrella_text` injects **every**
umbrella chapter into **every** profession's LLM prompt for that state.
For UT (1 universal chapter) that's fine; for FL/CO/HI/AR/TN (tiered:
universal + health-only + sometimes others) it's noise. Sonnet ignores
it but auditability suffers and tokens inflate.

Plan:

1. Augment each `umbrella_chapters/<STATE>.json` chapter entry with:
   - `parent_title_label` (one cheap fetch of the title-level URL)
   - `first_section_text` (one extra section fetch — chapters open with
     definitions / "applies to")
2. One LLM call per umbrella chapter (~200 calls total) emits
   `{scope: "universal" | "health" | "construction" | "specific:[...]",
   evidence_quote: "..."}`. Store as flat fields on the same record.
3. Tag each profession in `config/professions.yaml` with `family` (health
   / financial / construction / etc.).
4. `load_umbrella_text` filters chapters by `scope` ∩ `profession.family`.

Shape note: store these as flat fields per [ARCHITECTURE.md design
principle #3](ARCHITECTURE.md#design-principles) so the eventual Postgres
migration is a 1:1 column mapping.

Effort: ~half-day. No re-extraction needed afterward unless we want the
LLM to *use* the now-filtered umbrella context (which we'd do for UT only,
~$2 in API spend).

### 2. Field-list one-pager

A printable HTML page (or markdown) enumerating universal fields (from
`standard_model.py`) + profession-specific discovered fields (from
`discovered/<profession>.json`) for the appendix. Source data is already
sitting there.

### 3. Regulations pipeline (Cornell LII)

We don't pull regulations today — only statutes. Needed to answer "is
there more info in regs than in statutes?" Real work — a new
discover/ingest pair mirroring the Justia path. Scope to one profession
+ one state first.

### 4. Utah-office comparison

Blocked on them sending us their working data. When it lands, a
side-by-side of our extracted record vs. their spreadsheet for one or
two professions.

## Future direction

A relational store modeled on `/Users/abigailhaddad/Documents/repos/newyork`
(single `documents` table, `parent_id` self-FK, classification columns
added incrementally, Drizzle + numbered SQL migrations, Neon Postgres).
Not urgent — see [ARCHITECTURE.md § Future: Postgres](ARCHITECTURE.md#future-postgres)
for the mapping from today's scattered JSON to that schema.

## Reference

- Live site: https://utah-licensing.vercel.app (pw `utah`)
- Blob: `tf7defwrsanhzl3r.public.blob.vercel-storage.com/data/<profession>.json`
- Pipeline shape: [ARCHITECTURE.md](ARCHITECTURE.md)
- Reference repo: `/Users/abigailhaddad/Documents/repos/newyork`
- Entrypoints:
  - extract: `python -m pipeline.extract.extract_state --profession <p>`
  - re-verify quotes: `python -m pipeline.extract.reverify_evidence --profession <p>`
  - pull umbrella text: `python -m pipeline.ingest.pull_umbrella_text [--state XX]`
  - publish: `python -m pipeline.publish.build_frontend --profession <p>` (add `--deploy` to push prod)
