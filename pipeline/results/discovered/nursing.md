# Discovered fields — nursing

## types of nursing licenses and what each one covers

### `license_tiers` — list[str]
- **what:** The distinct license or certification tiers recognized in the state, each with its own scope and requirements.
- **states:** AK, AL, AR, AZ, CA
- **sample (AR):** "In order to safeguard life and health, a person practicing or offering to practice nursing for compensation shall be required to submit evidence that he or she is qualified to so practice and shall be licensed as provided in this chapter: (1) Professional nursing; (2) Advanced practice registered nursing; (3) Registered practitioner nursing; (4) Practical nursing; or (5) Psychiatric technician nursing."

### `aprn_role_categories` — list[str]
- **what:** The recognized advanced practice registered nurse role categories, each with distinct scope and certification requirements.
- **states:** AK, AL, AR, AZ, CA
- **sample (AL):** "There shall be four categories of advanced practice nurses: Certified registered nurse practitioners (CRNP), certified nurse midwives (CNM), certified registered nurse anesthetists (CRNA), and clinical nurse specialists (CNS)."

## supervision and who a nurse must work under

### `lpn_supervision_requirements` — list[str]
- **what:** The categories of licensed professionals under whose supervision a practical or vocational nurse must work.
- **states:** AK, AL, AR, AZ, CA
- **sample (AK):** "A practical nurse shall work under the supervision of a licensed registered or advanced practice registered nurse, a licensed physician, a licensed physician assistant, or a licensed dentist."

### `collaborative_practice_agreement_required` — bool
- **what:** Whether certain advanced practice nurses (typically NPs and CNMs) must have a written collaborative practice agreement with a physician to practice or prescribe.
- **states:** AL, AR, CA
- **sample (AL):** "No person may practice as a certified registered nurse practitioner or a certified nurse midwife in this state unless that person possesses a certificate of qualification issued by the Board of Nursing and practices under written protocols approved by the State Board of Medical Examiners and the Board of Nursing and signed by a qualified collaborating physician."

### `full_independent_practice_available` — bool
- **what:** Whether the state provides a pathway for certain APRNs to practice fully independently without a physician collaboration or supervision requirement.
- **states:** AR, AZ, CA
- **sample (AR):** "As used in this section, 'full independent practice authority' means the ability of a certified nurse practitioner or a clinical nurse specialist to practice with prescriptive authority without a collaborative practice agreement."

### `full_independent_practice_experience_hours_required` — int
- **what:** Number of supervised or collaborative practice hours required before an APRN may qualify for full independent practice authority.
- **states:** AR, CA
- **sample (AR):** "Proof of successful completion of six thousand two hundred forty (6,240) hours of practice: (i) Under a board-required agreement with a physician; or (ii) From another state, territory, or foreign country that authorizes a certified nurse practitioner or a clinical nurse specialist to practice with prescriptive authority."

## prescribing and drug authority details

### `prescriptive_authority_certificate_required` — bool
- **what:** Whether APRNs must obtain a separate board-issued certificate or number to prescribe or furnish drugs, beyond the basic APRN license.
- **states:** AR, AZ, CA
- **sample (CA):** "The furnishing or ordering of drugs or devices by a nurse practitioner is conditional on issuance by the board of a number to the nurse applicant who has successfully completed the requirements of subdivision (g) of Section 2836.1."

### `controlled_substance_schedule_authority` — list[str]
- **what:** The DEA controlled substance schedules that APRNs are authorized to prescribe, which may differ by role or state.
- **states:** AK, AL, AR, AZ, CA
- **sample (AR):** "An advanced practice registered nurse's prescriptive authority shall extend only to drugs listed in Schedules III - V and, if expressly authorized by the collaborative practice agreement, also to those hydrocodone combination products reclassified from Schedule III to Schedule II."

### `opioid_prescribing_limits` — str
- **what:** Statutory limits on opioid prescriptions issued by APRNs, including maximum day-supply and documentation requirements.
- **states:** AK, AR
- **sample (AK):** "An advanced practice registered nurse may not issue (1) an initial prescription for an opioid that exceeds a seven-day supply to an adult patient for outpatient use."

### `dea_registration_required` — bool
- **what:** Whether APRNs authorized to prescribe controlled substances must register with the federal DEA.
- **states:** AK, AR, AZ, CA
- **sample (CA):** "Every certified nurse-midwife who is authorized pursuant to this section to furnish or issue a drug order for a controlled substance shall register with the United States Drug Enforcement Administration."

### `controlled_substance_database_registration_required` — bool
- **what:** Whether APRNs with DEA numbers must register with the state's controlled substance prescription monitoring database.
- **states:** AK, CA
- **sample (AK):** "Require that a licensed advanced practice registered nurse who has a federal Drug Enforcement Administration registration number register with the controlled substance prescription database under AS 17.30.200(n)."

## nurse aide and assistive personnel oversight

### `nurse_aide_registry_maintained` — bool
- **what:** Whether the state board maintains a registry of certified nurse aides, including disciplinary findings.
- **states:** AK, AZ, CA
- **sample (AK):** "The board shall maintain a registry of certified nurse aides. At a minimum, this registry must include the information required under federal regulations that are applicable to nurse aides found to have committed abuse, neglect, or misappropriation of property."

### `medication_assistant_certification_available` — bool
- **what:** Whether the state has a separate certification category for medication assistants or medication assistive persons who may administer certain medications under nurse supervision.
- **states:** AR, AZ, CA
- **sample (AR):** "A medication assistive person means a person who is certified by the board to administer certain nonprescription and legend drugs in designated facilities."

### `delegation_to_unlicensed_personnel_authorized` — bool
- **what:** Whether licensed nurses are explicitly authorized by statute to delegate nursing tasks to unlicensed assistive personnel under defined conditions.
- **states:** AK, AL, AR, AZ, CA
- **sample (AK):** "A registered, advanced practice registered, or practical nurse licensed under this chapter may delegate nursing duties to other persons, including unlicensed assistive personnel, under regulations adopted by the board."

## reporting obligations and whistleblower protections

### `employer_mandatory_reporting_required` — bool
- **what:** Whether employers of nurses are legally required to report to the board when a nurse is discharged, suspended, or resigns under circumstances related to grounds for discipline.
- **states:** AK, CA
- **sample (AK):** "An employer of a nurse licensed under this chapter... that discharges or suspends a nurse or nurse aide or conditions or restricts the practice of a nurse or nurse aide shall, within seven working days after the action, report to the board the name and address of the person and the reason for the action."

### `whistleblower_protection_for_delegation_refusal` — bool
- **what:** Whether the state provides explicit statutory protection for nurses who refuse to perform improperly delegated tasks.
- **states:** AK, AL
- **sample (AK):** "An employer may not discharge, threaten, or otherwise discriminate against a nurse employed by the employer regarding the nurse's compensation, terms, conditions, location, or privileges of employment for the nurse's refusal to perform a task involving nursing care delegated to the nurse by the nurse's superior if the nurse alleges that the task was improperly delegated."

## multistate practice and interstate compacts

### `nurse_licensure_compact_member` — bool
- **what:** Whether the state has enacted the Enhanced Nurse Licensure Compact (eNLC), allowing multistate licensure privileges.
- **states:** AL, AR, AZ
- **sample (AL):** "A multistate license to practice registered or licensed practical nursing issued by a home state to a resident in that state shall be recognized by each party state as authorizing a nurse to practice as a registered nurse or as a licensed practical nurse, under a multistate licensure privilege, in each party state."

### `multistate_license_option_available` — bool
- **what:** Whether applicants may choose between a single-state license and a multistate license when applying for licensure.
- **states:** AL, AR, AZ
- **sample (AL):** "An applicant for a license to practice professional nursing in Alabama may apply for either a single state license or a multistate license."

## impaired nurse programs and rehabilitation

### `impaired_nurse_alternative_program_available` — bool
- **what:** Whether the state has a voluntary non-disciplinary alternative or diversion program for nurses impaired by substance use or mental health conditions.
- **states:** AL, AR, AZ, CA
- **sample (AL):** "The board shall establish a voluntary Disciplinary Alternative Program to promote early identification, intervention, treatment, and rehabilitation of any licensed nurse whose competence is found to be impaired or compromised because of the use or abuse of drugs, alcohol, controlled substances, chemicals, or other substances."

## special clinical authorities granted to nurses

### `rn_death_pronouncement_authorized` — bool
- **what:** Whether registered nurses are explicitly authorized by statute to make a determination and pronouncement of death under specified conditions.
- **states:** AK, CA
- **sample (AK):** "A registered nurse licensed under this chapter may make a determination and pronouncement of death of a person under the following circumstances: an attending physician, an attending advanced practice registered nurse, or an attending physician assistant has documented in the person's medical or clinical record that the person's death is anticipated due to illness, infirmity, or disease."

### `public_health_nurse_certification_available` — bool
- **what:** Whether the state has a separate board-issued public health nurse certification with title protection.
- **states:** CA
- **sample (CA):** "No individual shall hold himself or herself out as a public health nurse or use a title which includes the term 'public health nurse' unless that individual is in possession of a valid California public health nurse certificate issued pursuant to this article."

### `telehealth_prescribing_rules` — str
- **what:** Statutory rules governing when an APRN may prescribe or treat without a prior in-person physical examination, including telehealth or internet-based restrictions.
- **states:** AK, CA
- **sample (AK):** "The board may not impose disciplinary sanctions on an advanced practice registered nurse for rendering a diagnosis, providing treatment, or prescribing, dispensing, or administering a prescription drug that is not a controlled substance to a person without conducting a physical examination if the advanced practice registered nurse or another licensed health care provider in the medical practice is available to provide follow-up care."

## extra credentials and tiered scope for advanced practice nurses

### `nurse_practitioner_transition_to_practice_hours` — int
- **what:** Number of supervised or collaborative practice hours a nurse practitioner must complete before qualifying for independent or expanded practice authority.
- **states:** AR, CA
- **sample (CA):** "Has completed a transition to practice in California of a minimum of three full-time equivalent years of practice or 4600 hours."

### `crna_physician_supervision_model` — enum[direction and presence required, direction without required presence, consultation model, coordination model]
- **what:** The statutory model governing the relationship between a CRNA and a physician during anesthesia administration.
- **states:** AL, AR, AZ, CA
- **sample (AZ):** "A certified registered nurse anesthetist may administer anesthetics under the direction of and in the presence of a physician or surgeon in connection with the preoperative, intraoperative or postoperative care of a patient."

### `cnm_out_of_hospital_birth_authorized` — bool
- **what:** Whether certified nurse midwives are explicitly authorized to attend births in out-of-hospital settings.
- **states:** AR, AZ, CA
- **sample (CA):** "The certificate to practice nurse-midwifery authorizes the holder to attend pregnancy and childbirth in an out-of-hospital setting if consistent with subdivisions (a), (b), and (c)."

### `aprn_formulary_or_protocol_required` — bool
- **what:** Whether APRNs who prescribe must do so pursuant to a board-approved formulary or written protocol specifying permissible drugs.
- **states:** AL, AR, CA
- **sample (AL):** "The drug shall be on the formulary recommended by the joint committee and adopted by the State Board of Medical Examiners and the Board of Nursing."

## nursing school and education program standards

### `nursing_education_program_clinical_hours_minimum` — int
- **what:** Minimum number of direct patient care clinical hours required in an approved prelicensure nursing education program.
- **states:** AZ, CA
- **sample (CA):** "An approved school of nursing or nursing program shall meet a minimum of 500 direct patient care clinical hours in a board-approved clinical setting."

### `implicit_bias_training_required_in_curriculum` — bool
- **what:** Whether approved nursing education programs are required to include implicit bias training as part of graduation requirements.
- **states:** CA
- **sample (CA):** "Graduation requirements for an approved school of nursing, or an approved nursing program, shall include one hour of direct participation in an implicit bias training."

### `military_education_credit_required` — bool
- **what:** Whether approved nursing schools are required to grant credit toward licensure for military medical education and experience.
- **states:** AZ, CA
- **sample (CA):** "The board shall deny the application for approval made by, and shall revoke the approval given to, any school of nursing that does not give student applicants credit in the field of nursing for military education and experience by the use of challenge examinations or other methods of evaluation."
