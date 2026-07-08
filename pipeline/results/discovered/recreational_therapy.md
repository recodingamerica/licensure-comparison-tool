# Discovered fields — recreational_therapy

## license levels and career ladder

### `license_tier_classifications` — list[str]
- **what:** Named tiers or classifications of licensure available within the profession, reflecting different levels of education, experience, and authorized scope.
- **states:** NC, UT
- **sample (UT):** "The division shall issue to a person who qualifies under this chapter a license in the classification of: (a) master therapeutic recreation specialist; (b) therapeutic recreation specialist; or (c) therapeutic recreation technician."

### `assistant_tier_available` — bool
- **what:** Whether the state recognizes a sub-therapist assistant or technician license tier distinct from the full therapist license.
- **states:** NC, UT
- **sample (NC):** "Licensed recreational therapy assistant. - A person who holds a license pursuant to this Chapter as a recreational therapy assistant to act under the supervision of a licensed recreational therapist as defined by rule."

### `aide_tier_available` — bool
- **what:** Whether the state recognizes an unlicensed aide role that may perform limited tasks under direct on-site supervision.
- **states:** NC, UT
- **sample (NC):** "Recreational therapy aide. - Any nonlicensed person who aids in the provision of recreational therapy services under the provisions of this Chapter, and who acts under the direction and on-site supervision of a licensed recreational therapist or licensed recreational therapy assistant."

### `credential_type` — enum[license, registration, certification]
- **what:** The formal credential type issued by the state to authorize practice.
- **states:** NC, NH, NJ, UT, WA
- **sample (WA):** "'Registration' means the registration issued to a person under this chapter."

## national credential and exam pathways

### `nctrc_certification_accepted_in_lieu_of_exam` — bool
- **what:** Whether holding an active NCTRC Certified Therapeutic Recreation Specialist (CTRS) credential can substitute for or satisfy the state examination requirement.
- **states:** NC, NH, UT
- **sample (UT):** "document proof of current certification in good standing as a Certified Therapeutic Recreation Specialist by the National Council for Therapeutic Recreation Certification, or an equivalence of that certification, as determined by division rule made in consultation with the board."

### `nctrc_continuing_education_accepted` — bool
- **what:** Whether continuing education programs meeting NCTRC recertification standards are accepted toward state renewal requirements.
- **states:** NC, NH
- **sample (NH):** "The executive director, in consultation with the advisory board, shall accept continuing education programs that meet the recertification standards of the National Council for Therapeutic Recreation Certification."

### `scope_job_analysis_reference` — bool
- **what:** Whether the state explicitly references the NCTRC Job Analysis Study as the authoritative basis for defining scope of practice.
- **states:** NC, NH
- **sample (NC):** "The practice of recreational therapy includes all direct patient or client services... representing the process and knowledge base delineated in the most recent National Council for Therapeutic Recreation Certification (NCTRC) Job Analysis Study and professional standards of practice."

## where and how services may be delivered

### `authorized_practice_settings` — list[str]
- **what:** Explicit list of settings in which a licensee is authorized to practice recreational therapy.
- **states:** NC, UT
- **sample (NC):** "A person licensed as a 'Recreational Therapist' under this Chapter may practice in clinical, residential, educational, and community settings."

### `private_practice_authorized` — bool
- **what:** Whether the licensee is explicitly authorized to practice in private practice (as opposed to only institutional or supervised employment settings).
- **states:** NC, UT
- **sample (UT):** "A master therapeutic recreation specialist licensed under this chapter may: (a) practice recreational therapy: ... (ii) in private practice; or (iii) as a consultant."

### `referral_required_for_treatment` — bool
- **what:** Whether a referral from a qualified health care professional is required before initiating recreational therapy services for individuals with medically-related conditions.
- **states:** NH, UT
- **sample (NH):** "Initiation of recreational therapy services to individuals with medically-related conditions shall be based on a referral from any qualified health care professional who, within the scope of the professional's licensure, is authorized to refer for health care services."

### `referral_exempt_services` — list[str]
- **what:** Categories of services explicitly exempted from the referral requirement.
- **states:** NH, UT
- **sample (NH):** "Prevention, wellness, education, adaptive sports and recreation, and related services shall not require a referral."

## what therapists are specifically allowed to do

### `adaptive_equipment_authorized` — bool
- **what:** Whether the statute explicitly authorizes identifying, designing, fabricating, applying, or training in the use of adaptive recreational equipment.
- **states:** NH, NJ
- **sample (NH):** "Identifying, designing, fabricating, applying, or training in the use of, adaptive recreational equipment."

### `community_integration_services_authorized` — bool
- **what:** Whether the statute explicitly authorizes community integration, reintegration, inclusion, and transitioning services.
- **states:** NH, NJ, WA
- **sample (NJ):** "Providing community integration, reintegration, inclusion, and transitioning services to maximize health and participation in play, recreation, leisure, and related community activities."

### `leisure_education_and_counseling_authorized` — bool
- **what:** Whether the statute explicitly authorizes leisure education and counseling as a distinct service within scope of practice.
- **states:** NH, NJ, WA
- **sample (NJ):** "Providing leisure education and counseling to address issues that hinder health and engagement in play, recreation, leisure, and related community activities."

### `pain_management_modalities_authorized` — bool
- **what:** Whether the statute explicitly authorizes non-invasive and non-pharmacological approaches to reduce or alleviate pain as part of recreational therapy services.
- **states:** NH, NJ
- **sample (NH):** "Identifying, applying, and evaluating the use of non-invasive and non-pharmacological approaches to reduce or alleviate pain or manage pain to minimize its impact upon participation."

### `discharge_planning_authorized` — bool
- **what:** Whether the statute explicitly authorizes developing a discharge or transition plan in collaboration with the patient, family, and treatment team.
- **states:** NC, NH, NJ, UT
- **sample (NJ):** "Developing a discharge plan in collaboration with the individual, the individual's family, and other treatment team members."

## supervision and delegation rules

### `supervision_required_for_assistant_tier` — bool
- **what:** Whether the statute requires assistant- or technician-tier licensees to practice under the supervision of a higher-tier licensed recreational therapist.
- **states:** NC, UT
- **sample (UT):** "A therapeutic recreation technician: (a) may perform recreational therapy services if: (i) under the supervision of a master therapeutic recreation specialist or a therapeutic recreation specialist employed full-time and on-site in the same hospital, clinic, or facility."

### `delegation_coercion_prohibited` — bool
- **what:** Whether the statute explicitly prohibits coercing a licensed recreational therapist into delegating tasks when the therapist determines delegation would compromise client safety.
- **states:** NH, UT
- **sample (NH):** "No person shall coerce a licensed recreational therapist into compromising client safety by requiring the licensed recreational therapist to delegate activities or tasks if the licensed recreational therapist determines that it is inappropriate to do so."

### `technician_assessment_limitations` — bool
- **what:** Whether the statute explicitly restricts the technician or assistant tier from performing the interpretive or analytical portion of patient assessment.
- **states:** NC, UT
- **sample (UT):** "A therapeutic recreation technician: ... (d) may not perform the portion of an assessment described in Subsection 58-40-102(2)(a)(ii) [interpreting and analyzing collected data]."

## patient rights and confidentiality

### `privileged_communications_protection` — bool
- **what:** Whether the statute places therapist-client communications on the same privileged legal basis as physician-patient communications.
- **states:** NH, UT
- **sample (NH):** "The confidential communications between licensed recreational therapists and their clients or patients is placed on the same legal basis as those between physician and patient, and except as otherwise provided by law, no recreational therapist shall be required to disclose such privileged communications."

### `patient_privacy_duty` — bool
- **what:** Whether the statute explicitly imposes a duty on licensees to safeguard a patient's right to privacy regarding identity, condition, diagnosis, and personal effects.
- **states:** NH, UT
- **sample (UT):** "Failing to safeguard a person's right to privacy as to the person's identity, condition, diagnosis, personal effects, or other matters about which the licensee is privileged to know from providing recreational therapy services."

## mandatory specialized training

### `suicide_prevention_training_required` — bool
- **what:** Whether the statute mandates a minimum number of hours of suicide prevention training as a condition of initial licensure or license renewal.
- **states:** NH, UT
- **sample (UT):** "The division shall require a licensee, as a condition of renewal of the licensee's license, to complete a minimum of two hours of training in suicide prevention via a course that the division designates as approved."

### `suicide_prevention_training_hours` — int
- **what:** Minimum number of hours of suicide prevention training required by statute for licensure or renewal.
- **states:** NH, UT
- **sample (UT):** "complete a minimum of two hours of training in suicide prevention via a course that the division designates as approved."

### `treatment_plan_documentation_required` — bool
- **what:** Whether the statute explicitly requires a written individualized treatment or intervention plan to be maintained for each patient receiving recreational therapy services.
- **states:** NC, NH, NJ, UT
- **sample (UT):** "A recreational therapy treatment or intervention plan shall be maintained for each patient receiving recreational therapy services under this chapter."

## professional title and credential display rules

### `authorized_title_abbreviations` — list[str]
- **what:** Specific letter abbreviations or title designations that licensed practitioners are authorized or prohibited from using.
- **states:** NC, NH, UT
- **sample (NH):** "Licensed recreational therapists may use the letters 'TR,' 'TRS,' and 'CTRS/L' in connection with their name or place of business."

### `recreational_activity_exemption` — bool
- **what:** Whether the statute explicitly exempts persons conducting recreational activities for purely recreational (non-therapeutic) purposes from licensure requirements.
- **states:** NC, UT, WA
- **sample (UT):** "A person may conduct or participate in a recreational activity without being licensed under this chapter if the person is using the recreational activity for the sole outcome of the recreational experience and is not using recreational activity as a therapeutic intervention following the therapeutic recreation process."
