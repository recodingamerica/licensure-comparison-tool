# Discovered fields — medical_interpreter

## extra credentials and tiered scope

### `certification_tier` — enum[tier 1, tier 2]
- **what:** Tiered certification level distinguishing full oral+written qualification from written-only qualification when oral exam is unavailable in the target language.
- **states:** UT
- **sample (UT):** "An individual qualifies as a tier 1 certified medical language interpreter if the individual... passes an oral and written examination... If an oral examination under Subsection (1)(b) is not available in the language for which an individual applies for certification, the individual may qualify as a tier 2 certified medical language interpreter if the individual passes the written portion of an examination."

## language and communication scope

### `certified_languages` — list[str]
- **what:** The specific language(s) for which the interpreter is certified, as specified on the certificate.
- **states:** UT
- **sample (UT):** "A certificate described in Subsection (1) shall specify the language that the person is certified for."

### `language_pairs_required` — bool
- **what:** Whether the interpreter must demonstrate competency between English and at least one other language.
- **states:** UT
- **sample (UT):** "acts as a medical language interpreter between English and at least one other language"

## exam and knowledge requirements

### `exam_content_areas` — list[str]
- **what:** Specific subject-matter domains tested in the certification examination.
- **states:** UT
- **sample (UT):** "tests: basic language fluency... basic medical terminology... basic cultural competency relating to medical care beliefs and practices... knowledge and understanding of the national standards of practice... a basic understanding of medical confidentiality requirements, including the confidentiality requirements of the federal Health Insurance Portability and Accountability Act"

### `recognized_national_certification_bodies` — list[str]
- **what:** Named national organizations whose certification examinations are accepted by the state for credentialing purposes.
- **states:** UT
- **sample (UT):** "the National Board of Certification for Medical Interpreters; or the Certification Commission for Healthcare Interpreters"

## professional conduct and ethics

### `national_standards_adherence_required` — bool
- **what:** Whether the applicant must sign a statement agreeing to abide by a recognized national standards of practice document.
- **states:** UT
- **sample (UT):** "signs a statement agreeing to abide by the national standards of practice"

### `confidentiality_breach_as_unprofessional_conduct` — bool
- **what:** Whether willful or negligent disclosure of confidential patient information is explicitly enumerated as unprofessional conduct subject to discipline.
- **states:** UT
- **sample (UT):** "willful or negligent betrayal or disclosure of confidential information about which the certified medical language interpreter becomes knowledgeable as a result of or incidental to the certified medical language interpreter's practice"

## who must be licensed

### `compensation_required_for_regulation` — bool
- **what:** Whether the regulatory definition of a medical interpreter is limited to persons performing services for compensation (i.e., volunteers are excluded).
- **states:** UT
- **sample (UT):** "a person who, for compensation, performs verbal language interpretation services between a health care provider who speaks English and another person"
