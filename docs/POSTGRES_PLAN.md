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

### `sections`

The trimmed corpus, one row per (state, profession, citation). Used as
the join target for evidence (so we can show "view in context" against
the actual statute text) AND as a standalone FTS target so Atharv can
search the raw statutory language for terms we may not have explicitly
extracted as evidence.

| col | type | notes |
|---|---|---|
| `id` | BIGSERIAL PK | |
| `state` | CHAR(2) | |
| `profession_id` | BIGINT FK → professions | nullable when `is_umbrella=true` (umbrella sections are shared across professions per state) |
| `url` | TEXT | Justia source URL |
| `citation` | TEXT | normalized form (see `normalize_citation`) |
| `label` | TEXT | section label as Justia rendered it |
| `text` | TEXT | the cleaned statute text (full body) |
| `is_umbrella` | BOOLEAN | true when the section came from cross-cutting chapter |
| `text_tsv` | TSVECTOR | generated column for FTS |

Indexes:
- `(state, profession_id, citation)` for evidence joins
- GIN on `text_tsv` for raw-statute phrase search

Storage note: ~50 MB raw text + ~80 MB FTS index. This is the bulk of
the database size; we accept it because Atharv wants to search the
statute language directly, not just the excerpts.

### `evidence`

One row per Evidence-shaped node in `structured/<prof>/<state>.json`.
Search runs against this table.

| col | type | notes |
|---|---|---|
| `id` | BIGSERIAL PK | |
| `state` | CHAR(2) | |
| `profession_id` | BIGINT FK → professions | |
| `section_id` | BIGINT FK → sections (nullable) | citation → section join |
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

## Migrations

Each numbered SQL file does one thing, named for what it adds.

```
pipeline/publish/db/migrations/
  0001_professions.sql
  0002_sections.sql
  0003_evidence.sql
  0004_state_profession_profile.sql
  0005_discovered_fields.sql
  0006_evidence_fts_index.sql       -- generates quote_tsv, adds GIN
  0007_section_fts_index.sql        -- same for sections.text
```

Run order is lex; future migrations append. We never edit a landed
migration — bug fixes become new migrations (`0008_fix_X.sql`).

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
- Uses `ON CONFLICT (state, profession_id) DO UPDATE` (or similar) to
  make re-runs idempotent. Old rows from professions still in scope
  get refreshed; rows from professions removed from scope are left
  alone unless `--prune` is passed.
- Walks Evidence via the shared `iter_evidence` helper from
  `extract/standard_model.py` so the field paths line up with the rest
  of the pipeline.
- Logs a per-profession summary (`N evidence rows / N sections / N
  profile rows upserted`).

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

- Schema + migrations: 1 day
- Python loader: 1 day
- /search route + UI: 1 day
- Wiring, env, deploy debugging, edge cases: 1 day

Total: ~4 working days of focused effort. Could compress if I'm not
also debugging extract runs in parallel.
