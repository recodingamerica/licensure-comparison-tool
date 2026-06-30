# Field dictionary — medicine

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from medicine/AK.

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
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Board of Examiners for Osteopathic Physicians and  |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "Association of American Medical Colleges; American Medical  |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "for a fee, donation or other consideration, to diagnose, tr |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["diagnose", "treat", "operate on", "prescribe for", "admini |
| `drug_authority` | string |  | "Licensees may prescribe, dispense, and administer drugs inc |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `license_status_types` | list | The distinct license status categories a physician may hold beyond a standard active license, such as inactive, retired, volunteer, temporary, or administrative. | ["active", "inactive", "retired status", "temporary permit", |
| `foreign_medical_graduate_requirements` | string | Special additional requirements imposed on graduates of medical schools outside the United States or Canada, such as additional postgraduate training years, ECFMG certification, or separate examination standards. | "Foreign medical graduates must meet requirements of AS 08.6 |
| `postgraduate_training_years_required` | integer | The minimum number of years of postgraduate internship or residency training required before a license will be issued to a standard domestic medical school graduate. | 2 |
| `pain_management_education_required` | boolean | Whether the state requires applicants or licensees to complete specific education in pain management and opioid use and addiction as a condition of licensure or renewal. | true |
| `opioid_prescribing_limits` | string | Statutory limits on the quantity or duration of opioid prescriptions a licensee may issue, including any exceptions for chronic pain, cancer, or palliative care. | "Initial opioid prescription may not exceed a seven-day supp |
| `controlled_substance_database_registration_required` | boolean | Whether licensees who hold a DEA registration number are required to register with or use the state's prescription drug monitoring program or controlled substance database. | true |
| `pain_management_clinic_registration_required` | boolean | Whether physicians providing pain management services must obtain a separate registration or license from the board in addition to their standard medical license. |  |
| `telehealth_prescribing_rules` | string | Specific statutory conditions under which a physician may prescribe drugs, including controlled substances, to patients seen only via telehealth rather than in person. | "Board may not impose disciplinary sanctions for prescribing |
| `telemedicine_license_available` | boolean | Whether the state offers a distinct telemedicine or telehealth license category for out-of-state physicians who wish to treat in-state patients remotely without obtaining a full in-state license. |  |
| `interstate_medical_licensure_compact_member` | boolean | Whether the state has enacted the Interstate Medical Licensure Compact, enabling eligible physicians to obtain expedited licenses in multiple member states. |  |
| `physician_assistant_supervision_model` | enum — one of: direct supervision required, collaborative practice agreement, job description with board approval, facility credentialing system | The statutory model governing how physician assistants must relate to supervising or collaborating physicians, ranging from strict supervision to collaborative practice agreements. | "direct supervision required" |
| `physician_assistant_prescriptive_authority` | string | The scope of prescriptive authority granted to physician assistants, including which drug schedules they may prescribe and any conditions or limitations on that authority. | "Physician assistants may prescribe drugs (including control |
| `max_physician_assistants_per_supervising_physician` | integer | The maximum number of physician assistants or advanced practice registered nurses that a single supervising or delegating physician may oversee at one time under standard practice settings. |  |
| `malpractice_reporting_required` | boolean | Whether licensees are required by statute to report to the board the outcome of medical malpractice claims or civil actions in which damages are paid on their behalf. | true |
| `hospital_privilege_action_reporting_required` | boolean | Whether hospitals are required by statute to report to the medical board when they revoke, suspend, restrict, or refuse to grant hospital privileges to a licensed physician. | true |
| `impaired_physician_program_authorized` | boolean | Whether the state statute explicitly authorizes or requires the board to establish or contract with a program to identify, evaluate, and rehabilitate physicians impaired by substance use or mental illness. | true |
| `compelled_mental_physical_exam_authority` | boolean | Whether the board has statutory authority to order a licensee to submit to a mental or physical examination when there is probable cause to believe the licensee cannot practice safely. | true |
| `administrative_medicine_license_available` | boolean | Whether the state offers a distinct administrative medicine license for physicians who wish to perform management or advisory functions without engaging in direct patient care. |  |
| `locum_tenens_permit_available` | boolean | Whether the state offers a specific temporary permit for physicians practicing as locum tenens substitutes for licensed in-state physicians. | true |
| `sexual_misconduct_training_required` | boolean | Whether the state requires physicians or medical school students to complete specific training on professional boundaries and physician sexual misconduct as a condition of licensure or renewal. |  |
| `investigational_drug_protection` | boolean | Whether the state statute explicitly protects physicians from disciplinary action for prescribing or administering investigational drugs or unapproved treatments to terminally ill patients who have given informed consent. | true |

