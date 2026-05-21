-- Migration: 0007_umbrella_applies_to
-- Many-to-many: which `documents` rows (umbrella chapters or sections)
-- apply to which profession in a given state. Sourced from
-- pipeline/results/umbrella_scope/<STATE>.json — the deterministic
-- scope assigner (assign_umbrella_scope.py) already classifies
-- umbrella sections as universal vs profession-specific based on the
-- statute's own "licensed under Chapter X" enumerations.
--
-- A document_id may apply to MANY professions (universal sections
-- apply to all). A profession may have MANY umbrella documents.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0007_umbrella_applies_to.sql

CREATE TABLE IF NOT EXISTS umbrella_applies_to (
    document_id     BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    profession_id   BIGINT NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    scope_source    VARCHAR(32) NOT NULL
        CHECK (scope_source IN ('universal','anchor_universal','anchor_enumeration','inherited_enumeration')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (document_id, profession_id)
);

CREATE INDEX IF NOT EXISTS idx_umbrella_applies_to_profession ON umbrella_applies_to(profession_id);
