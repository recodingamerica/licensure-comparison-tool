# Field dictionary — architecture

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from architecture/AK.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "State Board of Registration for Architects, Engineers, and  |
| `regulatory_authority` | RegulatoryAuthority | Structured decomposition of the issuing authority — name, type (standalone board / shared board / division / department / joint), and any umbrella agency it sits within. Populated alongside the legacy free-text issuing_authority for back-compat. |  |
| `age_minimum` | integer |  |  |
| `moral_character_required` | boolean |  | true |
| `education` | EducationRequirement |  |  |
| `post_degree_experience` | PostDegreeExperience | Residency / supervised practice / apprenticeship — name varies, structure doesn't. |  |
| `exams` | list |  |  |
| `renewal` | Renewal |  |  |
| `renewal_fee_usd` | integer | License renewal fee in US dollars (integer). Many statutes leave the amount to the board's discretion — leave null in that case. |  |
| `continuing_education` | ContinuingEducation |  |  |
| `reciprocity` | Reciprocity |  |  |
| `advisory_board` | AdvisoryBoard | Profession-specific advisory body sitting alongside the main licensing board, when one exists. Populated for states that delegate licensure to a generic board and add a specialty advisory committee. |  |
| `national_certification` | string | Name of a national CERTIFICATION the state recognizes or requires, e.g. 'American Board of Podiatric Surgery (ABPS)' or 'National Board of Podiatric Medical Examiners (NBPME)'. The certifying body, NOT the association. Null if the statute doesn't reference one. | "National Council of Architectural Registration Boards (NCAR |
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. |  |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"practice of architecture\" means professional service or  |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["design of buildings", "consultation", "investigation", "ev |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

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

