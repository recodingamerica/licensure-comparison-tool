-- Migration: 0003_evidence
-- One row per Evidence-shaped node in structured/<prof>/<state>.json. The
-- ETL walks via the shared iter_evidence() helper so the field_paths line
-- up with the rest of the pipeline (e.g. licensure.issuing_authority,
-- profession_specific.opioid_prescribing_limits).
--
-- This is the table /search hits for quote-scope queries.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0003_evidence.sql

CREATE TABLE IF NOT EXISTS evidence (
    id              BIGSERIAL PRIMARY KEY,
    state           CHAR(2) NOT NULL,
    profession_id   BIGINT NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    section_id      BIGINT REFERENCES documents(id) ON DELETE SET NULL,
    field_path      TEXT NOT NULL,
    value_text      TEXT,
    value_jsonb     JSONB,
    quote           TEXT NOT NULL,
    citation        TEXT NOT NULL,
    unverified      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),

    -- A (state, profession, field_path) tuple uniquely identifies an Evidence
    -- node when re-ETL'd. Use this for upserts.
    UNIQUE (state, profession_id, field_path)
);

-- Drill-down lookups: "show me all evidence for nursing in CA".
CREATE INDEX IF NOT EXISTS idx_evidence_state_prof   ON evidence(state, profession_id);
CREATE INDEX IF NOT EXISTS idx_evidence_field_path   ON evidence(field_path);
-- The "what's flagged" use case.
CREATE INDEX IF NOT EXISTS idx_evidence_unverified   ON evidence(state, profession_id) WHERE unverified;
-- Section join (sparse — not every evidence row pins to a single section).
CREATE INDEX IF NOT EXISTS idx_evidence_section      ON evidence(section_id) WHERE section_id IS NOT NULL;
