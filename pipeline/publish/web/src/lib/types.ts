// Mirrors the shapes emitted by pipeline/publish/build_frontend.py.
// Kept narrow — just the fields the UI reads.

export type Evidence<T = unknown> = {
  value: T;
  quote: string;
  citation: string;
  unverified?: boolean;
  // Set by the verifier's fuzzy fallback when the strict regex match
  // fails but a long contiguous substring of the LLM quote DOES appear
  // in the corpus. `ratio` is longest_matching_block / quote_length,
  // so 0.85 = "85% of the quote text was found verbatim somewhere in
  // the source." `matched_normalized` is that longest block in
  // normalized form (lowercased, punctuation collapsed) — useful for
  // surfacing "this is what we think you meant" in the UI.
  approximate?: {
    ratio: number;
    matched_normalized: string;
  };
  // Pre-computed character offsets into the cited section's `text`,
  // emitted by pipeline/publish/build_frontend.py via
  // pipeline/extract/locate_quote.py. Each pair is [start, end). Multiple
  // pairs when the quote was elided with "..." across non-contiguous
  // ranges. Absent when the quote couldn't be pinned to a single section
  // (the verifier may still have accepted it against the combined
  // corpus — render quote without a highlight in that case).
  quote_spans?: Array<[number, number]>;
};

export type EducationRequirement = {
  degree_required?: Evidence<string> | null;
  accrediting_body?: Evidence<string> | null;
};

export type PostDegreeExperience = {
  required?: Evidence<boolean> | null;
  duration?: Evidence<string> | null;
  kind?: Evidence<string> | null;
};

export type ContinuingEducation = {
  required?: Evidence<boolean> | null;
  hours_per_period?: Evidence<number> | null;
  period_years?: Evidence<number> | null;
  topical_requirements?: Evidence<string[]> | null;
};

export type Renewal = {
  interval_years?: Evidence<number> | null;
};

export type Reciprocity = {
  available?: Evidence<boolean> | null;
  requirements?: Evidence<string> | null;
};

export type Exam = {
  name: string;
  required: boolean;
  notes?: string | null;
  quote: string;
  citation: string;
};

export type DisciplinaryGround = {
  short_label: string;
  description: string;
  quote: string;
  citation: string;
  // Content bucket assigned by the per-item bucketing pass (e.g. "Fraud &
  // Misrepresentation"). Absent when the pass hasn't run for the profession.
  category?: string;
};

export type LicensureRequirements = {
  license_required?: Evidence<boolean> | null;
  issuing_authority?: Evidence<string> | null;
  age_minimum?: Evidence<number> | null;
  moral_character_required?: Evidence<boolean> | null;
  education?: EducationRequirement | null;
  post_degree_experience?: PostDegreeExperience | null;
  exams: Exam[];
  renewal?: Renewal | null;
  continuing_education?: ContinuingEducation | null;
  reciprocity?: Reciprocity | null;
  regulatory_model?: Evidence<string> | null;
  credential_type?: Evidence<string> | null;
  is_mandatory?: Evidence<boolean> | null;
  title_protection?: Evidence<boolean> | null;
  scope_protection?: Evidence<boolean> | null;
  disciplinary_grounds: DisciplinaryGround[];
};

export type ScopeOfPractice = {
  definition_quote?: Evidence<string> | null;
  methods_authorized?: Evidence<string[]> | null;
  drug_authority?: Evidence<string> | null;
};

export type StructuredRecord = {
  state: string;
  profession: string;
  licensure: LicensureRequirements;
  scope: ScopeOfPractice;
  profession_specific: Record<string, Evidence<unknown> | null>;
};

export type SectionRef = {
  url: string;
  citation: string;
  label?: string;
  text?: string;
};

export type Row = {
  state: string;
  coverage_gap: boolean;
  coverage_gap_reason?: string;
  coverage_gap_label?: string;
  license_required: boolean | null;
  regulatory_model: string | null;
  credential_type: string | null;
  is_mandatory: boolean | null;
  title_protection: boolean | null;
  scope_protection: boolean | null;
  issuing_authority: string | null;
  education_degree: string | null;
  post_degree_duration: string | null;
  exams_count: number;
  renewal_years: number | null;
  ce_hours: number | null;
  ce_period_years: number | null;
  reciprocity_available: boolean | null;
  compacts: string[];
  disciplinary_grounds_count: number;
  // Per-state content tags for disciplinary grounds (from the per-item
  // bucketing pass), count desc. Empty when the pass hasn't run.
  disciplinary_categories?: { label: string; count: number }[];
  // Same, for every per-item-bucketed profession-specific list field, keyed by
  // dotted field name (e.g. "profession_specific.laser_procedures_authorized").
  list_field_categories?: Record<string, { label: string; count: number }[]>;
  // Universal-comparison fields aligned with the cross-state schema.
  advisory_board_exists: boolean | null;
  advisory_board_name: string | null;
  advisory_board_authority: string | null;
  national_certification: string | null;
  national_association: string | null;
  renewal_fee_usd: number | null;
  evidence_verified: number;
  evidence_unverified: number;
  // Subset of evidence_unverified — entries that strict-fail but pass
  // the fuzzy fallback (longest matching block ≥ 0.7 of quote length).
  // UI uses this to show "approximate match" instead of bare unverified.
  evidence_approximate?: number;
  source_chapter_urls?: string[];
  sections?: SectionRef[];
  // Concatenation of every section body shipped with this row. Lives here so
  // the table's "Statute text" filter can do plain substring matching across
  // all the statute language for this (state, profession) without joining at
  // query time. Large (~50–500 KB per row).
  section_text_full?: string;
  // Per-individual-section data for the /browse view. One entry per section
  // (umbrella not aggregated, unlike row.sections), tagged with scope_layer
  // so the tree can group practice / health umbrella / universal umbrella.
  // Each section carries its own evidence spans anchored to its text.
  browse_sections?: BrowseSection[];
  _full: StructuredRecord;
};

export type BrowseSection = {
  url: string;
  citation: string;
  label: string;
  text: string;
  scope_layer: "practice" | "umbrella_universal" | "umbrella_enumeration";
  applies_to: string[] | null;
  evidence: BrowseEvidence[];
};

// Tree groups for the per-profession /browse/[state]/[prof] view.
// Layer key matches BrowseSection.scope_layer; tree is a forest of
// TreeNode (defined in components/browse/tree-node.tsx).
export type BrowseGroup<TreeNodeT = unknown> = {
  key: BrowseSection["scope_layer"];
  tree: TreeNodeT[];
};

export type BrowseEvidence = {
  field_path: string;
  value: unknown;
  quote: string;
  spans: Array<[number, number]>;
  unverified: boolean;
  // Only present on state-level browse data — identifies which profession's
  // extraction produced this evidence (so the UI can show "nursing drew X
  // from this universal section"). Absent on per-profession browse data
  // because the whole blob is already scoped to one profession.
  profession?: string;
};

export type DiscoveredField = {
  name: string;
  category: string;
  type: "bool" | "int" | "str" | "list[str]" | "enum";
  enum_values?: string[] | null;
  description: string;
  sample_quote: string;
  sample_state: string;
  states_supporting: string[];
};

// Choropleth normalization output, produced by pipeline/map_prep/run.py and
// attached to the per-profession payload by build_frontend.py. The spec
// describes how each mappable field is colored (gradient vs. palette + which
// categories); rows are the per-state normalized values.
export type MapFieldSpec = {
  field_name: string;
  mappable: true;
  kind: "continuous" | "categorical";
  unit: string | null;
  categories: string[] | null;
  reason: string;
};

export type MapRow = {
  field_name: string;
  state: string;
  raw_value: string;
  normalized: number | string | null;
  // Verbatim statute quote + citation pulled from the structured record by
  // build_frontend.py. Absent when the source field has no Evidence at the
  // expected dotted path (rare, but possible for sparse profession-specific
  // fields).
  quote?: string;
  citation?: string;
};

export type MapPrep = {
  spec: MapFieldSpec[];
  rows: MapRow[];
  // Pass-3 LLM bucketing of the not_mappable free-text fields (added 2026-
  // 05-28). Surfaces as a chip in the profile-view table cell + the raw text.
  text_buckets?: Record<
    string,
    {
      bucket_set: string[];
      rationale: string;
      by_state: Record<string, string>;
    }
  >;
  // Per-item tag breadth: for each per-item-bucketed list field, the count of
  // distinct content categories each state falls into. Rendered as continuous
  // "# of distinct …" choropleths (e.g. how many laser-procedure types a state
  // authorizes). Added 2026-06-10.
  per_item_count_fields?: {
    field_name: string;
    by_state_count: Record<string, number>;
  }[];
};

export type ProfilePayload = {
  profession: string;
  display: string;
  discovered_fields: DiscoveredField[];
  rows: Row[];
  map_prep?: MapPrep | null;
  evidence_summary: { verified: number; unverified: number };
};

export type ProfessionsListEntry = {
  profession: string;
  display: string;
  covered: number;
  gaps: number;
  fields: number;
  verified_pct: number | null;
};
