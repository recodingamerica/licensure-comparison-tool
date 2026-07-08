# Discovered fields — community_health_worker

## whether certification is required or optional

### `certification_is_voluntary` — bool
- **what:** Whether the certification credential is voluntary (title protection only) or mandatory to practice at all.
- **states:** CT, MA, MD, NH
- **sample (NH):** "Certification as a community health worker is voluntary. Nothing in this section shall be construed as requiring community health workers to be certified for purposes of employment."

### `title_protection_only` — bool
- **what:** Whether the statute restricts only the use of the certified title rather than the practice of community health work itself.
- **states:** CT, KY, MA, MD, ND, NH
- **sample (ND):** "An individual may not use the title 'community health worker' unless that individual is certified as a community health worker under this chapter."

### `protected_title` — list[str]
- **what:** The specific protected title(s) or credential abbreviation(s) that only certified individuals may use.
- **states:** CT, KY, MA, MD, ND, NH
- **sample (NH):** "In order to use the title 'certified community health worker', the initials 'CCHW', or other designation indicating that the individual is a certified community health worker, an individual shall be certified pursuant to the provisions of this chapter."

## governance and advisory structures

### `advisory_body_established` — bool
- **what:** Whether the statute establishes a formal advisory body or board to guide certification and training standards for community health workers.
- **states:** CT, LA, MD
- **sample (CT):** "There is established within the Office of Health Strategy a Community Health Worker Advisory Body."

### `advisory_body_chw_majority_required` — bool
- **what:** Whether the statute requires that a majority of the advisory body members be practicing community health workers.
- **states:** CT, LA
- **sample (LA):** "It shall consist of eleven members to include a majority of community health workers."

### `advisory_body_member_categories` — list[str]
- **what:** Categories of stakeholders required to be represented on the advisory body (e.g., practicing CHWs, employers, training organizations, health care providers).
- **states:** CT, LA, MD
- **sample (CT):** "Six members who are actively practicing as community health workers in the state; A member of the Community Health Workers Association of Connecticut; A representative of a community-based community health worker training organization; An employer of community health workers; A health care provider who works directly with community health workers."

## approved training programs and curriculum

### `training_program_accreditation_required` — bool
- **what:** Whether training programs must be formally accredited or approved by the state before their graduates qualify for certification.
- **states:** CT, KY, MD
- **sample (MD):** "A certified community health worker training program must be accredited by the Department before operating in the State."

### `competency_based_training_required` — bool
- **what:** Whether the statute explicitly requires that training be competency-based rather than purely hour-based.
- **states:** KY, MD
- **sample (KY):** "Complete a competency-based community health worker training and mentorship program offered by an organization approved by the department to provide community health worker training and mentorship."

### `core_competencies_defined_by_authority` — bool
- **what:** Whether the statute directs the issuing authority to formally define the core competencies of community health work through regulation.
- **states:** KY, MD
- **sample (KY):** "'Core competencies' means the knowledge and skills a certified community health worker is expected to demonstrate in order to carry out the mission and goals of the profession as defined by the department through the promulgation of administrative regulations."

### `experience_pathway_available` — bool
- **what:** Whether applicants may qualify for certification through documented prior work experience as an alternative or supplement to completing a formal training program.
- **states:** CT, KY, MD
- **sample (CT):** "Has a minimum of two thousand hours of paid or unpaid experience as a community health worker."

### `minimum_experience_hours` — int
- **what:** Minimum number of hours of community health worker experience required for the experience-based certification pathway.
- **states:** CT, KY
- **sample (CT):** "Has a minimum of one thousand hours of experience working as a community health worker during the three years prior to the date of such application."

### `mentorship_required` — bool
- **what:** Whether a formal mentorship component is required as part of the training or certification process.
- **states:** KY, MD
- **sample (KY):** "Complete a competency-based community health worker training and mentorship program offered by an organization approved by the department."

### `college_credit_eligible` — bool
- **what:** Whether the statute explicitly provides that CHW training, mentorship, or continuing education may count toward college course credit.
- **states:** KY, MD
- **sample (KY):** "Notwithstanding any other provision of law to the contrary, an individual shall be eligible to earn college course credit for training, mentorship, and continuing education completed pursuant to subsections (2) and (4) of this section."

## continuing education specifics

### `ce_topical_mandates` — list[str]
- **what:** Specific subject areas that are mandated by statute to be included in continuing education for renewal or recertification.
- **states:** CT, KY
- **sample (KY):** "Administrative regulations promulgated pursuant to this subsection shall include requirements for continuing education related to oral health care, infant and maternal health care, and geriatric health care."

### `ce_cultural_competency_hours` — int
- **what:** Number of continuing education hours specifically required to address cultural competency, systemic racism, or related equity topics.
- **states:** CT, KY
- **sample (CT):** "Two hours focused on cultural competency, systemic racism or systemic oppression."

### `ce_mental_health_screening_hours` — int
- **what:** Number of continuing education hours specifically required on mental health screening topics such as PTSD, depression, suicide risk, or grief.
- **states:** CT, KY
- **sample (CT):** "Two hours of training on (1) screening for post-traumatic stress disorder, risk of suicide, depression and grief, and (2) suicide prevention."

## how and where services may be delivered

### `telemedicine_authorized` — bool
- **what:** Whether the statute explicitly authorizes certified community health workers to deliver services via telemedicine or other electronic means.
- **states:** KY, NH
- **sample (NH):** "Certified community health workers shall be permitted to provide services through the use of telemedicine."

### `scope_limited_to_preventive_services` — bool
- **what:** Whether the statute explicitly limits the CHW scope of practice to preventive or non-clinical services, excluding diagnosis or treatment.
- **states:** MA, ND, NH
- **sample (ND):** "'Preventative services' means services to prevent a disease, disability, or other health condition or the progression of a disease, disability, or other health condition."

### `liaison_role_defined` — bool
- **what:** Whether the statute explicitly defines the CHW role as a liaison, link, or intermediary between community members and health or social services.
- **states:** CT, MA, MD, NH
- **sample (CT):** "Serves as a liaison between individuals within the community and health care and social services providers to facilitate access to such services and health-related resources."

### `social_determinants_of_health_in_scope` — bool
- **what:** Whether the statute explicitly includes addressing social determinants of health as part of the CHW scope of practice or definition.
- **states:** CT, MA, MD
- **sample (CT):** "Research related to social determinants of health and basic screenings and assessments of any risks associated with social determinants of health."

### `target_population_criteria` — list[str]
- **what:** Specific population characteristics or conditions that define who the CHW is authorized or intended to serve.
- **states:** CT, MD, ND
- **sample (ND):** "Preventative services means services provided to an individual: with a chronic condition; at risk for a chronic condition who is unable to self-manage the chronic condition; or with a documented barrier that affects the individual's health."

### `community_health_representative_recognized` — bool
- **what:** Whether the statute explicitly recognizes Indian Health Service-trained Community Health Representatives as a distinct category eligible for CHW certification.
- **states:** KY, ND
- **sample (ND):** "'Community health representative' means an individual trained through the Indian health service to provide community-based and medically guided health care, which may include traditional native concepts."

## certification renewal and expiration

### `certificate_renewal_interval_years` — int
- **what:** The number of years (or fraction thereof expressed as a year) between required certificate renewals.
- **states:** CT, KY, MA
- **sample (CT):** "A certification issued under this section may be renewed every three years."

### `grandfathering_provision` — bool
- **what:** Whether the statute includes a provision allowing individuals already working as CHWs before the law's effective date to qualify for certification without meeting all new requirements.
- **states:** CT, MD
- **sample (MD):** "A process through which an individual working as a community health worker on October 1, 2018, and who already possesses the knowledge taught in a community health worker training program accredited by the Department under this section, may be exempted from the training required."

### `scope_of_practice_defined_by_regulation` — bool
- **what:** Whether the statute delegates to the issuing authority the power to define the scope of practice for certified CHWs through administrative rulemaking.
- **states:** KY, ND, NH
- **sample (KY):** "The scope of practice for certified community health workers."

## relationship to other licensed professions

### `other_licensed_profession_exemption` — bool
- **what:** Whether the statute explicitly exempts individuals licensed under other professional laws from CHW certification requirements when practicing within their own licensed scope.
- **states:** CT, MA, MD, NH
- **sample (MA):** "Nothing in this section shall permit a certified community health worker to engage in or perform any act or service for which a license issued by a professional licensing board is required."

### `dual_credential_use_restriction` — bool
- **what:** Whether the statute restricts a person who holds both a CHW certificate and another professional license from simultaneously using the CHW title while practicing under the other license.
- **states:** MA, NH
- **sample (NH):** "Nothing in this section shall be construed to prevent or restrict the practice, service, or activities of any individual simultaneously certified as a community health worker and licensed... if that individual does not, while engaged in the authorized practice of another profession, use any name, title, the initials 'CCHW', or other designation indicating that the individual is a certified community health worker."

## enforcement and disciplinary powers

### `cease_and_desist_authority` — bool
- **what:** Whether the statute explicitly grants the issuing authority power to issue cease-and-desist orders against unauthorized use of the CHW title.
- **states:** MA, MD, NH
- **sample (MA):** "The use by any person not so certified of any words, letters, abbreviations or insignia indicating or implying a person holds such certification shall be in violation of this section for which the board may issue a cease and desist order."

### `community_reference_required_for_application` — bool
- **what:** Whether applicants must submit a reference from a community member (not just a professional employer) who can attest to their CHW experience.
- **states:** CT, MD
- **sample (CT):** "A reference from a member of the community with direct knowledge of the applicant's experience as a community health worker."
