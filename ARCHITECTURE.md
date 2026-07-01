# Architecture

How utah is laid out today, and where it's heading. Written so future-us (or
a new collaborator) doesn't have to re-derive the design.

## What this is

A pipeline that turns state-statute web pages (currently Justia) into a
structured, cross-state comparison of professional licensing rules. Built
for Utah OPLR / UORF to look across all 50 states for a given profession
and ask "who does this differently, and where's the verbatim authority for
each claim?"

Inputs: Justia URLs.
Outputs: one `public/data/<profession>.json` per profession, served on a
gated Next.js site (https://utah-licensing.vercel.app, pw `utah`).

Every leaf value in the output is an `Evidence` carrier: `{ value, quote,
citation, [unverified], [quote_spans] }`. The verbatim quote is regex-
checked against the source corpus; offsets back into the source text
are pre-computed so the UI can paint a yellow highlight without re-deriving
the matcher.

## Pipeline stages

There are four conceptual stages. Each writes its outputs to a fresh
directory under `pipeline/results/` and is independently re-runnable.

```
discover ── ingest ── extract ── publish
   │           │         │          │
   │           │         │          └─ public/data/<profession>.json
   │           │         └─ structured/<profession>/<STATE>.json
   │           └─ text/<profession>/<STATE>.json
   │             umbrella_text/<STATE>.json
   └─ hierarchy/<STATE>.json
     licensing_titles/<STATE>.json
     umbrella_chapters/<STATE>.json
     profession_index/<profession>.json
     discovered/<profession>.json (schema)
```

### 1. discover (`pipeline/discover/`)

Figures out the *map* — what to fetch — without fetching content yet.

- `build_hierarchy.py` — for each state, lists the chapters under each
  licensing title.
- `match_profession.py` / `expand_hierarchy.py` — picks the practice-act
  chapter for a given (state, profession).
- `discover_schema.py` (in `extract/` but logically discovery) — examines
  one canonical state for a profession and proposes profession-specific
  fields beyond the universal schema.

### 2. ingest (`pipeline/ingest/`)

Fetches the actual section bodies. Self-rate-limited (`PER_HOST_DELAY=0.3s`).

- `pull_text.py` — per-profession practice-act sections.
- `pull_umbrella_text.py` — umbrella chapter section bodies. Capped at
  50 sections per chapter (the top-of-chapter "definitions / applies to /
  board" sections are what we care about, not the entire admin code).

### 3. extract (`pipeline/extract/`)

LLM call per (state, profession). Outputs typed JSON.

- `standard_model.py` — universal schema every profession has
  (licensure, scope, etc.).
- `discover_schema.py` writes per-profession field discoveries to
  `results/discovered/<profession>.json`.
- `extract_state.py` builds a Pydantic model composing universal +
  discovered fields, prompts the LLM with practice-act + umbrella context,
  and validates the response. Then walks the result and sets
  `unverified: true` on any Evidence whose quote can't be found in the
  combined corpus.
- `reverify_evidence.py` — re-runs the verifier against existing structured
  records without re-paying for LLM extraction. Use this when the matcher
  changes, or when umbrella content lands and you want to widen the
  acceptable corpus.
- `locate_quote.py` — the single matcher. `normalize_with_mapping` (port
  of the old TS code), `locate_quote_in_section` (returns char-offset
  spans into the original text), `quote_in_corpus` (bool fallback against
  combined corpus). One source of truth; no Python-vs-TS parity issue.

### 4. publish (`pipeline/publish/`)

- `build_frontend.py` — assembles `data/<profession>.json` for the site.
  Hoists table columns from universal fields, embeds the full structured
  record under `_full` for the modal, attaches per-state section text
  (chapter + umbrella, the latter concatenated under one
  `UMBRELLA / <chapter>` citation), and **computes `quote_spans` against
  the exact section text it's about to publish** (avoids drift between
  what the verifier saw and what the UI slices).
- Uploads to Vercel Blob. `--deploy` then runs `vercel --prod`.

## Where state lives

Each scattered file under `results/` is the **write-once output of one
discovery or pipeline step**. Read-only thereafter.

| Path | Owned by | Shape |
|---|---|---|
| `hierarchy/<STATE>.json` | `build_hierarchy.py` | titles → chapters |
| `licensing_titles/<STATE>.json` | `find_licensing_titles.py` | which titles are licensing |
| `umbrella_chapters/<STATE>.json` | `find_umbrella_chapters.py` | which chapters are cross-cutting + their slugs |
| `profession_index/<profession>.json` | `match_profession.py` | which chapter is the practice act for each state |
| `discovered/<profession>.json` | `discover_schema.py` | per-profession schema |
| `text/<profession>/<STATE>.json` | `pull_text.py` | practice-act section bodies |
| `umbrella_text/<STATE>.json` | `pull_umbrella_text.py` | umbrella section bodies |
| `trimmed/<profession>/<STATE>.json` | trim step | text with non-relevant sections removed |
| `structured/<profession>/<STATE>.json` | `extract_state.py` | the LLM-extracted record |

Nothing joins these today. Consumers (`extract_state`, `build_frontend`)
do per-file lookups by state / profession. Tolerable at current scale;
will hurt once we add cross-cutting queries.

## The umbrella problem

Many states have multiple "general provisions" chapters that apply to
different *subsets* of professions:

- **UT** — Title 58 Ch 1 (DOPL Act) is universal across all DOPL pros.
  Easy.
- **FL** — Ch 455 is universal for DBPR; Ch 456 is health-only.
  Tiered.
- **CO, HI, AR, MS, TN** — similar tiered pattern.

Today, `extract_state.load_umbrella_text` injects **every** umbrella chapter
we discovered into **every** profession's LLM prompt for that state. Noise,
not corruption — Sonnet at temp 0 ignores irrelevant context — but it
inflates tokens and weakens any future audit.

The fix (not yet built): per-chapter scope tagging. At discovery time, one
LLM call per umbrella chapter emits `{scope: "universal" | "health" |
"construction" | "specific:[...]", evidence_quote: "..."}`. Stored as a flat
field on the existing `umbrella_chapters/<STATE>.json` record. At extract
time, `load_umbrella_text` filters chapters to those whose scope matches
the current profession's family. Auditable in one file per state.

Information the LLM needs for this to work and doesn't have today:
1. **Parent title name** (one cheap fetch of the title-level URL).
   "Ch 456 — Health Professions" + "Title XXXII — Regulation of Professions
   and Occupations" is far more informative than just the chapter label.
2. **First-section text** — chapters almost always open with definitions
   or an "applies to" statement.
3. **Profession-family tag** — health / financial / construction / etc. —
   on the practice-act side, so the filter has both sides of the match.

## Frontend

Next.js 16 (Turbopack) under `pipeline/publish/web/`. Reads
`data/<profession>.json` from Vercel Blob at request time.

- `lib/types.ts` mirrors what `build_frontend.py` emits.
- `lib/format.ts` — `humanize`, `highlightSpans` (slices text by span
  offsets the Python side computed), `citationUrlWithFragment` (builds
  Justia deep-links with `#:~:text=...` so clicking lands on the actual
  quoted clause in browsers that support text fragments).
- `components/evidence-row.tsx` — renders an evidence row in the modal,
  with badges, source link, and the "in context" expander.

There is **no TS-side quote matcher**. That code used to exist; it's been
replaced by Python emitting offsets the TS just slices. If you find
yourself writing a TS regex against quote text, you're recreating the
parity problem.

## Design principles

1. **Each pipeline stage writes one canonical output.** Re-runnable, idempotent.
   Don't mutate prior stages' outputs.
2. **Single source of truth for any cross-cutting fact.** Quote matching
   lives in Python; the frontend slices. Don't re-derive the same answer
   on two sides.
3. **Shape new derived facts like future Postgres columns.** Flat fields,
   not nested sub-objects. Booleans for binary classifications. String
   enums for small closed sets. If you can't picture the SQL column,
   refactor.
4. **Verifier and highlight matcher share code.** `pipeline/extract/locate_quote.py`
   is the lone matcher. Both `extract_state` (bool) and `build_frontend`
   (spans) call into it.
5. **Don't pay LLM cost twice.** `reverify_evidence` lets you re-check
   quotes against a changed corpus without re-extracting. Use it before
   spending money on re-extraction.

## Future: Postgres

We will eventually want this in a relational store, modeled on the
`/Users/abigailhaddad/Documents/repos/newyork` schema:

- **One `documents` table** keyed on `(state, hierarchy_level, citation)`,
  self-referential via `parent_id`, with a materialized `hierarchy_path`
  and `hierarchy_level ∈ {title, chapter, section}`.
- **Classification columns** as we add them: `is_umbrella`, `is_practice_act`,
  `scope_keyword`, `profession_family`.
- **Join tables** for many-to-many: `practice_acts (profession, document_id)`,
  `umbrella_applies_to (umbrella_id, profession_family)`.
- **Per-state metadata** flattened into typed columns (cf. newyork's
  `nycrr_*` / `njac_*` / `njsa_*` columns) so URL-back-references are
  cheap. For Justia + state statutes this is roughly `justia_title`,
  `justia_chapter`, `justia_section`, with the matching `_name` fields.
- **Precomputed stats** like `descendant_count` for performance — same
  pattern newyork uses.
- **Drizzle schema + numbered SQL migrations** under
  `frontend/packages/database/migrations/0NNN_*.sql`, run in lex order
  on a fresh DB. Use a/b/c suffixes for same-number ordering.
- **Neon** for hosting.

Today's scattered JSON maps almost 1:1 to that schema. As long as new
fields land in the existing per-state files as flat columns, the
eventual migration is a `for row in json: INSERT` loop.

When to actually do it: when we have a second consumer of the
hierarchy data (analytics, cross-state querying, an embedded admin UI),
or when the per-file lookups in `extract_state` / `build_frontend`
start to feel painful. Today they're tolerable.

## Pointers

- Live: https://utah-licensing.vercel.app (pw `utah`)
- Blob: `tf7defwrsanhzl3r.public.blob.vercel-storage.com/data/<profession>.json`
- Repo: `/Users/abigailhaddad/Documents/repos/utah`
- Reference architecture: `/Users/abigailhaddad/Documents/repos/newyork`
  (DATABASE_SETUP.md, frontend/packages/database/migrations/)
- Status / next steps: STATUS.md
