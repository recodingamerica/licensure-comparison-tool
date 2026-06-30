# Field dictionary — public_accountancy

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from public_accountancy/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "Board of Public Accountancy" |
| `regulatory_authority` | RegulatoryAuthority | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| `age_minimum` | integer |  |  |
| `moral_character_required` | boolean |  | true |
| `education` | EducationRequirement |  |  |
| `post_degree_experience` | PostDegreeExperience | Residency / supervised practice / apprenticeship — name varies, structure doesn't. |  |
| `exams` | list |  |  |
| `renewal` | Renewal |  |  |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. |  |
| `continuing_education` | ContinuingEducation |  |  |
| `reciprocity` | Reciprocity |  |  |
| `advisory_board` | AdvisoryBoard | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. |  |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Institute of Certified Public Accountants" |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "the offering to perform or the performance as a person hold |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["preparing financial statements", "issuing reports", "furni |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

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

