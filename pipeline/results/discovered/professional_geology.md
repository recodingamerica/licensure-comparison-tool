# Discovered fields — professional_geology

## pre-licensure candidate status

### `geologist_in_training_certificate_available` — bool
- **what:** Whether the jurisdiction offers a formal geologist-in-training (GIT) certificate as an intermediate credential before full licensure.
- **states:** PA
- **sample (PA):** ""Geologist-in-training" means a candidate for licensure as a professional geologist who has been granted a certificate as a geologist-in-training after successfully passing the required written examination in fundamental geology subjects."

## education requirements specific to geology

### `geology_education_minimum_semester_hours` — int
- **what:** Minimum number of semester hours in geology or closely related geoscience subjects required for licensure eligibility.
- **states:** PA
- **sample (PA):** "Has graduated from an accredited institution of higher learning with a major in geology, geophysics, geochemistry or engineering geology with a minimum of thirty semester or forty-five quarter hours in geology, geophysics, geochemistry, engineering geology or their subdivisions."

### `geology_education_upper_division_minimum_hours` — int
- **what:** Minimum number of semester hours that must be at the third/fourth year or graduate level within the geology coursework requirement.
- **states:** PA
- **sample (PA):** "at least twenty-four semester hours or an equivalent amount are in third or fourth year or graduate courses."

### `accepted_geology_majors` — list[str]
- **what:** List of academic majors or concentrations accepted as satisfying the geology degree requirement.
- **states:** PA
- **sample (PA):** "a major in geology, geophysics, geochemistry or engineering geology"

## experience requirements for geologists

### `professional_geology_experience_years_required` — int
- **what:** Total minimum years of professional geological work experience required for licensure.
- **states:** PA
- **sample (PA):** "Has completed at least five years of professional geological work, which shall include either a minimum of three years of professional geological work under the supervision of a licensed professional geologist or a minimum of five years experience in a responsible position in professional geological work."

### `supervised_experience_years_required` — int
- **what:** Minimum years of the total experience requirement that must be performed under supervision of a licensed professional geologist.
- **states:** PA
- **sample (PA):** "a minimum of three years of professional geological work under the supervision of a licensed professional geologist"

### `graduate_study_experience_credit_max_years` — int
- **what:** Maximum number of years of graduate study that may be credited toward the professional geological work experience requirement.
- **states:** PA
- **sample (PA):** "Credit for graduate study may not exceed a total of two years toward meeting the required number of years of professional geological work."

### `excluded_experience_types` — list[str]
- **what:** Types of work explicitly excluded from counting as qualifying professional geological experience.
- **states:** PA
- **sample (PA):** "professional geological work does not include routine sampling, laboratory work or geological drafting."

## what geologists can and cannot do

### `scope_excludes_professions` — list[str]
- **what:** Other licensed professions whose practice is explicitly excluded from the definition of geology practice, requiring separate licensure.
- **states:** PA
- **sample (PA):** "The term shall not include the practice of engineering, land surveying or landscape architecture for which separate licensure is required."

### `incidental_geology_exemption` — bool
- **what:** Whether holders of other professional licenses (e.g., engineers, surveyors) may perform geological work that is incidental to their primary licensed practice without a geology license.
- **states:** PA
- **sample (PA):** "Individuals licensed as professional engineers, professional land surveyors or registered landscape architects may perform geological work which is incidental to their engineering, surveying or landscape architecture without being licensed as a professional geologist."

### `oil_gas_exploration_exemption` — bool
- **what:** Whether individuals providing geologic services to oil or gas exploration businesses are exempt from licensure requirements.
- **states:** PA
- **sample (PA):** "The practice of individuals providing geologic services to businesses engaged in the exploration or development of gas or oil."

## professional seal and document signing

### `professional_seal_required` — bool
- **what:** Whether a licensed professional geologist is required to obtain and use an official seal on plans, specifications, and reports.
- **states:** PA
- **sample (PA):** "Each person, registered under this act, shall obtain a seal of a design authorized by the board which shall bear the registrant's name and number and the legend ... "Registered Professional Geologist." Such seal, or a facsimile imprint of same, shall be stamped on all plans, specifications, plats and reports issued by a professional ... geologist."

## continuing education specifics

### `pdh_units_per_renewal_period` — int
- **what:** Number of Professional Development Hours (PDH) required per biennial renewal period.
- **states:** PA
- **sample (PA):** "Each licensee shall be required to obtain twenty-four PDH units during the biennial renewal period."

### `pdh_carryover_max_units` — int
- **what:** Maximum number of excess PDH units that may be carried forward into the next renewal period.
- **states:** PA
- **sample (PA):** "If a licensee exceeds the requirement in any renewal period, a maximum of twelve PDH units may be carried forward into the subsequent renewal period."

### `retired_status_license_available` — bool
- **what:** Whether the jurisdiction offers a retired-status license that exempts the holder from continuing education requirements.
- **states:** PA
- **sample (PA):** "A licensee who lists his occupation as retired on the board-approved renewal form and certifies to the board that he no longer engages in the practice of his licensed profession shall be exempt from the requirement set forth in subsection (a), and the board shall issue him a retired-status license."

## governance and board structure

### `combined_licensing_board` — bool
- **what:** Whether geology licensure is administered by a board that also oversees other professions (e.g., engineers and land surveyors) rather than a standalone geology board.
- **states:** PA
- **sample (PA):** "There is hereby established within the Department of State the State Registration Board for Professional Engineers, Land Surveyors and Geologists."

### `geologist_board_member_seats` — int
- **what:** Number of seats on the licensing board reserved for registered professional geologists.
- **states:** PA
- **sample (PA):** "nine members appointed by the Governor, five of whom shall be registered professional engineers, two of whom shall be registered professional land surveyors and two of whom shall be registered professional geologists."

### `multiple_licensure_reporting_required` — bool
- **what:** Whether licensees holding geology licenses in other jurisdictions must report that fact and any out-of-state disciplinary actions to the home-state board.
- **states:** PA
- **sample (PA):** "Any licensee of this Commonwealth who is also licensed to practice engineering, land surveying or geology in any other state, territory or country shall report this information to the board on the biennial renewal application."
