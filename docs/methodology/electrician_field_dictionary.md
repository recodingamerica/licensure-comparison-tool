# Field dictionary — electrician

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from electrician/AK.

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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"electrical administrator\" means a person who is responsi |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["installing electrical wiring, conduits, devices, fixtures, |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `license_tiers` | list | The named tiers or classifications of electrician license available in the state, from apprentice through master and including residential variants. | ["electrical administrator"] |
| `residential_project_definition` | string | Statutory definition of what constitutes a 'residential project' for purposes of limiting or distinguishing residential electrician license scope. |  |
| `residential_wiring_method_restriction` | boolean | Whether the residential-tier electrician license is restricted to work on buildings primarily wired with nonmetallic sheathed (NM) cable. |  |
| `voltage_limit_residential` | integer | Maximum voltage (line-to-line) permitted under a residential electrician license classification. |  |
| `scope_exclusions` | list | Specific categories of work explicitly excluded from the definition of the electrical trade and therefore not requiring an electrician license. | ["utility or municipality: electrical construction and maint |
| `minor_electrical_work_amperage_limit` | integer | Maximum amperage for minor electrical work incidental to a mechanical or service installation that is excluded from the licensed electrical trade. |  |
| `minor_electrical_work_distance_limit_feet` | integer | Maximum distance in feet that wiring may be extended from an existing outlet or disconnect to qualify as minor electrical work excluded from licensure. |  |
| `apprentice_supervision_ratio` | string | The maximum ratio of licensed apprentice electricians permitted under the immediate supervision of one licensed supervisor, as set by rule. |  |
| `apprentice_unsupervised_hours_allowed` | integer | Maximum hours per 24-hour period that a fourth-year or later apprentice electrician may work without direct supervision. |  |
| `apprentice_unsupervised_year_threshold` | integer | The year of apprenticeship training at which an apprentice electrician first becomes eligible to work limited hours without direct supervision. |  |
| `residential_apprentice_supervisor_ratio_max` | integer | Maximum number of apprentice electricians a licensed supervisor may oversee on a residential project. |  |
| `qualifier_required` | boolean | Whether a licensed electrical contractor entity must designate a qualifying individual who holds the relevant journeyman or master license and exercises material authority over the business. | true |
| `qualifier_license_requirement_by_contractor_type` | list | The specific electrician license tier that the qualifier for each type of electrical contractor must hold. |  |
| `qualifier_replacement_notice_days` | integer | Number of days within which a contractor must notify the licensing division in writing after a qualifier ceases association with the business. |  |
| `qualifier_replacement_grace_period_days` | integer | Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named. |  |
| `long_term_compliance_qualifier_waiver_years` | integer | Number of consecutive years of violation-free licensure after which an electrical contractor business entity may substitute an active licensed employee name for a named individual qualifier at renewal. |  |
| `journeyman_electrician_apprenticeship_hours` | integer | Minimum hours of full-time apprenticeship training required to qualify for a journeyman electrician license via the apprenticeship pathway. |  |
| `journeyman_electrician_experience_alternative_years` | integer | Years of full-time electrical experience accepted as an alternative pathway to journeyman electrician licensure in lieu of a formal apprenticeship. |  |
| `master_electrician_journeyman_experience_years` | integer | Years of practical experience as a journeyman electrician required to qualify for a master electrician license via the experience pathway. |  |
| `master_electrician_engineering_degree_pathway` | boolean | Whether a graduate electrical engineering degree from an accredited institution, combined with reduced practical experience, is an accepted pathway to master electrician licensure. |  |
| `master_electrician_trade_school_degree_pathway` | boolean | Whether an associate of applied sciences degree from an approved electrical trade school, combined with journeyman experience, is an accepted pathway to master electrician licensure. |  |
| `residential_journeyman_training_program_years` | integer | Minimum years of training in a division-approved electrical training program accepted as a pathway to residential journeyman electrician licensure. |  |
| `residential_master_electrician_journeyman_experience_years` | integer | Minimum years of practical experience as a residential journeyman electrician required to qualify for a residential master electrician license. |  |
| `expedited_licensure_pathway_available` | boolean | Whether an expedited licensure pathway exists for applicants who can clearly demonstrate equivalent knowledge and skills without meeting the standard experience or training requirements. |  |
| `electrician_continuing_education_hours` | integer | Total hours of continuing education a licensed electrician (journeyman through master) must complete per two-year renewal cycle. |  |
| `approved_continuing_education_providers` | list | Named organizations whose courses are approved to satisfy electrician continuing education requirements. |  |
| `national_electrical_code_reference` | boolean | Whether the statute explicitly references the National Electrical Code as the governing standard for electrical work. | true |
| `gas_appliance_work_certification_required` | boolean | Whether electricians or contractors performing installation, repair, or replacement of gas appliances or combustion systems must obtain a separate certification beyond their electrician license. |  |
| `small_project_dollar_threshold_exemption` | integer | Maximum total project cost (labor and materials) below which a person may perform certain construction work without a contractor license, with electrical and plumbing work explicitly excluded from this exemption. | 5000 |
| `solar_panel_electrical_work_exemption` | boolean | Whether electrical work incidental to installing or repairing solar panels is exempt from standard electrician licensure requirements. |  |
| `hot_tub_sign_electrical_exemption` | boolean | Whether electrical work incidental to installing or repairing an above-ground prebuilt hot tub or on-premise signage is exempt from electrician licensure. |  |
| `utility_worker_exemption` | boolean | Whether persons employed by electric utilities, railroads, telephone corporations, or municipal utilities are exempt from electrician licensure for work incidental to those employers' operations. | true |
| `financial_responsibility_bond_option` | boolean | Whether an electrical contractor applicant may satisfy the financial responsibility requirement by submitting a surety bond as an alternative to completing a financial questionnaire. |  |
| `workers_compensation_insurance_required` | boolean | Whether proof of workers' compensation insurance covering employees is required before the division will issue an electrical contractor license. |  |
| `public_liability_insurance_required` | boolean | Whether proof of public liability insurance in division-specified amounts is required before the division will issue an electrical contractor license. |  |

