# Discovered fields — osteopathic_medicine

## types of licenses and permits issued

### `license_types_available` — list[str]
- **what:** The distinct categories of licenses or permits the board may issue to osteopathic physicians.
- **states:** PA
- **sample (PA):** "The board may grant the following licenses: (1) Unrestricted license... (2) Temporary graduate license... (3) Short-term camp physician license."

### `temporary_graduate_license_duration_months` — int
- **what:** Duration in months of a temporary graduate license issued to new osteopathic graduates for supervised training.
- **states:** PA
- **sample (PA):** "A temporary graduate license shall be valid for 12 months thereafter and shall be recognized only as conferring upon the licensee the right to participate in approved graduate osteopathic or medical training within the complex of the hospital to which he is assigned."

### `short_term_license_available` — bool
- **what:** Whether the board may issue a short-term license (e.g., for camp physicians) of limited duration.
- **states:** PA
- **sample (PA):** "A short-term license valid for a period not to exceed three months may be granted by the board to osteopathic physicians licensed and in good standing in other states or Canada who intend to practice osteopathic medicine as osteopathic physicians in camps in the Commonwealth."

### `visiting_team_physician_exemption` — bool
- **what:** Whether out-of-state physicians traveling with sports teams or national governing bodies are exempt from licensure requirements.
- **states:** PA
- **sample (PA):** "A physician who is licensed in good standing to practice in another state or country shall be exempt from the licensure requirements of this act while practicing in this Commonwealth if either of the following apply: The physician has a written or oral agreement with a sports team to provide care to the team members and coaching staff traveling with the team for a specific sporting event."

## character and fitness requirements

### `drug_addiction_bar` — bool
- **what:** Whether addiction to habit-forming drugs is an explicit disqualifying factor for licensure.
- **states:** PA
- **sample (PA):** "A graduate of an osteopathic medical college in the United States who seeks licensure by the board shall furnish the board with evidence, prior to any examination, that he is of good moral character, is not addicted to habit-forming drugs, and has completed the educational requirements prescribed by the board."

### `felony_drug_conviction_waiting_period_years` — int
- **what:** Minimum number of years that must elapse after a felony controlled-substance conviction before an applicant may be considered for licensure.
- **states:** PA
- **sample (PA):** "An applicant who has been convicted of a felonious act prohibited by... 'The Controlled Substance, Drug, Device and Cosmetic Act'... shall not be licensed unless: (1) at least ten years have elapsed from the date of conviction."

### `multi_state_license_reporting_required` — bool
- **what:** Whether licensees holding licenses in other states must report that fact and any out-of-state disciplinary actions to the board.
- **states:** PA
- **sample (PA):** "Any licensed osteopathic physician of this Commonwealth who is also licensed to practice osteopathic medicine or surgery in any other state, territory or country... shall report this information to the board on the biennial registration application. Any disciplinary action taken in other states shall be reported to the board on the biennial registration application or within 90 days of final disposition."

## discipline, impairment, and reinstatement

### `impaired_professional_program_available` — bool
- **what:** Whether the board operates a formal impaired-professional program allowing deferred discipline for licensees in approved treatment.
- **states:** PA
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the professional is progressing satisfactorily in an approved treatment program."

### `mandatory_impairment_reporting_required` — bool
- **what:** Whether hospitals, health care facilities, peers, or colleagues are legally required to report a licensee's active addictive disease, diversion, or incompetence to the board.
- **states:** PA
- **sample (PA):** "Any hospital or health care facility, peer or colleague who has substantial evidence that a professional has an active addictive disease for which the professional is not receiving treatment, is diverting a controlled substance or is mentally or physically incompetent to carry out the duties of his or her license shall make or cause to be made a report to the board."

### `license_revocation_reinstatement_waiting_period_years` — int
- **what:** Minimum number of years after revocation before a licensee may apply for reinstatement.
- **states:** PA
- **sample (PA):** "Any person whose license, certificate or registration has been revoked may apply for reinstatement after a period of at least five years, but must meet all of the licensing qualifications of this act for the license applied for."

### `automatic_suspension_triggers` — list[str]
- **what:** Specific events that automatically suspend a license without a prior hearing.
- **states:** PA
- **sample (PA):** "A license or certificate issued under this act shall automatically be suspended upon the commitment to an institution of a licensee because of mental incompetency from any cause... conviction of a felony under... 'The Controlled Substance, Drug, Device and Cosmetic Act.'"

## supervision and delegation rules

### `physician_assistant_supervision_ratio_max` — int
- **what:** Maximum number of physician assistants a single supervising physician may supervise at one time.
- **states:** PA
- **sample (PA):** "There shall be no more than six physician assistants for whom a physician has responsibility or supervises pursuant to a written agreement at any time."

### `physician_assistant_written_agreement_required` — bool
- **what:** Whether a formal written agreement between the supervising physician and physician assistant must be filed with the board.
- **states:** PA
- **sample (PA):** "The primary supervising physician shall file, or cause to be filed, with the board a written agreement that identifies the manner in which the physician assistant will assist the primary supervising physician."

### `physician_assistant_countersignature_requirement` — str
- **what:** Rules governing when and how often a supervising physician must countersign patient records completed by a physician assistant.
- **states:** PA
- **sample (PA):** "The approved physician shall countersign 100% of the patient records completed by the physician assistant within a reasonable time, which shall not exceed 10 days, during each of the following time periods: (i) The first 12 months of the physician assistant's practice post graduation... (ii) The first 12 months of the physician assistant's practice in a new specialty."

### `physician_assistant_prescribing_authority` — str
- **what:** Description of a physician assistant's authority to prescribe or dispense drugs, including any restrictions.
- **states:** PA
- **sample (PA):** "Nothing in this act shall be construed to permit a physician assistant to independently prescribe or dispense drugs. The board and State Board of Pharmacy will jointly develop regulations to permit a physician assistant to prescribe and dispense drugs at the direction of a licensed physician."

## professional liability insurance requirements

### `physician_assistant_liability_insurance_minimum_per_occurrence` — int
- **what:** Minimum professional liability insurance coverage amount (in dollars per occurrence or claims made) required for physician assistants.
- **states:** PA
- **sample (PA):** "A licensed physician assistant in this Commonwealth shall maintain a level of professional liability insurance coverage in the minimum amount of $1,000,000 per occurrence or claims made."

### `perfusionist_liability_insurance_minimum_per_occurrence` — int
- **what:** Minimum professional liability insurance coverage amount (in dollars per occurrence or claims made) required for licensed perfusionists.
- **states:** PA
- **sample (PA):** "A licensed perfusionist practicing in this Commonwealth shall maintain a level of professional liability insurance coverage in the minimum amount of $1,000,000 per occurrence or claims made."

### `genetic_counselor_liability_insurance_minimum_per_occurrence` — int
- **what:** Minimum professional liability insurance coverage amount (in dollars per occurrence or claims made) required for licensed genetic counselors.
- **states:** PA
- **sample (PA):** "A licensee under this section, practicing in this Commonwealth, shall maintain a level of professional liability insurance coverage in the minimum amount of $1,000,000 per occurrence or claims made."

## what allied health staff may do under osteopathic physician oversight

### `radiologic_procedures_auxiliary_personnel_rules` — str
- **what:** Rules governing when and under what supervision auxiliary personnel may perform radiologic procedures on an osteopathic physician's premises.
- **states:** PA
- **sample (PA):** "No auxiliary personnel shall perform radiologic procedures on the premises of an osteopathic physician unless such person is under the direct supervision of an osteopathic physician and unless such person has passed an examination approved by the board."

### `athletic_trainer_direction_model` — str
- **what:** Description of the supervision or direction model under which licensed athletic trainers may provide services, including whether physical presence of the supervising physician is required.
- **states:** PA
- **sample (PA):** "Supervision over the actions of a licensed athletic trainer via referral by prescription to treat conditions for a physically active person from a licensed physician, dentist or podiatrist or written protocol approved by a supervising physician, dentist or podiatrist, except that the physical presence of the supervising physician, dentist or podiatrist is not required if the supervising physician, dentist or podiatrist is readily available for consultation by direct communication, radio, telephone, facsimile, telecommunications or via other electronic means."

### `board_regulated_allied_professions` — list[str]
- **what:** Allied health professions whose licensure or certification is regulated by the same osteopathic medicine board.
- **states:** PA
- **sample (PA):** "'Board-regulated practitioner.' An osteopathic physician, physician assistant, respiratory therapist or licensed athletic trainer or an applicant for a license or certificate issued by the board."

## education and training institution standards

### `osteopathic_college_accrediting_body` — str
- **what:** The named accrediting body whose approval qualifies an osteopathic medical college for purposes of graduate eligibility.
- **states:** PA
- **sample (PA):** "'Osteopathic medical college.' An institution of higher learning accredited by the American Osteopathic Association, its successors and assigns, as an agency to provide courses in the arts and sciences of medicine and related subjects and empowered to grant academic degrees in osteopathic medicine and surgery."

### `approved_hospital_required_for_graduate_training` — bool
- **what:** Whether supervised graduate osteopathic medical training must occur at a hospital specifically approved by the board.
- **states:** PA
- **sample (PA):** "'Approved hospital.' A hospital which has been approved by the board for providing supervised graduate osteopathic medical training."

### `continuing_education_excluded_topics` — list[str]
- **what:** Topics explicitly excluded from counting toward continuing education credit.
- **states:** PA
- **sample (PA):** "No credit shall be given for any course in office management or practice building."
