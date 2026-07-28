# Field dictionary — medicine

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-27** (latest commit to `medicine` records). Regenerate to refresh.

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
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "standalone_board" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development (AK) |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 19 (AL) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AL) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Certificate of graduation from a legally chartered medical  (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "Association of American Medical Colleges and the Council on (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "doctorate" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "national_accreditor" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "MD degree (allopathic)" (MD) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "doctorate" (MD) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "required_by_statute" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "One year (pre-1995 graduates) or two years (1995 and later  (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "residency or internship" (AK) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Board examination in subjects determined by the board" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "May be waived for license by credentials under AS 08.64.250 (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "state (in-house)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 3 (AL) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 500 (FL) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 30 (CO) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 2 (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["pain management and opioid use and addiction (minimum 2 ho (AK) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must meet education requirements, submit proof of (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "State Board of Medical Examiners" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "advisory \u2014 commission shall receive and consider but n (AL) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Board of Examiners for Osteopathic Physicians and  (AK) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "Association of American Medical Colleges; American Medical  (AK) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_license" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Securing a license through deceit, fraud, or intentional mi (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. | false (MA) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? | true (CA) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (AL) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.64.010" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "scope of practice definition" (AL) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "for a fee, donation or other consideration, to diagnose, tr (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["diagnose", "treat", "operate on", "prescribe for", "admini (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. | "Physicians may prescribe, dispense, and administer prescrip (AK) |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.64.380" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "practice definition" (AL) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `license_status_types` | list | The distinct license status categories a physician may hold beyond a standard active license, such as inactive, retired, volunteer, temporary, or administrative. | ["active", "inactive", "retired status", "temporary permit", (AK) |
| `foreign_medical_graduate_requirements` | string | Special additional requirements imposed on graduates of medical schools outside the United States or Canada, such as additional postgraduate training years, ECFMG certification, or separate examination standards. | "Foreign medical graduates must meet requirements of AS 08.6 (AK) |
| `postgraduate_training_years_required` | integer | The minimum number of years of postgraduate internship or residency training required before a license will be issued to a standard domestic medical school graduate. | 2 (AK) |
| `pain_management_education_required` | boolean | Whether the state requires applicants or licensees to complete specific education in pain management and opioid use and addiction as a condition of licensure or renewal. | true (AK) |
| `opioid_prescribing_limits` | string | Statutory limits on the quantity or duration of opioid prescriptions a licensee may issue, including any exceptions for chronic pain, cancer, or palliative care. | "Initial opioid prescription to an adult may not exceed a se (AK) |
| `controlled_substance_database_registration_required` | boolean | Whether licensees who hold a DEA registration number are required to register with or use the state's prescription drug monitoring program or controlled substance database. | true (AK) |
| `pain_management_clinic_registration_required` | boolean | Whether physicians providing pain management services must obtain a separate registration or license from the board in addition to their standard medical license. | true (AL) |
| `telehealth_prescribing_rules` | string | Specific statutory conditions under which a physician may prescribe drugs, including controlled substances, to patients seen only via telehealth rather than in person. | "The board may not impose disciplinary sanctions on a physic (AK) |
| `telemedicine_license_available` | boolean | Whether the state offers a distinct telemedicine or telehealth license category for out-of-state physicians who wish to treat in-state patients remotely without obtaining a full in-state license. | true (AR) |
| `interstate_medical_licensure_compact_member` | boolean | Whether the state has enacted the Interstate Medical Licensure Compact, enabling eligible physicians to obtain expedited licenses in multiple member states. | true (AL) |
| `physician_assistant_supervision_model` | enum — one of: direct supervision required, collaborative practice agreement, job description with board approval, facility credentialing system | The statutory model governing how physician assistants must relate to supervising or collaborating physicians, ranging from strict supervision to collaborative practice agreements. | "direct supervision required" (AK) |
| `physician_assistant_prescriptive_authority` | string | The scope of prescriptive authority granted to physician assistants, including which drug schedules they may prescribe and any conditions or limitations on that authority. | "Physician assistants may prescribe, dispense, or administer (AK) |
| `max_physician_assistants_per_supervising_physician` | integer | The maximum number of physician assistants or advanced practice registered nurses that a single supervising or delegating physician may oversee at one time under standard practice settings. | 2 (AR) |
| `malpractice_reporting_required` | boolean | Whether licensees are required by statute to report to the board the outcome of medical malpractice claims or civil actions in which damages are paid on their behalf. | true (AK) |
| `hospital_privilege_action_reporting_required` | boolean | Whether hospitals are required by statute to report to the medical board when they revoke, suspend, restrict, or refuse to grant hospital privileges to a licensed physician. | true (AK) |
| `impaired_physician_program_authorized` | boolean | Whether the state statute explicitly authorizes or requires the board to establish or contract with a program to identify, evaluate, and rehabilitate physicians impaired by substance use or mental illness. | true (AK) |
| `compelled_mental_physical_exam_authority` | boolean | Whether the board has statutory authority to order a licensee to submit to a mental or physical examination when there is probable cause to believe the licensee cannot practice safely. | true (AK) |
| `administrative_medicine_license_available` | boolean | Whether the state offers a distinct administrative medicine license for physicians who wish to perform management or advisory functions without engaging in direct patient care. | true (AR) |
| `locum_tenens_permit_available` | boolean | Whether the state offers a specific temporary permit for physicians practicing as locum tenens substitutes for licensed in-state physicians. | true (AK) |
| `sexual_misconduct_training_required` | boolean | Whether the state requires physicians or medical school students to complete specific training on professional boundaries and physician sexual misconduct as a condition of licensure or renewal. | false (FL) |
| `investigational_drug_protection` | boolean | Whether the state statute explicitly protects physicians from disciplinary action for prescribing or administering investigational drugs or unapproved treatments to terminally ill patients who have given informed consent. | true (AK) |
| `scope__license_status_types` | list | Scope checklist for 'license_status_types'. Return EXACTLY one entry for each of these 14 items, using the item name verbatim: ['Inactive License', 'Retired License', 'Temporary License / Permit', 'Restricted License', 'Probationary License', 'Suspended License', 'Revoked License', 'Surrendered License', 'Academic License', 'Volunteer / Charitable License', 'Expedited / Interstate Compact License', 'Intern / Resident Permit', 'Graduate Registered Physician License', 'Locum Tenens Permit']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_status_types[].item` | string |  | "Inactive License" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_status_types[].status` | string |  | "present" (AK) |

