# Discovered fields — insurance_navigator

## license types and scope of service

### `navigator_line_of_authority` — enum[navigator, certified application counselor]
- **what:** The specific line of authority granted under a navigator license, distinguishing full navigator authority from the more limited certified application counselor authority.
- **states:** NY, UT
- **sample (UT):** "A license type under this chapter shall be a navigator line of authority or a certified application counselor line of authority."

### `scope_limited_to_exchange_plans` — bool
- **what:** Whether the navigator's authorized activities are restricted to plans and programs offered on a health benefit exchange, prohibiting assistance with off-exchange products.
- **states:** NY, UT
- **sample (UT):** "may perform, offer to perform, or advertise a service as a navigator only for a person selecting a qualified health plan or public program offered on an exchange; and may not perform, offer to perform, or advertise services as a navigator for individuals or small employer groups selecting accident and health insurance plans, qualified health plans, public programs, business, or services that are not offered on an exchange"

### `plan_recommendation_prohibited` — bool
- **what:** Whether the navigator is explicitly prohibited from recommending a particular health plan to a consumer.
- **states:** NY, UT
- **sample (UT):** "may not recommend a particular accident and health insurance plan or qualified health plan"

### `insurance_sales_prohibited` — bool
- **what:** Whether the navigator is explicitly prohibited from selling insurance.
- **states:** NY, UT
- **sample (NY):** "does not sell insurance"

### `public_programs_covered` — list[str]
- **what:** The public health programs (e.g., Medicaid, CHIP) that navigators are authorized to assist consumers in enrolling in.
- **states:** NY, UT
- **sample (UT):** ""Public programs" means the state Medicaid program in Title 26B, Chapter 3, Health Care - Administration and Assistance, and Title 26B, Chapter 3, Part 9, Utah Children's Health Insurance Program."

### `premium_subsidy_assistance_authorized` — bool
- **what:** Whether the navigator is authorized to assist consumers with applying for premium subsidies through the exchange.
- **states:** NY, UT
- **sample (UT):** "applying for premium subsidies through an exchange"

## how navigators are authorized and overseen

### `federal_grant_or_certification_required` — bool
- **what:** Whether the navigator must have received a grant from and been certified by the health benefit exchange established under the ACA as a condition of operating.
- **states:** NY, UT
- **sample (NY):** "any person who has received a grant from and has been certified by the health benefit exchange established pursuant to section 1311 of the affordable care act, 42 U.S.C. § 18031, to act as a navigator"

### `federal_training_completion_required` — bool
- **what:** Whether the navigator must complete the training program required by the health benefit exchange (including CMS-developed programs) as a condition of licensure.
- **states:** NY, UT
- **sample (NY):** "has completed the training required by the health benefit exchange"

### `cms_training_program_required` — bool
- **what:** Whether the navigator's pre-license training must specifically include the training and certification program developed by the Centers for Medicare and Medicaid Services.
- **states:** NY, UT
- **sample (UT):** "the training required by Subsection (1) shall consist of at least 21 credit hours of training before obtaining the license, which shall include the navigator training and certification program developed by the Centers for Medicare and Medicaid Services"

### `pre_license_training_hours` — int
- **what:** Minimum number of training credit hours required before obtaining a navigator license (for the full navigator line of authority).
- **states:** NY, UT
- **sample (UT):** "the training required by Subsection (1) shall consist of at least 21 credit hours of training before obtaining the license"

### `conflict_of_interest_standards_required` — bool
- **what:** Whether the navigator must comply with conflict-of-interest standards established by federal PPACA regulations, including as part of training and character requirements.
- **states:** NY, UT
- **sample (UT):** "the applicant does not have a conflict of interest as defined by regulations issued under PPACA"

## compensation and financial rules

### `compensation_source_restrictions` — list[str]
- **what:** Entities from which a navigator is prohibited from receiving direct or indirect compensation for navigator services.
- **states:** NY, UT
- **sample (NY):** "does not receive any compensation for acting as a navigator directly or indirectly from an insured, insurance producer, or an insurer"

### `exchange_compensation_permitted` — bool
- **what:** Whether the navigator may be compensated by the exchange itself for performing navigator duties.
- **states:** NY, UT
- **sample (UT):** "may be compensated by the exchange for performing the duties of a navigator"

### `surety_bond_required` — bool
- **what:** Whether the navigator is required to obtain and maintain a surety bond to cover legal liability arising from erroneous acts or failures to act.
- **states:** NY, UT
- **sample (UT):** "a navigator shall obtain a surety bond in an amount designated by the commissioner by administrative rule to cover the legal liability of the navigator as the result of an erroneous act or failure to act in the navigator's capacity as a navigator"

### `fiduciary_funds_prohibited` — bool
- **what:** Whether the navigator is explicitly prohibited from receiving, collecting, or holding funds that would constitute fiduciary funds under insurance law.
- **states:** NY, UT
- **sample (NY):** "A person who has received a grant from and has been certified by the health benefit exchange ... shall not receive, collect or hold any funds that would constitute fiduciary funds within the meaning of section two thousand one hundred twenty of this article."

## individual and agency licensing structure

### `agency_license_available` — bool
- **what:** Whether a navigator agency (organizational) license is available in addition to individual navigator licenses.
- **states:** NY, UT
- **sample (UT):** "An organization shall be licensed as a navigator agency if the organization acts as a navigator."

### `designated_responsible_individual_required` — bool
- **what:** Whether a navigator agency must designate a specific licensed individual responsible for the agency's compliance with navigator laws and regulations.
- **states:** NY, UT
- **sample (UT):** "A navigator agency that does business in the state shall designate an individual who is licensed under this chapter to act on the agency's behalf."

### `license_term_years` — int
- **what:** Duration in years of a navigator license before renewal is required.
- **states:** NY, UT
- **sample (UT):** "A license issued under this chapter is valid for one year."

## who does not need a navigator license

### `licensing_exemptions` — list[str]
- **what:** Categories of persons or entities explicitly exempt from the navigator licensing requirement.
- **states:** NY, UT
- **sample (UT):** "The commissioner may not require a license as a navigator of: a person who is employed by or contracts with a health care facility ... to assist an individual with enrollment in a public program or an application for premium subsidy; a federally qualified health center ... an Indian health clinic or Urban Indian Health Center"

## training content requirements

### `cultural_and_linguistic_competence_training_required` — bool
- **what:** Whether navigator training must include cultural and linguistic competence as a required topic.
- **states:** NY, UT
- **sample (UT):** "The training required by Subsection (1) shall be approved by the commissioner and shall include: ... cultural and linguistic competence"

### `continuing_education_ethics_hours_required` — int
- **what:** Minimum number of continuing education hours per renewal period that must be dedicated to ethics courses.
- **states:** NY, UT
- **sample (UT):** "that at least two of the 12 credit hours described in Subsection (3)(a)(i) be ethics courses"

### `annual_cms_recertification_required` — bool
- **what:** Whether navigators must complete the annual CMS navigator or certified application counselor training and certification program as part of continuing education each license period.
- **states:** NY, UT
- **sample (UT):** "that a licensee complete the annual navigator training and certification program developed by the Centers for Medicare and Medicaid Services"
