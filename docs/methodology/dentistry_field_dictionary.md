# Field dictionary — dentistry

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from dentistry/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "Board of Dental Examiners" |
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
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Association of Dental Boards" |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "A person engages in the practice of dentistry who (1) perfo |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["diagnosis and treatment of dental diseases and conditions" |
| `drug_authority` | string |  | "Dentists may prescribe drugs within the scope of dental pra |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `sedation_anesthesia_permit_types` | list | The distinct categories of sedation and anesthesia permits a dentist may obtain beyond basic local anesthesia, each requiring separate training and board approval. |  |
| `sedation_permit_onsite_inspection_required` | boolean | Whether the board may require an on-site inspection of the facility, equipment, and personnel before issuing or renewing a sedation or anesthesia permit. |  |
| `sedation_adverse_event_reporting_required` | boolean | Whether licensees are required to report deaths, injuries, or other adverse events resulting from sedation or anesthesia to the board within a specified timeframe. |  |
| `pediatric_sedation_endorsement_required` | boolean | Whether a separate pediatric endorsement on a sedation or anesthesia permit is required before administering sedation to patients below a specified age threshold. |  |
| `specialist_license_available` | boolean | Whether the state issues a separate specialist license or certificate allowing a dentist to hold themselves out to the public as a specialist in a recognized branch of dentistry. | true |
| `specialty_practice_scope_restriction` | boolean | Whether a dentist who obtains a specialist license is restricted to practicing only within that specialty branch. | true |
| `specialty_advertising_disclaimer_required` | boolean | Whether dentists who advertise a practice emphasis in an area not recognized as a specialty by the board must include a specific statutory disclaimer in their advertising. |  |
| `dental_hygienist_supervision_levels` | list | The defined levels of dentist supervision under which dental hygienists may perform procedures, as enumerated in statute. | ["direct supervision", "indirect supervision", "general supe |
| `collaborative_agreement_available` | boolean | Whether the state authorizes a formal written collaborative agreement between a dentist and a dental hygienist that allows the hygienist to provide specified services without the dentist's physical presence. | true |
| `collaborative_agreement_max_hygienists_per_dentist` | integer | The maximum number of collaborative or affiliated practice agreements a single dentist may hold simultaneously with dental hygienists. | 5 |
| `advanced_practice_permit_available` | boolean | Whether the state issues an advanced practice permit or equivalent credential allowing a dental hygienist to provide services to underserved populations without a dentist's physical presence or prior examination. | true |
| `advanced_practice_eligible_patient_populations` | list | The specific patient populations or settings for which an advanced practice or affiliated practice dental hygienist may provide services without direct dentist supervision. | ["residents in senior centers including hospitals, long-term |
| `dental_therapist_license_available` | boolean | Whether the state licenses dental therapists as a distinct mid-level dental provider category with its own scope of practice. |  |
| `dental_therapist_collaborative_practice_required` | boolean | Whether a dental therapist must operate under a written collaborative practice agreement with a supervising dentist in order to practice independently of direct supervision. |  |
| `dental_therapist_practice_setting_restrictions` | list | The specific practice settings or facility types in which a dental therapist is authorized to practice. |  |
| `mobile_dental_facility_registration_required` | boolean | Whether operators of mobile dental facilities or portable dental units must register with the state dental board and comply with specific operational requirements. |  |
| `mobile_facility_followup_care_protocol_required` | boolean | Whether operators of mobile dental facilities are required to maintain a written protocol for emergency follow-up care for patients treated at the mobile facility. |  |
| `dental_office_ownership_restrictions` | boolean | Whether the state restricts ownership or operation of dental offices to licensed dentists or specified entities, prohibiting non-dentist corporate ownership. | true |
| `opioid_prescribing_limits` | boolean | Whether the state imposes statutory limits on the quantity or duration of opioid prescriptions that a dentist may issue. | true |
| `controlled_substance_database_registration_required` | boolean | Whether dentists who hold a DEA registration number are required to register with or use the state's controlled substance prescription monitoring database. | true |
| `dental_laboratory_work_authorization_required` | boolean | Whether dentists must provide a written work authorization or prescription to dental laboratories when ordering prosthetic or orthodontic appliances, with specified content requirements. |  |
| `denture_patient_identification_marking_required` | boolean | Whether dentists are required to have complete dentures permanently marked with the patient's name or initials during fabrication for identification purposes. |  |
| `teledentistry_authorized` | boolean | Whether the state expressly authorizes or defines teledentistry as a permitted mode of delivering dental services. |  |
| `hygienist_local_anesthesia_certification_required` | boolean | Whether dental hygienists must obtain a separate board-issued certificate or permit before they are authorized to administer local anesthesia. | true |
| `hygienist_nitrous_oxide_certification_required` | boolean | Whether dental hygienists must obtain a separate board-issued certificate or permit before they are authorized to administer nitrous oxide analgesia. | true |
| `restorative_function_endorsement_available` | boolean | Whether the state issues a restorative function endorsement or certificate allowing a dental hygienist or dental assistant to place and finish direct restorations prepared by a dentist. | true |
| `interim_therapeutic_restoration_authorized` | boolean | Whether the state expressly authorizes dental hygienists or dental assistants in extended functions to place interim therapeutic restorations using hand instrumentation only. |  |
| `patient_record_retention_years` | integer | The minimum number of years a licensee is required to retain patient dental records after the last date of service. | 7 |
| `cpr_certification_required_for_sedation` | boolean | Whether dentists and auxiliary personnel involved in sedation procedures are required to maintain current certification in basic or advanced cardiac life support. |  |
| `dental_hygienist_alternative_practice_license` | boolean | Whether the state issues a distinct 'alternative practice' or equivalent license category allowing dental hygienists to practice independently in specified community or public health settings without a supervising dentist on-site. | true |

