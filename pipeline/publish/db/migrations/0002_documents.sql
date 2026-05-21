-- Migration: 0002_documents
-- The regulatory-document tree. One row per regulatory entity at any level —
-- title, chapter, subchapter, article, part, or section — linked via
-- parent_id and identified by a materialized hierarchy_path.
--
-- Modeled on newyork's regulatory_documents. Self-referential FK so the
-- whole code tree per state hangs together; hierarchy_path lets us
-- do "all docs under /title-32/..." with a single B-tree index lookup
-- instead of recursive CTEs.
--
-- Section-level rows (hierarchy_level='section') carry the actual statute
-- text in `text`. Higher-level rows (title, chapter) carry NULL text —
-- they exist to anchor the tree and to be referenced by joins like
-- practice_acts and umbrella_applies_to.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0002_documents.sql

CREATE TABLE IF NOT EXISTS documents (
    id                 BIGSERIAL PRIMARY KEY,
    state              CHAR(2) NOT NULL,
    parent_id          BIGINT REFERENCES documents(id) ON DELETE SET NULL,
    hierarchy_level    VARCHAR(32) NOT NULL
        CHECK (hierarchy_level IN ('title','chapter','subchapter','article','part','section')),
    hierarchy_path     TEXT NOT NULL,
    url                TEXT,
    citation           TEXT,
    label              TEXT NOT NULL,
    text               TEXT,
    is_umbrella        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at         TIMESTAMP NOT NULL DEFAULT NOW(),

    -- A (state, hierarchy_path) pair uniquely identifies a document. The
    -- loader uses this for upserts.
    UNIQUE (state, hierarchy_path)
);

-- Tree-walk + filter indexes.
CREATE INDEX IF NOT EXISTS idx_documents_state_level   ON documents(state, hierarchy_level);
CREATE INDEX IF NOT EXISTS idx_documents_parent        ON documents(parent_id);
CREATE INDEX IF NOT EXISTS idx_documents_hierarchy_path ON documents(hierarchy_path text_pattern_ops);
CREATE INDEX IF NOT EXISTS idx_documents_is_umbrella   ON documents(is_umbrella) WHERE is_umbrella;
-- Citation lookups (e.g., from evidence) — partial index on the populated rows.
CREATE INDEX IF NOT EXISTS idx_documents_citation      ON documents(state, citation) WHERE citation IS NOT NULL;
