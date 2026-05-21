-- Migration: 0005_discovered_fields
-- The auto-discovered per-profession schema. One row per
-- (profession, field). Lets /search and analytics show a result like
-- "California / podiatry / opioid_prescribing_limits" alongside the
-- field's display description, instead of just the raw field name.
--
-- Sourced from pipeline/results/discovered/<prof>.json on each ETL run.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0005_discovered_fields.sql

CREATE TABLE IF NOT EXISTS discovered_fields (
    id              BIGSERIAL PRIMARY KEY,
    profession_id   BIGINT NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    name            VARCHAR(128) NOT NULL,
    category        VARCHAR(128),
    description     TEXT,
    type            VARCHAR(16) NOT NULL
        CHECK (type IN ('bool','int','str','list[str]','enum')),
    sample_quote    TEXT,
    sample_state    CHAR(2),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE (profession_id, name)
);

CREATE INDEX IF NOT EXISTS idx_discovered_fields_profession ON discovered_fields(profession_id);
CREATE INDEX IF NOT EXISTS idx_discovered_fields_category   ON discovered_fields(profession_id, category);
