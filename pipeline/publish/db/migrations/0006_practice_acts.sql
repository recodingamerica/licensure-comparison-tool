-- Migration: 0006_practice_acts
-- Many-to-many: which `documents` rows constitute a profession's practice
-- act in a given state. Used by /search to filter "show me only
-- practice-act material for nursing", and by analytics to count states
-- with a recognizable practice act per profession.
--
-- Sourced from pipeline/results/profession_index/<prof>.json — for each
-- state where match_profession.py found the profession's chapter, we
-- link that chapter (and its descendant sections) to the profession.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0006_practice_acts.sql

CREATE TABLE IF NOT EXISTS practice_acts (
    profession_id   BIGINT NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    document_id     BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (profession_id, document_id)
);

CREATE INDEX IF NOT EXISTS idx_practice_acts_document ON practice_acts(document_id);
