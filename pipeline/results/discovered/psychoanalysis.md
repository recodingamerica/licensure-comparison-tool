# Discovered fields — psychoanalysis

## type of credential granted

### `credential_type` — enum[certification, licensure]
- **what:** Whether the state grants a certification or a license to practice psychoanalysis.
- **states:** NJ, VT
- **sample (NJ):** "State certified psychoanalyst means an individual who has met the eligibility requirements contained in section 6 of this act and holds a current, valid certificate of State certification."

## education and training pathway

### `psychoanalytic_institute_required` — bool
- **what:** Whether the applicant must earn a graduate certificate or doctoral degree from a free-standing psychoanalytic institute (distinct from a general university).
- **states:** NJ, VT
- **sample (NJ):** "Have received a graduate certificate in psychoanalysis from a free-standing psychoanalytic institute that is chartered by a state or foreign government and approved by the director or accredited by a national psychoanalytic association."

### `institute_accrediting_bodies` — list[str]
- **what:** The bodies that must accredit or charter the psychoanalytic institute from which the applicant earned their graduate credential.
- **states:** NJ, VT
- **sample (VT):** "a free-standing psychoanalytic institute that is chartered by a state or foreign government and accredited by a national psychoanalytic association"

### `personal_analysis_required` — bool
- **what:** Whether the applicant must have undergone a personal psychoanalysis conducted by an approved psychoanalyst as part of their training.
- **states:** VT
- **sample (VT):** "undergone a personal analysis by a psychoanalyst who has been approved by a psychoanalytic training institute"

### `trainee_practice_permitted` — bool
- **what:** Whether a student in training at an approved psychoanalytic institute may practice under a trainee designation before full certification is issued.
- **states:** VT
- **sample (VT):** "A student who is in training at a free-standing state or foreign government chartered psychoanalytic institute may practice as a psychoanalyst-in-training until issuance of State certification as long as that person is meeting the requirements for supervised practice of the institute at which that person is training."

## exemptions and who is excluded from the rules

### `exempt_licensed_professions` — list[str]
- **what:** Other licensed or certified mental health and medical professions that are exempt from psychoanalyst certification requirements when they also meet the educational criteria.
- **states:** SD, VT
- **sample (VT):** "Any person who has met the educational and clinical criteria established under subdivision 4057(a)(2) of this title and is licensed or certified under this title as a physician, osteopath, psychologist, clinical social worker, clinical mental health counselor, or marriage and family therapist shall be exempt from the provisions of this chapter."

### `lay_psychoanalyst_physician_cooperation_exemption` — bool
- **what:** Whether a qualified lay psychoanalyst practicing in cooperation with a licensed physician is exempt from the general regulatory chapter.
- **states:** SD
- **sample (SD):** "Nothing contained in this chapter shall be construed to apply to any qualified lay psychoanalyst who is practicing psychoanalysis in cooperation with a physician or doctor of medicine."

## oversight and advisory structure

### `advisory_body_composition` — str
- **what:** The makeup of the advisory committee or appointees that advises the issuing authority on psychoanalyst certification matters, including number of practitioner vs. public members.
- **states:** NJ, VT
- **sample (NJ):** "The advisory committee shall consist of six members who are residents of the State, four of whom shall be State certified psychoanalysts and two of whom shall be public members."

### `advisory_body_practitioner_experience_years` — int
- **what:** Minimum years of active practice in the state required for psychoanalyst members of the advisory committee.
- **states:** NJ
- **sample (NJ):** "The four psychoanalyst members shall be, except for the members first appointed, State certified psychoanalysts under the provisions of this act and shall have been actively engaged in the practice of psychoanalytic services in the State for at least five years immediately preceding their appointment."

## client protection and professional conduct rules

### `client_disclosure_rules_required` — bool
- **what:** Whether the state requires certified psychoanalysts to disclose professional qualifications, complaint procedures, and conduct standards to each client.
- **states:** VT
- **sample (VT):** "The Office of Professional Regulation, in consultation with the advisor appointees, shall adopt rules requiring certified psychoanalysts to disclose to each client the psychoanalyst's professional qualifications and experience, those actions that constitute unprofessional conduct, the method for filing a complaint or making a consumer inquiry."

### `prohibited_conduct_categories` — list[str]
- **what:** Specific categories of conduct explicitly defined as unprofessional or prohibited in the statute.
- **states:** VT
- **sample (VT):** "Engaging in any sexual conduct with a client, or with the immediate family member of a client, with whom the certified psychoanalyst has had a professional relationship within the previous two years."

### `conversion_therapy_prohibition` — bool
- **what:** Whether the statute explicitly prohibits the use of conversion therapy on minors as a form of unprofessional conduct.
- **states:** VT
- **sample (VT):** "Using conversion therapy as defined in 18 V.S.A. § 8351 on a client younger than 18 years of age."

## continuing education content requirements

### `continuing_education_equity_requirement` — bool
- **what:** Whether the state mandates that continuing education include content on systematic oppression, anti-oppressive practice, cultural competency, or antiracism.
- **states:** VT
- **sample (VT):** "Continuing education requirements shall include requiring one or more continuing education units in the area of systematic oppression and anti-oppressive practice, or in related topic areas."

### `continuing_education_cross_profession_credit` — bool
- **what:** Whether continuing education units completed for another licensed mental health profession count toward the psychoanalyst continuing education requirement.
- **states:** VT
- **sample (VT):** "If the licensee is licensed in one or more other mental health professions under this title, continuing education units completed for one mental health profession shall count toward the required continuing education units for the other mental health profession or professions."

### `virtual_continuing_education_accepted` — bool
- **what:** Whether synchronous virtual continuing education is explicitly accepted as equivalent to live in-person training.
- **states:** VT
- **sample (VT):** "Synchronous virtual continuing education credits shall be approvable and accepted as live in-person training."
