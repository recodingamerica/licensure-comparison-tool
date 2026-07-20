# Field dictionary — electrician

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-18** (latest commit to `electrician` records). Regenerate to refresh.

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
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 18 (AZ) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AZ) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "No degree required; technical training in an accredited col (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "accredited college or university (for engineering degree pa (CO) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "none" (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "regional_accreditor" (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "master electrician (engineering degree pathway)" (CO) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "bachelor" (CO) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "none" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "4 years" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "practical experience as a journeyman electrician in charge  (AL) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Electrical Administrator Licensing Examination" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Covers ability to understand plans/specifications, knowledg (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "state (department-administered)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 2 (MI) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 50 (AR) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 14 (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 2 (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["national electrical code", "core competencies as determine (CO) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must show they are licensed as an electrical admi (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "Electrical Work Board" (CT) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "The board advises the Commissioner of Consumer Protection o (CT) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. |  |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American National Standards Institute" (AK) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraudulent_application" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "The license application is fraudulent or misleading." (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. | true (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? | true (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (DE) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.40.045" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "statute" (AK) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "a person who is responsible for (A) installing or repairing (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["installing electrical wiring, conduits, devices, fixtures, (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. |  |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.40.200" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "statute" (AK) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `license_tiers` | list | The named tiers or classifications of electrician license available in the state, from apprentice through master and including residential variants. | ["electrical administrator categories (set by regulation)"] (AK) |
| `residential_project_definition` | string | Statutory definition of what constitutes a 'residential project' for purposes of limiting or distinguishing residential electrician license scope. | "residential journeyman and master electrician licenses are  (AR) |
| `residential_wiring_method_restriction` | boolean | Whether the residential-tier electrician license is restricted to work on buildings primarily wired with nonmetallic sheathed (NM) cable. | true (UT) |
| `voltage_limit_residential` | integer | Maximum voltage (line-to-line) permitted under a residential electrician license classification. | 1000 (NC) |
| `scope_exclusions` | list | Specific categories of work explicitly excluded from the definition of the electrical trade and therefore not requiring an electrician license. | ["utilities/municipalities for generation and distribution s (AK) |
| `minor_electrical_work_amperage_limit` | integer | Maximum amperage for minor electrical work incidental to a mechanical or service installation that is excluded from the licensed electrical trade. | 200 (DE) |
| `minor_electrical_work_distance_limit_feet` | integer | Maximum distance in feet that wiring may be extended from an existing outlet or disconnect to qualify as minor electrical work excluded from licensure. | 10 (AR) |
| `apprentice_supervision_ratio` | string | The maximum ratio of licensed apprentice electricians permitted under the immediate supervision of one licensed supervisor, as set by rule. | "1 master or journeyman to 3 apprentices on a single electri (AR) |
| `apprentice_unsupervised_hours_allowed` | integer | Maximum hours per 24-hour period that a fourth-year or later apprentice electrician may work without direct supervision. | 8 (UT) |
| `apprentice_unsupervised_year_threshold` | integer | The year of apprenticeship training at which an apprentice electrician first becomes eligible to work limited hours without direct supervision. | 4 (UT) |
| `residential_apprentice_supervisor_ratio_max` | integer | Maximum number of apprentice electricians a licensed supervisor may oversee on a residential project. | 6 (ID) |
| `qualifier_required` | boolean | Whether a licensed electrical contractor entity must designate a qualifying individual who holds the relevant journeyman or master license and exercises material authority over the business. | true (AK) |
| `qualifier_license_requirement_by_contractor_type` | list | The specific electrician license tier that the qualifier for each type of electrical contractor must hold. | ["Electrical contractor: must be a master electrician or emp (AR) |
| `qualifier_replacement_notice_days` | integer | Number of days within which a contractor must notify the licensing division in writing after a qualifier ceases association with the business. | 15 (AZ) |
| `qualifier_replacement_grace_period_days` | integer | Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named. | 60 (AZ) |
| `long_term_compliance_qualifier_waiver_years` | integer | Number of consecutive years of violation-free licensure after which an electrical contractor business entity may substitute an active licensed employee name for a named individual qualifier at renewal. | 5 (AZ) |
| `journeyman_electrician_apprenticeship_hours` | integer | Minimum hours of full-time apprenticeship training required to qualify for a journeyman electrician license via the apprenticeship pathway. | 8000 (DE) |
| `journeyman_electrician_experience_alternative_years` | integer | Years of full-time electrical experience accepted as an alternative pathway to journeyman electrician licensure in lieu of a formal apprenticeship. | 4 (CO) |
| `master_electrician_journeyman_experience_years` | integer | Years of practical experience as a journeyman electrician required to qualify for a master electrician license via the experience pathway. | 4 (AL) |
| `master_electrician_engineering_degree_pathway` | boolean | Whether a graduate electrical engineering degree from an accredited institution, combined with reduced practical experience, is an accepted pathway to master electrician licensure. | true (CO) |
| `master_electrician_trade_school_degree_pathway` | boolean | Whether an associate of applied sciences degree from an approved electrical trade school, combined with journeyman experience, is an accepted pathway to master electrician licensure. | true (CO) |
| `residential_journeyman_training_program_years` | integer | Minimum years of training in a division-approved electrical training program accepted as a pathway to residential journeyman electrician licensure. | 2 (CO) |
| `residential_master_electrician_journeyman_experience_years` | integer | Minimum years of practical experience as a residential journeyman electrician required to qualify for a residential master electrician license. | 2 (OR) |
| `expedited_licensure_pathway_available` | boolean | Whether an expedited licensure pathway exists for applicants who can clearly demonstrate equivalent knowledge and skills without meeting the standard experience or training requirements. | true (CA) |
| `electrician_continuing_education_hours` | integer | Total hours of continuing education a licensed electrician (journeyman through master) must complete per two-year renewal cycle. | 14 (AL) |
| `approved_continuing_education_providers` | list | Named organizations whose courses are approved to satisfy electrician continuing education requirements. | ["accredited college or university", "established industry t (CO) |
| `national_electrical_code_reference` | boolean | Whether the statute explicitly references the National Electrical Code as the governing standard for electrical work. | true (AK) |
| `gas_appliance_work_certification_required` | boolean | Whether electricians or contractors performing installation, repair, or replacement of gas appliances or combustion systems must obtain a separate certification beyond their electrician license. | true (UT) |
| `small_project_dollar_threshold_exemption` | integer | Maximum total project cost (labor and materials) below which a person may perform certain construction work without a contractor license, with electrical and plumbing work explicitly excluded from this exemption. | 5000 (AK) |
| `solar_panel_electrical_work_exemption` | boolean | Whether electrical work incidental to installing or repairing solar panels is exempt from standard electrician licensure requirements. | true (CT) |
| `hot_tub_sign_electrical_exemption` | boolean | Whether electrical work incidental to installing or repairing an above-ground prebuilt hot tub or on-premise signage is exempt from electrician licensure. | false (SC) |
| `utility_worker_exemption` | boolean | Whether persons employed by electric utilities, railroads, telephone corporations, or municipal utilities are exempt from electrician licensure for work incidental to those employers' operations. | true (AK) |
| `financial_responsibility_bond_option` | boolean | Whether an electrical contractor applicant may satisfy the financial responsibility requirement by submitting a surety bond as an alternative to completing a financial questionnaire. | true (AZ) |
| `workers_compensation_insurance_required` | boolean | Whether proof of workers' compensation insurance covering employees is required before the division will issue an electrical contractor license. | true (AZ) |
| `public_liability_insurance_required` | boolean | Whether proof of public liability insurance in division-specified amounts is required before the division will issue an electrical contractor license. | true (DE) |

