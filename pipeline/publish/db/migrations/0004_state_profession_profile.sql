-- Migration: 0004_state_profession_profile
-- The flat per-(state, profession) summary row. Reproduces the shape of
-- `Row` that hoist_row() in build_frontend.py produces, so SQL queries
-- can ask things like "every state where credential_type='registration'"
-- without joining-and-aggregating from evidence.
--
-- One row per (state, profession). UPSERTed by the ETL.
--
-- Run: psql $DATABASE_URL -f pipeline/publish/db/migrations/0004_state_profession_profile.sql

CREATE TABLE IF NOT EXISTS state_profession_profile (
    id                          BIGSERIAL PRIMARY KEY,
    state                       CHAR(2) NOT NULL,
    profession_id               BIGINT NOT NULL REFERENCES professions(id) ON DELETE CASCADE,
    coverage_gap                BOOLEAN NOT NULL DEFAULT FALSE,
    coverage_gap_reason         VARCHAR(64),

    -- Core licensure shape
    license_required            BOOLEAN,
    regulatory_model            VARCHAR(64),     -- 6-rung UORF enum
    credential_type             VARCHAR(32),     -- license / certification / registration / exemption / none
    is_mandatory                BOOLEAN,
    title_protection            BOOLEAN,
    scope_protection            BOOLEAN,

    -- Issuing body
    issuing_authority           TEXT,

    -- Path to licensure
    education_degree            TEXT,
    post_degree_duration        TEXT,
    exams_count                 INTEGER NOT NULL DEFAULT 0,
    renewal_years               INTEGER,
    ce_hours                    INTEGER,
    ce_period_years             INTEGER,
    reciprocity_available       BOOLEAN,

    -- Compacts (text[] mirrors the JSON array)
    compacts                    TEXT[] NOT NULL DEFAULT '{}',
    disciplinary_grounds_count  INTEGER NOT NULL DEFAULT 0,

    -- Atharv's universal-comparison fields
    advisory_board_exists       BOOLEAN,
    national_certification      TEXT,
    national_association        TEXT,
    renewal_fee_usd             INTEGER,

    -- Evidence-audit summary
    evidence_verified           INTEGER NOT NULL DEFAULT 0,
    evidence_unverified         INTEGER NOT NULL DEFAULT 0,

    extracted_at                TIMESTAMP,
    created_at                  TIMESTAMP NOT NULL DEFAULT NOW(),

    UNIQUE (state, profession_id)
);

CREATE INDEX IF NOT EXISTS idx_profile_state             ON state_profession_profile(state);
CREATE INDEX IF NOT EXISTS idx_profile_profession        ON state_profession_profile(profession_id);
-- Common filter combos so Atharv's ad-hoc queries don't seq-scan.
CREATE INDEX IF NOT EXISTS idx_profile_regulatory_model  ON state_profession_profile(regulatory_model);
CREATE INDEX IF NOT EXISTS idx_profile_credential_type   ON state_profession_profile(credential_type);
