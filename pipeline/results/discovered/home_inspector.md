# Discovered fields — home_inspector

## types of license and who can hold them

### `license_tier` — enum[home inspector - existing homes, home inspector - new homes, home inspector - joint/both, home inspector - general, associate/intern/trainee]
- **what:** The specific tier or category of home inspector credential, distinguishing between new-construction inspectors, existing-home inspectors, joint registrations, and entry-level supervised roles.
- **states:** AK, CT, DE, IL, IN, KY
- **sample (AK):** "an individual may not perform a home inspection for a residence (1) not previously occupied as a residence unless that individual is registered as a home inspector for new homes under this chapter; (2) previously occupied as a residence unless that individual is registered as a home inspector for existing homes under this chapter."

### `trainee_intern_registration_required` — bool
- **what:** Whether the state establishes a formal entry-level supervised credential (associate, intern, or trainee) that must be registered or permitted before performing inspections under supervision.
- **states:** AK, CT, DE, IL, KY
- **sample (DE):** "No person shall act as a home inspector trainee or hold himself or herself out to be a home inspector trainee unless such person has been duly registered by the Board under this chapter."

### `minimum_inspections_for_licensure` — int
- **what:** The minimum number of completed fee-paid home inspections required before an applicant qualifies for a full license.
- **states:** AL, CT, DE, KY
- **sample (CT):** "Have earned a home inspector intern permit and performed not less than one hundred home inspections in accordance with subsection (c) of section 20-493b"

### `entity_license_required` — bool
- **what:** Whether the state requires business entities (corporations, LLCs, partnerships) that offer home inspection services to obtain their own separate license in addition to the individual inspector's license.
- **states:** IL, KY
- **sample (IL):** "A corporation, limited liability company, partnership, or entity shall, as a condition of licensure, designate a managing licensed home inspector. The managing home inspector of any home inspector entity shall be responsible for the actions of all licensed and unlicensed employees, agents, and representatives of that home inspector entity."

## supervision and trainee rules

### `supervision_model` — enum[direct - supervisor on site 100% of time, direct for first N inspections then indirect, personal supervision throughout, general supervision]
- **what:** The required level of oversight a licensed home inspector must provide to a trainee or associate, ranging from constant on-site presence to general oversight.
- **states:** AK, CT, DE, KY
- **sample (CT):** "Such supervision shall be direct supervision for a minimum of the first ten inspections, and then may be indirect for the remaining training period. For the purpose of this section, 'direct supervision' means the supervisor shall be present at the site of a home inspection where the home inspector intern is assigned one hundred per cent of the time."

### `supervisor_liability_for_trainee` — bool
- **what:** Whether the supervising licensed home inspector is explicitly held legally responsible for all inspection work performed by the trainee or associate under their supervision.
- **states:** AK, CT, DE, KY
- **sample (AK):** "A registered home inspector who employs an associate home inspector under (d) of this section is liable for the work done by the associate home inspector."

### `trainee_cosign_permitted` — bool
- **what:** Whether a trainee or intern is explicitly permitted to co-sign a home inspection report alongside the supervising licensed inspector.
- **states:** AK, CT, DE
- **sample (DE):** "The trainee may assist in the completion of a home inspection report, and may co-sign a home inspection report, provided that the trainee has been under the personal supervision of the licensed home inspector, and provided further that the licensed home inspector shall review and sign the home inspection report."

## insurance and financial responsibility

### `errors_and_omissions_insurance_required` — bool
- **what:** Whether the state explicitly requires errors and omissions (E&O) insurance in addition to general liability insurance.
- **states:** AL, AZ, DE
- **sample (AL):** "evidence of insurance against the errors and omissions of the home inspector in an amount and form to be prescribed by the Building Commission"

### `surety_bond_required` — bool
- **what:** Whether the state requires a surety bond (or equivalent cash deposit) as a condition of licensure, as an alternative or supplement to liability insurance.
- **states:** AK, AZ
- **sample (AK):** "each applicant shall, at the time of applying for a certificate of registration, file with the commissioner a surety bond running to the state... The amount of the bond for a... mechanical or specialty contractor or home inspector shall be $10,000"

### `general_liability_minimum_coverage` — str
- **what:** The minimum dollar amount of general liability insurance coverage required for licensure, expressed as a free-form string because amounts vary across states.
- **states:** AL, AR, AZ, IL, IN, KY
- **sample (IN):** "Provides for general liability coverage of at least one hundred thousand dollars ($100,000)"

## inspection report rules

### `inspection_report_validity_period_days` — int
- **what:** The number of days a signed home inspection report remains valid after the date the inspector signs it.
- **states:** AK
- **sample (AK):** "A home inspection report is valid for 180 days after the date the home inspector signs and dates the report."

### `pre_inspection_agreement_required` — bool
- **what:** Whether the inspector must provide a written pre-inspection document or agreement to the client before performing the inspection, specifying scope and other disclosures.
- **states:** AK, IL, IN, KY
- **sample (AK):** "Before performing a home inspection, a registered home inspector or associate home inspector shall provide to the person on whose behalf a home is inspected a written document that includes the home inspector's registration number and that specifies (1) the scope of intended inspection"

### `report_must_list_uninspected_components` — bool
- **what:** Whether the written home inspection report must explicitly list any systems or components that were designated for inspection but were not inspected, along with the reason.
- **states:** IN, KY
- **sample (IN):** "A list of any systems or components that were designated for inspection in the standards of performance adopted by the board but that were not inspected. The reason a system or component listed under subdivision (3) was not inspected."

### `report_must_disclaim_environmental_hazards` — bool
- **what:** Whether the home inspection report must include a written statement that it does not address environmental hazards such as lead, radon, asbestos, mold, or similar substances.
- **states:** IN, KY
- **sample (IN):** "A statement that the report does not address environmental hazards, including: (A) lead-based paint; (B) radon; (C) asbestos; (D) cockroaches; (E) rodents; (F) pesticides; (G) treated lumber; (H) mold; (I) mercury; (J) carbon monoxide; or (K) other similar environmental hazards."

### `inspection_report_record_retention_years` — int
- **what:** The minimum number of years a licensee must retain copies of home inspection reports and related contracts.
- **states:** IL
- **sample (IL):** "A person licensed under this Act shall retain the original or a true and exact copy of all written contracts that engage the licensee's services as a home inspector and all home inspection reports... for a period of 5 years or 2 years after the final disposition of any judicial proceeding"

## ethics and conflicts of interest

### `prohibited_conflict_of_interest_practices` — list[str]
- **what:** Specific business practices explicitly prohibited as conflicts of interest or unfair practices, such as performing repairs on inspected properties, inspecting properties with a financial interest, or accepting contingent fees.
- **states:** AK, AR, CA, IL, IN, KY
- **sample (AR):** "It is an unfair business practice for a home inspector... to do any of the following: (1) Perform or offer to perform for an additional fee any repairs to the property on which the home inspector or the home inspector's company has prepared a home inspection report in the past twelve (12) months; (2) Inspect for a fee any property in which the home inspector or the home inspector's company has any financial interest or any interest in the transfer of the property; (3) Offer or deliver any compensation, inducement, or reward to the owner of the inspected property, the broker, or the agent for the referral of any business; (4) Accept an engagement... in which the employment itself or the fee payable for the home inspection is contingent upon the conclusions in the home inspection report"

### `liability_waiver_clauses_void` — bool
- **what:** Whether the state explicitly voids contractual provisions that attempt to limit the home inspector's liability to the cost of the inspection report or waive the inspector's duty of care.
- **states:** AK, CA
- **sample (AK):** "Contractual provisions that purport to limit the liability of a home inspector to the cost of the home inspection report are contrary to public policy and void."

### `statute_of_limitations_years` — int
- **what:** The number of years within which a legal action against a home inspector based on a home inspection report must be commenced.
- **states:** AK
- **sample (AK):** "a person may not bring an action against an individual registered under this chapter based on a home inspection report unless the action is commenced within one year."

### `inspector_valuation_opinion_prohibited` — bool
- **what:** Whether the state explicitly prohibits a home inspector from giving an opinion of property valuation.
- **states:** CA, IL
- **sample (CA):** "A home inspector shall not give an opinion of valuation on a property."

## professional standards and approved organizations

### `standards_of_practice_body` — list[str]
- **what:** Named professional organizations whose standards of practice are recognized or required by the state for conducting home inspections.
- **states:** AK, AL, AR, DE, KY
- **sample (KY):** "Require all fee-paid home inspections to be conducted in accordance with the standards of practice of: (a) The American Society of Home Inspectors; (b) The International Association of Certified Home Inspectors; or (c) Any other approved standards of practice"

### `approved_exam_bodies` — list[str]
- **what:** Named national organizations whose examinations are approved or required for home inspector licensure.
- **states:** AK, AL, AR, AZ, CT, DE, IL, IN, … (+1)
- **sample (AK):** "the appropriate home inspection examination for an individual who applies to be registered for inspection of (A) existing homes is the examination offered by the American Society of Home Inspectors or National Association of Home Inspectors; (B) new homes or for a joint registration is the examination offered by the International Code Council"

## what the inspection must cover

### `pool_spa_safety_inspection_required` — bool
- **what:** Whether the state requires that home inspections of properties with a swimming pool or spa include a specific examination of drowning prevention safety features.
- **states:** CA
- **sample (CA):** "In connection with the transfer... of real property with a swimming pool or spa, an appropriate inspection shall include a noninvasive physical examination of the pool or spa and dwelling for the purpose of identifying which, if any, of the seven drowning prevention safety features listed in subdivision (a) of Section 115922 of the Health and Safety Code the pool or spa is equipped"

### `energy_efficiency_inspection_optional` — bool
- **what:** Whether the state explicitly authorizes or encourages an optional energy efficiency component to the home inspection if requested by the client.
- **states:** CA
- **sample (CA):** "'Home inspection,' if requested by the client, may include an inspection of energy efficiency. Energy efficiency items to be inspected may include the following: (A) A noninvasive inspection of insulation R-values in attics, roofs, walls, floors, and ducts."

### `smoke_detector_reporting_required` — bool
- **what:** Whether the state requires the home inspection report to specifically address the presence, location, quantity, testability, and age of smoke detection equipment.
- **states:** CT
- **sample (CT):** "The minimum and uniform standard for a home inspection shall include a requirement that a home inspector report on the presence of smoke detection and warning equipment and specify where such equipment is located, the total number of such equipment, whether the home inspector is able to test such equipment, and whether the home inspector is able to verify that such equipment was less than ten years old."

### `code_compliance_inspection_excluded` — bool
- **what:** Whether the state explicitly excludes code compliance inspections from the definition of a home inspection.
- **states:** IN, KY
- **sample (IN):** "The term does not include a code compliance inspection."

### `residential_unit_maximum` — int
- **what:** The maximum number of dwelling units in a structure that falls within the definition of a residential property subject to home inspection licensing requirements.
- **states:** AK, AL, AR, CA, CT, DE, IL, IN, … (+1)
- **sample (IN):** "Residential dwelling means a structure consisting of at least one (1) but not more than five (5) units, each designed for occupancy by a single family"
