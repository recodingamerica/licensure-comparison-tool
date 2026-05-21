-- Migration: 0008_documents_fts_index
-- Full-text search index on documents.text so /search can find raw
-- statute language (not just LLM-extracted quotes). Generated column
-- means the index stays in sync automatically — no triggers needed,
-- no manual REFRESH.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0008_documents_fts_index.sql

ALTER TABLE documents
    ADD COLUMN IF NOT EXISTS text_tsv TSVECTOR
        GENERATED ALWAYS AS (
            to_tsvector('english', COALESCE(text, ''))
        ) STORED;

CREATE INDEX IF NOT EXISTS idx_documents_text_tsv ON documents USING GIN (text_tsv);
