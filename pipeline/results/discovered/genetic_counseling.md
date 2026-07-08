# Discovered fields — genetic_counseling

## credentials and certification

### `certifying_bodies_accepted` — list[str]
- **what:** The national certification organizations whose credentials satisfy the licensure examination or certification requirement.
- **states:** AL, AR, CT, DE, GA, HI, IA, ID, … (+2)
- **sample (IL):** "Has successfully completed an examination provided by the ABGC or its successor, the ABMGG or its successor, or a substantially equivalent examination approved by the Department"

### `active_candidate_status_recognized` — bool
- **what:** Whether the state explicitly recognizes 'active candidate status' (ACS) from ABGC or equivalent as a basis for a provisional or temporary license.
- **states:** AL, AR, CT, DE, GA, HI, IA, ID, … (+2)
- **sample (IA):** "Active candidate status means a person has met the requirements established by the American board of genetic counseling or its equivalent or successor organization to take the American board of genetic counseling certification examination"

### `certification_maintenance_required_for_renewal` — bool
- **what:** Whether maintaining active certification from ABGC or ABMGG (or equivalent) is explicitly required as a condition of license renewal.
- **states:** AR, CT, DE, HI, IA, ID, IL, IN
- **sample (HI):** "Proof of maintenance of American Board of Genetic Counseling or its equivalent board certification shall be required for license renewal."

### `nsgc_ethics_code_referenced` — bool
- **what:** Whether the statute explicitly references the National Society of Genetic Counselors (NSGC) code of ethics as a standard of conduct or ground for discipline.
- **states:** DE, HI, ID
- **sample (HI):** "Violation of recognized ethical standards for genetic counselors as set by the National Society of Genetic Counselors"

## temporary and provisional practice

### `temporary_license_exam_attempt_limit` — int
- **what:** The maximum number of times an applicant may fail the certification examination before a temporary or provisional license is denied or automatically expires.
- **states:** AR, DE, IN
- **sample (AR):** "A temporary license shall not be issued if the applicant has failed the American Board of Genetic Counseling certification examination more than two (2) times."

### `temporary_license_duration_years` — int
- **what:** The maximum duration (in years) of a temporary or provisional license before it expires or must be renewed.
- **states:** AL, AR, CT, DE, GA, HI, IA, ID, … (+2)
- **sample (AR):** "A temporary license is valid for one (1) year from the date of issuance."

### `temporary_license_supervisor_types` — list[str]
- **what:** The categories of professionals who are authorized to supervise a holder of a temporary or provisional genetic counselor license.
- **states:** AL, AR, CT, DE, GA, HI, IA, ID, … (+2)
- **sample (AR):** "As a condition of temporary licensure, an applicant shall work under the supervision of a licensed genetic counselor or a licensed physician with current American Board of Genetic Counseling certification in clinical genetics when the applicant provides genetic counseling services."

### `supervision_contract_required` — bool
- **what:** Whether a written supervision contract between the supervisor and the provisionally licensed genetic counselor is explicitly required by statute.
- **states:** AL, GA, IA, IN
- **sample (AL):** "Supervision means the overall responsibility of a qualified supervisor to assess the work of a genetic counselor with a temporary license, including regular meetings and chart review, if an annual supervision contract signed by the supervisor and the temporarily licensed genetic counselor is on file with both parties."

### `supervisor_physical_presence_required` — bool
- **what:** Whether the statute explicitly states that the supervisor's physical presence is NOT required during the performance of genetic counseling services by a provisional licensee.
- **states:** AL, GA, IA, ID
- **sample (AL):** "The presence of a qualified supervisor is not required during the performance of the genetic counseling service."

## what genetic counselors are allowed to do

### `genetic_test_ordering_authority` — bool
- **what:** Whether the statute explicitly authorizes licensed genetic counselors to order or coordinate genetic laboratory tests (not merely recommend or identify them).
- **states:** GA, IA, ID, IL, IN
- **sample (IA):** "Identify, order, and coordinate genetic laboratory tests and other diagnostic studies as appropriate for the genetic assessment."

### `temporary_licensee_test_ordering_prohibited` — bool
- **what:** Whether the statute explicitly prohibits holders of a temporary or provisional license from ordering genetic tests.
- **states:** GA, IL
- **sample (IL):** "The holder of a temporary license shall practice only under the supervision of a qualified supervisor and may not have the authority to order genetic tests."

### `medicine_practice_exclusion` — bool
- **what:** Whether the statute explicitly states that nothing in the chapter authorizes a genetic counselor to practice medicine or diagnose disease.
- **states:** AL, IL, IN
- **sample (AL):** "Nothing in this chapter may be construed as authorizing a genetic counselor to practice medicine."

### `referral_to_physician_required_when_outside_scope` — bool
- **what:** Whether the statute requires a genetic counselor to refer a client to a physician when the counselor finds a condition requiring services outside the genetic counselor's scope of practice.
- **states:** DE, IL
- **sample (DE):** "if in the course of providing a genetic counseling service to any client, a genetic counselor finds any indication of disease or condition that requires medical assessment, the genetic counselor shall refer a client to a physician licensed to practice medicine"

## who is exempt from licensure

### `consumer_direct_testing_company_exemption` — bool
- **what:** Whether the statute explicitly exempts FDA-approved direct-to-consumer genetic risk assessment companies (that assess but do not diagnose) from the licensure requirement.
- **states:** AL, GA
- **sample (AL):** "Any company providing services available directly to consumers without seeing a physician or genetic counselor which is approved by the United States Food and Drug Administration to assess, and not diagnose, risks for certain genetic diseases or conditions."

### `visiting_out_of_state_counselor_exemption_days` — int
- **what:** The maximum number of days per year a certified genetic counselor from another state may practice in the state without obtaining a local license under a visiting-counselor exemption.
- **states:** AR, IL
- **sample (AR):** "A visiting genetic counselor who is certified by the American Board of Genetic Counseling or the American Board of Medical Genetics and Genomics from outside the state performing activities and services for a period of thirty (30) days each year."

### `federal_employee_exemption` — bool
- **what:** Whether the statute explicitly exempts individuals employed as genetic counselors by the federal government or a federal agency, when providing services solely under that agency's direction.
- **states:** AL, AR, GA, HI, IA, ID, IL, IN
- **sample (ID):** "Any person employed as a genetic counselor by the federal government or an agency thereof if the person provides genetic counseling services solely under the direction and control of the organization by which he is employed"

## education pathways to licensure

### `phd_medical_geneticist_pathway` — bool
- **what:** Whether the statute provides a separate doctoral-degree pathway (e.g., ABMGG-accredited medical genetics training program) as an alternative to the master's-degree genetic counseling pathway for licensure.
- **states:** AL, AR, DE, GA, IA, IL, IN
- **sample (AL):** "Has successfully completed a doctoral degree and an ABMGG accredited medical genetics training program or an equivalent program approved by the ABMGG"

### `accrediting_body_for_training_program` — list[str]
- **what:** The accrediting organizations whose approval of a genetic counseling training program satisfies the educational requirement for licensure.
- **states:** AL, AR, CT, DE, GA, HI, IA, ID, … (+2)
- **sample (AR):** "A master's degree from a genetic counseling training program that is accredited by the American Board of Genetic Counseling or an equivalent as determined by the American Board of Genetic Counseling or the American Board of Medical Genetics and Genomics"

## ongoing requirements after licensure

### `continuing_education_hours_per_period` — int
- **what:** The minimum number of continuing education hours (or units) required per renewal period, where specified by statute.
- **states:** AR, GA, IA
- **sample (GA):** "the number of hours of continuing education required for renewal of licensure shall not be less than 30 hours biennially"

### `inactive_license_status_available` — bool
- **what:** Whether the statute explicitly provides for an inactive license status that excuses the licensee from renewal fees while prohibiting practice.
- **states:** AL, DE, GA, IL
- **sample (DE):** "A licensee, upon written request, may be placed in an inactive status for no more than 5 years."

## client rights and professional obligations

### `client_confidentiality_provisions` — bool
- **what:** Whether the statute contains explicit provisions protecting the confidentiality of client communications or information obtained during genetic counseling.
- **states:** ID, IL
- **sample (ID):** "No licensee shall disclose any information that he may have acquired from a client consulting him in his professional capacity that was necessary to enable him to render services in his professional capacity"

### `conscientious_objection_protection` — bool
- **what:** Whether the statute explicitly protects a genetic counselor from being required to perform or participate in a service that violates the counselor's sincerely held ethical, moral, or religious beliefs.
- **states:** IN
- **sample (IN):** "A genetic counselor may not be required to perform, participate in, or provide a service that violates any sincerely held ethical, moral, or religious belief held by the genetic counselor."

## governance and board structure

### `advisory_council_established` — bool
- **what:** Whether the statute establishes a dedicated advisory council or board specifically for genetic counseling (as opposed to regulation by a general medical board).
- **states:** AL, DE, ID
- **sample (DE):** "The Genetic Counselor Advisory Council (Council) consists of 5 voting members, and 1 ex officio member."

### `physician_member_on_governing_body` — bool
- **what:** Whether the statute requires at least one licensed physician to serve on the board or advisory council that regulates genetic counselors.
- **states:** AL, DE, ID
- **sample (DE):** "The 5 voting members shall consist of 1 physician member of the Board of Medical Licensure and Discipline and 4 Council members licensed and trained as genetic counselors"

### `grandfathering_provision` — bool
- **what:** Whether the statute includes a transitional or grandfathering provision allowing individuals practicing genetic counseling before the law's effective date to obtain licensure without meeting all standard requirements.
- **states:** CT, ID
- **sample (ID):** "Until July 1, 2016, an individual who does not qualify for licensure under this chapter may apply to the board for licensure, and the board may approve the application if the individual has paid the required fees and has worked as a genetic counselor for a minimum of ten (10) years"
