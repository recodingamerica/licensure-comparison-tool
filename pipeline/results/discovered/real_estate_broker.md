# Discovered fields — real_estate_broker

## license types and tiers

### `license_tiers` — list[str]
- **what:** The distinct license categories recognized under the act, each with its own qualifications and scope.
- **states:** PA
- **sample (PA):** "It shall be unlawful for any person, directly or indirectly, to engage in or conduct, or to advertise or hold himself out as engaging in or conducting the business, or acting in the capacity of a broker or salesperson, cemetery broker, cemetery salesperson, campground membership salesperson, time-share salesperson, builder-owner salesperson, rental listing referral agent or cemetery company within this Commonwealth without first being licensed or registered."

### `broker_of_record_required` — bool
- **what:** Whether a corporation, partnership, or association applicant must designate a named individual as broker of record who meets all broker qualifications.
- **states:** PA
- **sample (PA):** "If the applicant for a broker's license is a corporation, partnership or association, then the provisions of sections 511 and 512 shall apply to the individual designated as broker of record."

### `pre_exam_experience_years` — int
- **what:** Minimum years of licensed salesperson experience (or equivalent) required before sitting for the broker examination.
- **states:** PA
- **sample (PA):** "The applicant shall have been engaged as a licensed real estate salesperson for at least three years or possess educational or experience qualifications which the commission deems to be the equivalent thereof."

### `pre_exam_instruction_hours` — int
- **what:** Number of approved real estate instruction hours required before sitting for the licensing examination.
- **states:** PA
- **sample (PA):** "The applicant shall have completed 240 hours in real estate instruction in areas of study prescribed by the rules of the commission, which rules shall require instruction in the areas of fair housing and professional ethics."

### `required_instruction_topics` — list[str]
- **what:** Specific subject areas that must be included in the pre-licensure instruction curriculum.
- **states:** PA
- **sample (PA):** "which rules shall require instruction in the areas of fair housing and professional ethics"

### `exam_application_window_years` — int
- **what:** Maximum number of years after passing the licensing examination within which the applicant must submit a completed license application.
- **states:** PA
- **sample (PA):** "The application shall be received by the commission within three years of the date upon which the applicant passed the examination."

### `inactive_license_max_years` — int
- **what:** Maximum number of years a license may remain on inactive status before the holder must retake the licensing examination to reactivate.
- **states:** PA
- **sample (PA):** "Any person who remains inactive for a period of five years without renewing his license shall, prior to having a license reissued to him, submit to and pass the examination pertinent to the license for which the person is reapplying."

### `license_revocation_reapplication_waiting_years` — int
- **what:** Minimum number of years after revocation before a person may reapply for a license.
- **states:** PA
- **sample (PA):** "Unless ordered to do so by Commonwealth Court, the commission shall not reinstate the license, within five years of the date of revocation, of any person whose license has been revoked under this act."

## agency relationships and representation roles

### `agency_relationship_types` — list[str]
- **what:** The legally recognized relationship roles a broker or licensee may occupy in a transaction.
- **states:** PA
- **sample (PA):** "A broker may act in a real estate transaction, subject to the provisions of this act, as a seller/landlord agent, buyer/tenant agent, as a dual agent for seller/landlord and buyer/tenant or as a transaction licensee."

### `dual_agency_written_consent_required` — bool
- **what:** Whether dual agency requires prior written consent from both parties to the transaction.
- **states:** PA
- **sample (PA):** "A licensee may act as a dual agent only with the written consent of both parties to the transaction following the disclosures given at the initial interview required by section 608."

### `designated_agency_permitted` — bool
- **what:** Whether a broker may designate individual licensees to represent separate parties within the same transaction exclusively.
- **states:** PA
- **sample (PA):** "In an agency relationship with a principal, the broker may, with the written consent of the principal, designate one or more licensees employed by the broker to serve as the designated agent of the principal to the exclusion of all other licensees employed by the same broker."

### `transaction_licensee_role_permitted` — bool
- **what:** Whether a licensee may provide services to a consumer without acting as an agent or advocate, in a non-agency facilitation role.
- **states:** PA
- **sample (PA):** "A licensed broker or salesperson who provides communication or document preparation services or performs acts described under the definition of 'broker' or 'salesperson' for which a license is required, without being an agent or advocate of the consumer."

## consumer disclosure and contract requirements

### `initial_interview_disclosure_required` — bool
- **what:** Whether a licensee must provide a standardized written disclosure of agency relationship options to a consumer at the first substantive meeting.
- **states:** PA
- **sample (PA):** "For the purposes of this section, the initial interview is the first contact between a licensee and a consumer of real estate-related services where a substantive discussion about real estate needs occurs. Such disclosure shall be provided on a form adopted by the commission by regulation."

### `written_service_agreement_required` — bool
- **what:** Whether a broker must have a signed written agreement with a consumer before being entitled to collect a fee or commission for services.
- **states:** PA
- **sample (PA):** "A licensee may not perform a service for a consumer of real estate services for a fee, commission or other valuable consideration paid by or on behalf of the consumer unless the nature of the service and the fee to be charged are set forth in a written agreement between the broker and the consumer that is signed by the consumer."

### `sales_contract_mandatory_disclosures` — list[str]
- **what:** Specific items that must be disclosed or included in every sales agreement or sales contract by the broker.
- **states:** PA
- **sample (PA):** "In a sales agreement or sales contract, a broker shall disclose the following information... A statement of the zoning classification of the property... A statement that access to a public road may require issuance of a highway occupancy permit from the Department of Transportation."

### `listing_contract_termination_date_required` — bool
- **what:** Whether every listing contract must specify a definite termination date not subject to prior notice.
- **states:** PA
- **sample (PA):** "Failing to specify a definite termination date that is not subject to prior notice, in any listing contract."

### `transaction_record_retention_years` — int
- **what:** Minimum number of years a broker must retain records relating to a completed real estate transaction.
- **states:** PA
- **sample (PA):** "Failing to preserve for three years following its consummation records relating to any real estate transaction."

## handling of client money and escrow

### `escrow_account_required` — bool
- **what:** Whether a broker must maintain a separate custodial or trust fund account for deposits and other funds belonging to clients.
- **states:** PA
- **sample (PA):** "A broker must deposit moneys and property of whatever kind or nature, belonging to others, in a separate custodial or trust fund account maintained by the broker with a bank or recognized depository by the end of the business day following their receipt by the broker."

### `escrow_deposit_deadline_business_days` — int
- **what:** Number of business days after receipt within which a broker must deposit client funds into the escrow or trust account.
- **states:** PA
- **sample (PA):** "A broker must deposit moneys and property of whatever kind or nature, belonging to others, in a separate custodial or trust fund account maintained by the broker with a bank or recognized depository by the end of the business day following their receipt by the broker."

### `commingling_of_funds_prohibited` — bool
- **what:** Whether a broker is explicitly prohibited from mixing client deposits or escrow funds with the broker's own personal or business funds.
- **states:** PA
- **sample (PA):** "A broker shall not commingle deposits or other escrows or property of another person with the broker's own funds or property."

## office and business operation requirements

### `fixed_office_required` — bool
- **what:** Whether a broker holding a standard license must maintain a fixed physical office within the state.
- **states:** PA
- **sample (PA):** "Each broker (which term in this section shall include cemetery broker) and rental listing referral agent who holds a standard license shall maintain a fixed office within this Commonwealth."

### `branch_office_associate_broker_required` — bool
- **what:** Whether each branch office must be under the direction and supervision of the broker or a licensed associate broker.
- **states:** PA
- **sample (PA):** "Each office shall be under the direction and supervision of a manager who is either the broker or an associate broker."

### `salesperson_broker_affiliation_required` — bool
- **what:** Whether a salesperson or associate broker must be affiliated with and supervised by a licensed broker in order to practice.
- **states:** PA
- **sample (PA):** "The applicant shall submit a sworn statement by the broker with whom he desires to be affiliated certifying that the broker will actively supervise and train the applicant."

### `qualified_association_permitted` — bool
- **what:** Whether licensees may receive commissions through a pass-through business entity (qualified association) solely owned by licensees affiliated with the same broker.
- **states:** PA
- **sample (PA):** "it is not unlawful for a broker to pay a commission or compensation to a qualified association or for an associate broker or salesperson to receive a commission or compensation for the provision of real estate services or real estate-related services from a qualified association in which the associate broker or salesperson owns an interest."

## consumer protection fund and penalties

### `recovery_fund_exists` — bool
- **what:** Whether the state maintains a Real Estate Recovery Fund from which aggrieved consumers may recover losses caused by licensee fraud or misrepresentation.
- **states:** PA
- **sample (PA):** "There is hereby established the Real Estate Recovery Fund for the purposes hereinafter set forth in this act."

### `recovery_fund_max_per_claim` — int
- **what:** Maximum dollar amount payable from the recovery fund for any single claim by an aggrieved person.
- **states:** PA
- **sample (PA):** "the liability of that portion of the fund allocated for the purpose of this act shall not exceed $20,000 for any one claim"

### `recovery_fund_max_per_licensee` — int
- **what:** Maximum total dollar amount payable from the recovery fund for all claims against a single licensee.
- **states:** PA
- **sample (PA):** "shall not exceed $100,000 per licensee"

## specialty property and transaction rules

### `promotional_land_sales_registration_required` — bool
- **what:** Whether persons engaging in promotional real estate transactions (subdivisions marketed by mail, radio, etc.) must register with the commission before doing so.
- **states:** PA
- **sample (PA):** "Any person who proposes to engage in real estate transactions of a promotional nature in this Commonwealth for a property located inside or outside of this Commonwealth, shall first register with the commission for its approval before so doing."

### `time_share_cancellation_right_days` — int
- **what:** Number of days after contract execution during which a purchaser of a time share or campground membership may cancel without penalty.
- **states:** PA
- **sample (PA):** "A purchaser shall have the right to cancel the purchase of a time share or a campground membership until midnight of the fifth day following the date on which the purchaser executed the purchase contract."

### `wholesale_transaction_cancellation_right_days` — int
- **what:** Number of days after contract execution during which a consumer in a wholesale transaction may cancel the sales agreement.
- **states:** PA
- **sample (PA):** "A consumer who is party to a wholesale transaction shall have the right to cancel a sales agreement or sales contract... until midnight of the 30th day after the date when the consumer executed the agreement or contract, or until conveyance, whichever occurs first."

### `broker_price_opinion_permitted` — bool
- **what:** Whether licensees are authorized to prepare broker price opinions and under what conditions.
- **states:** PA
- **sample (PA):** "A broker price opinion may be prepared by a broker, associate broker or salesperson only for use in conjunction with: a property owned by a lender after an unsuccessful sale at a foreclosure auction; a modification of a first or junior mortgage or equity line of credit; a short sale of a property; or an evaluation or monitoring of a portfolio of properties."

### `comparative_market_analysis_permitted` — bool
- **what:** Whether licensees are authorized to prepare comparative market analyses and whether specific disclosure language is required on the document.
- **states:** PA
- **sample (PA):** "A comparative market analysis must contain the following statement printed conspicuously and without change on the first page: This analysis has not been performed in accordance with the Uniform Standards of Professional Appraisal Practice... It is not to be construed as an appraisal and may not be used as such for any purpose."

## who does not need a license

### `license_exemptions` — list[str]
- **what:** Categories of persons or activities explicitly excluded from the licensing requirement.
- **states:** PA
- **sample (PA):** "Except as otherwise provided in this act, the provisions of this act shall not apply to the following: An owner of real estate with respect to property owned or leased by such owner... The services rendered by an attorney-in-fact under an executed and recorded power of attorney... A person acting as trustee in bankruptcy, administrator, executor, trustee or guardian while acting under a court order..."
