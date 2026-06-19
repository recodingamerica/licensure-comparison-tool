# Discovered fields — professional_engineering

## related professions covered under the same law

### `covers_land_surveying` — bool
- **what:** Whether the same statute and licensing board also governs professional land surveyors.
- **states:** PA
- **sample (PA):** "Practice of Land Surveying means the practice of that branch of the profession of engineering which involves the location, relocation, establishment, reestablishment or retracement of any property line or boundary of any parcel of land..."

### `covers_geology` — bool
- **what:** Whether the same statute and licensing board also governs professional geologists.
- **states:** PA
- **sample (PA):** "for any person to practice or to offer to practice geology unless he is licensed and registered under the laws of this Commonwealth as a professional geologist."

## pre-licensure credentials and training tiers

### `engineer_intern_certificate_available` — bool
- **what:** Whether the state issues a formal intermediate certificate (engineer intern or engineer-in-training) to candidates who pass the fundamentals exam but have not yet completed experience requirements.
- **states:** PA
- **sample (PA):** "Engineer Intern means a candidate for licensure as a professional engineer, who has been granted a certificate as an engineer intern after successfully passing the prescribed written examination in fundamental engineering subjects."

### `surveyor_in_training_certificate_available` — bool
- **what:** Whether the state issues a formal intermediate certificate to land surveying candidates who pass the fundamentals exam but have not yet completed experience requirements.
- **states:** PA
- **sample (PA):** "Surveyor-in-Training means a candidate for licensure as a professional land surveyor who has been granted a certificate as a surveyor-in-training after successfully passing the prescribed written examination in fundamental land surveying subjects."

### `geologist_in_training_certificate_available` — bool
- **what:** Whether the state issues a formal intermediate certificate to geology candidates who pass the fundamentals exam but have not yet completed experience requirements.
- **states:** PA
- **sample (PA):** "Geologist-in-training means a candidate for licensure as a professional geologist who has been granted a certificate as a geologist-in-training after successfully passing the required written examination in fundamental geology subjects."

### `postgraduate_degree_experience_credit_years_max` — int
- **what:** Maximum number of years of experience credit that may be granted for postbaccalaureate engineering degrees earned before licensure.
- **states:** PA
- **sample (PA):** "The board may grant one year of experience credit for each postbaccalaureate engineering degree earned by applicants for licensure, not to exceed two years."

## what counts as practicing the profession

### `responsible_charge_defined` — bool
- **what:** Whether the statute provides an explicit statutory definition of 'responsible charge' as a term of art for the level of oversight required for licensure and practice.
- **states:** PA
- **sample (PA):** "Responsible Charge means a position that requires initiative, skill and independent judgment, and implies such degree of competence and accountability gained by technical education and experience of a grade and character as is sufficient to qualify an individual to personally and independently engage in and be entrusted with the work involved in the practice of engineering or land surveying."

## professional seal and document signing rules

### `seal_required_on_documents` — bool
- **what:** Whether licensees are required by statute to obtain and affix an official seal to plans, specifications, plats, and reports they issue.
- **states:** PA
- **sample (PA):** "Such seal, or a facsimile imprint of same, shall be stamped on all plans, specifications, plats and reports issued by a professional engineer, professional land surveyor or professional geologist."

### `seal_document_types` — list[str]
- **what:** Types of professional documents that must bear the licensee's seal and signature.
- **states:** PA
- **sample (PA):** "whose name, seal and signature, along with the date of signature, shall be stamped on all plans, specifications, plats and reports issued by such firm or corporation."

## who may offer engineering services

### `firm_practice_allowed` — bool
- **what:** Whether firms and corporations may lawfully offer engineering, surveying, or geology services, subject to the condition that responsible employees are licensed.
- **states:** PA
- **sample (PA):** "it shall be unlawful for any firm or corporation to engage in such practice... unless the directing heads and employes of such firm or corporation in responsible charge of its activities in the practice of such profession are licensed and registered in conformity with the requirements of this act."

### `exemptions_from_licensure` — list[str]
- **what:** Categories of persons or activities explicitly exempted from the licensure requirement.
- **states:** PA
- **sample (PA):** "The practice of engineering, land surveying or geology by officers and employes of the United States Government for the said government."

## professional conduct and discipline

### `code_of_ethics_in_statute` — bool
- **what:** Whether the statute itself contains a codified code of ethics whose violation is grounds for license suspension or revocation.
- **states:** PA
- **sample (PA):** "It shall be considered unprofessional and inconsistent with honorable and dignified bearing for a person who is a professional engineer, professional land surveyor or professional geologist: To act for the person's client or employer in professional matters otherwise than as a faithful agent or trustee..."

### `multi_license_reporting_required` — bool
- **what:** Whether licensees holding licenses in other states, territories, or countries must report that fact and any out-of-state disciplinary actions to the board.
- **states:** PA
- **sample (PA):** "Any licensee of this Commonwealth who is also licensed to practice engineering, land surveying or geology in any other state, territory or country shall report this information to the board on the biennial renewal application."

## governing board composition

### `board_engineering_disciplines_represented` — list[str]
- **what:** The major engineering disciplines that must be represented on the licensing board, as specified by statute.
- **states:** PA
- **sample (PA):** "The professional members of the board shall be so selected that not more than two of them shall specialize in any one of the five major disciplines of engineering: civil, mining and metallurgical, mechanical, electrical and chemical."

### `board_member_responsible_charge_years_required` — int
- **what:** Minimum number of years a professional board member must have been in responsible charge of work to be eligible for appointment.
- **states:** PA
- **sample (PA):** "Each professional member shall have been engaged in the practice of the respective profession for at least ten years and shall have been in responsible charge of work for at least five years."

## continuing education specifics

### `pdh_units_per_renewal_period` — int
- **what:** Number of Professional Development Hours (PDH) required per biennial renewal period.
- **states:** PA
- **sample (PA):** "Each licensee shall be required to obtain twenty-four PDH units during the biennial renewal period."

### `pdh_carryover_max_units` — int
- **what:** Maximum number of excess PDH units that may be carried forward into the next renewal period.
- **states:** PA
- **sample (PA):** "If a licensee exceeds the requirement in any renewal period, a maximum of twelve PDH units may be carried forward into the subsequent renewal period."

### `retired_status_license_available` — bool
- **what:** Whether the state offers a retired-status license that exempts the holder from continuing education requirements while prohibiting active practice.
- **states:** PA
- **sample (PA):** "A licensee who lists his occupation as retired on the board-approved renewal form and certifies to the board that he no longer engages in the practice of his licensed profession shall be exempt from the requirement set forth in subsection (a), and the board shall issue him a retired-status license."
