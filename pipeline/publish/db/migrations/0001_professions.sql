-- Migration: 0001_professions
-- The registered set of professions the pipeline extracts. Keyed by the
-- snake_case identifier used throughout the pipeline (pipeline/results/
-- discovered/<key>.json, structured/<key>/...).
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0001_professions.sql

CREATE TABLE IF NOT EXISTS professions (
    id          BIGSERIAL PRIMARY KEY,
    key         VARCHAR(64) NOT NULL UNIQUE,
    display     TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Seed with the six currently-extracted professions. Re-runnable: ON CONFLICT
-- DO NOTHING so re-applying the migration is idempotent. New professions get
-- their own migrations rather than editing this one.
INSERT INTO professions (key, display) VALUES
    ('podiatry',           'Podiatry'),
    ('nursing',            'Nursing (RN / LPN / APRN)'),
    ('medicine',           'Medicine'),
    ('dentistry',          'Dentistry'),
    ('optometry',          'Optometry'),
    ('public_accountancy', 'Public Accountancy (CPA)')
ON CONFLICT (key) DO NOTHING;
