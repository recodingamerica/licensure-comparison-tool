# Discovered fields — occupational_therapy

## license types and credential levels

### `license_tiers` — list[str]
- **what:** The distinct license or credential classifications recognized by the state for occupational therapy practice.
- **states:** PA, UT
- **sample (UT):** "The division shall issue to a person who qualifies under this chapter a license in the classification of: (a) occupational therapist; or (b) occupational therapy assistant."

### `ota_aide_tier_recognized` — bool
- **what:** Whether the state recognizes an unlicensed occupational therapy aide as a distinct support role with defined limitations.
- **states:** PA, UT
- **sample (UT):** ""Occupational therapy aide" means a person who is not licensed under this chapter but who provides supportive services under the supervision of an occupational therapist or occupational therapy assistant."

## referral and independent practice rules

### `referral_required_for_direct_treatment` — bool
- **what:** Whether a referral from another licensed health care provider is required before an occupational therapist may initiate direct treatment for a specific medical condition.
- **states:** PA, UT
- **sample (PA):** "Implementation of direct occupational therapy to an individual for a specific medical condition shall be based on a referral from a licensed physician, licensed optometrist, licensed podiatrist, licensed certified registered nurse practitioner or licensed physician assistant."

### `referral_sources_authorized` — list[str]
- **what:** The categories of licensed providers whose referral authorizes direct occupational therapy treatment, where a referral is required.
- **states:** PA, UT
- **sample (PA):** "Implementation of direct occupational therapy to an individual for a specific medical condition shall be based on a referral from a licensed physician, licensed optometrist, licensed podiatrist, licensed certified registered nurse practitioner or licensed physician assistant."

### `indirect_services_without_referral_permitted` — bool
- **what:** Whether an occupational therapist may enter a case and provide evaluation, consultation, or indirect services without a referral.
- **states:** PA, UT
- **sample (PA):** "An occupational therapist may enter a case for the purposes of providing indirect services, consultation, evaluating an individual as to the need for services and other occupational therapy services for conditions such as perceptual, cognitive, sensory integration and similar conditions."

## supervision and delegation rules

### `ota_supervision_face_to_face_frequency` — str
- **what:** The minimum required frequency and modality of face-to-face contact between a supervising occupational therapist and a supervised occupational therapy assistant.
- **states:** PA, UT
- **sample (UT):** "meet face to face with the supervised occupational therapy assistant as often as necessary but at least once every two weeks in person or by video conference, and at least one time every month in person"

### `ota_supervisor_client_review_frequency` — str
- **what:** The minimum required frequency with which the supervising occupational therapist must personally meet with each client referred to an occupational therapy assistant.
- **states:** PA, UT
- **sample (UT):** "meet with each client who has been referred to a supervised occupational therapy assistant at least once each month, to further assess the patient, evaluate the treatment, and modify the individual's treatment plan"

### `max_ota_per_supervising_ot` — str
- **what:** The maximum number of occupational therapy assistants a single occupational therapist may supervise at one time, including any distinction between full-time and part-time assistants.
- **states:** PA, UT
- **sample (UT):** "supervise no more than two full-time occupational therapy assistants at one time, or four part-time occupational therapy assistants if the combined work hours of the assistants do not exceed 40 hours per week"

### `ota_treatment_plan_authority` — list[str]
- **what:** The specific treatment plan actions an occupational therapy assistant is and is not authorized to perform (e.g., write, modify, contribute, maintain).
- **states:** PA, UT
- **sample (UT):** "An occupational therapy assistant: (b) may not write an individual treatment plan; (c) may not approve or cosign modifications to an individual treatment plan; and (d) may contribute to and maintain an individual treatment plan."

### `aide_scope_limitations` — list[str]
- **what:** The specific restrictions on what tasks an occupational therapy aide may perform, including supervision level required and task type constraints.
- **states:** PA, UT
- **sample (UT):** "An occupational therapy aide: (a) may only perform occupational therapy services under the direct supervision of an occupational therapist or an occupational therapy assistant; (b) may not write, modify, contribute, or maintain an individual treatment plan; and (c) may only perform tasks that are repetitive and routine for which the aide has been trained and has demonstrated competence."

## treatment planning and documentation

### `individual_treatment_plan_required` — bool
- **what:** Whether the state statute defines and requires a written individual treatment plan for each client receiving occupational therapy services.
- **states:** PA, UT
- **sample (UT):** ""Individual treatment plan" means a written record composed for each client by a person licensed under this chapter to engage in the practice of occupational therapy."

## insurance and financial responsibility

### `professional_liability_insurance_required` — bool
- **what:** Whether the state requires occupational therapists to obtain and maintain professional liability insurance as a condition of licensure.
- **states:** PA, UT
- **sample (PA):** "Effective by the next biennial period for license renewal following the effective date of this paragraph, an occupational therapist shall obtain and maintain professional liability insurance as specified in subparagraphs (ii) and (iii)."

### `professional_liability_insurance_minimum_per_occurrence` — int
- **what:** The minimum required professional liability insurance coverage amount per occurrence or claims-made, in dollars.
- **states:** PA, UT
- **sample (PA):** "The level of professional liability insurance coverage shall be in the minimum amount of $1,000,000 per occurrence or claims made."

## background screening requirements

### `criminal_background_check_required` — bool
- **what:** Whether applicants for licensure are required to submit to a criminal background check, including fingerprinting.
- **states:** PA, UT
- **sample (UT):** "consent to a fingerprint background check conducted by the Bureau of Criminal Identification and the Federal Bureau of Investigation regarding the application."

## advanced techniques requiring extra training

### `advanced_technique_training_required` — bool
- **what:** Whether the state authorizes occupational therapists to perform advanced techniques (such as physical agent modalities, manual therapy, or dry needling) only after completing additional specified training.
- **states:** PA, UT
- **sample (UT):** "applying physical agent modalities, managing wound care, and using manual therapy techniques to enhance an individual's performance skills, if the occupational therapist has received the necessary training as determined by division rule in collaboration with the board."

### `advanced_techniques_authorized` — list[str]
- **what:** The specific advanced clinical techniques that occupational therapists are authorized to perform upon completion of required additional training.
- **states:** PA, UT
- **sample (UT):** "applying physical agent modalities, managing wound care, dry needling, and using manual therapy techniques to enhance an individual's performance skills, if the occupational therapist has received the necessary training as determined by division rule in collaboration with the board."

### `dry_needling_registration_required` — bool
- **what:** Whether occupational therapists who wish to perform trigger point dry needling must complete a separate registration process with the state beyond holding a standard OT license.
- **states:** PA, UT
- **sample (UT):** "An occupational therapist may practice trigger point dry needling if the occupational therapist: ... (d) registers with the division as a trigger point dry needling practitioner."

## multistate practice and portability

### `interstate_compact_participation` — bool
- **what:** Whether the state participates in the Occupational Therapy Licensure Compact, allowing licensees to practice across member states under a compact privilege.
- **states:** PA, UT
- **sample (UT):** ""Compact Privilege" means the authorization, which is equivalent to a license, granted by a Remote State to allow a Licensee from another Member State to practice as an Occupational Therapist or practice as an Occupational Therapy Assistant in the Remote State under its laws and rules."

### `telehealth_authorized` — bool
- **what:** Whether the state statute explicitly recognizes telehealth as an authorized modality for delivering occupational therapy services.
- **states:** PA, UT
- **sample (UT):** ""Telehealth" means the application of telecommunication technology to deliver Occupational Therapy services for assessment, intervention and/or consultation."

## what occupational therapists are not allowed to do

### `mental_health_therapy_excluded` — bool
- **what:** Whether the state statute explicitly prohibits occupational therapists from engaging in the practice of mental health therapy.
- **states:** PA, UT
- **sample (UT):** "Nothing in this chapter shall permit an individual licensed under this chapter to engage in the practice of mental health therapy."

## practitioner health and discipline alternatives

### `impaired_professional_program_available` — bool
- **what:** Whether the state provides a formal impaired professional or alternative monitoring program as an option in lieu of or alongside disciplinary action for licensees with substance abuse or health conditions.
- **states:** PA, UT
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the licensee is progressing satisfactorily in an approved treatment program."
