# Field dictionary — public_accountancy

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-06-29** (latest commit to `public_accountancy` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from public_accountancy/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "Board of Public Accountancy" |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "Board of Public Accountancy" |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "standalone_board" |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. |  |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "baccalaureate degree or its equivalent conferred by a colle |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "bachelor" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "board_approved" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "required_by_statute" |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "two years" |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "accounting experience" |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Uniform Certified Public Accountant Examination" |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Administered by the American Institute of Certified Public  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "national (AICPA)" |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. |  |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. |  |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 2 |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] |  |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must have passed the Uniform CPA Examination to r |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. |  |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. |  |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Institute of Certified Public Accountants" |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_license" |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Fraud or deceit in obtaining a license or permit" |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.04.005" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "purpose" |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "the offering to perform or the performance as a person hold |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["preparing financial statements", "issuing reports", "furni |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. |  |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.04.680" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definitions" |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `attest_services_types` | list | Enumerated types of attest services that constitute the regulated scope of practice, typically defined by reference to AICPA/PCAOB standards. | ["audit or other engagement established by Statements on Aud |
| `compilation_services_authorized` | boolean | Whether compilation services (presenting financial statements as management's representation without assurance) are separately defined and regulated as a distinct service type. | true |
| `education_semester_hours_required` | integer | Total semester hours of college education required for initial CPA licensure (typically 150 hours post-2000). | 150 |
| `exam_sit_hours_minimum` | integer | Minimum semester hours of college education required before a candidate may sit for the CPA examination (often 120 hours, less than the full 150 required for licensure). |  |
| `ethics_exam_required` | boolean | Whether a separate ethics examination (e.g., AICPA ethics exam or state-specific ethics exam) is required as a condition of initial licensure. |  |
| `practice_privilege_no_notice_required` | boolean | Whether out-of-state CPAs with substantially equivalent qualifications may practice in the state without providing notice, paying a fee, or making any submission to the board. | true |
| `practice_privilege_consent_conditions` | list | Conditions to which an out-of-state CPA exercising practice privileges must consent, including board jurisdiction, compliance with state law, cessation if license lapses, and appointment of home-state board as agent for service of process. | ["consent to the personal and subject matter jurisdiction an |
| `attest_services_require_firm_permit` | boolean | Whether individuals with practice privileges or individual licensees must perform certain attest services (audits, PCAOB engagements) only through a firm holding a valid permit. | true |
| `firm_majority_cpa_ownership_required` | boolean | Whether a simple majority (more than 50%) of firm ownership in terms of financial interests and voting rights must belong to licensed CPAs. | true |
| `nonlicensee_firm_owners_permitted` | boolean | Whether CPA firms may include owners who are not licensed CPAs, subject to specified conditions. | true |
| `peer_review_required_for_firm_renewal` | boolean | Whether peer review is required as a condition for renewal of a firm permit or registration. | true |
| `peer_review_max_frequency_years` | integer | Maximum frequency (in years) at which peer review may be required for firm permit renewal. | 3 |
| `peer_review_records_privileged` | boolean | Whether peer review proceedings, records, and work papers are privileged and not subject to discovery or introduction into evidence in civil or administrative proceedings. | true |
| `inactive_license_status_available` | boolean | Whether a licensee who is not engaged in the practice of public accounting may place their license on inactive status, typically with reduced fees and no CPE requirement. | true |
| `retired_license_status_available` | boolean | Whether a licensee may place their license on a retired status, typically with reduced or no fees and no CPE requirement, with restrictions on active practice. |  |
| `out_of_state_firm_no_office_exemption` | boolean | Whether a firm without an office in the state may provide certain services (compilation, review, or non-attest services) without obtaining a firm permit, subject to specified conditions. |  |
| `office_supervision_by_licensed_cpa_required` | boolean | Whether each office of a firm established in the state for the practice of public accounting must be under the direct supervision of a licensed CPA. | true |
| `attest_report_signer_competency_requirement` | boolean | Whether individuals who sign or authorize signing of attest or compilation reports on behalf of a firm must meet specific competency requirements set out in professional standards. | true |
| `client_confidentiality_privilege` | boolean | Whether communications between a licensee and client are confidential and privileged, with specified exceptions for professional standards, court proceedings, peer review, and ethical investigations. | true |
| `working_papers_ownership_by_licensee` | boolean | Whether working papers, schedules, and memoranda made by a licensee incident to professional services remain the property of the licensee (absent contrary agreement), with restrictions on transfer without client consent. | true |
| `commission_prohibition_during_attest` | boolean | Whether a licensee is prohibited from receiving commissions or referral fees when also performing attest or compilation services for the same client. |  |
| `contingent_fee_prohibition_during_attest` | boolean | Whether a licensee is prohibited from performing services for a contingent fee when also performing attest or compilation services for the same client, or from preparing tax returns for a contingent fee. |  |
| `safe_harbor_disclaimer_language_for_nonlicensees` | boolean | Whether the statute provides specific safe harbor disclaimer language that nonlicensees may use when preparing financial statements without expressing assurance, thereby avoiding unlicensed practice violations. | true |
| `foreign_accountant_practice_exception` | boolean | Whether holders of foreign country accounting designations may practice in the state under limited conditions (serving only clients from their home country, using only their foreign title, not issuing reports on domestic entities). | true |
| `single_act_evidence_sufficient` | boolean | Whether evidence of a single prohibited act is sufficient to justify a penalty, injunction, or conviction without evidence of a general course of conduct. | true |
| `firm_corrective_action_period_for_ownership_noncompliance` | boolean | Whether firms that fall out of compliance with ownership requirements due to changes in personnel are granted a reasonable period to take corrective action before facing permit suspension or revocation. | true |
| `firm_permit_required_for_attest_services` | boolean | Whether a firm must hold a valid permit or registration to provide attest or compilation services, separate from individual licensure requirements. | true |
| `registered_municipal_accountant_designation` | boolean | Whether the state has a specialized 'Registered Municipal Accountant' designation requiring additional examination, limited to auditing municipal or county financial statements. |  |
| `public_school_accountant_designation` | boolean | Whether the state has a specialized 'Public School Accountant' designation required for auditing school district financial statements. |  |
| `accounting_practitioner_tier` | boolean | Whether the state has a separate 'Accounting Practitioner' or 'Licensed Public Accountant' tier below CPA with its own examination, education, and scope-of-practice requirements. |  |
| `cpa_emeritus_or_retired_status_available` | boolean | Whether the state provides a formal 'CPA Emeritus' or 'CPA Retired' status for licensees who have permanently ceased practice, with reduced or no fees and no CPE requirement. |  |
| `government_audit_cpe_requirement` | boolean | Whether the state imposes additional or specific continuing professional education requirements for CPAs engaged in auditing governmental entities. |  |
| `ethics_cpe_hours_required` | integer | Minimum hours of ethics-related continuing professional education required per renewal period. |  |
| `hawaii_attest_work_supplement_required` | boolean | Whether Hawaii requires a state-specific supplemental peer review report covering Hawaii attest engagements when the primary peer review does not include Hawaii offices or engagements. |  |
| `liability_privity_limitation` | boolean | Whether the state limits CPA liability to third parties not in privity of contract, with exceptions for fraud, intentional misrepresentation, or known intended reliance. |  |
| `statute_of_limitations_for_accountant_negligence` | string | Specific statute of limitations period for actions based on negligence or breach of contract against accountants, typically shorter than general tort limitations. |  |
| `independence_requirement_for_attest` | boolean | Whether the statute explicitly requires a CPA to be independent with respect to an enterprise before expressing an opinion on its financial statements. |  |
| `client_records_return_obligation` | boolean | Whether the statute explicitly requires a licensee to return client-provided records and furnish copies of working papers that constitute part of the client's records upon client request. |  |

