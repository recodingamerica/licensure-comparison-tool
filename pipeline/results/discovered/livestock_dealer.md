# Discovered fields — livestock_dealer

## financial security and bonding

### `surety_bond_required` — bool
- **what:** Whether the applicant must post a surety bond, cash bond, irrevocable letter of credit, or equivalent financial security before a license is issued.
- **states:** IL, ND, OH, UT
- **sample (IL):** "Prior to the issuance of a license, as a livestock dealer, each applicant therefor shall file a surety bond with the Department, conditioned on his performance of all duties required by law of a livestock dealer."

### `bond_minimum_amount_dollars` — int
- **what:** The statutory minimum dollar amount of the required surety bond or equivalent security.
- **states:** IL, ND, OH, UT
- **sample (ND):** "A bond required by this chapter may not be in an amount less than ten thousand dollars."

### `bond_alternative_forms` — list[str]
- **what:** The alternative instruments accepted in lieu of a traditional surety bond to satisfy financial responsibility requirements.
- **states:** IL, ND, OH, UT
- **sample (ND):** "As a condition of licensure, the applicant shall post a bond with the agriculture commissioner. The bond must be: a. A surety bond; b. A cash bond; or c. An irrevocable letter of credit."

### `federal_bond_accepted_in_lieu` — bool
- **what:** Whether a bond already on file with the USDA Packers and Stockyards Administration satisfies the state bonding requirement.
- **states:** IL, ND, OH, UT
- **sample (IL):** "In cases where a livestock dealer under this Act has a bond on file with the United States Department of Agriculture, Packers and Stockyards, Agricultural Marketing Service, or any successor agency, and such bond is in an amount and conditioned upon such terms so as to meet the requirements of this Act, separate bond coverage under this Act is not required."

### `bond_covers_agent_transactions` — bool
- **what:** Whether the dealer's bond or equivalent security explicitly covers livestock transactions conducted by the dealer's agents.
- **states:** IL, ND, UT
- **sample (IL):** "The surety bond, trust fund agreement or letter of credit filed by the licensee with the Department shall cover all livestock dealer transactions of the agent."

### `insolvency_trust_fund_procedure` — bool
- **what:** Whether the statute establishes a formal trust fund and trustee procedure administered by the licensing authority upon a dealer's insolvency or bond default.
- **states:** ND, OH, UT
- **sample (ND):** "If a livestock dealer defaults in the provisions of any bond required by this chapter, the livestock dealer is deemed to be insolvent within the meaning of this chapter. The claim for relief for damages upon the bond... constitutes a trust fund in the hands of the agriculture commissioner for all persons having a claim for relief against the livestock dealer on the bond."

## agents and employees

### `agent_license_required` — bool
- **what:** Whether individuals acting as agents on behalf of a licensed dealer must themselves obtain a separate license or permit.
- **states:** IL, ND, UT
- **sample (ND):** "Before an individual may serve as the agent of a livestock dealer, the individual must be licensed by the agriculture commissioner."

### `dealer_liable_for_agent_acts` — bool
- **what:** Whether the licensed dealer is explicitly held responsible or strictly liable for all livestock transactions conducted by their agents.
- **states:** CT, IL, ND, OH, UT
- **sample (ND):** "The principal has filed with the agriculture commissioner a signed statement indicating that the principal is responsible for and will be held strictly liable for any acts and omissions arising out of the agent's livestock dealings, even if the dealings were not authorized by the principal."

### `agent_prohibited_from_own_account_transactions` — bool
- **what:** Whether agents are explicitly prohibited from conducting livestock transactions in their own name or for their own account.
- **states:** IL, ND
- **sample (ND):** "While acting as an agent, an individual may not conduct any transaction involving livestock in the agent's own name."

### `employee_restrictions_on_defaulters` — bool
- **what:** Whether a licensed dealer is prohibited from employing a person who previously defaulted on livestock purchase contracts or whose dealer license was revoked, unless additional bond coverage or guarantees are provided.
- **states:** ND, OH
- **sample (OH):** "No licensed livestock dealer or broker shall employ as an employee a person who, as a dealer or broker, previously defaulted on contracts pertaining to the purchase, exchange, or sale of livestock until the licensee does both of the following: (1) Increases the value of the dealer's or broker's bond... (2) Signs and files with the director an agreement that guarantees, without condition, all contracts pertaining to the purchase, exchange, or sale of livestock made by such person while in the employ of the licensee."

## license tiers and volume thresholds

### `tiered_dealer_classification` — bool
- **what:** Whether the statute creates distinct license tiers based on annual volume of animals handled (e.g., 'small dealer' vs. 'dealer/broker').
- **states:** CT, OH
- **sample (OH):** "'Small dealer' means any person found by the department buying, receiving, selling... any animals in an amount of two hundred fifty head or less of cattle, horses, or other equidae or five hundred head or less of sheep, goats, or other bovidae, swine or other suidae, poultry, alpacas, llamas, or monitored captive deer... during any one year."

### `volume_threshold_for_licensure` — str
- **what:** The minimum number of animals or dollar value of transactions that triggers the licensing requirement.
- **states:** CT, OH
- **sample (OH):** "'Dealer' or 'broker' means any person found by the department of agriculture buying, receiving, selling... any animals in an amount of more than two hundred fifty head of cattle, horses, or other equidae or five hundred head of sheep, goats, or other bovidae, swine and other suidae, poultry, alpacas, llamas, or monitored captive deer... during any one year."

### `exemptions_from_licensure` — list[str]
- **what:** Categories of persons or entities explicitly exempt from the dealer licensing requirement.
- **states:** CT, DE, IL, ND, OH, UT
- **sample (CT):** "The provisions of this chapter shall not apply to (1) any person... which by dispersal sale is permanently discontinuing the activities or business of a livestock producer; (2) any person... which sells livestock that have been raised on the premises; (3) any livestock producer who purchases or receives livestock for the purpose of producing milk, meat or other animal products..."

## what animals are covered

### `species_covered` — list[str]
- **what:** The specific animal species or categories explicitly included in the statutory definition of 'livestock' subject to dealer regulation.
- **states:** CT, DE, IL, ND, OH, UT
- **sample (UT):** "'Livestock' means cattle, swine, equines, sheep, camelidae, ratites, bison, goats, and domesticated elk as defined in Section 4-39-102."

### `poultry_included_in_livestock_definition` — bool
- **what:** Whether poultry is explicitly included within the statutory definition of livestock subject to dealer regulation.
- **states:** DE, OH
- **sample (DE):** "'Livestock' means any cattle, sheep, swine, goats, horses, mules, other equines, poultry or cultured aquatic stock."

### `captive_deer_regulatory_provisions` — bool
- **what:** Whether the statute includes specific provisions for captive or monitored deer (e.g., white-tailed deer, chronic wasting disease testing) within the dealer licensing framework.
- **states:** OH, UT
- **sample (OH):** "A person who wishes to propagate captive deer with status or captive deer with certified chronic wasting disease status shall obtain a license under section 943.03 or 943.031 of the Revised Code in addition to a captive white-tailed deer propagation license issued under section 1533.71 of the Revised Code."

## animal health and disease control

### `disease_testing_authority` — bool
- **what:** Whether the statute authorizes or requires periodic disease testing (e.g., tuberculosis, brucellosis) of livestock held by dealers.
- **states:** CT, IL, OH
- **sample (CT):** "All livestock owned by a livestock dealer or held by a livestock dealer, pending sale, exchange, resale or shipment on premises owned, rented, leased or borrowed by such dealer may be subjected periodically to diagnostic tests for infectious diseases, including, but not limited to, tuberculin and brucellosis tests."

### `quarantine_compliance_required` — bool
- **what:** Whether dealers are required to comply with quarantine orders and related biosecurity or sanitation requirements for diseased or exposed livestock.
- **states:** CT, IL, OH
- **sample (CT):** "Such dealer shall not be prohibited from engaging in business as a dealer, provided such dealer shall comply with all quarantine restrictions and orders and any isolation, bio-security and sanitation requirements of the department in respect to quarantined livestock."

### `sanitation_inspection_required` — bool
- **what:** Whether dealers are required to maintain sanitary conditions and submit to veterinary or departmental inspection of yards, pens, premises, and vehicles used for livestock.
- **states:** CT, OH, UT
- **sample (OH):** "Each small dealer, dealer, or broker leasing, renting, operating, or owning livestock yards, pens, premises, or vehicles in which animals are quartered, fed, held, or transported, shall have a veterinary inspector approved by the department of agriculture, inspect, when directed, all such yards, premises, and vehicles and shall thoroughly and completely disinfect all such yards, pens, premises, and vehicles."

## weighing and market facility rules

### `weighing_facility_license_required` — bool
- **what:** Whether dealers operating weighing facilities must obtain a separate scale certification or employ licensed weighers, and submit to scale inspection.
- **states:** OH, UT
- **sample (OH):** "No license shall be issued by the department to a dealer or broker having weighing facilities until the applicant has filed with the department a copy of a scale test certificate showing the weighing facilities to be in satisfactory condition, a copy of the license of each weigher employed by the applicant, and a certificate of inspection by the department showing livestock market facilities to be in satisfactory sanitary condition."

### `livestock_auction_market_exemption_or_overlap` — bool
- **what:** Whether state-federal approved livestock auction markets or their operators are explicitly exempt from, or subject to separate regulation under, the dealer licensing chapter.
- **states:** DE, IL, UT
- **sample (DE):** "Those livestock markets and their owners and officers which are approved and are classified as state-federal approved livestock markets are exempt from this chapter."

## recordkeeping requirements

### `recordkeeping_retention_period_years` — int
- **what:** The minimum number of years (or equivalent period) that dealers are required to retain transaction records.
- **states:** IL, ND, OH, UT
- **sample (IL):** "These records along with any accompanying health certificates shall be maintained for a period of 3 years."

### `annual_report_filing_required` — bool
- **what:** Whether dealers must file an annual summary report of purchases and sales with the licensing authority.
- **states:** IL, UT
- **sample (IL):** "Each licensee shall file annually with the Department a report on prescribed forms not later than April 15 following the calendar year end or, if the records are kept on a fiscal year basis, not later than 90 days after the close of his fiscal year."

### `financial_responsibility_required` — bool
- **what:** Whether applicants must demonstrate financial solvency or submit a financial statement as a condition of licensure.
- **states:** ND, OH, UT
- **sample (ND):** "The agriculture commissioner shall deny an applicant a livestock dealer's license if: a. The applicant's current assets do not exceed the applicant's current liabilities."

## license discipline and enforcement

### `license_revocation_for_out_of_state_suspension` — bool
- **what:** Whether a prior suspension or revocation of a livestock dealer license by another state constitutes grounds for denial or revocation of the in-state license.
- **states:** CT, OH, UT
- **sample (CT):** "Where a license to deal in livestock, issued to the applicant or licensee by another state, has been suspended or revoked by such state within five years next preceding the date of issuance or renewal of a license under the provisions of section 22-385."

### `failure_to_pay_for_livestock_is_revocation_ground` — bool
- **what:** Whether failure to pay for purchased livestock in a timely manner is an explicit statutory ground for license denial, suspension, or revocation.
- **states:** IL, ND, OH, UT
- **sample (ND):** "The livestock dealer has failed to pay for livestock purchased in a timely manner and without reasonable cause."

### `beef_promotion_assessment_compliance_required` — bool
- **what:** Whether failure to remit mandatory beef promotion or checkoff assessments is an explicit ground for license suspension or revocation.
- **states:** IL, ND
- **sample (IL):** "failing to remit the assessment required in Section 9 of the Beef Market Development Act upon written complaint of the Checkoff Division of the Illinois Beef Association Board of Governors."

### `brand_or_veterinary_inspection_fee_payment_required` — bool
- **what:** Whether failure to pay brand inspection fees or veterinary inspection fees within a specified period is a ground for license denial or revocation.
- **states:** ND, UT
- **sample (ND):** "If the applicant has failed to pay brand inspection fees or veterinary inspection fees, as required by law, within sixty days of the date on which they were due."

## consumer and producer protections

### `commission_schedule_disclosure_required` — bool
- **what:** Whether dealers or agents must file or disclose a schedule of commissions, fees, and other charges they intend to collect.
- **states:** IL, UT
- **sample (UT):** "a schedule of the commissions, fees, and other charges the applicant intends to collect for services during the period of licensure."

### `self_dealing_fraud_provisions` — bool
- **what:** Whether the statute explicitly defines or creates a presumption of fraud when a dealer sells livestock below market price to a financially interested party or retains part of the sale price beyond agreed charges.
- **states:** IL, UT
- **sample (UT):** "The following constitutes prima facie evidence of fraud in the sale of livestock: (1) any sale of livestock at less than market price by a dealer to a person with whom the dealer has a financial interest; or (2) any sale out of which the dealer receives part of the sale price other than the agreed commission or other agreed charges."

### `nonresident_applicant_service_of_process_required` — bool
- **what:** Whether non-resident applicants must file an irrevocable consent to service of process within the state as a condition of licensure.
- **states:** IL, UT
- **sample (IL):** "Each non-resident applicant for an original license or renewal license shall file with the Department an irrevocable consent that actions against the applicant may be filed in the circuit court of the county where the plaintiff resides or where some part of the transaction occurred."
