# Discovered fields — acupuncture

## extra credentials and tiered scope

### `oriental_medicine_endorsement_available` — bool
- **what:** Whether the state offers a distinct higher-tier credential (e.g., practitioner of Oriental medicine) that expands scope beyond basic acupuncture licensure.
- **states:** PA, UT
- **sample (PA):** "An acupuncturist may practice Oriental medicine if the acupuncturist is licensed with the board as a practitioner of Oriental medicine."

### `oriental_medicine_endorsement_requirements` — list[str]
- **what:** Requirements to obtain the higher-tier Oriental medicine or herbal therapy credential, such as completing an herbology program or passing a national herbology exam.
- **states:** PA, UT
- **sample (PA):** "has successfully completed an acupuncture education program that includes the study of East Asian herbology and passed an East Asian herbology examination approved by the board; or has obtained national certification in East Asian herbology or Oriental medicine from a certifying organization approved by the board"

### `herbal_therapy_authorized` — bool
- **what:** Whether licensed acupuncturists (with appropriate endorsement) are authorized to use herbal preparations or recommend herbs and supplements as part of practice.
- **states:** PA, UT
- **sample (PA):** "The use of herbal preparations and products that contain as active ingredients parts of plants, minerals and other organic materials or a combination of these items administered according to East Asian medicine tradition to normalize function."

### `injection_therapy_authorized` — bool
- **what:** Whether licensed acupuncturists may perform injection therapy (injecting sterile substances into acupuncture points) with additional certification.
- **states:** PA, UT
- **sample (UT):** ""Injection therapy" means the use of a hypodermic needle, by a licensed acupuncturist who has obtained a clean needle technique certificate from the National Commission for the Certification of Acupuncture and Oriental Medicine (NCCAOM), to inject any of the following sterile substances in liquid form into acupuncture points on the body subcutaneously or intramuscularly."

### `injection_therapy_permitted_substances` — list[str]
- **what:** Specific sterile substances that a licensed acupuncturist is authorized to inject during injection therapy.
- **states:** PA, UT
- **sample (UT):** "a nutritional substance; a local anesthetic; autologous blood, if the licensee holds a current phlebotomy certification to draw blood; sterile water; dextrose; sodium bicarbonate; and sterile saline."

## what they can treat and where on the body

### `injection_therapy_excluded_sites` — list[str]
- **what:** Anatomical sites explicitly excluded from injection therapy.
- **states:** PA, UT
- **sample (UT):** ""Injection therapy" does not include injecting a substance into a vein, joint, artery, blood vessel, nerve, tendon, deep organ, or the spine."

### `injection_therapy_patient_exclusions` — list[str]
- **what:** Patient populations on whom injection therapy is explicitly prohibited.
- **states:** PA, UT
- **sample (UT):** ""Injection therapy" may not be performed on a pregnant woman or a child under the age of eight."

### `adjunctive_therapies_authorized` — list[str]
- **what:** Non-needle supplemental or adjunctive modalities explicitly authorized within the acupuncture scope of practice.
- **states:** PA, UT
- **sample (PA):** "the use of traditional and modern oriental therapeutics, heat therapy, moxibustion, electrical and low-level laser stimulation, acupressure and other forms of massage, herbal therapy and counseling that shall include the therapeutic use of foods and supplements and lifestyle modifications"

### `scope_exclusions` — list[str]
- **what:** Procedures or activities explicitly excluded from the acupuncture scope of practice.
- **states:** PA, UT
- **sample (UT):** ""Practice of acupuncture" does not include: the manual manipulation or adjustment of the joints of the body beyond the elastic barrier; or the "manipulation of the articulation of the spinal column""

### `animal_acupuncture_permitted` — bool
- **what:** Whether licensed acupuncturists are explicitly permitted to practice acupuncture on animals under specified conditions.
- **states:** PA, UT
- **sample (UT):** "the practice described in Subsections (5)(a) and (b) on an animal to the extent permitted by Subsection 58-28-307(12); the provisions of this chapter; and division rule."

## supervision and delegation

### `physician_diagnosis_requirement` — bool
- **what:** Whether a physician diagnosis is required before or after a certain period of acupuncture treatment.
- **states:** PA, UT
- **sample (PA):** "an acupuncturist may treat a person's condition without the condition being diagnosed by a licensed physician, dentist or podiatrist for 60 calendar days from the date of the first treatment."

### `physician_diagnosis_grace_period_days` — int
- **what:** Number of days an acupuncturist may treat a patient without a physician diagnosis before one is required.
- **states:** PA, UT
- **sample (PA):** "an acupuncturist may treat a person's condition without the condition being diagnosed by a licensed physician, dentist or podiatrist for 60 calendar days from the date of the first treatment."

### `student_supervision_requirements` — str
- **what:** Rules governing supervision of acupuncture students performing procedures in educational settings.
- **states:** PA, UT
- **sample (PA):** "students enrolled in an acupuncture educational program from performing acupuncture or supplemental acupuncture techniques in the course of their instruction, provided that a licensed physician is readily available for consultations and that an acupuncturist is on site and responsible for the direct supervision of students."

### `licensure_exempt_professions` — list[str]
- **what:** Other licensed health professions explicitly exempt from acupuncture licensure requirements when practicing acupuncture within their own scope.
- **states:** PA, UT
- **sample (PA):** "A dentist performing acupuncture in connection with the practice of dentistry, a podiatrist performing acupuncture in connection with the practice of podiatry or a veterinarian performing acupuncture on animals in connection with the practice of veterinary medicine."

## national certification and professional standards

### `nccaom_certification_required` — bool
- **what:** Whether current active NCCAOM (National Commission for the Certification of Acupuncture and Oriental Medicine) certification is required for initial licensure or renewal.
- **states:** PA, UT
- **sample (UT):** "meet the requirements for current active certification in acupuncture under guidelines established by the National Commission for the Certification of Acupuncture and Oriental Medicine (NCCAOM) as demonstrated through a current certificate or other appropriate documentation"

### `clean_needle_technique_certificate_required` — bool
- **what:** Whether a clean needle technique certificate (from NCCAOM or equivalent) is required to perform injection therapy.
- **states:** PA, UT
- **sample (UT):** "a licensee who has received the necessary training to practice injection therapy, including having obtained a clean needle technique certificate from the National Commission for the Certification of Acupuncture and Oriental Medicine (NCCAOM)"

### `informed_consent_required` — bool
- **what:** Whether the statute explicitly requires the acupuncturist to establish procedures enabling patients to give informed consent to treatment.
- **states:** PA, UT
- **sample (UT):** "establish procedures, as defined by rule, which shall enable patients to give informed consent to treatment"

## insurance and financial responsibility

### `professional_liability_insurance_required` — bool
- **what:** Whether the statute explicitly requires licensees to maintain professional liability insurance.
- **states:** PA, UT
- **sample (PA):** "A licensee shall obtain and maintain, to the satisfaction of the board, professional liability insurance coverage in accordance with the provisions of this section."

### `professional_liability_insurance_minimum_per_occurrence` — int
- **what:** Minimum required professional liability insurance coverage per occurrence in dollars.
- **states:** PA, UT
- **sample (PA):** "A licensee under this act, practicing in this Commonwealth, shall maintain a level of professional liability insurance coverage in the minimum amount of $1,000,000 per occurrence or claims made."

## professional titles and identification

### `title_restrictions` — list[str]
- **what:** Specific title terms that are restricted or prohibited for use by licensed acupuncturists.
- **states:** PA, UT
- **sample (UT):** "A licensed acupuncturist may not use the term "physician," "physician or surgeon," or "doctor" in conjunction with the acupuncturist's name or practice."

### `required_display_title` — str
- **what:** The specific title or badge text that a licensee is required to display to patients.
- **states:** PA, UT
- **sample (PA):** "an acupuncturist shall wear a tag or badge with lettering clearly visible to the patient bearing the acupuncturist's name and the title "acupuncturist.""

### `medical_practice_not_authorized` — bool
- **what:** Whether the statute explicitly states that an acupuncture license does not authorize the practice of medicine.
- **states:** PA, UT
- **sample (UT):** "Nothing in this chapter may be construed to permit the practice of medicine nor require direct payment from third party insurers directly to a person engaged in the practice of acupuncture."
