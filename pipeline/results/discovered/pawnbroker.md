# Discovered fields — pawnbroker

## financial guarantees and bonding

### `surety_bond_required` — bool
- **what:** Whether a surety bond must be filed with the licensing authority as a condition of licensure.
- **states:** PA
- **sample (PA):** "A bond in the penal sum of two thousand ($2,000.00) dollars shall accompany every application for license."

### `surety_bond_amount_usd` — int
- **what:** Dollar amount of the required surety bond per licensed place of business.
- **states:** PA
- **sample (PA):** "A bond in the penal sum of two thousand ($2,000.00) dollars shall accompany every application for license."

### `bond_per_location` — bool
- **what:** Whether a separate bond is required for each licensed place of business.
- **states:** PA
- **sample (PA):** "A separate bond shall be required for each place of business conducted by a pawnbroker."

## loan terms and interest rate limits

### `max_interest_rate_annual_pct` — str
- **what:** Maximum annual interest rate a pawnbroker may charge on a loan.
- **states:** PA
- **sample (PA):** "A pawnbroker shall not charge, contract for or receive interest in excess of six per cent (6%) per year on any loan."

### `max_service_fee_monthly_pct` — str
- **what:** Maximum monthly percentage fee for storage, insurance, and other services in addition to interest.
- **states:** PA
- **sample (PA):** "Not more than two and one-half per cent (2 1/2%) per month on that part of the unpaid principal balance of any loan."

### `installment_loans_prohibited` — bool
- **what:** Whether pawn loans are prohibited from being structured as installment loans.
- **states:** PA
- **sample (PA):** "A loan granted under the provisions of this act shall not be repayable in installments."

### `minimum_pledge_hold_hours` — int
- **what:** Minimum number of hours a pawnbroker must retain a pledge before it may be redeemed or sold.
- **states:** PA
- **sample (PA):** "A pledge taken as security on a loan granted under the provisions of this act may be retained by the pawnbroker until a period of forty-eight (48) hours has elapsed since such pledge was received by the pawnbroker."

## recordkeeping and transaction documentation

### `pawn_ticket_required` — bool
- **what:** Whether the pawnbroker must issue a serially numbered pawn ticket to the pledger at the time of each loan.
- **states:** PA
- **sample (PA):** "At the time of granting a loan and upon the subsequent renewal of any loan, the pawnbroker shall furnish to the pledger a pawn ticket which is serially numbered."

### `pawn_ticket_required_fields` — list[str]
- **what:** Specific data elements that must appear on the pawn ticket by statute.
- **states:** PA
- **sample (PA):** "name and address of the pawnbroker, the name and address of the pledger, name and address of disclosed principal, if any, the date of the loan, the amount actually loaned, the serial number of the loan, description of the pledge, due date of the loan, the total amount of principal, interest and charges required to redeem the pledge on the due date"

### `pledger_identity_verification_required` — bool
- **what:** Whether the pawnbroker must record identifying information about the pledger at the time of each loan.
- **states:** PA
- **sample (PA):** "the pawnbroker shall enter upon his records, in the form and manner designated by the Secretary of Banking, a description of the pledger so as to identify the pledger, including the pledger's name and address, and either the pledger's motor vehicle operator's number, the pledger's Social Security number, or, if the pledger does not have this information, such other proof of identity"

### `records_retention_period_years` — int
- **what:** Number of years pawnbroker transaction records must be retained after loan payment or pledge sale.
- **states:** PA
- **sample (PA):** "The records of a pawnbroker shall be retained for a period of two years after the date of the payment of any loan, or in case the loan is not paid, the records of a pawnbroker shall be retained for a period of two (2) years after the date of the sale of the pledge."

### `annual_report_due_date` — str
- **what:** Statutory deadline by which the pawnbroker must file an annual report with the licensing authority.
- **states:** PA
- **sample (PA):** "Every pawnbroker licensed under this act shall annually, on or before the first day of March, file a report with the Secretary of Banking."

## who pawnbrokers may do business with

### `minimum_pledger_age` — int
- **what:** Minimum age of a person from whom a pawnbroker may accept a pledge.
- **states:** PA
- **sample (PA):** "A pawnbroker shall not accept a pledge from any person under the age of eighteen years."

### `sunday_business_prohibited` — bool
- **what:** Whether pawnbrokers are prohibited from transacting business on Sundays.
- **states:** PA
- **sample (PA):** "A pawnbroker shall not transact any business on Sunday, nor shall he accept a pledge on any other day between the hours of nine o'clock in the evening and seven o'clock in the morning."

### `restricted_business_hours` — str
- **what:** Hours during which accepting pledges or transacting pawnbroker business is prohibited.
- **states:** PA
- **sample (PA):** "nor shall he accept a pledge on any other day between the hours of nine o'clock in the evening and seven o'clock in the morning, unless further restricted by municipal ordinance."

## sale of unredeemed pledges

### `unredeemed_pledge_min_hold_days_before_sale` — int
- **what:** Minimum number of days after the loan due date that must elapse before an unredeemed pledge may be sold.
- **states:** PA
- **sample (PA):** "No unredeemed pledge may be sold before the expiration of ninety (90) days after the due date of the loan unless otherwise specifically authorized in writing by the pledger."

### `presale_notice_required` — bool
- **what:** Whether the pawnbroker must mail advance notice to the pledger before selling an unredeemed pledge.
- **states:** PA
- **sample (PA):** "A pawnbroker shall not sell any pledge where the loan is seven dollars ($7) or more unless due notice of such contemplated sale has been forwarded to the pledger by mail."

### `presale_notice_days` — int
- **what:** Number of days before a pledge sale that written notice must be mailed to the pledger.
- **states:** PA
- **sample (PA):** "Notice of the contemplated sale of a pledge shall be mailed to the pledger not less than thirty (30) days prior to the date of sale."

### `surplus_reversion_period_years` — int
- **what:** Number of years after a pledge sale after which an unclaimed surplus reverts to the pawnbroker.
- **states:** PA
- **sample (PA):** "If a surplus remaining from the sale of a pledge is not paid or claimed within one year from the date of sale, such surplus shall revert to the pawnbroker."

## licensing process and location approval

### `public_hearing_required_for_initial_license` — bool
- **what:** Whether a public hearing must be held before an initial pawnbroker license is issued.
- **states:** PA
- **sample (PA):** "A public hearing shall be held upon initial application for a pawnbroker's license."

### `neighbor_notice_radius_feet` — int
- **what:** Radius in feet within which nearby residents must be permitted to testify at a license hearing.
- **states:** PA
- **sample (PA):** "The Secretary of Banking shall permit residents residing within a radius of five hundred (500) feet of the proposed location to testify at the hearing."

### `license_nontransferable` — bool
- **what:** Whether a pawnbroker license may not be transferred or assigned to another person or entity.
- **states:** PA
- **sample (PA):** "Such license may not be transferred or assigned."

### `one_license_per_location` — bool
- **what:** Whether each physical place of business requires its own separate license.
- **states:** PA
- **sample (PA):** "Not more than one place of business may be operated under the same license."

### `municipal_license_also_required` — bool
- **what:** Whether a pawnbroker must also obtain a separate license from the local municipality in addition to the state license.
- **states:** PA
- **sample (PA):** "A pawnbroker shall not be authorized to engage in business unless he shall have obtained a license from the municipality, if the municipality requires such a license to be obtained."

## law enforcement cooperation and stolen goods

### `stolen_property_reporting_required` — bool
- **what:** Whether pawnbrokers are required to report or surrender suspected stolen property to police authorities.
- **states:** PA
- **sample (PA):** "Such property and a copy of the seizure receipt shall be delivered immediately by the pawnbroker to the police authorities."

### `compliance_as_defense_to_receiving_stolen_goods` — bool
- **what:** Whether a pawnbroker's compliance with reporting and recordkeeping requirements constitutes evidence of innocence for receiving stolen goods.
- **states:** PA
- **sample (PA):** "Whenever any pawnbroker shall make a complete and accurate report to the local police authorities, and shall comply with this act... such conduct on the part of the pawnbroker shall be evidence of the innocence of such pawnbroker of any crime of receiving stolen goods."
