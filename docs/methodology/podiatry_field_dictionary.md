# Field dictionary — podiatry

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from podiatry/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "State Medical Board" |
| `regulatory_authority` | RegulatoryAuthority | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| `age_minimum` | integer |  |  |
| `moral_character_required` | boolean |  |  |
| `education` | EducationRequirement |  |  |
| `post_degree_experience` | PostDegreeExperience | Residency / supervised practice / apprenticeship — name varies, structure doesn't. |  |
| `exams` | list |  |  |
| `renewal` | Renewal |  |  |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. |  |
| `continuing_education` | ContinuingEducation |  |  |
| `reciprocity` | Reciprocity |  |  |
| `advisory_board` | AdvisoryBoard | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. |  |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. |  |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| `alternative_regulation` | AlternativeRegulation | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| `citations` | list |  |  |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope and any title/scope protection._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "the medical, mechanical, and surgical treatment of ailments |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["medical", "mechanical", "surgical"] |
| `drug_authority` | string |  | "Use of preparations, medicines, and drugs as are necessary  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `anatomical_scope_upper_boundary` | enum — one of: foot_only, foot_and_ankle, foot_ankle_and_leg_below_knee, foot_ankle_and_soft_tissue_to_tibial_tuberosity, foot_ankle_and_soft_tissue_to_myotendinous_junction_triceps_surae, foot_ankle_and_soft_tissue_to_distal_tibial_metaphyseal_flare, foot_ankle_and_soft_tissue_below_mid_calf, foot_ankle_and_tendons_inserting_into_foot | The upper anatomical boundary of the podiatrist's authorized scope of practice, which varies significantly across states. | "foot_ankle_and_tendons_inserting_into_foot" |
| `amputation_authorized` | enum — one of: toes_only, toes_and_parts_of_foot, transmetatarsal_and_below, chopart_joint_and_below, foot_entirety_excluded, forefoot_excluded, not_authorized | The level of amputation a podiatrist is authorized to perform, ranging from toes only to parts of the foot, with the entire foot typically excluded. |  |
| `anesthesia_authority` | enum — one of: local_only, local_and_conscious_sedation, local_and_moderate_deep_sedation, general_permitted_with_physician_supervision, general_excluded | The types of anesthesia a podiatrist is authorized to administer, with local anesthesia universally permitted and general anesthesia typically excluded or restricted. | "general_permitted_with_physician_supervision" |
| `ankle_surgery_authorized` | boolean | Whether the state authorizes podiatrists to perform surgical treatment of the ankle, often subject to additional qualifications. |  |
| `ankle_surgery_residency_requirement` | enum — one of: 24_month_surgical_residency, 36_month_surgical_residency, 2_year_pre_2007_or_3_year_post_2007, board_certification_or_qualification_required, hospital_credentialing_required, board_certification_by_ABFAS | The specific residency length or certification required for a podiatrist to perform ankle surgery. |  |
| `ankle_surgery_facility_requirement` | enum — one of: licensed_hospital_only, hospital_or_ambulatory_surgical_center, accredited_hospital_or_ASC, JCAHO_accredited_facility, multispecialty_ambulatory_surgical_facility | The type of facility in which ankle surgery must be performed by a podiatrist. |  |
| `systemic_disease_treatment_excluded` | boolean | Whether the state explicitly excludes treatment of systemic diseases from the podiatric scope of practice, except as manifested in the foot. | true |
| `systemic_disease_local_manifestations_included` | boolean | Whether the state explicitly includes treatment of local manifestations of systemic diseases as they appear on the foot or ankle. | true |
| `board_certification_body` | list | The recognized certifying body or bodies for advanced podiatric surgery, particularly for ankle surgery privileges. |  |
| `podiatric_assistant_authorized` | boolean | Whether the state explicitly authorizes podiatric medical assistants or podiatric assistants to assist under podiatrist supervision. | true |
| `podiatric_assistant_supervision_level` | enum — one of: direct_supervision_on_premises, indirect_supervision, general_supervision | The level of supervision required when a podiatrist delegates tasks to a podiatric assistant or medical assistant. |  |
| `xray_technician_certification_required` | boolean | Whether the state requires certification or training for unlicensed personnel operating X-ray equipment in a podiatrist's office. |  |
| `professional_liability_insurance_required` | boolean | Whether the state requires podiatrists to maintain professional liability (malpractice) insurance as a condition of licensure or renewal. |  |
| `telehealth_authorized` | boolean | Whether the state explicitly authorizes podiatrists to provide services via telehealth or telemedicine. |  |
| `opioid_prescribing_rules_required` | boolean | Whether the state has specific statutory requirements or mandates for the board to adopt rules governing opioid prescribing by podiatrists. | true |
| `controlled_substances_prescribing_ce_required` | boolean | Whether the state requires continuing education specifically related to controlled substances prescribing as part of license renewal. | true |
| `ankle_surgery_board_certification_timeline` | string | The time period within which a podiatrist who qualifies for ankle surgery must obtain board certification, where specified by statute. |  |
| `total_ankle_replacement_authorized` | boolean | Whether the state explicitly addresses or authorizes total ankle replacement surgery by podiatrists. |  |
| `tibial_pilon_fracture_excluded` | boolean | Whether the state explicitly excludes treatment of tibial pilon fractures from the podiatric scope of practice. |  |
| `wound_debridement_authorized` | boolean | Whether the state explicitly authorizes podiatrists to perform wound debridement beyond the foot and ankle. |  |
| `vaccination_authority` | boolean | Whether the state explicitly authorizes podiatrists to administer vaccinations. |  |
| `physician_assistant_collaboration_authorized` | boolean | Whether the state explicitly authorizes podiatrists to collaborate with or supervise physician assistants. | true |
| `advanced_practice_nurse_collaboration_authorized` | boolean | Whether the state explicitly authorizes podiatrists to collaborate with advanced practice registered nurses. |  |
| `hospital_privileges_nondiscrimination` | boolean | Whether the state has a statutory provision prohibiting hospitals from discriminating against podiatrists in granting privileges based solely on their degree type. |  |
| `corrective_footwear_exemption` | boolean | Whether the state explicitly exempts the fitting, recommending, or sale of corrective shoes, arch supports, or similar appliances by retail dealers from the podiatry licensing requirement. |  |
| `clubfoot_surgery_restriction` | boolean | Whether the state explicitly restricts or excludes surgical correction of clubfoot from the podiatric scope of practice. |  |
| `ankle_surgery_standard_of_care_reference` | boolean | Whether the state statute explicitly requires podiatrists performing ankle surgery to meet the same standard of care as orthopedic surgeons. |  |
| `impaired_practitioner_program` | boolean | Whether the state has a statutory provision for a podiatrist health or rehabilitation program for impaired practitioners. | true |
| `electronic_prescribing_required` | boolean | Whether the state requires podiatrists to use electronic prescribing for medications, particularly controlled substances. |  |
| `cosmetic_procedures_included` | boolean | Whether the state explicitly includes cosmetic procedures of the foot, ankle, or leg within the podiatric scope of practice. |  |
| `preoperative_history_and_physical_authorized` | boolean | Whether the state explicitly authorizes podiatrists to perform preoperative history and physical examinations on their patients. |  |
| `assistant_surgeon_role_authorized` | boolean | Whether the state explicitly authorizes podiatrists to function as assistant surgeons in non-podiatric procedures. |  |
| `office_based_surgery_accreditation_required` | boolean | Whether the state requires that office-based surgeries performed by podiatrists be conducted in an accredited or licensed facility. |  |
| `minor_patient_chaperone_requirement` | boolean | Whether the state has a statutory requirement for a chaperone or third party to be present when a podiatrist treats a minor patient. |  |
| `nondiscrimination_in_public_programs` | boolean | Whether the state has a statutory provision ensuring recipients of public aid programs may choose podiatric care. |  |
| `noncompete_clause_restriction` | boolean | Whether the state has a statutory provision rendering noncompete clauses in podiatrist employment contracts unenforceable. |  |

