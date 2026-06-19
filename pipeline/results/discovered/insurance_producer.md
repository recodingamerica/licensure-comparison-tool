# Discovered fields — insurance_producer

## what they are licensed to sell

### `lines_of_authority` — list[str]
- **what:** The specific categories of insurance a producer is licensed to sell, solicit, or negotiate.
- **states:** PA
- **sample (PA):** ""Line of authority." The licensed ability to sell, solicit or negotiate particular classes or types of insurance, including the following: (1) Life. (2) Accident and health or sickness. (3) Property. (4) Casualty. (5) Variable life and variable annuity products. (6) Personal lines. (7) Credit. (8) Motor vehicle rental. (9) Limited line."

### `resident_license_available` — bool
- **what:** Whether the state issues a resident insurance producer license distinct from a nonresident license.
- **states:** PA
- **sample (PA):** "An applicant with a principal place of residence or business within this Commonwealth may apply to the department for a resident insurance producer license."

### `nonresident_license_available` — bool
- **what:** Whether the state issues a nonresident insurance producer license for producers whose home state is elsewhere.
- **states:** PA
- **sample (PA):** "An applicant with a principal place of residence or business outside this Commonwealth may apply for a nonresident insurance producer license."

## education and exam prerequisites

### `preexamination_education_hours` — int
- **what:** Minimum credit hours of approved pre-examination coursework required before sitting for the licensing exam.
- **states:** PA
- **sample (PA):** "an individual who desires to be licensed as an insurance producer shall complete a minimum of 24 credit hours of approved preexamination courses."

### `preexamination_ethics_hours` — int
- **what:** Minimum credit hours specifically dedicated to ethics within the required pre-examination education program.
- **states:** PA
- **sample (PA):** "A preexamination education program approved by the department shall include no less than three credit hours on ethics."

### `exam_waiver_designations` — list[str]
- **what:** Professional designations that exempt a candidate from the pre-examination education or licensing examination requirements.
- **states:** PA
- **sample (PA):** "A person who possesses the professional designation of Chartered Life Underwriter (CLU) and is applying for life or accident and health line of authority... A person who possesses the professional designation of Chartered Property and Casualty Underwriter (CPCU)... A person who possesses the professional designation of Certified Insurance Counselor (CIC)..."

## who can hold a license

### `business_entity_license_available` — bool
- **what:** Whether a business entity (non-individual) may obtain an insurance producer license in addition to individual producers.
- **states:** PA
- **sample (PA):** "Upon designating one or more individuals licensed under this act to be responsible for the business entity's compliance with the insurance laws and regulations of the Commonwealth, a business entity may apply to the department for an insurance producer license."

### `designated_licensee_required_for_business_entity` — bool
- **what:** Whether a business entity must designate one or more individually licensed producers responsible for the entity's regulatory compliance.
- **states:** PA
- **sample (PA):** ""Designated licensee." An individual who is licensed by the Insurance Department as an insurance producer and who is designated by a business entity to be responsible for the business entity's compliance with the insurance laws and regulations of this Commonwealth."

### `temporary_license_available` — bool
- **what:** Whether the state may issue a temporary insurance producer license in specified circumstances such as death or disability of a licensee.
- **states:** PA
- **sample (PA):** "the department may issue a temporary insurance producer license to the following persons: The surviving spouse or court-appointed personal representative of a resident individual licensee who dies or becomes mentally or physically disabled."

### `temporary_license_max_days` — int
- **what:** Maximum number of days a temporary insurance producer license may remain in effect.
- **states:** PA
- **sample (PA):** "The temporary license shall be for a period not to exceed 180 days and is not transferable."

## relationship between producer and insurer

### `appointment_required_to_represent_insurer` — bool
- **what:** Whether a producer must be formally appointed in writing by an insurer before acting as that insurer's representative.
- **states:** PA
- **sample (PA):** "An insurance producer shall not act on behalf of or as a representative of the insurer unless the insurance producer is appointed by the insurer."

### `appointment_fee` — str
- **what:** Fee charged to the insurer for each producer appointment, including billing frequency.
- **states:** PA
- **sample (PA):** "An appointment fee of $12.50 will be billed annually to the insurer for each producer appointed by the insurer during the preceding calendar year regardless of the length of time the producer held the appointment with the insurer."

### `appointment_termination_reporting_days` — int
- **what:** Number of days within which an insurer must notify the department after terminating a producer's appointment.
- **states:** PA
- **sample (PA):** "An insurer which terminates an appointment pursuant to section 671-A(d) shall notify the department in writing on a form approved by the department... within 30 days following the effective date of the termination."

### `written_consumer_representation_agreement_required` — bool
- **what:** Whether a producer acting on behalf of a consumer (rather than an insurer) must execute a written agreement disclosing services and fees before representing that consumer.
- **states:** PA
- **sample (PA):** "An insurance producer acting on behalf of or representing an insurance consumer shall execute a written agreement with the insurance consumer prior to representing or acting on their behalf that: (1) delineates the services to be provided; and (2) provides full and complete disclosure of the fee to be paid to the insurance producer by the insurance consumer."

## financial and ethical obligations

### `fiduciary_duty_for_funds` — bool
- **what:** Whether the producer is explicitly held to a fiduciary standard for all funds received or collected in their capacity as a producer.
- **states:** PA
- **sample (PA):** "An insurance producer shall be responsible in a fiduciary capacity for all funds received or collected as an insurance producer and shall not, without the express consent of the insurance entity on whose behalf the funds were received, mingle the funds with the producer's own funds."

### `rebates_prohibited` — bool
- **what:** Whether the statute explicitly prohibits producers from offering or paying rebates of premiums or commissions as inducements.
- **states:** PA
- **sample (PA):** "No insurance producer shall, directly or indirectly, offer, promise, allow, give, set off or pay a rebate of, or part of, a premium payable on the contract of insurance or on the insurance producer's commission... which is not specified in the contract of insurance."

### `additional_fee_for_commercial_business_allowed` — bool
- **what:** Whether a producer may charge a fee in addition to a commission for commercial insurance business, subject to advance written disclosure.
- **states:** PA
- **sample (PA):** "A licensee may charge a fee in addition to a commission to a person for the sale, solicitation or negotiation of a contract of insurance for commercial business. The fee charged by the licensee shall be disclosed in advance in writing to the person and shall be reasonable in relationship to the services provided."

### `misconduct_reporting_to_department_days` — int
- **what:** Number of days within which a licensee must report to the department any administrative action taken against them in another jurisdiction or by another governmental agency.
- **states:** PA
- **sample (PA):** "A licensee shall report to the department any administrative action taken against the licensee in another jurisdiction or by another governmental agency in this Commonwealth within 30 days of the final disposition of the matter."

## practice setting and consumer protection rules

### `financial_institution_insurance_sales_restrictions` — bool
- **what:** Whether the statute imposes specific disclosure, physical separation, and anti-tying requirements on producers selling insurance on or from the premises of a financial institution.
- **states:** PA
- **sample (PA):** "Sales of annuities or insurance, except credit insurance, by a financial institution or by a licensee employed by or affiliated with the financial institution shall take place in a location which is distinct from the area where deposits are taken and loan applications are discussed and accepted."

### `conditional_loan_insurance_tying_prohibited` — bool
- **what:** Whether the statute explicitly prohibits requiring a borrower to purchase insurance from a financial institution or its affiliates as a condition of a loan or deposit transaction.
- **states:** PA
- **sample (PA):** "No financial institution or its directors, officers, employees, agents or insurance producers may require the purchase of insurance from the financial institution or its affiliates or from a designated insurer or insurance producer as a condition of a loan or deposit transaction."

## extra credentials and tiered license types

### `manager_exclusive_general_agent_license_required` — bool
- **what:** Whether the state requires a separate license for managers and exclusive general agents who bind coverage or manage insurer business beyond ordinary production.
- **states:** PA
- **sample (PA):** "no person shall engage in any activities requiring a manager or exclusive general agent license without being licensed as a manager or exclusive general agent by the department."

### `manager_exclusive_general_agent_license_term_years` — str
- **what:** Maximum term length for a manager or exclusive general agent license (expressed as a period, may be less than one year).
- **states:** PA
- **sample (PA):** "A license issued in accordance with this section shall be for a period of not more than one year."

## licensing administration and reciprocity

### `naic_producer_database_used_for_verification` — bool
- **what:** Whether the department may use the NAIC Producer Database to verify a producer's licensing status for reciprocal or nonresident applications.
- **states:** PA
- **sample (PA):** "The department may verify the individual's licensing status through the Producer Database maintained by the NAIC."

### `home_state_change_application_window_days` — int
- **what:** Number of days after establishing a new principal place of residence or business in the state within which a producer must apply to transfer their home-state license.
- **states:** PA
- **sample (PA):** "Within 90 days of establishing a principal place of residence or business in this Commonwealth, the individual shall submit to the department a completed application indicating the lines of authority for which the individual desires to be licensed."

### `lapsed_license_reinstatement_window_days` — int
- **what:** Maximum number of days after license lapse within which a licensee may request reinstatement without reapplying from scratch (one year expressed in context).
- **states:** PA
- **sample (PA):** "A licensee who allows his or her license to lapse... may within one year of the license renewal date request the department to reinstate the license."

### `fingerprint_submission_required` — bool
- **what:** Whether applicants and renewing licensees must submit fingerprints to enable a national criminal history background check.
- **states:** PA
- **sample (PA):** "the applicant's fingerprints, in order for the department to receive national criminal history records information from the Federal Bureau of Investigation Criminal Justice Information Services Division"
