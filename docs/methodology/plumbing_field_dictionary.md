# Field dictionary — plumbing

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from plumbing/AL.

## licensure
_Whether and how the state credentials this profession — the regulatory model, credential type, authority, exams, fees, and renewal._

| field | type | what it means | example value |
|---|---|---|---|
| `license_required` | boolean |  | true |
| `issuing_authority` | string |  | "State of Alabama Plumbers and Gas Fitters Examining Board" |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "All work associated with the installation, repair, or repla |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["installation", "repair", "replacement"] |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `license_tiers` | list | The distinct license classification tiers available for plumbers, from apprentice through master and contractor levels. | ["apprentice plumber", "journeyman plumber", "master plumber |
| `residential_scope_limited` | boolean | Whether a residential-tier plumber license restricts the licensee to work only on residential buildings (typically single or multi-family dwellings up to four units). |  |
| `residential_building_unit_cap` | integer | Maximum number of dwelling units in a building that a residential-tier plumber or contractor license authorizes work on. | 8 |
| `apprentice_supervision_requirement` | string | Description of which license types are authorized to directly supervise a licensed apprentice plumber. | "An apprentice plumber must work directly under the supervis |
| `apprentice_unsupervised_hours_allowed` | integer | Maximum number of hours per 24-hour period that a fourth-year or later apprentice plumber may work without direct supervision. |  |
| `apprentice_unsupervised_training_year_threshold` | integer | The year of apprenticeship training at which an apprentice plumber first becomes eligible to work limited hours without direct supervision. |  |
| `apprentice_to_supervisor_ratio_regulated` | boolean | Whether the statute establishes or delegates authority to set a maximum ratio of apprentice plumbers per supervising licensee. | true |
| `journeyman_experience_pathways` | list | Alternative pathways an applicant may use to satisfy the experience requirement for journeyman plumber licensure. | ["two years of current work experience as an apprentice plum |
| `master_plumber_supervisory_experience_required` | boolean | Whether a master plumber applicant must demonstrate supervisory experience as a journeyman plumber in addition to time-in-grade. | true |
| `expedited_licensure_pathway_available` | boolean | Whether the statute provides an expedited licensure pathway for applicants who can otherwise demonstrate equivalent knowledge and skills. |  |
| `plumbing_trade_geographic_limit_feet` | integer | How many feet beyond the outside walls of a building the plumbing trade definition extends. |  |
| `gas_supply_work_included_in_scope` | boolean | Whether the delivery of gas for lighting, heating, and industrial purposes is explicitly included within the plumbing trade scope. | true |
| `natural_gas_appliance_certification_required` | boolean | Whether a separate certification (beyond the plumbing license) is required before a licensee may install, repair, or replace a residential or commercial gas appliance or combustion system. | false |
| `fire_sprinkler_work_authorized` | boolean | Whether a licensed journeyman plumber is authorized to perform installation, repair, or replacement of water-based fire protection systems. |  |
| `natural_gas_facilities_installation_authorized` | boolean | Whether a licensed plumber (as a qualifying installer) is authorized to install natural gas mains and service lines beyond the building. |  |
| `contractor_qualifier_license_requirement` | enum — one of: master plumber required for general plumbing contractor, master plumber or master residential plumber required for residential plumbing contractor | The specific individual plumber license tier that the qualifier for a plumbing contractor entity must hold. | "master plumber required for general plumbing contractor" |
| `qualifier_replacement_notice_days` | integer | Number of days within which a contractor must notify the licensing division after a qualifier ceases association with the business. |  |
| `qualifier_replacement_grace_period_days` | integer | Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named. |  |
| `long_term_compliance_qualifier_waiver_years` | integer | Number of consecutive violation-free years after which a plumbing or electrical contractor business entity may substitute an active employee license number for a named individual qualifier at renewal. |  |
| `minor_plumbing_repair_exemption` | boolean | Whether the statute provides an exemption from licensure for minor plumbing repair work incidental to fixing a fixture or appliance in a residential or small commercial building, provided no piping or gas system is altered. | true |
| `small_project_dollar_threshold` | integer | Maximum total project cost (labor and materials) below which an unlicensed person may perform certain construction work, with plumbing and electrical systems explicitly excluded from this exemption. |  |
| `continuing_education_hours_plumber` | integer | Number of continuing education hours a licensed plumber (individual, not contractor) must complete per two-year renewal cycle. |  |
| `continuing_education_hours_contractor` | integer | Number of continuing education hours a licensed plumbing contractor must complete per two-year renewal cycle. |  |

