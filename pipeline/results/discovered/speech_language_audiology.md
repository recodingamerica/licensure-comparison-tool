# Discovered fields — speech_language_audiology

## license types and structure

### `dual_licensure_available` — bool
- **what:** Whether a single license can cover both speech-language pathology and audiology for a dually qualified applicant.
- **states:** UT
- **sample (UT):** "An applicant who qualifies to be licensed as both a speech-language pathologist and audiologist shall receive a single license reflecting licensure in both classifications."

### `license_disciplines` — list[str]
- **what:** The distinct professional disciplines for which separate licensure is available under the same regulatory chapter.
- **states:** UT
- **sample (UT):** "Licensing shall be granted independently either in speech-language pathology or audiology. A person shall be licensed in one or both areas when the person meets the respective qualifications."

### `temporary_license_available` — bool
- **what:** Whether a temporary license may be issued to applicants completing a clinical fellowship year prior to full licensure.
- **states:** UT
- **sample (UT):** "The division may issue a temporary license to an applicant for an audiology license who … is practicing audiology in a year of clinical fellowship. The temporary license is valid for up to 12 months."

### `temporary_license_duration_months` — int
- **what:** Maximum duration in months of a temporary license issued during the clinical fellowship year.
- **states:** UT
- **sample (UT):** "The temporary license is valid for up to 12 months."

## supervision and delegation

### `aide_classification_recognized` — bool
- **what:** Whether the statute formally recognizes a subordinate aide classification (audiology aide or speech-language pathology aide) with defined supervision requirements.
- **states:** UT
- **sample (UT):** "'Audiology aide' means an individual who … works under the personal direction and direct supervision of a licensed audiologist who accepts responsibility for the acts and performance of that audiology aide under this chapter."

### `aide_supervision_level` — enum[direct, indirect, personal direction and direct]
- **what:** The required level of supervision a licensed professional must provide over an aide.
- **states:** UT
- **sample (UT):** "works under the personal direction and direct supervision of a licensed speech-language pathologist who accepts the responsibility for the acts and performances of that speech-language pathology aide"

### `aide_independent_practice_prohibited` — bool
- **what:** Whether aides are explicitly prohibited from acting independently.
- **states:** UT
- **sample (UT):** "does not act independently"

## supervised clinical training

### `clinical_fellowship_year_required` — bool
- **what:** Whether a clinical fellowship year (CFY) is a recognized and required component of the licensure pathway.
- **states:** UT
- **sample (UT):** "'CFY' means the clinical fellowship year prescribed by ASHA."

### `post_degree_experience_hours_per_week` — int
- **what:** Minimum weekly hours of direct clinical experience required during the post-degree supervised professional experience period.
- **states:** UT
- **sample (UT):** "at least one academic year of professional experience, at least 30 hours per week, of direct clinical experience in treatment and management of patients"

### `supervisor_credential_requirement` — list[str]
- **what:** Credentials the supervising professional must hold to qualify as a supervisor for post-degree clinical experience.
- **states:** UT
- **sample (UT):** "supervised and attested to by one holding an audiologist license under this chapter, the CCC, or their full equivalent"

## professional credentials and standards

### `national_professional_certification_referenced` — bool
- **what:** Whether the statute explicitly references a national professional certification (e.g., ASHA's Certificate of Clinical Competence) as a benchmark or alternative pathway.
- **states:** UT
- **sample (UT):** "'CCC' means the certificate of clinical competence awarded by the American Speech-Language-Hearing Association."

### `doctoral_degree_required_after_date` — bool
- **what:** Whether a doctoral-level degree (AuD or equivalent) is required for audiologist licensure after a specified transition date.
- **states:** UT
- **sample (UT):** "To obtain and maintain a license as an audiologist beginning July 1, 2010, an applicant must … provide the committee with verification that the applicant is the legal holder of a clinical doctor's degree or AuD, in audiology"

### `doctoral_degree_transition_date` — str
- **what:** The date on or after which a doctoral degree became required for audiologist licensure.
- **states:** UT
- **sample (UT):** "To obtain and maintain a license as an audiologist beginning July 1, 2010"

### `continuing_education_graduate_level_required` — bool
- **what:** Whether continuing education for license renewal must be at the graduate level and clinically related to the profession.
- **states:** UT
- **sample (UT):** "At the time of renewal the licensee shall show satisfactory evidence of completion of scheduled graduate level professional training, related clinically to the profession of speech-language pathology or audiology"

## hearing aid dispensing rules

### `hearing_aid_sale_consumer_protections` — bool
- **what:** Whether the statute imposes specific consumer-protection requirements on licensees who sell hearing aids, such as mandatory written receipts and cancellation rights.
- **states:** UT
- **sample (UT):** "A person licensed under this chapter who sells a hearing aid to a consumer shall provide a written receipt or written contract to the consumer that provides the consumer with a 30-day right to cancel the purchase"

### `hearing_aid_return_period_days` — int
- **what:** Number of days a consumer has to return a hearing aid for a refund after purchase.
- **states:** UT
- **sample (UT):** "a 30-day right to cancel the purchase and to obtain a refund if the consumer returns the hearing aid to the seller in the same condition as when purchased"

### `hearing_aid_ada_compatibility_disclosure_required` — bool
- **what:** Whether licensees selling hearing aids must inform consumers about ADA-compatible assistive listening systems.
- **states:** UT
- **sample (UT):** "A person licensed under this chapter who offers to sell a hearing aid to a consumer shall inform the consumer about hearing aids that work with assistive listening systems that are compliant with the ADA Standards for Accessible Design"

## telehealth and interstate practice

### `telehealth_authorized` — bool
- **what:** Whether the statute explicitly authorizes delivery of audiology or speech-language pathology services via telehealth.
- **states:** UT
- **sample (UT):** "'Telehealth' means the application of electronic communication or information technology that meets the applicable standard of care to deliver audiology or speech-language pathology services or information at a distance for assessment, intervention and/or consultation."

### `interstate_compact_member` — bool
- **what:** Whether the state has enacted the Audiology and Speech-Language Pathology Interstate Compact, enabling multistate practice privileges.
- **states:** UT
- **sample (UT):** "Chapter 41a, Audiology and Speech-Language Pathology Interstate Compact"

### `compact_privilege_adverse_action_waiting_period_years` — int
- **what:** Number of years after an adverse action during which a licensee is ineligible to obtain a compact privilege in a remote state.
- **states:** UT
- **sample (UT):** "Have not had any adverse action against any license or compact privilege within the previous 2 years from date of application"

## client rights and confidentiality

### `privileged_communication_protected` — bool
- **what:** Whether the statute establishes a privileged-communication protection between the licensee and client, preventing compelled disclosure without client consent.
- **states:** UT
- **sample (UT):** "A person licensed under this chapter may not be examined or required to reveal any findings, examinations, or representation made to the licensed person by the licensed person's client … without the consent of the client or the client's representative."

## exemptions from licensure

### `school_credential_exemption` — bool
- **what:** Whether persons holding a valid state education credential are exempt from licensure when practicing solely within a school setting.
- **states:** UT
- **sample (UT):** "a person who has obtained a valid and current credential issued by the State Board of Education while specifically performing the functions of a speech-language pathologist or audiologist solely within the confines of … the school employing the person"

### `federal_employee_exemption` — bool
- **what:** Whether persons employed by federal government agencies are exempt from state licensure when providing services solely within that agency.
- **states:** UT
- **sample (UT):** "a person employed as a speech-language pathologist or audiologist by federal government agencies or subdivisions … while specifically performing speech-language pathology or audiology services solely within the confines of … the agency or subdivision"

### `newborn_hearing_screening_exemption` — bool
- **what:** Whether persons trained in newborn hearing screening and working under indirect audiologist supervision are exempt from full licensure.
- **states:** UT
- **sample (UT):** "a person who is … trained in newborn hearing screening … and working under the indirect supervision of a licensed audiologist responsible for a newborn hearing screening program"
