# Discovered fields — hvac

## what the license covers and what work is authorized

### `system_components_included` — list[str]
- **what:** Specific components explicitly included within the definition of an HVAC system for licensing purposes.
- **states:** UT
- **sample (UT):** "'HVAC' means a heating, ventilation, and air conditioning system and the specific components that are a part of the system, including the gas line."

### `gas_appliance_certification_required` — bool
- **what:** Whether persons performing installation, repair, maintenance, or replacement of gas appliances or combustion systems must obtain a separate certification beyond the base contractor license.
- **states:** UT
- **sample (UT):** "Any person described in Subsection (2)(b) that performs work described in Subsection (2)(a): must first receive training and certification as specified in rules adopted by the commission"

### `natural_gas_facilities_installation_authorized` — bool
- **what:** Whether an HVAC contractor is authorized as a qualifying installer to install natural gas mains, service lines, and related facilities.
- **states:** UT
- **sample (UT):** "'Qualifying installer' means a person who: a gas corporation approves to install natural gas facilities; and is: licensed under this chapter; and authorized to install natural gas facilities within the person's scope of practice as established by statute or administrative rule."

### `scope_expansion_by_rule_authorized` — bool
- **what:** Whether the licensing commission may expand the authorized scope of work for an HVAC contractor beyond the statutory definition through administrative rulemaking.
- **states:** UT
- **sample (UT):** "'HVAC contractor' means a person licensed under this chapter specialized in the installation, maintenance, repair, and servicing of heating, ventilation, air conditioning systems or any other work the division authorizes by rule in accordance with Subsection 58-55-301(4)."

## experience and qualifications before getting a license

### `hvac_specific_experience_required` — bool
- **what:** Whether the applicant must demonstrate HVAC-specific (not general construction) paid employment experience.
- **states:** UT
- **sample (UT):** "An applicant for licensure as an HVAC contractor shall produce satisfactory evidence to the division that the applicant: completed two years full-time paid employment of HVAC specific experience."

### `hvac_specific_experience_years` — int
- **what:** Number of years of full-time HVAC-specific paid employment experience required for licensure.
- **states:** UT
- **sample (UT):** "completed two years full-time paid employment of HVAC specific experience"

### `prelicensure_course_hours` — int
- **what:** Number of hours in the required pre-licensure course that must be completed before a contractor license is issued.
- **states:** UT
- **sample (UT):** "complete a 25-hour pre-licensure course that: is taught by an approved pre-licensure course provider"

### `business_law_course_hours` — int
- **what:** Number of hours in a required business and law course that must be completed as part of the licensure process.
- **states:** UT
- **sample (UT):** "complete a five-hour business and law course that: is taught by an approved pre-licensure course provider"

## supervision and delegation

### `qualifier_required` — bool
- **what:** Whether a licensed contractor entity must designate a named individual qualifier who holds the relevant trade license and exercises material authority over the business.
- **states:** UT
- **sample (UT):** "The division shall require a contractor to have a qualifier."

### `qualifier_license_type_required` — list[str]
- **what:** The specific individual trade license(s) that the qualifier for an HVAC contractor entity must hold.
- **states:** UT
- **sample (UT):** "An applicant for licensure as an HVAC contractor shall submit to the division satisfactory evidence that the applicant: completed two-years' full-time, paid employment requiring HVAC specific experience; and passed an examination"

### `qualifier_cessation_notification_days` — int
- **what:** Number of days within which a contractor must notify the licensing division after a qualifier ceases association with the business.
- **states:** UT
- **sample (UT):** "the contractor shall notify the division in writing within 10 days after the day on which the association ceases."

### `qualifier_replacement_grace_period_days` — int
- **what:** Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named.
- **states:** UT
- **sample (UT):** "If notice is given, the contractor's license shall remain in force for 60 days after the day on which the association ceases."

## ongoing training requirements

### `hvac_continuing_education_topic_hours_minimum` — int
- **what:** Minimum number of continuing education hours per renewal cycle that must directly relate to HVAC installation, repair, or replacement.
- **states:** UT
- **sample (UT):** "For an HVAC contractor, at least three of the six required continuing education hours must directly relate to the installation, repair, or replacement of heating, ventilation, or air conditioning systems."

## insurance, bonding, and financial requirements

### `financial_responsibility_demonstration_methods` — list[str]
- **what:** Acceptable methods by which a contractor applicant may demonstrate financial responsibility to the licensing authority.
- **states:** UT
- **sample (UT):** "Before issuing, renewing, or reinstating a contractor license, the division shall require an applicant to demonstrate financial responsibility by: completing a financial responsibility questionnaire the division prepares; and signing the questionnaire and certifying the accuracy of the information provided; or submitting a bond in the form and amount the commission determines by rule"

### `workers_compensation_insurance_required` — bool
- **what:** Whether proof of workers' compensation insurance covering employees must be filed with the division before a license is issued.
- **states:** UT
- **sample (UT):** "Before the division issues a license, the applicant shall file with the division: proof of workers' compensation insurance covering the applicant's employees"

### `public_liability_insurance_required` — bool
- **what:** Whether proof of public liability insurance in division-specified coverage amounts must be filed before a license is issued.
- **states:** UT
- **sample (UT):** "proof of public liability insurance in the coverage amounts and form the division makes by rule in accordance with Title 63G, Chapter 3, Utah Administrative Rulemaking Act"

## exemptions and limits on who must be licensed

### `small_project_exemption_threshold_dollars` — int
- **what:** Dollar threshold below which a project may be performed without a contractor license, subject to stated exclusions.
- **states:** UT
- **sample (UT):** "subject to Subsection (3), a person working on a project that has a total cost of less than $7,000 including labor, material, and changes to the agreed upon work"

### `hvac_exempt_from_small_project_exemption` — bool
- **what:** Whether HVAC system installation, repair, or replacement is explicitly excluded from the general small-project dollar-threshold exemption from licensure.
- **states:** UT
- **sample (UT):** "does not involve the installation, repair, or replacement of a heating, ventilation, or air conditioning system"

## administrative and business operation rules

### `license_number_on_permits_required` — bool
- **what:** Whether the contractor's license number must appear on all permit applications, contracts, agreements, or bids.
- **states:** UT
- **sample (UT):** "The division shall require the contractor's license number on permit applications, contracts, agreements, or bids that require a license."
