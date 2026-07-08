# Discovered fields — music_therapy

## credentialing and certification

### `national_certification_body` — list[str]
- **what:** The national organization(s) whose certification credential is recognized or required for licensure or title use.
- **states:** AZ, CA, CT, GA, IA, IL, MD, ND, … (+2)
- **sample (CT):** "holds a current certification as a music therapist from the Certification Board for Music Therapists, or any successor of said board"

### `credential_required_for_licensure` — enum[MT-BC (Music Therapist-Board Certified), RMT (Registered Music Therapist), CMT (Certified Music Therapist), ACMT (Advanced Certified Music Therapist)]
- **what:** The specific national credential designation(s) that satisfy the certification requirement for licensure.
- **states:** CT, GA, IA, IL, MD, ND, NJ, NV
- **sample (ND):** "A music therapist board-certified credential from the certification board for music therapists; or a professional designation from the national music therapy registry, which may include registered music therapist, certified music therapist, and advanced certified music therapist"

### `certification_maintenance_required_for_renewal` — bool
- **what:** Whether the licensee must maintain active national board certification as a condition of license renewal.
- **states:** CT, GA, MD, NJ, NV
- **sample (GA):** "Proof of maintenance of the applicant's Certification Board for Music Therapists credentials"

### `protected_titles` — list[str]
- **what:** Specific titles, abbreviations, or designations that only a licensed or certified music therapist may use.
- **states:** CA, CT, GA, IA, IL, MD, NJ, NV
- **sample (NV):** "A person who is not licensed to practice music therapy...shall not use in connection with his or her name the words or letters 'MT,' 'music therapist,' 'licensed, board-certified music therapist,' 'MT-BC,' 'Music Therapist - Board Certified,' 'MT - BC/L' or 'Licensed Music Therapist - Board Certified'"

## governance and oversight body

### `advisory_body_composition` — str
- **what:** The membership composition of the state advisory board or group for music therapy, including number of members and their required backgrounds.
- **states:** GA, IL, MD
- **sample (IL):** "The Secretary shall appoint 3 members who practice as professional music therapists in this State, one member who is a licensed health care provider who is not a music therapist, and one member who is a consumer"

### `advisory_body_name` — str
- **what:** The official name of the advisory or regulatory body overseeing music therapy licensure.
- **states:** GA, IL, MD, ND, NV
- **sample (IL):** "There is created within the Department a Music Therapy Advisory Board"

## what music therapists cannot do

### `music_therapy_excluded_from_scope` — list[str]
- **what:** Activities or diagnoses explicitly excluded from the authorized scope of music therapy practice.
- **states:** CA, IL, MD, NJ, NV
- **sample (IL):** "'Music therapy' does not include the screening, diagnosis, or assessment of any physical, mental, or communication disorder"

### `cannot_replace_other_professions` — list[str]
- **what:** Other licensed professions whose services a music therapist is explicitly prohibited from replacing.
- **states:** IL, MD, NJ
- **sample (IL):** "When providing educational or health care services, a licensed professional music therapist may not replace the services provided by an audiologist or a speech-language pathologist"

### `psychotherapy_supervision_required` — bool
- **what:** Whether a music therapist with only a baccalaureate degree must be supervised by a qualified mental health professional to engage in psychotherapy.
- **states:** CA, IL
- **sample (IL):** "A licensed music therapist whose highest degree in music therapy is a baccalaureate degree shall not engage in the practice of psychotherapy unless supervised by a licensed music therapist with a master's degree in music therapy, a licensed clinical social worker, a licensed clinical psychologist, a licensed clinical professional counselor, a licensed marriage and family therapist, or a psychiatrist"

## what music therapists are authorized to do

### `authorized_music_therapy_interventions` — list[str]
- **what:** Specific music-based techniques and interventions explicitly enumerated as within the scope of music therapy practice.
- **states:** CA, GA, IL, MD, ND, NJ, NV
- **sample (CA):** "music improvisation, receptive music listening, song writing, lyric discussion, music and imagery, singing, music performance, learning through music, music combined with other arts, music-assisted relaxation, music-based patient education, electronic music technology, adapted music intervention, and movement to music"

### `authorized_practice_settings` — list[str]
- **what:** Types of care settings or service contexts in which music therapy is explicitly authorized.
- **states:** CA, IL, MD, NJ
- **sample (CA):** "developmental, rehabilitative, habilitative, medical, mental health, preventive, wellness care, or educational settings"

### `treatment_planning_required` — bool
- **what:** Whether the statute explicitly requires development of an individualized music therapy treatment plan for each client.
- **states:** CA, GA, IL, MD, NJ, NV
- **sample (IL):** "developing an individualized music therapy treatment plan for the client that is based upon the results of the music therapy assessment"

## working with other health professionals

### `interdisciplinary_collaboration_required` — bool
- **what:** Whether the statute explicitly requires the music therapist to collaborate with other health care or education professionals before or during treatment.
- **states:** GA, IL, MD, NJ, NV
- **sample (IL):** "Before a licensed professional music therapist provides music therapy services to a client for an identified clinical or developmental need, the licensee shall review the client's diagnosis, treatment needs, and treatment plan with the health care providers involved in the client's care"

### `referral_acceptance_authorized` — bool
- **what:** Whether the statute explicitly authorizes music therapists to accept referrals from other professionals, family members, or clients.
- **states:** GA, IL, MD, NJ, NV
- **sample (NV):** "accepting referrals for music therapy services from physicians, psychologists or other medical, developmental or mental health professionals, education professionals, family members, clients or caregivers"

### `least_restrictive_environment_required` — bool
- **what:** Whether the statute explicitly requires the music therapist to minimize barriers so clients receive services in the least restrictive environment.
- **states:** GA, IL, MD, NJ, NV
- **sample (NJ):** "minimizing any barriers so that the client may receive music therapy services in the least restrictive environment"

## client rights and professional conduct

### `client_confidentiality_privilege` — bool
- **what:** Whether the statute establishes a privileged communication or confidentiality protection for information shared by clients with music therapists.
- **states:** IL, MD
- **sample (IL):** "No licensed professional music therapist shall disclose any information acquired from persons consulting the therapist in a professional capacity"

### `delegation_of_services_restricted` — bool
- **what:** Whether the statute restricts or prohibits requiring a licensee to delegate music therapy services to another person against the licensee's clinical judgment.
- **states:** IL, NV
- **sample (NV):** "A person shall not require a licensee to delegate the provision of music therapy services to another person if, in the opinion of the licensee, such delegation would be inappropriate or create a risk of harm to the client"

## pathways to practice before full licensure

### `temporary_permit_available` — bool
- **what:** Whether the state offers a temporary or provisional permit allowing practice under supervision while completing full licensure requirements.
- **states:** CT, MD
- **sample (CT):** "The Department of Public Health may issue a temporary permit to an applicant for licensure as a music therapist who holds a bachelor's degree or higher in music therapy or a related field"

### `temporary_permit_supervision_requirement` — str
- **what:** The type of supervision required while practicing under a temporary or provisional permit.
- **states:** CT, MD
- **sample (CT):** "Such temporary permit shall authorize the holder of the temporary permit to practice music therapy under the general supervision of a licensed music therapist"

### `student_exemption_from_licensure` — bool
- **what:** Whether students enrolled in accredited music therapy programs are explicitly exempt from licensure requirements while performing supervised coursework.
- **states:** CT, GA, IL, MD, NJ, NV
- **sample (IL):** "Any practice of music therapy as an integral part of a program of study for students enrolled in an accredited music therapy program, if the student does not represent the student as a music therapist"

## ongoing education requirements

### `continuing_education_hours_per_renewal` — int
- **what:** The minimum number of continuing education hours required per renewal period.
- **states:** GA, IL, MD, NV
- **sample (IL):** "Proof of completion of a minimum of 40 hours of continuing education as established by rule"

### `continuing_education_approved_by` — str
- **what:** The organization whose approval is required for continuing education programs to count toward renewal.
- **states:** GA, IL, MD, NV
- **sample (GA):** "Proof of completion of a minimum of 40 hours of continuing education in a program approved by the Certification Board of Music Therapists or any successor organization"

### `dementia_training_required` — bool
- **what:** Whether the statute specifically requires training on Alzheimer's disease or dementia care as part of continuing education for renewal.
- **states:** IL, MD
- **sample (IL):** "For those licensed professional music therapists that have direct patient interactions with adult populations age 26 or older, proof of completion of at least one hour of training on the diagnosis, treatment, and care of individuals with Alzheimer's disease and other dementias per renewal period"

## background and fitness requirements

### `criminal_background_check_required` — bool
- **what:** Whether applicants are required to submit to a criminal history records check, including fingerprinting, as part of the licensure application.
- **states:** CT, GA, MD, NV
- **sample (GA):** "The applicant has satisfactory results from a fingerprint record check report conducted by the Georgia Crime Information Center and the Federal Bureau of Investigation"

## license status options

### `inactive_license_status_available` — bool
- **what:** Whether the state allows a licensee to place their license on inactive status and later reactivate it.
- **states:** CT, GA, IL, MD
- **sample (GA):** "Upon written request of a licensee, the Secretary may place an active license on an inactive status subject to an inactive status fee established by the Secretary"

### `rehabilitation_committee_available` — bool
- **what:** Whether the statute establishes or references a rehabilitation committee to assist music therapists with substance abuse or other health conditions affecting practice.
- **states:** IL, MD
- **sample (MD):** "the music therapist rehabilitation committee...evaluates and provides assistance to any music therapist in need of treatment and rehabilitation for alcoholism, drug abuse, chemical dependency, or other physical, emotional, or mental condition"
