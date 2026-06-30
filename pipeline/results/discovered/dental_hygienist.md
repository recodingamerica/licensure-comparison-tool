# Discovered fields — dental_hygienist

## supervision and delegation

### `supervision_level_definitions` — list[str]
- **what:** Statutory definitions of the distinct supervision tiers (direct, indirect, general, prescriptive, telehealth, etc.) that govern when and how a dentist must be present for dental hygiene services.
- **states:** AK, AL, CA, CO, FL, GA, IN, ME, … (+2)
- **sample (IN):** ""Direct supervision" means that a licensed dentist is physically present in the facility when patient care is provided by the dental hygienist. "Prescriptive supervision" means that a licensed dentist is not required to be physically present in the facility when patient care is provided by the dental hygienist if..."

### `unsupervised_or_independent_practice_authorized` — bool
- **what:** Whether the state authorizes dental hygienists to provide at least some services without any dentist supervision or authorization.
- **states:** AK, CA, CO, FL, GA, IN, ME, OH
- **sample (CO):** "Unsupervised dental hygiene may be performed by licensed dental hygienists without the supervision of a licensed dentist."

### `written_practice_agreement_required` — bool
- **what:** Whether a formal written agreement between the dental hygienist and a supervising or collaborating dentist is required to practice under reduced supervision.
- **states:** AK, CO, IN, ME, OH
- **sample (ME):** "A dental therapist may practice under the general supervision of a dentist through a written practice agreement signed by both parties."

### `max_hygienists_per_supervising_dentist` — int
- **what:** The maximum number of dental hygienists a single dentist may supervise simultaneously under clinical or reduced-supervision conditions.
- **states:** AK, CA, CO, FL, GA, OH
- **sample (OH):** "At no time shall more than four dental hygienists be practicing clinical hygiene under the supervision of the same dentist."

### `patient_referral_to_dentist_required_after_unsupervised_care` — bool
- **what:** Whether the statute requires a dental hygienist practicing without direct supervision to refer or schedule the patient for a subsequent dentist examination.
- **states:** AK, CA, CO, FL, GA, IN, ME, OH
- **sample (OH):** "Immediately following the completion of the dental hygiene services and subject to division (B) of this section, direct the patient to a dentist for a clinical evaluation and schedule or cause to be scheduled an appointment for the patient with a dentist."

## extra credentials and tiered scope

### `independent_or_alternative_practice_license_type` — enum[advanced_practice_permit, independent_practice_dental_hygienist, public_health_dental_hygienist, access_practice_agreement, collaborative_agreement, oral_health_access_supervision_permit, none]
- **what:** The specific credential or agreement type that authorizes a dental hygienist to practice with reduced or no dentist supervision beyond the standard license.
- **states:** AK, CA, CO, FL, GA, IN, ME, OH
- **sample (AK):** "A licensed dental hygienist holding an advanced practice permit may provide the services described in (a) of this section to a patient who is unable to access dental treatment because of age, infirmity, or disability..."

### `minimum_clinical_hours_for_expanded_practice` — int
- **what:** Minimum documented clinical practice hours required before a dental hygienist may obtain an expanded or independent practice credential.
- **states:** AK, CA, IN, ME, OH
- **sample (IN):** "The dental hygienist has at least two thousand (2,000) documented clinical hours of dental hygiene services during two (2) years of active practice under the direct supervision of a dentist."

### `dental_therapy_license_available` — bool
- **what:** Whether the state has created a dental therapist or dental therapy license that may be held by or built upon a dental hygienist license.
- **states:** AK, CO, ME
- **sample (ME):** ""Dental therapist" means a person who holds a valid license as a dental hygienist issued by the board and is authorized to practice dental therapy under this chapter."

### `cpr_bls_certification_required_for_renewal` — bool
- **what:** Whether current CPR or basic life support certification is an explicit statutory requirement for license renewal.
- **states:** AL, CA, FL, GA, IN, ME, OH
- **sample (GA):** "After 1988, as a prerequisite for license renewal, dental hygienists shall furnish satisfactory evidence of current certification in cardiopulmonary resuscitation, as may be defined by rule or regulation of the board."

### `continuing_education_hours_per_period` — int
- **what:** The minimum number of continuing education hours required per renewal period for dental hygienists.
- **states:** AK, AL, CA, CO, FL, GA, IN, ME, … (+2)
- **sample (OH):** "Every person licensed to practice as a dental hygienist and required to register with the state dental board shall certify to the board at the time of applying for a renewal of registration that in the two-year period preceding the registration period for which renewal is sought the registrant completed a minimum of twenty hours of continuing dental hygiene education."

## where and how services can be delivered

### `authorized_practice_settings` — list[str]
- **what:** Specific settings or facility types where dental hygienists are explicitly authorized to practice, including any settings that allow reduced supervision.
- **states:** AK, AL, CA, CO, FL, GA, IN, ME, … (+2)
- **sample (IN):** "A licensed dental hygienist may practice dental hygiene in Indiana in the following: A dental office, clinical setting, or health facility... A fixed charitable dental care clinic; public health setting; correctional institution..."

### `public_health_setting_definition` — str
- **what:** Statutory definition of 'public health setting' or equivalent term that triggers reduced-supervision practice authority for dental hygienists.
- **states:** AK, CA, CO, FL, GA, IN, ME, OH
- **sample (IN):** ""Public health setting" means a location, including a mobile health care vehicle, where the public is invited for health care, information, and services by a program sponsored or endorsed by a governmental entity or charitable organization."

### `teledentistry_authorized` — bool
- **what:** Whether the state explicitly authorizes dental hygienists to provide services through teledentistry or synchronous remote communication.
- **states:** CO, ME, OH
- **sample (ME):** "An individual licensed under this chapter may provide oral health care services and procedures authorized under this chapter or by rule using teledentistry."

## drugs and anesthesia

### `local_anesthesia_authority` — enum[permitted_with_certificate_or_permit, permitted_under_direct_supervision_only, permitted_under_general_supervision, not_authorized]
- **what:** The level of authority a dental hygienist has to administer local anesthesia, and any additional credential required.
- **states:** AK, AL, CA, CO, FL, GA, IN, ME, … (+2)
- **sample (NY):** "A dental hygienist shall not administer or monitor nitrous oxide analgesia or local infiltration anesthesia in the practice of dental hygiene without a dental hygiene restricted local infiltration anesthesia/nitrous oxide analgesia certificate and except under the personal supervision of a dentist."

### `nitrous_oxide_authority` — enum[permitted_with_certificate_or_permit, permitted_under_direct_supervision_only, permitted_under_general_supervision, not_authorized]
- **what:** The level of authority a dental hygienist has to administer or monitor nitrous oxide analgesia, and any additional credential required.
- **states:** AK, CA, CO, FL, GA, IN, ME, NY, … (+1)
- **sample (CA):** "A registered dental hygienist is authorized to perform the following procedures under direct supervision of a licensed dentist, after submitting to the dental hygiene board evidence of satisfactory completion of a course of instruction... (c) Administration of nitrous oxide and oxygen, whether administered alone or in combination with each other."

### `silver_diamine_fluoride_authority` — bool
- **what:** Whether dental hygienists are explicitly authorized to prescribe, apply, or administer silver diamine fluoride.
- **states:** AK, CA, CO, ME, OH
- **sample (OH):** "A licensed dentist may assign to a dental hygienist the application of silver diamine fluoride if the dentist has examined the patient and diagnosed the need for such treatment and the dental hygienist has completed a course approved in accordance with rules adopted under division (B) of section 4715.436 of the Revised Code."

### `prescriptive_authority_scope` — list[str]
- **what:** Specific drugs, agents, or categories of medications that dental hygienists are authorized to prescribe, dispense, or administer independently or under collaboration.
- **states:** AK, CA, CO, ME, OH
- **sample (CO):** "Prescribes, administers, and dispenses fluoride, fluoride varnish, silver diamine fluoride in accordance with subsection (1)(g)(IV) of this section, antimicrobial solutions for mouth rinsing, other nonsystemic antimicrobial agents, and related emergency drugs and reversal agents in collaboration with a licensed dentist."

## what they can treat and where on the body

### `interim_therapeutic_restoration_authorized` — bool
- **what:** Whether dental hygienists are explicitly authorized to place interim therapeutic restorations (provisional restorations placed without rotary instrumentation).
- **states:** CA, CO, IN, ME, OH
- **sample (CA):** "Place protective restorations, which for this purpose are identified as interim therapeutic restorations, and defined as a direct provisional restoration placed to stabilize the tooth until a licensed dentist diagnoses the need for further definitive treatment."

### `dental_hygiene_diagnosis_authorized` — bool
- **what:** Whether the state explicitly authorizes dental hygienists to perform a 'dental hygiene diagnosis' distinct from a full dental diagnosis.
- **states:** CA, CO, ME
- **sample (CO):** ""Dental hygiene diagnosis" means the identification of an existing oral health problem that a dental hygienist is qualified and licensed to treat within the scope of dental hygiene practice."

### `dental_hygiene_diagnosis_treatment_planning_scope` — list[str]
- **what:** Specific assessment, diagnosis, and treatment planning functions explicitly authorized for dental hygienists beyond basic prophylaxis.
- **states:** CA, CO, FL, GA, ME, NY, OH
- **sample (ME):** "Perform dental hygiene assessment, dental hygiene diagnosis and dental hygiene treatment planning and implementation in the identification, prevention and management of oral disease."

## practice setting and facility rules

### `malpractice_insurance_required_for_independent_practice` — bool
- **what:** Whether the state explicitly requires dental hygienists practicing under reduced or no supervision to maintain professional liability or malpractice insurance.
- **states:** AK, CA, FL, GA, IN, ME, OH
- **sample (IN):** "A dental hygienist who provides services under an access practice agreement shall maintain malpractice liability insurance."

### `mobile_dental_facility_regulated` — bool
- **what:** Whether the state has specific statutory provisions governing mobile dental facilities or portable dental operations where hygienists may practice.
- **states:** AL, CA, GA, ME, OH
- **sample (OH):** ""Mobile dental facility" means either of the following: A self-contained, intact facility in which dentistry or dental hygiene is practiced that may be transported from one location to another; A site used on a temporary basis to provide dental or dental hygiene services using portable equipment."

## reciprocity and interstate practice

### `interstate_compact_participation` — bool
- **what:** Whether the state has enacted the Dentist and Dental Hygienist Compact, enabling compact privilege practice across participating states.
- **states:** CO, ME, OH
- **sample (OH):** "The Dentist and Dental Hygienist Compact is hereby ratified, enacted into law, and entered into by the state of Ohio as a party to the compact with any other state that has legally joined the compact."
