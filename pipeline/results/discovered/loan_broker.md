# Discovered fields — loan_broker

## licensing and registration

### `registration_required` — bool
- **what:** Whether loan brokers must register with a state agency (as distinct from obtaining a full professional license).
- **states:** PA
- **sample (PA):** "Loan brokers shall be registered with the Department of Banking pursuant to regulations promulgated by the department."

### `registration_fee_annual` — int
- **what:** Annual fee in dollars required to register as a loan broker with the state.
- **states:** PA
- **sample (PA):** "Loan brokers seeking to be registered by the department shall pay to the department an annual registration fee of $300."

## fee and payment restrictions

### `advance_fee_prohibited` — bool
- **what:** Whether loan brokers are prohibited from collecting any fee from a borrower before a loan is closed or services are fully performed.
- **states:** PA
- **sample (PA):** "No loan broker shall: Assess or collect an advance fee from a borrower to provide services as a loan broker."

## financial security requirements

### `surety_bond_or_trust_account_required` — bool
- **what:** Whether the organization must obtain a surety bond or establish a trust account before collecting fees.
- **states:** PA
- **sample (PA):** "Charge or receive any money or other valuable consideration prior to full and complete performance of the services the credit services organization has agreed to perform for or on behalf of the buyer unless the credit services organization has, in conformity with section 7, either obtained a surety bond issued by a surety company admitted to do business in this Commonwealth or established a trust account."

### `surety_bond_minimum_amount` — int
- **what:** Minimum dollar amount required for the surety bond or trust account.
- **states:** PA
- **sample (PA):** "in no case shall the bond be less than $5,000 nor more than $25,000"

### `surety_bond_maximum_amount` — int
- **what:** Maximum dollar amount required for the surety bond or trust account.
- **states:** PA
- **sample (PA):** "in no case shall the bond be less than $5,000 nor more than $25,000"

### `surety_bond_basis_percent_of_fees` — int
- **what:** Percentage of total fees collected in the prior 12 months used to calculate the required bond or trust account amount.
- **states:** PA
- **sample (PA):** "The bond or the trust account shall be in an amount equal to 5% of the total amount of the fees charged buyers by the credit services organization under the contracts entered into between the credit services organization and such buyers during the previous 12 months."

## consumer disclosure and contract requirements

### `written_contract_required` — bool
- **what:** Whether a written, signed, dated contract must be provided to the buyer before services are rendered.
- **states:** PA
- **sample (PA):** "Every contract between the buyer and a credit services organization for the purchase of the services of the credit services organization shall be in writing, shall be dated, shall be signed by the buyer."

### `cancellation_right_days` — int
- **what:** Number of days after signing during which the buyer may cancel the contract without penalty.
- **states:** PA
- **sample (PA):** "You may cancel this contract without any penalty or obligation within five days from the date the contract is signed."

### `pre_contract_information_sheet_required` — bool
- **what:** Whether the organization must provide a written information sheet to the buyer before any contract is signed or money is received.
- **states:** PA
- **sample (PA):** "Prior to the execution of a contract or agreement between the buyer and a credit services organization or prior to the receipt by the credit services organization of any money or other valuable consideration, whichever occurs first, the credit services organization shall provide the buyer a statement in writing."

### `information_sheet_retention_years` — int
- **what:** Number of years the organization must retain a signed copy of the buyer's information sheet.
- **states:** PA
- **sample (PA):** "The credit services organization shall maintain on file or microfilm for a period of three years an exact copy of the information sheet, personally signed by the buyer."

## supervision and accountability

### `principal_liability_for_agent_acts` — bool
- **what:** Whether principals (officers, directors, managers) of a loan broker may be held personally responsible for the acts of the broker's agents or employees.
- **states:** PA
- **sample (PA):** "Each principal of a loan broker may be held responsible for the actions of a loan broker, including its agents or employees in the course of business of the loan broker."

## consumer protections

### `waiver_of_consumer_rights_prohibited` — bool
- **what:** Whether any attempt to have a buyer or borrower waive statutory rights is void and constitutes a violation.
- **states:** PA
- **sample (PA):** "Any waiver by a buyer or borrower of the provisions of this act shall be deemed contrary to public policy and shall be void and unenforceable."

### `exemption_burden_of_proof_on_claimant` — bool
- **what:** Whether the burden of proving an exemption or exception from the statute's definitions falls on the party claiming it.
- **states:** PA
- **sample (PA):** "In any proceeding involving this act, the burden of proving an exemption or an exception from a definition is upon the person claiming it."

## who is excluded from regulation

### `excluded_entity_types` — list[str]
- **what:** Categories of entities explicitly excluded from the definition of loan broker or credit services organization.
- **states:** PA
- **sample (PA):** "The term shall not include: Any bank, bank and trust company, trust company, savings bank, Federal savings and loan association... Any person licensed as a real estate broker where the person is acting within the course and scope of that license... Any person admitted to practice law in this Commonwealth."
