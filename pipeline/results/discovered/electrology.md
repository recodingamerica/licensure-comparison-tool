# Discovered fields — electrology

## what the procedure involves and how it works

### `hair_removal_modalities_authorized` — list[str]
- **what:** The specific electrical or physical modalities authorized for permanent hair removal, such as galvanic, thermolysis, or blend.
- **states:** CA, CT, FL, HI, ID, IL, KS
- **sample (IL):** ""Electrology" means the practice or teaching of services for permanent hair removal utilizing only solid probe electrode type epilation, which may include thermolysis (shortwave, high frequency), electrolysis (galvanic), or a combination of both (superimposed or sequential blend)."

### `needle_penetration_required` — bool
- **what:** Whether the statutory definition requires physical penetration of the skin by a needle or probe (distinguishing electrology from non-penetrating light-based hair removal).
- **states:** CA, DE, HI, IL, IN, KS
- **sample (HI):** ""Electrologist" means any person who removes hair from the human body using a needle inserted in the hair follicle and uses direct electric current or shortwave alternating current to destroy the follicle but does not include any hair removal system that does not penetrate the skin."

### `fda_device_clearance_required` — bool
- **what:** Whether the statute requires that equipment and devices used for electrolysis be cleared by and registered with the U.S. Food and Drug Administration.
- **states:** FL, ID
- **sample (FL):** ""Electrolysis or electrology" means the permanent removal of hair by destroying the hair-producing cells of the skin and vascular system, using equipment and devices approved by the board which have been cleared by and registered with the United States Food and Drug Administration."

### `laser_prohibited` — bool
- **what:** Whether the statute explicitly prohibits electrologists from using laser technology in their practice.
- **states:** CA, IL
- **sample (IL):** "Services involving laser technology may only be performed if they are delegated by a physician licensed to practice medicine in all its branches consistent with Section 20 of this Act and the Medical Practice Act of 1987."

## who oversees the profession

### `governing_board_type` — enum[standalone electrology board, cosmetology board, board of medicine, department of health, department of consumer affairs]
- **what:** The type of regulatory body that has primary authority over electrology licensure and discipline.
- **states:** AR, CA, CT, DE, FL, HI, ID, IL, … (+2)
- **sample (FL):** "There is created the Electrolysis Council under the supervision of the board [Board of Medicine]."

### `board_includes_physician_member` — bool
- **what:** Whether the governing board or advisory council is required to include a licensed physician (often a dermatologist) as a member.
- **states:** CT, FL
- **sample (CT):** "There shall be in the department a Board of Examiners of Electrologists, composed of five members, one of whom shall be a doctor of medicine licensed to practice medicine and surgery in the state and a diplomate of the American Board of Dermatology."

## education and training before you can practice

### `training_hours_required` — int
- **what:** The minimum number of clock hours of electrology-specific training required for initial licensure.
- **states:** AR, CA, DE, FL, ID, IL, KS
- **sample (IL):** "Has completed a total of 600 hours in the study of electrology over a period of not less than 16 weeks nor more than 4 consecutive years at a program approved by the Department."

### `training_pathway_options` — list[str]
- **what:** The recognized pathways through which an applicant may satisfy pre-licensure training requirements (e.g., school program, apprenticeship, out-of-state practice).
- **states:** AR, CA, DE, ID, IN, KS
- **sample (ID):** "As an electrologist, must have: (i) Completed and graduated from a course of instruction of at least six hundred (600) hours in a school approved by the board; or (ii) Completed at least one thousand two hundred (1,200) hours as an apprentice in a cosmetology establishment under the direct personal supervision of a licensed electrologist instructor."

### `cosmetology_license_prerequisite` — bool
- **what:** Whether the applicant must hold a cosmetology or esthetician license as a prerequisite to obtaining an electrologist license.
- **states:** AR, IN
- **sample (IN):** "The application described in section 2 of this chapter must state that the applicant: (1) holds a cosmetologist license issued under IC 25-8-9 or an esthetician license issued under IC 25-8-12.5."

## examination requirements

### `national_exam_accepted` — bool
- **what:** Whether the state may accept or waive its own written examination in favor of a nationally recognized electrology examination.
- **states:** CT, DE, FL
- **sample (CT):** "The department may waive the written examination for a person who has passed the written examination of a nationally recognized board or agency approved by the department and the board."

### `exam_components` — list[str]
- **what:** The required components of the licensure examination (e.g., written, practical/clinical, oral).
- **states:** AR, CT, DE, FL, ID, KS
- **sample (CT):** "No person shall receive a license, except as provided in this section, until such person has passed a written, oral and practical examination prescribed by the department with the advice and consent of the board."

## keeping your license active

### `continuing_education_hours_per_period` — int
- **what:** The number of continuing education hours required per renewal period for electrologists.
- **states:** CT, FL, IL
- **sample (IL):** "All renewal applicants shall provide proof of having met the continuing education requirements in accordance with rules established by the Department, consisting of the equivalent of 30 hours of continuing education every 24 months."

### `continuing_education_bloodborne_pathogens_required` — bool
- **what:** Whether continuing education must specifically include training on blood-borne diseases or pathogens.
- **states:** AR, FL
- **sample (FL):** "An application for license renewal must be accompanied by proof of the successful completion of 20 hours of continuing education courses... Both the continuing education and reexamination shall contain education on blood-borne diseases."

## where you can practice and facility rules

### `facility_license_required` — bool
- **what:** Whether a separate license is required for the physical facility or establishment where electrolysis is performed, in addition to the individual practitioner license.
- **states:** AR, CA, DE, FL, ID, KS
- **sample (FL):** "No electrology facility shall be permitted to operate without a facility license issued by the department."

### `practice_outside_licensed_facility_allowed` — bool
- **what:** Whether the statute explicitly permits a licensed electrologist to practice outside a licensed establishment under specified conditions (e.g., at a patient's home, healthcare facility).
- **states:** AR, DE, ID, KS
- **sample (ID):** "A licensed electrologist practicing electrology or a licensed esthetician practicing esthetics under the supervision of a licensed chiropractor, dentist, medical doctor, nurse practitioner or podiatrist at a facility used by the supervising individual."

## supervision and temporary practice

### `supervision_of_temporary_permittee_required` — bool
- **what:** Whether a person holding a temporary or provisional permit to practice electrology must do so under the supervision of a licensed electrologist.
- **states:** FL, ID, IN
- **sample (FL):** "As used in subsection (2), 'supervision' means responsible control by a licensed electrologist who provides the initial direction in developing a treatment plan and also periodically inspects the permittee's implementation of such plan."

### `physician_supervision_exemption` — bool
- **what:** Whether the statute exempts from licensure requirements persons practicing electrology under the direct supervision or direction of a licensed physician.
- **states:** CT, FL, ID, IL
- **sample (CT):** "Nor shall this chapter prohibit the practice of electrology by a person licensed to practice the healing arts or a person employed in a hospital or in the office of a licensed physician under such physician's immediate direction."

## teaching and schools

### `instructor_license_required` — bool
- **what:** Whether a separate instructor license is required to teach electrology in a licensed school or clinic.
- **states:** AR, CA, DE, ID, IN, KS
- **sample (KS):** "Any person who teaches electrology in a licensed school of cosmetology or electrology shall be required to obtain an electrology instructor's license from the board."

### `instructor_experience_years_required` — int
- **what:** The minimum number of years of licensed practice as an electrologist required before a person may qualify as an electrology instructor.
- **states:** AR, ID, KS
- **sample (AR):** "Has had three (3) years of practical experience as an electrologist in the State of Arkansas within the past five (5) years."

### `clinic_apprenticeship_teaching_allowed` — bool
- **what:** Whether a licensed electrologist who owns or manages a clinic or establishment may teach an apprentice in that setting without operating a licensed school, subject to limits on the number of apprentices.
- **states:** AR, KS
- **sample (KS):** "Nothing in this act shall prohibit any person who is a licensed electrologist, while acting as owner and manager of the person's clinic or establishment, from teaching electrology in the regular course of the person's business, but at no time shall any clinic or establishment have more than one apprentice or charge tuition for its teaching services."

## professional titles and identity

### `protected_title_abbreviations` — list[str]
- **what:** Specific titles or abbreviations that only licensed electrologists are permitted to use.
- **states:** CT, FL, HI, IL
- **sample (FL):** "Only persons who are licensed under this chapter may use the title 'Electrologist,' 'Registered Electrologist,' or the abbreviation 'RE.'"

### `certified_professional_electrologist_title_allowed` — bool
- **what:** Whether the statute explicitly permits a licensee to use the title 'Certified Professional Electrologist' (CPE) if awarded by a recognized national certification body.
- **states:** CT
- **sample (CT):** "Such licensee may use the title 'certified professional electrologist' or its abbreviation 'CPE', provided such licensee has been awarded certification by the international board of electrologist certification of The American Electrology Association."

## drugs and anesthesia

### `anesthesia_and_medication_authority` — str
- **what:** The statutory treatment of an electrologist's authority or restrictions regarding use of topical anesthetics, anesthetic injections, or other medications in connection with electrolysis.
- **states:** FL, HI, IL
- **sample (HI):** "The department pursuant to chapter 91, may adopt rules as it deems necessary for the public health or safety relating to, but not limited to: ... (3) The use of anesthetic injections, topical anesthetics, other medications, and prescription drugs."

## patient safety and referral obligations

### `abnormal_skin_growth_education_required` — bool
- **what:** Whether the statute requires electrologists to complete training in identifying abnormal skin growths, including melanoma, as a condition of licensure or renewal.
- **states:** IL
- **sample (IL):** "In addition to any other requirements under this Act, the following applicants must provide proof of completion of a course approved by the Department in abnormal skin growth education, including training on identifying melanoma."

### `referral_obligation_to_physician` — bool
- **what:** Whether the statute requires an electrologist to refer a client to a licensed physician when the client's condition is beyond the electrologist's scope of practice.
- **states:** FL, IL
- **sample (IL):** "An electrologist shall refer to a licensed physician any individual whose condition, at the time of evaluation or service, is determined to be beyond the scope of practice of the electrologist, such as an individual with signs of infection or bleeding."
