# Discovered fields — auctioneer

## license types and tiers

### `license_tiers` — list[str]
- **what:** The distinct license or registration categories recognized under the statute for this profession.
- **states:** PA
- **sample (PA):** "It is unlawful for any person to engage in the business or profession of an auctioneer, apprentice auctioneer or an auction company to conduct an auction...without first obtaining a license from the board as an auctioneer, apprentice auctioneer, auction company or special licensee."

### `special_license_available` — bool
- **what:** Whether out-of-state auctioneers or auction companies may obtain a per-event special license to conduct a single auction in the state.
- **states:** PA
- **sample (PA):** "An auctioneer or auction company authorized to engage in auctioneering in another state shall, on application and payment of the license fee, be issued a special license for each specifically identified auction to be conducted in this Commonwealth."

### `special_license_advance_notice_days` — int
- **what:** Minimum number of days in advance that an application for a special (per-event) license must be submitted before the auction.
- **states:** PA
- **sample (PA):** "Applications must be made not less than 20 days in advance of the auction or sale at auction."

## apprenticeship and sponsorship rules

### `apprentice_sponsor_required` — bool
- **what:** Whether an apprentice auctioneer must be sponsored and employed by a currently licensed auctioneer (qualified sponsor).
- **states:** PA
- **sample (PA):** "To qualify for an apprentice auctioneer license, an individual must be sponsored and employed for compensation by a qualified sponsor who employs no more than one other apprentice auctioneer."

### `apprentice_sponsor_max_apprentices` — int
- **what:** Maximum number of apprentice auctioneers a single qualified sponsor may employ simultaneously.
- **states:** PA
- **sample (PA):** "an individual must be sponsored and employed for compensation by a qualified sponsor who employs no more than one other apprentice auctioneer."

### `apprenticeship_minimum_auctions` — int
- **what:** Minimum number of auctions an apprentice must participate in for compensation to qualify for a full auctioneer license.
- **states:** PA
- **sample (PA):** "serving an apprenticeship as a licensed apprentice auctioneer for a period of not less than two years in the employ of a qualified sponsor and participating for compensation in no less than 30 auctions"

## approved education pathways

### `auction_school_groups` — list[str]
- **what:** Named tiers or groups of board-approved auction schools that satisfy the education requirement, distinguished by credit-hour thresholds.
- **states:** PA
- **sample (PA):** "'Group A auction school.' A provider, approved by the board, offering a course of study in auctioneering and the auction industry...the completion of which requires not less than 20 credit hours, including two credit hours of practicum or cooperative practical experience."

### `auction_school_minimum_credit_hours` — int
- **what:** Minimum credit hours required to complete a board-approved Group A auction school course of study.
- **states:** PA
- **sample (PA):** "the completion of which requires not less than 20 credit hours, including two credit hours of practicum or cooperative practical experience."

### `practicum_hours_required` — int
- **what:** Number of practicum or cooperative practical experience credit hours required within the auction school curriculum.
- **states:** PA
- **sample (PA):** "the completion of which requires not less than 20 credit hours, including two credit hours of practicum or cooperative practical experience."

## auction company governance

### `auction_company_auctioneer_of_record_required` — bool
- **what:** Whether every licensed auction company must designate a specific licensed auctioneer as its auctioneer-of-record who is principally responsible for the company's auctions.
- **states:** PA
- **sample (PA):** "Every auction company shall designate an auctioneer-of-record. Each auction company licensed under this act shall designate an individual licensed as an auctioneer under this act to serve as the auction company's auctioneer-of-record."

### `auction_company_auctioneer_of_record_notification_days` — int
- **what:** Number of calendar days within which an auction company must notify the board when its auctioneer-of-record ceases to serve in that role.
- **states:** PA
- **sample (PA):** "Within 30 calendar days after an auction company's auctioneer-of-record ceases to serve as auctioneer-of-record for the auction company, both the auction company and the auctioneer-of-record...shall notify the board in writing of the termination of such status."

## financial protection requirements

### `surety_bond_required` — bool
- **what:** Whether licensees and registrants must file a surety bond with the board before a license or registration is granted.
- **states:** PA
- **sample (PA):** "No license, including a special license, or registration shall be granted or issued to any person under this act until the applicant has filed with the board an approved bond payable to the Commonwealth in the amount of $5,000."

### `surety_bond_amount` — int
- **what:** Dollar amount of the surety bond required to be filed with the board by each licensee or registrant.
- **states:** PA
- **sample (PA):** "the applicant has filed with the board an approved bond payable to the Commonwealth in the amount of $5,000."

### `escrow_account_required` — bool
- **what:** Whether licensees and registrants must maintain a separate custodial or trust (escrow) account for funds received from the sale of others' property.
- **states:** PA
- **sample (PA):** "Every licensee and registrant shall promptly deposit moneys, received from the sale of property, belonging to others in a separate custodial or trust fund account maintained by the licensee or registrant until the transaction involved is terminated."

## transaction and recordkeeping obligations

### `written_contract_required` — bool
- **what:** Whether a licensee or registrant must enter into a written contract with the owner or consignor of property before conducting a sale.
- **states:** PA
- **sample (PA):** "Prior to conducting a transaction, a licensee or registrant shall enter into a written contract, in duplicate, with the owner or consignor of the property to be sold, containing the terms and conditions upon which the licensee or registrant agrees to conduct the sale."

### `records_retention_years` — int
- **what:** Minimum number of years that sale records and receipts must be retained by a licensee or registrant.
- **states:** PA
- **sample (PA):** "The written records shall be kept on file in the office of the licensee or registrant for a period of not less than two years."

### `license_display_required` — bool
- **what:** Whether licensees and registrants must prominently display their certificate of licensure or registration at their office and produce their wallet card on demand at auctions.
- **states:** PA
- **sample (PA):** "Every licensee and registrant under this act shall prominently display the certificate of licensure or registration at the licensee's or registrant's office, and the current wallet card or any facsimile thereof issued to the licensee or registrant shall be shown on demand of any person at all auctions."

### `advertisement_must_include_license_number` — bool
- **what:** Whether advertisements or notices of sale must include the name and license or registration number of the licensee or registrant conducting the transaction.
- **states:** PA
- **sample (PA):** "For a licensee or registrant to advertise an auction or a sale through an online trading assistant consignment sale without including in the advertisement or notice of sale the name and the license or registration number of the licensee or registrant conducting the transaction."

## online and alternative sale formats

### `online_trading_assistant_registration_required` — bool
- **what:** Whether individuals or entities conducting online trading assistant consignment sale transactions must separately register with the board.
- **states:** PA
- **sample (PA):** "It shall be unlawful for an individual to act as a trading assistant, or for any legally recognized entity to act as a trading assistant company, without either first registering with or obtaining licensure from the board."

### `auction_format_types_authorized` — list[str]
- **what:** Types of auction formats explicitly recognized and authorized under the statute.
- **states:** PA
- **sample (PA):** "Licensees under this act shall be authorized to conduct auctions at any venue within this Commonwealth...by any method of conducting the sale, including live auctions and online auctions and auctions that are conducted live and online contemporaneously, whether real-time auctions or extended auctions."

## exemptions from licensure

### `license_exemptions` — list[str]
- **what:** Categories of sales at auction that are explicitly exempt from the licensure requirement.
- **states:** PA
- **sample (PA):** "The requirement to obtain a license under this act does not apply to sales at auction in the following circumstances: To a specified single sale per year conducted by the owner of property...To a sale conducted by or on behalf of a charitable organization if the person conducting the sale receives no compensation therefor."

## license reinstatement rules

### `inactive_license_reexamination_threshold_years` — int
- **what:** Number of years a license must have been inactive or non-renewed before the holder is required to pass a new examination to have it reissued.
- **states:** PA
- **sample (PA):** "Any individual to whom an auctioneer license has been issued and whose license has been in an inactive or nonrenewed status for a period of seven or more years shall be required to submit to and pass an examination approved by the board prior to having a license reissued."

### `post_revocation_reapplication_waiting_years` — int
- **what:** Minimum number of years after license revocation before a new license may be issued to the same person.
- **states:** PA
- **sample (PA):** "After the revocation of any license or registration, no new license or registration may be requested by or issued to the same licensee or registrant within a period of at least five years from the date of the revocation."

## prohibited conduct

### `self_bidding_prohibited` — bool
- **what:** Whether a licensed auctioneer or apprentice auctioneer is prohibited from bidding on and buying property at an auction they are conducting.
- **states:** PA
- **sample (PA):** "For any licensed auctioneer or apprentice auctioneer to bid and buy for himself at any auction he is conducting."

### `shill_bidding_prohibited` — bool
- **what:** Whether the use of false bidders, cappers, or puffers is explicitly prohibited.
- **states:** PA
- **sample (PA):** "Knowingly using false bidders, cappers or puffers."
