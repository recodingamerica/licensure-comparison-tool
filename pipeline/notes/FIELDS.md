# Fields the pipeline extracts

Two layers: a **universal base** that applies to every profession, and a
**profession-specific** set auto-discovered by the pass-1b LLM from each
profession's own statutory corpus. Adding a third profession means running the
pipeline; no schema changes required.

## Universal base — every profession

All leaf fields are Evidence-wrapped (`{value, quote, citation}`); the quote is
regex-validated against the source statute.

### LicensureRequirements
- `license_required` — bool
- `issuing_authority` — str (e.g., "State Board of Podiatry")
- `age_minimum` — int
- `moral_character_required` — bool
- `education.degree_required` — str (e.g., "Doctor of Podiatric Medicine")
- `education.accrediting_body` — str (e.g., "CPME")
- `post_degree_experience.required` — bool
- `post_degree_experience.duration` — str (e.g., "24 months", "1 year")
- `post_degree_experience.kind` — str (residency / apprenticeship / supervised work)
- `exams` — list of `{name, required, notes, quote, citation}`
- `renewal.interval_years` — int
- `continuing_education.required` — bool
- `continuing_education.hours_per_period` — int
- `continuing_education.period_years` — int
- `continuing_education.topical_requirements` — list[str]
- `reciprocity.available` — bool
- `reciprocity.requirements` — str
- **`regulatory_model`** — enum: `license` | `mandatory_certification` | `registration` | `exemption` | `voluntary_certification` | `market_forces` (UORF six-rung ladder)
- **`title_protection`** — bool (may unlicensed people use the title?)
- **`scope_protection`** — bool (may unlicensed people perform the scope?)
- **`disciplinary_grounds`** — list of `{short_label, description, quote, citation}`
- `citations` — list of `{cite, kind}`

### ScopeOfPractice
- `definition_quote` — verbatim statutory definition
- `methods_authorized` — list[str] (e.g., ["medical", "surgical", "mechanical"])
- `drug_authority` — str
- `citations` — list

## Podiatry — 36 profession-specific fields auto-discovered

### advanced_tier (additional credentials that unlock extra scope)
- `ankle_surgery_authorized` — bool
- `ankle_surgery_residency_requirement` — enum (24-mo, 36-mo, 2yr-pre-2007, board-cert-required, hospital-credentialing-required, ABFAS-cert)
- `board_certification_body` — list[str]
- `ankle_surgery_board_certification_timeline` — str
- `total_ankle_replacement_authorized` — bool
- `ankle_surgery_standard_of_care_reference` — bool

### anatomy_or_procedure
- `anatomical_scope_upper_boundary` — enum (foot only / foot+ankle / leg below knee / soft tissue to tibial tuberosity / soft tissue to myotendinous junction / soft tissue to distal tibial metaphyseal flare / below mid-calf / tendons inserting into foot)

### drug_or_anesthesia
- `anesthesia_authority` — enum (local-only, local+conscious, local+moderate-deep, general-with-physician, general-excluded)
- `opioid_prescribing_rules_required` — bool
- `electronic_prescribing_required` — bool

### facility
- `ankle_surgery_facility_requirement` — enum (licensed-hospital, hospital-or-ASC, accredited-hospital-or-ASC, JCAHO-accredited, multispecialty-ASC)
- `hospital_privileges_nondiscrimination` — bool
- `office_based_surgery_accreditation_required` — bool

### scope_inclusion
- `amputation_authorized` — enum (toes-only, toes+parts, transmetatarsal, Chopart, foot-excluded, forefoot-excluded, not-authorized)
- `systemic_disease_local_manifestations_included` — bool
- `telehealth_authorized` — bool
- `wound_debridement_authorized` — bool
- `vaccination_authority` — bool
- `cosmetic_procedures_included` — bool
- `preoperative_history_and_physical_authorized` — bool
- `assistant_surgeon_role_authorized` — bool

### scope_exclusion
- `systemic_disease_treatment_excluded` — bool
- `tibial_pilon_fracture_excluded` — bool
- `corrective_footwear_exemption` — bool
- `clubfoot_surgery_restriction` — bool

### supervision_delegation
- `podiatric_assistant_authorized` — bool
- `podiatric_assistant_supervision_level` — enum (direct-on-premises, indirect, general)
- `xray_technician_certification_required` — bool
- `physician_assistant_collaboration_authorized` — bool
- `advanced_practice_nurse_collaboration_authorized` — bool

### other
- `professional_liability_insurance_required` — bool
- `controlled_substances_prescribing_ce_required` — bool
- `impaired_practitioner_program` — bool
- `minor_patient_chaperone_requirement` — bool
- `nondiscrimination_in_public_programs` — bool
- `noncompete_clause_restriction` — bool

## Public Accountancy (CPA) — 38 profession-specific fields auto-discovered

### advanced_tier
- `registered_municipal_accountant_designation` — bool
- `public_school_accountant_designation` — bool
- `accounting_practitioner_tier` — bool (sub-CPA designation)

### facility
- `firm_majority_cpa_ownership_required` — bool
- `nonlicensee_firm_owners_permitted` — bool
- `out_of_state_firm_no_office_exemption` — bool
- `firm_corrective_action_period_for_ownership_noncompliance` — bool
- `firm_permit_required_for_attest_services` — bool

### scope_inclusion
- `attest_services_types` — list[str]
- `compilation_services_authorized` — bool
- `attest_services_require_firm_permit` — bool
- `independence_requirement_for_attest` — bool

### scope_exclusion
- `commission_prohibition_during_attest` — bool
- `contingent_fee_prohibition_during_attest` — bool
- `safe_harbor_disclaimer_language_for_nonlicensees` — bool
- `foreign_accountant_practice_exception` — bool

### supervision_delegation
- `office_supervision_by_licensed_cpa_required` — bool
- `attest_report_signer_competency_requirement` — bool

### other
- `education_semester_hours_required` — int (typically 150 post-2000)
- `exam_sit_hours_minimum` — int (typically 120 to sit, 150 to license)
- `ethics_exam_required` — bool
- `practice_privilege_no_notice_required` — bool
- `practice_privilege_consent_conditions` — list[str]
- `peer_review_required_for_firm_renewal` — bool
- `peer_review_max_frequency_years` — int
- `peer_review_records_privileged` — bool
- `inactive_license_status_available` — bool
- `retired_license_status_available` — bool
- `client_confidentiality_privilege` — bool
- `working_papers_ownership_by_licensee` — bool
- `single_act_evidence_sufficient` — bool
- `cpa_emeritus_or_retired_status_available` — bool
- `government_audit_cpe_requirement` — bool
- `ethics_cpe_hours_required` — int
- `hawaii_attest_work_supplement_required` — bool (Hawaii-specific peer-review nuance)
- `liability_privity_limitation` — bool
- `statute_of_limitations_for_accountant_negligence` — str
- `client_records_return_obligation` — bool

## Notes

- Categories (`advanced_tier`, `scope_inclusion`, `facility`, etc.) are
  hand-defined in `pipeline/extract/discover_schema.py` — the LLM picks one
  per discovered field, but the categories themselves are profession-agnostic
  buckets. Renaming a category (e.g. `advanced_tier` → `tiered_credentials`)
  is one-line in the enum but requires re-extraction to propagate.
- The two professions share the universal base verbatim (32 fields across
  LicensureRequirements + ScopeOfPractice). Profession-specific fields are
  fully orthogonal — none are shared between podiatry and CPA, which is what
  we'd expect.
- `wound_debridement_authorized`, `vaccination_authority`, `cosmetic_procedures_included`
  in podiatry are each supported by only one state in the corpus — the LLM
  surfaced them anyway because they're real distinguishing facts. The
  schema-discovery prompt allows single-state idiosyncrasies when the
  evidence is strong.
