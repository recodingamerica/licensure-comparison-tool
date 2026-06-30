# Field dictionary — professional_engineering

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from professional_engineering/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "State Board of Registration for Architects, Engineers, and  |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"practice of engineering\" means professional service or c |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["design of structures, machines, equipment, utilities syste |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `covers_land_surveying` | boolean | Whether the same statute and licensing board also governs professional land surveyors. | true |
| `covers_geology` | boolean | Whether the same statute and licensing board also governs professional geologists. | false |
| `engineer_intern_certificate_available` | boolean | Whether the state issues a formal intermediate certificate (engineer intern or engineer-in-training) to candidates who pass the fundamentals exam but have not yet completed experience requirements. | false |
| `surveyor_in_training_certificate_available` | boolean | Whether the state issues a formal intermediate certificate to land surveying candidates who pass the fundamentals exam but have not yet completed experience requirements. | false |
| `geologist_in_training_certificate_available` | boolean | Whether the state issues a formal intermediate certificate to geology candidates who pass the fundamentals exam but have not yet completed experience requirements. |  |
| `postgraduate_degree_experience_credit_years_max` | integer | Maximum number of years of experience credit that may be granted for postbaccalaureate engineering degrees earned before licensure. |  |
| `responsible_charge_defined` | boolean | Whether the statute provides an explicit statutory definition of 'responsible charge' as a term of art for the level of oversight required for licensure and practice. | true |
| `seal_required_on_documents` | boolean | Whether licensees are required by statute to obtain and affix an official seal to plans, specifications, plats, and reports they issue. | true |
| `seal_document_types` | list | Types of professional documents that must bear the licensee's seal and signature. | ["final drawings", "specifications", "surveys", "plats", "pl |
| `firm_practice_allowed` | boolean | Whether firms and corporations may lawfully offer engineering, surveying, or geology services, subject to the condition that responsible employees are licensed. | true |
| `exemptions_from_licensure` | list | Categories of persons or activities explicitly exempted from the licensure requirement. | ["contractor performing work designed by a professional arch |
| `code_of_ethics_in_statute` | boolean | Whether the statute itself contains a codified code of ethics whose violation is grounds for license suspension or revocation. | true |
| `multi_license_reporting_required` | boolean | Whether licensees holding licenses in other states, territories, or countries must report that fact and any out-of-state disciplinary actions to the board. |  |
| `board_engineering_disciplines_represented` | list | The major engineering disciplines that must be represented on the licensing board, as specified by statute. | ["civil engineering (two members)", "mining engineering", "e |
| `board_member_responsible_charge_years_required` | integer | Minimum number of years a professional board member must have been in responsible charge of work to be eligible for appointment. | 5 |
| `pdh_units_per_renewal_period` | integer | Number of Professional Development Hours (PDH) required per biennial renewal period. |  |
| `pdh_carryover_max_units` | integer | Maximum number of excess PDH units that may be carried forward into the next renewal period. |  |
| `retired_status_license_available` | boolean | Whether the state offers a retired-status license that exempts the holder from continuing education requirements while prohibiting active practice. | true |

