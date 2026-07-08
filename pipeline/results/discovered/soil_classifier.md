# Discovered fields — soil_classifier

## extra credentials and tiered scope

### `tiered_registration_levels` — list[str]
- **what:** The named credential tiers available under the state's registration scheme, from entry-level trainee to full professional.
- **states:** AR, IN, ME, NC, ND, SC
- **sample (SC):** ""Soil classifier-in-training" means a person who complies with the requirements for education and character and who has passed an examination in the fundamental soil and related subjects as provided for in this chapter."

### `trainee_certification_validity_years` — int
- **what:** Number of years for which a soil classifier-in-training or associate-level certification is valid before it expires or must be converted to full licensure.
- **states:** AR, ND, SC
- **sample (ND):** "Unless otherwise qualified, a person must be admitted to certification as a soil classifier-in-training, which certification is valid for four years."

### `trainee_exam_type` — enum[fundamentals of soil classification, fundamentals of soil science, principles and practice]
- **what:** The type of examination required for the entry-level trainee credential, distinct from the full professional practice examination.
- **states:** AR, ME, ND, SC
- **sample (AR):** "A graduate of a soils curriculum approved by the board and has passed an examination in the fundamentals of soil classification."

### `field_skills_exam_required` — bool
- **what:** Whether the state explicitly requires a separate field-based examination (e.g., soil morphology and landscape analysis) in addition to a written examination.
- **states:** IN, ME
- **sample (IN):** "The board shall require an applicant for registration as a professional soil scientist to pass … an examination that evaluates field skills in soil morphology and landscape analysis."

### `peer_review_experience_pathway` — bool
- **what:** Whether the statute provides an alternative experience pathway in which a longer period of experience evaluated through a peer review system may substitute for the standard supervised-experience route.
- **states:** WI
- **sample (WI):** "At least 7 years of professional experience in soil science work … with a satisfactory evaluation of the last 2 years of the professional experience under a peer review system approved by the section."

## education and coursework details

### `approved_soils_curriculum_required` — bool
- **what:** Whether the applicant's degree curriculum must be formally approved by the licensing board (as opposed to any accredited degree being acceptable).
- **states:** AL, AR, ND, SC, VA
- **sample (AR):** "Is a graduate of a soils curriculum approved by the commission as satisfactory and with a specific record of an additional one (1) year or more of experience."

### `minimum_soil_science_credit_hours` — int
- **what:** Minimum number of semester credit hours specifically in soil science courses required for licensure eligibility.
- **states:** IN, ME, NC, SC
- **sample (ME):** "Completed a minimum of 15 credit hours of soil or soil-related courses."

### `supporting_science_credit_hours` — int
- **what:** Minimum number of semester credit hours in supporting sciences (biology, chemistry, geology, etc.) required alongside the soil science core.
- **states:** IN, NC
- **sample (IN):** "At least forty-five (45) semester hours of course work in supporting sciences, including biology, chemistry, crop science, engineering, geology, mathematics, physics, and statistics."

### `teaching_or_research_counts_as_experience` — bool
- **what:** Whether teaching soil science at a college/university or conducting soil science research may be credited toward the professional work experience requirement.
- **states:** AL, ME, NC, ND, SC, VA
- **sample (AL):** "Teaching soil classification courses in a college or university offering an approved four-year soil science or agronomic curriculum should be considered as experience in soil investigations."

### `advanced_degree_experience_credit` — bool
- **what:** Whether holding a master's or doctoral degree in soil science may substitute for a portion of the required post-degree professional work experience.
- **states:** IN, ME, NC, VA, WI
- **sample (NC):** "The Board, in its discretion, may allow an applicant to substitute a masters degree in soil science for one year of professional work experience and to substitute a doctoral degree in soil science for two years of professional work experience."

## supervision and delegation

### `supervised_experience_required` — bool
- **what:** Whether a specified portion of the required work experience must be performed under the direct supervision of a licensed or registered soil scientist.
- **states:** ME, NC, SC, WI
- **sample (NC):** "Have at least three years of professional work experience as a soil scientist under the supervision of a licensed soil scientist, or a soil scientist who is eligible for licensure."

### `subordinate_definition_included` — bool
- **what:** Whether the statute explicitly defines 'subordinate' as a person who assists a licensed soil scientist without assuming responsible charge of work.
- **states:** AL, ME, NC, ND, SC
- **sample (ME):** ""Subordinate" means any person who assists a licensed geologist or soil scientist without assuming the responsible charge of work."

### `responsible_charge_definition_included` — bool
- **what:** Whether the statute explicitly defines 'responsible charge' or 'responsible charge of work' as independent control and direction of soil classification work.
- **states:** AL, ME, NC, ND, SC, VA
- **sample (AL):** ""Responsible charge of work" means the independent control and direction by the use of initiative, skill, and independent judgment of work or the supervision of such work."

## practice setting and business structure

### `firm_corporation_practice_allowed` — bool
- **what:** Whether the statute explicitly permits soil classifiers to practice through a sole proprietorship, partnership, corporation, or LLC, subject to having at least one licensed member in responsible charge.
- **states:** AL, ME, NC, VA, WI
- **sample (AL):** "This chapter does not prohibit one or more professional soil classifiers from practicing through the medium of a sole proprietorship, partnership, or corporation. In such partnership or corporation whose primary activity consists of classification services, at least one partner or officer shall be a registered professional soil classifier."

### `firm_certificate_of_authorization_required` — bool
- **what:** Whether firms, partnerships, or corporations offering soil science services must obtain a separate certificate of authorization from the board.
- **states:** WI
- **sample (WI):** "A firm, partnership or corporation desiring a certificate of authorization shall submit an application to the department on forms provided by the department."

### `nonresident_temporary_permit_available` — bool
- **what:** Whether out-of-state practitioners may obtain a temporary permit to work in the state for a limited period or specific project without full registration.
- **states:** AR, NC, ND
- **sample (ND):** "May be granted a temporary permit for a definite period of time not to exceed one (1) year to do a specific job provided, however, no right to practice soil classifying shall accrue to such applicant with respect to any other work not set forth in said permit."

### `nonresident_practice_exempt_days` — int
- **what:** Number of days per calendar year a non-resident licensed practitioner may practice in the state without obtaining local registration.
- **states:** AL, AR, ME, NC, ND
- **sample (AL):** "A person not a resident of and having no established place of business in this State, practicing or offering to practice herein the profession of soil classifier when such practice does not exceed a total of 30 days in any calendar year."

### `private_employer_exemption` — bool
- **what:** Whether persons employed solely to perform soil classifying services for their private employer (not the public) are exempt from licensure requirements.
- **states:** AL, AR, ND, SC, WI
- **sample (ND):** "The practice of soil classifying by any person regularly employed to perform soil classifying services solely for his or her employer or for a subsidiary or affiliated corporation of his or her employer, providing the soil classifying performed is in connection with the property, products, or services of that person's employer."

## what they can do and related professions

### `wetland_delineation_scope_included` — bool
- **what:** Whether the statute explicitly includes or addresses wetland delineation as a related or overlapping scope of practice for soil scientists.
- **states:** IN, NC, SC, VA
- **sample (VA):** ""Practice of wetland delineation" means the delineation of wetlands by accepted principles and methods including, observation, investigation, and consultation on soil, vegetation, and hydrologic parameters."

### `national_cooperative_soil_survey_standard_referenced` — bool
- **what:** Whether the statute explicitly references the National Cooperative Soil Survey as the standard for soil identification and mapping.
- **states:** AL, ME, NC
- **sample (ME):** ""Practice of soil science" includes identification and mapping of soils according to the standards of the National Cooperative Soil Survey, consultation or evaluation."

### `hydric_soil_and_redoximorphic_features_in_scope` — bool
- **what:** Whether the statute explicitly lists identification of hydric soils and redoximorphic features as part of the authorized scope of practice.
- **states:** NC
- **sample (NC):** ""Practice of soil science" includes … identification of hydric soil and redoximorphic features."

### `soil_fertility_sampling_excluded_from_scope` — bool
- **what:** Whether the statute explicitly excludes routine soil sampling for plant nutrient or fertility testing from the regulated practice of soil classifying.
- **states:** AR, NC, ND, SC
- **sample (NC):** "Soil sampling solely for the purpose of determining plant nutrient and lime application rates for gardening and agricultural purposes by persons who are not licensed soil scientists."

### `engineering_geology_excluded_from_scope` — bool
- **what:** Whether the statute explicitly carves out geotechnical or soils engineering evaluations for structural or construction purposes from the soil classifier's scope.
- **states:** AL, AR, NC, ND, SC, WI
- **sample (AL):** "This chapter shall not be construed to affect or prevent individuals who are duly licensed by the State of Alabama Board of Registration of Professional Engineers and Land Surveyors and who are engaging in the practice of geotechnical engineering or soils engineering from conducting an engineering evaluation."

## professional documents and signing authority

### `seal_or_stamp_required_on_documents` — bool
- **what:** Whether the statute requires licensed soil scientists to affix a personal seal or stamp to soil science maps, reports, or other documents they prepare or approve.
- **states:** AL, IN, ME, NC, WI
- **sample (ME):** "All soil science maps, reports or documents that are prepared by a licensed soil scientist or by a subordinate under the licensed soil scientist's direction must be signed by the licensed soil scientist."

## professional conduct and discipline

### `code_of_ethics_required` — bool
- **what:** Whether the statute mandates the board to adopt and promulgate a formal code of ethics binding on all registrants.
- **states:** AL, AR, IN, NC, ND, SC, VA, WI
- **sample (ND):** "The board shall cause to have prepared and shall adopt a code of ethics a copy of which must be delivered to every registrant and applicant for registration under this chapter."

### `minimum_exam_passing_score` — int
- **what:** Minimum percentage score required to pass the licensure examination, where explicitly stated in statute.
- **states:** ND, SC
- **sample (SC):** "The passing grade on any examination shall not be less than seventy percent."

### `reexamination_minimum_score_waiting_period` — bool
- **what:** Whether the statute imposes a waiting period before a candidate who scored below a threshold (e.g., below 50%) may reapply for examination.
- **states:** ND, SC
- **sample (SC):** "Any candidate for registration having an average grade of less than fifty percent may not apply for reexamination for a period of one year from the date of such examination."

## governance and board structure

### `advisory_council_established` — bool
- **what:** Whether the statute creates a separate advisory council of soil scientists to assist the primary licensing authority in evaluating applicants and recommending certification.
- **states:** AL, SC
- **sample (AL):** "The board shall appoint an advisory council of five members, four of whom shall be qualified professional soil classifiers who shall have the qualifications required in this chapter."

### `board_includes_public_member` — bool
- **what:** Whether the statute requires at least one non-soil-scientist public member to serve on the licensing board.
- **states:** ME, NC
- **sample (NC):** "One member appointed by the General Assembly upon recommendation of the Speaker of the House of Representatives, who shall be a member of the public who is not a soil scientist."

### `board_includes_ex_officio_state_soil_scientist` — bool
- **what:** Whether the state's chief or official soil scientist serves as an ex officio member of the licensing board.
- **states:** AL, ME
- **sample (ME):** "The 6th and 7th members are the State Soil Scientist employed in State Government, ex officio."

### `combined_board_with_related_professions` — bool
- **what:** Whether soil scientists share a single licensing board or examining body with one or more related professions such as geologists or hydrologists.
- **states:** ME, VA, WI
- **sample (VA):** ""Board" means the Board for Professional Soil Scientists, Wetland Professionals, and Geologists."
