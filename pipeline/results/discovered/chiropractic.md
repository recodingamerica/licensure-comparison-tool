# Discovered fields — chiropractic

## extra credentials and tiered scope

### `adjunctive_procedures_certification_required` — bool
- **what:** Whether a separate certification (beyond the base license) is required to use adjunctive physical-modality procedures.
- **states:** PA
- **sample (PA):** "after January 1, 1988, the licensee must be certified in accordance with this act to use adjunctive procedures"

### `adjunctive_procedures_certification_pathways` — list[str]
- **what:** Recognized pathways by which a licensee may obtain certification to use adjunctive procedures.
- **states:** PA
- **sample (PA):** "passed an examination on the use of adjunctive procedures … completed a minimum of 100 hours of study in the use of adjunctive procedures … used adjunctive procedures in the licensed practice of chiropractic for three years immediately preceding the effective date of this act"

### `limited_license_available` — bool
- **what:** Whether a limited (restricted-purpose) license is available, typically for out-of-state or foreign graduates for teaching purposes.
- **states:** PA
- **sample (PA):** "a limited license which may be issued to an out-of-State or foreign chiropractic school or college graduate for a period not to exceed one year for the purpose of teaching in an approved graduate chiropractic education program"

### `specialist_title_requires_postgraduate_certification` — bool
- **what:** Whether a chiropractor must hold a postgraduate certification in a specialty before holding themselves out as a specialist in that area.
- **states:** PA
- **sample (PA):** "Holding himself out as a specialist unless he possesses a postgraduate certification in that specialty."

## what they can treat and where on the body

### `adjunctive_procedures_defined` — list[str]
- **what:** Enumerated physical modalities classified as adjunctive procedures within the chiropractic scope.
- **states:** PA
- **sample (PA):** "Physical measures such as mechanical stimulation, heat, cold, light, air, water, electricity, sound, massage and mobilization."

### `explicitly_excluded_practices` — list[str]
- **what:** Practices or procedures explicitly excluded from the chiropractic scope of practice by statute.
- **states:** PA
- **sample (PA):** "The term shall not include the practice of obstetrics or gynecology, the reduction of fractures or major dislocations, or the use of drugs or surgery."

### `nutritional_counseling_authorized` — bool
- **what:** Whether nutritional counseling is explicitly included within the authorized chiropractic scope of practice.
- **states:** PA
- **sample (PA):** "nutritional counseling, provided that nothing herein shall be construed to require licensure as a chiropractor in order to engage in nutritional counseling"

### `imaging_authorized` — bool
- **what:** Whether the use of X-ray or other diagnostic imaging is explicitly authorized within the chiropractic scope.
- **states:** PA
- **sample (PA):** "the use of board-approved scientific instruments of analysis, including X-ray"

### `diagnosis_authorized` — bool
- **what:** Whether chiropractors are explicitly authorized to perform diagnosis (typically limited to determining appropriateness of chiropractic treatment).
- **states:** PA
- **sample (PA):** "the term shall also include diagnosis, provided that such diagnosis is necessary to determine the nature and appropriateness of chiropractic treatment"

## supervision and delegation

### `referral_obligation` — bool
- **what:** Whether licensees have a statutory duty to refer patients to other healthcare practitioners when diagnosis indicates it is appropriate.
- **states:** PA
- **sample (PA):** "Failing to refer a patient to a licensed practitioner of another branch of the healing arts for consultation or treatment when a diagnosis of such patient indicates that such a referral is appropriate."

### `auxiliary_personnel_radiologic_supervision_required` — bool
- **what:** Whether auxiliary personnel performing radiologic procedures must be under the direct on-premises supervision of a licensed chiropractor.
- **states:** PA
- **sample (PA):** "no auxiliary personnel shall perform radiologic procedures on the premises of a chiropractor unless such person is under the direct supervision of a chiropractor who is on the premises at the time the X-ray of the patient is taken"

### `auxiliary_personnel_radiologic_exam_required` — bool
- **what:** Whether auxiliary personnel who perform radiologic procedures must pass a board-approved examination.
- **states:** PA
- **sample (PA):** "unless such person has passed an examination approved by the board and administered in accordance with section 812.1"

### `unlicensed_supportive_personnel_permitted` — bool
- **what:** Whether a licensed chiropractor may utilize unlicensed supportive personnel under direct on-premises supervision.
- **states:** PA
- **sample (PA):** "Nothing in this act shall prohibit a licensed chiropractor from utilizing the assistance of unlicensed supportive personnel performing under the direct on-premises supervision of a licensed chiropractor"

### `student_practice_exemption` — bool
- **what:** Whether chiropractic students are exempt from licensure requirements when performing clinical activities under direct licensed supervision as part of an approved curriculum.
- **states:** PA
- **sample (PA):** "This section does not apply to a student enrolled in a chiropractic education program at a chiropractic college approved by the board … provided that the student is under the direct, immediate and personal supervision of a chiropractor licensed by the board."

## practice setting and insurance requirements

### `professional_liability_insurance_required` — bool
- **what:** Whether professional liability insurance (or self-insurance) is a mandatory condition for obtaining or renewing a chiropractic license.
- **states:** PA
- **sample (PA):** "an applicant shall submit to the board satisfactory evidence that he has obtained professional liability insurance, or that he has established self-insurance for professional liability"

### `liability_insurance_minimum_per_occurrence` — int
- **what:** Minimum required professional liability insurance coverage per occurrence, in US dollars.
- **states:** PA
- **sample (PA):** "in the minimum amount of $100,000 per occurrence and $300,000 per annual aggregate"

### `liability_insurance_minimum_annual_aggregate` — int
- **what:** Minimum required professional liability insurance coverage per annual aggregate, in US dollars.
- **states:** PA
- **sample (PA):** "in the minimum amount of $100,000 per occurrence and $300,000 per annual aggregate"

## discipline and impairment programs

### `impaired_professional_program_available` — bool
- **what:** Whether the statute establishes a formal impaired-professional program allowing deferred or stayed disciplinary action in exchange for participation in an approved treatment program.
- **states:** PA
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the professional is progressing satisfactorily in an approved treatment program"

### `mandatory_impairment_reporting` — bool
- **what:** Whether hospitals, health care facilities, peers, or colleagues are legally required to report a licensee's active addictive disease, diversion of controlled substances, or mental/physical incompetence to the board.
- **states:** PA
- **sample (PA):** "Any hospital or health care facility, peer or colleague who has substantial evidence that a professional has an active addictive disease for which the professional is not receiving treatment … shall make or cause to be made a report to the board"

### `multiple_licensure_reporting_required` — bool
- **what:** Whether licensees holding chiropractic licenses in other jurisdictions must report that fact and any out-of-state disciplinary actions to the board.
- **states:** PA
- **sample (PA):** "Any licensed chiropractor of this Commonwealth who is also licensed to practice chiropractic in any other state, territory, possession or country shall report this information to the board on the biennial registration application."

### `cure_claim_prohibition` — bool
- **what:** Whether the statute explicitly prohibits licensees from claiming or guaranteeing that chiropractic treatment will cure specific conditions such as cancer or infectious diseases.
- **states:** PA
- **sample (PA):** "Making representations that chiropractic treatment will cure cancer or an infectious or communicable disease."

## professional title and designation

### `authorized_professional_title` — str
- **what:** The professional title and abbreviation a licensee is authorized to use under the statute.
- **states:** PA
- **sample (PA):** "Any person who has a valid license in accordance with this act may practice chiropractic and use the title 'Doctor of Chiropractic' and the abbreviation 'DC.'"

### `prohibited_title_impersonation` — list[str]
- **what:** Titles or designations from other licensed professions that a chiropractor is explicitly prohibited from using or implying.
- **states:** PA
- **sample (PA):** "A chiropractor shall not hold himself out in any manner to be a licensed physical therapist unless he is duly licensed under the act … known as the Physical Therapy Practice Act."

## education before chiropractic school

### `pre_chiropractic_college_education_required` — bool
- **what:** Whether applicants must complete a specified amount of undergraduate college education prior to entering or graduating from chiropractic college.
- **states:** PA
- **sample (PA):** "Has completed two years of college or 60 credit hours."

### `pre_chiropractic_college_credit_hours` — int
- **what:** Minimum undergraduate college credit hours required before chiropractic licensure.
- **states:** PA
- **sample (PA):** "Has completed two years of college or 60 credit hours."

### `chiropractic_college_minimum_instructional_hours` — int
- **what:** Minimum number of classroom and laboratory instruction hours required at an approved chiropractic college.
- **states:** PA
- **sample (PA):** "successful completion of not less than the minimum number of hours of classroom and laboratory instruction required by regulation of the board, which minimum shall be at least 4,000 hours"
