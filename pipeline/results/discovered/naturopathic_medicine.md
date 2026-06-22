# Discovered fields — naturopathic_medicine

## license and registration type

### `credential_type` — enum[license, registration, certification]
- **what:** Whether the state issues a formal license, a registration, or another credential type to practitioners.
- **states:** PA
- **sample (PA):** "It shall be unlawful for an individual to use the title of "naturopathic doctor" or "doctor of naturopathic medicine" unless that person is registered as a naturopathic doctor with the board."

### `protected_titles` — list[str]
- **what:** Specific titles that are legally protected and may only be used by credentialed practitioners.
- **states:** PA
- **sample (PA):** "It shall be unlawful for an individual to use the title of "naturopathic doctor" or "doctor of naturopathic medicine" unless that person is registered as a naturopathic doctor with the board."

## education and training requirements

### `prerequisite_bachelor_degree_required` — bool
- **what:** Whether a bachelor's degree from an accredited institution is required before entering the naturopathic program.
- **states:** PA
- **sample (PA):** "Have a bachelor's degree from a regionally accredited or preaccredited college or university or the equivalent."

### `naturopathic_program_total_credit_hours` — int
- **what:** Minimum total credit hours required in the naturopathic medical program.
- **states:** PA
- **sample (PA):** "Complete a minimum of 4,100 total credit hours in basic and clinical sciences, naturopathic philosophy, naturopathic modalities and naturopathic medicine."

### `naturopathic_program_academic_instruction_hours` — int
- **what:** Minimum hours of academic (didactic) instruction required within the naturopathic program.
- **states:** PA
- **sample (PA):** "Of the total requisite hours, not less than 2,500 hours shall consist of academic instruction."

### `naturopathic_program_clinical_training_hours` — int
- **what:** Minimum hours of supervised clinical training required within the naturopathic program.
- **states:** PA
- **sample (PA):** "not less than 1,200 hours shall consist of supervised clinical training approved by a naturopathic medical school."

### `cpr_certification_required` — bool
- **what:** Whether current CPR certification is required as a condition of licensure or registration.
- **states:** PA
- **sample (PA):** "Be certified to administer cardiopulmonary resuscitation."

## examination and testing

### `exam_grandfather_clause` — bool
- **what:** Whether practitioners who graduated before a specified cutoff year may substitute a prior state exam for the current national exam requirement.
- **states:** PA
- **sample (PA):** "or has graduated prior to 1986 and has passed a state naturopathic licensing examination."

### `exam_grandfather_cutoff_year` — int
- **what:** The graduation year before which a practitioner may qualify under a grandfather clause and substitute a prior state exam.
- **states:** PA
- **sample (PA):** "or has graduated prior to 1986 and has passed a state naturopathic licensing examination."

## discipline and enforcement

### `disciplinary_grounds` — list[str]
- **what:** Enumerated statutory grounds on which the board may impose disciplinary or corrective action against a practitioner.
- **states:** PA
- **sample (PA):** "The board may impose disciplinary or corrective action on a naturopathic doctor for any of the following reasons: Failing to demonstrate the qualifications or standards for a registration contained in this act."

### `mandatory_fitness_examination_authority` — bool
- **what:** Whether the board has statutory authority to compel a practitioner to undergo a physical or mental fitness examination upon probable cause.
- **states:** PA
- **sample (PA):** "the board shall, upon probable cause, have authority to compel a practitioner to submit to a mental or physical examination by a physician or a psychologist approved by the board."

### `revocation_reinstatement_waiting_period_years` — int
- **what:** Minimum number of years a practitioner must wait after revocation before applying for reinstatement.
- **states:** PA
- **sample (PA):** "A person whose registration has been revoked may apply for reinstatement, after a period of at least five years, but must meet all of the qualifications under section 202."

### `felony_revocation_reinstatement_waiting_period_years` — int
- **what:** Minimum number of years a practitioner whose registration was revoked due to a felony drug conviction must wait before applying for reinstatement.
- **states:** PA
- **sample (PA):** "may apply for reinstatement after a period of at least 10 years has elapsed from the date of conviction."
