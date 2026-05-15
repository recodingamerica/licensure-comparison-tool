// Mirrors the shapes emitted by pipeline/publish/build_frontend.py.
// Kept narrow — just the fields the UI reads.

export type Evidence<T = unknown> = {
  value: T;
  quote: string;
  citation: string;
  unverified?: boolean;
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
  disciplinary_grounds_count: number;
  evidence_verified: number;
  evidence_unverified: number;
  source_chapter_urls?: string[];
  sections?: SectionRef[];
  _full: StructuredRecord;
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
