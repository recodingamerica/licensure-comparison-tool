# Field dictionary — nursing

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from nursing/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "Board of Nursing" |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "practice of registered nursing means the performance for co |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["assessment of problems, counseling, and teaching", "admini |
| `drug_authority` | string |  | "APRNs may prescribe and dispense medical, therapeutic, or c |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `license_tiers` | list | The distinct license or certification tiers recognized in the state, each with its own scope and requirements. | ["Registered Nurse (RN)", "Licensed Practical Nurse (LPN)",  |
| `aprn_role_categories` | list | The recognized advanced practice registered nurse role categories, each with distinct scope and certification requirements. | ["certified registered nurse anesthetist (CRNA)", "certified |
| `lpn_supervision_requirements` | list | The categories of licensed professionals under whose supervision a practical or vocational nurse must work. | ["licensed registered nurse", "advanced practice registered  |
| `collaborative_practice_agreement_required` | boolean | Whether certain advanced practice nurses (typically NPs and CNMs) must have a written collaborative practice agreement with a physician to practice or prescribe. |  |
| `full_independent_practice_available` | boolean | Whether the state provides a pathway for certain APRNs to practice fully independently without a physician collaboration or supervision requirement. |  |
| `full_independent_practice_experience_hours_required` | integer | Number of supervised or collaborative practice hours required before an APRN may qualify for full independent practice authority. |  |
| `prescriptive_authority_certificate_required` | boolean | Whether APRNs must obtain a separate board-issued certificate or number to prescribe or furnish drugs, beyond the basic APRN license. |  |
| `controlled_substance_schedule_authority` | list | The DEA controlled substance schedules that APRNs are authorized to prescribe, which may differ by role or state. |  |
| `opioid_prescribing_limits` | string | Statutory limits on opioid prescriptions issued by APRNs, including maximum day-supply and documentation requirements. | "An APRN may not issue an initial opioid prescription exceed |
| `dea_registration_required` | boolean | Whether APRNs authorized to prescribe controlled substances must register with the federal DEA. |  |
| `controlled_substance_database_registration_required` | boolean | Whether APRNs with DEA numbers must register with the state's controlled substance prescription monitoring database. | true |
| `nurse_aide_registry_maintained` | boolean | Whether the state board maintains a registry of certified nurse aides, including disciplinary findings. | true |
| `medication_assistant_certification_available` | boolean | Whether the state has a separate certification category for medication assistants or medication assistive persons who may administer certain medications under nurse supervision. |  |
| `delegation_to_unlicensed_personnel_authorized` | boolean | Whether licensed nurses are explicitly authorized by statute to delegate nursing tasks to unlicensed assistive personnel under defined conditions. | true |
| `employer_mandatory_reporting_required` | boolean | Whether employers of nurses are legally required to report to the board when a nurse is discharged, suspended, or resigns under circumstances related to grounds for discipline. | true |
| `whistleblower_protection_for_delegation_refusal` | boolean | Whether the state provides explicit statutory protection for nurses who refuse to perform improperly delegated tasks. | true |
| `nurse_licensure_compact_member` | boolean | Whether the state has enacted the Enhanced Nurse Licensure Compact (eNLC), allowing multistate licensure privileges. |  |
| `multistate_license_option_available` | boolean | Whether applicants may choose between a single-state license and a multistate license when applying for licensure. |  |
| `impaired_nurse_alternative_program_available` | boolean | Whether the state has a voluntary non-disciplinary alternative or diversion program for nurses impaired by substance use or mental health conditions. |  |
| `rn_death_pronouncement_authorized` | boolean | Whether registered nurses are explicitly authorized by statute to make a determination and pronouncement of death under specified conditions. | true |
| `public_health_nurse_certification_available` | boolean | Whether the state has a separate board-issued public health nurse certification with title protection. |  |
| `telehealth_prescribing_rules` | string | Statutory rules governing when an APRN may prescribe or treat without a prior in-person physical examination, including telehealth or internet-based restrictions. | "An APRN may prescribe without a physical examination for no |
| `nurse_practitioner_transition_to_practice_hours` | integer | Number of supervised or collaborative practice hours a nurse practitioner must complete before qualifying for independent or expanded practice authority. |  |
| `crna_physician_supervision_model` | enum — one of: direction and presence required, direction without required presence, consultation model, coordination model | The statutory model governing the relationship between a CRNA and a physician during anesthesia administration. |  |
| `cnm_out_of_hospital_birth_authorized` | boolean | Whether certified nurse midwives are explicitly authorized to attend births in out-of-hospital settings. |  |
| `aprn_formulary_or_protocol_required` | boolean | Whether APRNs who prescribe must do so pursuant to a board-approved formulary or written protocol specifying permissible drugs. |  |
| `nursing_education_program_clinical_hours_minimum` | integer | Minimum number of direct patient care clinical hours required in an approved prelicensure nursing education program. |  |
| `implicit_bias_training_required_in_curriculum` | boolean | Whether approved nursing education programs are required to include implicit bias training as part of graduation requirements. |  |
| `military_education_credit_required` | boolean | Whether approved nursing schools are required to grant credit toward licensure for military medical education and experience. | true |

