# Field dictionary — optometry

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

**Reflects extracted data as of 2026-06-24** (latest commit to `optometry` records). Regenerate to refresh.

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from optometry/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model,
credential type, issuing authority, entry requirements (education, exams, age,
character), fees, renewal, continuing education, and reciprocity._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean | Whether the state requires a credential to practice this profession. | true |
| `issuing_authority` | string | Free-text name of the board/agency that issues the credential (the structured form is `regulatory_authority`). | "Board of Examiners in Optometry" |
| `regulatory_authority` | object | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.name` | string | Canonical name of the immediate authority (e.g., 'State Board of Podiatry'). | "Board of Examiners in Optometry" |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.type` | enum — one of: standalone_board, shared_board, division, department, joint, other | Structural classification of the immediate authority. | "standalone_board" |
| &nbsp;&nbsp;&nbsp;&nbsp;`regulatory_authority.umbrella_agency` | string | Higher-level agency that contains the immediate authority, if any. Example: 'Division of Occupations and Professions, Department of Commerce'. Null for standalone boards that don't sit inside a larger department. | "Department of Commerce, Community, and Economic Development |
| `age_minimum` | integer | Minimum age (years) to hold the credential, if the statute sets one. |  |
| `moral_character_required` | boolean | Whether the statute conditions licensure on good moral character / fitness. |  |
| `education` | object | Education entry requirement — degree, level, accreditation, and any tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_required` | string |  | "graduate of a school or college of optometry recognized by  |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.accrediting_body` | string |  | "American Optometric Association" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | The comparable education FLOOR as a normalized rung. Populate whenever licensure is gated on a degree; null only if the statute is silent on education. | "doctorate" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.school_approval_basis` | enum — one of: national_accreditor, regional_accreditor, board_approved, unspecified | How the statute decides a school counts. national_accreditor=a named national program accreditor (ACOE/CODA/ACEND/LCME/CPME). regional_accreditor='regionally accredited college or university'. board_approved='approved by the board' (discretionary state gate). unspecified=says 'accredited' with no basis named, or silent. | "national_accreditor" |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.credential_pegged` | boolean | True if the statute pegs the education requirement to a NATIONAL CREDENTIAL (e.g. 'registered by CDR', 'passed the NBEO') rather than (or in addition to) a stated degree — such a state inherits whatever that national body currently requires. | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`education.tiers` | list | Per-tier floors when the statute sets different education levels for different license classes, or phases the floor in by date. Omit/null when there is a single floor. `degree_level` still records the overall floor across all tiers. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].license_class` | string | Which class/date this floor applies to — e.g. 'licensed dietitian', 'certified nutritionist', 'applicants on or after 2024-01-01'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].degree_level` | enum — one of: none, high_school, associate, bachelor, master, doctorate | Normalized education floor, low -> high. Resolved to the rung even when the statute uses verbiage ('six college years' -> doctorate, 'or equivalent degree' -> the named level). Professional/clinical doctorates (OD, DDS, MD, DPM) are `doctorate`. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`education.tiers[].effective_date` | string | ISO date when this floor takes effect, for date-phased tiers (e.g. '2024-01-01'). Null otherwise. |  |
| `post_degree_experience` | object | Supervised practice / residency / apprenticeship required after the degree. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.required` | boolean |  | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.experience_source` | enum — one of: required_by_statute, embedded_in_credential, none | ALWAYS populate (required_by_statute / embedded_in_credential / none) unless the governing statute is absent from the corpus. Disambiguates a blank `required`: 'none' (truly no requirement) vs 'embedded_in_credential' (the accredited degree the statute points to carries the supervised hours). | "embedded_in_credential" |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.duration` | string | e.g. '24 months', '1 year', '2,000 hours' (free text — units vary) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`post_degree_experience.kind` | string | e.g. 'podiatric residency', 'accounting work experience', 'AXP' |  |
| `exams` | list | Examinations required for the credential (one entry per exam). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].name` | string |  | "National or international examination designated by the boa |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].notes` | string |  | "All or part of a national or international examination desi |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].jurisdiction` | string | Where the exam is administered / who owns it — e.g. 'NBPME (national)', 'state board (in-state)', 'NCLEX-RN (national)'. Use the statute's language; null if the source doesn't say. | "national or international (board-designated)" |
| &nbsp;&nbsp;&nbsp;&nbsp;`exams[].permitted_attempts` | integer | Max attempts allowed before re-qualification. Null if not specified. |  |
| `renewal` | object | How the credential is renewed — interval and any conditions. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`renewal.interval_years` | integer | Most states are 1 or 2 | 2 |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. |  |
| `continuing_education` | object | Continuing-education requirement to keep the credential active. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.required` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.hours_per_period` | integer |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.period_years` | integer |  |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`continuing_education.topical_requirements` | list | Specific topical CE requirements, e.g. ['1.5 hrs opioid', 'ethics'] | ["pain management and opioid use and addiction (at least 2 h |
| `reciprocity` | object | Whether/how the state recognizes out-of-state credentials (endorsement/reciprocity). |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.available` | boolean |  | true |
| &nbsp;&nbsp;&nbsp;&nbsp;`reciprocity.requirements` | string | Free-form summary | "Applicant must be a graduate of a board-recognized optometr |
| `advisory_board` | object | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.exists` | boolean | True if a profession-specific advisory body exists alongside the main licensing board. False if the licensing board itself is profession-specific (no separate advisory body needed). | false |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.name` | string | Name of the advisory board, e.g. 'Podiatry Advisory Committee'. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`advisory_board.authority` | string | Authority the advisory board has, in the statute's own words — e.g. 'advisory only', 'rulemaking subject to board approval', 'disciplinary recommendations'. Free text from the statute. |  |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Board of Examiners in Optometry (NBEO)" |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Optometric Association (AOA)" |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "license" |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | true |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].short_label` | string | snake_case key, e.g. 'fraud_in_obtaining_license' | "fraud_in_obtaining_license" |
| &nbsp;&nbsp;&nbsp;&nbsp;`disciplinary_grounds[].description` | string | One-line plain-English description | "Secured a license through deceit, fraud, or intentional mis |
| `alternative_regulation` | object | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.bonding_required` | boolean | Does the statute require the practitioner or firm to post a bond (funds against which consumer claims can be made)? Independent of whether a credential is also required. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.insurance_required` | boolean | Does the statute require the practitioner or firm to carry insurance (e.g., professional liability, surety insurance)? |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`alternative_regulation.establishment_regulation_required` | boolean | Does the statute regulate the ESTABLISHMENT / FIRM (e.g., facility license, mandatory inspection of premises) as a route to consumer protection, independent of any practitioner credential? |  |
| `citations` | list | Statutory citations supporting the licensure fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.72.010" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  |  |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope,
authorized methods, drug authority, and any title/scope protection. Skeleton only —
profession-specific scope richness lives in the discovered block._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"optometry\" means the examination, evaluation, diagnosis, |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["examination", "evaluation", "diagnosis", "treatment", "per |
| `drug_authority` | string | Whether/how the profession may prescribe, administer, or dispense drugs. | "A licensee may prescribe and use a pharmaceutical agent, in |
| `citations` | list | Statutory citations supporting the scope fields above. |  |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].cite` | string |  | "08.72.300" |
| &nbsp;&nbsp;&nbsp;&nbsp;`citations[].kind` | string |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes); they vary profession to profession._

| field | type | what it means | example value |
|---|---|---|---|
| `surgery_prohibited` | boolean | Whether the statute explicitly prohibits optometrists from performing invasive or ophthalmic surgery. | false |
| `surgery_definition` | string | Statutory definition of 'surgery' as it applies to the limits of optometric practice. | "an invasive procedure in which human tissue is cut, ablated |
| `foreign_body_removal_authorized` | boolean | Whether the statute explicitly authorizes removal of superficial foreign bodies from the eye and its appendages. | true |
| `laser_procedures_authorized` | list | Specific laser procedures the statute explicitly authorizes optometrists to perform. |  |
| `minor_surgical_procedures_authorized` | list | Minor non-laser procedural authorities explicitly granted by statute beyond foreign body removal. |  |
| `glaucoma_treatment_authorized` | boolean | Whether the statute explicitly authorizes optometrists to medically treat glaucoma. |  |
| `anaphylaxis_treatment_authorized` | boolean | Whether the statute explicitly authorizes optometrists to administer epinephrine or similar agents for anaphylaxis. |  |
| `vision_therapy_authorized` | boolean | Whether the statute explicitly includes vision therapy, orthoptics, or visual training within the scope of practice. |  |
| `immunization_authority` | boolean | Whether the statute authorizes optometrists to administer immunizations/vaccines. |  |
| `controlled_substance_schedule_restrictions` | list | Specific controlled substance schedules that optometrists are prohibited from or limited in prescribing. |  |
| `opioid_prescription_day_limit` | integer | Maximum number of days' supply for an initial opioid prescription issued by an optometrist. | 4 |
| `oral_pharmaceutical_authority` | boolean | Whether the statute explicitly grants authority to prescribe oral (systemic) pharmaceutical agents, beyond topical agents. | true |
| `pharmaceutical_certification_required` | boolean | Whether a separate board certification or approval is required before an optometrist may use therapeutic pharmaceutical agents. | true |
| `dea_registration_required` | boolean | Whether the statute requires optometrists who prescribe controlled substances to hold or register a federal DEA number. | true |
| `tiered_license_types` | list | Named license tiers or designations beyond the basic optometrist license that carry different scopes of practice. |  |
| `specialty_certification_types` | list | Named specialty certifications (beyond basic licensure) that unlock additional scope, such as therapeutic pharmaceutical agents or glaucoma treatment. |  |
| `pharmacology_training_hours_required` | integer | Minimum clock hours of pharmacology or ocular disease training required for therapeutic pharmaceutical agent certification or expanded scope. | 23 |
| `supervised_clinical_internship_required` | boolean | Whether a supervised clinical internship or preceptorship is required for expanded pharmaceutical or procedural certification. |  |
| `referral_to_physician_required` | boolean | Whether the statute requires optometrists to refer patients to a physician when conditions exceed the optometric scope of practice. | true |
| `comanagement_with_ophthalmologist_required` | boolean | Whether the statute requires co-management with an ophthalmologist for pre- or post-operative care or certain conditions. |  |
| `delegation_to_unlicensed_assistants_authorized` | boolean | Whether the statute explicitly authorizes optometrists to delegate routine or specified tasks to unlicensed or non-optometrist assistants. | true |
| `telemedicine_authorized` | boolean | Whether the statute explicitly addresses or authorizes the delivery of optometric services via telemedicine. |  |
| `mobile_office_authorized` | boolean | Whether the statute explicitly addresses or regulates the operation of mobile optometric offices (vans, trailers, etc.). |  |
| `home_visit_permit_required` | boolean | Whether the statute requires a special permit or registration to practice optometry at a patient's home residence. |  |
| `maximum_number_of_offices` | integer | Maximum number of offices a single optometrist or group may operate under the statute. |  |
| `contact_lens_prescription_expiration_years` | integer | Minimum required expiration period (in years) for a contact lens prescription. |  |
| `spectacle_prescription_release_required` | boolean | Whether the statute requires the prescriber to provide the patient with a copy of their spectacle or eyeglass prescription at no additional charge. |  |
| `patient_record_retention_years` | integer | Minimum number of years optometrists are required to retain patient records. |  |
| `impaired_practitioner_program_established` | boolean | Whether the statute establishes or references a formal program for identifying, treating, and monitoring impaired optometrists. |  |
| `limited_teaching_license_available` | boolean | Whether the statute provides for a limited license for optometry faculty or instructors who are not otherwise licensed in the state. |  |
| `retired_license_status_available` | boolean | Whether the statute provides for a formal retired license status that exempts the holder from renewal and continuing education requirements. | true |
| `jurisprudence_exam_required` | boolean | Whether the statute explicitly requires passage of a state law (jurisprudence) examination as a condition of licensure or endorsement. | true |
| `criminal_background_check_required` | boolean | Whether the statute requires applicants to submit to a criminal background check (including fingerprinting) as part of the licensure process. |  |

