# Discovered fields — athletic_training

## credentials and certification

### `national_certification_required` — bool
- **what:** Whether the applicant must hold current certification from a nationally recognized credentialing body (e.g., Board of Certification Inc.) as a condition of licensure.
- **states:** UT
- **sample (UT):** "is in good standing with and provides documentation of current certification by the Board of Certification Inc. or a nationally recognized credentialing agency approved by the board"

### `certifying_body_name` — str
- **what:** Name of the primary national credentialing organization whose certification satisfies the licensure requirement.
- **states:** UT
- **sample (UT):** "the certification examination administered by the Board of Certification Inc."

## supervision and oversight

### `supervising_clinician_types` — list[str]
- **what:** Types of licensed clinicians who may serve as the directing or supervising authority over an athletic trainer's practice.
- **states:** UT
- **sample (UT):** ""Directing physician" means a physician and surgeon... an osteopathic physician and surgeon... a chiropractic physician... a naturopathic physician... or dentist"

### `supervision_order_types` — list[str]
- **what:** Forms of direction or orders through which a supervising clinician may authorize athletic training services.
- **states:** UT
- **sample (UT):** "A directing physician shall provide direction to an athletic trainer by a verbal order when in the presence of the athletic trainer and by written order or by athletic training service plans or protocols when a directing physician is not present."

### `service_plan_or_protocol_required` — bool
- **what:** Whether athletic training services must be carried out under established written service plans or protocols when the directing clinician is not present.
- **states:** UT
- **sample (UT):** "by written order or by athletic training service plans or protocols when a directing physician is not present"

## who can be treated

### `patient_population_definition` — str
- **what:** Statutory definition of the population an athletic trainer is authorized to serve, including any non-athlete roles covered.
- **states:** UT
- **sample (UT):** ""Athlete" means an individual, referee, coach, or athletic staff member who participates in exercises, sports, or games requiring physical strength, agility, flexibility, range of motion, speed, or stamina"

## treatments and techniques allowed

### `authorized_therapeutic_modalities` — list[str]
- **what:** Specific therapeutic modalities explicitly enumerated in statute as within the athletic trainer's scope of practice.
- **states:** UT
- **sample (UT):** "administering therapeutic exercise and therapeutic and physical modalities, including cryotherapy, thermotherapy, and intermittent compression, electrical stimulation, ultra sound, traction devices, or mechanical devices"

### `return_to_play_authority` — bool
- **what:** Whether the athletic trainer is explicitly authorized to determine an athlete's readiness to return to participation.
- **states:** UT
- **sample (UT):** "determine whether an athlete may return to participation or, if the injury requires further definitive care, refer the athlete to the appropriate directing physician"

### `preparticipation_screening_authorized` — bool
- **what:** Whether the athletic trainer is explicitly authorized to perform preparticipation physical screening.
- **states:** UT
- **sample (UT):** "performing preparticipation screening"

## recordkeeping requirements

### `adequate_records_components` — list[str]
- **what:** Minimum required elements that must appear in an athletic trainer's client records as defined by statute.
- **states:** UT
- **sample (UT):** ""Adequate records" means legible records that contain, at a minimum: (a) the athletic training service plan or protocol; (b) an evaluation of objective findings; (c) the plan of care and the treatment records; or (d) written orders."
