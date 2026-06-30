# Field dictionary — construction_trades

_Auto-generated from the extraction model (`standard_model.py` + the profession's discovered schema). Do not edit by hand — regenerate with `python -m pipeline.publish.generate_field_dictionary`._

Every field is an **Evidence** object: a `value`, the verbatim `quote` from the statute that supports it, and the `citation` it came from. Examples below are sampled from construction_trades/AK.

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
| `national_association` | string | Professional ASSOCIATION the state references (e.g. for accreditation or CE provider approval) — 'American Podiatric Medical Association (APMA)', 'American Dental Association (ADA)'. Distinct from the certifying body. Null if not referenced. | "American Society of Home Inspectors; National Association o |
| `regulatory_model` | enum — one of: market_forces, voluntary_certification, registration, exemption, mandatory_certification, license | Which UORF model the state applies to this profession (license / mandatory_cert / registration / etc). | "registration" |
| `credential_type` | enum — one of: none, registration, certification, license, exemption | What SHAPE of credential does the state issue, independent of whether holding it is mandatory? license / certification / registration / exemption / none. Pairs with is_mandatory to decompose the legacy regulatory_model rung. | "registration" |
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
| `definition_quote` | string | Verbatim statutory definition; quote field repeats the value text. | "\"contractor\" means a person who, in the pursuit of an ind |
| `methods_authorized` | list | High-level methods, e.g. ['medical','surgical','mechanical'] | ["construct", "alter", "repair", "move", "demolish", "excava |
| `drug_authority` | string |  |  |
| `citations` | list |  |  |

## profession_specific
_Fields discovered specifically for this profession (auto-derived from its statutes; they vary profession to profession)._

| field | type | what it means | example value |
|---|---|---|---|
| `registration_number_required_in_ads` | boolean | Whether the contractor's registration number must appear in all advertisements, contracts, estimates, and proposals. | true |
| `insurance_personal_injury_minimum_usd` | integer | Minimum dollar amount of liability insurance covering personal injury that a contractor must maintain. | 50000 |
| `insurance_property_damage_minimum_usd` | integer | Minimum dollar amount of insurance covering property damage caused by the contractor's work. | 20000 |
| `self_insurance_permitted` | boolean | Whether a contractor may satisfy insurance requirements by attesting to being self-insured rather than carrying a third-party policy. | true |
| `contract_must_be_written` | boolean | Whether a home improvement contract must be in writing to be valid and enforceable against the owner. |  |
| `right_of_rescission_days` | integer | Number of business days within which an owner may rescind a signed home improvement contract without penalty. |  |
| `deposit_cap_fraction` | string | Maximum fraction of the total contract price a contractor may collect as a deposit before work begins, for contracts above a threshold amount. |  |
| `deposit_cap_contract_threshold_usd` | integer | Minimum contract price above which the deposit cap rule applies. |  |
| `change_order_must_be_written` | boolean | Whether any deviation from the original plans or specifications requires a written change order signed by both parties. |  |
| `arbitration_clause_allowed` | boolean | Whether a home improvement contract may include an arbitration clause, subject to specific formatting and disclosure requirements. |  |
| `voidable_contract_clauses` | list | List of clause types that, if included in a home improvement contract, make the contract voidable by the owner. |  |
| `minimum_annual_revenue_threshold_usd` | integer | Minimum total cash value of home improvements in the prior taxable year below which a person is exempt from contractor registration. |  |
| `minimum_project_value_usd` | integer | Minimum cash price of a single project for the work to qualify as a regulated home improvement requiring a registered contractor. |  |
| `fraud_offense_defined` | boolean | Whether the statute defines a specific criminal offense of home improvement fraud with enumerated prohibited acts. |  |
| `fraud_felony_threshold_usd` | integer | Dollar amount above which a home improvement fraud violation is graded as a felony rather than a misdemeanor. |  |
| `enhanced_penalty_for_elderly_victims` | boolean | Whether the grading of a fraud offense is elevated by one level when the victim is 60 years of age or older. |  |
| `state_preempts_local_registration_fees` | boolean | Whether state registration preempts local governments from imposing their own contractor registration fees or licensing requirements. |  |
| `local_trade_licensing_preserved` | boolean | Whether existing local licensing standards for specific trades (e.g., electricians, plumbers) are preserved notwithstanding state preemption. |  |
| `registration_renewal_interval_years` | integer | How often, in years, a contractor must renew their registration with the issuing authority. | 2 |
| `out_of_state_disciplinary_action_reporting_required` | boolean | Whether a contractor must report to the state any disciplinary action taken against them in another jurisdiction. |  |

