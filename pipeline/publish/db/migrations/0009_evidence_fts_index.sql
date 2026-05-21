-- Migration: 0009_evidence_fts_index
-- Full-text search index on evidence.quote so /search can find the
-- LLM-extracted quotes that ground each structured claim.
-- Generated + stored so it stays in sync without triggers.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0009_evidence_fts_index.sql

ALTER TABLE evidence
    ADD COLUMN IF NOT EXISTS quote_tsv TSVECTOR
        GENERATED ALWAYS AS (
            to_tsvector('english', COALESCE(quote, ''))
        ) STORED;

CREATE INDEX IF NOT EXISTS idx_evidence_quote_tsv ON evidence USING GIN (quote_tsv);
