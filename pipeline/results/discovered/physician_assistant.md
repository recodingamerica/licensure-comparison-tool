# Discovered fields — physician_assistant

## supervision and collaboration requirements

### `collaboration_hours_threshold_initial` — int
- **what:** Number of post-graduate clinical practice hours during which a PA must engage in active collaboration with a physician before being permitted to practice more independently.
- **states:** UT
- **sample (UT):** "engage in collaboration with a physician for the first 4,000 hours of the physician assistant's post-graduate clinical practice experience"

### `collaboration_hours_threshold_independent` — int
- **what:** Total post-graduate clinical practice hours after which a PA may practice without a formal written collaborative agreement.
- **states:** UT
- **sample (UT):** "A physician assistant with less than 10,000 hours of post-graduate clinical practice experience shall: (a) practice under written policies and procedures established at a practice level"

### `written_collaborative_agreement_required` — bool
- **what:** Whether a PA is required to maintain a written collaborative agreement with a physician or senior PA during a defined phase of practice experience.
- **states:** UT
- **sample (UT):** "a physician assistant who has more than 4,000 hours of practice experience and less than 10,000 hours of practice experience shall enter into a written collaborative agreement"

### `new_specialty_collaboration_hours_required` — int
- **what:** Minimum hours of supervised collaboration required when a PA changes to a new specialty in which they have insufficient experience.
- **states:** UT
- **sample (UT):** "A physician assistant who wishes to change specialties to another specialty in which the PA has less than 4,000 hours of experience shall engage in collaboration for a minimum of 4,000 hours with a physician who is trained and experienced in the specialty"

## extra credentials and tiered license types

### `temporary_license_available` — bool
- **what:** Whether the state offers a temporary license to PA applicants who have completed their program but have not yet passed the required examination.
- **states:** UT
- **sample (UT):** "An applicant for licensure as a physician assistant who has met all qualifications for licensure except passing an examination component...may apply for and be granted a temporary license"

### `temporary_license_max_days` — int
- **what:** Maximum duration in days for which a temporary pre-examination license may be held.
- **states:** UT
- **sample (UT):** "The temporary license shall be issued for a period not to exceed 120 days to allow the applicant to pass the Physician Assistant National Certifying Examination."

### `mental_health_specialty_credential_available` — bool
- **what:** Whether the state recognizes a distinct specialty credential or qualification pathway for PAs who wish to practice mental health therapy.
- **states:** UT
- **sample (UT):** "A physician assistant specializing in mental health care under this section shall...obtain and maintain a Certification of Added Qualification in psychiatry issued by the National Commission on Certification of Physician Assistants"

### `mental_health_specialty_clinical_hours_required` — int
- **what:** Total clinical practice hours in mental health required for a PA to qualify for the mental health specialty credential.
- **states:** UT
- **sample (UT):** "A physician assistant specializing in mental health care under this section shall complete 10,000 hours of clinical practice in mental health."

## procedures that are restricted or require extra steps

### `general_anesthesia_prohibited` — bool
- **what:** Whether PAs are generally prohibited from administering general anesthetics, subject to defined exceptions.
- **states:** UT
- **sample (UT):** "Except as provided in Subsections (c) through (e), a physician assistant may not administer general anesthetics."

### `minimal_sedation_authorized` — bool
- **what:** Whether PAs are explicitly authorized to perform minimal sedation or anxiolysis within their scope of practice.
- **states:** UT
- **sample (UT):** "A physician assistant may perform minimal sedation anxiolysis if the procedure is within the physician assistant's scope of practice."

### `rapid_sequence_intubation_authorized_with_conditions` — bool
- **what:** Whether PAs may perform rapid sequence induction for intubation subject to specific credentialing and availability conditions.
- **states:** UT
- **sample (UT):** "A physician assistant may perform rapid sequence induction for intubation of a patient if...the physician assistant holds a valid ALS/ACLS certification and is credentialed and privileged at the hospital where the procedure is performed"

### `neurostimulation_neuromodulation_restricted` — bool
- **what:** Whether PAs are prohibited from administering neurostimulation or neuromodulation except under physician supervision in a health care facility.
- **states:** UT
- **sample (UT):** "A physician assistant may not administer neurostimulation or neuromodulation...Subsection (4)(a) does not apply to neurostimulation or neuromodulation administered by a physician assistant: (i) in a health care facility; and (ii) under supervision of a physician"

## what they are allowed to sign and certify

### `document_authentication_authority` — bool
- **what:** Whether PAs are explicitly authorized to authenticate documents (sign, certify, stamp, verify, etc.) to the same extent as a physician, within their scope of practice.
- **states:** UT
- **sample (UT):** "A physician assistant may authenticate through a signature, certification, stamp, verification, affidavit, or endorsement any document that may be authenticated by a physician and that is within the physician assistant's scope of practice."

## how they must identify themselves to patients

### `title_and_identification_requirements` — list[str]
- **what:** Specific statutory requirements governing how a PA must identify themselves to patients and the public, including badge and title rules.
- **states:** UT
- **sample (UT):** "A physician assistant, while practicing as a physician assistant: (a) shall wear an identification badge showing the physician assistant's license classification as a physician assistant; (b) shall identify themselves to a patient as a physician assistant; and (c) may not identify themselves to any person...other than as a physician assistant or PA."

## volunteer and charitable practice rules

### `volunteer_practice_controlled_substance_restriction` — bool
- **what:** Whether PAs providing uncompensated volunteer health services are prohibited from prescribing controlled substances to patients.
- **states:** UT
- **sample (UT):** "a physician assistant who is providing volunteer health services under this section may not issue a prescription to a patient for a controlled substance."

## practicing across state lines

### `interstate_compact_participation` — bool
- **what:** Whether the state participates in the PA Licensure Compact, allowing qualifying licensees to practice in other member states via a compact privilege.
- **states:** UT
- **sample (UT):** ""Compact Privilege" means the authorization granted by a Remote State to allow a Licensee from another Participating State to practice as a PA to provide Medical Services"

### `compact_privilege_nccpa_certification_required` — bool
- **what:** Whether holding current NCCPA certification is a prerequisite for exercising a compact privilege to practice in another participating state.
- **states:** UT
- **sample (UT):** "To exercise the Compact Privilege, a Licensee must:...Hold current NCCPA certification."

## mandatory training topics for license renewal

### `suicide_prevention_training_required_for_renewal` — bool
- **what:** Whether completion of a suicide prevention training or video is explicitly required as part of each license renewal cycle.
- **states:** UT
- **sample (UT):** "Prior to license renewal, each licensee shall, during each two-year licensure cycle...view a suicide prevention video described in Section 58-1-601 and submit proof in the form required by the division"

## background screening and fitness requirements

### `criminal_background_check_required` — bool
- **what:** Whether applicants for licensure must submit to a fingerprint-based criminal background check through state and federal databases.
- **states:** UT
- **sample (UT):** "An applicant for licensure under this chapter who requires a criminal background check shall: (a) submit fingerprint cards in a form acceptable to the division at the time the license application is filed; and (b) consent to a fingerprint background check conducted by the Bureau of Criminal Identification and the Federal Bureau of Investigation"
