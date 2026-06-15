# Discovered fields — physical_therapy

## whether a doctor's referral is needed

### `direct_access_allowed` — bool
- **what:** Whether a physical therapist may evaluate and treat patients without a referral from another health care provider.
- **states:** UT
- **sample (UT):** "A physical therapist may evaluate, initiate, and provide physical therapy treatment for a client without a referral from another health service provider."

## license tiers and assistant roles

### `pta_license_required` — bool
- **what:** Whether a physical therapist assistant must hold a separate state license distinct from the physical therapist license.
- **states:** UT
- **sample (UT):** "An applicant for a license as a physical therapist assistant shall: ... submit proof of graduation from a physical therapist assistant education program that is accredited by a recognized accreditation agency."

### `pta_supervision_type_required` — list[str]
- **what:** The type(s) of supervision a licensed physical therapist must provide over a physical therapist assistant during practice.
- **states:** UT
- **sample (UT):** "A licensed physical therapist assistant is authorized to practice physical therapy under the on-site supervision or general supervision of a licensed physical therapist."

### `aide_role_defined` — bool
- **what:** Whether the statute defines a non-licensed physical therapy aide role with limited, supervised assistance functions.
- **states:** UT
- **sample (UT):** "A physical therapy aide means a person who is trained, on-the-job, by a licensed physical therapist and provides routine assistance to a licensed physical therapist or licensed physical therapist assistant."

### `aide_supervision_type_required` — list[str]
- **what:** The type of supervision required over a physical therapy aide during practice.
- **states:** UT
- **sample (UT):** "A physical therapy aide may provide routine assistance to a licensed physical therapist ... if the physical therapy aide is under the on-site supervision of the licensed physical therapist."

### `pta_restricted_procedures` — list[str]
- **what:** Specific clinical procedures that a physical therapist assistant or aide is explicitly prohibited from performing.
- **states:** UT
- **sample (UT):** "A physical therapist assistant or a physical therapy aide may not: perform a physical therapy evaluation or assessment; identify or label a physical impairment or injury; design a plan of care for a patient; perform the joint mobilization component of manual therapy; or perform the sharp selective debridement component of wound management."

## special procedures requiring extra credentials

### `trigger_point_dry_needling_authorized` — bool
- **what:** Whether physical therapists are authorized to perform trigger point dry needling as part of physical therapy practice.
- **states:** UT
- **sample (UT):** "Trigger point dry needling means the stimulation of a trigger point using a dry needle to treat neuromuscular pain and functional movement deficits."

### `trigger_point_dry_needling_min_practice_years` — int
- **what:** Minimum years of active physical therapy practice required before a licensee may perform trigger point dry needling.
- **states:** UT
- **sample (UT):** "A physical therapist may practice trigger point dry needling if the physical therapist has held a license to practice physical therapy under this chapter, and has actively practiced physical therapy, for two years."

### `trigger_point_dry_needling_course_hours` — int
- **what:** Minimum total course hours required to qualify for trigger point dry needling practice.
- **states:** UT
- **sample (UT):** "has successfully completed a course in trigger point dry needling that ... includes at least 300 total course hours, including at least 54 hours of in-person instruction and 250 supervised patient treatment sessions."

### `trigger_point_dry_needling_registration_required` — bool
- **what:** Whether a physical therapist must register separately with the licensing authority to practice trigger point dry needling.
- **states:** UT
- **sample (UT):** "registers with the division as a trigger point dry needling practitioner."

### `animal_physical_therapy_authorized` — bool
- **what:** Whether physical therapists are authorized to practice physical therapy on animals under defined conditions.
- **states:** UT
- **sample (UT):** "Animal physical therapy means practicing physical therapy or physiotherapy on an animal."

### `animal_physical_therapy_training_hours` — int
- **what:** Minimum training hours required for a physical therapist to practice animal physical therapy.
- **states:** UT
- **sample (UT):** "A licensed physical therapist may practice animal physical therapy if the licensed physical therapist completes at least 100 hours of animal physical therapy training and education."

### `animal_physical_therapy_veterinarian_supervision_hours` — int
- **what:** Minimum hours of on-the-job training under a licensed veterinarian required to practice animal physical therapy.
- **states:** UT
- **sample (UT):** "50 hours of on-the-job training under the supervision of a licensed veterinarian."

## what they are not allowed to do

### `scope_exclusions` — list[str]
- **what:** Activities explicitly excluded from the authorized scope of physical therapy practice.
- **states:** UT
- **sample (UT):** "Physical therapy or physiotherapy does not include: diagnosing disease; performing surgery; performing acupuncture; taking x-rays; or prescribing or dispensing a drug."

## drugs and medications

### `topical_drug_administration_authorized` — bool
- **what:** Whether physical therapists are authorized to purchase, store, and administer topical prescription medications.
- **states:** UT
- **sample (UT):** "A licensed physical therapist may purchase, store, and administer topically applied medicinal agents, including steroids and analgesics, for wound care and for musculoskeletal treatment, using iontophoresis or phonorphoresis."

### `aerosol_drug_administration_authorized` — bool
- **what:** Whether physical therapists are authorized to administer aerosol prescription medications in limited institutional settings.
- **states:** UT
- **sample (UT):** "aerosols for pulmonary hygiene in an institutional setting, if a licensed respiratory therapist is not available in, or within a 10 mile radius of, the institution."

### `drug_administration_requires_written_prescription` — bool
- **what:** Whether a physical therapist must have a written prescription from a licensed prescriber before administering any medication.
- **states:** UT
- **sample (UT):** "A licensed physical therapist may only purchase, store, or administer a medication described in this section pursuant to a written prescription issued by a practitioner who is licensed to prescribe that medication."

## practicing across state lines

### `interstate_compact_member` — bool
- **what:** Whether the state has enacted the Physical Therapy Licensure Compact allowing multi-state practice privileges.
- **states:** UT
- **sample (UT):** "The purpose of this Compact is to facilitate interstate practice of physical therapy with the goal of improving public access to physical therapy services."

### `compact_privilege_adverse_action_waiting_years` — int
- **what:** Number of years that must elapse after an adverse action before a licensee may obtain a compact privilege in a remote state.
- **states:** UT
- **sample (UT):** "Have not had any adverse action against any license or compact privilege within the previous 2 years."

### `jurisprudence_exam_required_for_compact_privilege` — bool
- **what:** Whether a remote state may require a jurisprudence assessment of state-specific laws as a condition of granting a compact privilege.
- **states:** UT
- **sample (UT):** "Meet any jurisprudence requirements established by the remote state(s) in which the licensee is seeking a compact privilege."

### `telehealth_consultation_exemption` — bool
- **what:** Whether an out-of-state physical therapist may provide consultation to an in-state licensee via telecommunication without obtaining a Utah license.
- **states:** UT
- **sample (UT):** "Consultation by telecommunication means the provision of expert or professional advice by a physical therapist who is licensed outside of Utah to a licensed physical therapist or a health care provider by telecommunication or electronic communication."

### `visiting_practitioner_exemption_days` — int
- **what:** Maximum number of days per calendar year an out-of-state licensed physical therapist may practice in the state without obtaining a local license.
- **states:** UT
- **sample (UT):** "teaching, demonstrating, or providing physical therapy in connection with an educational seminar, if the person engages in this conduct in Utah no more than 60 days per calendar year."

## supervised training and internships

### `internship_certification_required` — bool
- **what:** Whether individuals engaging in a physical therapy internship must be certified by the licensing division rather than simply enrolled in a program.
- **states:** UT
- **sample (UT):** "An individual may not engage in an internship in physical therapy, unless the person is certified by the division or exempt from licensure under Section 58-24b-304."

### `pt_initial_evaluation_exclusive_to_pt` — bool
- **what:** Whether the initial patient evaluation and documentation must be performed exclusively by the licensed physical therapist and cannot be delegated to an assistant or aide.
- **states:** UT
- **sample (UT):** "In practicing physical therapy, a licensed physical therapist shall: perform the initial evaluation and documentation for each patient."

## professional titles and protected terms

### `protected_title_abbreviations` — list[str]
- **what:** Abbreviations and titles that are legally protected and may only be used by licensed physical therapists or assistants.
- **states:** UT
- **sample (UT):** "It is unlawful for a person who is not a licensed physical therapist to use, in connection with the person's name or business, any of the following words or abbreviations: physical therapist; physiotherapist; PT; DPT; MPT."

### `ethics_code_reference` — str
- **what:** The named professional ethics code or conduct standard that licensees are required to follow.
- **states:** UT
- **sample (UT):** "A licensed physical therapist shall adhere to the standards of ethics described in the American Physical Therapy Association's Code of Ethics and Guide for Professional Conduct."
