# Discovered fields — respiratory_care

## supervision and delegation

### `medical_direction_required` — bool
- **what:** Whether practice must occur under the qualified medical direction or supervision of an authorized prescribing practitioner.
- **states:** UT
- **sample (UT):** "treatment, operation of equipment, management, diagnostic testing, and care of any human disease, deficiency, pain, injury, or other physical condition associated with the cardiopulmonary system under the qualified medical direction or supervision of a practitioner"

### `independent_practice_prohibited` — bool
- **what:** Whether the licensee is explicitly prohibited from practicing independently of a supervising practitioner or health care facility.
- **states:** UT
- **sample (UT):** "A respiratory care practitioner may not: (1) practice independently of a practitioner or of a health care facility while under the supervision of a practitioner; or (2) charge a fee for his services independently of a practitioner or health care facility."

### `order_types_accepted` — list[str]
- **what:** Types of practitioner orders or prescriptions a respiratory care practitioner is authorized to accept and carry out.
- **states:** UT
- **sample (UT):** "accepting and carrying out a practitioner's written, verbal, or telephonic prescription or order specifically relating to respiratory care"

### `teaching_supervision_authorized` — bool
- **what:** Whether the licensee is authorized to supervise, direct, or teach personnel in respiratory care modalities as part of an education program.
- **states:** UT
- **sample (UT):** "supervising, directing, or teaching personnel in the performance of respiratory care modalities as part of a respiratory care education program"

## what they can treat and where on the body

### `emergency_transport_authorized` — bool
- **what:** Whether the licensee is authorized to administer respiratory care during patient transportation or in emergency situations.
- **states:** UT
- **sample (UT):** "administering respiratory care during transportation of a patient and under other circumstances where an emergency requires immediate respiratory care"

### `durable_medical_equipment_exclusion` — bool
- **what:** Whether delivery, installation, or maintenance of respiratory-related durable medical equipment without clinical evaluation is explicitly excluded from the scope of practice.
- **states:** UT
- **sample (UT):** "does not include a person who delivers, installs, or maintains respiratory related durable medical equipment and who gives instructions regarding the use of that equipment as long as that person does not perform clinical evaluation or treatment of the patient"

### `durable_medical_equipment_categories` — list[str]
- **what:** Enumerated categories of respiratory-related durable medical equipment defined in statute.
- **states:** UT
- **sample (UT):** "medical grade oxygen; equipment and supplies related to medical gases; apnea monitors; oximeters; noninvasive positive pressure generators, except those with back-up respiratory rate or when used invasively; bilirubin lights; suctioning equipment; large volume nebulizers with compressors; medication nebulizers; enteral nutrition equipment"

### `cardiopulmonary_system_focus` — bool
- **what:** Whether the scope of practice is explicitly limited to conditions associated with the cardiopulmonary system.
- **states:** UT
- **sample (UT):** "care of any human disease, deficiency, pain, injury, or other physical condition associated with the cardiopulmonary system"

## professional titles and credentials

### `protected_titles` — list[str]
- **what:** Titles or designations that only a licensed respiratory care practitioner may use.
- **states:** UT
- **sample (UT):** "Only a respiratory care practitioner may use the following titles or designations in this state: (a) respiratory care practitioner; (b) respiratory therapist; or (c) respiratory technician."

## exemptions from licensure

### `licensure_exemption_categories` — list[str]
- **what:** Categories of persons explicitly exempt from licensure requirements while still permitted to perform respiratory care activities under stated conditions.
- **states:** UT
- **sample (UT):** "any person who acts under a certification issued pursuant to Title 53, Chapter 2d, Emergency Medical Services Act, while providing emergency medical services"

### `polysomnography_technician_scope_restrictions` — list[str]
- **what:** Specific respiratory care activities a polysomnographic technician or trainee may perform without a license, and the settings or conditions under which they are permitted.
- **states:** UT
- **sample (UT):** "a polysomnographic technician or trainee, acting under supervision, as long as the technician or trainee administers the following only in a sleep lab, sleep center, or sleep facility: (i) oxygen titration; and (ii) positive airway pressure that does not include mechanical ventilation"

## education and training requirements

### `high_school_education_required` — bool
- **what:** Whether a high school diploma or equivalent is explicitly required as a baseline educational prerequisite for licensure.
- **states:** UT
- **sample (UT):** "possess a high school education or its equivalent, as determined by the division in collaboration with the board"
