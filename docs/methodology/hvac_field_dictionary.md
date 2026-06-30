# Field dictionary — hvac

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from hvac/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "Department of Commerce, Community, and Economic Development |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"mechanical administrator\" means a person who is responsi |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["installing", "modifying", "certifying compliance"] |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `system_components_included` | list | Specific components explicitly included within the definition of an HVAC system for licensing purposes. | ["mechanical piping and systems", "devices", "fixtures", "eq |
| `hvac_specific_experience_required` | boolean | Whether the applicant must demonstrate HVAC-specific (not general construction) paid employment experience. |  |
| `hvac_specific_experience_years` | integer | Number of years of full-time HVAC-specific paid employment experience required for licensure. |  |
| `prelicensure_course_hours` | integer | Number of hours in the required pre-licensure course that must be completed before a contractor license is issued. |  |
| `business_law_course_hours` | integer | Number of hours in a required business and law course that must be completed as part of the licensure process. |  |
| `qualifier_required` | boolean | Whether a licensed contractor entity must designate a named individual qualifier who holds the relevant trade license and exercises material authority over the business. | true |
| `qualifier_license_type_required` | list | The specific individual trade license(s) that the qualifier for an HVAC contractor entity must hold. | ["mechanical administrator license"] |
| `qualifier_cessation_notification_days` | integer | Number of days within which a contractor must notify the licensing division after a qualifier ceases association with the business. |  |
| `qualifier_replacement_grace_period_days` | integer | Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named. |  |
| `hvac_continuing_education_topic_hours_minimum` | integer | Minimum number of continuing education hours per renewal cycle that must directly relate to HVAC installation, repair, or replacement. |  |
| `gas_appliance_certification_required` | boolean | Whether persons performing installation, repair, maintenance, or replacement of gas appliances or combustion systems must obtain a separate certification beyond the base contractor license. |  |
| `natural_gas_facilities_installation_authorized` | boolean | Whether an HVAC contractor is authorized as a qualifying installer to install natural gas mains, service lines, and related facilities. |  |
| `financial_responsibility_demonstration_methods` | list | Acceptable methods by which a contractor applicant may demonstrate financial responsibility to the licensing authority. |  |
| `workers_compensation_insurance_required` | boolean | Whether proof of workers' compensation insurance covering employees must be filed with the division before a license is issued. |  |
| `public_liability_insurance_required` | boolean | Whether proof of public liability insurance in division-specified coverage amounts must be filed before a license is issued. |  |
| `small_project_exemption_threshold_dollars` | integer | Dollar threshold below which a project may be performed without a contractor license, subject to stated exclusions. | 50000 |
| `hvac_exempt_from_small_project_exemption` | boolean | Whether HVAC system installation, repair, or replacement is explicitly excluded from the general small-project dollar-threshold exemption from licensure. |  |
| `license_number_on_permits_required` | boolean | Whether the contractor's license number must appear on all permit applications, contracts, agreements, or bids. |  |
| `scope_expansion_by_rule_authorized` | boolean | Whether the licensing commission may expand the authorized scope of work for an HVAC contractor beyond the statutory definition through administrative rulemaking. | true |

