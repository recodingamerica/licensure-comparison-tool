# Discovered fields — social_work

## license types and credential levels

### `license_tiers` — list[str]
- **what:** The distinct named license tiers available within the regulated profession, from entry-level to advanced independent practice.
- **states:** PA
- **sample (PA):** "It shall be unlawful for any person to hold oneself forth as a licensed bachelor social worker, licensed social worker, licensed clinical social worker, licensed associate marriage and family therapist, licensed marriage and family therapist, licensed associate professional counselor or licensed professional counselor unless he or she shall first have obtained a license pursuant to this act."

### `associate_license_renewal_limit` — int
- **what:** Maximum number of biennial renewals permitted for an associate-level license before the holder must advance to full licensure or cease practice.
- **states:** PA
- **sample (PA):** "Renewal of an associate marriage and family therapist license shall be on a biennial basis, and the license shall be eligible for no more than three renewals."

### `credential_abbreviations` — list[str]
- **what:** Official post-nominal letter abbreviations authorized for each license tier (e.g., L.C.S.W., L.M.F.T., L.P.C.).
- **states:** PA
- **sample (PA):** "Only individuals who have received licenses as licensed clinical social workers under this act may style themselves as licensed clinical social workers and use the letters 'L.C.S.W.' in connection with their names."

## supervision and practice restrictions by tier

### `independent_practice_allowed` — bool
- **what:** Whether a given license tier permits independent (unsupervised, unaffiliated) private practice.
- **states:** PA
- **sample (PA):** "Licensed bachelor social workers may not practice in a private setting, practice independently or engage in clinical social work practice or hold themselves out as licensed social workers or licensed clinical social workers."

### `diagnosis_authority` — bool
- **what:** Whether a license tier is authorized to diagnose mental illness or conduct clinical assessments for diagnostic purposes.
- **states:** PA
- **sample (PA):** "Licensed bachelor social workers are not qualified to diagnose mental illness nor provide psychotherapy services."

### `insurance_billing_permitted` — bool
- **what:** Whether holders of a given license tier are permitted to bill health insurance plans for services rendered.
- **states:** PA
- **sample (PA):** "Bachelor social workers are not permitted to bill a health insurance plan for services rendered under this license."

### `supervisor_minimum_experience_years` — int
- **what:** Minimum years of full-time professional experience a supervisor must have to oversee an associate-level licensee.
- **states:** PA
- **sample (PA):** "A supervisor shall hold a current and active license to practice marriage and family therapy or to practice in a related field as approved by the board and shall have no less than five full-time years of experience or the equivalent in the prior ten years."

### `supervision_plan_required` — bool
- **what:** Whether an associate-level applicant must submit a formal supervision plan, including job description and practice locations, as part of licensure.
- **states:** PA
- **sample (PA):** "The applicant has submitted a supervision plan, including a detailed job description and each location where client contact and supervision will occur."

## what practitioners can assess and treat

### `diagnostic_classification_systems_authorized` — list[str]
- **what:** Named diagnostic classification systems that licensees are authorized to use within their scope of practice.
- **states:** PA
- **sample (PA):** "The utilization of currently accepted diagnostic classifications by a clinical social worker, a marriage and family therapist or a professional counselor, including, but not limited to, the American Psychiatric Association's Diagnostic and Statistical Manual of Mental Disorders."

### `psychotherapy_authorized` — bool
- **what:** Whether the license tier explicitly authorizes the provision of psychotherapy services.
- **states:** PA
- **sample (PA):** "The term includes the delivery of psychotherapeutic services to individuals, couples, families and groups for the purpose of treating the disorders."

### `arts_based_therapy_authorized` — bool
- **what:** Whether the scope of practice explicitly includes arts-based therapeutic modalities such as art, dance, music, or drama therapy.
- **states:** PA
- **sample (PA):** "Professional counselors' utilization of verbal and nonverbal approaches and specialization in the use of arts-based therapeutic approaches, such as art, dance, music or drama, to accomplish treatment objectives."

## consumer protection and disclosure obligations

### `client_disclosure_statement_required` — bool
- **what:** Whether licensees must provide clients with a written disclosure statement before rendering services.
- **states:** PA
- **sample (PA):** "Marriage and family therapists and professional counselors licensed under this act shall furnish each client with a copy of a disclosure statement prior to rendering professional services."

### `disclosure_statement_required_contents` — list[str]
- **what:** Specific items that must be included in the client disclosure statement as required by statute.
- **states:** PA
- **sample (PA):** "The statement shall include the following: The name, title, business address and business telephone number... The formal professional education... professional philosophy and approach to treatment... fee schedule listed by type of service or hourly rate."

### `referral_obligation` — bool
- **what:** Whether licensees are statutorily required to refer clients whose problems fall outside the licensee's scope of practice to appropriate licensed practitioners.
- **states:** PA
- **sample (PA):** "Licensees under this act shall refer health care problems which fall outside the boundaries of their professional competence and scope of practice as defined in section 3 to appropriate licensed practitioners."

## discipline and impairment programs

### `impaired_professional_program_available` — bool
- **what:** Whether the statute establishes a formal impaired professional program allowing deferred discipline for licensees in approved treatment.
- **states:** PA
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the professional is progressing satisfactorily in an approved treatment program."

### `mandatory_reporting_of_impaired_colleagues` — bool
- **what:** Whether peers, colleagues, or facilities are legally required to report a licensee believed to be impaired or diverting controlled substances.
- **states:** PA
- **sample (PA):** "Any hospital or health care facility, peer or colleague who has substantial evidence that a professional has an active addictive disease for which the professional is not receiving treatment, is diverting a controlled substance or is mentally or physically incompetent to carry out the duties of his or her license shall make or cause to be made a report to the board."

## reciprocity and emergency practice

### `emergency_practice_without_license_days` — int
- **what:** Maximum number of days an out-of-state licensee may practice in the state without a local license during a declared state of emergency.
- **states:** PA
- **sample (PA):** "The board shall have the power to allow an individual who is licensed or certified as a clinical social worker, a marriage and family therapist or a professional counselor in another state to practice in this Commonwealth without licensure for no more than 60 days as part of a relief effort related to a state of emergency."

### `exam_waiver_by_prior_practice_years` — int
- **what:** Minimum years of documented prior practice that may qualify an applicant for an examination waiver under a grandfathering or endorsement pathway.
- **states:** PA
- **sample (PA):** "Can demonstrate proof of practice of clinical social work for at least five of the seven years immediately prior to the date of application for license."

## governing board structure

### `board_composition_public_members` — int
- **what:** Number of public (non-professional) members required to sit on the regulatory board.
- **states:** PA
- **sample (PA):** "The board shall consist of 13 members who are citizens of the United States and who have been residents of this Commonwealth for a two-year period, two of whom shall be public members."

### `board_member_term_years` — int
- **what:** Standard length in years of a board member's term of office.
- **states:** PA
- **sample (PA):** "The members shall serve for four-year terms, except as provided in subsection (c), and shall be appointed by the Governor by and with the advice and consent of a majority of the members elected to the Senate."
