# Discovered fields — psychology

## education and training pathways

### `doctoral_degree_types_accepted` — list[str]
- **what:** The specific doctoral degree titles accepted for licensure as a psychologist.
- **states:** PA
- **sample (PA):** "a graduate of an accredited college or university holding a degree of Doctor of Philosophy in psychology, Doctor of Psychology, or Doctor of Education in psychology"

### `equivalent_doctoral_field_accepted` — bool
- **what:** Whether a doctoral degree in a field related to psychology (not strictly psychology) is accepted if experience and training are deemed equivalent.
- **states:** PA
- **sample (PA):** "a graduate of an accredited college or university holding a doctoral degree in a field related to psychology and has not less than two years of supervised experience, provided such experience and training are acceptable to the board as being equivalent"

### `supervised_experience_years_required` — int
- **what:** Minimum number of years of supervised experience required for licensure.
- **states:** PA
- **sample (PA):** "has not less than two years of supervised experience, provided that such experience is acceptable to the board pursuant to criteria established by board regulations"

### `postdoctoral_trainee_titles` — list[str]
- **what:** Official titles that must be used by postdoctoral individuals completing supervised experience requirements.
- **states:** PA
- **sample (PA):** "Such individuals shall perform their duties under the full direction, control and supervision of a licensed psychologist... designated as 'psychology interns,' 'psychology residents' or 'psychological trainees.'"

## what psychologists are authorized to do

### `scope_methods_authorized` — list[str]
- **what:** Specific named methods or service types explicitly authorized within the practice of psychology.
- **states:** PA
- **sample (PA):** "measuring and testing of personality, intelligence, aptitudes, and emotions... counseling and the use of psychological methods... offering services as a psychological consultant"

### `diagnosable_conditions_listed` — list[str]
- **what:** Categories of conditions that psychologists with appropriate training are explicitly authorized to diagnose and treat.
- **states:** PA
- **sample (PA):** "Psychologists with appropriate education, training and experience may diagnose and use psychological methods in the treatment of a mental, emotional or nervous illness or disability; alcoholism and other substance abuse; disorders of habit or conduct; psychological aspects of physical illness, accident, injury or disability; and psychoeducational evaluation, therapy, remediation and consultation."

## who is exempt from licensure

### `industrial_organizational_exemption` — bool
- **what:** Whether employees of business and industrial organizations are exempt when applying psychology principles to their own workforce (not for public sale).
- **states:** PA
- **sample (PA):** "Nothing in this act shall be construed to prohibit employes of business and industrial organizations from applying the principles of psychology described in section 2 to the employment placement, evaluation, selection, promotion or job adjustment of their own officers or employes"

### `government_employee_exemption` — bool
- **what:** Whether psychologists employed by specified government agencies are exempt from licensure requirements when acting within their official duties.
- **states:** PA
- **sample (PA):** "Nothing in this act shall be construed to limit the practice of psychology or use of an official title on the part of a person employed as a psychologist by a Federal agency, the Department of Corrections or the Department of Human Services"

### `academic_and_research_exemption` — bool
- **what:** Whether faculty, staff, and researchers at accredited universities or colleges are exempt from licensure when practicing within their academic or research role.
- **states:** PA
- **sample (PA):** "Nothing in this act shall be construed to limit the practice of psychology or use of an official title on the part of a member of the faculty or staff of a duly accredited university, college or State-approved nonpublic school in so far as such practice is a part of the normal function of his position"

### `other_licensed_professions_exemption` — bool
- **what:** Whether persons licensed in other healing arts or recognized professions (e.g., social workers, clergy, counselors) are exempt from psychology licensure requirements.
- **states:** PA
- **sample (PA):** "Nothing in this act shall be construed to prevent qualified members of other recognized professions, including, but not limited to, clergy, drug and alcohol abuse counselors, mental health counselors, social workers, crisis intervention counselors, marriage and family therapists, pastoral counselors, rehabilitation counselors and psychoanalysts, from doing work of a psychological nature consistent with the training and the code of ethics of their respective professions"

## temporary and reciprocal licensing

### `temporary_license_available` — bool
- **what:** Whether the board may issue a temporary license to applicants licensed in another jurisdiction while their full application is pending.
- **states:** PA
- **sample (PA):** "The board may issue a temporary license to an applicant for licensure as a psychologist who holds a similar or current license from another state, province or territory and whose standards, in the opinion of the board, are substantially equivalent to those required under this act."

### `temporary_license_denial_for_prior_discipline` — bool
- **what:** Whether the board may refuse a temporary license to an applicant who has past or pending disciplinary action in another jurisdiction.
- **states:** PA
- **sample (PA):** "The board may refuse a temporary license to a psychologist who is the subject of past or pending disciplinary action in another jurisdiction."

## ongoing reporting and professional obligations

### `multiple_licensure_reporting_required` — bool
- **what:** Whether licensees must report to the board any licenses held in other states or jurisdictions and any disciplinary actions taken there.
- **states:** PA
- **sample (PA):** "Any licensed psychologist of this Commonwealth who is also licensed to practice psychology or another health profession in any other state, territory or country shall report this information to the board on the biennial registration application."

### `out_of_state_discipline_reporting_deadline_days` — int
- **what:** Number of days within which a licensee must report disciplinary action taken in another jurisdiction to the board.
- **states:** PA
- **sample (PA):** "Any disciplinary action taken in any other state, territory or country shall be reported to the board on the biennial registration application or within ninety days of disposition, whichever is sooner."

### `mandatory_impairment_reporting_required` — bool
- **what:** Whether hospitals, health care facilities, peers, or colleagues are required to report a licensee who shows evidence of active addiction, controlled substance diversion, or mental/physical incompetence.
- **states:** PA
- **sample (PA):** "Any hospital or health care facility, peer or colleague who has substantial evidence that a professional has an active addictive disease for which the professional is not receiving treatment, is diverting a controlled substance or is mentally or physically incompetent to carry out the duties of his or her license shall make or cause to be made a report to the board"

## impairment and rehabilitation programs

### `impaired_professional_program_available` — bool
- **what:** Whether the state has a formal impaired professional program through which a licensee in treatment may have disciplinary action deferred or dismissed.
- **states:** PA
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the professional is progressing satisfactorily in an approved treatment program"

## continuing education rules

### `continuing_education_excluded_topics` — list[str]
- **what:** Topics explicitly excluded from counting toward continuing education credit for license renewal.
- **states:** PA
- **sample (PA):** "No credit shall be given for any course in office management or practice building."

## license discipline and reinstatement

### `license_reinstatement_waiting_period_years` — int
- **what:** Minimum number of years a person must wait after license revocation before applying for reinstatement.
- **states:** PA
- **sample (PA):** "Any person whose license has been revoked may apply for reinstatement, after a period of at least five years, but must meet all of the licensing qualifications of this act for the license applied for, to include the examination requirement"

### `temporary_suspension_max_duration_days` — int
- **what:** Maximum number of days a temporary license suspension may remain in effect before formal proceedings must resolve it.
- **states:** PA
- **sample (PA):** "The temporary suspension shall remain in effect until vacated by the board but in no event longer than one hundred eighty days."

### `felony_drug_conviction_bar_with_exceptions` — bool
- **what:** Whether a felony conviction under controlled substance laws bars licensure, subject to specified exceptions such as elapsed time and demonstrated rehabilitation.
- **states:** PA
- **sample (PA):** "has not been convicted of a felony under the act of April 14, 1972 (P.L.233, No.64), known as 'The Controlled Substance, Drug, Device and Cosmetic Act'... unless: (i) at least ten years have elapsed from the date of conviction; (ii) the applicant satisfactorily demonstrates to the board that he has made significant progress in personal rehabilitation"

## licensing board structure

### `board_composition_public_members` — int
- **what:** Number of public (non-professional) members required on the psychology licensing board.
- **states:** PA
- **sample (PA):** "Two members shall be appointed as representatives of the public at large."

### `board_composition_professional_members` — int
- **what:** Number of licensed psychologist members required on the psychology licensing board.
- **states:** PA
- **sample (PA):** "Six members shall be appointed who shall hold current valid licenses to practice psychology in this Commonwealth and shall be broadly representative of the practice areas of psychology."

### `board_member_max_consecutive_terms` — int
- **what:** Maximum number of consecutive terms a board member may serve.
- **states:** PA
- **sample (PA):** "No member shall be eligible for appointment to serve more than two consecutive terms."
