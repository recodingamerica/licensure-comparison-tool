# Field dictionary — hvac

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-27** (latest commit to `hvac` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Each example below is drawn from the first state that has a value for that field; the source state is shown in parentheses.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true (AK) |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "Department of Commerce, Community, and Economic Development (AK) |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "Department of Commerce, Community, and Economic Development (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "department" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Labor and Licensing" (AR) |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 18 (AR) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AL) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "graduate of an approved heating, air conditioning, or refri (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "United States Department of Labor (apprenticeship programs) (NJ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "none" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "board_approved" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "none" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "3,000 hours" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "HVAC work experience" (AL) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Mechanical Administrator Licensing Examination" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Examination waived if applicant holds equivalent license fr (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "state (department-administered)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 3 (DE) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 100 (LA) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 4 (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 1 (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["workers' compensation", "business practices", "workplace s (FL) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must hold equivalent license from another state o (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "Committee of Mechanical Examiners" (OK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "Assist and advise the Board on all matters pertaining to ru (OK) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "Environmental Protection Agency (EPA) certification for han (DE) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "Mechanical Contractors Association of Arkansas, Inc." (AR) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraudulent_application" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "License application is fraudulent or misleading" (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. | true (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? | true (AR) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (ID) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.40.230" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "Categories of licenses" (AK) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"mechanical administrator\" means a person who is responsi (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["installing", "modifying", "certifying compliance"] (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. |  |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.40.490" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "Definitions" (AK) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `system_components_included` | list | Specific components explicitly included within the definition of an HVAC system for licensing purposes. | ["mechanical piping and systems", "devices", "fixtures", "eq (AK) |
| `hvac_specific_experience_required` | boolean | Whether the applicant must demonstrate HVAC-specific (not general construction) paid employment experience. | false (AK) |
| `hvac_specific_experience_years` | integer | Number of years of full-time HVAC-specific paid employment experience required for licensure. | 4 (AZ) |
| `prelicensure_course_hours` | integer | Number of hours in the required pre-licensure course that must be completed before a contractor license is issued. | 120 (ID) |
| `business_law_course_hours` | integer | Number of hours in a required business and law course that must be completed as part of the licensure process. | 5 (UT) |
| `qualifier_required` | boolean | Whether a licensed contractor entity must designate a named individual qualifier who holds the relevant trade license and exercises material authority over the business. | true (AK) |
| `qualifier_license_type_required` | list | The specific individual trade license(s) that the qualifier for an HVAC contractor entity must hold. | ["Mechanical Administrator License"] (AK) |
| `qualifier_cessation_notification_days` | integer | Number of days within which a contractor must notify the licensing division after a qualifier ceases association with the business. | 15 (AZ) |
| `qualifier_replacement_grace_period_days` | integer | Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named. | 60 (AZ) |
| `hvac_continuing_education_topic_hours_minimum` | integer | Minimum number of continuing education hours per renewal cycle that must directly relate to HVAC installation, repair, or replacement. | 3 (UT) |
| `gas_appliance_certification_required` | boolean | Whether persons performing installation, repair, maintenance, or replacement of gas appliances or combustion systems must obtain a separate certification beyond the base contractor license. | false (AR) |
| `natural_gas_facilities_installation_authorized` | boolean | Whether an HVAC contractor is authorized as a qualifying installer to install natural gas mains, service lines, and related facilities. | false (FL) |
| `financial_responsibility_demonstration_methods` | list | Acceptable methods by which a contractor applicant may demonstrate financial responsibility to the licensing authority. | ["Surety bond"] (AL) |
| `workers_compensation_insurance_required` | boolean | Whether proof of workers' compensation insurance covering employees must be filed with the division before a license is issued. | true (AZ) |
| `public_liability_insurance_required` | boolean | Whether proof of public liability insurance in division-specified coverage amounts must be filed before a license is issued. | true (FL) |
| `small_project_exemption_threshold_dollars` | integer | Dollar threshold below which a project may be performed without a contractor license, subject to stated exclusions. | 50000 (AK) |
| `hvac_exempt_from_small_project_exemption` | boolean | Whether HVAC system installation, repair, or replacement is explicitly excluded from the general small-project dollar-threshold exemption from licensure. | true (AZ) |
| `license_number_on_permits_required` | boolean | Whether the contractor's license number must appear on all permit applications, contracts, agreements, or bids. | true (AL) |
| `scope_expansion_by_rule_authorized` | boolean | Whether the licensing commission may expand the authorized scope of work for an HVAC contractor beyond the statutory definition through administrative rulemaking. | true (AK) |
| `scope__system_components_included` | list | Scope checklist for 'system_components_included'. Return EXACTLY one entry for each of these 28 items, using the item name verbatim: ['Air heating fixture', 'Air cooling fixture', 'Pipes / piping', 'Plenums', 'Blowers', 'Ductwork', 'Air filters', 'Air delivery and return grilles', 'Exhaust fans', 'Refrigerating machinery', 'Refrigerant lines', 'Compressors', 'Self-contained refrigeration units', 'Window-type air conditioning units', 'Central heating unit', 'Liquefied petroleum gas appliances', 'Gas fitting / gas piping connections', 'Manual safety shutoff gas cock', 'Flue gas vents', 'Combustion air systems', 'Ventilation systems', 'Piping fixtures, devices, and equipment', 'Accessories and ancillary equipment', 'Boilers and steamfitting', 'Hot water systems', 'Process cooling and heating systems', 'Electrical connections to HVAC units', 'Comfort heating and cooling systems']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__system_components_included[].item` | string |  | "Air heating fixture" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__system_components_included[].status` | string |  | "absent" (AK) |
| `scope__qualifier_license_type_required` | list | Scope checklist for 'qualifier_license_type_required'. Return EXACTLY one entry for each of these 9 items, using the item name verbatim: ['Mechanical Administrator License', 'Certified Heating, Air Conditioning, and Refrigeration Contractor License', 'Master HVACR License', 'Master HVACR Restricted License', 'Class A Air-Conditioning Contractor License', 'Class B Air-Conditioning Contractor License', 'Class C Air-Conditioning Contractor License', 'Mechanical Contractor License', 'Mechanical Contractor Registration (Certificate of Registration)']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__qualifier_license_type_required[].item` | string |  | "Mechanical Administrator License" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__qualifier_license_type_required[].status` | string |  | "present" (AK) |
| `scope__financial_responsibility_demonstration_methods` | list | Scope checklist for 'financial_responsibility_demonstration_methods'. Return EXACTLY one entry for each of these 15 items, using the item name verbatim: ['Surety bond', 'Cash deposit', 'Certificate of deposit / investment certificate / share account', 'General liability insurance', "Workers' compensation insurance", 'Professional liability insurance', 'Credit report from a nationally recognized credit agency', 'Evidence of net worth', 'Evidence of minimum cash holdings', 'Completion of a financial responsibility course', 'Assumption of personal financial responsibility by a financially responsible officer', 'Affidavit of insurance', 'Satisfaction of or accord regarding unsatisfied judgments', 'Proof of good standing with the state business registry (Secretary of State)', 'Minimum general liability insurance coverage established by board rule']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__financial_responsibility_demonstration_methods[].item` | string |  | "Surety bond" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__financial_responsibility_demonstration_methods[].status` | string |  | "absent" (AK) |

