# Discovered fields — dental_assistant

## credential tiers and categories

### `assistant_license_type` — enum[unlicensed dental assistant, registered dental assistant, registered dental assistant in extended functions, orthodontic assistant permitholder, dental sedation assistant permitholder, certified dental assistant]
- **what:** The specific credential tier or category of dental assistant recognized by the state, ranging from unlicensed to advanced licensed classifications.
- **states:** CA, NY, UT
- **sample (CA):** "A registered dental assistant in extended functions licensed on or after January 1, 2010, is authorized to perform all duties and procedures that a registered dental assistant is authorized to perform as specified in and limited by Section 1752.4"

### `expanded_functions_authorized` — bool
- **what:** Whether the dental assistant credential tier is authorized to perform expanded functions beyond basic supportive procedures, such as placing direct restorations, taking final impressions, or administering botulinum toxin.
- **states:** CA, UT
- **sample (UT):** "The division shall create certifications for dental auxiliaries to perform, under the indirect supervision of a dentist, various expanded functions, including: delegated maxillofacial administration of botulinum toxin by a dental hygienist certified by the division; placement of direct restorations by a dental hygienist certified by the division or a dental assistant certified by the division; and the removal of coronal dental adhesive by a dental hygienist certified by the division or a dental assistant certified by the division."

### `specialty_permit_types` — list[str]
- **what:** The named specialty permits available to dental assistants beyond the basic registered dental assistant license, such as orthodontic assistant or dental sedation assistant permits.
- **states:** CA, NY, UT
- **sample (CA):** "The board may issue an orthodontic assistant permit to a person who files a completed application, pays the applicable fee, and provides evidence, satisfactory to the board, of the following eligibility requirements."

## supervision and oversight

### `supervision_level_required` — enum[direct supervision, indirect supervision, general supervision, direct personal supervision, no supervision required]
- **what:** The level of dentist supervision required for the dental assistant to perform authorized duties, which varies by task and credential tier.
- **states:** CA, NY, UT
- **sample (NY):** "Direct personal supervision, for purposes of this section, means supervision of dental procedures based on instructions given by a licensed dentist in the course of a procedure who remains in the dental office where the supportive services are being performed, personally diagnoses the condition to be treated, personally authorizes the procedures, and before dismissal of the patient, who remains the responsibility of the licensed dentist, evaluates the services performed by the registered dental assistant."

### `employer_training_responsibility` — bool
- **what:** Whether the employing dentist or dental practice bears statutory responsibility for ensuring the dental assistant completes required training courses and maintains required certifications.
- **states:** CA, NY, UT
- **sample (CA):** "The employer of a dental assistant shall be responsible for ensuring that the dental assistant has successfully completed a board-approved eight-hour course in infection control prior to performing any basic supportive dental procedures involving potential exposure to blood, saliva, or other potentially infectious materials."

### `supervising_dentist_concurrent_patient_limit` — int
- **what:** The maximum number of extended-functions dental assistants or dental hygienists a single supervising dentist may simultaneously supervise in clinical practice.
- **states:** CA, NY
- **sample (CA):** "A licensed dentist may simultaneously utilize in his or her practice no more than three registered dental assistants in extended functions or registered dental hygienists in extended functions licensed pursuant to Section 1753 or 1918."

## what they can do in the mouth

### `authorized_intraoral_procedures` — list[str]
- **what:** The specific intraoral clinical procedures a dental assistant is authorized to perform, which differ by credential tier and state.
- **states:** CA, NY, UT
- **sample (CA):** "A dental assistant may perform the following duties under the direct supervision and pursuant to the order, control, and full professional responsibility of a licensed dentist: Apply nonaerosol and noncaustic topical agents, including all forms of topical fluoride. Take intraoral impressions for all nonprosthodontic appliances. Take facebow transfers and bite registrations. Place and remove rubber dams or other isolation devices."

### `prohibited_procedures` — list[str]
- **what:** Procedures explicitly prohibited for dental assistants regardless of credential tier, typically including diagnosis, surgery, prescribing, and placing permanent restorations.
- **states:** CA, NY, UT
- **sample (CA):** "The duties of a dental assistant or a dental assistant holding a permit in orthodontic assisting or in dental sedation shall not include any of the following procedures unless specifically allowed by law: Diagnosis and comprehensive treatment planning. Placing, finishing, or removing permanent restorations. Surgery or cutting on hard and soft tissue including, but not limited to, the removal of teeth and the cutting and suturing of soft tissue. Prescribing medication."

### `radiography_authorized` — bool
- **what:** Whether the dental assistant is authorized to operate dental radiographic equipment, typically contingent on completing a board-approved radiation safety course.
- **states:** CA, NY, UT
- **sample (CA):** "Operate dental radiography equipment for the purpose of oral radiography if the dental assistant has complied with the requirements of paragraph (4) of subdivision (f) of Section 1750."

### `coronal_polishing_authorized` — bool
- **what:** Whether the dental assistant credential tier is authorized to perform coronal polishing, typically requiring a separate board-approved course.
- **states:** CA, NY, UT
- **sample (CA):** "To perform coronal polishing prior to licensure as a registered dental assistant, an unlicensed dental assistant shall complete a board-approved coronal polishing course and obtain a certificate of completion."

### `pit_fissure_sealant_authorized` — bool
- **what:** Whether the dental assistant credential tier is authorized to apply pit and fissure sealants, typically restricted to registered or extended-functions levels.
- **states:** CA, NY, UT
- **sample (CA):** "The placement of pit and fissure sealants may only be performed by a registered dental assistant, registered dental assistant in extended functions, registered dental hygienist, or registered dental hygienist in alternative practice."

### `interim_therapeutic_restoration_authorized` — bool
- **what:** Whether the dental assistant credential tier is authorized to place interim therapeutic restorations (provisional restorations using hand instrumentation only, without rotary instruments).
- **states:** CA, UT
- **sample (CA):** "Place protective restorations, which for this purpose are identified as interim therapeutic restorations, and defined as a direct provisional restoration placed to stabilize the tooth until a licensed dentist diagnoses the need for further definitive treatment. An interim therapeutic restoration consists of the removal of soft material from the tooth using only hand instrumentation, without the use of rotary instrumentation, and subsequent placement of an adhesive restorative material."

### `orthodontic_procedures_authorized` — list[str]
- **what:** The specific orthodontic chairside procedures a dental assistant or permitholder is authorized to perform, such as placing/removing separators, ligating archwires, and bonding brackets.
- **states:** CA, NY, UT
- **sample (NY):** "Prepare teeth for bonding, and select, preposition, and cure orthodontic brackets after their position has been approved by the supervising licensed dentist. Remove only orthodontic brackets and attachments with removal of the bonding material by the supervising licensed dentist. Size, fit, and cement orthodontic bands. Remove orthodontic bands and remove excess cement from supragingival surfaces of teeth with a hand instrument. Place and ligate archwires."

## sedation and anesthesia support

### `sedation_monitoring_authorized` — bool
- **what:** Whether the dental assistant credential tier is authorized to monitor patients undergoing sedation or anesthesia using noninvasive instrumentation.
- **states:** CA, NY, UT
- **sample (CA):** "Monitor patients undergoing moderate sedation, deep sedation, or general anesthesia utilizing data from noninvasive instrumentation such as pulse oximeters, electrocardiograms, capnography, blood pressure, pulse, and respiration rate monitoring devices. Evaluation of the condition of a sedated patient shall remain the responsibility of the supervising dentist or the licensed health care professional authorized to administer moderate sedation, deep sedation, or general anesthesia."

### `iv_drug_administration_authorized` — bool
- **what:** Whether the dental assistant is authorized to add drugs or fluids to intravenous lines under direct dentist supervision.
- **states:** CA, NY
- **sample (CA):** "Add drugs, medications, and fluids to intravenous lines using a syringe, provided that a supervising licensed dentist is present at the patient's chairside, limited to determining patency of intravenous line, selection of injection port, syringe insertion into injection port, occlusion of intravenous line and blood aspiration, line release, and injection of drugs for appropriate time interval. The exception to this duty is that the initial dose of a drug or medication shall be administered by the supervising licensed dentist."

## required training courses

### `radiation_safety_course_required` — bool
- **what:** Whether completion of a board-approved radiation safety course is required before the dental assistant may perform radiographic procedures.
- **states:** CA, NY, UT
- **sample (CA):** "To perform radiographic procedures, a dental assistant shall complete a board-approved course in radiation safety. The original or a copy of the current, valid certificate issued by a board-approved radiation safety course provider shall be publicly displayed at the treatment facility where the dental assistant performs dental services."

### `infection_control_course_required` — bool
- **what:** Whether completion of a board-approved infection control course is a prerequisite for performing clinical duties as a dental assistant.
- **states:** CA, NY, UT
- **sample (CA):** "The employer of a dental assistant shall be responsible for ensuring that the dental assistant has successfully completed a board-approved eight-hour course in infection control prior to performing any basic supportive dental procedures involving potential exposure to blood, saliva, or other potentially infectious materials."

### `dental_practice_act_course_required` — bool
- **what:** Whether completion of a course covering the state Dental Practice Act or dental law is required for dental assistant employment or licensure.
- **states:** CA, NY
- **sample (CA):** "A board-approved two-hour course in the Dental Practice Act."

### `basic_life_support_required` — bool
- **what:** Whether current certification in basic life support (CPR) is required for dental assistants to perform patient-care duties.
- **states:** CA, NY, UT
- **sample (CA):** "Current certification in basic life support issued by the American Red Cross, the American Heart Association, the American Safety and Health Institute, the American Dental Association's Continuing Education Recognition Program, or the Academy of General Dentistry's Program Approval for Continuing Education."

## pathways to licensure

### `work_experience_pathway_available` — bool
- **what:** Whether a dental assistant may qualify for a registered dental assistant license through documented on-the-job work experience rather than or in addition to formal schooling.
- **states:** CA, NY, UT
- **sample (CA):** "For individuals applying on or after January 1, 2010, evidence of completion of satisfactory work experience of at least 15 months as a dental assistant in California or another state and satisfactory performance on the Registered Dental Assistant Combined Written and Law and Ethics Examination administered by the board."

### `preceptorship_pathway_available` — bool
- **what:** Whether a dental assistant may qualify for licensure through a formal preceptorship program under a supervising dentist, combining supervised on-the-job training with required coursework.
- **states:** CA, NY
- **sample (CA):** "Completion of a preceptorship in dental assisting that includes all the following: At least 500 hours of clinical chairside work experience documented on a form furnished by the board, involving allowable duties described in Section 1750.1, directly supervised, evaluated, and documented by a preceptor."

### `minimum_work_experience_hours` — int
- **what:** The minimum number of hours of verifiable work experience as a dental assistant required to qualify for a registered dental assistant license via the experience pathway.
- **states:** CA, NY
- **sample (CA):** "Completion of satisfactory work experience performing the duties of a dental assistant, as defined in Section 1750.1, which includes at least 15 months and a minimum of 1,280 hours before the submission of the application."

## practice setting and facility rules

### `license_display_required` — bool
- **what:** Whether the dental assistant is required to publicly display their current license or permit certificate at the treatment facility where they perform services.
- **states:** CA, NY
- **sample (CA):** "The original or a copy of the current, valid permit issued by the board shall be publicly displayed at the treatment facility where the permitholder performs dental services."

### `teledentistry_scope_limitations` — str
- **what:** Specific restrictions on what dental assistants or dental auxiliaries may or may not do when services are delivered via teledentistry, including which supervision levels apply remotely.
- **states:** CA, UT
- **sample (UT):** "A dental hygienist, other unlicensed individual supervised by a dentist, or any other provider may not carry out any duties through teledentistry that require direct or indirect supervision of a dentist."

### `public_health_setting_practice_allowed` — bool
- **what:** Whether dental assistants or dental hygienists are authorized to provide services in defined public health settings such as schools, nursing homes, or mobile dental programs, potentially under reduced supervision requirements.
- **states:** CA, NY, UT
- **sample (UT):** "Notwithstanding any other provision of this chapter, without general supervision and without a collaborative practice agreement with a dentist if: the dental hygienist engages in the practice of dental hygiene in a public health setting."
