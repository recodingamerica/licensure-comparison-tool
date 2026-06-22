# Discovered fields — mental_health_counseling

## license types and credential levels

### `license_tiers` — list[str]
- **what:** The distinct named license tiers or credential levels recognized under the statute, from entry-level to fully independent practice.
- **states:** PA
- **sample (PA):** "licensed bachelor social worker, licensed social worker, licensed clinical social worker, licensed associate marriage and family therapist, licensed marriage and family therapist, licensed associate professional counselor or licensed professional counselor"

### `associate_license_available` — bool
- **what:** Whether the state offers a supervised associate or provisional license tier that precedes full licensure.
- **states:** PA
- **sample (PA):** "An individual licensed as an associate professional counselor under this act who is obtaining supervised clinical experience for the purpose of becoming a licensed professional counselor."

### `associate_license_renewal_limit` — int
- **what:** Maximum number of times an associate-level license may be renewed before the holder must achieve full licensure.
- **states:** PA
- **sample (PA):** "Renewal of an associate professional counselor license shall be on a biennial basis, and the license shall be eligible for no more than three renewals."

## supervision and practice restrictions

### `independent_practice_restricted_to_full_licensees` — bool
- **what:** Whether independent (unaffiliated, self-directed) practice is prohibited for associate or lower-tier licensees and reserved only for fully licensed practitioners.
- **states:** PA
- **sample (PA):** "A licensed associate professional counselor shall not practice in a private setting without the direction of a supervisor."

### `supervisor_minimum_experience_years` — int
- **what:** Minimum years of full-time professional experience a supervisor must have before being approved to supervise associate-level licensees.
- **states:** PA
- **sample (PA):** "A supervisor shall hold a current and active license to practice professional counseling or to practice in a related field as approved by the board and shall have no less than five full-time years of experience or the equivalent in the prior ten years."

### `supervision_plan_required` — bool
- **what:** Whether an applicant for an associate license must submit a formal supervision plan (including job description and supervision locations) as part of the application.
- **states:** PA
- **sample (PA):** "The applicant has submitted a plan of supervision, including a detailed job description and each location where client contact and supervision will occur."

## what practitioners are authorized to assess and diagnose

### `diagnosis_authority` — bool
- **what:** Whether licensees are explicitly authorized to perform diagnostic assessments using accepted classification systems such as the DSM.
- **states:** PA
- **sample (PA):** "The utilization of currently accepted diagnostic classifications by a clinical social worker, a marriage and family therapist or a professional counselor, including, but not limited to, the American Psychiatric Association's Diagnostic and Statistical Manual of Mental Disorders."

### `diagnosis_restricted_by_tier` — bool
- **what:** Whether lower-tier licensees (e.g., bachelor-level) are explicitly prohibited from diagnosing mental illness or providing psychotherapy.
- **states:** PA
- **sample (PA):** "Licensed bachelor social workers are not qualified to diagnose mental illness nor provide psychotherapy services."

### `insurance_billing_restricted_by_tier` — bool
- **what:** Whether lower-tier licensees are explicitly prohibited from billing health insurance plans for services rendered.
- **states:** PA
- **sample (PA):** "Bachelor social workers are not permitted to bill a health insurance plan for services rendered under this license."

## treatment methods and therapeutic approaches

### `arts_based_therapy_authorized` — bool
- **what:** Whether the statute explicitly authorizes the use of arts-based therapeutic approaches (art, dance, music, drama) as part of the scope of practice.
- **states:** PA
- **sample (PA):** "Professional counselors' utilization of verbal and nonverbal approaches and specialization in the use of arts-based therapeutic approaches, such as art, dance, music or drama, to accomplish treatment objectives."

### `family_systems_therapy_authorized` — bool
- **what:** Whether the statute explicitly authorizes the application of family systems theories and techniques as part of the scope of practice.
- **states:** PA
- **sample (PA):** "The professional application of psychotherapeutic and family systems theories and techniques to the evaluation, assessment, diagnosis and treatment of mental and emotional disorders."

## consumer protection and disclosure obligations

### `client_disclosure_statement_required` — bool
- **what:** Whether licensees are required to provide each client with a written disclosure statement before rendering services.
- **states:** PA
- **sample (PA):** "Marriage and family therapists and professional counselors licensed under this act shall furnish each client with a copy of a disclosure statement prior to rendering professional services."

### `disclosure_statement_required_contents` — list[str]
- **what:** Specific items the statute requires to be included in the client disclosure statement.
- **states:** PA
- **sample (PA):** "The formal professional education of the marriage and family therapist or professional counselor, including the institutions attended and the degrees received."

### `referral_obligation_for_out_of_scope_conditions` — bool
- **what:** Whether licensees are statutorily required to refer clients whose health problems fall outside the licensee's competence or scope of practice to appropriate licensed practitioners.
- **states:** PA
- **sample (PA):** "Licensees under this act shall refer health care problems which fall outside the boundaries of their professional competence and scope of practice as defined in section 3 to appropriate licensed practitioners."

## reciprocity and emergency practice

### `emergency_practice_without_license_allowed` — bool
- **what:** Whether out-of-state licensees may practice temporarily in the state without a local license during a declared state of emergency.
- **states:** PA
- **sample (PA):** "The board shall have the power to allow an individual who is licensed or certified as a clinical social worker, a marriage and family therapist or a professional counselor in another state to practice in this Commonwealth without licensure for no more than 60 days as part of a relief effort related to a state of emergency as declared by the Federal Government or the Governor."

### `emergency_practice_max_days` — int
- **what:** Maximum number of days an out-of-state licensee may practice without a local license during a declared emergency.
- **states:** PA
- **sample (PA):** "to practice in this Commonwealth without licensure for no more than 60 days as part of a relief effort related to a state of emergency"

## licensee health and impairment programs

### `impaired_professional_program_available` — bool
- **what:** Whether the state has a formal impaired professional program allowing the board to defer or dismiss disciplinary action while a licensee participates in an approved treatment program.
- **states:** PA
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the professional is progressing satisfactorily in an approved treatment program."

### `mandatory_reporting_of_impaired_colleagues` — bool
- **what:** Whether hospitals, health care facilities, peers, or colleagues are legally required to report a licensee who shows signs of active addiction, diversion of controlled substances, or mental/physical incompetence.
- **states:** PA
- **sample (PA):** "Any hospital or health care facility, peer or colleague who has substantial evidence that a professional has an active addictive disease for which the professional is not receiving treatment, is diverting a controlled substance or is mentally or physically incompetent to carry out the duties of his or her license shall make or cause to be made a report to the board."
