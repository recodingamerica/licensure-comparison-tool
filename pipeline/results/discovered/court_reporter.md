# Discovered fields — court_reporter

## how the record is made

### `verbatim_recording_methods_authorized` — list[str]
- **what:** The specific methods or technologies by which a court reporter may create a verbatim record.
- **states:** AL, CA, GA, HI, ID, IL
- **sample (AL):** "The making of a verbatim record by means of manual shorthand, machine shorthand, closed microphone voice dictation silencer, or by other means of personal verbatim reporting"

### `voice_writing_authorized` — bool
- **what:** Whether voice writing (using a steno mask or closed microphone voice dictation silencer) is explicitly recognized as an authorized reporting method.
- **states:** AL, CA, GA, ID
- **sample (CA):** "'Voice writing' means a verbatim record or a proceeding using a closed microphone voice dictation silencer, steno mask, or similar device using oral shorthand and voice notes made by a certified shorthand reporter."

### `reporting_methodology_indicated_on_certificate` — bool
- **what:** Whether the certificate or license must indicate the specific methodology (stenography, voice writing, etc.) by which the reporter qualified.
- **states:** CA, ID
- **sample (CA):** "The board shall indicate on each certificate issued pursuant to this chapter whether the certificate holder met the certified shorthand reporter examination requirements through the use of stenography, voice writing, or both."

## what proceedings they may report

### `proceedings_covered` — list[str]
- **what:** The types of legal proceedings or forums in which a court reporter is authorized or required to make a verbatim record.
- **states:** AL, CA, GA, HI, ID, IL
- **sample (IL):** "reporting, by the use of any system of manual or mechanical shorthand writing, of Grand Jury proceedings, court proceedings, court related proceedings, pretrial examinations, depositions, motions and related proceedings of like character, or proceedings of an administrative agency"

### `deposition_reporting_included` — bool
- **what:** Whether the taking of depositions is explicitly included within the definition of court reporting or the scope of practice.
- **states:** AL, CA, GA, ID, IL
- **sample (AL):** "The taking of a deposition is the making of a verbatim record."

## employment setting and role type

### `official_reporter_employment_type` — enum[official, freelance, private, substitute]
- **what:** The recognized employment or practice categories for court reporters, distinguishing court-employed official reporters from freelance or private reporters.
- **states:** AL, AR, GA, HI, ID, IL
- **sample (HI):** "'Official court reporter' means a certified shorthand reporter employed by the courts of the State to provide court reporting services. 'Private court reporter' means a certified shorthand reporter who offers services on a freelance basis and who is not employed by the courts of the State."

### `substitute_reporter_allowed` — bool
- **what:** Whether the statute explicitly provides for temporary or substitute court reporters to fill in when the official reporter is unavailable.
- **states:** AR, GA, ID
- **sample (AR):** "In the absence or unavailability of the official court reporter, the circuit judge or circuit judge on assignment as authorized by § 16-10-101 may temporarily employ the services of a substitute court reporter if the temporary employment is essential to prevent a disruption of the business of the circuit court."

## extra credentials and tiered licensure

### `temporary_permit_available` — bool
- **what:** Whether the state offers a temporary or provisional permit allowing a person to practice before obtaining full certification.
- **states:** AL, CA, GA, ID
- **sample (AL):** "Commencing on August 1, 2012, any person who is a graduate of a court reporting program may receive a temporary license to practice as a court reporter from the board."

### `temporary_permit_duration_months` — int
- **what:** The maximum duration in months for which a temporary or provisional permit is valid.
- **states:** AL, CA, ID
- **sample (AL):** "The temporary license shall be valid for 18 months from the date of issuance."

### `restricted_certificate_available` — bool
- **what:** Whether the state offers a restricted certificate that limits the holder to a narrower scope of practice (e.g., only court proceedings in a specific circuit).
- **states:** GA, IL
- **sample (IL):** "the Department shall, upon payment of the required fee, issue to any reporter who has been appointed in counties of less than 1,000,000 in population, has been examined under the Court Reporters Act, and has achieved an 'A' proficiency rating, a restricted certificate by which such official court reporter may then lawfully engage in reporting only court proceedings to which the Chief Judge of the reporter's circuit may assign."

### `inactive_status_available` — bool
- **what:** Whether the state provides a formal inactive license status for reporters not currently practicing.
- **states:** AL, CA, IL
- **sample (AL):** "The board shall establish an inactive status for persons who are not actively engaged in the practice of court reporting."

## examination and qualification pathways

### `nationally_recognized_exam_accepted` — list[str]
- **what:** National certification examinations that the state accepts in lieu of or as a pathway to its own licensing examination.
- **states:** AL, CA, ID, IL
- **sample (AL):** "shall pass an Alabama skills examination or provide documentation of having passed the NCRA Registered Professional Reporter Examination or NVRA CVR Examination."

### `exam_speed_requirement_wpm` — int
- **what:** The minimum dictation speed in words per minute required to pass the skills/dictation portion of the licensing examination.
- **states:** AL, CA
- **sample (CA):** "the qualifier examination shall consist of 4-voice testimony of 10-minute duration at 200 words per minute, graded at 95 percent accuracy"

### `exam_accuracy_threshold_percent` — int
- **what:** The minimum accuracy percentage required to pass the dictation or transcription portion of the licensing examination.
- **states:** AL, CA
- **sample (CA):** "The passing grades for the Dictation/Transcription part of the examination is 95 percent."

## approved training programs and schools

### `court_reporting_school_recognition_program` — bool
- **what:** Whether the state board has a formal program to recognize or accredit court reporting training schools.
- **states:** AL, CA, ID
- **sample (CA):** "The board may grant provisional recognition to a new court reporting school upon satisfactory evidence that it has met all of the provisions of subdivision (b) and this subdivision."

## transcript duties and record-keeping

### `transcript_certification_required` — bool
- **what:** Whether the reporter is required to certify transcripts as true, complete, and correct before delivery.
- **states:** AR, CA, GA, HI, IL
- **sample (GA):** "The reporter, upon delivering the transcript to such counsel, shall affix thereto a certificate signed by him reciting that the transcript is true, complete, and correct."

### `notes_retention_period_years` — int
- **what:** The minimum number of years a reporter must retain stenographic notes or transcripts.
- **states:** AR, CA, IL
- **sample (IL):** "It is the licensee's responsibility to preserve the licensee's shorthand notes for a period of no less than 10 years from the date that the notes or transcripts were taken"

### `notes_retention_media_types` — list[str]
- **what:** The acceptable storage media or formats for retaining stenographic notes or transcripts.
- **states:** CA, IL
- **sample (IL):** "through storage of the original paper notes or an electronic copy of either the shorthand notes or the English transcript of the notes on computer disks, cassettes, backup tape systems, optical or laser disk systems, or other retrieval systems"

### `transcript_page_format_defined` — bool
- **what:** Whether the statute defines a standard format or line/character count for a transcript page.
- **states:** CA, CT
- **sample (CT):** "'Transcript page' means a page consisting of twenty-seven double-spaced lines on paper eight and one-half by eleven inches in size, if printed, with sixty spaces available per line"

### `transcript_fee_schedule_set_by_statute` — bool
- **what:** Whether the statute sets specific per-page or per-folio fees that reporters may charge for transcripts.
- **states:** AR, CA, CT
- **sample (CT):** "an official court reporter and a court recording monitor shall be entitled to charge an individual, who is not a public official, three dollars and sixty cents for each transcript page that is ordered and transcribed"

## conflicts of interest and impartiality rules

### `prohibited_exclusive_contracts` — bool
- **what:** Whether the statute prohibits court reporters from entering into exclusive or non-case-specific contracts with attorneys or parties that could compromise impartiality.
- **states:** CA, GA, HI
- **sample (GA):** "Contracts for court reporting services not related to a particular case or reporting incident between a certified court reporter or any person with whom a certified court reporter has a principal and agency relationship and any attorney at law, party to an action, party having a financial interest in an action, or agent for an attorney at law...are prohibited."

### `contingent_fee_prohibited` — bool
- **what:** Whether the statute explicitly prohibits court reporters from charging contingent fees as a basis of compensation.
- **states:** CA, IL
- **sample (IL):** "Establishing contingent fees as a basis of compensation"

### `gifts_to_attorneys_prohibited` — bool
- **what:** Whether the statute prohibits or limits giving gifts or items of value to attorneys or their staff.
- **states:** CA, IL
- **sample (IL):** "giving, directly or indirectly, any gift or anything of value to attorneys or the attorneys' staff or any other persons or entities associated with any litigation, that exceeds $100 total per year"

## firm and entity regulation

### `court_reporting_firm_registration_required` — bool
- **what:** Whether court reporting firms or entities (not individual reporters) must separately register with the state board.
- **states:** CA, GA
- **sample (GA):** "A court reporting firm doing business in Georgia shall register with the board by completing an application in the form adopted by the board and paying fees as required by the board."

### `reporter_in_charge_required_for_entity` — bool
- **what:** Whether a non-reporter-owned entity providing court reporting services must designate a licensed reporter-in-charge responsible for compliance.
- **states:** CA, GA
- **sample (CA):** "The entity has designated a board-certified reporter-in-charge who is a full-time employee of the registered entity and a resident of California, and who holds a currently valid California license at all times as a certified shorthand reporter"

## official duties and powers

### `oath_administration_authorized` — bool
- **what:** Whether certified court reporters are explicitly authorized to administer oaths or affirmations.
- **states:** CA, GA, HI
- **sample (HI):** "A certified shorthand reporter may administer oaths or affirmations and may perform the duties of a deposition officer pursuant to rules of court relating to persons before whom depositions may be taken."

### `reporter_appointed_by_judge` — bool
- **what:** Whether official court reporters are formally appointed by a judge or judicial authority rather than hired through a general employment process.
- **states:** AR, CT, GA, HI
- **sample (GA):** "The judges of the superior courts shall have power to appoint and, at their pleasure, to remove a court reporter"

### `license_number_disclosure_on_record_required` — bool
- **what:** Whether the reporter must state their name and license number on the record at the start of a proceeding.
- **states:** AL, CA, IL
- **sample (CA):** "A certified shorthand reporter, whether appearing in person or through the use of remote technology, shall state on the record their full name and license number as each appears on their certificate issued by the board, at the beginning of a proceeding, deposition, or other matter for transcription"

### `remote_reporting_authorized` — bool
- **what:** Whether the statute explicitly recognizes or addresses court reporters appearing or reporting remotely using technology.
- **states:** CA, CT
- **sample (CA):** "A certified shorthand reporter, whether appearing in person or through the use of remote technology, shall state on the record their full name and license number"
