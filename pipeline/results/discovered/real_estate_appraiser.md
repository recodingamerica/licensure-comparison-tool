# Discovered fields — real_estate_appraiser

## license tiers and credential types

### `credential_tiers` — list[str]
- **what:** The distinct credential levels or classifications available under the state's appraiser licensure framework.
- **states:** PA
- **sample (PA):** "There shall be three classes of certified real estate appraisers as follows: (1) Certified residential appraiser... (2) Certified general appraiser... (3) Broker/appraiser"

## what they can appraise and under what authority

### `federally_related_transaction_scope` — bool
- **what:** Whether the credential authorizes appraisals required by FIRREA for federally related transactions.
- **states:** PA
- **sample (PA):** "to perform appraisals required by the Financial Institutions Reform, Recovery, and Enforcement Act of 1989 (Public Law 101-73, 103 Stat. 183) to be performed by a State-certified or State-licensed real estate appraiser"

### `nonfederally_related_transaction_scope` — bool
- **what:** Whether the credential authorizes appraisals in non-federally related transactions.
- **states:** PA
- **sample (PA):** "Persons who are certified as residential real estate appraisers and general real estate appraisers under this act shall also have authority to perform real estate appraisals in nonfederally related transactions appropriate to their certification classification."

### `property_type_scope` — enum[residential only, residential and nonresidential, broker-permitted only]
- **what:** The category of real property types the credential holder is authorized to appraise.
- **states:** PA
- **sample (PA):** "Certified general appraiser, which shall consist of those persons applying for and granted certification relating to the appraisal of both residential and nonresidential real property without limitation"

## supervision and delegation

### `trainee_supervision_required` — bool
- **what:** Whether appraiser trainees must operate under the direct supervision of a certified appraiser.
- **states:** PA
- **sample (PA):** "An appraiser trainee shall operate under the direct supervision of one certified residential appraiser or certified general appraiser for the purpose of completing the experience requirement for an appraiser credential."

### `supervisor_experience_years` — int
- **what:** Minimum years of experience a supervising appraiser must have before supervising trainees.
- **states:** PA
- **sample (PA):** "The supervisory appraiser shall be in good standing, have at least five years of experience as a certified residential appraiser or certified general appraiser"

### `max_trainees_per_supervisor` — int
- **what:** Maximum number of appraiser trainees a single supervising appraiser may supervise at one time.
- **states:** PA
- **sample (PA):** "shall not supervise more than three appraiser trainees"

## temporary and reciprocal practice

### `temporary_practice_permitted` — bool
- **what:** Whether out-of-state appraisers may temporarily practice in the state without full licensure.
- **states:** PA
- **sample (PA):** "the board shall recognize on a temporary basis the certification or license of an appraiser issued by another state if: (1) the property to be appraised is part of a federally related transaction; (2) the appraiser's business is of a temporary nature; and (3) the appraiser registers with the board."

### `temporary_practice_conditions` — list[str]
- **what:** Conditions that must be met for an out-of-state appraiser to practice temporarily in the state.
- **states:** PA
- **sample (PA):** "the property to be appraised is part of a federally related transaction; the appraiser's business is of a temporary nature; and the appraiser registers with the board."

## ongoing reporting and recordkeeping obligations

### `multi_state_licensure_reporting_required` — bool
- **what:** Whether appraisers holding credentials in multiple states must report that fact and any out-of-state disciplinary actions to the home-state board.
- **states:** PA
- **sample (PA):** "Any appraiser certified in this Commonwealth who is also certified or licensed to perform appraisals in any other state, territory or country shall report this information to the board on the biennial renewal application. Any disciplinary action taken in any other state, territory or country shall be reported to the board on the biennial renewal application, or within 90 days of disposition, whichever is sooner."

## prohibited compensation and conflict of interest rules

### `contingent_fee_prohibited` — bool
- **what:** Whether it is prohibited to base appraiser compensation on the outcome, value conclusion, or a percentage of the appraised value.
- **states:** PA
- **sample (PA):** "Accepting an appraisal assignment when the employment itself is contingent upon the appraiser's reporting a predetermined analysis or opinion, or where the fee to be paid for the performance of the appraisal assignment is contingent upon the opinion, conclusion or valuation reached"

### `percentage_fee_prohibited` — bool
- **what:** Whether basing appraiser fees on a percentage of the final estimated value is explicitly prohibited.
- **states:** PA
- **sample (PA):** "Basing the fee or compensation on a percentage of the final estimate of value."

### `commission_split_fee_prohibited` — bool
- **what:** Whether accepting compensation in the form of commissions, rebates, or division of brokerage commissions is prohibited.
- **states:** PA
- **sample (PA):** "Contracting for or accepting compensation for appraisal services in the form of a commission, rebate, division of brokerage commissions or any other similar form."

## education and qualifying coursework rules

### `qualifying_education_credit_for_prior_coursework` — bool
- **what:** Whether the board may grant credit toward qualifying education requirements for classroom hours completed before the board defined the required subjects.
- **states:** PA
- **sample (PA):** "the board may give credit to an applicant for classroom hours of academic experience successfully completed prior to the board's prescription and definition of subjects pursuant to this subsection."

### `continuing_education_excluded_topics` — list[str]
- **what:** Topics explicitly excluded from counting toward continuing education credit.
- **states:** PA
- **sample (PA):** "No credit shall be given for any course in office management or practice building."

### `trainee_qualifying_education_counts_toward_ce` — bool
- **what:** Whether qualifying education completed after licensure as a trainee may also satisfy continuing education requirements during the same renewal period.
- **states:** PA
- **sample (PA):** "any qualifying education completed after the issuance of the license and during the biennial licensure period may also be applied to satisfy the licensed appraiser trainee's continuing education requirements under this subsection."

## discipline, reinstatement, and enforcement

### `revocation_reinstatement_waiting_period_years` — int
- **what:** Minimum number of years a person must wait after revocation before applying for reinstatement of their credential.
- **states:** PA
- **sample (PA):** "Any person whose certificate or license has been revoked may apply for reinstatement, after a period of at least five years"

## professional standards and federal compliance

### `appraisal_standards_reference` — str
- **what:** The named national or federal standards framework that governs how appraisals must be developed and communicated.
- **states:** PA
- **sample (PA):** "standards of professional appraisal practice requiring that appraisals be performed in accordance with generally accepted appraisal standards as required pursuant to the Financial Institutions Reform, Recovery, and Enforcement Act of 1989"

### `qualifications_board_reference` — str
- **what:** The named national body whose qualification criteria the state adopts for education and experience requirements.
- **states:** PA
- **sample (PA):** "in accordance with the criteria established by the Appraiser Qualifications Board of the Appraisal Foundation required pursuant to the Financial Institutions Reform, Recovery, and Enforcement Act of 1989"
