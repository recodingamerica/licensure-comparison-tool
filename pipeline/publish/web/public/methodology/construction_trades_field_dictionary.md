# Field dictionary — construction_trades

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-18** (latest commit to `construction_trades` records). Regenerate to refresh.

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
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Consumer Affairs" (CA) |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 18 (AR) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AZ) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Educational and experience requirements adopted by the depa (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "accredited 4-year college" (FL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "none" (CA) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "board_approved" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (CA) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "residential-basic contractor" (GA) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "none" (GA) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "none" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "4 years (minimum 2 within last 10 years)" (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "practical or management trade experience in construction" (AZ) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Home inspection examination (existing homes) \u2013 America (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Required for registration as a home inspector for existing  (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "national (American Society of Home Inspectors or National A (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 5 (OH) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 200 (AL) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 8 (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 1 (CT) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["workers' compensation", "business practices", "workplace s (FL) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Temporary courtesy licenses may be issued to nonresidents;  (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "Residential Contractors Committee" (AR) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "Issue, modify, suspend, and revoke licenses; establish qual (AR) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Institute for Certification in Engineering Technol (KY) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Society of Home Inspectors; National Association o (AK) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "registration" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraudulent_or_misleading_application" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "The application for endorsement or registration is fraudule (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (IL) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.18.011" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "registration_required" (AK) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "a person who, in the pursuit of an independent business, un (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["construct", "alter", "repair", "move", "demolish", "excava (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. |  |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.18.171" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definition_of_contractor" (AK) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `registration_number_required_in_ads` | boolean | Whether the contractor's registration number must appear in all advertisements, contracts, estimates, and proposals. | true (AK) |
| `insurance_personal_injury_minimum_usd` | integer | Minimum dollar amount of liability insurance covering personal injury that a contractor must maintain. | 50000 (AK) |
| `insurance_property_damage_minimum_usd` | integer | Minimum dollar amount of insurance covering property damage caused by the contractor's work. | 20000 (AK) |
| `self_insurance_permitted` | boolean | Whether a contractor may satisfy insurance requirements by attesting to being self-insured rather than carrying a third-party policy. | true (AK) |
| `contract_must_be_written` | boolean | Whether a home improvement contract must be in writing to be valid and enforceable against the owner. | true (AZ) |
| `right_of_rescission_days` | integer | Number of business days within which an owner may rescind a signed home improvement contract without penalty. | 10 (FL) |
| `deposit_cap_fraction` | string | Maximum fraction of the total contract price a contractor may collect as a deposit before work begins, for contracts above a threshold amount. | "one-third of the total contract price or the actual cost of (MA) |
| `deposit_cap_contract_threshold_usd` | integer | Minimum contract price above which the deposit cap rule applies. | 1000 (MA) |
| `change_order_must_be_written` | boolean | Whether any deviation from the original plans or specifications requires a written change order signed by both parties. | true (CT) |
| `arbitration_clause_allowed` | boolean | Whether a home improvement contract may include an arbitration clause, subject to specific formatting and disclosure requirements. | true (GA) |
| `voidable_contract_clauses` | list | List of clause types that, if included in a home improvement contract, make the contract voidable by the owner. | ["acceleration clause"] (MA) |
| `minimum_annual_revenue_threshold_usd` | integer | Minimum total cash value of home improvements in the prior taxable year below which a person is exempt from contractor registration. | 2000 (IA) |
| `minimum_project_value_usd` | integer | Minimum cash price of a single project for the work to qualify as a regulated home improvement requiring a registered contractor. | 100000 (AL) |
| `fraud_offense_defined` | boolean | Whether the statute defines a specific criminal offense of home improvement fraud with enumerated prohibited acts. | true (AZ) |
| `fraud_felony_threshold_usd` | integer | Dollar amount above which a home improvement fraud violation is graded as a felony rather than a misdemeanor. | 300 (LA) |
| `enhanced_penalty_for_elderly_victims` | boolean | Whether the grading of a fraud offense is elevated by one level when the victim is 60 years of age or older. | true (HI) |
| `state_preempts_local_registration_fees` | boolean | Whether state registration preempts local governments from imposing their own contractor registration fees or licensing requirements. | true (AR) |
| `local_trade_licensing_preserved` | boolean | Whether existing local licensing standards for specific trades (e.g., electricians, plumbers) are preserved notwithstanding state preemption. | true (CA) |
| `registration_renewal_interval_years` | integer | How often, in years, a contractor must renew their registration with the issuing authority. | 2 (AK) |
| `out_of_state_disciplinary_action_reporting_required` | boolean | Whether a contractor must report to the state any disciplinary action taken against them in another jurisdiction. | true (CA) |

