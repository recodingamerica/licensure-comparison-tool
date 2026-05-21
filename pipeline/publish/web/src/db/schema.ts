// Drizzle schema mirror of pipeline/publish/db/migrations/0001..0009.
//
// IMPORTANT: this file does NOT create the schema — `psql -f migrations/*.sql`
// is the source of truth. The Drizzle types here exist so the web app can
// query the DB with type safety (column names, return types, generated SQL).
// When you add a migration, also add the matching Drizzle column here, OR
// regenerate via `drizzle-kit introspect` if you'd rather sync from the DB.
//
// Generated columns (text_tsv on documents, quote_tsv on evidence) are
// declared as plain `customType('tsvector')`. Drizzle doesn't have first-
// class generated-column support; we treat them as read-only string columns
// the DB maintains.

import {
  bigserial,
  boolean,
  char,
  customType,
  index,
  integer,
  jsonb,
  pgTable,
  primaryKey,
  text,
  timestamp,
  uniqueIndex,
  varchar,
  type AnyPgColumn,
} from "drizzle-orm/pg-core";

// tsvector: Postgres FTS index payload. Custom type because Drizzle's
// builtin set doesn't include it. We never write to these columns from
// the app — Postgres generates them from `text` / `quote`.
const tsvector = customType<{ data: string }>({
  dataType: () => "tsvector",
});

// ─── professions ──────────────────────────────────────────────────────────

export const professions = pgTable(
  "professions",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    key: varchar("key", { length: 64 }).notNull().unique(),
    display: text("display").notNull(),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
);

// ─── documents (the regulatory tree) ──────────────────────────────────────

export const documents = pgTable(
  "documents",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    state: char("state", { length: 2 }).notNull(),
    // Self-reference: a section's parent is a chapter, a chapter's parent
    // is a title. AnyPgColumn typing dance is the Drizzle workaround for
    // TS not handling recursive type references.
    parentId: integer("parent_id").references((): AnyPgColumn => documents.id),
    hierarchyLevel: varchar("hierarchy_level", { length: 32 }).notNull(),
    hierarchyPath: text("hierarchy_path").notNull(),
    url: text("url"),
    citation: text("citation"),
    label: text("label").notNull(),
    text: text("text"),
    textTsv: tsvector("text_tsv"),
    isUmbrella: boolean("is_umbrella").notNull().default(false),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex("documents_state_hierarchy_path_key").on(t.state, t.hierarchyPath),
    index("idx_documents_state_level").on(t.state, t.hierarchyLevel),
    index("idx_documents_parent").on(t.parentId),
    index("idx_documents_hierarchy_path").on(t.hierarchyPath),
  ],
);

// ─── evidence ─────────────────────────────────────────────────────────────

export const evidence = pgTable(
  "evidence",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    state: char("state", { length: 2 }).notNull(),
    professionId: integer("profession_id").notNull().references(() => professions.id, {
      onDelete: "cascade",
    }),
    sectionId: integer("section_id").references(() => documents.id, {
      onDelete: "set null",
    }),
    fieldPath: text("field_path").notNull(),
    valueText: text("value_text"),
    valueJsonb: jsonb("value_jsonb"),
    quote: text("quote").notNull(),
    citation: text("citation").notNull(),
    unverified: boolean("unverified").notNull().default(false),
    quoteTsv: tsvector("quote_tsv"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex("evidence_state_profession_field_key").on(t.state, t.professionId, t.fieldPath),
    index("idx_evidence_state_prof").on(t.state, t.professionId),
    index("idx_evidence_field_path").on(t.fieldPath),
  ],
);

// ─── state_profession_profile ─────────────────────────────────────────────

export const stateProfessionProfile = pgTable(
  "state_profession_profile",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    state: char("state", { length: 2 }).notNull(),
    professionId: integer("profession_id").notNull().references(() => professions.id, {
      onDelete: "cascade",
    }),
    coverageGap: boolean("coverage_gap").notNull().default(false),
    coverageGapReason: varchar("coverage_gap_reason", { length: 64 }),
    licenseRequired: boolean("license_required"),
    regulatoryModel: varchar("regulatory_model", { length: 64 }),
    credentialType: varchar("credential_type", { length: 32 }),
    isMandatory: boolean("is_mandatory"),
    titleProtection: boolean("title_protection"),
    scopeProtection: boolean("scope_protection"),
    issuingAuthority: text("issuing_authority"),
    educationDegree: text("education_degree"),
    postDegreeDuration: text("post_degree_duration"),
    examsCount: integer("exams_count").notNull().default(0),
    renewalYears: integer("renewal_years"),
    ceHours: integer("ce_hours"),
    cePeriodYears: integer("ce_period_years"),
    reciprocityAvailable: boolean("reciprocity_available"),
    compacts: text("compacts").array().notNull().default([]),
    disciplinaryGroundsCount: integer("disciplinary_grounds_count").notNull().default(0),
    advisoryBoardExists: boolean("advisory_board_exists"),
    nationalCertification: text("national_certification"),
    nationalAssociation: text("national_association"),
    renewalFeeUsd: integer("renewal_fee_usd"),
    evidenceVerified: integer("evidence_verified").notNull().default(0),
    evidenceUnverified: integer("evidence_unverified").notNull().default(0),
    extractedAt: timestamp("extracted_at"),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex("state_profession_profile_state_prof_key").on(t.state, t.professionId),
    index("idx_profile_state").on(t.state),
    index("idx_profile_profession").on(t.professionId),
    index("idx_profile_regulatory_model").on(t.regulatoryModel),
    index("idx_profile_credential_type").on(t.credentialType),
  ],
);

// ─── discovered_fields ────────────────────────────────────────────────────

export const discoveredFields = pgTable(
  "discovered_fields",
  {
    id: bigserial("id", { mode: "number" }).primaryKey(),
    professionId: integer("profession_id").notNull().references(() => professions.id, {
      onDelete: "cascade",
    }),
    name: varchar("name", { length: 128 }).notNull(),
    category: varchar("category", { length: 128 }),
    description: text("description"),
    type: varchar("type", { length: 16 }).notNull(),
    sampleQuote: text("sample_quote"),
    sampleState: char("sample_state", { length: 2 }),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex("discovered_fields_profession_name_key").on(t.professionId, t.name),
    index("idx_discovered_fields_profession").on(t.professionId),
  ],
);

// ─── practice_acts (join) ─────────────────────────────────────────────────

export const practiceActs = pgTable(
  "practice_acts",
  {
    professionId: integer("profession_id").notNull().references(() => professions.id, {
      onDelete: "cascade",
    }),
    documentId: integer("document_id").notNull().references(() => documents.id, {
      onDelete: "cascade",
    }),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [
    primaryKey({ columns: [t.professionId, t.documentId] }),
    index("idx_practice_acts_document").on(t.documentId),
  ],
);

// ─── umbrella_applies_to (join) ───────────────────────────────────────────

export const umbrellaAppliesTo = pgTable(
  "umbrella_applies_to",
  {
    documentId: integer("document_id").notNull().references(() => documents.id, {
      onDelete: "cascade",
    }),
    professionId: integer("profession_id").notNull().references(() => professions.id, {
      onDelete: "cascade",
    }),
    scopeSource: varchar("scope_source", { length: 32 }).notNull(),
    createdAt: timestamp("created_at").notNull().defaultNow(),
  },
  (t) => [
    primaryKey({ columns: [t.documentId, t.professionId] }),
    index("idx_umbrella_applies_to_profession").on(t.professionId),
  ],
);

// ─── Inferred types for callers ───────────────────────────────────────────

export type Profession = typeof professions.$inferSelect;
export type Document = typeof documents.$inferSelect;
export type Evidence = typeof evidence.$inferSelect;
export type StateProfessionProfile = typeof stateProfessionProfile.$inferSelect;
export type DiscoveredField = typeof discoveredFields.$inferSelect;
export type PracticeAct = typeof practiceActs.$inferSelect;
export type UmbrellaAppliesTo = typeof umbrellaAppliesTo.$inferSelect;
