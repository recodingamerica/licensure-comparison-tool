# Discovered fields — building_inspector

## inspector credentials and certification tiers

### `certification_categories` — list[str]
- **what:** The distinct categories of code administrator certification established by the department (e.g., residential building inspector, fire inspector, plans examiner).
- **states:** PA
- **sample (PA):** "One member who must be a Uniform Construction Code-certified residential building inspector, possess all five residential certifications from an association representing building code officials and have experience administering and enforcing residential codes."

### `decertification_authority` — bool
- **what:** Whether the issuing authority has explicit statutory power to decertify code administrators for just cause.
- **states:** PA
- **sample (PA):** "The department is empowered to decertify code administrators for just cause. The department shall by regulation establish a procedure for the notification of code administrators of decertification and the right of the individual to receive a hearing before the department on decertification."

### `certification_waiver_available` — bool
- **what:** Whether the department may waive initial training and certification requirements for individuals who demonstrate substantially similar prior training or experience.
- **states:** PA
- **sample (PA):** "The department shall by regulation establish a procedure for the consideration of requests for waivers of the initial training and certification requirements for individuals who present documentation that they have previously satisfied substantially similar training, testing and certification requirements."

### `remedial_education_authority` — bool
- **what:** Whether the issuing authority has explicit statutory power to require code administrators to participate in remedial education programs.
- **states:** PA
- **sample (PA):** "The department is empowered to require code administrators to participate in remedial education programs for just cause."

## practice setting and liability rules

### `third_party_agency_insurance_required` — bool
- **what:** Whether code administrators working in third-party agencies are required by regulation to carry minimum levels of liability insurance.
- **states:** PA
- **sample (PA):** "The department shall promulgate regulations requiring code administrators in third-party agencies to carry minimum levels of liability insurance."

### `financial_interest_prohibition` — bool
- **what:** Whether a code administrator is prohibited from reviewing or approving plans for any building or structure in which the administrator has a financial interest.
- **states:** PA
- **sample (PA):** "A code administrator shall not review or approve any plans for or construction of any building or structure in which the code administrator has any financial interest."

## permit review and inspection timelines

### `permit_application_decision_deadline_days` — int
- **what:** The maximum number of business days within which a permit application must be granted or denied (for one- and two-family dwellings and miscellaneous structures).
- **states:** PA
- **sample (PA):** "Every application for a construction permit for one-family and two-family dwelling units and utility and miscellaneous use structures shall be granted or denied, in whole or in part, within 15 business days of the filing date."

### `required_inspection_stages` — list[str]
- **what:** The specific mandatory inspection stages that must be completed for residential construction.
- **states:** PA
- **sample (PA):** "For one-family and two-family dwelling units and utility and miscellaneous use structures, all of the following five inspections shall be required: Foundation inspection. Plumbing, mechanical and electrical inspection. Frame and masonry inspection. Wallboard inspection. Final inspection."

### `deemed_approved_if_no_action` — bool
- **what:** Whether a permit application is automatically deemed approved if the code administrator fails to act within the prescribed time period.
- **states:** PA
- **sample (PA):** "If the code administrator fails to act on an application for a construction permit for one-family and two-family dwelling units and utility and miscellaneous use structures within the time prescribed, the application shall be deemed approved."

## code adoption and enforcement framework

### `adopted_model_code` — str
- **what:** The specific model building code or code family adopted as the statewide uniform construction standard.
- **states:** PA
- **sample (PA):** "The department shall, within 180 days of the effective date of this section, promulgate regulations adopting the 1999 BOCA National Building Code, Fourteenth Edition, as a Uniform Construction Code."

### `state_preempts_local_codes` — bool
- **what:** Whether the statewide construction code preempts local municipal building codes and ordinances.
- **states:** PA
- **sample (PA):** "The regulations adopted by the department implementing these codes shall supersede and preempt all local building codes regulating any aspect of the construction, alteration and repair of buildings adopted or enforced by any municipality."

### `municipality_may_exceed_minimum` — bool
- **what:** Whether municipalities are permitted to enact ordinances that equal or exceed (but not fall below) the minimum requirements of the statewide construction code.
- **states:** PA
- **sample (PA):** "Subject to the provisions of this act, the municipal governing body may propose and enact an ordinance to equal or exceed the minimum requirements of the Uniform Construction Code under the law governing the adoption of ordinances in that jurisdiction."

### `enforcement_delivery_options` — list[str]
- **what:** The permissible methods by which a municipality may administer and enforce the construction code (e.g., municipal employee, third-party agency, intermunicipal agreement).
- **states:** PA
- **sample (PA):** "This act may be administered and enforced by municipalities in any of the following ways: By the designation of an employee to serve as the municipal code official... By the retention of one or more construction code officials or third-party agencies... Two or more municipalities may provide for the joint administration and enforcement."

## appeals and variance process

### `board_of_appeals_required` — bool
- **what:** Whether municipalities that adopt the construction code are required to establish or designate a board of appeals.
- **states:** PA
- **sample (PA):** "A municipality which has adopted an ordinance for the administration and enforcement of this act or municipalities which are parties to an agreement for the joint administration and enforcement of this act shall establish or designate a board of appeals."

## accessibility oversight and requirements

### `accessibility_advisory_board_exists` — bool
- **what:** Whether a dedicated advisory board exists to review and advise on accessibility code requirements.
- **states:** PA
- **sample (PA):** "There is hereby created an Accessibility Advisory Board which shall be composed of 11 members, seven of which shall be appointed by the secretary."

### `accessibility_certification_required` — bool
- **what:** Whether code administrators must obtain specific certification covering accessibility provisions of the construction code.
- **states:** PA
- **sample (PA):** "One member who must be a Uniform Construction Code-certified building inspector, who possesses all nonresidential inspection certifications but does not need to possess a fire inspector certification, or a certified plans examiner, who holds an accessibility certification from an association representing building code officials."

## buildings and structures exempt from the code

### `exempt_building_types` — list[str]
- **what:** Categories of buildings or structures explicitly excluded from the application of the statewide construction code.
- **states:** PA
- **sample (PA):** "This act shall not apply to any of the following: Any agricultural building... Any recreational cabin... Temporary structures... Structures used to load, unload or sort livestock at livestock auction facilities."
