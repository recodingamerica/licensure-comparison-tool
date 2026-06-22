# Discovered fields — security_personnel

## who must be licensed and why

### `lethal_weapon_carry_required_for_regulation` — bool
- **what:** Whether the licensing/certification requirement is triggered specifically by carrying a lethal weapon as an incidence of employment, rather than by the act of working as security personnel generally.
- **states:** PA
- **sample (PA):** "All privately employed agents, except those who have been granted a waiver from compliance herewith by the commissioner who, as an incidence to their employment, carry a lethal weapon shall be required to attend the program"

## weapons and use of force rules

### `lethal_weapon_definition_excludes` — list[str]
- **what:** Substances or devices explicitly excluded from the statutory definition of 'lethal weapons'.
- **states:** PA
- **sample (PA):** "The chemical mace or any similar substance shall not be considered as 'lethal weapons' for the purposes of this act."

### `approved_firearm_type` — str
- **what:** The type or category of firearm that certified personnel are authorized to carry, as specified or approved by the regulatory authority.
- **states:** PA
- **sample (PA):** "he shall carry only a powder actuated firearm approved by the commissioner"

### `inoperative_firearm_prohibited` — bool
- **what:** Whether certified personnel are explicitly prohibited from carrying inoperative or model firearms while on duty.
- **states:** PA
- **sample (PA):** "No individual certified under this act shall carry an inoperative or model firearm while employed"

## fitness and background screening

### `physical_psychological_screening_required` — bool
- **what:** Whether applicants must pass physical and psychological testing before being admitted to the training program or receiving certification.
- **states:** PA
- **sample (PA):** "To implement and administer or approve physical and psychological testing and screening of the candidate for the purpose of barring from the program those not physically or mentally fit to handle lethal weapons."

### `criminal_history_disqualifier` — str
- **what:** The specific criminal history criterion that disqualifies an applicant from certification (e.g., conviction of or plea to a crime of violence).
- **states:** PA
- **sample (PA):** "if the commissioner determines that the applicant is eighteen years of age and has not been convicted of or has not pleaded guilty or nolo contendere to a crime of violence"

### `fingerprint_check_required` — bool
- **what:** Whether applicants must submit fingerprints for examination by state and/or federal law enforcement agencies as part of the application process.
- **states:** PA
- **sample (PA):** "The fingerprints of the applicant shall be examined by the Pennsylvania State Police and the Federal Bureau of Investigation to determine if he has been convicted of or has pleaded guilty or nolo contendere to a crime of violence."

## on-duty identification and certificate requirements

### `certificate_must_be_carried_on_duty` — bool
- **what:** Whether certified personnel are legally required to carry their certification credential on their person while on duty or traveling to and from duty while armed.
- **states:** PA
- **sample (PA):** "Every certified individual shall carry his wallet or billfold size certificate on his person as identification during the time when he is on duty or going to and from duty and carrying a lethal weapon."

### `certificate_format` — str
- **what:** The prescribed physical format of the certification credential issued to qualified personnel.
- **states:** PA
- **sample (PA):** "The commissioner shall furnish to each individual satisfactorily completing the program, an appropriate wallet or billfold size copy of the certificate, which shall include a photograph of the individual thereon."

## employer obligations and oversight

### `employer_discharge_notification_required` — bool
- **what:** Whether employers are required to notify the regulatory authority when a certified employee is discharged for cause.
- **states:** PA
- **sample (PA):** "Whenever an employer of a privately employed agent subject to the provisions of this act discharges him for cause, the employer shall notify the commissioner of such within five days of the discharge."

### `employer_program_participation_prohibited` — bool
- **what:** Whether non-government employers of armed security personnel are prohibited from owning, operating, or participating in the training program their employees must attend.
- **states:** PA
- **sample (PA):** "Except for colleges and universities, no nongovernment employer of a privately employed agent who, as an incidence to his employment, carries a lethal weapon, shall own, operate, or otherwise participate in, directly or indirectly, the establishment or administration of the program"

## exemptions and waivers for prior law enforcement experience

### `retired_officer_expedited_certification` — bool
- **what:** Whether retired police officers with qualifying service may receive initial certification without meeting standard training, qualification, or physical/psychological requirements.
- **states:** PA
- **sample (PA):** "A nondisability retired police officer of a Pennsylvania municipality or the Pennsylvania State Police shall be initially certified under this act, and need not meet the training and qualification standards or physical and psychological qualifications hereunder, if he was a full-time police officer for at least twenty years, retired in good standing"

### `retired_officer_minimum_service_years` — int
- **what:** Minimum years of full-time police service required for a retired officer to qualify for expedited certification without standard training requirements.
- **states:** PA
- **sample (PA):** "if he was a full-time police officer for at least twenty years, retired in good standing"

### `retired_officer_post_retirement_window_years` — int
- **what:** Maximum number of years after retirement within which a retired officer may assume security duties and still qualify for expedited certification without physical/psychological re-screening.
- **states:** PA
- **sample (PA):** "has assumed the duties of a privately employed agent on or before three years from the date of his retirement"

### `active_officer_training_waiver_available` — bool
- **what:** Whether active police officers who have completed a recognized municipal police training program are automatically granted a waiver of the security personnel training requirements.
- **states:** PA
- **sample (PA):** "All active police officers subject to the training provisions of the act of June 18, 1974 (P.L.359, No.120), referred to as the Municipal Police Education and Training Law, shall be granted a waiver of the training requirements of this act"

### `firearms_qualification_exam_interval_years` — int
- **what:** The recurring interval (in years) at which active police officers must pass a firearms qualification examination administered by their agency to maintain their training waiver.
- **states:** PA
- **sample (PA):** "the successful completion of a biennial firearms qualification examination administered by their respective police agency"
