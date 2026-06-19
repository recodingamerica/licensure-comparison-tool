# Discovered fields — surgical_technologist

## alternative ways to qualify

### `military_training_pathway` — bool
- **what:** Whether completion of a military surgical technology training program (Army, Navy, or Air Force) is accepted as an alternative qualification pathway.
- **states:** PA
- **sample (PA):** "has successfully completed an appropriate training program for surgical technology in the United States Army, Navy or Air Force"

### `grandfathering_available` — bool
- **what:** Whether individuals employed as surgical technologists before the effective date of the statute are exempt from new certification requirements.
- **states:** PA
- **sample (PA):** "provides evidence that the individual maintains a surgical technologist certification from an accredited certification program or was employed to practice surgical technology by the health care facility on or before the effective date of this section"

### `provisional_employment_period_months` — int
- **what:** Number of months a newly graduated surgical technologist may be employed before obtaining required certification.
- **states:** PA
- **sample (PA):** "A health care facility may employ or contract an individual to practice surgical technology during the six-month period immediately following successful completion of a surgical technology program"

## employer and facility obligations

### `facility_employer_verification_required` — bool
- **what:** Whether the employing health care facility is required to verify and maintain documentation of a surgical technologist's credentials and employment dates.
- **states:** PA
- **sample (PA):** "A health care facility that employs or contracts with an individual to practice surgical technology shall verify the dates of employment of the individual or contract period with the individual upon request"

### `workforce_shortage_exception` — bool
- **what:** Whether a health care facility may hire unqualified individuals when it cannot find a sufficient number of qualified surgical technologists after documented diligent effort.
- **states:** PA
- **sample (PA):** "after a diligent and thorough effort has been made, the health care facility is unable to employ or contract with a sufficient number of qualified surgical technologists who meet the requirements"

### `facility_can_restrict_practice` — bool
- **what:** Whether a health care facility is explicitly authorized to restrict an employee's eligibility to practice surgical technology for non-compliance.
- **states:** PA
- **sample (PA):** "A health care facility may restrict an employee's eligibility to practice surgical technology, as deemed appropriate by the health care facility, in the event the employee does not comply with this act."

## where they are allowed to work

### `approved_practice_settings` — list[str]
- **what:** Types of health care facilities where surgical technologists are authorized to practice.
- **states:** PA
- **sample (PA):** "A health care facility shall not employ or otherwise contract for the services of a surgical technologist in a health care facility"

## ongoing requirements for uncertified practitioners

### `continuing_education_hours_uncertified` — int
- **what:** Number of continuing education hours required per period for surgical technologists who are not certified or whose certification has lapsed.
- **states:** PA
- **sample (PA):** "complete 30 hours of relevant continuing education every two years in order to remain eligible to practice surgical technology"

### `continuing_education_governed_by_credentialing_body` — bool
- **what:** Whether certified surgical technologists must follow continuing education requirements set by their credentialing organization rather than a fixed statutory hour requirement.
- **states:** PA
- **sample (PA):** "comply with the continuing education requirements specified by the credentialing organization as necessary to keep the certification current"

## related regulated roles covered by the same law

### `central_service_technician_regulated` — bool
- **what:** Whether the same statute also regulates central service technicians (those who sterilize and prepare surgical instruments).
- **states:** PA
- **sample (PA):** "An individual shall not function as a central service technician, and a health care facility shall not employ or otherwise contract for the services of a central service technician, unless the individual has successfully passed a nationally accredited central service exam"

### `central_service_technician_accepted_credentials` — list[str]
- **what:** Specific credential designations accepted for central service technicians under the same statute.
- **states:** PA
- **sample (PA):** "Certified registered central service technician credential. Certified sterile processing and distribution technician credential."
