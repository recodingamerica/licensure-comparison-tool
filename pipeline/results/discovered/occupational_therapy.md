# Discovered fields — occupational_therapy

## license types and tiers

### `license_tiers` — list[str]
- **what:** The distinct license classifications or unlicensed support roles recognized by statute for this profession.
- **states:** UT
- **sample (UT):** "The division shall issue to a person who qualifies under this chapter a license in the classification of: (a) occupational therapist; or (b) occupational therapy assistant."

### `mental_health_therapy_excluded` — bool
- **what:** Whether the statute explicitly prohibits licensees from engaging in the practice of mental health therapy.
- **states:** UT
- **sample (UT):** "Nothing in this chapter shall permit an individual licensed under this chapter to engage in the practice of mental health therapy."

## treatment planning and documentation

### `individual_treatment_plan_required` — bool
- **what:** Whether the statute requires a written individual treatment plan to be composed for each client.
- **states:** UT
- **sample (UT):** "'Individual treatment plan' means a written record composed for each client by a person licensed under this chapter to engage in the practice of occupational therapy."

### `assistant_treatment_plan_restrictions` — list[str]
- **what:** Specific restrictions on what an occupational therapy assistant may or may not do with respect to the individual treatment plan.
- **states:** UT
- **sample (UT):** "An occupational therapy assistant: (b) may not write an individual treatment plan; (c) may not approve or cosign modifications to an individual treatment plan; and (d) may contribute to and maintain an individual treatment plan."

### `aide_treatment_plan_restrictions` — list[str]
- **what:** Specific restrictions on what an occupational therapy aide may or may not do with respect to the individual treatment plan.
- **states:** UT
- **sample (UT):** "An occupational therapy aide: (b) may not write, modify, contribute, or maintain an individual treatment plan; and (c) may only perform tasks that are repetitive and routine for which the aide has been trained and has demonstrated competence."

## supervision and delegation

### `supervisor_client_contact_frequency` — str
- **what:** How often the supervising occupational therapist must personally meet with each client referred to an occupational therapy assistant.
- **states:** UT
- **sample (UT):** "meet with each client who has been referred to a supervised occupational therapy assistant at least once each month... except that if the interval of client care occurs one time per month or less, the occupational therapist shall meet with the client at least once every four visits"

### `supervisor_assistant_contact_frequency` — str
- **what:** How often the supervising occupational therapist must meet face-to-face with the supervised occupational therapy assistant.
- **states:** UT
- **sample (UT):** "meet face to face with the supervised occupational therapy assistant as often as necessary but at least once every two weeks in person or by video conference, and at least one time every month in person"

### `max_assistants_per_supervisor` — str
- **what:** The maximum number of occupational therapy assistants a single supervising occupational therapist may supervise at one time.
- **states:** UT
- **sample (UT):** "supervise no more than two full-time occupational therapy assistants at one time, or four part-time occupational therapy assistants if the combined work hours of the assistants do not exceed 40 hours per week"

### `aide_supervision_level` — enum[direct supervision, general supervision]
- **what:** The level of supervision required when an occupational therapy aide provides services.
- **states:** UT
- **sample (UT):** "An occupational therapy aide: (a) may only perform occupational therapy services under the direct supervision of an occupational therapist or an occupational therapy assistant"

## fieldwork and supervised training requirements

### `fieldwork_weeks_ot` — int
- **what:** Minimum number of weeks of supervised fieldwork experience required for licensure as an occupational therapist.
- **states:** UT
- **sample (UT):** "if applying for licensure on or after July 1, 2015, complete a minimum of 24 weeks of supervised fieldwork experience"

### `fieldwork_weeks_ota` — int
- **what:** Minimum number of weeks of supervised fieldwork experience required for licensure as an occupational therapy assistant.
- **states:** UT
- **sample (UT):** "if applying for licensure on or after July 1, 2015, complete a minimum of 16 weeks of supervised fieldwork experience"

## advanced and specialized techniques requiring extra training

### `dry_needling_authorized` — bool
- **what:** Whether occupational therapists are authorized to perform trigger point dry needling with additional training.
- **states:** UT
- **sample (UT):** "applying physical agent modalities, managing wound care, dry needling, and using manual therapy techniques to enhance an individual's performance skills, if the occupational therapist has received the necessary training as determined by division rule in collaboration with the board"

### `dry_needling_registration_required` — bool
- **what:** Whether a separate registration with the division is required before an occupational therapist may practice trigger point dry needling.
- **states:** UT
- **sample (UT):** "An occupational therapist may practice trigger point dry needling if the occupational therapist: ... (d) registers with the division as a trigger point dry needling practitioner"

### `dry_needling_course_hours` — int
- **what:** Minimum total course hours required to qualify for trigger point dry needling practice.
- **states:** UT
- **sample (UT):** "at least 304 total course hours, including a minimum of: (A) 54 hours of in-person instruction; and (B) 250 supervised patient treatment hours"

### `physical_agent_modalities_authorized` — bool
- **what:** Whether occupational therapists are authorized to apply physical agent modalities with appropriate training.
- **states:** UT
- **sample (UT):** "applying physical agent modalities, managing wound care, and using manual therapy techniques to enhance an individual's performance skills, if the occupational therapist has received the necessary training as determined by division rule in collaboration with the board"

## patient access and referral rules

### `referral_required` — bool
- **what:** Whether a referral from another health care provider is required before an occupational therapist may evaluate or treat a client.
- **states:** UT
- **sample (UT):** "An occupational therapist may evaluate, initiate, and provide occupational therapy treatment for a client without a referral from another health service provider."

## multistate practice and telehealth

### `interstate_compact_member` — bool
- **what:** Whether the state has enacted the Occupational Therapy Licensure Compact allowing multistate practice privileges.
- **states:** UT
- **sample (UT):** "'Compact Privilege' means the authorization, which is equivalent to a license, granted by a Remote State to allow a Licensee from another Member State to practice as an Occupational Therapist or practice as an Occupational Therapy Assistant in the Remote State under its laws and rules."

### `telehealth_authorized` — bool
- **what:** Whether the statute or compact expressly authorizes delivery of occupational therapy services via telehealth.
- **states:** UT
- **sample (UT):** "'Telehealth' means the application of telecommunication technology to deliver Occupational Therapy services for assessment, intervention and/or consultation."

### `jurisprudence_exam_required` — bool
- **what:** Whether applicants for a compact privilege must demonstrate knowledge of the state's specific laws and rules governing occupational therapy practice.
- **states:** UT
- **sample (UT):** "'Jurisprudence Requirement' means the assessment of an individual's knowledge of the laws and rules governing the Practice of Occupational Therapy in a State."

## background check and fitness requirements

### `criminal_background_check_required` — bool
- **what:** Whether applicants for licensure must consent to and complete a criminal background check including fingerprinting.
- **states:** UT
- **sample (UT):** "An applicant for licensure under this chapter who requires a criminal background check shall: (a) submit fingerprint cards in a form acceptable to the division at the time the license application is filed; and (b) consent to a fingerprint background check conducted by the Bureau of Criminal Identification and the Federal Bureau of Investigation"
