# Discovered fields — public_adjuster

## who can hold a license

### `business_entity_licensure_allowed` — bool
- **what:** Whether business entities (corporations, partnerships, LLCs, etc.) may obtain a public adjuster license in addition to individuals.
- **states:** PA
- **sample (PA):** "Upon designating one or more officers or partners licensed under this act to be responsible for the business entity's compliance with the insurance laws and regulations of the Commonwealth, a business entity may apply to the department for a public adjuster license."

### `designated_licensee_required_for_business_entity` — bool
- **what:** Whether a business entity must designate one or more individually licensed public adjusters responsible for the entity's regulatory compliance.
- **states:** PA
- **sample (PA):** "if a corporation or limited liability company, individual public adjuster licenses shall be held by or secured for each officer of the corporation or limited liability company"

### `resident_vs_nonresident_license_types` — list[str]
- **what:** The license classifications available based on whether the applicant's home state is the issuing state.
- **states:** PA
- **sample (PA):** "An individual who is a resident of this Commonwealth may apply to the department for a resident public adjuster license. An individual who is not a resident of this Commonwealth may apply for a nonresident public adjuster license."

## background and character screening

### `fingerprint_background_check_required` — bool
- **what:** Whether applicants must submit fingerprints for a national criminal history background check through the FBI.
- **states:** PA
- **sample (PA):** "the applicant's fingerprints, for the department to receive national criminal history records information from the Criminal Justice Information Services Division of the Federal Bureau of Investigation"

### `prohibited_salvage_business_interest` — bool
- **what:** Whether a licensee is prohibited from having any financial interest in or receiving profit from a salvage or similar business.
- **states:** PA
- **sample (PA):** "No license as a public adjuster shall be issued to any person engaged or interested in, or receiving any profit from, nor shall the holder of any such license engage or be interested in, or receive any profit from, any salvage or similar business."

## financial security requirements

### `surety_bond_required` — bool
- **what:** Whether a public adjuster must file a surety bond with the state before transacting business.
- **states:** PA
- **sample (PA):** "Each person receiving a public adjuster's license shall, before transacting any business thereunder, execute and deliver to the Insurance Commissioner a bond in the minimum penal sum of $20,000 with such sureties as the Insurance Commissioner may approve."

### `surety_bond_minimum_amount` — int
- **what:** The minimum dollar amount of the surety bond required before a public adjuster may transact business.
- **states:** PA
- **sample (PA):** "execute and deliver to the Insurance Commissioner a bond in the minimum penal sum of $20,000"

## contract and disclosure rules

### `written_contract_required` — bool
- **what:** Whether a public adjuster must execute a written, department-approved contract with the insured before acting.
- **states:** PA
- **sample (PA):** "No public adjuster shall, directly or indirectly, act within this Commonwealth as a public adjuster without having first entered into a contract, in writing, on a form approved by the department and executed in duplicate by the public adjuster and the insured or a duly authorized representative."

### `contract_rescission_period_days` — int
- **what:** The number of calendar days after signing during which the insured may rescind the public adjuster contract.
- **states:** PA
- **sample (PA):** "That the insured has the right to rescind the contract within three calendar days after signature."

### `insurer_notification_deadline_days` — int
- **what:** The number of calendar days within which the public adjuster must notify the insured's insurer after entering into a contract.
- **states:** PA
- **sample (PA):** "Failing to notify the insured's insurer within two calendar days of entering into a contract."

### `financial_interest_disclosure_required` — bool
- **what:** Whether the public adjuster must provide the insured a written disclosure of any direct or indirect financial interest in other firms involved in the claim.
- **states:** PA
- **sample (PA):** "A public adjuster shall provide the insured a written disclosure concerning a direct or indirect financial interest the public adjuster has with another party involved in an aspect of the claim other than the salary, fee, commission or other consideration established in the written contract with the insured."

## what claims they are allowed to handle

### `prohibited_claim_types` — list[str]
- **what:** Categories of claims that a public adjuster is explicitly prohibited from handling.
- **states:** PA
- **sample (PA):** "No public adjuster shall act in any manner in relation to claims for personal injury or automobile property damage."

### `claims_only_against_own_insurer` — bool
- **what:** Whether a public adjuster may only adjust claims on behalf of an insured against that insured's own insurance carrier.
- **states:** PA
- **sample (PA):** "No public adjuster may adjust or solicit a contract for the adjustment of any claim for losses or damages on behalf of any person except claims by an insured against his own insurance carrier."

### `repair_contract_prohibition_before_settlement` — bool
- **what:** Whether a public adjuster is prohibited from entering into a contract with the insured for repair, replacement, or demolition of damaged property prior to a verdict, award, or payment from the insurer.
- **states:** PA
- **sample (PA):** "No public adjuster shall, directly or indirectly, through or with any person, partnership, corporation or association in which it has an indirect or beneficial interest, enter into any contract with any insured for the repair, replacement, restoration, renovation or demolition of damaged property, real or personal, at any time prior to the date a verdict or award is entered or payment is received from the insurance carrier."

## conduct and disciplinary rules

### `catastrophe_solicitation_prohibited` — bool
- **what:** Whether soliciting business during an active loss-producing event such as a fire, tornado, or other catastrophe is a prohibited act.
- **states:** PA
- **sample (PA):** "Soliciting business during the progress of a loss-producing occurrence such as a fire, tornado, severe storm or other catastrophe where the immediate safety and security of persons and property is paramount."

### `max_civil_penalty_per_violation` — int
- **what:** The maximum civil penalty in dollars that may be imposed per violation of the public adjuster statute.
- **states:** PA
- **sample (PA):** "the Insurance Commissioner may, at his discretion, in cases warranting such action, impose a civil penalty of not more than $5,000 for each and every violation of this act."

## fees

### `license_fee_initial` — int
- **what:** The nonrefundable initial application fee in dollars for a resident or nonresident public adjuster license.
- **states:** PA
- **sample (PA):** "A nonrefundable $200 fee shall accompany a completed application for a resident or nonresident public adjuster license until modified by the department by regulation."

### `license_fee_renewal` — int
- **what:** The nonrefundable renewal fee in dollars for a resident or nonresident public adjuster license.
- **states:** PA
- **sample (PA):** "Resident or nonresident renewal fee, $200."

### `license_fee_lapsed_renewal` — int
- **what:** The nonrefundable fee in dollars required to renew a lapsed public adjuster license.
- **states:** PA
- **sample (PA):** "Lapsed license renewal fee, $400."
