# Discovered fields — health_facility_admin

## license types and temporary credentials

### `provisional_license_available` — bool
- **what:** Whether a provisional (temporary pre-full-licensure) license category exists for this profession.
- **states:** PA
- **sample (PA):** ""Provisional license" is a temporary license issued to a provisional nursing home administrator."

### `temporary_permit_available` — bool
- **what:** Whether a temporary permit may be issued without examination in emergency or unusual circumstances (e.g., death or resignation of the licensed administrator).
- **states:** PA
- **sample (PA):** "In the event of unusual circumstances affecting the administration of a nursing home, such as death or disability of the licensed administrator, his resignation or dismissal, or other valid reasons as determined by the board, the board may, in its discretion, issue without examination a temporary permit as nursing home administrator."

### `temporary_permit_max_duration_months` — int
- **what:** Maximum duration in months for a temporary permit issued without examination.
- **states:** PA
- **sample (PA):** "A temporary permit shall entitle the holder to serve as a nursing home administrator only in the particular facility indicated on his application, and shall be valid for a period as determined by the board, not to exceed one year from the date of issuance."

### `temporary_permit_facility_restricted` — bool
- **what:** Whether a temporary permit restricts the holder to practice only at the single facility named on the application.
- **states:** PA
- **sample (PA):** "A temporary permit shall entitle the holder to serve as a nursing home administrator only in the particular facility indicated on his application."

## what kind of facility this license covers

### `facility_type_covered` — list[str]
- **what:** The type(s) of health facility whose administration falls under this licensure act.
- **states:** PA
- **sample (PA):** ""Nursing home" means any institution or facility in which nursing care and related medical or other health services are provided for a period exceeding twenty-four hours, for two or more individuals."

### `small_facility_shared_admin_threshold_beds` — int
- **what:** Bed-count threshold below which a facility may share an administrator with another facility rather than having a dedicated full-time administrator.
- **states:** PA
- **sample (PA):** "A nursing home of twenty-five beds or less may share the services of an administrator who is readily available at all times, and who can devote sufficient time to supervise the standards of the nursing home."

## who is eligible to apply

### `citizenship_required` — bool
- **what:** Whether U.S. citizenship (or declared intent to become a citizen) is a stated eligibility requirement for licensure.
- **states:** PA
- **sample (PA):** "He is at least twenty-one years old, a citizen of the United States, or that he has duly declared his intention of becoming a citizen of the United States."

### `experience_substitutable_for_education` — bool
- **what:** Whether documented practical experience in nursing home or health facility administration may be substituted for required post-secondary education credits.
- **states:** PA
- **sample (PA):** "A candidate who applies for examination under and pursuant to subsection (c) of this section, in lieu of the educational requirements provided for therein, may submit evidence satisfactory to the board that he has obtained one year of practical experience in nursing home administration or in related health facility administration for each year of required post-high school or post-secondary school education."

### `long_term_operator_exam_exemption` — bool
- **what:** Whether individuals who have operated a nursing home for a specified number of years may sit for the licensing exam without meeting the standard educational prerequisites.
- **states:** PA
- **sample (PA):** "Any person who has operated a nursing home for a period of three years or more shall be admitted to the licensing examination without the necessity of submitting written evidence of high school graduation or its equivalent."

## ongoing registration and reporting requirements

### `registration_renewal_interval_years` — int
- **what:** The interval in years at which a licensee must renew their certificate of registration with the board (distinct from the license itself).
- **states:** PA
- **sample (PA):** "Thereafter, such individual shall biennially be required to apply to the board for a new certificate of registration and report any facts requested by the board on forms provided for such purpose."

### `multi_state_licensure_reporting_required` — bool
- **what:** Whether a licensee who also holds a license in another state, territory, or country must report that fact and any out-of-state disciplinary actions to the home-state board.
- **states:** PA
- **sample (PA):** "Any licensed nursing home administrator of this Commonwealth who is also licensed to practice nursing home administration in any other state, territory or country shall report this information to the board on the biennial renewal application. Any disciplinary action taken in other states shall be reported to the board on the biennial renewal application or within ninety days of final disposition, whichever is sooner."

### `out_of_state_discipline_reporting_deadline_days` — int
- **what:** Number of days after final disposition within which a licensee must report disciplinary action taken against them in another jurisdiction.
- **states:** PA
- **sample (PA):** "Any disciplinary action taken in other states shall be reported to the board on the biennial renewal application or within ninety days of final disposition, whichever is sooner."

## governing board structure

### `board_composition_required` — str
- **what:** Statutory description of the required membership composition of the licensing board, including professional, consumer, and government representatives.
- **states:** PA
- **sample (PA):** "The State Board of Examiners of Nursing Home Administrators shall consist of fifteen members as follows: six members shall be nursing home administrators, (two from not-for-profit facilities, two from operated-for-profit facilities and two from county facilities); three members who have been actively involved with the care of chronically ill and infirm aged patients... three members representative of the consumer; and the Secretary of Health, or his designee, the Director of the Bureau of Consumer Protection in the Office of Attorney General, or his designee, and the Commissioner of Professional and Occupational Affairs."

### `board_member_term_years` — int
- **what:** Length in years of a standard board member term.
- **states:** PA
- **sample (PA):** "The term of office of each member shall be four years from his appointment, or until his successor has been appointed and qualified, but no longer than six months beyond the four-year period."

### `board_member_consecutive_term_limit` — int
- **what:** Maximum number of consecutive full terms a board member may serve.
- **states:** PA
- **sample (PA):** "No member shall be eligible for appointment to serve more than two consecutive full terms."

## discipline and enforcement

### `automatic_license_suspension_triggers` — list[str]
- **what:** Specific events that trigger automatic (non-hearing) suspension of a license by operation of law.
- **states:** PA
- **sample (PA):** "A license issued under this act shall automatically be suspended upon the legal commitment to an institution of a licensee because of mental incompetency from any cause... conviction of a felony under the act of April 14, 1972 (P.L.233, No.64), known as 'The Controlled Substance, Drug, Device and Cosmetic Act.'"

### `temporary_suspension_max_days` — int
- **what:** Maximum number of days a temporary emergency suspension may remain in effect before the board must take further formal action.
- **states:** PA
- **sample (PA):** "The temporary suspension shall remain in effect until vacated by the board, but in no event longer than one hundred eighty days."

### `revocation_reinstatement_waiting_period_years` — int
- **what:** Minimum number of years a person must wait after license revocation before applying for reinstatement.
- **states:** PA
- **sample (PA):** "Any person whose license or registration has been revoked may apply for reinstatement, after a period of at least five years, but must meet all of the licensing qualifications of this act for the license applied for, to include the examination requirement."

## oversight and coordination with other agencies

### `interdepartmental_deficiency_reporting_required` — bool
- **what:** Whether the licensing board is required to establish a formal reporting procedure with the state health department to exchange information about facility deficiencies and administrator disciplinary actions.
- **states:** PA
- **sample (PA):** "The board, in cooperation with the Department of Health, shall develop a reporting procedure which requires the Department of Health to notify the board when deficiencies found in a licensed nursing home may be due to the practices of the nursing home administrator and which requires the board to notify the Department of Health of any disciplinary actions taken against a nursing home administrator licensed under this act."
