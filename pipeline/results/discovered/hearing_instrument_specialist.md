# Discovered fields — hearing_instrument_specialist

## license types and trainee status

### `license_tiers` — list[str]
- **what:** The named license classifications available under the state's regulatory scheme for this profession.
- **states:** PA, UT
- **sample (UT):** "The division shall issue to an individual qualified under the provisions of this chapter a license in the classification of: (a) hearing instrument specialist; or (b) hearing instrument intern."

### `trainee_license_name` — enum[apprentice fitter, hearing instrument intern]
- **what:** The specific name given to the entry-level or trainee license tier that requires supervision before full licensure.
- **states:** PA, UT
- **sample (PA):** "An applicant who has fulfilled the requirements of section 301 and has made application therefor... may have an apprentice fitter's registration certificate issued to him."

### `trainee_license_term_years` — int
- **what:** The fixed term in years for which a trainee or intern license is issued.
- **states:** PA, UT
- **sample (UT):** "The division shall issue a license for a hearing instrument intern for a term of three years."

## supervision and delegation

### `direct_supervision_defined` — bool
- **what:** Whether the statute explicitly defines 'direct supervision' for trainees or interns.
- **states:** PA, UT
- **sample (UT):** "'Direct supervision' means that the supervising hearing instrument specialist is present in the same facility as is the person being supervised and is available for immediate in person consultation."

### `indirect_supervision_available` — bool
- **what:** Whether the statute permits a trainee or intern to practice under indirect (remote) supervision under specified conditions.
- **states:** PA, UT
- **sample (UT):** "A hearing instrument intern may practice under the indirect supervision of a licensed hearing instrument specialist if the hearing instrument specialist: (a) receives a passing score on a practical examination..."

### `supervisor_minimum_experience_years` — int
- **what:** The minimum number of years of full-time practice required before a licensee may serve as an approved supervisor for trainees or interns.
- **states:** PA, UT
- **sample (UT):** "has practiced full-time as a hearing instrument specialist for not less than two years"

## patient safety and medical referral rules

### `medical_referral_required_conditions` — list[str]
- **what:** Specific clinical conditions that, when observed or reported, require the practitioner to refer the patient to a physician before fitting or selling a hearing aid.
- **states:** PA, UT
- **sample (PA):** "Visible congenital or traumatic deformity of the ear... Active drainage from the ear within the previous 90 days... Sudden or rapidly progressive hearing loss within the previous 90 days... Acute or chronic dizziness... Unilateral hearing loss of sudden or recent onset within the previous 90 days... Visible evidence of cerumen accumulation or a foreign body in the ear canal... Pain in the ear within the previous 90 days."

### `minor_patient_age_threshold` — int
- **what:** The age at or below which a patient must be referred to a physician or audiologist and may only receive a hearing aid by prescription.
- **states:** PA, UT
- **sample (PA):** "No hearing aid shall be sold by an individual registered under this act to a person 18 years of age or younger, unless within the preceding six months a recommendation for a hearing aid has been made by a physician specializing in otolaryngology or otology."

### `pre_sale_medical_exam_required` — bool
- **what:** Whether the statute requires a medical examination by a physician within a specified period before a hearing aid may be sold.
- **states:** PA, UT
- **sample (PA):** "No hearing aid is to be sold to any individual unless, within the preceding six months, the individual has been examined by an otologist or otolaryngologist or any licensed physician, and a written recommendation has been made by such physician that the use of a hearing aid may be beneficial."

### `medical_exam_waiver_permitted` — bool
- **what:** Whether a consumer may sign a written waiver to forgo the required pre-sale medical examination.
- **states:** PA, UT
- **sample (PA):** "This section does not apply to... any individual who signs a written waiver as set forth in this section."

## consumer protection and sale requirements

### `return_period_days` — int
- **what:** The mandatory number of days during which a consumer may return a hearing aid for a refund after purchase.
- **states:** PA, UT
- **sample (PA):** "No hearing aid shall be sold to any person unless accompanied by a 30-day money-back written guarantee providing that if the person returns the hearing aid in the same condition, ordinary wear and tear excluded, as when purchased within 30 days of the date of delivery, the customer shall be entitled to the refund of the purchase price."

### `cancellation_fee_cap` — str
- **what:** The maximum cancellation or restocking fee a seller may retain when a consumer exercises the right to return a hearing aid.
- **states:** PA, UT
- **sample (UT):** "Upon exercise of the right to cancel a hearing aid purchase, the seller of the hearing aid is entitled to a cancellation fee not to exceed 15% of all fees charged to the consumer, including testing, fitting, counseling, and the purchase price of the hearing aid."

### `written_receipt_required` — bool
- **what:** Whether the practitioner is required to provide a written receipt or written contract to the consumer at the time of sale.
- **states:** PA, UT
- **sample (PA):** "A registrant shall, upon the consummation of a sale of a hearing aid, deliver to the purchaser a written receipt, signed by or on behalf of the registrant."

### `device_condition_disclosure_required` — bool
- **what:** Whether the practitioner must disclose in writing whether a hearing aid is new, used, or reconditioned at the time of sale.
- **states:** PA, UT
- **sample (UT):** "a statement whether any hearing instrument provided to a patient is 'new,' 'used,' or 'reconditioned' and the terms and conditions of any warranty or guarantee that applies to each instrument"

### `informed_consent_required` — bool
- **what:** Whether the practitioner must obtain written informed consent from the patient before providing services or fitting a hearing instrument.
- **states:** PA, UT
- **sample (UT):** "obtain written informed consent from the patient regarding offered services, products, and the expected results of the services and products in a form approved by the division"

### `non_medical_disclaimer_required` — bool
- **what:** Whether the practitioner must affirmatively disclose to the consumer that their services do not constitute a medical examination, diagnosis, or prescription.
- **states:** PA, UT
- **sample (PA):** "The registrant shall, at the outset of his relationship with the potential purchaser, advise such person that any examination or representation made by a registered hearing aid dealer or fitter in connection with the practice of fitting and selling of his hearing aid is not an examination, diagnosis or prescription by a person licensed to practice medicine."

## equipment and facility standards

### `required_testing_equipment` — list[str]
- **what:** Specific equipment that the statute requires a practitioner to maintain and use in the fitting process.
- **states:** PA, UT
- **sample (PA):** "An audiometer conforming at all times to specifications for pure-tone and speech diagnostic audiometers as established by the department, and subject to periodic inspection and calibration by the department."

### `equipment_calibration_required` — bool
- **what:** Whether the statute explicitly requires that testing and fitting equipment be kept properly calibrated.
- **states:** PA, UT
- **sample (UT):** "calibration of all appropriate technical instruments used in practice"

### `fixed_place_of_business_required` — bool
- **what:** Whether the practitioner is required to maintain a regular, established physical place of business.
- **states:** PA, UT
- **sample (UT):** "have a regular place or places of business from which the person conducts business as a hearing instrument specialist and the place or places of business shall be represented to a patient and others with whom business is conducted by the street address at which the place of business is located"

### `record_retention_years` — int
- **what:** The minimum number of years a practitioner must retain patient and transaction records.
- **states:** PA, UT
- **sample (PA):** "each such record shall be kept and maintained for a seven-year period"

## who is exempt from needing this license

### `exempted_professions` — list[str]
- **what:** Other licensed professions explicitly exempted from needing a hearing instrument specialist license to perform overlapping acts.
- **states:** PA, UT
- **sample (UT):** "the following persons may engage in acts and practices included within the definition of practice as a hearing instrument specialist or hearing instrument intern... without being licensed under this chapter: (1) an audiologist... (2) a physician and surgeon... or osteopathic physician... and (3) a physician assistant"

## extra credentials and tiered scope

### `national_board_certification_required` — bool
- **what:** Whether the applicant must hold or qualify for certification from the National Board for Certification in Hearing Instrument Sciences (or equivalent) as a condition of licensure.
- **states:** PA, UT
- **sample (UT):** "have qualified for and currently hold board certification by the National Board for Certification - Hearing Instrument Sciences, or an equivalent certification approved by the division"

### `referral_fee_prohibition` — bool
- **what:** Whether the statute explicitly prohibits paying or receiving compensation for patient referrals.
- **states:** PA, UT
- **sample (UT):** "paying any professional person any consideration of any kind for referral of a patient"
