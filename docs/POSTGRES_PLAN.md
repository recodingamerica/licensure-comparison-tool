# Postgres + Search Plan

Draft. Concrete plan for moving Utah-licensing's structured data into Neon
Postgres so we can ship cross-state phrase search and unblock the
"second-consumer" use cases ARCHITECTURE.md warned us to expect.

## Sizing (measured, not guessed)

Counted across all 6 current professions on 2026-05-21:

| Table | Rows |
|---|---|
| `professions` | 6 |
| `state_profession_profile` | 277 |
| `evidence` | 9,343 |
| `sections` (per-profession trimmed + umbrella) | 24,455 |
| `discovered_fields` | ~150 |

Storage estimate (~150 MB) — the chosen scope stores BOTH the LLM-
extracted evidence AND the full trimmed statute text in `sections.text`
with a tsvector FTS index, so Atharv can search the raw statute language
directly (not just the excerpts we already extracted). Breakdown:

| Component | Size |
|---|---|
| `evidence` rows | ~7 MB |
| `evidence` quote FTS (GIN on tsvector) | ~10–15 MB |
| `sections.text` | ~50 MB |
| `sections` text FTS | ~80 MB |
| smaller tables + indexes | < 1 MB |

Neon free tier limits: 3 GB storage + 191 compute hours / month. We use
~5% of storage; search queries on 9 K and 24 K row tables with GIN
indexes are sub-millisecond, so compute is dominated by Vercel function
cold starts, not by Postgres. Free tier covers current scale and the
~2× growth from Atharv's next-occupations list (Pharmacy / Medical
Assistant / Surgical Technologist / Chiropractor / Radiologic
Technician).

## Goals

In priority order:

1. **Phrase / field search** across every extracted Evidence node (state,
   profession, field, quote, citation). Atharv's "direct phrase searching"
   ask from the May 20 PDF, replacing the AI-chatbot direction.
2. **Atharv-runnable SQL** for ad-hoc analyses. He wants "filters &
   drop-downs" but also raw-data access; SQL is the most flexible answer.
3. **Same data, two access paths.** The web app keeps reading the per-
   profession blob JSON for table rendering (fast page load, no DB round
   trips). The DB serves search + ad-hoc queries on top of the same data.
   We do NOT migrate the table view to DB queries — too much churn for
   no user gain. The blob JSON stays the canonical "for the web app"
   shape; the DB is the canonical "for search and analysis" shape.

## Non-goals

- Replacing the structured-record JSON in `pipeline/results/structured/`.
  Those stay as the source-of-truth artifact the pipeline produces.
- Real-time mutation. Reads-only from the app side. Re-ETL happens after
  each successful publish run; nothing writes to the DB through the web app.
- A general document store. We're indexing what we already extracted, not
  re-scraping into the DB.

## Where this lives

- Hosting: **Neon** (per ARCHITECTURE.md; Vercel-native integration).
- Schema source: SQL migration files under
  `pipeline/publish/db/migrations/0NNN_*.sql`, lex-sorted (mirrors the
  newyork convention).
- ORM in the web app: **Drizzle** under
  `pipeline/publish/web/src/db/schema.ts`. Type-safe queries from the
  Next.js API route that backs `/search`.
- ETL: new Python module `pipeline/publish/db/load.py` — reads
  `pipeline/results/structured/<prof>/<STATE>.json` files and upserts
  them into the DB. Idempotent; rerun-safe after every extract.

## Schema

Five tables. Smaller than newyork's because we don't need the
nycrr_*/njac_*/njsa_* per-state path columns — Justia gives us one URL
shape across all 50 states.

### `professions`

| col | type | notes |
|---|---|---|
| `id` | BIGSERIAL PK | |
| `key` | VARCHAR(64) UNIQUE | e.g. `podiatry`, `public_accountancy` |
| `display` | TEXT | "Podiatry", "Public Accountancy (CPA)" |
| `created_at` | TIMESTAMP | |

### `documents`

Replaces what was originally planned as a flat `sections` table. Modeled
on newyork's `regulatory_documents`: one row per regulatory entity at
ANY level (title, chapter, subchapter, article, part, section), linked
via `parent_id`, with a materialized `hierarchy_path` for fast tree
rendering.

| col | type | notes |
|---|---|---|
| `id` | BIGSERIAL PK | |
| `state` | CHAR(2) NOT NULL | |
| `parent_id` | BIGINT FK → documents(id), nullable | parent in the regulatory tree |
| `hierarchy_level` | VARCHAR(32) | enum: title / chapter / subchapter / article / part / section |
| `hierarchy_path` | TEXT | materialized, e.g. `/title-32/chapter-19/section-32-851` — for fast ancestor lookup |
| `url` | TEXT | Justia source URL (or other source) |
| `citation` | TEXT | normalized form (see `normalize_citation`); null for title rows |
| `label` | TEXT NOT NULL | as rendered, e.g. `§ 32-851 - Practicing podiatry without license` |
| `text` | TEXT | full body — populated only for section-level rows, NULL for titles/chapters |
| `text_tsv` | TSVECTOR | generated column for FTS over section text |
| `is_umbrella` | BOOLEAN DEFAULT FALSE | true when this is a cross-cutting umbrella chapter or its sections |
| `created_at` | TIMESTAMP | |

Indexes:
- `(state, hierarchy_level)` for "all titles in CA"-style queries
- `parent_id` for tree walks
- `hierarchy_path` (B-tree) — also useful for `LIKE '/title-32/%'` ancestor queries
- GIN on `text_tsv` for raw-statute phrase search

Notes:
- For "section_fallback" states (AZ etc., where Justia presents title-level
  flat section lists with no chapter in between), the chapter row may be
  synthesized OR the section's parent_id may point directly at the title.
  Pick one — synthesize for consistency, document in the ETL.
- Umbrella chapters appear as title/chapter rows with `is_umbrella=true`;
  their section descendants inherit the flag. They link to professions via
  the `umbrella_applies_to` join (below), not via parent_id.
- `evidence.section_id` foreign-keys to `documents(id)` and is expected to
  reference only rows where `hierarchy_level='section'`.

Storage note: ~50 MB raw section text + ~80 MB FTS index + ~5 MB for
the title/chapter rows and their indexes. Bulk of DB size; we accept it
because raw-statute search is in scope.

### `evidence`

One row per Evidence-shaped node in `structured/<prof>/<state>.json`.
Search runs against this table.

| col | type | notes |
|---|---|---|
| `id` | BIGSERIAL PK | |
| `state` | CHAR(2) | |
| `profession_id` | BIGINT FK → professions | |
| `section_id` | BIGINT FK → documents(id), nullable | only references rows where hierarchy_level='section' |
| `field_path` | TEXT | dotted: `licensure.issuing_authority`, `scope.definition_quote`, `profession_specific.opioid_prescribing_limits` |
| `value_text` | TEXT | string form of `value` (bool → "true"/"false", lists → comma-joined) |
| `value_jsonb` | JSONB | raw value for structured queries |
| `quote` | TEXT | verbatim statute text the LLM grounded against |
| `citation` | TEXT | normalized form |
| `unverified` | BOOLEAN | mirrors the structured-record flag |
| `quote_tsv` | TSVECTOR | generated column for FTS |
| `created_at` | TIMESTAMP | |

Indexes:
- `(state, profession_id, field_path)` for the table's drill-down lookups
- `unverified` for the "show me everything flagged" use case
- GIN on `quote_tsv` for phrase search

### `state_profession_profile`

One row per (state, profession) carrying the flat top-level facts.
Reproduces the published per-row shape so SQL queries don't have to
join-and-aggregate constantly.

| col | type | notes |
|---|---|---|
| `id` | BIGSERIAL PK | |
| `state` | CHAR(2) | |
| `profession_id` | BIGINT FK | |
| `coverage_gap` | BOOLEAN | |
| `license_required` | BOOLEAN | |
| `regulatory_model` | VARCHAR(64) | one of the 6-rung enum values |
| `credential_type` | VARCHAR(32) | |
| `is_mandatory` | BOOLEAN | |
| `title_protection` | BOOLEAN | |
| `scope_protection` | BOOLEAN | |
| `issuing_authority` | TEXT | |
| `education_degree` | TEXT | |
| `renewal_years` | INTEGER | |
| `ce_hours` | INTEGER | |
| `reciprocity_available` | BOOLEAN | |
| `compacts` | TEXT[] | |
| `national_certification` | TEXT | |
| `national_association` | TEXT | |
| `advisory_board_exists` | BOOLEAN | |
| `renewal_fee_usd` | INTEGER | |
| `evidence_verified` | INTEGER | |
| `evidence_unverified` | INTEGER | |
| `extracted_at` | TIMESTAMP | mirrors the structured-record write time |

UNIQUE constraint on `(state, profession_id)`.

### `discovered_fields`

One row per (profession, field) for the auto-discovered profession-specific
schema. Lets `/search` show a result like "California / podiatry /
opioid_prescribing_limits" with the field's display description nearby.

| col | type | notes |
|---|---|---|
| `id` | BIGSERIAL PK | |
| `profession_id` | BIGINT FK | |
| `name` | VARCHAR(128) | |
| `category` | VARCHAR(128) | |
| `description` | TEXT | |
| `type` | VARCHAR(16) | bool / int / str / list / enum |

### `practice_acts`

Many-to-many: which `documents` rows constitute a profession's practice
act. Used by /search to filter "show me only sections that are
practice-act material for nursing" and by analytics to count states
with a recognizable practice act per profession.

| col | type | notes |
|---|---|---|
| `profession_id` | BIGINT FK → professions(id) | |
| `document_id` | BIGINT FK → documents(id) | typically a chapter-level row |
| PRIMARY KEY | (profession_id, document_id) | |

### `umbrella_applies_to`

Many-to-many: which `documents` rows (umbrella chapters / sections) apply
to which profession in that state. Populated from
`pipeline/results/umbrella_scope/<STATE>.json` — the deterministic
scope assigner already classifies umbrella sections as universal vs
profession-specific based on statute enumerations.

| col | type | notes |
|---|---|---|
| `document_id` | BIGINT FK → documents(id) | the umbrella chapter or section |
| `profession_id` | BIGINT FK → professions(id) | |
| `scope_source` | VARCHAR(32) | mirrors the scope assigner: universal / anchor_universal / anchor_enumeration / inherited_enumeration |
| PRIMARY KEY | (document_id, profession_id) | |

## Migrations

Each numbered SQL file does one thing, named for what it adds.

```
pipeline/publish/db/migrations/
  0001_professions.sql
  0002_documents.sql                -- the regulatory-document tree (titles/chapters/sections)
  0003_evidence.sql
  0004_state_profession_profile.sql
  0005_discovered_fields.sql
  0006_practice_acts.sql            -- profession → document join
  0007_umbrella_applies_to.sql      -- umbrella scope join
  0008_documents_fts_index.sql      -- generates text_tsv on documents, adds GIN
  0009_evidence_fts_index.sql       -- generates quote_tsv on evidence, adds GIN
```

Run order is lex; future migrations append. We never edit a landed
migration — bug fixes become new migrations (`0010_fix_X.sql`).

## ETL: `pipeline/publish/db/load.py`

```bash
python -m pipeline.publish.db.load --profession podiatry      # one profession
python -m pipeline.publish.db.load --all                       # all six
python -m pipeline.publish.db.load --dry-run                   # plan-only
```

Behavior:
- Reads `DATABASE_URL` from `.env.local` (Vercel env pull).
- Walks `structured/<prof>/<state>.json` and produces upserts for each
  table.
- Uses `ON CONFLICT (...) DO UPDATE` (natural-key-style) to make
  re-runs idempotent. Old rows from professions still in scope get
  refreshed; rows from professions removed from scope are left alone
  unless `--prune` is passed.
- Walks Evidence via the shared `iter_evidence` helper from
  `extract/standard_model.py` so the field paths line up with the rest
  of the pipeline.
- Builds the `documents` tree from BOTH `hierarchy/<STATE>.json` (title
  + chapter rows + URL structure) AND `trimmed/<prof>/<STATE>.json`
  (section rows with text). `parent_id` is set by matching URL prefixes;
  `hierarchy_path` is materialized as `/<title-slug>/<chapter-slug>/<section-slug>`.
- Loads umbrella rows from `umbrella_text/<STATE>.json` and links them
  to professions via `umbrella_applies_to` using
  `umbrella_scope/<STATE>.json` as the source of truth on which sections
  apply to which professions.
- Logs a per-profession summary (`N evidence rows / N section rows /
  N profile rows / N umbrella links upserted`).

Hook into the publish flow: after `build_frontend.py` succeeds, run
`load.py` for the same profession. Add a `--load-db` flag to
build_frontend, or wire a separate orchestrator. For dev work we just
invoke `load.py` directly.

## /search route

Next.js route handler under `src/app/api/search/route.ts` that hits the
DB and a React page at `src/app/search/page.tsx`.

Query shape:
```
GET /api/search?q=<phrase>&scope=<quotes|statutes|both>
               &profession=<key?>&state=<XX?>&unverified_only=<bool?>
```

Two query targets the route can hit:

**Quotes (the extracted excerpts):** narrow, high-signal — the LLM
already picked these as the supporting language for a structured claim.
Result rows carry the field path so you know what claim the quote was
backing.

```sql
SELECT e.state, p.key AS profession, e.field_path, e.value_text,
       e.quote, e.citation, e.unverified,
       'quote' AS scope,
       ts_rank(e.quote_tsv, plainto_tsquery('english', $1)) AS rank
FROM evidence e
JOIN professions p ON p.id = e.profession_id
WHERE e.quote_tsv @@ plainto_tsquery('english', $1)
ORDER BY rank DESC
LIMIT 200;
```

**Statutes (the raw section text):** broader, finds language we may not
have extracted. Result rows carry section metadata; a click navigates
to the section in context.

```sql
SELECT s.state, p.key AS profession, s.citation, s.label,
       ts_headline('english', s.text, plainto_tsquery('english', $1),
                   'MaxFragments=2,MinWords=8,MaxWords=30') AS snippet,
       s.is_umbrella, 'statute' AS scope,
       ts_rank(s.text_tsv, plainto_tsquery('english', $1)) AS rank
FROM sections s
LEFT JOIN professions p ON p.id = s.profession_id
WHERE s.text_tsv @@ plainto_tsquery('english', $1)
ORDER BY rank DESC
LIMIT 200;
```

Default scope: `both` — UNION the two queries and let the UI tab between
them. Lets Atharv answer "find every state whose statute mentions
'subcutaneous'" (statute scope) vs "show me every state where we
extracted scope language containing 'subcutaneous'" (quote scope).

UI:
- A search bar at the top; results table below
- Two tabs: "In extracted quotes (N)" vs "In statute text (M)"
- Each row is clickable → opens the corresponding (state, profession) on
  the existing /profile page, scrolled to the relevant row
- Filter chips for profession / state / unverified
- Linked from the homepage Reports section as another report-style entry
  point ("Search across all extractions")

## Phased rollout

Three stages, each commit-able and reviewable:

1. **Schema + ETL** (no UI change). Land the migrations, get the loader
   running, verify the DB matches a hand-spot-check. Atharv can already
   use this for SQL.
2. **/search route + React page.** Now the search is on the live site.
3. **Integration polish.** Search results link to /profile drill-downs;
   add the search box to the homepage; consider replacing the per-cell
   citation lookup in build_frontend with DB-backed queries (only if
   page-build time is hurting).

## Open decisions

- **Neon free vs paid tier.** Free covers the current scale (~150 MB
  data, sub-millisecond queries) plus the +5 occupations Atharv has
  queued. Paid (Launch, $19/mo) buys multiple branches (dev/prod
  separation), longer query timeouts, and autosuspend tuning. Default:
  free until something forces an upgrade.
- **Drizzle vs raw SQL in the search route.** Drizzle is what the
  newyork repo uses, but a single `/api/search` query might be cleaner
  as raw parameterized SQL. Default: Drizzle for parity with newyork.
- **What goes in `sections.text`?** Two candidate shapes:
  - Trimmed text (what the LLM saw — the substantive sections, with
    "repealed/reserved/ministerial" sections already dropped). Smaller
    DB; matches what evidence quotes can map back to.
  - Clean text (the full scraped corpus, including dropped sections).
    Bigger DB (probably ~3× the size), but `/search` could find
    language in sections we trimmed away.

  Default: trimmed. Atharv's use case is "find statutory language
  that's actually load-bearing", not "find every mention anywhere in
  the code". If we hear "I wished I could search the dropped sections
  too", revisit.
- **ETL frequency / trigger.** Options:
  - Manual: `python -m pipeline.publish.db.load --all` after each
    publish run.
  - Hooked into `build_frontend.py` via a `--load-db` flag.
  - Cron / GitHub Action: nightly re-load.

  Default: manual + a `--load-db` convenience flag. Pipeline runs are
  rare enough (few times a week) that automation doesn't earn its
  complexity yet.
- **Historical extractions / time travel.** Right now structured/
  files overwrite on each extract. If we want "show me how the
  extraction for CA podiatry changed between May 12 and May 21", we'd
  need to either keep extraction history in the DB (extra column
  `extracted_at`, never delete) or rely on git history. Default:
  don't store history; rely on git for that audit trail.
- **Search-index file as interim.** If the DB takes more than a day or
  two to land, we may want to ship the flat-JSON search index as a
  stopgap. Throwaway code; takes ~2 hrs to build.

## What to write before starting

- `apps/web/.env.local` needs `DATABASE_URL=...` from Neon
- Vercel project env needs the same (use `vercel env pull` once configured)
- `requirements.txt` += `psycopg[binary]` for the Python loader
- `package.json` += `drizzle-orm`, `drizzle-kit`, `pg` for the web side

## What to ask the team

Before starting:
- Is the Neon free tier enough for your usage pattern, or pay for the
  scale-up plan from day one?
- Does Atharv want any specific SQL views pre-built (e.g., "states by
  compact membership", "fields with the most unverified flags")?
- Should the search results page show the quote_spans yellow-highlight
  preview, or just plain text with the matched phrase bolded?

## Estimated effort

- Schema + migrations (7 tables, 2 FTS indexes): 1 day
- Python loader — evidence + profile + discovered_fields: 1 day
- Python loader — documents tree (titles/chapters/sections + parent_id +
  hierarchy_path) + umbrella linking: 1.5 days (more careful work
  because per-state URL patterns vary and section_fallback states need
  synthesized chapter rows)
- /search route + UI with two query targets (quote / statute) and
  hierarchy-aware breadcrumbs: 1 day
- Wiring, env, deploy debugging, edge cases: 1 day

Total: ~5.5 working days. The hierarchy load is the main extra cost
vs. the original flat-`sections` plan; the wins (group by chapter,
search constrained to title, render umbrella context) earn it for a
project where Atharv will write his own analyses.
