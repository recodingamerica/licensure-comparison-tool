# Discovered fields — applied_behavior_analysis

## license tiers and credential levels

### `tiered_license_levels` — list[str]
- **what:** The distinct license tiers recognized by the state for this profession, ranging from full behavior analyst to assistant and temporary levels.
- **states:** AK, AL, CT, GA, HI, IL, IN, KS, … (+1)
- **sample (AK):** "The department shall issue a license to practice as an assistant behavior analyst to a person who... provides proof acceptable to the department that the person is directly supervised by a licensed behavior analyst."

### `national_certification_body` — str
- **what:** The nationally recognized certifying entity whose certification is required or accepted as the basis for state licensure.
- **states:** AK, AL, AZ, CT, GA, HI, IL, IN, … (+2)
- **sample (GA):** "Certifying entity means the Behavior Analyst Certification Board, Inc., or its successor, or another entity that conducts programs to certify professional practitioners of behavior analysis that are accredited by the National Commission on Certifying Agencies or the American National Standards Institute."

### `national_certification_required_for_licensure` — bool
- **what:** Whether holding active national certification (e.g., BCBA or BCaBA) is a prerequisite for obtaining or renewing a state license.
- **states:** AK, AL, GA, HI, IN, KS, KY
- **sample (KS):** "The board shall not issue a license under this act until the license applicant provides proof that such applicant has met the certification requirements of a certifying entity."

### `doctoral_tier_recognized` — bool
- **what:** Whether the state explicitly recognizes a doctoral-level behavior analyst credential (BCBA-D) as a distinct or equivalent credential for licensure.
- **states:** GA, HI, IL
- **sample (HI):** "Maintains active status with the Behavior Analyst Certification Board as a board certified behavior analyst or board certified behavior analyst-doctoral."

## supervision and delegation

### `assistant_analyst_supervision_requirement` — str
- **what:** The requirement that a licensed assistant behavior analyst practice only under the supervision of a licensed behavior analyst, including any specifics about supervision format.
- **states:** AK, AL, GA, HI, IL, IN, KS, KY
- **sample (IN):** "An individual who is licensed as an assistant behavior analyst under this section must be directly supervised by a behavior analyst licensed under this chapter and must submit to the committee a written record of the supervision provided."

### `supervisee_technician_exemption` — bool
- **what:** Whether the statute explicitly exempts paraprofessionals or direct-contact technicians who implement (but do not design) ABA services under a licensed analyst's supervision from licensure requirements.
- **states:** AK, AL, GA, HI, IL, IN, KY
- **sample (GA):** "A behavior technician who delivers applied behavior analysis services under the extended authority, close and ongoing supervision, and responsibility of a licensed behavior analyst or a licensed assistant behavior analyst. Such individuals shall not represent themselves as professional behavior analysts."

### `family_member_caregiver_exemption` — bool
- **what:** Whether family members or caregivers implementing a behavior analysis plan under a licensed analyst's direction are explicitly exempt from licensure.
- **states:** AK, AL, CT, GA, HI, IL, IN, KY
- **sample (AK):** "A family member implementing a behavior analysis plan within the home, who acts under the direction of a licensed behavior analyst or licensed assistant behavior analyst."

### `max_supervisees_per_analyst` — str
- **what:** Any statutory or regulatory limit on the number of supervisees or temporary licensees a licensed behavior analyst may supervise simultaneously.
- **states:** KS, KY
- **sample (KY):** "Establishing the number of persons a licensed behavior analyst may supervise at one (1) time, including temporary licensees and supervisees."

## temporary and out-of-state practice

### `temporary_license_available` — bool
- **what:** Whether the state offers a temporary license for out-of-state practitioners providing services for a limited period.
- **states:** AK, AL, GA, KY
- **sample (AK):** "The department may issue a temporary license to practice behavior analysis in this state for 30 days or less in a calendar year if the person is licensed to practice behavior analysis in another state whose requirements to practice behavior analysis are substantially equivalent."

### `temporary_license_max_days_per_year` — int
- **what:** The maximum number of days per calendar year an out-of-state practitioner may practice under a temporary license.
- **states:** AK, GA, IN
- **sample (GA):** "A temporary behavior analysis license may be issued only if the behavior analysis services are to be delivered during a limited and defined period of not more than a total of 30 days within a calendar year."

## practice setting and population exemptions

### `school_setting_exemption` — bool
- **what:** Whether individuals employed by schools or school districts to deliver behavior analytic services in educational settings are exempt from licensure requirements.
- **states:** GA, HI, IL, KS, KY
- **sample (GA):** "An individual employed by a local board of education performing the duties of their positions; provided, however, that such individuals shall not represent themselves as licensed behavior analysts or licensed assistant behavior analysts."

### `medicaid_waiver_services_exemption` — bool
- **what:** Whether individuals providing services under Medicaid home- and community-based services waiver programs are explicitly exempt from licensure.
- **states:** GA, HI, KS, KY
- **sample (GA):** "Individuals providing behavior support services covered under the Medicaid Comprehensive Supports Waiver Program (COMP) or New Options Waiver (NOW) program."

### `organizational_behavior_management_exemption` — bool
- **what:** Whether practitioners providing ABA services exclusively to organizations (not individuals) or working in organizational behavior management are exempt from licensure.
- **states:** AK, AL, GA, HI, IL, IN
- **sample (GA):** "An individual who provides general applied behavior analysis services to organizations, so long as those services are for the benefit of the organizations and do not involve direct services to individuals."

### `nonhuman_animal_behaviorist_exemption` — bool
- **what:** Whether applied animal behaviorists or others practicing exclusively with nonhuman subjects are exempt from licensure.
- **states:** AK, AL, GA, HI, IL, IN
- **sample (AK):** "An applied animal behaviorist who practices exclusively with nonhumans."

### `researcher_educator_exemption` — bool
- **what:** Whether individuals who teach behavior analysis or conduct research without providing direct clinical services are exempt from licensure.
- **states:** GA, IL, KS
- **sample (GA):** "Individuals who teach behavior analysis or conduct behavior analysis research, provided that such teaching or research does not involve the direct delivery of applied behavior analysis services."

## what this profession cannot do

### `scope_exclusions` — list[str]
- **what:** Modalities or activities explicitly excluded from the statutory definition of behavior analysis practice.
- **states:** AK, AL, CT, GA, HI, IL, IN, KY
- **sample (HI):** "The practice of applied behavior analysis expressly excludes psychological testing, diagnosis of a mental or physical disorder, neuropsychology, psychotherapy, cognitive therapy, sex therapy, psychoanalysis, hypnotherapy, and long-term counseling as treatment modalities."

### `prescribing_medical_diagnosis_prohibited` — bool
- **what:** Whether the statute explicitly prohibits licensed behavior analysts from prescribing drugs, making medical diagnoses, or providing medical treatment.
- **states:** AL, HI, KY
- **sample (AL):** "Nothing in this chapter shall be construed as permitting or allowing a licensed behavior analyst to prescribe or administer any drug, make a medical diagnosis, provide medical treatment, or manage a medical condition."

## target populations and conditions

### `autism_spectrum_disorder_focus` — bool
- **what:** Whether the statute specifically references autism spectrum disorder as a primary population or condition addressed by licensed behavior analysts.
- **states:** AL, KS, KY
- **sample (KY):** "Design, implement, evaluate, and modify treatment programs to change the behavior of individuals diagnosed with an autism spectrum disorder."

### `autism_service_provider_designation` — bool
- **what:** Whether the statute formally designates licensed behavior analysts as 'autism service providers' with associated insurance or regulatory implications.
- **states:** KS, KY
- **sample (KS):** "'Autism service provider' means any person that provides diagnostic or treatment services for autism spectrum disorders who is licensed or certified by the state of Kansas; or who is licensed by the behavioral sciences regulatory board as a licensed behavior analyst or a licensed assistant behavior analyst."

## service delivery methods

### `telehealth_authorized` — bool
- **what:** Whether the statute explicitly authorizes or regulates the delivery of applied behavior analysis services via telehealth or electronic media.
- **states:** KS, KY
- **sample (KY):** "A treating behavior analyst or assistant behavior analyst who provides or facilitates the use of telehealth, shall ensure that the informed consent of the patient... is obtained before services are provided through telehealth."

### `informed_consent_required` — bool
- **what:** Whether the statute explicitly requires a licensed behavior analyst to obtain informed consent from the patient or authorized decision-maker before providing services.
- **states:** IL, KY
- **sample (KY):** "A treating behavior analyst or assistant behavior analyst who provides or facilitates the use of telehealth, shall ensure that the informed consent of the patient, or another appropriate person with authority to make the health-care treatment decision for the patient, is obtained before services are provided."

## practice setting and facility rules

### `business_entity_license_requirement` — bool
- **what:** Whether the statute requires that business organizations providing ABA services employ only licensed practitioners and be organized under specific corporate structures.
- **states:** IL, KY
- **sample (IL):** "No business organization shall provide, attempt to provide, or offer to provide behavior analysis services unless every member, partner, shareholder, director, officer, holder of any other ownership interest, agent, and employee who renders applied behavior analysis services holds a currently valid license issued under this Act."

## applicant screening and background checks

### `criminal_background_check_required` — bool
- **what:** Whether applicants for licensure are required to submit to a criminal background check, including fingerprinting.
- **states:** AK, AL, GA, IL, IN
- **sample (AK):** "Has been fingerprinted and has provided the fees required by the Department of Public Safety under AS 12.62.160 for criminal justice information and a national criminal history record check."

### `fingerprint_submission_required` — bool
- **what:** Whether applicants must submit fingerprints specifically (as opposed to a general background check authorization) as part of the licensure process.
- **states:** AK, AL, GA, IL
- **sample (IL):** "Each applicant for licensure as a behavior analyst shall have his or her fingerprints submitted to the Illinois State Police in an electronic format that complies with the form and manner for requesting and furnishing criminal history record information."

### `mandatory_reporting_of_disciplinary_actions` — bool
- **what:** Whether licensees are required to report disciplinary actions taken against them in other jurisdictions or by the national certifying body to the state licensing authority.
- **states:** HI, IN, KY
- **sample (HI):** "Failing to report in writing to the director any disciplinary decision issued against the licensee or applicant in another jurisdiction within thirty days of the disciplinary decision."

## professional conduct standards

### `ethical_code_compliance_required` — bool
- **what:** Whether compliance with a specified professional and ethical code (typically the BACB's) is an explicit statutory requirement for licensure and continued practice.
- **states:** AK, AL, GA, HI, IN, KS, KY
- **sample (IN):** "An individual who is licensed under this chapter shall comply with the requirements of the Professional and Ethical Compliance Code for Behavior Analysts published by the Behavior Analyst Certification Board, Inc."

### `suicide_prevention_training_required` — bool
- **what:** Whether the state mandates specific training in suicide prevention or mental health screening as a condition of license renewal.
- **states:** CT
- **sample (CT):** "Completing not less than two hours of training or education... on (A) screening for post-traumatic stress disorder, risk of suicide, depression and grief, and (B) suicide prevention training, during the first renewal period and not less than once every six years thereafter."

## governing board structure

### `advisory_board_composition` — str
- **what:** The statutory composition of the licensing or advisory board, including the number and types of members (e.g., behavior analysts, public members, psychologists, parents).
- **states:** AL, AZ, GA, IL, IN, KY
- **sample (KY):** "The board shall consist of seven (7) members appointed by the Governor... Four (4) members shall be licensed behavior analysts... One (1) member shall be a psychologist licensed in the state... Two (2) members shall be the parent of a child diagnosed with and treated for a behavior disorder."

### `board_includes_parent_consumer_member` — bool
- **what:** Whether the licensing or advisory board is required to include a parent of a person with a behavior disorder or a consumer/public member with lived experience.
- **states:** AL, GA, KY
- **sample (KY):** "Two (2) members shall be the parent of a child diagnosed with and treated for a behavior disorder, including but not limited to an autism spectrum disorder, selected from the state at large."

### `board_includes_psychologist_member` — bool
- **what:** Whether the licensing or advisory board is required to include a licensed psychologist as a member.
- **states:** AL, IN, KY
- **sample (KY):** "One (1) member shall be a psychologist licensed in the state, the majority of whose practice is related to the treatment of behavior disorders."
