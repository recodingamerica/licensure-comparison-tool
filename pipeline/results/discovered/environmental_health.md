# Discovered fields — environmental_health

## professional title and credential type

### `credential_title` — enum[Registered Sanitarian (R.S.), Environmental Health Specialist (E.H.S.), Licensed Environmental Health Specialist (L.E.H.S. / R.E.H.S.), Licensed Environmental Health Practitioner (L.E.H.P.), Environmental Health Practitioner (E.H.P.), Registered Environmental Health Specialist (R.E.H.S.)]
- **what:** The official title and post-nominal abbreviation conferred upon a fully credentialed environmental health professional, which varies by state.
- **states:** AR, AZ, CT, IL, KY, LA, MD, MT, … (+2)
- **sample (AZ):** "Only a person with a valid registration certificate issued pursuant to this section may use the title "registered sanitarian" or the abbreviation "R.S." after the registrant's name."

### `trainee_credential_title` — enum[Sanitarian-in-Training, Sanitarian Trainee, Environmental Health Practitioner in Training (L.E.H.P. in Training), Environmental Health Specialist-in-Training, Registered Environmental Health Specialist Intern]
- **what:** The official title for a person who meets educational qualifications but has not yet completed experience or examination requirements for full licensure.
- **states:** AR, AZ, IL, LA, MD, MT, NC
- **sample (AR):** ""Sanitarian-in-training" means a person who meets the educational qualifications as provided in this chapter but does not meet the experience requirements of this chapter for registration as a registered sanitarian."

### `trainee_permit_max_duration_years` — int
- **what:** Maximum number of years a trainee or in-training permit may be held before the holder must qualify for full licensure.
- **states:** IL, LA, MD, NC
- **sample (LA):** "Such permits shall not be issued for a period in excess of two years."

### `tiered_license_levels` — bool
- **what:** Whether the state establishes multiple formal tiers or grades of credential (e.g., associate, specialist, inspector) with different scopes of authorized practice.
- **states:** AZ, IL, NC, ND
- **sample (AZ):** "The council shall provide for the classification of sanitarians, establish standards for persons employed as sanitarians."

## who must be licensed and where they work

### `employment_sector_restriction` — enum[public sector only, public and private sector, government employment triggers requirement]
- **what:** Whether the licensure requirement applies only to those employed in the public/government sector or to all practitioners regardless of employer.
- **states:** AZ, KY, MT, NC
- **sample (AZ):** "A person shall not be employed as a sanitarian by this state or any political subdivision of this state unless that person is registered by the department as a sanitarian of the class determined by the council to be appropriate for the performance of the functions of that person's employment."

### `exempted_occupations` — list[str]
- **what:** Categories of workers or professionals explicitly exempted from the environmental health licensure requirement.
- **states:** CT, IL, MD, MT, NC
- **sample (IL):** "This Act does not prohibit or restrict any of the following: ... A person licensed in this State under any other Act from engaging in the practice for which he or she is licensed. ... A person working in laboratories licensed by, registered with, or operated by the State of Illinois."

### `employer_prohibition_on_unlicensed_hire` — bool
- **what:** Whether the statute explicitly prohibits employers (agencies, firms, or governments) from hiring unlicensed persons to perform environmental health duties.
- **states:** KY, LA
- **sample (LA):** "It shall be unlawful for any department, board, commission or other agency of the state of Louisiana or of any district, parish or municipal governing body or for any person, firm or corporation to employ any sanitarian or sanitarian trainee who is not licensed or otherwise authorized by the board."

## what the job covers

### `scope_of_practice_areas` — list[str]
- **what:** Enumerated program or subject-matter areas that constitute the recognized scope of environmental health practice.
- **states:** IL, KY, MD, MT, NC, ND
- **sample (IL):** ""Environmental health practice" is the practice of environmental health by licensed environmental health practitioners within the meaning of this Act and includes, but is not limited to, the following areas of professional activities: milk and food sanitation; protection and regulation of private water supplies; private waste water management; domestic solid waste disposal practices; institutional health and safety; and consultation and education in these fields."

## education details

### `natural_science_semester_hours_required` — int
- **what:** Minimum number of semester credit hours in natural, physical, or biological sciences required as part of the qualifying degree.
- **states:** AR, AZ, IL, LA, MD, NC
- **sample (AR):** "A college graduate in one (1) of the natural sciences, i.e., biology, chemistry, physics, math, earth science, or geology, or engineering, with a minimum of thirty (30) semester hours or its equivalent of those subjects."

### `neha_accreditation_accepted` — bool
- **what:** Whether graduation from a program accredited by the National Environmental Health Association (NEHA) Accreditation Council (EHAC) satisfies the educational requirement.
- **states:** IL, NC
- **sample (IL):** "A Bachelor's Degree in environmental health science from a college or university approved by the National Environmental Health Association Accreditation Council for environmental health curricula or its equivalent as approved by the Department."

### `military_experience_substitution` — bool
- **what:** Whether full-time military service in the field of environmental health may substitute for civilian education or experience requirements.
- **states:** AZ, IL
- **sample (AZ):** "Has satisfactorily completed at least three years of full-time military duty in the field of environmental health."

### `field_experience_required_months` — int
- **what:** Minimum months of field or work experience in environmental health required before full licensure (distinct from the post-degree supervised training program).
- **states:** AR, CT, LA, MD, NC
- **sample (LA):** "Prior to being issued a license as a sanitarian, all sanitarian trainees shall have completed a minimum of one year of field experience."

### `board_approved_training_course_substitution` — bool
- **what:** Whether completion of a board-approved special training course may substitute for a portion of the required field experience.
- **states:** CT, LA, NC
- **sample (CT):** "An applicant who successfully completes a special training course in environmental health approved by the commissioner may substitute such course for six months of such required experience in the field of environmental health."

## supervision and delegation

### `supervision_required_for_trainees` — bool
- **what:** Whether trainees or in-training licensees are explicitly required to work under the supervision of a fully licensed environmental health professional.
- **states:** CT, IL, LA, MD, NC
- **sample (IL):** "An environmental health practitioner in training may engage in the practice of environmental health for a period not to exceed 6 years provided that he or she is supervised by a licensed professional engineer or a licensed environmental health practitioner as prescribed in this Act."

### `licensed_professional_engineer_as_supervisor` — bool
- **what:** Whether a licensed professional engineer is explicitly authorized to serve as a supervisor for environmental health trainees or inspectors in lieu of a licensed environmental health practitioner.
- **states:** IL, MD
- **sample (IL):** "A licensed environmental health practitioner or a licensed professional engineer may serve as a supervisor to any licensed environmental health practitioner in training or environmental health inspector."

### `supervisor_daily_availability_required` — bool
- **what:** Whether the supervising practitioner is explicitly required to be available for consultation on a daily basis.
- **states:** IL, LA
- **sample (IL):** "The supervisor shall fulfill the minimum supervisor requirements, including but not limited to: (1) being available for consultation on a daily basis."

## license status and renewal options

### `inactive_status_available` — bool
- **what:** Whether the state provides a formal inactive status option that allows a licensee to maintain the credential without actively practicing, typically with reduced or waived fees and CE requirements.
- **states:** IL, KY, MD
- **sample (KY):** "Those persons previously registered by the cabinet and not engaged in environmental health practice in the Commonwealth of Kentucky, but desiring to maintain the privilege to use the designation of environmental health specialist or "E.H.S." and sanitarian or "R.S." may apply and be granted inactive status by the cabinet."

### `inactive_status_max_duration_years` — int
- **what:** Maximum number of years a licensee may remain on inactive status before the license lapses or must be reactivated.
- **states:** IL, MD
- **sample (MD):** "The Board shall place a licensed environmental health specialist on inactive status for a period not to exceed 4 years."

### `continuing_education_hours_per_period` — int
- **what:** Number of continuing education hours required per renewal period for active licensees.
- **states:** AZ, IL, KY, LA, MD, NC
- **sample (LA):** "The council may establish minimum continuing education requirements for the renewal of a license, which requirements shall not exceed eight annual contact hours as approved by the board."

## reciprocity and endorsement

### `reciprocity_experience_requirement_years` — int
- **what:** Minimum years of experience in environmental health required of an out-of-state applicant seeking licensure by reciprocity or endorsement without examination.
- **states:** AR, MD
- **sample (AR):** "Has had at least two (2) years' experience in the field of environmental sanitation."

### `neha_rehs_credential_accepted_for_endorsement` — bool
- **what:** Whether holding the national NEHA Registered Environmental Health Specialist/Registered Sanitarian (REHS/RS) credential is explicitly accepted as a basis for licensure by endorsement without examination.
- **states:** IL, NC
- **sample (IL):** "The Department shall issue a license as a licensed environmental health practitioner to any applicant who holds a Registered Environmental Health Specialist/Registered Sanitarian credential in good standing with the National Environmental Health Association."

## professional conduct and discipline

### `code_of_ethics_required` — bool
- **what:** Whether the statute explicitly requires the board to adopt a formal code of ethics and/or requires licensees to adhere to it as a condition of registration.
- **states:** MD, NC, ND
- **sample (NC):** "The Board shall prepare and adopt, by rule, a Code of Ethics to be made available in writing to all registered environmental health specialists and registered environmental health specialist interns and each applicant for registration under this Article. All registered environmental health specialists and registered environmental health specialist interns shall adhere to the Code of Ethics adopted by the Board."

### `mandatory_peer_reporting_obligation` — bool
- **what:** Whether licensed practitioners are explicitly required by statute to report known violations or grounds for discipline by colleagues to the board.
- **states:** MD, NC
- **sample (MD):** "If a licensed environmental health specialist knows of an action or condition that might be grounds for action under subsection (b) of this section, the licensed environmental health specialist shall report the action or condition to the Board."

### `unlicensed_practice_criminal_penalty_class` — enum[misdemeanor (unspecified), Class A misdemeanor, Class 1 misdemeanor, Class 2 misdemeanor, misdemeanor with fine and/or imprisonment]
- **what:** The criminal classification assigned to unlicensed practice of environmental health.
- **states:** IL, LA, MD, NC
- **sample (IL):** "A person who engages or offers to engage in environmental health practice in this State without being licensed for that purpose, or whose license has been suspended or revoked, or who violates any of the provisions of this Act for which no specific penalty has been provided is guilty of a Class A misdemeanor."

### `civil_penalty_for_unlicensed_practice` — bool
- **what:** Whether the statute authorizes a civil monetary penalty (in addition to or instead of criminal penalties) for practicing without a license.
- **states:** IL, MD, NC
- **sample (IL):** "Any person who practices, offers to practice, attempts to practice, or holds himself or herself out to practice environmental health without being licensed under this Act shall, in addition to any other penalty provided by law, pay a civil penalty to the Department in an amount not to exceed $5,000 for each offense."

## governing board composition

### `board_member_public_representative_required` — bool
- **what:** Whether the statute requires at least one non-practitioner public or consumer representative on the governing board.
- **states:** AR, AZ, IL, LA, NC, ND
- **sample (AR):** "One (1) member shall not be actively engaged in the business of sanitation or retired as a sanitarian and shall represent consumers."

### `board_member_practitioner_minimum_experience_years` — int
- **what:** Minimum years of experience in environmental health required for practitioner members appointed to the governing board.
- **states:** AR, IL
- **sample (IL):** "Each of the environmental health practitioners shall have at least 5 years of full time employment in the field of environmental health practice before the date of appointment."

### `board_member_count` — int
- **what:** Total number of members on the state environmental health governing or examining board.
- **states:** AR, AZ, IL, KY, LA, NC
- **sample (IL):** "The Board of Environmental Health Practitioners is created and shall exercise its duties as provided in this Act. The Board shall consist of 5 members appointed by the Secretary."
