# Field dictionary — podiatry

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-29** (latest commit to `podiatry` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Each example below is drawn from the first state that has a value for that field; the source state is shown in parentheses.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true (AK) |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "State Medical Board" (AK) |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "State Medical Board" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "shared_board" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development (AK) |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 19 (AL) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AL) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Certificate of graduation from a legally chartered school o (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "Board-approved school of podiatry" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "doctorate" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "board_approved" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "embedded_in_credential" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "minimum one year" (AR) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "podiatric residency" (AL) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Board examination for podiatry" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "The board shall call to its aid a podiatrist of known abili (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "state (in-house)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 3 (AR) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 1300 (ID) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 12 (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 2 (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["pain management and opioid use and addiction (minimum 2 ho (AK) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Must meet podiatry qualification requirements, submit proof (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "Connecticut Board of Examiners in Podiatry" (CT) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "advises and supervises examinations; approves schools with  (CT) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Board of Podiatric Examiners" (AL) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Podiatric Medical Association" (AL) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_license" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Secured a license through deceit, fraud, or intentional mis (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? | true (CO) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (DE) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.64.010" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definitions" (AL) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "the medical, mechanical, and surgical treatment of ailments (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["medical", "mechanical", "surgical"] (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. | "Podiatrists may use preparations, medicines, and drugs as a (AK) |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.64.380" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "scope definition" (AL) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `anatomical_scope_upper_boundary` | enum — one of: foot_only, foot_and_ankle, foot_ankle_and_leg_below_knee, foot_ankle_and_soft_tissue_to_tibial_tuberosity, foot_ankle_and_soft_tissue_to_myotendinous_junction_triceps_surae, foot_ankle_and_soft_tissue_to_distal_tibial_metaphyseal_flare, foot_ankle_and_soft_tissue_below_mid_calf, foot_ankle_and_tendons_inserting_into_foot | The upper anatomical boundary of the podiatrist's authorized scope of practice, which varies significantly across states. | "foot_ankle_and_tendons_inserting_into_foot" (AK) |
| `amputation_authorized` | enum — one of: toes_only, toes_and_parts_of_foot, transmetatarsal_and_below, chopart_joint_and_below, foot_entirety_excluded, forefoot_excluded, not_authorized | The level of amputation a podiatrist is authorized to perform, ranging from toes only to parts of the foot, with the entire foot typically excluded. | "chopart_joint_and_below" (AL) |
| `anesthesia_authority` | enum — one of: local_only, local_and_conscious_sedation, local_and_moderate_deep_sedation, general_permitted_with_physician_supervision, general_excluded | The types of anesthesia a podiatrist is authorized to administer, with local anesthesia universally permitted and general anesthesia typically excluded or restricted. | "general_permitted_with_physician_supervision" (AK) |
| `ankle_surgery_authorized` | boolean | Whether the state authorizes podiatrists to perform surgical treatment of the ankle, often subject to additional qualifications. | true (AL) |
| `ankle_surgery_residency_requirement` | enum — one of: 24_month_surgical_residency, 36_month_surgical_residency, 2_year_pre_2007_or_3_year_post_2007, board_certification_or_qualification_required, hospital_credentialing_required, board_certification_by_ABFAS | The specific residency length or certification required for a podiatrist to perform ankle surgery. | "36_month_surgical_residency" (AL) |
| `ankle_surgery_facility_requirement` | enum — one of: licensed_hospital_only, hospital_or_ambulatory_surgical_center, accredited_hospital_or_ASC, JCAHO_accredited_facility, multispecialty_ambulatory_surgical_facility | The type of facility in which ankle surgery must be performed by a podiatrist. | "accredited_hospital_or_ASC" (AR) |
| `systemic_disease_treatment_excluded` | boolean | Whether the state explicitly excludes treatment of systemic diseases from the podiatric scope of practice, except as manifested in the foot. | true (AL) |
| `systemic_disease_local_manifestations_included` | boolean | Whether the state explicitly includes treatment of local manifestations of systemic diseases as they appear on the foot or ankle. | true (AK) |
| `board_certification_body` | list | The recognized certifying body or bodies for advanced podiatric surgery, particularly for ankle surgery privileges. | ["American Board of Podiatric Surgery (ABPS)", "American Boa (CO) |
| `podiatric_assistant_authorized` | boolean | Whether the state explicitly authorizes podiatric medical assistants or podiatric assistants to assist under podiatrist supervision. | true (AK) |
| `podiatric_assistant_supervision_level` | enum — one of: direct_supervision_on_premises, indirect_supervision, general_supervision | The level of supervision required when a podiatrist delegates tasks to a podiatric assistant or medical assistant. | "direct_supervision_on_premises" (AR) |
| `xray_technician_certification_required` | boolean | Whether the state requires certification or training for unlicensed personnel operating X-ray equipment in a podiatrist's office. | true (CO) |
| `professional_liability_insurance_required` | boolean | Whether the state requires podiatrists to maintain professional liability (malpractice) insurance as a condition of licensure or renewal. | true (CO) |
| `telehealth_authorized` | boolean | Whether the state explicitly authorizes podiatrists to provide services via telehealth or telemedicine. | true (AR) |
| `opioid_prescribing_rules_required` | boolean | Whether the state has specific statutory requirements or mandates for the board to adopt rules governing opioid prescribing by podiatrists. | true (AK) |
| `controlled_substances_prescribing_ce_required` | boolean | Whether the state requires continuing education specifically related to controlled substances prescribing as part of license renewal. | true (AK) |
| `ankle_surgery_board_certification_timeline` | string | The time period within which a podiatrist who qualifies for ankle surgery must obtain board certification, where specified by statute. | "within six (6) years of May 24, 2000, or within six (6) yea (TN) |
| `total_ankle_replacement_authorized` | boolean | Whether the state explicitly addresses or authorizes total ankle replacement surgery by podiatrists. | false (AL) |
| `tibial_pilon_fracture_excluded` | boolean | Whether the state explicitly excludes treatment of tibial pilon fractures from the podiatric scope of practice. | true (CT) |
| `wound_debridement_authorized` | boolean | Whether the state explicitly authorizes podiatrists to perform wound debridement beyond the foot and ankle. | true (CA) |
| `vaccination_authority` | boolean | Whether the state explicitly authorizes podiatrists to administer vaccinations. | true (CA) |
| `physician_assistant_collaboration_authorized` | boolean | Whether the state explicitly authorizes podiatrists to collaborate with or supervise physician assistants. | true (CO) |
| `advanced_practice_nurse_collaboration_authorized` | boolean | Whether the state explicitly authorizes podiatrists to collaborate with advanced practice registered nurses. | true (IL) |
| `hospital_privileges_nondiscrimination` | boolean | Whether the state has a statutory provision prohibiting hospitals from discriminating against podiatrists in granting privileges based solely on their degree type. | true (RI) |
| `corrective_footwear_exemption` | boolean | Whether the state explicitly exempts the fitting, recommending, or sale of corrective shoes, arch supports, or similar appliances by retail dealers from the podiatry licensing requirement. | true (AL) |
| `clubfoot_surgery_restriction` | boolean | Whether the state explicitly restricts or excludes surgical correction of clubfoot from the podiatric scope of practice. | true (NC) |
| `ankle_surgery_standard_of_care_reference` | boolean | Whether the state statute explicitly requires podiatrists performing ankle surgery to meet the same standard of care as orthopedic surgeons. | true (TN) |
| `impaired_practitioner_program` | boolean | Whether the state has a statutory provision for a podiatrist health or rehabilitation program for impaired practitioners. | true (AK) |
| `electronic_prescribing_required` | boolean | Whether the state requires podiatrists to use electronic prescribing for medications, particularly controlled substances. | true (CO) |
| `cosmetic_procedures_included` | boolean | Whether the state explicitly includes cosmetic procedures of the foot, ankle, or leg within the podiatric scope of practice. | true (GA) |
| `preoperative_history_and_physical_authorized` | boolean | Whether the state explicitly authorizes podiatrists to perform preoperative history and physical examinations on their patients. | true (GA) |
| `assistant_surgeon_role_authorized` | boolean | Whether the state explicitly authorizes podiatrists to function as assistant surgeons in non-podiatric procedures. | true (CA) |
| `office_based_surgery_accreditation_required` | boolean | Whether the state requires that office-based surgeries performed by podiatrists be conducted in an accredited or licensed facility. | true (CA) |
| `minor_patient_chaperone_requirement` | boolean | Whether the state has a statutory requirement for a chaperone or third party to be present when a podiatrist treats a minor patient. | true (DE) |
| `nondiscrimination_in_public_programs` | boolean | Whether the state has a statutory provision ensuring recipients of public aid programs may choose podiatric care. | true (SC) |
| `noncompete_clause_restriction` | boolean | Whether the state has a statutory provision rendering noncompete clauses in podiatrist employment contracts unenforceable. |  |
| `scope__board_certification_body` | list | Scope checklist for 'board_certification_body'. Return EXACTLY one entry for each of these 6 items, using the item name verbatim: ['American Board of Foot and Ankle Surgery (ABFAS)', 'American Board of Podiatric Surgery (ABPS)', 'American Board of Podiatric Medicine (ABPM)', 'American Board of Multiple Specialties in Podiatry (ABMSP)', 'American Board of Orthopaedic Surgery (ABOS)', 'American Osteopathic Board of Orthopedic Surgery']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__board_certification_body[].item` | string |  | "American Board of Foot and Ankle Surgery (ABFAS)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__board_certification_body[].status` | string |  | "absent" (AK) |

