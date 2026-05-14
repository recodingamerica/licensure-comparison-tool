# Discovered fields — optometry

## what they can and cannot do clinically

### `surgery_prohibited` — bool
- **what:** Whether the statute explicitly prohibits optometrists from performing invasive or ophthalmic surgery.
- **states:** AK, AL, AR, AZ, CA
- **sample (AL):** "Optometrists are prohibited from performing injections into the eyeball, cataract surgery, muscle surgery, retinal surgery, radial keratotomy, laser surgery, cryosurgery, or any other invasive surgery."

### `surgery_definition` — str
- **what:** Statutory definition of 'surgery' as it applies to the limits of optometric practice.
- **states:** AK, AZ, CA
- **sample (AK):** "'ophthalmic surgery' means an invasive procedure in which human tissue is cut, ablated, or otherwise penetrated by incision, laser, or other means to treat diseases of the human eye, alter or correct refractive error, or alter or enhance cosmetic appearance"

### `foreign_body_removal_authorized` — bool
- **what:** Whether the statute explicitly authorizes removal of superficial foreign bodies from the eye and its appendages.
- **states:** AK, AL, AR, AZ, CA
- **sample (AK):** "A licensee may remove superficial foreign bodies from the eye and its appendages. This section is not intended to permit a licensee to perform invasive surgery."

### `laser_procedures_authorized` — list[str]
- **what:** Specific laser procedures the statute explicitly authorizes optometrists to perform.
- **states:** AR, CA
- **sample (AR):** "The 'practice of optometry' includes the following procedures: ... Laser capsulotomy; and Laser trabeculoplasty."

### `minor_surgical_procedures_authorized` — list[str]
- **what:** Minor non-laser procedural authorities explicitly granted by statute beyond foreign body removal.
- **states:** AR, CA
- **sample (AR):** "Injections, excluding intravenous or intraocular injections; Incision and curettage of a chalazion; Removal and biopsy of skin lesions with low risk of malignancy"

### `glaucoma_treatment_authorized` — bool
- **what:** Whether the statute explicitly authorizes optometrists to medically treat glaucoma.
- **states:** AR, CA
- **sample (CA):** "If also certified under subdivision (c), using or prescribing topical and oral antiglaucoma agents for the medical treatment of all primary open-angle, exfoliation, pigmentary, and steroid-induced glaucomas in persons 18 years of age or over."

### `anaphylaxis_treatment_authorized` — bool
- **what:** Whether the statute explicitly authorizes optometrists to administer epinephrine or similar agents for anaphylaxis.
- **states:** AL, AR, AZ
- **sample (AL):** "The practice of optometry shall include the authority to administer benedryl, epinephrine, or other medication to counteract anaphylaxis or anaphylactic reaction."

### `vision_therapy_authorized` — bool
- **what:** Whether the statute explicitly includes vision therapy, orthoptics, or visual training within the scope of practice.
- **states:** AL, AR, AZ, CA
- **sample (AL):** "the providing of developmental and perceptual therapy for the vision system"

### `immunization_authority` — bool
- **what:** Whether the statute authorizes optometrists to administer immunizations/vaccines.
- **states:** AZ, CA
- **sample (CA):** "independent initiation and administration of immunizations for influenza, herpes zoster virus, pneumococcus, and SARS-CoV-2 ... in persons 18 years of age or over."

## drugs and prescribing limits

### `controlled_substance_schedule_restrictions` — list[str]
- **what:** Specific controlled substance schedules that optometrists are prohibited from or limited in prescribing.
- **states:** AK, AL, AR, AZ, CA
- **sample (AR):** "Optometrists are excluded from possessing, administering, or prescribing those pharmaceutical agents listed in Schedules I and II of the Uniform Controlled Substances Act, except hydrocodone combination drugs, regardless of their schedule, in combination with oral analgesic drugs."

### `opioid_prescription_day_limit` — int
- **what:** Maximum number of days' supply for an initial opioid prescription issued by an optometrist.
- **states:** AK, AR
- **sample (AK):** "A licensee may not issue an initial prescription for an opioid that exceeds a four-day supply to an adult patient for outpatient use."

### `oral_pharmaceutical_authority` — bool
- **what:** Whether the statute explicitly grants authority to prescribe oral (systemic) pharmaceutical agents, beyond topical agents.
- **states:** AL, AR, AZ, CA
- **sample (AZ):** "A licensee may prescribe, dispense and administer the following oral prescription pharmaceuticals for treating diseases of the eye and its adnexa"

### `pharmaceutical_certification_required` — bool
- **what:** Whether a separate board certification or approval is required before an optometrist may use therapeutic pharmaceutical agents.
- **states:** AL, AR, AZ, CA
- **sample (AL):** "The use and prescribing of pharmaceutical agents for the treatment of the human eye and its adjacent structures shall be limited to those optometrists approved by the board."

### `dea_registration_required` — bool
- **what:** Whether the statute requires optometrists who prescribe controlled substances to hold or register a federal DEA number.
- **states:** AK, CA
- **sample (AK):** "require that a licensee who has a federal Drug Enforcement Administration registration number register with the controlled substance prescription database"

## extra credentials and tiered scope

### `tiered_license_types` — list[str]
- **what:** Named license tiers or designations beyond the basic optometrist license that carry different scopes of practice.
- **states:** AR, CA
- **sample (AR):** "Beginning July 1, 2003, the board will issue licenses only for optometric physicians to persons who meet the requirements of this section"

### `specialty_certification_types` — list[str]
- **what:** Named specialty certifications (beyond basic licensure) that unlock additional scope, such as therapeutic pharmaceutical agents or glaucoma treatment.
- **states:** AL, AR, AZ, CA
- **sample (CA):** "In order to be certified to use therapeutic pharmaceutical agents and authorized to diagnose and treat the conditions listed in subdivisions (b) and (d) of Section 3041, an optometrist shall apply for a certificate from the board"

### `pharmacology_training_hours_required` — int
- **what:** Minimum clock hours of pharmacology or ocular disease training required for therapeutic pharmaceutical agent certification or expanded scope.
- **states:** AK, AL, AR, CA
- **sample (AK):** "a nontopical therapeutic pharmaceutical agent course of at least 23 hours approved by the board or an examination approved by the board on the treatment and management of ocular disease"

### `supervised_clinical_internship_required` — bool
- **what:** Whether a supervised clinical internship or preceptorship is required for expanded pharmaceutical or procedural certification.
- **states:** AR, CA
- **sample (AR):** "Served an internship program established by the board, supervised and certified by a board-certified ophthalmologist, which internship includes at least one hundred (100) hours of supervised clinical training"

## supervision and coordination with other providers

### `referral_to_physician_required` — bool
- **what:** Whether the statute requires optometrists to refer patients to a physician when conditions exceed the optometric scope of practice.
- **states:** AK, AL, AZ, CA
- **sample (AK):** "failed to refer a patient to a physician after ascertaining the presence of ocular or systemic conditions requiring management by a physician"

### `comanagement_with_ophthalmologist_required` — bool
- **what:** Whether the statute requires co-management with an ophthalmologist for pre- or post-operative care or certain conditions.
- **states:** AR, CA
- **sample (CA):** "Treatment with topical and oral medications authorized in subdivision (a) related to an ocular surgery shall be comanaged with the ophthalmologist that performed the surgery"

### `delegation_to_unlicensed_assistants_authorized` — bool
- **what:** Whether the statute explicitly authorizes optometrists to delegate routine or specified tasks to unlicensed or non-optometrist assistants.
- **states:** AK, AL, CA
- **sample (AK):** "authorizing an optometrist licensed under this chapter to delegate routine services of optometry to an agent of the optometrist"

## how and where care can be delivered

### `telemedicine_authorized` — bool
- **what:** Whether the statute explicitly addresses or authorizes the delivery of optometric services via telemedicine.
- **states:** AL, CA
- **sample (AL):** "TELEMEDICINE. A health service that is delivered by a licensed optometrist acting within the scope of his or her license and that requires the use of advanced telecommunications technology"

### `mobile_office_authorized` — bool
- **what:** Whether the statute explicitly addresses or regulates the operation of mobile optometric offices (vans, trailers, etc.).
- **states:** AK, CA
- **sample (CA):** "'mobile optometric office' means a trailer, van, or other means of transportation in which the practice of optometry, as defined in Section 3041, is performed"

### `home_visit_permit_required` — bool
- **what:** Whether the statute requires a special permit or registration to practice optometry at a patient's home residence.
- **states:** AK, CA
- **sample (CA):** "An optometrist who is certified as a therapeutic pharmaceutical agent pursuant to Section 3041.3 may ... submit an application to the board for a home residence permit"

### `maximum_number_of_offices` — int
- **what:** Maximum number of offices a single optometrist or group may operate under the statute.
- **states:** AL, CA
- **sample (CA):** "No optometrist, and no two or more optometrists jointly, may have more than 11 offices."

## prescriptions and optical devices

### `contact_lens_prescription_expiration_years` — int
- **what:** Minimum required expiration period (in years) for a contact lens prescription.
- **states:** AR, AZ, CA
- **sample (AR):** "A written contact lens prescription shall expire one (1) year after the date of the completion of the contact lens fitting unless there is a medical reason that warrants a prescription for less than one (1) year."

### `spectacle_prescription_release_required` — bool
- **what:** Whether the statute requires the prescriber to provide the patient with a copy of their spectacle or eyeglass prescription at no additional charge.
- **states:** AR, AZ, CA
- **sample (AR):** "the optometrist or physician practicing as an ophthalmologist shall upon request of the patient provide to the patient a complete and accurate written prescription at no additional charge."

## patient records and documentation

### `patient_record_retention_years` — int
- **what:** Minimum number of years optometrists are required to retain patient records.
- **states:** AL, CA
- **sample (CA):** "An optometrist shall retain a patient's records for a minimum of seven years from the date he or she completes treatment of the patient."

## practitioner health and impairment

### `impaired_practitioner_program_established` — bool
- **what:** Whether the statute establishes or references a formal program for identifying, treating, and monitoring impaired optometrists.
- **states:** AL, AR, CA
- **sample (AL):** "IMPAIRED DOCTOR OF OPTOMETRY TREATMENT PROGRAM. The Alabama Board of Optometry approved or sponsored program for the detection, intervention, and monitoring of impaired providers."

## special and limited license types

### `limited_teaching_license_available` — bool
- **what:** Whether the statute provides for a limited license for optometry faculty or instructors who are not otherwise licensed in the state.
- **states:** AL, CA
- **sample (AL):** "The board may, under rules and regulations to be promulgated by the board, issue limited licenses, in the case of teachers, to persons who hold an optometric degree where such persons are not licensed and registered to practice optometry in this state."

### `retired_license_status_available` — bool
- **what:** Whether the statute provides for a formal retired license status that exempts the holder from renewal and continuing education requirements.
- **states:** AK, AL, CA
- **sample (AK):** "On retiring from practice and on payment of an appropriate one-time fee, a licensee in good standing with the board may apply for the conversion of an active or inactive license to a retired status license."

### `jurisprudence_exam_required` — bool
- **what:** Whether the statute explicitly requires passage of a state law (jurisprudence) examination as a condition of licensure or endorsement.
- **states:** AK, AR, AZ, CA
- **sample (AK):** "Has passed a written examination approved by the board that is designed to test the applicant's knowledge of the laws of Alaska governing the practice of optometry"

### `criminal_background_check_required` — bool
- **what:** Whether the statute requires applicants to submit to a criminal background check (including fingerprinting) as part of the licensure process.
- **states:** AR, AZ, CA
- **sample (AR):** "Application to the Identification Bureau of the Division of Arkansas State Police for a state and national criminal background check, to be conducted by the Federal Bureau of Investigation, which shall include the taking of fingerprints."
