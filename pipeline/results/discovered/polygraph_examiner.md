# Discovered fields — polygraph_examiner

## instrument and measurement standards

### `instrument_physiological_channels_required` — list[str]
- **what:** The specific physiological channels that the polygraph instrument must record simultaneously as a minimum statutory requirement.
- **states:** AL, AR, IL, IN, KY, LA, ME, MS, … (+2)
- **sample (IL):** "Every polygraph examiner shall use an instrument which records permanently and simultaneously the subject's cardiovascular, respiratory and galvanic skin response patterns as minimum standards."

### `additional_physiological_channels_permitted` — bool
- **what:** Whether the statute explicitly permits recording physiological channels beyond the required minimum.
- **states:** AL, AR, IL, KY, LA, ME, MS, NV, … (+1)
- **sample (MS):** "Patterns of other physiological changes in addition to (1) and (2) may also be recorded."

### `instrument_approval_required` — bool
- **what:** Whether the instrument used must be of a type formally approved by the licensing authority before use.
- **states:** AL, NV, OK
- **sample (NV):** "Each instrument used to conduct a polygraphic examination must be of a type approved by the Board."

### `voice_stress_analysis_regulated` — bool
- **what:** Whether the state separately regulates voice stress analysis as a distinct licensed activity alongside polygraph examination.
- **states:** AR, IL
- **sample (AR):** "'Voice stress analysis examiner' means an individual who has been trained in the operation of a voice stress analysis machine and who maintains a current certificate from a recognized training facility."

## approved training school requirements

### `polygraph_school_minimum_classroom_hours` — int
- **what:** Minimum number of classroom hours a polygraph examiner school must offer to be recognized by the state authority.
- **states:** KY, LA
- **sample (KY):** "In order to be recognized as an accepted training institution for detection of deception examiners by the cabinet, a polygraph examiner's school must offer at least two hundred and forty (240) hours of classroom training and instruction."

### `polygraph_school_required_subjects` — list[str]
- **what:** Subjects that an approved polygraph examiner school curriculum must include.
- **states:** KY, LA
- **sample (KY):** "Instrumentation of the instrument prescribed in KRS 329.020; Psychology; Physiology; Question formulation; Chart interpretation; Interrogation; History and legal ethics of the polygraph; Supervised practice examinations."

## alternative pathways to licensure

### `alternative_qualification_law_enforcement_experience` — bool
- **what:** Whether active law enforcement or investigative experience may substitute for the baccalaureate degree requirement.
- **states:** AL, AR, IL, LA, ME, MS, NV, OK
- **sample (AR):** "Holds a baccalaureate degree from a college or university that is accredited by an accrediting agency approved by the United States Secretary of Education or has at least five (5) consecutive years of active law enforcement experience."

### `alternative_qualification_experience_years` — int
- **what:** Number of years of investigative or law enforcement experience accepted in lieu of a baccalaureate degree.
- **states:** AL, AR, IL, ME, MS, NV, OK
- **sample (AR):** "Has five (5) consecutive years of active law enforcement experience."

### `federal_military_training_reciprocity` — bool
- **what:** Whether completion of a federal government or military polygraph training program (e.g., Defense Academy for Credibility Assessment) qualifies an applicant for licensure without the standard state requirements.
- **states:** IL, ME
- **sample (IL):** "Certification, if applicable, that the applicant has successfully completed the Defense Academy for Credibility Assessment course, or its predecessor or successor course."

## financial responsibility requirements

### `surety_bond_or_insurance_required` — bool
- **what:** Whether applicants must furnish a surety bond or liability insurance policy as a condition of licensure.
- **states:** AL, AR, IN, LA, MS, NV
- **sample (AL):** "Prior to the issuance of a license, the applicant must furnish to the board evidence of a surety bond or insurance policy in an amount to be determined by the board."

### `surety_bond_minimum_amount` — int
- **what:** Minimum dollar amount of the required surety bond or insurance policy.
- **states:** AR, MS
- **sample (AR):** "The surety bond or insurance policy shall be in the sum of five thousand dollars ($5,000)."

### `law_enforcement_employer_bond_exemption` — bool
- **what:** Whether examiners employed by a law enforcement agency may substitute an agency coverage letter for the individual surety bond requirement.
- **states:** AR, NV
- **sample (AR):** "An applicant who is conducting a polygraph examination solely in the course of his or her employment with a law enforcement agency may submit a letter from the county sheriff, municipal chief of police, or director of a state agency that states that any liability incurred will be covered under that entity's membership in the Fidelity Bond Trust Fund."

## exemptions from licensure

### `government_examiner_license_exemption` — bool
- **what:** Whether persons conducting polygraph examinations solely in the course of official duties for a government law enforcement or investigative agency are exempt from the licensing requirement.
- **states:** IL, ME, NV
- **sample (NV):** "A license as a polygraphic examiner or intern is not required under this chapter of a person who conducts polygraphic examinations solely in the performance of official duties for a federal, state, county or municipal law enforcement or investigative agency."

### `government_fee_exemption` — bool
- **what:** Whether government agencies or their examiner-employees are exempt from paying licensure fees.
- **states:** AR, KY
- **sample (KY):** "Subsection (1) of KRS 329.030 ... relating to fees charged applicants for a license, shall not apply to any department of the United States or any agency of the city, county or state, provided that no fee is charged for administration of the test."

## subject rights and examination conduct rules

### `subject_informed_consent_required` — bool
- **what:** Whether the examiner is required to obtain the subject's informed consent before conducting an examination.
- **states:** AL, AR, IL, KY, LA, ME, MS, NV, … (+1)
- **sample (NV):** "A polygraphic examination must not be conducted unless the person examined consents to it in writing."

### `subject_voluntary_participation_disclosure_required` — bool
- **what:** Whether the examiner must inform the subject that participation in the examination is voluntary before proceeding.
- **states:** AL, AR, KY, LA, ME, MS, NV, OK
- **sample (OK):** "For failing to inform a subject to be examined that his participation in the examination is voluntary."

### `subject_results_disclosure_on_request_required` — bool
- **what:** Whether the examiner must disclose the examination results to the subject upon request.
- **states:** AL, AR, IL, KY, LA, ME, MS, NV, … (+1)
- **sample (IL):** "An examiner shall, upon written request of a person examined, make known the results of such test to the person examined within 5 days of receipt of the written request."

### `minor_parental_consent_required` — bool
- **what:** Whether written parental or guardian consent is required before administering a polygraph examination to a minor.
- **states:** ME, NV
- **sample (ME):** "Administer a polygraph examination to a minor without the written consent of a parent of the minor or the minor's legal guardian."

### `prohibited_question_topics` — list[str]
- **what:** Categories of questions that examiners are prohibited from asking during an examination (absent specific exceptions).
- **states:** IL, ME, NV
- **sample (IL):** "No Examiner shall inquire into any of the following areas during pre-employment or periodic employment examinations, unless the area is directly related to employment: (1) Religious beliefs or affiliations; (2) Beliefs or opinions regarding racial matters; (3) Political beliefs or affiliations; (4) Beliefs, affiliations or lawful activities regarding unions or labor organizations; or (5) Sexual preferences or activity."

### `right_to_refuse_incriminating_questions` — bool
- **what:** Whether the examiner must advise the subject of the right to refuse to answer questions that would tend to incriminate or degrade the person.
- **states:** LA, NV
- **sample (NV):** "An examiner or intern shall, before beginning a polygraphic examination, inform the person examined that he or she has the right to refuse to answer any questions if the answer would tend to incriminate or degrade the person."

### `waiver_of_liability_by_subject_prohibited` — bool
- **what:** Whether the statute prohibits requiring the subject to sign a waiver limiting the examiner's liability, and voids any such waiver.
- **states:** MS, NV
- **sample (NV):** "A person shall not request any person examined to sign a waiver limiting the liability of the examiner or intern. Any such waiver is void."

## employment use restrictions

### `preemployment_polygraph_prohibited` — bool
- **what:** Whether the state prohibits employers from requiring or using polygraph examinations as a condition of employment or hiring.
- **states:** LA, ME
- **sample (ME):** "An employer may not, directly or indirectly, require, request or suggest that an applicant for employment submit to a polygraph examination as a condition of obtaining employment."

### `preemployment_polygraph_law_enforcement_exception` — bool
- **what:** Whether law enforcement agencies are explicitly excepted from the prohibition on pre-employment polygraph screening.
- **states:** IL, ME
- **sample (ME):** "This section does not apply to employees of or applicants for employment with law enforcement agencies or county and regional communications centers."

### `contingency_fee_prohibited` — bool
- **what:** Whether accepting a fee contingent upon the outcome of a polygraphic examination is prohibited.
- **states:** MS, NV
- **sample (NV):** "Accepted a fee contingent upon the outcome of a polygraphic examination."

## legal status of examination results

### `examination_results_inadmissible_in_court` — bool
- **what:** Whether the statute explicitly provides that polygraph examination results may not be introduced or admitted as evidence in a court of law.
- **states:** AL, ME, MS
- **sample (AL):** "Nothing in this chapter shall be construed as permitting the results of truth examinations or polygraph examinations to be introduced or admitted as evidence in a court of law."

### `examination_results_admissibility_conditions` — str
- **what:** Conditions under which polygraph examination results may be considered or accepted into evidence, where the statute provides a qualified rather than absolute rule.
- **states:** ME, NV
- **sample (NV):** "In any matter involving the well-being, employment or liability of a person, another person shall not consider or accept into evidence an opinion resulting from a polygraphic examination unless the examination meets the minimum standards established by this chapter and was administered by a person who holds a valid license."

## record-keeping and confidentiality

### `examination_records_retention_required` — bool
- **what:** Whether examiners are required by statute to maintain records of examinations for a specified minimum period.
- **states:** LA, NV
- **sample (NV):** "The records of a polygraphic examination, including the written consent of the person examined, the questions asked, notes and charts obtained during the examination, must be maintained in a manner which protects their confidentiality by the examiner or intern or his or her employer, for a period of not less than 3 years."

### `examination_records_minimum_retention_years` — int
- **what:** Minimum number of years that examination records must be retained.
- **states:** LA, NV
- **sample (LA):** "These records must be kept for at least a one year period from the date of the original examination."

### `examination_results_confidentiality_required` — bool
- **what:** Whether the statute imposes a duty of confidentiality on examination results and related records, restricting disclosure to specified persons.
- **states:** ME, MS, NV
- **sample (ME):** "A polygraph examiner may not disclose information acquired from a polygraph examination, or records resulting from a polygraph examination, to another person other than [specified persons]."

### `mandatory_reporting_duty` — bool
- **what:** Whether the examiner has a statutory duty to report to a government agency when the examination reveals imminent danger to a child or other specified person.
- **states:** ME, NV
- **sample (ME):** "Immediately report to the Department of Health and Human Services when the examiner knows or has reasonable cause to suspect that a person 14 years of age or younger will be the victim of a sexual assault crime or is in imminent danger of substantial bodily injury or death."

### `chronological_examination_log_required` — bool
- **what:** Whether examiners are required to maintain a chronological log of all examinations administered.
- **states:** LA, NV
- **sample (NV):** "Each examiner or intern shall maintain a chronological log of all polygraphic examinations which he or she administers. The log must include the date of each examination, the name of the person examined, and an identifying case or file number."

## supervision and internship conduct

### `examiner_trainee_ratio_limit` — int
- **what:** Maximum number of trainees or interns a licensed examiner may supervise simultaneously.
- **states:** AR, KY
- **sample (KY):** "No examiner may have more than two (2) trainees under his or her supervision and control at any one (1) time."

### `supervisor_experience_requirement_for_trainee_oversight` — str
- **what:** Minimum experience a licensed examiner must have before being permitted to supervise a trainee.
- **states:** AL, KY
- **sample (KY):** "Before an examiner may supervise a trainee, he or she must have at least two (2) years' experience in detection of deception."

### `examination_technique_standards_required` — bool
- **what:** Whether the statute mandates that examiners use only standard and widely accepted examination techniques, including pre-test question review with the subject.
- **states:** ME, NV
- **sample (NV):** "In conducting a polygraphic examination, an examiner or intern shall use only standard and widely accepted techniques based on comparison of the reaction to relevant questions and to questions asked as a control or techniques based on comparison of peaks of tension. All questions used during the examination must be reviewed with the person examined before being used."

### `minimum_charts_before_opinion` — int
- **what:** Minimum number of polygraph charts an examiner must administer before rendering a written or oral opinion.
- **states:** ME, NV
- **sample (NV):** "An examiner or intern shall not render a written or oral opinion based upon his or her analysis of polygraphic charts without administering two or more charts with the same questions on at least two of the charts."

## governing board structure

### `board_composition_law_enforcement_seats` — int
- **what:** Minimum number of board seats reserved for polygraph examiners from governmental law enforcement agencies.
- **states:** AL, LA, ME, MS, OK
- **sample (AL):** "Three of the board members shall be qualified polygraph examiners of a governmental law enforcement agency."

### `board_composition_commercial_seats` — int
- **what:** Minimum number of board seats reserved for polygraph examiners working in the commercial (non-law-enforcement) field.
- **states:** AL, LA, ME, MS, OK
- **sample (AL):** "Two of the board members shall be qualified polygraph examiners and Alabama residents in the commercial field."

### `board_public_member_required` — bool
- **what:** Whether the governing board must include at least one member representing the general public who is not a polygraph examiner.
- **states:** ME, NV
- **sample (ME):** "One member who represents the public."
