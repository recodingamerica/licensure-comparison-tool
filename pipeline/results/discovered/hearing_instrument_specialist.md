# Discovered fields — hearing_instrument_specialist

## license types and tiers

### `license_tiers` — list[str]
- **what:** The named license classifications available under the statute for this profession.
- **states:** UT
- **sample (UT):** "The division shall issue to an individual qualified under the provisions of this chapter a license in the classification of: (a) hearing instrument specialist; or (b) hearing instrument intern."

### `intern_license_term_years` — int
- **what:** The fixed term in years for which an intern-level license is issued.
- **states:** UT
- **sample (UT):** "The division shall issue a license for a hearing instrument intern for a term of three years."

### `board_certification_required` — bool
- **what:** Whether the applicant must hold current board certification (e.g., NBC-HIS) as a condition of licensure or renewal.
- **states:** UT
- **sample (UT):** "have qualified for and currently hold board certification by the National Board for Certification - Hearing Instrument Sciences, or an equivalent certification approved by the division"

### `board_certification_body` — str
- **what:** The name of the national certifying body whose credential satisfies the board certification requirement.
- **states:** UT
- **sample (UT):** "board certification by the National Board for Certification - Hearing Instrument Sciences"

## equipment and technology standards

### `equipment_calibration_required_at_renewal` — bool
- **what:** Whether the licensee must demonstrate calibration of all technical instruments used in practice as a condition of license renewal.
- **states:** UT
- **sample (UT):** "calibration of all appropriate technical instruments used in practice"

### `circuitry_type_disclosure_required` — bool
- **what:** Whether the licensee must disclose the circuitry type (digital or analog) of a hearing instrument in advertisements, presentations, and purchase agreements.
- **states:** UT
- **sample (UT):** "failing to describe the circuitry in any advertisement, presentation, purchase, or trial agreement as being either 'digital' or 'analog'"

## patient protection and consumer rights

### `minor_patient_referral_required` — bool
- **what:** Whether the licensee is required to refer patients under a specified age to a physician or audiologist rather than testing and fitting them directly.
- **states:** UT
- **sample (UT):** "refer all individuals under the age of 18 who seek testing of hearing to a physician or surgeon, osteopathic physician, physician assistant, or audiologist"

### `minor_referral_age_threshold` — int
- **what:** The age below which a patient must be referred to another licensed provider rather than tested and fitted directly by the hearing instrument specialist.
- **states:** UT
- **sample (UT):** "refer all individuals under the age of 18 who seek testing of hearing to a physician or surgeon"

### `trial_period_days` — int
- **what:** The mandatory number of days a consumer has the right to cancel a hearing aid purchase and receive a refund.
- **states:** UT
- **sample (UT):** "provide the consumer with a 30-day right to cancel the purchase if the consumer finds that the hearing aid does not function adequately"

### `cancellation_fee_max_percent` — int
- **what:** The maximum percentage of total fees the seller may retain as a cancellation fee when a consumer exercises the right to cancel a hearing aid purchase.
- **states:** UT
- **sample (UT):** "the seller of the hearing aid is entitled to a cancellation fee not to exceed 15% of all fees charged to the consumer"

### `written_informed_consent_required` — bool
- **what:** Whether the licensee must obtain written informed consent from the patient before providing services or products.
- **states:** UT
- **sample (UT):** "obtain written informed consent from the patient regarding offered services, products, and the expected results of the services and products in a form approved by the division"

### `ada_assistive_listening_disclosure_required` — bool
- **what:** Whether the licensee must inform patients about hearing instruments compatible with ADA-compliant assistive listening systems before a sale.
- **states:** UT
- **sample (UT):** "inform each patient who is being offered a hearing instrument about hearing instruments that work with assistive listening systems that are compliant with the ADA Standards for Accessible Design"

## supervision and delegation

### `supervision_level_types` — list[str]
- **what:** The named levels of supervision defined in statute under which an intern may practice.
- **states:** UT
- **sample (UT):** "'Direct supervision' means that the supervising hearing instrument specialist is present in the same facility... 'Indirect supervision' means that the supervising hearing instrument specialist is not required to be present in the same facility"

### `supervisor_minimum_experience_years` — int
- **what:** The minimum number of years of full-time practice required before a licensee may serve as a supervising hearing instrument specialist.
- **states:** UT
- **sample (UT):** "has practiced full-time as a hearing instrument specialist for not less than two years"

### `indirect_supervision_practical_exam_required` — bool
- **what:** Whether a supervisor must pass a practical examination in hearing testing before being permitted to supervise an intern remotely (indirectly).
- **states:** UT
- **sample (UT):** "receives a passing score on a practical examination demonstrating acceptable skills in the area of hearing testing as approved by the division"

## who is exempt from needing this license

### `exempt_professions` — list[str]
- **what:** Other licensed professions explicitly exempted from needing a hearing instrument specialist license to perform overlapping acts.
- **states:** UT
- **sample (UT):** "an audiologist licensed under the provisions of Chapter 41... a physician and surgeon... osteopathic physician... physician assistant"

## practice setting and business rules

### `fixed_place_of_business_required` — bool
- **what:** Whether the licensee must maintain a regular physical place of business identified by street address.
- **states:** UT
- **sample (UT):** "have a regular place or places of business from which the person conducts business as a hearing instrument specialist and the place or places of business shall be represented to a patient and others with whom business is conducted by the street address"

### `device_condition_disclosure_required` — bool
- **what:** Whether the licensee must disclose in writing whether a hearing instrument sold to a patient is new, used, or reconditioned.
- **states:** UT
- **sample (UT):** "a statement whether any hearing instrument provided to a patient is 'new,' 'used,' or 'reconditioned' and the terms and conditions of any warranty or guarantee that applies to each instrument"
