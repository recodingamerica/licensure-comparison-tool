# Discovered fields — radiologic_technology

## types of credentials and who holds them

### `credential_tiers` — list[str]
- **what:** The distinct credential levels or specialty categories recognized by the state (e.g., radiographer, radiation therapist, nuclear medicine technologist, radiologist assistant, limited permit technician, practical technologist).
- **states:** AZ, CT, HI, KS, KY, LA, MD, MO, … (+2)
- **sample (AZ):** ""Practical technologist in podiatry", "Practical technologist in radiology", "Practical technologist in bone densitometry", "Radiologic technologist", "Radiation therapy technologist", "Mammographic technologist", "Nuclear medicine technologist", "Computed tomography technologist", "Radiologist assistant""

### `limited_scope_operator_recognized` — bool
- **what:** Whether the state recognizes a limited-scope or limited-permit category for operators who may only perform x-rays on specified body parts or procedures, distinct from a full radiologic technologist license.
- **states:** AZ, KY, MD, MS, MT
- **sample (MS):** ""Limited x-ray machine operator" means a person other than a licensed practitioner or radiologic technologist who is issued a permit by the State Board of Medical Licensure to perform medical radiation technology limited to specific radiographic procedures on certain parts of the human anatomy, specifically the chest, abdomen and skeletal structures, and excluding fluoroscopic, both stationary and mobile (C-arm), and contrast studies, computed tomography, nuclear medicine, radiation therapy studies and mammography."

## what they can treat and where on the body

### `body_parts_restricted_for_limited_operators` — list[str]
- **what:** Specific body parts or anatomical regions that limited-scope operators are authorized to image, as enumerated in statute.
- **states:** AZ, MD, MS
- **sample (AZ):** ""Practical technologist in podiatry certificate" means a certificate that is issued to a person, other than a licensed practitioner, who applies ionizing radiation to the foot and leg for diagnostic purposes while under the specific direction of a licensed practitioner."

### `excluded_modalities_for_limited_operators` — list[str]
- **what:** Imaging modalities explicitly excluded from the scope of limited-scope operators (e.g., fluoroscopy, CT, mammography, nuclear medicine).
- **states:** KY, MD, MS
- **sample (MD):** "Do not include: Computerized or noncomputerized tomography; Fluoroscopy; Invasive radiology; Mammography; Nuclear medicine; Radiation therapy; or Xerography"

### `modalities_excluded_from_radiologic_technology_definition` — list[str]
- **what:** Imaging or diagnostic modalities explicitly excluded from the statutory definition of radiologic technology (e.g., echocardiography, diagnostic sonography, MRI).
- **states:** KS, KY
- **sample (KS):** ""Radiologic technology" means the use of radioactive substance or equipment emitting or detecting ionizing radiation on humans for diagnostic or therapeutic purposes upon prescription of a licensed practitioner. The term includes the practice of radiography, nuclear medicine technology and radiation therapy, but does not include echocardiography, diagnostic sonography and magnetic resonance imaging."

## drugs and injections they are allowed to give

### `contrast_media_administration_authorized` — bool
- **what:** Whether licensed radiologic technologists are explicitly authorized to administer contrast media or other parenteral agents.
- **states:** AZ, CT, MS, MT
- **sample (MT):** "A radiologic technologist licensed under this chapter may inject contrast media and radioactive isotopes (radionuclide material) intravenously by the use of venous puncture and saline solution flush upon request and direction of a licensed practitioner."

### `contrast_media_physician_presence_required` — bool
- **what:** Whether a physician or ACLS-trained personnel must be immediately available in the facility when contrast media is administered by a technologist.
- **states:** CT, MT
- **sample (MT):** "In the case of contrast media, the licensed practitioner requesting the procedure, the radiologist, or personnel trained in advanced cardiac life support must be immediately available in the facility."

### `venipuncture_authorized` — bool
- **what:** Whether licensed radiologic technologists are explicitly authorized to perform venipuncture.
- **states:** CT, MT
- **sample (CT):** "A radiologic technologist licensed by the Department of Public Health may perform venipuncture and administer medication for diagnostic procedures."

### `radiopharmaceutical_administration_authorized` — bool
- **what:** Whether nuclear medicine technologists are explicitly authorized to prepare and administer radiopharmaceuticals.
- **states:** AZ, CT, HI, KS, KY, LA, MD, MS, … (+1)
- **sample (AZ):** ""Nuclear medicine technologist" means a person who uses radiopharmaceutical agents on humans for diagnostic or therapeutic purposes."

## extra credentials and expanded scope for advanced practitioners

### `radiologist_assistant_scope_authorized_procedures` — list[str]
- **what:** Specific procedures that a radiologist assistant is explicitly authorized to perform under radiologist supervision.
- **states:** AZ, CT, MD, MS, MT
- **sample (CT):** "A radiologist assistant may perform radiologic procedures delegated by a supervising radiologist provided... In addition to those procedures that the supervising radiologist deems appropriate to be performed under personal supervision, the following procedures shall be performed under personal supervision: (A) Lumbar puncture under fluoroscopic guidance, (B) lumbar myelogram, (C) thoracic or cervical myelogram, (D) nontunneled venous central line placement, (E) venous catheter placement for dialysis, (F) breast needle localization, and (G) ductogram."

### `radiologist_assistant_prohibited_activities` — list[str]
- **what:** Activities explicitly prohibited for radiologist assistants across states.
- **states:** AZ, CT, KS, MD, MS, MT
- **sample (CT):** "A radiologist assistant shall not: (1) Interpret images, (2) make diagnoses, (3) prescribe medications or therapies, or (4) administer anesthesia."

### `radiologist_assistant_education_requirement` — str
- **what:** The specific advanced academic credential required to qualify as a radiologist assistant (e.g., baccalaureate, post-baccalaureate certificate, graduate degree with radiologist-directed clinical preceptorship).
- **states:** AZ, CT, MD, MS, MT
- **sample (AZ):** "Has obtained a baccalaureate degree or postbaccalaureate certificate from an advanced academic program that encompasses a nationally recognized radiologist assistant curriculum that includes a radiologist-directed clinical preceptorship."

### `radiologist_assistant_acls_required` — bool
- **what:** Whether current certification in advanced cardiac life support (ACLS) is required for radiologist assistant licensure.
- **states:** CT, MD
- **sample (CT):** "Holds and maintains current certification in advanced cardiac life support"

### `radiologist_assistant_malpractice_insurance_required` — bool
- **what:** Whether radiologist assistants are required to maintain professional liability insurance.
- **states:** AZ, CT
- **sample (CT):** "Each person licensed to practice as a radiologist assistant who provides direct patient care services shall maintain professional liability insurance or other indemnity against liability for professional malpractice in an amount that shall not be less than five hundred thousand dollars for one person, per occurrence, with an aggregate of not less than one million five hundred thousand dollars."

## supervision and delegation rules

### `supervising_radiologist_patient_ratio_limit` — int
- **what:** The maximum number of radiologist assistants a single supervising radiologist may concurrently supervise.
- **states:** AZ, CT
- **sample (CT):** "A licensed radiologist may function as a supervising radiologist for no more than two full-time radiologist assistants concurrently, or the part-time equivalent thereof."

### `supervision_level_definitions` — list[str]
- **what:** Named levels of supervision defined in statute (e.g., direct supervision, personal supervision, general supervision) with distinct meanings for radiologic practice.
- **states:** CT, MD, MT
- **sample (CT):** ""Direct supervision" means a radiologist must be present in the office suite and immediately available to furnish assistance and direction throughout the performance of the procedure; "Personal supervision" means a radiologist must be in attendance in the room during the performance of the procedure."

### `procedures_requiring_personal_supervision` — list[str]
- **what:** Specific high-risk procedures that must be performed under personal (in-room) supervision of the radiologist rather than merely direct supervision.
- **states:** CT, MD
- **sample (CT):** "The following procedures shall be performed under personal supervision: (A) Lumbar puncture under fluoroscopic guidance, (B) lumbar myelogram, (C) thoracic or cervical myelogram, (D) nontunneled venous central line placement, (E) venous catheter placement for dialysis, (F) breast needle localization, and (G) ductogram."

### `written_protocol_required_for_delegation` — bool
- **what:** Whether a written protocol or standing orders must be established by the supervising radiologist before delegating procedures to a radiologist assistant or technologist.
- **states:** CT, MD, MT
- **sample (CT):** "Delegated procedures shall be implemented in accordance with written protocols established by the supervising radiologist."

### `image_interpretation_prohibited` — bool
- **what:** Whether technologists (non-radiologist-assistant) are explicitly prohibited from interpreting diagnostic images for physicians, patients, or the public.
- **states:** AZ, KS, LA
- **sample (AZ):** "Has interpreted a diagnostic image for a physician, a patient, the patient's family or the public."

### `prescription_or_order_required` — bool
- **what:** Whether a prescription or written order from a licensed practitioner is required before a technologist may apply ionizing radiation.
- **states:** KS, LA, MS
- **sample (LA):** "No person holding a license under this Chapter shall use radioactive substances or equipment emitting or detecting ionizing radiation on humans for diagnostic or therapeutic purposes unless under the direction and supervision of a licensed practitioner and unless so directed by prescription of a licensed practitioner."

## specialty certifications required for specific imaging types

### `mammography_certification_required` — bool
- **what:** Whether a separate mammography-specific certification or credential is required beyond the general radiologic technologist license to perform mammography.
- **states:** AZ, CT, MD, MS
- **sample (AZ):** "A person who wishes to perform diagnostic mammography or screening mammography as defined in section 30-651 shall obtain a mammographic technologist certificate from the department."

### `computed_tomography_certification_required` — bool
- **what:** Whether a separate computed tomography (CT)-specific certification is required beyond the general radiologic technologist license to perform CT.
- **states:** AZ, CT, LA
- **sample (AZ):** "A person who wishes to perform computed tomography shall obtain a computed tomography technologist certificate from the department."

### `bone_densitometry_certification_recognized` — bool
- **what:** Whether the state recognizes a separate bone densitometry credential or permit category.
- **states:** AZ, CT
- **sample (AZ):** ""Practical technologist in bone densitometry" means a technologist who holds a certificate to apply ionizing radiation to a person's hips, spine and extremities through the use of a bone density machine."

### `fusion_technology_credential_recognized` — bool
- **what:** Whether the state recognizes a separate credential for fusion technology (e.g., PET/CT hybrid imaging) operators.
- **states:** CT, LA
- **sample (LA):** ""Fusion technologist" means a person, other than a licensed practitioner, who under the direction and supervision of a licensed practitioner applies radiation while operating fusion technology imaging equipment or uses radioactive materials on humans for diagnostic or therapeutic purposes upon prescription of a licensed practitioner."

## examination and national certification

### `national_registry_accepted_in_lieu_of_state_exam` — bool
- **what:** Whether the state accepts current certification by a recognized national body (e.g., ARRT, NMTCB) in lieu of a separate state examination.
- **states:** AZ, CT, HI, KS, KY, LA, MD, MS, … (+1)
- **sample (KS):** "The board may accept, in lieu of its own licensure examination, a current certificate by the American registry of radiologic technologists, nuclear medicine technologist certification board or other recognized national voluntary credentialing bodies."

### `national_registry_good_standing_satisfies_ce` — bool
- **what:** Whether maintaining good standing with a recognized national registry (e.g., ARRT) satisfies the state's continuing education requirement for license renewal.
- **states:** AZ, CT, HI
- **sample (AZ):** "If a radiologic technologist is certified by the American registry of radiologic technologists or nuclear medicine technology certification board, that person must satisfy the continuing education requirements of this subsection by providing the department with evidence of the technologist's good standing and current certification with that registry."

### `continuing_education_hours_vary_by_credential_tier` — bool
- **what:** Whether the required continuing education hours differ by credential tier or specialty within the same state.
- **states:** AZ, CT, MS
- **sample (AZ):** "Practical technologist in podiatry, two hours every two years. Practical technologist in radiology, six hours every two years... Radiologist assistant, fifty hours every two years. Radiologic technologist, twenty-four hours every two years."

## who is exempt from licensure

### `dental_assistant_exemption` — bool
- **what:** Whether dental assistants or dental hygienists performing dental x-rays under dentist supervision are explicitly exempt from radiologic technology licensure requirements.
- **states:** AZ, CT, HI, KS, LA, MS, MT
- **sample (CT):** "Nothing in this section shall be construed to require licensure as a radiographer or to limit the activities of a dental hygienist licensed pursuant to chapter 379a, provided such dental hygienist is engaged in the taking of dental x-rays under the general supervision of a dentist."

### `podiatric_assistant_exemption` — bool
- **what:** Whether podiatric medical assistants performing podiatric x-rays under podiatrist supervision are explicitly exempt from radiologic technology licensure.
- **states:** AZ, CT, LA, MS
- **sample (CT):** "Nothing in this section shall be construed to require licensure as a radiographer or to limit the activities of a podiatric medical assistant, provided such podiatric assistant is engaged in taking of podiatric x-rays under the supervision and control of a podiatrist."

### `chiropractic_assistant_exemption` — bool
- **what:** Whether chiropractic assistants performing x-rays under chiropractor supervision are explicitly exempt from radiologic technology licensure.
- **states:** AZ, LA, MS
- **sample (LA):** "Chiropractors' assistants certified and authorized by the Louisiana Board of Chiropractic Examiners to perform certain radiologic procedures for diagnostic purposes upon prescription of a licensed chiropractor."

### `federal_employee_exemption` — bool
- **what:** Whether persons employed by federal government agencies (e.g., military, VA, public health service) performing radiologic duties in the line of duty are exempt from state licensure.
- **states:** AZ, CT, HI, KS, KY, LA, MD, MS, … (+1)
- **sample (AZ):** "A person engaged in performing the duties of a technologist in that person's employment by an agency, bureau or division of the government of the United States."

### `special_permit_for_shortage_areas` — bool
- **what:** Whether the state may issue special or temporary permits to unlicensed persons to practice in areas with a shortage of licensed technologists.
- **states:** AZ, HI, MT
- **sample (HI):** "The board may issue special temporary permits upon request to unlicensed radiographers working in shortage areas."

### `telehealth_radiologist_exemption` — bool
- **what:** Whether a radiologist licensed in another state who provides radiology services via telehealth to patients in that other state is exempt from the state's licensure requirement.
- **states:** HI
- **sample (HI):** "A radiologist duly licensed to practice medicine and radiology services in another state who uses telehealth while located in this State to provide radiology services to a patient who is located in the state in which the radiologist is licensed."

## license status options

### `inactive_or_retired_status_available` — bool
- **what:** Whether the state provides a formal inactive or retired license status that suspends practice rights and continuing education obligations.
- **states:** AZ, CT, HI, KS, KY, LA, MD
- **sample (AZ):** "The department shall waive the renewal fee if a certificate holder submits an affidavit to the department stating that the certificate holder is retired from the practice of radiologic technology or wishes to be placed on inactive status."

### `military_fee_waiver` — bool
- **what:** Whether the state waives licensure fees for active duty military members.
- **states:** AZ, KY
- **sample (KY):** "Normal licensure fees shall be waived for persons who provide the board with documentation of active duty in the United States Armed Forces."

## practice setting and workplace rules

### `license_display_required` — bool
- **what:** Whether licensees are required to display their certificate or license at their place of employment.
- **states:** AZ, KY, MD
- **sample (AZ):** "Every technologist or special permit holder shall display a certificate or permit at the technologist's or permit holder's place of employment."

### `employer_reporting_obligation` — bool
- **what:** Whether employers (hospitals, facilities) are required to report disciplinary actions or violations involving licensed technologists to the regulatory board.
- **states:** AZ, CT, MD
- **sample (AZ):** "A person or facility that employs a person certified under this section shall report any suspected violations of section 32-2821 to the department."

### `logbook_or_record_inspection_authorized` — bool
- **what:** Whether the regulatory authority is explicitly empowered to inspect ionizing radiation logbooks or audit records at practice sites.
- **states:** AZ, MS
- **sample (AZ):** "Auditing ionizing radiation logbooks."

### `mammography_physician_reader_requirements` — bool
- **what:** Whether the state imposes specific education or board certification requirements on physicians who read or interpret mammographic images.
- **states:** AZ, MD
- **sample (AZ):** "A physician licensed under chapter 13 or 17 of this title who reads or interprets mammographic images shall meet the following requirements: 1. Have completed forty hours of medical education credits in mammography. 2. Be certified by either the American board of radiology in diagnostic radiology or the American osteopathic board of radiology in diagnostic radiology."
