# Field dictionary — nursing

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-29** (latest commit to `nursing` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Each example below is drawn from the first state that has a value for that field; the source state is shown in parentheses.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true (AK) |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "Board of Nursing" (AK) |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "Board of Nursing" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "standalone_board" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development (AK) |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 16 (AZ) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AL) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Registered nurse education program accredited by a national (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "national nursing accrediting body" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "associate" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "national_accreditor" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "Registered Nurse (RN)" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "high_school" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. | "1998-10-01" (FL) |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "none" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "minimum of three full-time equivalent years of practice or  (CA) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "transition to practice (nurse practitioner)" (CA) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Registered Nursing Licensing Examination" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Prescribed by the board for registered nurse applicants" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "prescribed by the board" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. |  |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 100 (ID) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 2 (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 2 (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["pain management and opioid use and addiction"] (AK) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must be currently licensed in another state; must (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "Prescriptive Authority Advisory Committee" (AR) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "Advisory only; assists the board in implementing provisions (AR) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National certifying body recognized by the Arkansas State B (AR) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "Alabama State Nurses Association" (AL) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_license" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Obtained or attempted to obtain a license by fraud or decei (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. | false (MA) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? | true (CA) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (IL) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.68.010" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "board_composition" (AK) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "practice of registered nursing means the performance for co (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["assessment of problems, counseling, and teaching", "admini (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. | "Advanced practice registered nurses are certified to perfor (AK) |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.68.850" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definitions" (AK) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `license_tiers` | list | The distinct license or certification tiers recognized in the state, each with its own scope and requirements. | ["Registered Nurse (RN)", "Licensed Practical Nurse (LPN)",  (AK) |
| `aprn_role_categories` | list | The recognized advanced practice registered nurse role categories, each with distinct scope and certification requirements. | ["Certified Registered Nurse Anesthetist", "Certified Nurse  (AK) |
| `lpn_supervision_requirements` | list | The categories of licensed professionals under whose supervision a practical or vocational nurse must work. | ["Registered Nurse", "Advanced Practice Registered Nurse", " (AK) |
| `collaborative_practice_agreement_required` | boolean | Whether certain advanced practice nurses (typically NPs and CNMs) must have a written collaborative practice agreement with a physician to practice or prescribe. | true (AL) |
| `full_independent_practice_available` | boolean | Whether the state provides a pathway for certain APRNs to practice fully independently without a physician collaboration or supervision requirement. | false (AL) |
| `full_independent_practice_experience_hours_required` | integer | Number of supervised or collaborative practice hours required before an APRN may qualify for full independent practice authority. | 6240 (AR) |
| `prescriptive_authority_certificate_required` | boolean | Whether APRNs must obtain a separate board-issued certificate or number to prescribe or furnish drugs, beyond the basic APRN license. | true (AL) |
| `controlled_substance_schedule_authority` | list | The DEA controlled substance schedules that APRNs are authorized to prescribe, which may differ by role or state. | ["Schedule II (limited: opioids for 5-day supply or less, or (AR) |
| `opioid_prescribing_limits` | string | Statutory limits on opioid prescriptions issued by APRNs, including maximum day-supply and documentation requirements. | "An APRN may not issue an initial prescription for an opioid (AK) |
| `dea_registration_required` | boolean | Whether APRNs authorized to prescribe controlled substances must register with the federal DEA. | false (AK) |
| `controlled_substance_database_registration_required` | boolean | Whether APRNs with DEA numbers must register with the state's controlled substance prescription monitoring database. | true (AK) |
| `nurse_aide_registry_maintained` | boolean | Whether the state board maintains a registry of certified nurse aides, including disciplinary findings. | true (AK) |
| `medication_assistant_certification_available` | boolean | Whether the state has a separate certification category for medication assistants or medication assistive persons who may administer certain medications under nurse supervision. | true (AL) |
| `delegation_to_unlicensed_personnel_authorized` | boolean | Whether licensed nurses are explicitly authorized by statute to delegate nursing tasks to unlicensed assistive personnel under defined conditions. | true (AK) |
| `employer_mandatory_reporting_required` | boolean | Whether employers of nurses are legally required to report to the board when a nurse is discharged, suspended, or resigns under circumstances related to grounds for discipline. | true (AK) |
| `whistleblower_protection_for_delegation_refusal` | boolean | Whether the state provides explicit statutory protection for nurses who refuse to perform improperly delegated tasks. | true (AK) |
| `nurse_licensure_compact_member` | boolean | Whether the state has enacted the Enhanced Nurse Licensure Compact (eNLC), allowing multistate licensure privileges. | true (AL) |
| `multistate_license_option_available` | boolean | Whether applicants may choose between a single-state license and a multistate license when applying for licensure. | true (AL) |
| `impaired_nurse_alternative_program_available` | boolean | Whether the state has a voluntary non-disciplinary alternative or diversion program for nurses impaired by substance use or mental health conditions. | true (AK) |
| `rn_death_pronouncement_authorized` | boolean | Whether registered nurses are explicitly authorized by statute to make a determination and pronouncement of death under specified conditions. | true (AK) |
| `public_health_nurse_certification_available` | boolean | Whether the state has a separate board-issued public health nurse certification with title protection. | true (CA) |
| `telehealth_prescribing_rules` | string | Statutory rules governing when an APRN may prescribe or treat without a prior in-person physical examination, including telehealth or internet-based restrictions. | "An APRN may not prescribe, dispense, or administer a prescr (AK) |
| `nurse_practitioner_transition_to_practice_hours` | integer | Number of supervised or collaborative practice hours a nurse practitioner must complete before qualifying for independent or expanded practice authority. | 6240 (AR) |
| `crna_physician_supervision_model` | enum — one of: direction and presence required, direction without required presence, consultation model, coordination model | The statutory model governing the relationship between a CRNA and a physician during anesthesia administration. | "coordination model" (AL) |
| `cnm_out_of_hospital_birth_authorized` | boolean | Whether certified nurse midwives are explicitly authorized to attend births in out-of-hospital settings. | true (AR) |
| `aprn_formulary_or_protocol_required` | boolean | Whether APRNs who prescribe must do so pursuant to a board-approved formulary or written protocol specifying permissible drugs. | true (AL) |
| `nursing_education_program_clinical_hours_minimum` | integer | Minimum number of direct patient care clinical hours required in an approved prelicensure nursing education program. | 500 (CA) |
| `implicit_bias_training_required_in_curriculum` | boolean | Whether approved nursing education programs are required to include implicit bias training as part of graduation requirements. | true (CA) |
| `military_education_credit_required` | boolean | Whether approved nursing schools are required to grant credit toward licensure for military medical education and experience. | true (AK) |
| `scope__license_tiers` | list | Scope checklist for 'license_tiers'. Return EXACTLY one entry for each of these 13 items, using the item name verbatim: ['Registered Nurse (RN)', 'Licensed Practical Nurse (LPN)', 'Advanced Practice Registered Nurse (APRN)', 'Certified Registered Nurse Anesthetist (CRNA)', 'Certified Nurse Practitioner (CNP/CRNP/NP)', 'Certified Nurse Midwife (CNM)', 'Clinical Nurse Specialist (CNS)', 'Certified Nurse Aide (CNA)', 'Certified Medication Assistant', 'Full Independent Practice Authority Certificate', 'Nursing Home Administrator License', 'Multistate License (Nurse Licensure Compact)', 'Temporary Permit to Practice Nursing']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_tiers[].item` | string |  | "Registered Nurse (RN)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_tiers[].status` | string |  | "present" (AK) |
| `scope__aprn_role_categories` | list | Scope checklist for 'aprn_role_categories'. Return EXACTLY one entry for each of these 4 items, using the item name verbatim: ['Certified Nurse Practitioner', 'Certified Registered Nurse Anesthetist', 'Certified Nurse Midwife', 'Clinical Nurse Specialist']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__aprn_role_categories[].item` | string |  | "Certified Nurse Practitioner" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__aprn_role_categories[].status` | string |  | "present" (AK) |
| `scope__lpn_supervision_requirements` | list | Scope checklist for 'lpn_supervision_requirements'. Return EXACTLY one entry for each of these 6 items, using the item name verbatim: ['Registered Nurse', 'Advanced Practice Registered Nurse', 'Physician', 'Physician Assistant', 'Dentist', 'Podiatrist']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__lpn_supervision_requirements[].item` | string |  | "Registered Nurse" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__lpn_supervision_requirements[].status` | string |  | "present" (AK) |
| `scope__controlled_substance_schedule_authority` | list | Scope checklist for 'controlled_substance_schedule_authority'. Return EXACTLY one entry for each of these 4 items, using the item name verbatim: ['Schedule II controlled substances', 'Schedule III controlled substances', 'Schedule IV controlled substances', 'Schedule V controlled substances']. For EACH item, status is `authorized` if the statute permits it, `prohibited` if the statute forbids it (including via a broad exclusion/prohibition that covers it), or `not_addressed` if the statute is genuinely silent. Quote verbatim for `authorized` and `prohibited`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__controlled_substance_schedule_authority[].item` | string |  | "Schedule II controlled substances" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__controlled_substance_schedule_authority[].status` | string |  | "not_addressed" (AK) |

