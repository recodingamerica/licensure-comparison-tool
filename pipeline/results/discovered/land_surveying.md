# Discovered fields — land_surveying

## pre-licensure credentials and training stages

### `surveyor_in_training_certificate` — bool
- **what:** Whether the jurisdiction has a formal intermediate 'surveyor-in-training' certificate that candidates must obtain before sitting for the full licensure examination.
- **states:** PA
- **sample (PA):** "'Surveyor-in-Training' means a candidate for licensure as a professional land surveyor who has been granted a certificate as a surveyor-in-training after successfully passing the prescribed written examination in fundamental land surveying subjects."

### `field_office_experience_split_required` — bool
- **what:** Whether the statute requires candidates to demonstrate a minimum percentage of both field and office experience (i.e., diversification across both types).
- **states:** PA
- **sample (PA):** "An applicant shall show diversification of field and office experience, with at least twenty-five per cent of the applicant's experience in each."

## what they can do and where their work overlaps with engineering

### `engineering_land_surveys_authorized` — bool
- **what:** Whether a professional land surveyor is explicitly authorized to perform 'engineering land surveys' as a defined category of work.
- **states:** PA
- **sample (PA):** "A professional land surveyor may perform engineering land surveys but may not practice any other branch of engineering."

### `engineering_land_surveys_definition` — list[str]
- **what:** The enumerated types of surveys classified as 'engineering land surveys' that a land surveyor may perform.
- **states:** PA
- **sample (PA):** "'Engineering Land Surveys' means surveys for: (i) the development of any tract of land including the incidental design of related improvements... (ii) the determination of the configuration or contour of the earth's surface... (iii) geodetic survey, underground survey and hydrographic survey; (iv) storm water management surveys and sedimentation and erosion control surveys..."

### `tract_perimeter_survey_exclusive_to_pls` — bool
- **what:** Whether tract perimeter surveys are explicitly reserved as the exclusive function of the professional land surveyor (not engineers).
- **states:** PA
- **sample (PA):** "tract perimeter surveys shall be the function of the Professional Land Surveyor"

## supervision and responsible charge

### `responsible_charge_defined` — bool
- **what:** Whether the statute provides a formal definition of 'responsible charge' as it applies to land surveying practice.
- **states:** PA
- **sample (PA):** "'Responsible Charge' means a position that requires initiative, skill and independent judgment, and implies such degree of competence and accountability gained by technical education and experience of a grade and character as is sufficient to qualify an individual to personally and independently engage in and be entrusted with the work involved in the practice of engineering or land surveying."

## professional seal and document signing requirements

### `seal_required_on_documents` — bool
- **what:** Whether the statute requires a licensed land surveyor to affix an official seal to all plans, specifications, plats, and reports they issue.
- **states:** PA
- **sample (PA):** "Such seal, or a facsimile imprint of same, shall be stamped on all plans, specifications, plats and reports issued by a professional engineer, professional land surveyor or professional geologist."

### `firm_corporation_practice_permitted` — bool
- **what:** Whether firms or corporations may engage in the practice of land surveying, subject to the condition that responsible-charge employees are licensed and their seal and signature appear on all issued documents.
- **states:** PA
- **sample (PA):** "it shall be unlawful for any firm or corporation to engage in such practice... unless the directing heads and employes of such firm or corporation in responsible charge of its activities in the practice of such profession are licensed and registered in conformity with the requirements of this act, and whose name, seal and signature, along with the date of signature, shall be stamped on all plans, specifications, plats and reports issued by such firm or corporation."

## who is exempt from needing a license

### `exemptions_from_licensure` — list[str]
- **what:** The enumerated categories of persons or activities explicitly exempt from the land surveying licensure requirement.
- **states:** PA
- **sample (PA):** "The running of lines or grades and layout work on or within established property limits... when performed by a contractor or home builder in conjunction with the construction, reconstruction, alteration, maintenance or demolition of a structure or other facility."

### `nonresident_temporary_practice_days` — int
- **what:** Maximum number of days per calendar year a nonresident (without a place of business in the state) may practice land surveying without obtaining a state license.
- **states:** PA
- **sample (PA):** "The practice of engineering, land surveying or geology, not exceeding thirty days in the aggregate in one calendar year, by a nonresident not having a place of business in this Commonwealth, if such person is legally qualified to engage in the practice of engineering, land surveying or geology in the state or territory of his residence."

## reporting and disciplinary obligations

### `multiple_licensure_reporting_required` — bool
- **what:** Whether licensees holding licenses in other jurisdictions must report that fact and any out-of-state disciplinary actions to the board.
- **states:** PA
- **sample (PA):** "Any licensee of this Commonwealth who is also licensed to practice engineering, land surveying or geology in any other state, territory or country shall report this information to the board on the biennial renewal application. Any disciplinary action taken in other states, territories or countries shall be reported to the board on the biennial renewal application or within ninety days of final disposition, whichever is sooner."

### `code_of_ethics_statutory` — bool
- **what:** Whether a code of professional ethics for land surveyors is codified directly in the statute (not merely referenced to a separate rule).
- **states:** PA
- **sample (PA):** "It shall be considered unprofessional and inconsistent with honorable and dignified bearing for a person who is a professional engineer, professional land surveyor or professional geologist: To act for the person's client or employer in professional matters otherwise than as a faithful agent or trustee..."
