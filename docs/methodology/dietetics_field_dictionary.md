# Field dictionary — dietetics

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from dietetics/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "Department of Commerce, Community, and Economic Development |
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
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "Commission on Dietetic Registration" |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Dietetic Association" |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "voluntary_certification" |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "license" |
| `is_mandatory` | boolean | Is the credential MANDATORY to practice (or claim the title) in this state? True if practicing without it is prohibited; False if optional (e.g., voluntary certification that only protects the title for those who hold it). | true |
| `title_protection` | boolean | Does the state restrict use of the profession's title to licensees? True if unlicensed people may NOT call themselves the protected title (e.g. 'podiatrist', 'CPA'). | true |
| `scope_protection` | boolean | Does the state restrict practice of the profession's scope to licensees? True if performing the scope without a license is prohibited (independent of title use). | false |
| `disciplinary_grounds` | list | Grounds on which the board may discipline a licensee. Typical statutes list 5-15. |  |
| `alternative_regulation` | AlternativeRegulation | Non-credential regulatory mechanisms (bonding, insurance, establishment regulation) imposed by the state. Obama 2015 framework typology. Independent of credential_type. |  |
| `citations` | list |  |  |

## scope
_What the practice act lets (or reserves to) this profession — the defined scope and any title/scope protection._

| field | type | what it means | example value |
|---|---|---|---|
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "the integration and application of scientific principles of |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] |  |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `license_type_structure` | list | The distinct credential or license types recognized by the state (e.g., licensed dietitian, licensed nutritionist, dietitian-nutritionist, registered dietitian, provisionally licensed dietitian). | ["licensed dietitian", "licensed nutritionist"] |
| `provisional_license_available` | boolean | Whether the state offers a provisional or temporary license allowing practice under supervision while completing full licensure requirements. |  |
| `provisional_license_duration_months` | integer | Duration in months of a provisional or temporary license before it expires. |  |
| `provisional_license_requires_supervision` | boolean | Whether a provisional or temporary license restricts the holder to practice only under the supervision of a fully licensed dietitian. |  |
| `dietetic_technician_recognized` | boolean | Whether the state statute explicitly recognizes a dietetic technician credential as a distinct, lower-tier role that may perform limited functions under supervision. |  |
| `rd_credential_accepted_in_lieu_of_state_requirements` | boolean | Whether holding a current Registered Dietitian (RD/RDN) credential from the Commission on Dietetic Registration is explicitly accepted as satisfying all or most state licensure requirements. | true |
| `alternative_credential_pathways` | list | Non-RD national credentials or membership bodies that the state accepts as an alternative pathway to licensure (e.g., Certified Nutrition Specialist, American Board of Nutrition diplomate). | ["American Board of Nutrition diplomate", "Certified Nutriti |
| `medical_nutrition_therapy_authorized` | boolean | Whether the statute explicitly authorizes the practice of 'medical nutrition therapy' as part of the dietitian's scope. |  |
| `enteral_parenteral_nutrition_authorized` | boolean | Whether the statute explicitly includes ordering or recommending enteral and/or parenteral nutrition within the dietitian's scope of practice. |  |
| `diet_order_writing_authority` | boolean | Whether the statute explicitly grants dietitians authority to write or issue diet orders (including therapeutic diets) in institutional or hospital settings. |  |
| `lab_test_ordering_authority` | boolean | Whether the statute explicitly grants dietitians authority to order medical laboratory tests related to nutrition therapy. |  |
| `physician_referral_required` | boolean | Whether the statute requires a physician (or other authorized prescriber) referral or order before a dietitian may provide certain clinical nutrition services. |  |
| `diagnosis_treatment_prohibition` | boolean | Whether the statute explicitly prohibits dietitians from diagnosing, treating, or prescribing for human illness or otherwise practicing medicine. |  |
| `telehealth_practice_authorized` | boolean | Whether the statute explicitly authorizes dietitians to provide services via telehealth. |  |
| `supervision_ratio_limit` | integer | Maximum number of dietetic technicians a single registered dietitian may supervise at one time. |  |
| `direct_supervision_defined` | boolean | Whether the statute provides an explicit definition of 'direct supervision' for dietetic technicians or provisional licensees, including physical presence or availability requirements. |  |
| `exempt_professions_list` | list | Categories of other licensed professionals explicitly exempted from the dietetics licensure requirement when performing nutrition-related activities incidental to their own profession. | ["animal nutritionist (limited to nutritional care of animal |
| `federal_employee_exemption` | boolean | Whether persons employed by the federal government (including armed forces, VA, or public health service) in a dietitian or nutritionist role are explicitly exempt from state licensure. | true |
| `weight_control_program_exemption` | boolean | Whether persons offering weight control programs are explicitly exempt from licensure, typically conditioned on the program being reviewed or approved by a licensed or registered dietitian. |  |
| `food_supplement_sales_exemption` | boolean | Whether persons who sell, market, or provide information about food, dietary supplements, vitamins, or herbs are explicitly exempt from the dietetics licensure requirement. |  |
| `animal_nutrition_exemption` | boolean | Whether persons whose nutrition practice is limited to animals are explicitly exempt from the human dietetics licensure requirement. | true |
| `nonresident_temporary_practice_allowed` | boolean | Whether out-of-state dietitians may practice in the state for a limited period without obtaining a state license. |  |
| `nonresident_temporary_practice_max_days` | integer | Maximum number of days per year a nonresident dietitian may practice in the state without a state license. |  |
| `interstate_compact_member` | boolean | Whether the state has enacted the Dietitian Licensure Compact, enabling multistate practice privileges. |  |
| `compact_privilege_jurisprudence_requirement` | boolean | Whether a state may require applicants for a compact practice privilege to pass a jurisprudence (state law knowledge) assessment. |  |
| `protected_titles` | list | The specific titles, words, letters, or abbreviations that are legally restricted to licensed or certified practitioners under the statute. | ["dietitian", "licensed dietitian", "nutritionist", "license |
| `nutrition_assessment_includes_biochemical_data` | boolean | Whether the statutory definition of nutritional assessment explicitly includes biochemical and anthropometric data as evaluation components. |  |
| `hospital_order_authority_requires_policy` | boolean | Whether a dietitian's authority to issue orders in a hospital setting is conditioned on the hospital having written policies and procedures authorizing such orders. |  |
| `inactive_license_status_available` | boolean | Whether the state allows a licensee to place their license in an inactive status for a defined period. |  |
| `ethics_code_violation_grounds_for_discipline` | boolean | Whether violation of a recognized professional code of ethics (e.g., the American Dietetic Association's code) is explicitly listed as a ground for disciplinary action. |  |

