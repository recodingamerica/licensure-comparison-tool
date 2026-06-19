# Discovered fields — massage_therapy

## professional title and identity rules

### `protected_titles` — list[str]
- **what:** Titles, abbreviations, and descriptors that only licensed practitioners may use.
- **states:** PA
- **sample (PA):** "An individual who holds a license or is maintained on inactive status may use the title 'Licensed Massage Therapist' and the abbreviation 'L.M.T.' No other individual may use the title 'Licensed Massage Therapist' or the title 'Massage Therapist' or hold oneself out to others as a massage therapist."

### `prohibited_titles` — list[str]
- **what:** Specific terms (e.g., masseur, masseuse, myotherapist) that unlicensed individuals are prohibited from using.
- **states:** PA
- **sample (PA):** "adopting or using any title or description, including massage therapist, massage practitioner, masseur, masseuse, myotherapist or a derivative of those terms and their related abbreviations, which implies directly or indirectly that massage services are being provided"

## education and training requirements

### `education_minimum_hours` — int
- **what:** Minimum number of in-class instructional hours required in an approved massage therapy program.
- **states:** PA
- **sample (PA):** "The applicant has completed a massage program of at least 600 hours of in-class, postsecondary education instruction approved by the board"

### `education_required_topics` — list[str]
- **what:** Specific subject areas or trainings that must be included in the approved education program.
- **states:** PA
- **sample (PA):** "The program under this paragraph must include training in the human immunodeficiency virus and related risks and training in cardiopulmonary resuscitation."

### `cpr_certification_required_for_renewal` — bool
- **what:** Whether current CPR certification must be maintained and submitted at license renewal.
- **states:** PA
- **sample (PA):** "To renew a license, a licensee must do all of the following: File a renewal application with the board which includes the following: Current certification to administer cardiopulmonary resuscitation."

## temporary and provisional authorization

### `temporary_practice_permit_available` — bool
- **what:** Whether the board may issue a temporary permit allowing practice while awaiting full licensure.
- **states:** PA
- **sample (PA):** "The board may issue a temporary practice permit to an applicant in order to permit the applicant to practice massage therapy during the six-month period after completion of the applicant's education program."

### `temporary_permit_duration_months` — int
- **what:** Maximum duration in months of a temporary practice permit.
- **states:** PA
- **sample (PA):** "The temporary practice permit issued under paragraph (1) shall be nonrenewable and shall expire on the earlier of: six months from the date of issuance"

### `temporary_permit_renewable` — bool
- **what:** Whether a temporary practice permit may be renewed.
- **states:** PA
- **sample (PA):** "The temporary practice permit issued under paragraph (1) shall be nonrenewable"

## what is and is not within the profession's scope

### `excluded_modalities` — list[str]
- **what:** Specific techniques, procedures, or practices explicitly excluded from the definition of massage therapy.
- **states:** PA
- **sample (PA):** "The term does not include the diagnosis or treatment of impairment, illness, disease or disability, a medical procedure, a chiropractic manipulation - adjustment, physical therapy mobilization - manual therapy, therapeutic exercise, electrical stimulation, ultrasound or prescription of medicines"

### `included_adjunct_modalities` — list[str]
- **what:** Adjunct techniques or tools explicitly included within the statutory definition of massage therapy.
- **states:** PA
- **sample (PA):** "The term includes the external application of water, heat, cold, lubricants or other topical preparations, lymphatic techniques, myofascial release techniques and the use of electro-mechanical devices which mimic or enhance the action of the massage techniques."

### `exempted_practices` — list[str]
- **what:** Practices or practitioner categories explicitly exempted from the licensure requirement.
- **states:** PA
- **sample (PA):** "The practice by an individual while performing reflexology. The practice of an individual who uses touch, words and directed movement to deepen awareness of existing patterns of movement in the body... The practice of an individual who uses touch to affect the energy systems, acupoints, Qi meridians or channels of energy of the human body"

### `reflexology_defined_separately` — bool
- **what:** Whether reflexology is given its own statutory definition distinct from massage therapy.
- **states:** PA
- **sample (PA):** "'Reflexology.' The physical act of using thumbs, fingers and hand techniques to apply specific pressure on the reflex area in the feet, hands or ears of the client."

## supervision and delegation

### `student_supervision_exemption` — bool
- **what:** Whether students in approved programs are exempt from licensure requirements when practicing under supervision.
- **states:** PA
- **sample (PA):** "A student enrolled in a massage therapy education program who is: conducting massage therapy activities under the supervision of: a licensee; or instructors or supervisors who meet the licensing criteria of the Department of Education or the board"

### `employer_licensure_obligation` — bool
- **what:** Whether employers are prohibited from hiring unlicensed individuals to perform massage therapy.
- **states:** PA
- **sample (PA):** "An individual, corporation, partnership, firm or other entity may not employ an individual in massage therapy unless the individual is licensed by the board."

## license status and reinstatement

### `inactive_status_available` — bool
- **what:** Whether licensees may place their license on inactive status without fee.
- **states:** PA
- **sample (PA):** "Any person licensed under this act may request an application for inactive status. The application may be completed and returned to the board; upon receipt of each application, the applicant shall be maintained on inactive status without fee"

### `reactivation_ce_requirement_after_long_inactive` — bool
- **what:** Whether additional competency requirements apply when reactivating a license that has been inactive for an extended period.
- **states:** PA
- **sample (PA):** "Any person who requests an active status license who has been on inactive status for a period of five consecutive years or longer shall, prior to receiving an active license, satisfy the requirements of the board's regulations for ensuring continued competence"

### `revocation_reapplication_waiting_period_years` — int
- **what:** Minimum number of years a person must wait after license revocation before reapplying.
- **states:** PA
- **sample (PA):** "An individual whose license has been revoked may reapply for a license after a period of at least five years, and must meet all of the licensing requirements of this act."

## criminal history and discipline

### `criminal_history_disqualifying_offense` — str
- **what:** Specific category of criminal conviction that may disqualify an applicant, with any rehabilitation exception noted.
- **states:** PA
- **sample (PA):** "The applicant has not been convicted of a felony under the act of April 14, 1972 (P.L.233, No.64), known as The Controlled Substance, Drug, Device and Cosmetic Act... unless... At least ten years have elapsed from the date of conviction."

### `civil_penalty_maximum_dollars` — int
- **what:** Maximum civil monetary penalty the board may levy for violations of the act.
- **states:** PA
- **sample (PA):** "the board... may levy a civil penalty of up to $10,000"

## continuing education specifics

### `continuing_education_excluded_topics` — list[str]
- **what:** Topics explicitly excluded from counting toward continuing education credit hours.
- **states:** PA
- **sample (PA):** "No credit may be given for courses in office management or practice building."

### `continuing_education_hardship_waiver` — bool
- **what:** Whether the board may waive continuing education requirements for illness, emergency, or hardship.
- **states:** PA
- **sample (PA):** "The board may waive all or part of the continuing education requirement to a licensee who shows to the satisfaction of the board that the licensee was unable to complete the requirement due to illness, emergency or hardship."

### `multi_state_licensure_reporting_required` — bool
- **what:** Whether licensees holding licenses in other jurisdictions must report that fact and any out-of-state disciplinary actions at renewal.
- **states:** PA
- **sample (PA):** "A licensee who is licensed to practice massage therapy in another jurisdiction shall report this information to the board on the license renewal application. Any disciplinary action taken in another jurisdiction shall be reported to the board on the license renewal application or within 90 days of final disposition"
