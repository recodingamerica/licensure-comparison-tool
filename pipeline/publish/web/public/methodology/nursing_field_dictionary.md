# Field dictionary — nursing

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-05** (latest commit to `nursing` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from nursing/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "Board of Nursing" |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "Board of Nursing" |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "standalone_board" |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. |  |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. |  |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Completion of an accredited registered nurse, practical nur |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "national nursing accrediting body" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "associate" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "national_accreditor" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "registered nurse" |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "associate" |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "none" |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' |  |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Registered Nursing or Practical Nursing Licensing Examinati |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Applies to RN and LPN applicants" |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. |  |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. |  |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["pain management and opioid use and addiction (minimum 2 ho |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must be licensed in another state, meet AK qualif |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. |  |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. |  |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. |  |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_license" |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Obtained or attempted to obtain a nursing license by fraud  |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? |  |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.68.010" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "board creation" |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "practice of registered nursing means the performance for co |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["assessment of problems, counseling, and teaching clients t |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. | "Advanced practice registered nurses may prescribe and dispe |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.68.850" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definitions/scope" |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `license_tiers` | list | The distinct license or certification tiers recognized in the state, each with its own scope and requirements. | ["licensed practical nurse (LPN)", "registered nurse (RN)",  |
| `aprn_role_categories` | list | The recognized advanced practice registered nurse role categories, each with distinct scope and certification requirements. | ["certified registered nurse anesthetist (CRNA)", "certified |
| `lpn_supervision_requirements` | list | The categories of licensed professionals under whose supervision a practical or vocational nurse must work. | ["licensed registered nurse", "advanced practice registered  |
| `collaborative_practice_agreement_required` | boolean | Whether certain advanced practice nurses (typically NPs and CNMs) must have a written collaborative practice agreement with a physician to practice or prescribe. |  |
| `full_independent_practice_available` | boolean | Whether the state provides a pathway for certain APRNs to practice fully independently without a physician collaboration or supervision requirement. |  |
| `full_independent_practice_experience_hours_required` | integer | Number of supervised or collaborative practice hours required before an APRN may qualify for full independent practice authority. |  |
| `prescriptive_authority_certificate_required` | boolean | Whether APRNs must obtain a separate board-issued certificate or number to prescribe or furnish drugs, beyond the basic APRN license. |  |
| `controlled_substance_schedule_authority` | list | The DEA controlled substance schedules that APRNs are authorized to prescribe, which may differ by role or state. |  |
| `opioid_prescribing_limits` | string | Statutory limits on opioid prescriptions issued by APRNs, including maximum day-supply and documentation requirements. | "An advanced practice registered nurse may not issue an init |
| `dea_registration_required` | boolean | Whether APRNs authorized to prescribe controlled substances must register with the federal DEA. | true |
| `controlled_substance_database_registration_required` | boolean | Whether APRNs with DEA numbers must register with the state's controlled substance prescription monitoring database. | true |
| `nurse_aide_registry_maintained` | boolean | Whether the state board maintains a registry of certified nurse aides, including disciplinary findings. | true |
| `medication_assistant_certification_available` | boolean | Whether the state has a separate certification category for medication assistants or medication assistive persons who may administer certain medications under nurse supervision. |  |
| `delegation_to_unlicensed_personnel_authorized` | boolean | Whether licensed nurses are explicitly authorized by statute to delegate nursing tasks to unlicensed assistive personnel under defined conditions. | true |
| `employer_mandatory_reporting_required` | boolean | Whether employers of nurses are legally required to report to the board when a nurse is discharged, suspended, or resigns under circumstances related to grounds for discipline. | true |
| `whistleblower_protection_for_delegation_refusal` | boolean | Whether the state provides explicit statutory protection for nurses who refuse to perform improperly delegated tasks. | true |
| `nurse_licensure_compact_member` | boolean | Whether the state has enacted the Enhanced Nurse Licensure Compact (eNLC), allowing multistate licensure privileges. |  |
| `multistate_license_option_available` | boolean | Whether applicants may choose between a single-state license and a multistate license when applying for licensure. |  |
| `impaired_nurse_alternative_program_available` | boolean | Whether the state has a voluntary non-disciplinary alternative or diversion program for nurses impaired by substance use or mental health conditions. | true |
| `rn_death_pronouncement_authorized` | boolean | Whether registered nurses are explicitly authorized by statute to make a determination and pronouncement of death under specified conditions. | true |
| `public_health_nurse_certification_available` | boolean | Whether the state has a separate board-issued public health nurse certification with title protection. |  |
| `telehealth_prescribing_rules` | string | Statutory rules governing when an APRN may prescribe or treat without a prior in-person physical examination, including telehealth or internet-based restrictions. | "An APRN may render a diagnosis, provide treatment, or presc |
| `nurse_practitioner_transition_to_practice_hours` | integer | Number of supervised or collaborative practice hours a nurse practitioner must complete before qualifying for independent or expanded practice authority. |  |
| `crna_physician_supervision_model` | enum — one of: direction and presence required, direction without required presence, consultation model, coordination model | The statutory model governing the relationship between a CRNA and a physician during anesthesia administration. |  |
| `cnm_out_of_hospital_birth_authorized` | boolean | Whether certified nurse midwives are explicitly authorized to attend births in out-of-hospital settings. |  |
| `aprn_formulary_or_protocol_required` | boolean | Whether APRNs who prescribe must do so pursuant to a board-approved formulary or written protocol specifying permissible drugs. |  |
| `nursing_education_program_clinical_hours_minimum` | integer | Minimum number of direct patient care clinical hours required in an approved prelicensure nursing education program. |  |
| `implicit_bias_training_required_in_curriculum` | boolean | Whether approved nursing education programs are required to include implicit bias training as part of graduation requirements. |  |
| `military_education_credit_required` | boolean | Whether approved nursing schools are required to grant credit toward licensure for military medical education and experience. | true |

