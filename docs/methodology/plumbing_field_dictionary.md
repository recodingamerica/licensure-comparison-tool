# Field dictionary — plumbing

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-28** (latest commit to `plumbing` records). Regenerate to refresh.

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
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 18 (AZ) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AZ) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Technical training in an accredited college or university o (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "board-approved technical college or community college" (ME) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "none" (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "unspecified" (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (AZ) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "Journey level plumber" (WA) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "none" (WA) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "none" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "two years (journeyman); one year as journeyman (master)" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "work experience as an apprentice plumber or gas fitter, or  (AL) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Mechanical Administrator Examination" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Tests ability to understand plans/specs, knowledge of mecha (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "state (department-administered)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 3 (DE) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 200 (MS) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | false (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 8 (CO) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 1 (CO) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["course work related to the code, including core competenci (CO) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must hold equivalent license from another state o (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "Committee of Plumbing Examiners" (AR) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "The committee and other employees of the department shall s (AR) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Inspection Testing Certification (NITC) Corporatio (IA) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "National Fire Protection Association (NFPA)" (NJ) |
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
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (CO) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.40.230" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "categories_of_licenses" (AK) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"mechanical administrator\" means a person who is responsi (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["installing or modifying mechanical piping and systems, dev (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. |  |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.40.490" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definition" (AK) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `license_tiers` | list | The distinct license classification tiers available for plumbers, from apprentice through master and contractor levels. | ["Mechanical Administrator"] (AK) |
| `residential_scope_limited` | boolean | Whether a residential-tier plumber license restricts the licensee to work only on residential buildings (typically single or multi-family dwellings up to four units). | true (AR) |
| `residential_building_unit_cap` | integer | Maximum number of dwelling units in a building that a residential-tier plumber or contractor license authorizes work on. | 8 (AL) |
| `apprentice_supervision_requirement` | string | Description of which license types are authorized to directly supervise a licensed apprentice plumber. | "An apprentice plumber or gas fitter shall work directly und (AL) |
| `apprentice_unsupervised_hours_allowed` | integer | Maximum number of hours per 24-hour period that a fourth-year or later apprentice plumber may work without direct supervision. | 8 (UT) |
| `apprentice_unsupervised_training_year_threshold` | integer | The year of apprenticeship training at which an apprentice plumber first becomes eligible to work limited hours without direct supervision. | 4 (AR) |
| `apprentice_to_supervisor_ratio_regulated` | boolean | Whether the statute establishes or delegates authority to set a maximum ratio of apprentice plumbers per supervising licensee. | true (AL) |
| `journeyman_experience_pathways` | list | Alternative pathways an applicant may use to satisfy the experience requirement for journeyman plumber licensure. | ["Two years of current work experience as an apprentice plum (AL) |
| `master_plumber_supervisory_experience_required` | boolean | Whether a master plumber applicant must demonstrate supervisory experience as a journeyman plumber in addition to time-in-grade. | false (AL) |
| `expedited_licensure_pathway_available` | boolean | Whether the statute provides an expedited licensure pathway for applicants who can otherwise demonstrate equivalent knowledge and skills. | true (AR) |
| `plumbing_trade_geographic_limit_feet` | integer | How many feet beyond the outside walls of a building the plumbing trade definition extends. | 5 (AK) |
| `gas_supply_work_included_in_scope` | boolean | Whether the delivery of gas for lighting, heating, and industrial purposes is explicitly included within the plumbing trade scope. | true (AL) |
| `natural_gas_appliance_certification_required` | boolean | Whether a separate certification (beyond the plumbing license) is required before a licensee may install, repair, or replace a residential or commercial gas appliance or combustion system. | true (AL) |
| `fire_sprinkler_work_authorized` | boolean | Whether a licensed journeyman plumber is authorized to perform installation, repair, or replacement of water-based fire protection systems. | false (AK) |
| `natural_gas_facilities_installation_authorized` | boolean | Whether a licensed plumber (as a qualifying installer) is authorized to install natural gas mains and service lines beyond the building. | true (FL) |
| `contractor_qualifier_license_requirement` | enum — one of: master plumber required for general plumbing contractor, master plumber or master residential plumber required for residential plumbing contractor | The specific individual plumber license tier that the qualifier for a plumbing contractor entity must hold. | "master plumber required for general plumbing contractor" (AL) |
| `qualifier_replacement_notice_days` | integer | Number of days within which a contractor must notify the licensing division after a qualifier ceases association with the business. | 15 (AZ) |
| `qualifier_replacement_grace_period_days` | integer | Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named. | 60 (AZ) |
| `long_term_compliance_qualifier_waiver_years` | integer | Number of consecutive violation-free years after which a plumbing or electrical contractor business entity may substitute an active employee license number for a named individual qualifier at renewal. | 5 (AZ) |
| `minor_plumbing_repair_exemption` | boolean | Whether the statute provides an exemption from licensure for minor plumbing repair work incidental to fixing a fixture or appliance in a residential or small commercial building, provided no piping or gas system is altered. | true (AK) |
| `small_project_dollar_threshold` | integer | Maximum total project cost (labor and materials) below which an unlicensed person may perform certain construction work, with plumbing and electrical systems explicitly excluded from this exemption. | 50000 (AK) |
| `continuing_education_hours_plumber` | integer | Number of continuing education hours a licensed plumber (individual, not contractor) must complete per two-year renewal cycle. | 8 (CO) |
| `continuing_education_hours_contractor` | integer | Number of continuing education hours a licensed plumbing contractor must complete per two-year renewal cycle. | 14 (FL) |
| `scope__license_tiers` | list | Scope checklist for 'license_tiers'. Return EXACTLY one entry for each of these 11 items, using the item name verbatim: ['Apprentice Plumber', 'Apprentice Gas Fitter', 'Journeyman Plumber', 'Journeyman Gas Fitter', 'Master Plumber', 'Master Gas Fitter', 'Residential Plumber', 'Restricted Plumber', 'Medical Gas Piping Fitter', 'Plumbing Contractor', 'Mechanical Administrator']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_tiers[].item` | string |  | "Apprentice Plumber" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_tiers[].status` | string |  | "absent" (AK) |
| `scope__journeyman_experience_pathways` | list | Scope checklist for 'journeyman_experience_pathways'. Return EXACTLY one entry for each of these 11 items, using the item name verbatim: ['Registered apprenticeship program completion', 'On-the-job work experience as an apprentice plumber', 'Licensure as journeyman plumber in another state (reciprocity/endorsement)', 'Licensure as master plumber in another state (reciprocity/endorsement)', 'General plumbing work experience (years in the trade)', 'Technical training at an accredited college or university (substitution for experience)', "Manufacturer's accredited training program (substitution for experience)", 'Registered professional engineer with plumbing engineering expertise', 'Prior service as qualifying party or responsible managing employee under an active license', 'Experience as journeyman plumber (for master plumber licensure pathway)', 'Medical gas piping certification program completion']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__journeyman_experience_pathways[].item` | string |  | "Registered apprenticeship program completion" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__journeyman_experience_pathways[].status` | string |  | "absent" (AK) |

