# Postgres schema + ETL

The data model that backs `/search` and Atharv's ad-hoc SQL. See
`docs/POSTGRES_PLAN.md` for the rationale; this README is the operator's
guide.

## One-time setup

1. Create a Neon project at https://console.neon.tech.
2. Copy the connection string (looks like
   `postgresql://user:password@host/dbname?sslmode=require`).
3. Drop it in two places:

   ```bash
   # Web app
   echo 'DATABASE_URL=postgresql://...' >> pipeline/publish/web/.env.local

   # Pipeline (Python loader reads from here when available, else from
   # web/.env.local automatically)
   echo 'DATABASE_URL=postgresql://...' >> pipeline/.env
   ```

   Or use the Vercel native Neon integration which provisions the env
   var into Vercel automatically (recommended).

## Apply migrations

Run all migrations in order (idempotent — every migration uses
`CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO NOTHING`, etc., so
re-applying does nothing).

```bash
for f in pipeline/publish/db/migrations/*.sql; do
  echo ">>> $f"
  psql "$DATABASE_URL" -f "$f"
done
```

To apply one specific migration:

```bash
psql "$DATABASE_URL" -f pipeline/publish/db/migrations/0002_documents.sql
```

## Re-load data

After a `build_frontend` run (or any extraction refresh), reload the DB:

```bash
python -m pipeline.publish.db.load --all          # all 6 professions
python -m pipeline.publish.db.load --profession podiatry
python -m pipeline.publish.db.load --all --dry-run
```

The loader is idempotent: re-runs upsert via natural keys
(`(state, profession, field_path)` etc.), so the DB always reflects the
current state of `pipeline/results/structured/`.

## Migration naming

`NNNN_<short_description>.sql`, 4-digit zero-padded prefix, lex-sortable.
For same-number siblings use `NNNNa_`, `NNNNb_`. **Never edit a
landed migration** — bug fixes become new migrations.

## Reset for development

```bash
psql "$DATABASE_URL" <<SQL
DROP TABLE IF EXISTS evidence, umbrella_applies_to, practice_acts,
                     state_profession_profile, discovered_fields,
                     documents, professions CASCADE;
SQL

# then re-apply
for f in pipeline/publish/db/migrations/*.sql; do
  psql "$DATABASE_URL" -f "$f"
done
```
