# Field dictionary — dietetics

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-07-27** (latest commit to `dietetics` records). Regenerate to refresh.

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
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Health" (FL) |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. | 19 (AL) |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. | true (AL) |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "master's or doctoral degree from an accredited college or u (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "regional or national accrediting agencies recognized by the (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "master" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "unspecified" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. | "Licensed Dietitian" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. | "bachelor" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "required_by_statute" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) | "at least 900 hours" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' | "documented work experience in human nutrition or human nutr (AK) |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "Commission on Dietetic Registration Examination" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "Waived if applicant provides evidence of current CDR regist (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "national (Commission on Dietetic Registration)" (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. | 3 (MO) |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 (AK) |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. | 105 (CT) |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true (AL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  | 30 (DE) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  | 2 (DE) |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["pain and symptom management"] (MI) |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must hold a current unrestricted license as a die (AK) |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. | "Dietetics and Nutrition Practice Council" (FL) |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. | "The board may delegate such powers and duties to the counci (FL) |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "Commission on Dietetic Registration" (AK) |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Dietetic Association" (AK) |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "voluntary_certification" (AK) |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" (AK) |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true (AK) |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true (AK) |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | false (AK) |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_license" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Secured or attempted to secure a license through deceit, fr (AK) |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? |  |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.38.010" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "qualifications (Chapter 34)" (AL) |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "the integration and application of scientific principles of (AK) |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["Assessing nutritional needs of individuals and groups", "E (AL) |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. | "Dietitian nutritionist may implement prescription drug dose (MI) |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.38.100" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  | "dietetic practice scope" (AL) |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `license_type_structure` | list | The distinct credential or license types recognized by the state (e.g., licensed dietitian, licensed nutritionist, dietitian-nutritionist, registered dietitian, provisionally licensed dietitian). | ["Licensed Dietitian", "Licensed Nutritionist"] (AK) |
| `provisional_license_available` | boolean | Whether the state offers a provisional or temporary license allowing practice under supervision while completing full licensure requirements. | true (AL) |
| `provisional_license_duration_months` | integer | Duration in months of a provisional or temporary license before it expires. | 12 (AL) |
| `provisional_license_requires_supervision` | boolean | Whether a provisional or temporary license restricts the holder to practice only under the supervision of a fully licensed dietitian. | true (AR) |
| `dietetic_technician_recognized` | boolean | Whether the state statute explicitly recognizes a dietetic technician credential as a distinct, lower-tier role that may perform limited functions under supervision. | true (AL) |
| `rd_credential_accepted_in_lieu_of_state_requirements` | boolean | Whether holding a current Registered Dietitian (RD/RDN) credential from the Commission on Dietetic Registration is explicitly accepted as satisfying all or most state licensure requirements. | true (AK) |
| `alternative_credential_pathways` | list | Non-RD national credentials or membership bodies that the state accepts as an alternative pathway to licensure (e.g., Certified Nutrition Specialist, American Board of Nutrition diplomate). | ["Diplomate of the American Board of Nutrition", "Certified  (AK) |
| `medical_nutrition_therapy_authorized` | boolean | Whether the statute explicitly authorizes the practice of 'medical nutrition therapy' as part of the dietitian's scope. | true (AL) |
| `enteral_parenteral_nutrition_authorized` | boolean | Whether the statute explicitly includes ordering or recommending enteral and/or parenteral nutrition within the dietitian's scope of practice. | true (AL) |
| `diet_order_writing_authority` | boolean | Whether the statute explicitly grants dietitians authority to write or issue diet orders (including therapeutic diets) in institutional or hospital settings. | true (AZ) |
| `lab_test_ordering_authority` | boolean | Whether the statute explicitly grants dietitians authority to order medical laboratory tests related to nutrition therapy. | true (CA) |
| `physician_referral_required` | boolean | Whether the statute requires a physician (or other authorized prescriber) referral or order before a dietitian may provide certain clinical nutrition services. | true (AL) |
| `diagnosis_treatment_prohibition` | boolean | Whether the statute explicitly prohibits dietitians from diagnosing, treating, or prescribing for human illness or otherwise practicing medicine. | true (AL) |
| `telehealth_practice_authorized` | boolean | Whether the statute explicitly authorizes dietitians to provide services via telehealth. | true (AL) |
| `supervision_ratio_limit` | integer | Maximum number of dietetic technicians a single registered dietitian may supervise at one time. | 2 (CA) |
| `direct_supervision_defined` | boolean | Whether the statute provides an explicit definition of 'direct supervision' for dietetic technicians or provisional licensees, including physical presence or availability requirements. | true (AL) |
| `exempt_professions_list` | list | Categories of other licensed professionals explicitly exempted from the dietetics licensure requirement when performing nutrition-related activities incidental to their own profession. | ["Animal nutritionist (nutrition care of animals only)", "Fe (AK) |
| `federal_employee_exemption` | boolean | Whether persons employed by the federal government (including armed forces, VA, or public health service) in a dietitian or nutritionist role are explicitly exempt from state licensure. | true (AK) |
| `weight_control_program_exemption` | boolean | Whether persons offering weight control programs are explicitly exempt from licensure, typically conditioned on the program being reviewed or approved by a licensed or registered dietitian. | true (AL) |
| `food_supplement_sales_exemption` | boolean | Whether persons who sell, market, or provide information about food, dietary supplements, vitamins, or herbs are explicitly exempt from the dietetics licensure requirement. | true (AL) |
| `animal_nutrition_exemption` | boolean | Whether persons whose nutrition practice is limited to animals are explicitly exempt from the human dietetics licensure requirement. | true (AK) |
| `nonresident_temporary_practice_allowed` | boolean | Whether out-of-state dietitians may practice in the state for a limited period without obtaining a state license. | true (AR) |
| `nonresident_temporary_practice_max_days` | integer | Maximum number of days per year a nonresident dietitian may practice in the state without a state license. | 180 (AR) |
| `interstate_compact_member` | boolean | Whether the state has enacted the Dietitian Licensure Compact, enabling multistate practice privileges. | true (AL) |
| `compact_privilege_jurisprudence_requirement` | boolean | Whether a state may require applicants for a compact practice privilege to pass a jurisprudence (state law knowledge) assessment. | true (AL) |
| `protected_titles` | list | The specific titles, words, letters, or abbreviations that are legally restricted to licensed or certified practitioners under the statute. | ["dietitian", "licensed dietitian", "nutritionist", "license (AK) |
| `nutrition_assessment_includes_biochemical_data` | boolean | Whether the statutory definition of nutritional assessment explicitly includes biochemical and anthropometric data as evaluation components. | true (AL) |
| `hospital_order_authority_requires_policy` | boolean | Whether a dietitian's authority to issue orders in a hospital setting is conditioned on the hospital having written policies and procedures authorizing such orders. | true (AZ) |
| `inactive_license_status_available` | boolean | Whether the state allows a licensee to place their license in an inactive status for a defined period. | true (FL) |
| `ethics_code_violation_grounds_for_discipline` | boolean | Whether violation of a recognized professional code of ethics (e.g., the American Dietetic Association's code) is explicitly listed as a ground for disciplinary action. | true (DE) |
| `scope__license_type_structure` | list | Scope checklist for 'license_type_structure'. Return EXACTLY one entry for each of these 16 items, using the item name verbatim: ['Licensed Dietitian', 'Licensed Nutritionist', 'Licensed Dietitian/Nutritionist', 'Temporarily Licensed Dietitian/Nutritionist', 'Provisionally Licensed Dietitian', 'Registered Dietitian', 'Registered Dietitian Nutritionist', 'Certified Dietitian', 'Certified Nutritionist', 'Certified Dietitian-Nutritionist', 'Dietitian/Nutritionist', 'Dietitian', 'Nutritionist', 'Dietetic Technician', 'Dietetic Technician, Registered', 'Qualified Nutrition Professional']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_type_structure[].item` | string |  | "Licensed Dietitian" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__license_type_structure[].status` | string |  | "present" (AK) |
| `scope__alternative_credential_pathways` | list | Scope checklist for 'alternative_credential_pathways'. Return EXACTLY one entry for each of these 8 items, using the item name verbatim: ['Registered Dietitian (RD) / Registered Dietitian Nutritionist (RDN) — Commission on Dietetic Registration', 'Diplomate of the American Board of Nutrition (ABN)', 'Certified Nutrition Specialist (CNS) — Board for Certification of Nutrition Specialists', 'Diplomate of the American Clinical Board of Nutrition (DACBN)', 'Certified Clinical Nutritionist (CCN) — Clinical Nutrition Certification Board', 'American Institute of Nutrition (AIN) membership', 'American Society for Clinical Nutrition (ASCN) membership', 'Diet Technician, Registered (DTR) — Commission on Dietetic Registration']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__alternative_credential_pathways[].item` | string |  | "Registered Dietitian (RD) / Registered Dietitian Nutritioni (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__alternative_credential_pathways[].status` | string |  | "present" (AK) |
| `scope__exempt_professions_list` | list | Scope checklist for 'exempt_professions_list'. Return EXACTLY one entry for each of these 26 items, using the item name verbatim: ['Physician', 'Osteopathic physician', 'Nurse', 'Pharmacist', 'Dentist', 'Dental hygienist', 'Chiropractor', 'Physical therapist', 'Physician assistant', 'Dietetic technician', 'Dietary manager', 'Dietetic aide', 'Cooperative extension home economist', 'Federal government employee (dietitian or nutritionist role)', 'Armed forces / military dietitian or nutritionist', 'Dietetics student', 'Animal nutritionist', 'Food product marketer or distributor', 'Weight control program provider', 'Hospital or long-term care facility employee (dietetic department)', 'Religious denomination member or employee (spiritual/prayer healing)', 'Nonresident / out-of-state dietitian (temporary or incidental practice)', 'Person supervised by or employed under a licensed dietitian (general category)', 'Person with doctoral degree in human nutrition or related field', 'General nutrition information provider (non-fee, non-counseling)', 'Any person licensed under another state act (general licensed professional exemption)']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__exempt_professions_list[].item` | string |  | "Physician" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__exempt_professions_list[].status` | string |  | "absent" (AK) |
| `scope__protected_titles` | list | Scope checklist for 'protected_titles'. Return EXACTLY one entry for each of these 13 items, using the item name verbatim: ['Dietitian', 'Licensed Dietitian', 'Licensed Dietitian Nutritionist', 'Licensed Nutritionist', 'Nutritionist', 'Dietitian/Nutritionist', 'Registered Dietitian', 'Registered Dietitian Nutritionist', 'Certified Dietitian', 'Provisionally Licensed Dietitian', 'Temporarily Licensed Dietitian/Nutritionist', 'Certified Nutrition Specialist', 'Dietetic Technician']. For EACH item, status is `present` if this state's statute provides for it, else `absent`. Quote verbatim for `present`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__protected_titles[].item` | string |  | "Dietitian" (AK) |
| &nbsp;&nbsp;&nbsp;&nbsp;`scope__protected_titles[].status` | string |  | "present" (AK) |

