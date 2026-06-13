# Discovered fields — acupuncture

## credentials and certifications beyond the basic license

### `nccaom_certification_required` — bool
- **what:** Whether current active NCCAOM certification is required for initial licensure and/or renewal.
- **states:** UT
- **sample (UT):** "meet the requirements for current active certification in acupuncture under guidelines established by the National Commission for the Certification of Acupuncture and Oriental Medicine (NCCAOM) as demonstrated through a current certificate or other appropriate documentation"

### `clean_needle_technique_certificate_required_for_injection` — bool
- **what:** Whether a clean needle technique certificate from NCCAOM is required before a licensee may perform injection therapy.
- **states:** UT
- **sample (UT):** "a licensed acupuncturist who has obtained a clean needle technique certificate from the National Commission for the Certification of Acupuncture and Oriental Medicine (NCCAOM)"

## injections and substances that can be administered

### `injection_therapy_authorized` — bool
- **what:** Whether licensed acupuncturists are authorized to perform injection therapy using a hypodermic needle into acupuncture points.
- **states:** UT
- **sample (UT):** "'Injection therapy' means the use of a hypodermic needle, by a licensed acupuncturist who has obtained a clean needle technique certificate from the National Commission for the Certification of Acupuncture and Oriental Medicine (NCCAOM), to inject any of the following sterile substances in liquid form into acupuncture points on the body subcutaneously or intramuscularly"

### `injectable_substances_authorized` — list[str]
- **what:** List of sterile substances that a licensed acupuncturist is authorized to inject during injection therapy.
- **states:** UT
- **sample (UT):** "a nutritional substance; a local anesthetic; autologous blood, if the licensee holds a current phlebotomy certification to draw blood; sterile water; dextrose; sodium bicarbonate; and sterile saline"

### `injection_therapy_excluded_sites` — list[str]
- **what:** Anatomical sites into which injection therapy is explicitly prohibited.
- **states:** UT
- **sample (UT):** "'Injection therapy' does not include injecting a substance into a vein, joint, artery, blood vessel, nerve, tendon, deep organ, or the spine."

### `injection_therapy_patient_exclusions` — list[str]
- **what:** Patient populations on whom injection therapy is prohibited (e.g., pregnant women, young children).
- **states:** UT
- **sample (UT):** "'Injection therapy' may not be performed on a pregnant woman or a child under the age of eight."

## what treatments and techniques are allowed

### `adjunctive_therapies_authorized` — list[str]
- **what:** List of adjunctive or supplementary therapy modalities authorized within the scope of acupuncture practice.
- **states:** UT
- **sample (UT):** "Adjunctive therapies within the scope of the practice of acupuncture may include: manual, mechanical, thermal, electrical, light, and electromagnetic treatments based on traditional oriental medical diagnosis and modern research"

### `dietary_and_herbal_recommendations_authorized` — bool
- **what:** Whether the licensee is authorized to recommend or provide dietary guidelines, herbs, supplements, homeopathics, and therapeutic exercise.
- **states:** UT
- **sample (UT):** "the recommendation, administration, or provision of dietary guidelines, herbs, supplements, homeopathics, and therapeutic exercise based on traditional oriental medical diagnosis and modern research according to practitioner training"

### `animal_acupuncture_authorized` — bool
- **what:** Whether the practice of acupuncture on animals is permitted within the scope of the license, subject to applicable conditions.
- **states:** UT
- **sample (UT):** "the practice described in Subsections (5)(a) and (b) on an animal to the extent permitted by Subsection 58-28-307(12); the provisions of this chapter; and division rule"

### `moxibustion_authorized` — bool
- **what:** Whether moxibustion (heat therapy using the herb moxa applied to acupuncture points) is explicitly authorized within the scope of practice.
- **states:** UT
- **sample (UT):** "'Moxibustion' means a heat therapy that uses the herb moxa to heat acupuncture points of the body."

### `scope_exclusions` — list[str]
- **what:** Procedures or techniques explicitly excluded from the acupuncture scope of practice.
- **states:** UT
- **sample (UT):** "'Practice of acupuncture' does not include: the manual manipulation or adjustment of the joints of the body beyond the elastic barrier; or the 'manipulation of the articulation of the spinal column'"

## who else can practice without this license

### `license_exempt_practitioner_types` — list[str]
- **what:** Categories of other licensed professionals who may practice acupuncture without holding an acupuncturist license.
- **states:** UT
- **sample (UT):** "an individual licensed as a physician and surgeon or osteopathic physician and surgeon... a commissioned physician or surgeon serving in the armed forces... a chiropractic physician licensed under Chapter 73"

## professional title and credential display rules

### `authorized_professional_title` — str
- **what:** The official title and abbreviation a licensee is authorized to use in conjunction with their name or practice.
- **states:** UT
- **sample (UT):** "'Licensed acupuncturist,' designated as 'L.Ac.,' means a person who has been licensed under this chapter to practice acupuncture."

### `prohibited_titles` — list[str]
- **what:** Titles that a licensed acupuncturist is explicitly prohibited from using in connection with their practice.
- **states:** UT
- **sample (UT):** "A licensed acupuncturist may not use the term 'physician,' 'physician or surgeon,' or 'doctor' in conjunction with the acupuncturist's name or practice."

## patient rights and practice obligations

### `informed_consent_procedures_required` — bool
- **what:** Whether applicants must establish procedures enabling patients to give informed consent to treatment as a condition of licensure.
- **states:** UT
- **sample (UT):** "establish procedures, as defined by rule, which shall enable patients to give informed consent to treatment"
