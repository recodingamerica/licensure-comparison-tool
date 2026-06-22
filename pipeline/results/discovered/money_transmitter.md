# Discovered fields — money_transmitter

## what the license covers

### `virtual_currency_transmission_covered` — bool
- **what:** Whether the license requirement explicitly extends to transmission of virtual currency in addition to fiat money.
- **states:** PA
- **sample (PA):** "Engage in the business of transmitting virtual currency by means of a transmittal instrument for a fee or other consideration with or on behalf of an individual without first having obtained a license from the department."

## financial requirements

### `tangible_net_worth_minimum_usd` — int
- **what:** Minimum tangible net worth in US dollars that an applicant must demonstrate, as determined by audited financials under GAAP.
- **states:** PA
- **sample (PA):** "have a tangible net worth of at least five hundred thousand dollars ($500,000) as determined by audited financials prepared in accordance with United States generally accepted accounting principles"

### `surety_bond_amount_usd` — int
- **what:** Required surety bond amount in US dollars that must accompany a license application.
- **states:** PA
- **sample (PA):** "a bond in the penal sum of one million dollars ($1,000,000) executed by a surety company authorized to transact business within the Commonwealth of Pennsylvania"

### `application_fee_usd` — int
- **what:** Non-refundable application fee in US dollars required to accompany a new license application.
- **states:** PA
- **sample (PA):** "an application fee of five thousand dollars ($5,000)"

### `renewal_fee_usd` — int
- **what:** Fee in US dollars required to renew an existing license.
- **states:** PA
- **sample (PA):** "the license shall be renewed upon the payment of the renewal fee of five thousand dollars ($5,000)"

### `audited_financials_required` — bool
- **what:** Whether the applicant must submit audited financial statements prepared under GAAP.
- **states:** PA
- **sample (PA):** "a financial statement showing a tangible net worth of at least five hundred thousand dollars ($500,000) as determined by audited financials prepared in accordance with United States generally accepted accounting principles"

## agents and delegation

### `agent_registration_required` — bool
- **what:** Whether a licensee must register all agents who conduct money or virtual currency transmission on its behalf.
- **states:** PA
- **sample (PA):** "Register all of its agents who engage in the business of money transmission or virtual currency transmission involving individuals who are located in this Commonwealth."

### `agent_written_agreement_required` — bool
- **what:** Whether agents must be appointed under a written agreement with the licensee specifying control, liability, and scope.
- **states:** PA
- **sample (PA):** "An agent engaged in the business of money transmission or virtual currency transmission under subsection (a) or subject to an exemption under section 3 shall be appointed pursuant to a written agreement between the agent and the person on whose behalf the agent is acting."

### `licensee_liable_for_agent_transmittals` — bool
- **what:** Whether the licensee bears full financial liability for transmittal instruments issued through agents.
- **states:** PA
- **sample (PA):** "Every licensee shall be liable for the payment of all moneys or virtual currency covered by transmittal instruments which he issues in this Commonwealth whether directly or through an agent"

## who is exempt from licensing

### `exempted_entity_types` — list[str]
- **what:** Categories of entities or persons explicitly exempt from the license requirement.
- **states:** PA
- **sample (PA):** "Banks, bank and trust companies, credit unions, savings banks and trust companies organized under the laws of this Commonwealth; similar banking institutions organized under the laws of the United States or of any other state"

### `self_hosted_wallet_exemption` — bool
- **what:** Whether use of a self-hosted (non-custodial) wallet is explicitly exempt from the license requirement, subject to conditions.
- **states:** PA
- **sample (PA):** "The use of a self-hosted wallet, unless the individual with control of the controllable electronic records in the self-hosted wallet transmits virtual currency as part of a third-party service on behalf of another individual in exchange for a fee or other consideration"

## consumer protection and disclosure rules

### `transmittal_instrument_name_display_required` — bool
- **what:** Whether every transmittal instrument sold must clearly display the licensee's name.
- **states:** PA
- **sample (PA):** "Every transmittal instrument sold by a licensee directly or through an agent shall bear the name of the licensee clearly imprinted thereon."

### `material_change_notice_days` — int
- **what:** Number of days within which a licensee must notify the regulator of material changes in status such as address, ownership, or officers.
- **states:** PA
- **sample (PA):** "Provide the department with written notice within ten days of any change in status, including address, ownership, directors, officers, contact information and the reason for the change."

## penalties and enforcement

### `late_report_penalty_per_day_usd` — int
- **what:** Daily monetary penalty in US dollars assessed for each day a required periodic report is filed late.
- **states:** PA
- **sample (PA):** "Licensees who fail to file the required report by the date required by the department may be subject to a penalty of one hundred dollars ($100) for each day after the due date until the report is filed."

### `criminal_penalty_classification` — enum[felony, misdemeanor, civil only]
- **what:** Criminal classification of violations of the money transmission statute.
- **states:** PA
- **sample (PA):** "Any person who directly or through another violates or attempts to violate any provision of this act shall be guilty of a felony"

### `criminal_fine_range_usd` — str
- **what:** Statutory range of criminal fines (minimum and maximum) for violations of the act.
- **states:** PA
- **sample (PA):** "shall be fined not less than five thousand dollars ($5,000), nor more than fifty thousand dollars ($50,000)"

### `administrative_fine_per_offense_usd` — int
- **what:** Maximum administrative fine per offense that the regulator may levy against a licensee or associated person.
- **states:** PA
- **sample (PA):** "any director, officer, employee or agent of any such person, who shall violate the provisions of this act or shall direct or consent to such violations shall be subject to a fine levied by the department of up to ten thousand dollars ($10,000) for each offense"
