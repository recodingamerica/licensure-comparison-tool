# Field dictionary — architecture

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-06-29** (latest commit to `architecture` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from architecture/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "State Board of Registration for Architects, Engineers, and  |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "State Board of Registration for Architects, Engineers, and  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "shared_board" |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. |  |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Evidence satisfactory to the board of the applicant's educa |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "board_approved" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "required_by_statute" |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' |  |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Examination for registration" |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Procedure and standards shall at least meet the requirement |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "state, with national standards" |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. |  |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. |  |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] |  |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Must hold a certificate of registration from another U.S. s |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. |  |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Council of Architectural Registration Boards (NCAR |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. |  |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_certificate" |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Fraud or deceit in obtaining a certificate of registration" |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? |  |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.48.011" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "board_creation" |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"practice of architecture\" means professional service or  |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["design of buildings", "consultation", "investigation", "ev |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. |  |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.48.341" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definition" |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `interior_designer_certification_available` | boolean | Whether the state offers a separate certification credential for interior designers alongside the architect license. |  |
| `interior_design_services_defined` | boolean | Whether the statute separately defines 'interior design services' as a distinct regulated activity from the practice of architecture. |  |
| `design_build_authorized` | boolean | Whether the statute explicitly authorizes and regulates design-build project delivery by architectural firms or entities. |  |
| `permitted_firm_structures` | list | The legal business entity forms in which architects are permitted to practice. | ["corporation", "limited liability company", "limited liabil |
| `firm_licensed_architect_ownership_minimum_fraction` | string | The minimum fraction of ownership, directors, or partners in an architectural firm that must be licensed architects (as opposed to other licensed design professionals). |  |
| `firm_design_professional_ownership_minimum_fraction` | string | The minimum fraction of ownership, directors, or partners in an architectural firm that must be licensed in architecture, engineering, or landscape architecture combined. |  |
| `seal_required` | boolean | Whether a licensed architect is required to obtain and affix an official seal to drawings, specifications, and other design documents. | true |
| `seal_surrender_required_on_license_termination` | boolean | Whether an architect must surrender their seal or stamp to the board upon forfeiture, revocation, suspension, expiration, or death. |  |
| `continuing_education_subject_requirement` | list | Specific subject-area requirements mandated for continuing education credit toward license renewal. |  |
| `continuing_education_excluded_topics` | list | Topics explicitly prohibited from counting toward continuing education requirements. |  |
| `continuing_education_waiver_conditions` | list | Circumstances under which the board may waive all or part of the continuing education requirement. | ["active duty military service"] |
| `exempt_building_types` | list | Categories of structures or projects explicitly exempt from the architect licensure requirement. | ["single family residence for person's own use and occupancy |
| `ncarb_certificate_reciprocity_prima_facie` | boolean | Whether possession of an NCARB certificate constitutes prima facie evidence of meeting the state's licensure qualifications for reciprocity purposes. | true |
| `ncarb_standards_adoptable` | boolean | Whether the board is explicitly authorized to adopt NCARB guidelines for minimum education, training, and experience equivalents. |  |
| `unauthorized_practice_criminal_penalty_first_offense` | string | The criminal classification and maximum penalty for a first offense of unauthorized practice of architecture. | "Misdemeanor; fine not more than $10,000, or imprisonment no |
| `unauthorized_practice_criminal_penalty_subsequent_offense` | string | The criminal classification and penalty range for a second or subsequent offense of unauthorized practice of architecture. |  |
| `civil_penalty_maximum` | integer | Maximum civil penalty in dollars the board may levy on a current licensee or unauthorized practitioner for violations. | 5000 |

