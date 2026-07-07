# Discovered fields — alcohol_drug_counseling

## license types and credential levels

### `credential_tiers` — list[str]
- **what:** The distinct credential levels or tiers available within the profession, ranging from technician/associate through independent clinical practice.
- **states:** AR, AZ, CO, CT, FL, IN, KS
- **sample (AZ):** "Licensed addiction technician; licensed associate addiction counselor; licensed independent addiction counselor"

### `independent_practice_allowed` — bool
- **what:** Whether the credential tier authorizes independent (unsupervised) practice of addiction or alcohol/drug counseling.
- **states:** AR, AZ, CO, CT, IL, IN, KS
- **sample (KS):** "Licensed clinical addiction counselor means a person who engages in the independent practice of addiction counseling"

### `specialty_designation_available` — bool
- **what:** Whether the statute provides for specialty designations or endorsements that can be added to a base license upon meeting additional requirements.
- **states:** AL, AR, KS
- **sample (AL):** "A specialty designation may be added upon demonstration to the board that the applicant has met the recognized minimum standards as established by nationally recognized certification agencies."

### `national_certification_accepted_for_licensure` — bool
- **what:** Whether holding a recognized national certification can substitute for or satisfy part of the state licensure requirements.
- **states:** AR, IL, IN, KS
- **sample (IL):** "Any person who has received certification by any State or national organization whose standards are accepted by the Department as being substantially similar to the standards in this Act may apply for a professional counselor license and need not be examined further."

### `student_temporary_license_available` — bool
- **what:** Whether the state offers a student or pre-degree temporary license or permit allowing individuals still completing educational requirements to practice under supervision.
- **states:** AL, FL, IN, KS
- **sample (KS):** "A person may apply to the board for a student temporary addiction counselor license to practice as a student temporary addiction counselor"

## supervision and delegation

### `supervision_required_for_tier` — bool
- **what:** Whether the credential tier requires practice under direct supervision of a higher-credentialed professional.
- **states:** AL, AR, AZ, CT, FL, IL, IN, KS
- **sample (AZ):** "A licensed addiction technician shall practice only under direct supervision as prescribed by the board."

### `supervisor_credential_requirements` — list[str]
- **what:** The credential types or license categories that qualify a person to provide clinical supervision for applicants accumulating supervised hours.
- **states:** AR, AZ, CO, CT, FL, IL, IN, KS
- **sample (AR):** "Supervised experience shall be approved and documented by a registered clinical supervisor in good standing with the board"

### `registered_clinical_supervisor_credential` — bool
- **what:** Whether the state creates a distinct registered or approved clinical supervisor credential separate from the counselor license itself.
- **states:** AR, AZ, IN, KS
- **sample (AR):** "Registered clinical supervisor means a person registered by the State Board of Examiners of Alcoholism and Drug Abuse Counselors to provide clinical supervision of applicants for certification or licensure"

### `supervision_hours_required` — int
- **what:** Minimum total hours of clinical supervision required during the post-degree supervised experience period.
- **states:** AR, AZ, CT, IN, KS
- **sample (KS):** "not less than 100 hours of face-to-face clinical supervision, including not less than 50 hours of individual supervision"

### `individual_vs_group_supervision_split` — str
- **what:** The required breakdown between individual (one-on-one) and group supervision hours within the total supervision requirement.
- **states:** CO, IN, KS
- **sample (IN):** "at least one hundred fifty (150) hours under supervision, one hundred (100) hours of which must be under individual supervision and fifty (50) hours of which must be under group supervision"

### `virtual_supervision_permitted` — bool
- **what:** Whether telesupervision or virtual (synchronous audio-video) supervision is explicitly permitted to count toward supervised hours requirements.
- **states:** CO, IN
- **sample (IN):** "Up to one hundred percent (100%) of the supervised addiction counseling experience hours required under subsection (b) may be accounted for through virtual supervision by a qualified supervisor"

## supervised experience details

### `direct_client_contact_hours_required` — int
- **what:** Minimum hours of face-to-face direct client contact required as part of the supervised work experience.
- **states:** AZ, CO, CT, FL, IN, KS
- **sample (KS):** "at least 1,500 hours of direct client contact conducting substance abuse assessments and treatment with individuals, couples, families or groups"

### `psychoeducation_hours_cap` — int
- **what:** Maximum number of direct client contact hours that may be in psychoeducation (rather than direct counseling) for purposes of meeting experience requirements.
- **states:** AZ, CO
- **sample (AZ):** "For the direct client contact hours, not more than four hundred hours may be in psychoeducation."

### `practicum_hours_required` — int
- **what:** Minimum hours of supervised practicum, internship, or field experience required as part of the educational program (pre-degree, distinct from post-degree supervised work).
- **states:** CO, CT, FL, IN, KS
- **sample (IN):** "At least one (1) supervised practicum, internship, or field experience in an addiction counseling setting that requires the applicant to provide at least three hundred fifty (350) hours of addiction counseling services."

### `approved_education_clock_hours_required` — int
- **what:** Minimum clock hours of approved education (not necessarily degree coursework) required for certification or licensure, used in states that specify clock-hour rather than degree-based education requirements.
- **states:** AR, CT
- **sample (AR):** "Has successfully completed a minimum of two hundred seventy (270) clock hours of approved education. Approved education shall be directly related to alcoholism or drug abuse counseling subjects, theory, practice, or research"

## required curriculum content

### `substance_use_disorder_specific_coursework_required` — bool
- **what:** Whether the statute explicitly requires coursework specifically focused on substance use disorders, addiction, or alcohol and drug topics as part of the educational requirements.
- **states:** CA, CO, CT, FL, IN, KS
- **sample (KS):** "complete a minimum number of semester hours of coursework on substance use disorders as approved by the board"

### `required_curriculum_content_areas` — list[str]
- **what:** Specific subject matter or content areas that must be included in the educational program or coursework for licensure.
- **states:** CA, CO, CT, FL, IN, KS
- **sample (IN):** "Addictions theory; Psychoactive drugs; Addictions counseling skills; Theories of personality; Developmental psychology; Abnormal psychology; Group work; Cultural competency; Ethics and professional development; Family education"

### `core_competency_framework_required` — bool
- **what:** Whether the statute mandates a defined set of core competencies (beyond general coursework) that counselors must demonstrate, often aligned with national certification domains.
- **states:** CA, CO, IN
- **sample (CA):** "The department shall determine the required core competencies for registered and certified counselors working within an alcohol or other drug recovery and treatment program... Core competency requirements described in paragraph (2) shall align with national certification domains and competency exams."

### `medications_for_addiction_treatment_knowledge_required` — bool
- **what:** Whether the statute explicitly requires counselors to have knowledge of medications used in addiction treatment (e.g., MAT) as part of core competencies or curriculum.
- **states:** CA, CO, IN
- **sample (CA):** "Knowledge of medications for addiction treatment."

## what they can treat and who they can serve

### `co_occurring_disorders_scope` — bool
- **what:** Whether the statute explicitly includes co-occurring mental health disorders (alongside substance use disorders) within the authorized scope of practice.
- **states:** AZ, CA, CO, CT, FL, KS
- **sample (CT):** "the clinical evaluation by a licensed alcohol and drug counselor of substance use disorders and co-occurring disorders, including screening, assessment and diagnosis, treatment planning, counseling, therapy, trauma-informed care and psychoeducation"

### `diagnosis_authority` — enum[none, substance_use_disorders_only, substance_use_and_co_occurring, full_behavioral_health]
- **what:** The scope of diagnostic authority granted by the credential, ranging from no diagnosis authority to full behavioral health diagnosis.
- **states:** AL, AZ, CO, CT, FL, IN, KS
- **sample (KS):** "Licensed clinical addiction counselor means a person who engages in the independent practice of addiction counseling and diagnosis and treatment of substance use disorders specified in the edition of the American psychiatric association's diagnostic and statistical manual of mental disorders"

### `dsm_use_required` — bool
- **what:** Whether the statute explicitly requires use of the DSM (Diagnostic and Statistical Manual of Mental Disorders) for diagnosis or treatment planning.
- **states:** CA, CT, FL, KS
- **sample (KS):** "integrating diagnosis and treatment of substance use disorders with use of the diagnostic and statistical manual of mental disorders of the American psychiatric association"

### `opioid_antagonist_authority` — bool
- **what:** Whether the statute explicitly authorizes counselors to possess, furnish, or administer opioid antagonists (e.g., naloxone) notwithstanding general prohibitions on prescribing.
- **states:** CO, FL
- **sample (CO):** "a psychologist, social worker, marriage and family therapist, licensed professional counselor, unlicensed psychotherapist, or addiction counselor licensed, registered, or certified under this article 245 may possess, furnish, or administer an opioid antagonist in accordance with section 12-30-110."

### `conversion_therapy_prohibited` — bool
- **what:** Whether the statute explicitly prohibits licensees from engaging in conversion therapy, particularly with minors.
- **states:** CO, IL
- **sample (CO):** "Conversion therapy with a client who is under eighteen years of age"

## practice setting and facility rules

### `practice_setting_restrictions` — list[str]
- **what:** Restrictions on the settings in which lower-tier credential holders may practice (e.g., must work within a licensed treatment program).
- **states:** AL, AR, CT, FL, KS
- **sample (KS):** "No person may practice addiction counseling under a temporary addiction counselor license or a temporary master's addiction counselor license except in a licensed or certified alcohol and other drug abuse program, under the direction of a person licensed by the behavioral sciences regulatory board at the clinical level"

### `private_practice_restriction` — bool
- **what:** Whether the statute explicitly restricts or defines private practice of alcohol/drug counseling and limits who may engage in it.
- **states:** AL, AR, CT, IL, KS
- **sample (CT):** "Private practice of alcohol and drug counseling means the independent practice of alcohol and drug counseling by a licensed or certified alcohol and drug counselor who is self-employed on a full-time or part-time basis"

### `telehealth_authorized` — bool
- **what:** Whether the statute explicitly authorizes or addresses delivery of counseling services via telehealth or telecommunication technology.
- **states:** AL, CO, CT, FL
- **sample (AL):** "Telehealth means the application of telecommunication technology to deliver professional counseling services remotely to assess, diagnose, and treat behavioral health conditions."

## continuing education specifics

### `continuing_education_ethics_hours_required` — int
- **what:** Minimum number of continuing education hours specifically on ethics required per renewal period.
- **states:** CO, CT, KS
- **sample (KS):** "The application for renewal shall be accompanied by evidence satisfactory to the board that the applicant has completed during the previous 24 months the continuing education required by rules and regulations of the board, including not less than three hours in ethics."

### `continuing_education_cultural_competency_required` — bool
- **what:** Whether the statute explicitly requires continuing education hours on cultural competency as part of license renewal.
- **states:** CO, CT, IN
- **sample (CT):** "The continuing education shall be in areas related to the individual's practice and shall include not less than one contact hour of training or education each registration period on the topic of cultural competency"

## practitioner wellness and impairment

### `impaired_practitioner_program` — bool
- **what:** Whether the statute establishes or references a formal program for identifying, monitoring, and rehabilitating impaired licensees as an alternative to or alongside disciplinary action.
- **states:** AL, CO, FL
- **sample (AL):** "The Alabama Licensed Counselor Wellness Program is created to develop, maintain, and make available treatment programs for all licensees who voluntary seek medical intervention, treatment, and rehabilitation for an impairment."

## client confidentiality and mandatory reporting

### `duty_to_warn_codified` — bool
- **what:** Whether the statute explicitly codifies a duty to warn or protect identifiable third parties when a client communicates a serious threat of violence.
- **states:** AL, AR, CO, FL, IL, KS
- **sample (AL):** "If there is a duty to warn and protect under the limited circumstances specified above, the duty shall be discharged by the licensed professional counselor or associate licensed counselor making reasonable efforts to communicate the threat to the victim or victims and to a law enforcement agency."

### `client_disclosure_requirements` — bool
- **what:** Whether the statute requires licensees to provide written disclosures to clients at the start of the professional relationship about credentials, scope, and rights.
- **states:** AL, CO, FL, KS
- **sample (KS):** "A licensee under the addiction counselor licensure act, at the beginning of a client-therapist relationship, shall inform the client of the level of such licensee's training and the title or titles and license or licenses of such licensee."

## interstate practice and portability

### `interstate_compact_participation` — bool
- **what:** Whether the state has enacted or participates in an interstate counseling compact that allows licensees to practice across member states.
- **states:** AL, CO, FL
- **sample (FL):** "The compact is designed to achieve the following purposes and objectives: Facilitate interstate practice of licensed professional counseling to increase public access to professional counseling services by providing for the mutual recognition of other member state licenses."

### `jurisprudence_exam_required` — bool
- **what:** Whether applicants must pass a state-specific jurisprudence examination on the laws and rules governing practice in that state.
- **states:** AL, CO, FL, IN, KS
- **sample (AL):** "Jurisprudence requirement means the assessment of an individual's knowledge of the laws and rules governing the practice of professional counseling in a state."
