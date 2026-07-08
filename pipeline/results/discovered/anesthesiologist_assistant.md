# Discovered fields — anesthesiologist_assistant

## supervision and delegation

### `supervising_anesthesiologist_ratio` — int
- **what:** Maximum number of anesthesiologist assistants a single supervising anesthesiologist may concurrently supervise.
- **states:** AL, CO, FL, GA, IN, MO, NC, NM, … (+2)
- **sample (MO):** "A supervising anesthesiologist shall be allowed to supervise up to four anesthesiologist assistants consistent with federal rules or regulations for reimbursement for anesthesia services."

### `supervising_anesthesiologist_physical_presence_required` — bool
- **what:** Whether the supervising anesthesiologist must be physically present (on-site or in the same facility) while the anesthesiologist assistant is providing care.
- **states:** AL, CO, FL, GA, IN, MO, NC, NM, … (+2)
- **sample (OH):** "An anesthesiologist assistant shall practice only under the direct supervision and in the immediate presence of a physician who is actively and directly engaged in the clinical practice of medicine as an anesthesiologist."

### `written_practice_protocol_required` — bool
- **what:** Whether a written practice protocol or supervisory agreement between the supervising anesthesiologist and the anesthesiologist assistant is required before practice.
- **states:** FL, GA, IN, MO, NC, NM, NV, OH
- **sample (OH):** "Each anesthesiologist who agrees to act as the supervising anesthesiologist of an anesthesiologist assistant shall adopt a written practice protocol that is consistent with section 4760.09 of the Revised Code and delineates the services that the anesthesiologist assistant is authorized to provide and the manner in which the anesthesiologist will supervise the anesthesiologist assistant."

### `supervising_anesthesiologist_qualifications` — str
- **what:** Required qualifications for a physician to serve as a supervising anesthesiologist for an anesthesiologist assistant.
- **states:** AL, CO, FL, GA, MO, NC, NM, NV, … (+1)
- **sample (NV):** "'Supervising anesthesiologist' means an active physician who is licensed and in good standing in this State, is certified or is eligible to be certified as an anesthesiologist by the American Board of Anesthesiology or its successor organization and supervises one or more anesthesiologist assistants."

### `supervising_anesthesiologist_liability` — bool
- **what:** Whether the supervising anesthesiologist bears legal responsibility and liability for the acts and omissions of the anesthesiologist assistant.
- **states:** CO, FL, GA, MO, NC, NM, NV, OH
- **sample (NM):** "The anesthesiologist actually supervising the licensed anesthesiologist assistant at the time is individually responsible and liable for the acts and omissions that the anesthesiologist assistant performs in the scope of his duties."

### `enhanced_supervision_new_practitioners` — bool
- **what:** Whether enhanced or heightened supervision is required during the initial period of an anesthesiologist assistant's practice.
- **states:** MO, NM, OH
- **sample (OH):** "The board's rules shall include requirements for enhanced supervision of an anesthesiologist assistant during the first four years of practice."

## practice setting and facility rules

### `practice_setting_restrictions` — list[str]
- **what:** Types of facilities or settings in which an anesthesiologist assistant is authorized to practice.
- **states:** FL, GA, NM, NV, OH
- **sample (OH):** "An anesthesiologist assistant shall not practice in any location other than a hospital or ambulatory surgical facility."

### `student_trainee_exemption` — bool
- **what:** Whether students enrolled in an accredited anesthesiologist assistant training program are exempt from licensure requirements while in training.
- **states:** CO, FL, GA, MO, NC, NM, NV, OH
- **sample (NM):** "An anesthesiologist assistant student enrolled in an anesthesiologist assistant educational program accredited by the commission on accreditation of allied health education programs or its successor is exempt from licensure while functioning as an anesthesiologist assistant student."

### `patient_disclosure_required` — bool
- **what:** Whether the anesthesiologist assistant must identify themselves to patients as an anesthesiologist assistant.
- **states:** CO, FL, GA, MO, NC, NV, OH
- **sample (FL):** "An anesthesiologist assistant must clearly convey to the patient that he or she is an anesthesiologist assistant."

### `hospital_or_facility_credentialing_authority` — bool
- **what:** Whether hospitals or ambulatory surgical facilities have independent authority to grant, limit, or deny privileges to anesthesiologist assistants beyond state licensure.
- **states:** CO, FL, MO, NC, OH
- **sample (CO):** "A person licensed to practice as an anesthesiologist assistant shall not perform any act that constitutes the practice of medicine within a hospital or ambulatory surgical center licensed pursuant to part 1 of article 3 of title 25 or required to obtain a certificate of compliance pursuant to section 25-1.5-103(1)(a)(II), unless the licensed anesthesiologist assistant obtains authorization from the governing board of the hospital or ambulatory surgical center."

## drugs and anesthesia

### `prescribing_authority` — bool
- **what:** Whether an anesthesiologist assistant is authorized to independently prescribe controlled substances or other drugs.
- **states:** FL, GA, MO, NC, NM, NV, OH
- **sample (NV):** "An anesthesiologist assistant shall not prescribe any controlled substance or any dangerous drug, as defined in NRS 454.201."

## what they can do clinically

### `authorized_anesthesia_tasks` — list[str]
- **what:** Specific clinical tasks and procedures an anesthesiologist assistant is authorized to perform under supervision.
- **states:** AL, CO, FL, GA, MO, NC, NM, NV, … (+1)
- **sample (OH):** "Establish basic and advanced airway interventions, including intubation of the trachea and performing ventilatory support; Administer intermittent vasoactive drugs and start and adjust vasoactive infusions; Administer anesthetic drugs, adjuvant drugs, and accessory drugs; Assist the supervising anesthesiologist with the performance of epidural anesthetic procedures and spinal anesthetic procedures."

## credentials and certification

### `national_certification_body` — str
- **what:** The national organization whose certification is required for licensure as an anesthesiologist assistant.
- **states:** AL, CO, FL, GA, IN, MO, NC, NM, … (+2)
- **sample (NV):** "Has passed a certifying examination administered by the National Commission for Certification of Anesthesiologist Assistants, its successor organization or other nationally recognized organization for the certification of anesthesiologist assistants that has been reviewed and approved by the Board."

### `accredited_training_program_required` — bool
- **what:** Whether completion of a graduate-level or accredited anesthesiologist assistant training program is required for licensure.
- **states:** AL, CO, FL, GA, IN, MO, NC, NM, … (+2)
- **sample (CO):** "Successfully completed an education program for anesthesiologist assistants that conforms to standards delineated by the Commission on Accreditation of Allied Health Education Programs, or its successor organization, and approved by the board."

### `continuing_certification_required_for_renewal` — bool
- **what:** Whether maintaining active certification from the national certifying body is required to renew the anesthesiologist assistant license.
- **states:** AL, CO, FL, GA, IN, MO, NC, NM, … (+2)
- **sample (IN):** "In order to maintain a license under this article, an individual licensed under this article shall comply with all continuing certification requirements set by the National Commission for Certification of Anesthesiologist Assistants or a successor organization."
