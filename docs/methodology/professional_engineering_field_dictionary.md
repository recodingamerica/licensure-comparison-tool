# Field dictionary — professional_engineering

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-24** (latest commit to `professional_engineering` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Each example below is drawn from the first state that has a value for that field; the source state is shown in parentheses.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true (AK) |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "State Board of Registration for Architects, Engineers, and  (AK) |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "State Board of Registration for Architects, Engineers, and  (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "shared_board" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development (AK) |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 35 (AR) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AK) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "Evidence of education, training, and experience satisfactor (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "Board-approved" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "bachelor" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "unspecified" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "EAC of ABET-accredited engineering graduates" (DE) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "bachelor" (DE) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | true (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "none" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "four years or more" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "progressive experience in engineering work" (AL) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Professional Engineer Examination" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Examinations held at least once per year; must meet standar (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "national examining councils (national)" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 3 (FL) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 150 (ID) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 18 (FL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 2 (FL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["1 hour relating to this chapter and the rules adopted unde (FL) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must hold a certificate of registration from a st (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "State Board of Professional Engineers" (IL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "advisory capacity to the Secretary; makes written recommend (IL) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Council of Examiners for Engineering and Surveying (DE) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "Alabama Society of Professional Land Surveyors" (AL) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_certificate" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Fraud or deceit in obtaining a certificate of registration" (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? | false (OH) |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? | true (DE) |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.48.011" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "board_creation" (AK) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "practice of engineering means professional service or creat (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["design of structures, machines, equipment, utilities syste (AK) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. |  |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.48.341" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "definition_of_practice" (AK) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `covers_land_surveying` | boolean | Whether the same statute and licensing board also governs professional land surveyors. | true (AK) |
| `covers_geology` | boolean | Whether the same statute and licensing board also governs professional geologists. | true (AZ) |
| `engineer_intern_certificate_available` | boolean | Whether the state issues a formal intermediate certificate (engineer intern or engineer-in-training) to candidates who pass the fundamentals exam but have not yet completed experience requirements. | true (AL) |
| `surveyor_in_training_certificate_available` | boolean | Whether the state issues a formal intermediate certificate to land surveying candidates who pass the fundamentals exam but have not yet completed experience requirements. | true (AL) |
| `geologist_in_training_certificate_available` | boolean | Whether the state issues a formal intermediate certificate to geology candidates who pass the fundamentals exam but have not yet completed experience requirements. | true (AZ) |
| `postgraduate_degree_experience_credit_years_max` | integer | Maximum number of years of experience credit that may be granted for postbaccalaureate engineering degrees earned before licensure. | 2 (AL) |
| `responsible_charge_defined` | boolean | Whether the statute provides an explicit statutory definition of 'responsible charge' as a term of art for the level of oversight required for licensure and practice. | true (AK) |
| `seal_required_on_documents` | boolean | Whether licensees are required by statute to obtain and affix an official seal to plans, specifications, plats, and reports they issue. | true (AK) |
| `seal_document_types` | list | Types of professional documents that must bear the licensee's seal and signature. | ["final drawings", "specifications", "surveys", "plats", "pl (AK) |
| `firm_practice_allowed` | boolean | Whether firms and corporations may lawfully offer engineering, surveying, or geology services, subject to the condition that responsible employees are licensed. | true (AK) |
| `exemptions_from_licensure` | list | Categories of persons or activities explicitly exempted from the licensure requirement. | ["a contractor performing work designed by a professional ar (AK) |
| `code_of_ethics_in_statute` | boolean | Whether the statute itself contains a codified code of ethics whose violation is grounds for license suspension or revocation. | true (AK) |
| `multi_license_reporting_required` | boolean | Whether licensees holding licenses in other states, territories, or countries must report that fact and any out-of-state disciplinary actions to the board. | true (CA) |
| `board_engineering_disciplines_represented` | list | The major engineering disciplines that must be represented on the licensing board, as specified by statute. | ["civil engineering", "mining engineering", "electrical engi (AK) |
| `board_member_responsible_charge_years_required` | integer | Minimum number of years a professional board member must have been in responsible charge of work to be eligible for appointment. | 5 (AK) |
| `pdh_units_per_renewal_period` | integer | Number of Professional Development Hours (PDH) required per biennial renewal period. | 18 (FL) |
| `pdh_carryover_max_units` | integer | Maximum number of excess PDH units that may be carried forward into the next renewal period. | 12 (MN) |
| `retired_status_license_available` | boolean | Whether the state offers a retired-status license that exempts the holder from continuing education requirements while prohibiting active practice. | true (AK) |
| `scope__seal_document_types` | list | Scope checklist for 'seal_document_types'. Return EXACTLY one entry for each of these 18 items, using the item name verbatim: ['Drawings', 'Plans', 'Specifications', 'Reports', 'Surveys', 'Plats', 'Plates', 'Calculations', 'Design information', 'Construction documents', 'Maps', 'Descriptions', 'Data', 'Instruments of service', 'Shop drawings', 'Revisions', 'Certifications', 'Affidavits']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__seal_document_types[].item` | string |  | "Drawings" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__seal_document_types[].status` | string |  | "present" (AK) |
| `scope__exemptions_from_licensure` | list | Scope checklist for 'exemptions_from_licensure'. Return EXACTLY one entry for each of these 33 items, using the item name verbatim: ['Federal government officers and employees practicing engineering in official capacity', 'Contractors executing work designed by a licensed engineer (construction execution only)', 'Building trades workers, craft workers, and construction superintendents/supervisors/inspectors performing customary duties', 'Employees or subordinates working under direct supervision of a licensed engineer', 'Engineers-in-training / engineer interns acting under supervision', 'Land surveyor interns', 'Teaching engineering, architectural, landscape architectural, or surveying courses at accredited institutions', 'Regulated transportation companies and public utilities (and their officers and employees) performing engineering for their own facilities', 'Engineering services incidental to the practice of architecture by licensed architects and their subordinates', 'Engineering services incidental to the practice of geology by licensed geologists and their subordinates', 'Practice of any other legally recognized profession or trade', 'Manufacturing, mining, public utility, research and development, or other industrial corporations performing engineering work incidental to their own products, systems, or services', 'Firms performing engineering services for themselves or their own subsidiaries/affiliates (in-house engineering)', 'Nonresident persons, firms, or corporations meeting specified out-of-state criteria', 'Real estate brokers or salespersons making appraisals and valuations of real estate', 'Alterations or repairs to buildings not affecting structural system or public health, safety, or welfare', 'Single-family and small residential dwellings of limited size', 'Agricultural work not required to be of public record', 'Revegetation, restoration, reclamation, rehabilitation, or erosion control for disturbed land not affecting public health, safety, or welfare', 'Maintenance or placement of plant material not affecting public health, safety, or welfare', 'Horticultural consultants and persons preparing planting plans for plant installations', 'Authorized designers of fire protection systems', 'Holders of temporary permits for engineering practice', 'Corporations, partnerships, LLCs, and LLPs offering professional engineering services through licensed principals (business entity exemption with certificate of authorization)', 'Government employees inspecting residential structures as part of official duties', 'Persons performing home inspections solely for lender construction monitoring', 'Property managers inspecting their own managed residential structures without separate compensation', 'Small public works projects below a specified expenditure threshold', 'Licensed geologists practicing geology (not required to hold engineer license)', 'Persons with grandfathered or legacy licensure status in discontinued engineering branch titles', 'Boundary surveys on private land not intended as basis for engineering design', 'Professional engineers or engineer interns granted inactive status', 'Senior licensed professional engineers exempt from continuing education requirements']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__exemptions_from_licensure[].item` | string |  | "Federal government officers and employees practicing engine (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__exemptions_from_licensure[].status` | string |  | "present" (AK) |
| `scope__board_engineering_disciplines_represented` | list | Scope checklist for 'board_engineering_disciplines_represented'. Return EXACTLY one entry for each of these 7 items, using the item name verbatim: ['Civil Engineering', 'Electrical Engineering', 'Mechanical Engineering', 'Mining Engineering', 'Petroleum Engineering', 'Chemical Engineering', 'General/Other Engineering']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__board_engineering_disciplines_represented[].item` | string |  | "Civil Engineering" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__board_engineering_disciplines_represented[].status` | string |  | "present" (AK) |

