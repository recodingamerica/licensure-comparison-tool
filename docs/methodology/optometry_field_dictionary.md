# Field dictionary — optometry

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from optometry/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "Board of Examiners in Optometry" |
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
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Board of Examiners in Optometry (NBEO)" |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Optometric Association (AOA)" |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"optometry\" means the examination, evaluation, diagnosis, |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["examination", "evaluation", "diagnosis", "treatment", "per |
| `drug_authority` | string |  | "A licensee may prescribe and use a pharmaceutical agent, in |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

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

