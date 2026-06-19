# Discovered fields — athlete_agent

## registration and renewal

### `registration_validity_years` — int
- **what:** Duration in years for which a certificate of registration or renewal is valid.
- **states:** PA
- **sample (PA):** "A certificate of registration or renewal of registration under this chapter is valid for two years."

### `temporary_registration_available` — bool
- **what:** Whether the issuing authority may issue a temporary certificate of registration while an application is pending.
- **states:** PA
- **sample (PA):** "The commission may issue a temporary certificate of registration as an athlete agent while an application for registration or renewal of registration is pending."

### `pre_registration_acting_allowed` — bool
- **what:** Whether an individual may act as an athlete agent before receiving a certificate, provided the student athlete initiated contact and the individual applies within a specified window.
- **states:** PA
- **sample (PA):** "Before being issued a certificate of registration under this chapter, an individual may act as an athlete agent in this Commonwealth for all purposes except signing an agency contract, if a student athlete or another person acting on behalf of the student athlete initiates communication with the individual."

### `pre_registration_application_deadline_days` — int
- **what:** Number of days after the initial act requiring registration within which the individual must submit a registration application when acting before registration.
- **states:** PA
- **sample (PA):** "not later than seven days after an initial act which requires the individual to register as an athlete agent, the individual submits an application for registration as an athlete agent in this Commonwealth."

### `registration_fee_initial` — int
- **what:** Fee in dollars for an initial registration application by an individual or sole proprietor.
- **states:** PA
- **sample (PA):** "For an initial application for registration or an application for renewal of registration for an individual or sole proprietor, $200."

### `registration_fee_reciprocal` — int
- **what:** Fee in dollars for a registration application based on a certificate from another state.
- **states:** PA
- **sample (PA):** "For an application for registration or an application for renewal of registration based upon a certificate of registration or licensure issued by another state for an individual or a sole proprietor, $150."

## background and fitness requirements

### `criminal_history_check_required` — bool
- **what:** Whether applicants must submit a criminal history background check report from the state police.
- **states:** PA
- **sample (PA):** "An individual who applies for registration under subsection (a) or (b) shall submit to the commission, pursuant to 18 Pa.C.S. Ch. 91 (relating to criminal history record information), a report of criminal history record information from the Pennsylvania State Police."

### `fitness_disqualifying_factors` — list[str]
- **what:** List of conduct categories the issuing authority may consider when determining whether an applicant is unfit to act as an athlete agent.
- **states:** PA
- **sample (PA):** "the commission may consider whether the applicant has: pleaded guilty or no contest to, has been convicted of or has charges pending for an offense which involves moral turpitude or would constitute a felony; made a materially false, misleading, deceptive or fraudulent representation; engaged in conduct which would disqualify the applicant from serving in a fiduciary capacity; had a registration as an athlete agent suspended, revoked or denied in any state."

### `prior_occupation_disclosure_years` — int
- **what:** Number of years of prior business or occupational history the applicant must disclose on the registration application.
- **states:** PA
- **sample (PA):** "Each business or occupation in which the applicant engaged within five years before the date of the application, including self-employment and employment by others, and any professional or occupational license, registration or certification held by the applicant during that time."

### `prior_civil_proceeding_disclosure_years` — int
- **what:** Number of years before application within which civil proceedings involving the applicant must be disclosed.
- **states:** PA
- **sample (PA):** "Whether, within 15 years before the date of application, the applicant or a person named under paragraph (7) has been a defendant or respondent in a civil proceeding."

### `prior_bankruptcy_disclosure_years` — int
- **what:** Number of years before application within which bankruptcy adjudications must be disclosed.
- **states:** PA
- **sample (PA):** "Whether, within 10 years before the date of application, the applicant or a person named under paragraph (7) was adjudicated bankrupt or was an owner of a business that was adjudicated bankrupt."

### `professional_league_certification_disclosure_required` — bool
- **what:** Whether applicants must disclose any certification or registration held with a professional league or players association, including dates and any disciplinary history.
- **states:** PA
- **sample (PA):** "If the applicant is certified or registered by a professional league or players association: name of the league or association; date of certification or registration and, if applicable, date of expiration of the certification or registration."

### `social_media_disclosure_required` — bool
- **what:** Whether applicants must disclose all social media accounts affiliated with themselves or their business or employer.
- **states:** PA
- **sample (PA):** "Each social media account with which the applicant or the applicant's business or employer is affiliated."

## agency contract requirements

### `agency_contract_required_contents` — list[str]
- **what:** Mandatory elements that must appear in every agency contract between an athlete agent and a student athlete.
- **states:** PA
- **sample (PA):** "An agency contract shall contain: a statement that the athlete agent is registered as an athlete agent in this Commonwealth; the amount and method of calculating the consideration to be paid by the student athlete; the name of any person not listed in the athlete agent's application who will be compensated; a description of any expenses the student athlete agrees to reimburse; a description of the services to be provided; the duration of the contract; and the date of execution."

### `agency_contract_warning_notice_required` — bool
- **what:** Whether agency contracts must include a conspicuous boldface warning notice to the student athlete about eligibility loss and cancellation rights.
- **states:** PA
- **sample (PA):** "Subject to subsection (g), an agency contract shall contain a conspicuous notice in boldface type and in substantially the following form: WARNING TO STUDENT ATHLETE IF YOU SIGN THIS CONTRACT: IF YOU ENTER INTO NEGOTIATIONS FOR, OR SIGN, A PROFESSIONAL-SPORTS-SERVICES CONTRACT, YOU MAY LOSE YOUR ELIGIBILITY TO COMPETE AS A STUDENT ATHLETE IN YOUR SPORT."

### `agency_contract_signed_acknowledgment_required` — bool
- **what:** Whether a separate signed acknowledgment that signing may result in loss of athletic eligibility must accompany every agency contract.
- **states:** PA
- **sample (PA):** "An agency contract shall be accompanied by a separate record signed by the student athlete or, if the student athlete is a minor, the parent or guardian of the student athlete, acknowledging that signing the contract may result in the loss of the student athlete's eligibility to participate in the student athlete's sport."

### `student_athlete_cancellation_period_days` — int
- **what:** Number of days after signing within which a student athlete (or parent/guardian if a minor) may cancel an agency contract without penalty.
- **states:** PA
- **sample (PA):** "A student athlete or, if the student athlete is a minor, the parent or guardian of the student athlete may cancel an agency contract by giving notice in a record of cancellation to the athlete agent not later than 14 days after the contract is signed."

### `void_contract_on_noncompliance` — bool
- **what:** Whether an agency contract resulting from conduct that violates registration requirements is automatically void, requiring return of consideration.
- **states:** PA
- **sample (PA):** "An agency contract resulting from conduct in violation of this section is void, and the athlete agent shall return consideration received under the contract."

## notice and reporting obligations

### `notice_to_athletic_director_required` — bool
- **what:** Whether an athlete agent must notify the athletic director of the student athlete's educational institution upon entering into an agency contract or before initiating contact.
- **states:** PA
- **sample (PA):** "The athlete agent shall give notice in a record of the existence of the agency contract to the athletic director of the educational institution at which the student athlete is enrolled not later than the earlier of 72 hours after entering into an agency contract or before the next scheduled athletic event in which the student athlete may participate."

### `notice_to_athletic_director_deadline_hours` — int
- **what:** Maximum number of hours after entering into an agency contract within which the athlete agent must notify the athletic director.
- **states:** PA
- **sample (PA):** "Notice under paragraph (1) shall be given not later than the earlier of: 72 hours after entering into an agency contract; or before the next scheduled athletic event in which the student athlete may participate."

### `notice_to_commission_required` — bool
- **what:** Whether both the student athlete and athlete agent must notify the issuing authority of the existence of an agency contract within a specified period.
- **states:** PA
- **sample (PA):** "A student athlete and an athlete agent shall give notice in a record of the existence of an agency contract to the commission within 72 hours of entering into the agency contract."

### `pre_contact_notice_to_athletic_director_required` — bool
- **what:** Whether an athlete agent must notify the athletic director before communicating with a student athlete or another person to influence the student athlete to enter into an agency contract.
- **states:** PA
- **sample (PA):** "An athlete agent shall give notice in a record to the athletic director of the educational institution at which a student athlete is enrolled before the athlete agent communicates or attempts to communicate with the student athlete or another individual to have that individual influence the student athlete to enter into an agency contract."

### `student_initiated_contact_notice_deadline_days` — int
- **what:** Number of days after a student-athlete-initiated communication within which the athlete agent must notify the athletic director.
- **states:** PA
- **sample (PA):** "If a communication or attempt to communicate with an athlete agent is initiated by a student athlete or another individual on behalf of the student athlete, the athlete agent shall notify in a record the athletic director of the educational institution at which the student athlete is enrolled. The notification shall be made not later than 10 days after the communication or attempt."

### `records_retention_years` — int
- **what:** Number of years an athlete agent must retain records of represented individuals, agency contracts, and recruitment costs.
- **states:** PA
- **sample (PA):** "An athlete agent shall create and retain for five years records of the following: the name and address of each individual represented by the athlete agent; each agency contract entered into by the athlete agent; and the direct costs incurred by the athlete agent in the recruitment or solicitation of each student athlete."

## prohibited conduct and penalties

### `prohibited_conduct_list` — list[str]
- **what:** Enumerated acts an athlete agent is expressly prohibited from intentionally committing.
- **states:** PA
- **sample (PA):** "An athlete agent may not intentionally do any of the following: Give a student athlete materially false or misleading information; Furnish anything of value to a student athlete if the thing of value may result in loss of the student athlete's eligibility; Initiate contact with a student athlete to recruit or solicit the student athlete to enter an agency contract unless registered; Predate or postdate an agency contract."

### `criminal_penalty_classification` — str
- **what:** Criminal offense classification assigned to violations of the prohibited conduct provisions.
- **states:** PA
- **sample (PA):** "An athlete agent who violates section 3514 (relating to prohibited conduct) commits a misdemeanor of the third degree."

### `max_civil_administrative_penalty` — int
- **what:** Maximum dollar amount of administrative civil penalty the issuing authority may assess for a violation.
- **states:** PA
- **sample (PA):** "The commission may assess an administrative penalty against an athlete agent not to exceed $50,000 for a violation of this chapter."

### `civil_remedy_available_to_educational_institution` — bool
- **what:** Whether an educational institution adversely affected by an athlete agent's violation may bring a civil action for damages.
- **states:** PA
- **sample (PA):** "An educational institution or a student athlete may bring an action for damages against an athlete agent if the educational institution or student athlete is adversely affected by an act or omission of the athlete agent in violation of this chapter."

## oversight and public accountability

### `public_registry_required` — bool
- **what:** Whether the issuing authority must maintain and publicly publish a searchable database of registered athlete agents.
- **states:** PA
- **sample (PA):** "The commission shall develop and maintain a database for all registrations of an athlete agent under this chapter. The database shall be made available on the commission's publicly accessible Internet website."

## name image and likeness rights

### `nil_compensation_permitted` — bool
- **what:** Whether college student athletes are expressly permitted to earn compensation for the use of their name, image, or likeness.
- **states:** PA
- **sample (PA):** "A college student athlete may earn compensation for the use of the college student athlete's name, image or likeness under this chapter. The compensation shall be commensurate with the market value of the college student athlete's name, image or likeness."

### `nil_prohibited_categories` — list[str]
- **what:** Categories of products or industries with which a college student athlete may not associate their name, image, or likeness for compensation.
- **states:** PA
- **sample (PA):** "A college student athlete may not earn compensation as a result of the use of the college student athlete's name, image or likeness in connection with a person, company or organization related to or associated with the development, production, distribution, wholesaling or retailing of any of the following: Adult entertainment products and services; Alcohol products; Casinos and gambling; Tobacco and electronic smoking products and devices; Prescription pharmaceuticals; A controlled dangerous substance."

### `nil_contract_predisclosure_to_institution_required` — bool
- **what:** Whether a college student athlete must disclose the contents of a proposed NIL contract to a designated institutional official before executing it.
- **states:** PA
- **sample (PA):** "A college student athlete who proposes to enter into a contract providing compensation to the college student athlete for use of the college student athlete's name, image or likeness rights shall disclose the contents of the contract prior to execution of the contract to an official of the institution of higher education, who is designated by the institution of higher education."

### `nil_scholarship_protection` — bool
- **what:** Whether earning NIL compensation is expressly prohibited from affecting a student athlete's scholarship eligibility, duration, or renewal.
- **states:** PA
- **sample (PA):** "Earning compensation from the use of a college student athlete's name, image or likeness rights may not affect the college student athlete's scholarship eligibility, duration or renewal."

### `nil_royalty_payment_required` — bool
- **what:** Whether producers of commercial products (jerseys, video games, trading cards) using a college student athlete's identifiable features must pay a royalty to that athlete.
- **states:** PA
- **sample (PA):** "A person that produces a college team jersey, a college team video game or college team trading cards for the purpose of making a profit shall make a royalty payment to each college student athlete whose name, image, likeness or other individually identifiable feature is used."
