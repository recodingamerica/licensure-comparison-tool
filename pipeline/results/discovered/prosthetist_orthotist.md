# Discovered fields — prosthetist_orthotist

## license types and credential levels

### `license_tiers` — list[str]
- **what:** The distinct license categories recognized in the state, such as prosthetist, orthotist, combined prosthetist-orthotist, pedorthist, orthotic fitter, and assistant levels.
- **states:** AL, AR, GA, KY, NJ, OH, PA, TX
- **sample (AL):** "The board shall issue approved forms for application prior to January 1, 2003... In order to obtain a license as a prosthetist, orthotist, or prosthetist/orthotist in this state..."

### `assistant_license_available` — bool
- **what:** Whether the state issues a separate license or certification for assistants who work under the supervision of a licensed prosthetist or orthotist.
- **states:** AL, AR, GA, KY, OH, PA, TX
- **sample (TX):** ""Licensed orthotist assistant" or "LOA" means a person licensed under this chapter who assists at an orthotic or prosthetic facility and is under the supervision of a licensed orthotist responsible for the acts of the assistant."

### `orthotic_fitter_license_available` — bool
- **what:** Whether the state issues a separate, limited license for orthotic fitters who fit only prefabricated (non-custom) orthotic devices.
- **states:** AL, KY, PA
- **sample (KY):** ""Licensed orthotic fitter" means a person who receives a license under this chapter to fit the following noncustom orthotic devices: Cervical orthoses... Prefabricated orthoses of upper and lower extremities..."

### `pedorthist_license_available` — bool
- **what:** Whether the state issues a separate license for pedorthists who design, fabricate, and fit therapeutic footwear and foot orthoses.
- **states:** AL, AR, KY, OH, PA, TX
- **sample (KY):** ""Licensed pedorthist" means a person who is licensed under this chapter to practice pedorthics and who represents the person to the public by the title or description of services that includes the term "pedorthic," "pedorthist," or a similar title or description of services."

### `mastectomy_fitter_license_available` — bool
- **what:** Whether the state issues a separate license for mastectomy fitters who provide breast prostheses and post-mastectomy services.
- **states:** AL
- **sample (AL):** ""Mastectomy Fitter." A health care professional who is specifically educated and trained in the provision of breast prostheses and post-mastectomy services, including patient assessment, formulation of a treatment plan, implementation of the treatment plan, and follow-up and practice management."

### `student_registration_certificate_available` — bool
- **what:** Whether the state issues a formal student registration certificate allowing students completing clinical residency requirements to practice under supervision before full licensure.
- **states:** AL, AR, TX
- **sample (TX):** "The department may issue a student registration certificate to an individual who is working toward fulfilling the requirements for a license as an orthotist, prosthetist, or prosthetist orthotist..."

## national certification and accreditation bodies

### `national_certification_required` — bool
- **what:** Whether the state requires applicants to hold or obtain national certification from an approved certifying body (e.g., ABC or BOC) as a condition of licensure.
- **states:** AL, AR, KY, PA, TX
- **sample (AL):** "Be certified as a prosthetist, orthotist, or prosthetist/orthotist by a national certifying board in orthotics or prosthetics approved by the state board."

### `approved_national_certifying_bodies` — list[str]
- **what:** The nationally recognized certifying organizations whose credentials the state accepts for licensure purposes.
- **states:** AL, AR, KY, OH, PA, TX
- **sample (KY):** "A person certified by the American Board for Certification in Orthotics, Prosthetics and Pedorthics, Inc. (ABC)... or by the Board of Certification/Accreditation, International (BOC)..."

### `education_program_accreditor` — list[str]
- **what:** The accrediting body or bodies whose approval of an orthotic or prosthetic education program is required or recognized for licensure eligibility.
- **states:** AL, AR, GA, KY, OH, TX
- **sample (KY):** ""Orthotic and prosthetic education program" means a course of instruction accredited by CAAHEP..."

### `residency_accreditor` — list[str]
- **what:** The accrediting body or bodies whose approval of a clinical residency program is required or recognized for licensure eligibility.
- **states:** AL, AR, GA, KY, OH, TX
- **sample (KY):** ""Residency" means a minimum of a one-year NCOPE accredited program to acquire practical clinical training in orthotics, prosthetics, or both, in a patient care setting."

## referral and prescription requirements

### `written_prescription_required` — bool
- **what:** Whether a written prescription or order from an authorized health care practitioner is required before a licensee may provide prosthetic, orthotic, or pedorthic services to a patient.
- **states:** AL, AR, GA, KY, OH, PA, TX
- **sample (AL):** "A licensed prosthetist, licensed orthotist, or licensed prosthetist/orthotist may provide services utilizing new prostheses or orthoses for which he or she is licensed and only under a written order from an authorized health care practitioner."

### `authorized_prescribers` — list[str]
- **what:** The categories of health care practitioners authorized by law to write orders or prescriptions for orthotic, prosthetic, or pedorthic devices.
- **states:** AL, AR, GA, KY, OH, PA, TX
- **sample (TX):** "Orthotics means the science and practice of... measuring, designing, fabricating, assembling, fitting, adjusting, or servicing an orthosis under an order from a licensed physician, chiropractor, or podiatrist, or an advanced practice nurse or physician assistant acting under the delegation and supervision of a licensed physician..."

### `prescription_exemption_for_repair_adjustment` — bool
- **what:** Whether the state explicitly exempts repair, adjustment, or servicing of an existing device from the prescription requirement.
- **states:** AL, KY
- **sample (AL):** "A consultation with and periodic review by an authorized health care practitioner is not required for the evaluation, repair, adjusting, or servicing of a prosthesis by a licensed prosthetist... nor is an order from an authorized health care practitioner required for maintenance or replacement of an orthosis or prosthesis to the level of its original prescription for an indefinite period of time if the original order remains appropriate for the patient's medical needs."

### `patient_physical_presence_required` — bool
- **what:** Whether the statute explicitly requires the licensee to be in the physical presence of the patient when providing services.
- **states:** AL, OH
- **sample (AL):** "No person licensed under this chapter shall provide services to a patient without being in the physical presence of the patient."

## practice setting and facility rules

### `facility_accreditation_required` — bool
- **what:** Whether the state requires the facility where orthotic or prosthetic care is provided to be separately accredited or registered.
- **states:** AL, TX
- **sample (AL):** ""Accredited Facility." A facility where prosthetic, orthotic, prosthetic and orthotic, or pedorthic care is provided to patients needing such care and has met the requirements of the board for such designation."

### `facility_must_have_licensed_director` — bool
- **what:** Whether the statute requires an orthotic or prosthetic facility to be under the on-site direction of a licensed orthotist or prosthetist.
- **states:** GA, TX
- **sample (TX):** "An orthotic or prosthetic facility must be under the on-site direction of an orthotist or prosthetist licensed by the department in the discipline for which accreditation is sought."

### `facility_must_have_clinical_and_lab_space` — bool
- **what:** Whether the statute specifies that a licensed facility must have appropriate clinical and laboratory space and equipment to provide comprehensive care.
- **states:** GA, KY, TX
- **sample (GA):** ""Facility" means the business location where orthotic or prosthetic care is provided and which has the appropriate clinical and laboratory space and equipment to provide comprehensive orthotic or prosthetic care."

## supervision and delegation

### `supervisor_to_supervisee_ratio_limit` — int
- **what:** The maximum number of unlicensed or assistant-level individuals that a single licensed orthotist or prosthetist may supervise at one time.
- **states:** OH, PA
- **sample (OH):** "No individual licensed under this chapter may supervise more than four individuals not licensed to practice orthotics, prosthetics, or pedorthics who are practicing orthotic, prosthetic, or pedorthic services."

### `supervisor_physical_presence_required_at_initial_eval` — bool
- **what:** Whether the supervising licensee must be physically present during the initial patient evaluation and device fitting or delivery.
- **states:** GA, OH
- **sample (OH):** "During the initial evaluation of any patient who can reasonably be expected to require orthotic, prosthetic, or pedorthic services and during the fitting and delivery of an orthotic or pedorthic device or prosthesis, the supervising orthotist, prosthetist, orthotist-prosthetist, or pedorthist is physically present."

### `supervisor_remote_availability_allowed` — bool
- **what:** Whether the statute explicitly permits the supervising licensee to be available by telecommunication rather than physically present during routine (non-initial) patient care activities.
- **states:** OH, PA
- **sample (OH):** "At times other than those described in division (B) of this section, the supervising orthotist, prosthetist, orthotist-prosthetist, or pedorthist is either physically present at the location where the individual is practicing or is readily available to the individual through some means of telecommunication and is in a location that under normal circumstances is not more than sixty minutes travel time away."

## what licensees can and cannot do

### `scope_excludes_diagnosis` — bool
- **what:** Whether the statute explicitly states that the licensee's scope of practice does not include the right to diagnose a medical problem or condition.
- **states:** AL, GA, KY, PA
- **sample (KY):** "The scope of practice of a licensee shall not include the right to diagnose a medical problem or condition or the right to give medical advice as to the nature, cause, or treatment for the problem or condition for which the orthotic, prosthetic, or pedorthic device is being dispensed."

### `orthotic_fitter_scope_device_types` — list[str]
- **what:** The specific categories of prefabricated orthotic devices that an orthotic fitter (limited-scope licensee) is authorized to fit.
- **states:** KY, PA
- **sample (PA):** "The scope of practice of an orthotic fitter is limited to measuring, fitting, dispensing and adjusting prefabricated devices not requiring more than minor modification of: Cervical soft foam collars. Thoraco-lumbo-sacral orthoses. Lumbo-sacral orthoses. Knee orthoses. Ankle foot orthoses. Foot orthoses. Elbow orthoses. Shoulder orthoses..."

### `devices_excluded_from_scope` — list[str]
- **what:** Categories of devices explicitly excluded from the definition of orthosis or prosthesis and therefore outside the regulated scope of practice.
- **states:** AL, AR, GA, KY, OH, PA, TX
- **sample (GA):** ""Orthosis" does not include fabric or elastic supports, corsets, arch supports, low-temperature plastic splints, trusses, elastic hoses, canes, crutches, soft cervical collars, dental appliances, or other similar devices that are carried in stock and sold as over-the-counter items by a drug store, department store, corset shop, or surgical supply facility."

### `custom_vs_prefabricated_device_distinction_codified` — bool
- **what:** Whether the statute formally defines and distinguishes between custom-fabricated, custom-fitted, and prefabricated (over-the-counter) devices with different regulatory treatment.
- **states:** GA, KY, PA, TX
- **sample (GA):** ""Custom fabricated and fitted device" means that an orthosis or prosthesis is fabricated to original measurements or a mold, or both, for use by a patient in accordance with a prescription and which requires substantial clinical and technical judgment in its design and fitting. "Custom fitted device" means a prefabricated orthosis or prosthesis sized or modified, or both, for use by a patient in accordance with a prescription and which requires substantial clinical judgment and substantive alteration for appropriate use."

### `referral_duty_when_beyond_scope` — bool
- **what:** Whether the statute imposes an affirmative duty on the licensee to refer patients to an authorized health care practitioner when symptoms or conditions are present that are beyond the licensee's scope of practice.
- **states:** AL, KY, PA
- **sample (AL):** "Prosthetists and orthotists must refer persons receiving service to authorized health care practitioners if they have reasonable cause to believe symptoms or conditions are present that require services beyond the scope of their practice or for which the prescribed prosthetic or orthotic service is contraindicated."

## insurance and financial requirements

### `professional_liability_insurance_required` — bool
- **what:** Whether the statute requires licensees to maintain professional liability insurance as a condition of licensure or practice.
- **states:** PA
- **sample (PA):** "An individual licensed to practice prosthetics, orthotics, pedorthics or orthotic fitting in this Commonwealth shall maintain a level of professional liability insurance coverage in the minimum amount of $1,000,000 per occurrence or claims made..."

### `minimum_liability_insurance_amount` — str
- **what:** The minimum dollar amount of professional liability insurance coverage required per occurrence or claims made.
- **states:** PA
- **sample (PA):** "An individual licensed to practice prosthetics, orthotics, pedorthics or orthotic fitting in this Commonwealth shall maintain a level of professional liability insurance coverage in the minimum amount of $1,000,000 per occurrence or claims made."

## continuing education specifics

### `continuing_education_hours_orthotist_prosthetist` — int
- **what:** The number of continuing education hours required per renewal period for licensed orthotists and prosthetists.
- **states:** AL, AR, GA, OH, PA
- **sample (PA):** "A prosthetist and orthotist must provide certification of successful completion of a minimum of 24 hours of continuing education as approved by the board."

### `continuing_education_hours_orthotic_fitter_pedorthist` — int
- **what:** The number of continuing education hours required per renewal period for orthotic fitters and pedorthists (where different from the orthotist/prosthetist requirement).
- **states:** PA
- **sample (PA):** "An orthotic fitter and a pedorthist must provide certification of successful completion of a minimum of 13 hours of continuing education as approved by the board."

## who is exempt from these rules

### `exemptions_for_other_licensed_professions` — list[str]
- **what:** The categories of other licensed health care professionals explicitly exempted from the orthotic and prosthetic licensure requirements when practicing within their own scope.
- **states:** AL, AR, GA, KY, OH, PA, TX
- **sample (KY):** "Nothing in this chapter or in the administrative regulations promulgated by the board pursuant to this chapter shall be interpreted to limit or restrict: A licensed health care practitioner or provider from engaging in the full scope of practice authorized by the license for that person's profession... A person licensed as a physical therapist... occupational therapist... athletic trainer... physician... chiropractor... pharmacist..."

### `pharmacy_fitting_exemption` — bool
- **what:** Whether the statute explicitly exempts pharmacists or pharmacy employees from licensure requirements when fitting or sizing prefabricated (non-custom) orthotic or pedorthic devices.
- **states:** AR, KY, TX
- **sample (KY):** "Individuals acting under the supervision and control of a licensed pharmacist or pharmacy from measuring, fitting, or adjusting any noncustom fabricated and fitted device including but not limited to over-the-counter devices, so long as such individual does not create a cast, mold, or scan of a part of the human body for the purpose of constructing a medical device to treat a patient's medical condition..."

### `manufacturer_representative_exemption` — bool
- **what:** Whether the statute explicitly exempts employees or authorized representatives of orthotic or prosthetic device manufacturers from licensure requirements when fitting devices under physician supervision.
- **states:** AL, GA, KY, PA, TX
- **sample (KY):** "The measuring, fitting, or adjusting of an orthotic device by an employee or authorized representative of an orthosis manufacturer registered with the federal food and drug administration, when the employee or representative is directly supervised by a licensed health care professional authorized by law to prescribe, measure, or fit the device..."

### `federal_employee_exemption` — bool
- **what:** Whether the statute explicitly exempts individuals employed by the federal government from state licensure requirements when performing duties within their official federal role.
- **states:** AL, AR, GA, KY, OH, PA, TX
- **sample (KY):** "The practice of orthotics, prosthetics, or pedorthics by a person who is employed by the federal government or any bureau, division, or agency of the federal government while in the discharge of the employee's official duties."

### `pedorthist_exemption_from_op_licensure` — bool
- **what:** Whether certified pedorthists are explicitly exempted from the general orthotics and prosthetics licensure requirements.
- **states:** GA, TX
- **sample (TX):** "This chapter does not apply to a certified pedorthist."

### `three_d_printing_open_source_prosthetics_addressed` — bool
- **what:** Whether the statute specifically addresses the 3-D printing of open-source prosthetic kits by unlicensed individuals and establishes a separate authorization pathway.
- **states:** OH
- **sample (OH):** "Division (A) of this section does not prohibit an individual who is not licensed under this chapter to practice prosthetics or orthotics and prosthetics from engaging in the 3-D printing of open-source prosthetic kits if the individual has been granted the authority to engage in that activity by the Ohio occupational therapy, physical therapy, and athletic trainers board..."

## governing board structure

### `board_composition_includes_consumer_member` — bool
- **what:** Whether the statute requires the governing board to include at least one public or consumer member who is not a licensed practitioner.
- **states:** AL, AR, OH
- **sample (AR):** "One (1) member who is a representative of the public at large."

### `board_composition_includes_physician_member` — bool
- **what:** Whether the statute requires the governing board to include at least one licensed physician as a member.
- **states:** AL
- **sample (AL):** "One of whom shall be a physician licensed to practice medicine in the State of Alabama."

### `advisory_council_established` — bool
- **what:** Whether the statute establishes a separate advisory council or committee to advise the primary licensing board on orthotic and prosthetic matters.
- **states:** GA, OH, TX
- **sample (OH):** "The Ohio occupational therapy, physical therapy, and athletic trainers board shall appoint an orthotics, prosthetics, and pedorthics advisory council for the purpose of advising the board on issues relating to the practice of orthotics, prosthetics, and pedorthics..."

### `scope_of_practice_rules_jointly_promulgated` — bool
- **what:** Whether the statute requires scope-of-practice rules for orthotists and prosthetists to be jointly promulgated with the state medical board.
- **states:** AL
- **sample (AL):** "Any rule or regulation defining the scope of practice or permissible activities of a licensed orthotist, licensed prosthetist, or a licensed prosthetist/orthotist or a registered orthotic supplier shall be published jointly with the State Board of Medical Examiners."
