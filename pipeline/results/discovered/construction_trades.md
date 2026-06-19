# Discovered fields — construction_trades

## advertising and public disclosure rules

### `registration_number_required_in_ads` — bool
- **what:** Whether the contractor's registration number must appear in all advertisements, contracts, estimates, and proposals.
- **states:** PA
- **sample (PA):** "A contractor shall include its registration number in all advertisements distributed within this Commonwealth and on all contracts, estimates and proposals with owners in this Commonwealth."

## insurance requirements

### `insurance_personal_injury_minimum_usd` — int
- **what:** Minimum dollar amount of liability insurance covering personal injury that a contractor must maintain.
- **states:** PA
- **sample (PA):** "proof of liability insurance covering personal injury in an amount not less than $50,000"

### `insurance_property_damage_minimum_usd` — int
- **what:** Minimum dollar amount of insurance covering property damage caused by the contractor's work.
- **states:** PA
- **sample (PA):** "insurance covering property damage caused by the work of a home improvement contractor in an amount not less than $50,000"

### `self_insurance_permitted` — bool
- **what:** Whether a contractor may satisfy insurance requirements by attesting to being self-insured rather than carrying a third-party policy.
- **states:** PA
- **sample (PA):** "proof of insurance may include information attested to by an applicant that the applicant is self-insured and the bureau shall develop forms for this purpose"

## contract requirements

### `contract_must_be_written` — bool
- **what:** Whether a home improvement contract must be in writing to be valid and enforceable against the owner.
- **states:** PA
- **sample (PA):** "No home improvement contract shall be valid or enforceable against an owner unless it: Is in writing and legible"

### `right_of_rescission_days` — int
- **what:** Number of business days within which an owner may rescind a signed home improvement contract without penalty.
- **states:** PA
- **sample (PA):** "shall be permitted to rescind the contract without penalty regardless of where the contract was signed, within three business days of the date of signing"

### `deposit_cap_fraction` — str
- **what:** Maximum fraction of the total contract price a contractor may collect as a deposit before work begins, for contracts above a threshold amount.
- **states:** PA
- **sample (PA):** "for a home improvement contract in which the total price is more than $5,000, receive a deposit in excess of one-third of the home improvement contract price"

### `deposit_cap_contract_threshold_usd` — int
- **what:** Minimum contract price above which the deposit cap rule applies.
- **states:** PA
- **sample (PA):** "for a home improvement contract in which the total price is more than $5,000"

### `change_order_must_be_written` — bool
- **what:** Whether any deviation from the original plans or specifications requires a written change order signed by both parties.
- **states:** PA
- **sample (PA):** "Deviate from or disregard plans or specifications, in any material respect, without a written change order dated and signed by both the contractor and owner"

### `arbitration_clause_allowed` — bool
- **what:** Whether a home improvement contract may include an arbitration clause, subject to specific formatting and disclosure requirements.
- **states:** PA
- **sample (PA):** "Nothing in this act shall preclude the court from setting aside an arbitration clause on any basis permitted under Pennsylvania law."

### `voidable_contract_clauses` — list[str]
- **what:** List of clause types that, if included in a home improvement contract, make the contract voidable by the owner.
- **states:** PA
- **sample (PA):** "If a home improvement contract contains any of the following clauses, the home improvement contract shall be voidable by the owner: A hold harmless clause. A waiver of Federal, State or local health, life, safety or building code requirements. A confession of judgment clause."

## who must register

### `minimum_annual_revenue_threshold_usd` — int
- **what:** Minimum total cash value of home improvements in the prior taxable year below which a person is exempt from contractor registration.
- **states:** PA
- **sample (PA):** "A person for whom the total cash value of all of that person's home improvements is less than $5,000 during the previous taxable year."

### `minimum_project_value_usd` — int
- **what:** Minimum cash price of a single project for the work to qualify as a regulated home improvement requiring a registered contractor.
- **states:** PA
- **sample (PA):** "the total cash price of all work agreed upon between the contractor and owner is more than $500"

## fraud and criminal penalties

### `fraud_offense_defined` — bool
- **what:** Whether the statute defines a specific criminal offense of home improvement fraud with enumerated prohibited acts.
- **states:** PA
- **sample (PA):** "A person commits the offense of home improvement fraud if, with intent to defraud or injure anyone or with knowledge that he is facilitating a fraud or injury to be perpetrated by anyone"

### `fraud_felony_threshold_usd` — int
- **what:** Dollar amount above which a home improvement fraud violation is graded as a felony rather than a misdemeanor.
- **states:** PA
- **sample (PA):** "a felony of the third degree if the amount involved exceeds $2,000"

### `enhanced_penalty_for_elderly_victims` — bool
- **what:** Whether the grading of a fraud offense is elevated by one level when the victim is 60 years of age or older.
- **states:** PA
- **sample (PA):** "Where a person commits an offense under subsection (a) and the victim is 60 years of age or older, the grading of the offense shall be one grade higher"

## relationship between state and local rules

### `state_preempts_local_registration_fees` — bool
- **what:** Whether state registration preempts local governments from imposing their own contractor registration fees or licensing requirements.
- **states:** PA
- **sample (PA):** "Registration under this act shall preclude any requirement of payment of a fee or registration or licensing of any home improvement contractor by any political subdivision."

### `local_trade_licensing_preserved` — bool
- **what:** Whether existing local licensing standards for specific trades (e.g., electricians, plumbers) are preserved notwithstanding state preemption.
- **states:** PA
- **sample (PA):** "This provision does not affect existing licensing standards in effect on the effective date of this act, with respect to electricians and plumbers and other trades, where licensing is conditioned on requirements of testing or possession of certificates obtained through specific training in electricity or plumbing or other trades."

## registration administration

### `registration_renewal_interval_years` — int
- **what:** How often, in years, a contractor must renew their registration with the issuing authority.
- **states:** PA
- **sample (PA):** "Any registered contractor in this Commonwealth who is registered or licensed as a home improvement contractor in any other state, or political subdivision thereof, shall report this information to the bureau on the initial registration and biennial registration application."

### `out_of_state_disciplinary_action_reporting_required` — bool
- **what:** Whether a contractor must report to the state any disciplinary action taken against them in another jurisdiction.
- **states:** PA
- **sample (PA):** "Any disciplinary action taken in such other jurisdiction shall be reported to the bureau on the initial registration application or, if such action occurred subsequent to submission of an initial application, on the biennial registration application or within 90 days of final disposition, whichever is sooner."
