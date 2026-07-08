# Discovered fields — junk_dealer

## recordkeeping and reporting

### `transaction_record_format` — enum[paper, electronic, either paper or electronic]
- **what:** Whether transaction records must be kept in paper form, electronic form, or either.
- **states:** AK, CT, DE, FL, GA, HI, OH, WA
- **sample (HI):** "Every dealer, or the agent, employee, or representative of the dealer, shall, immediately upon receipt of any article, record the following information, on an electronic recordkeeping form or a paper form authorized by the chief of police in each county"

### `transaction_record_retention_years` — int
- **what:** Number of years transaction records must be retained by the dealer.
- **states:** AK, CT, DE, FL, HI, OH, WA
- **sample (AK):** "A dealer shall maintain the records of a transaction required by AS 08.60.200 and 08.60.210 for five years after the date of the transaction."

### `electronic_reporting_to_law_enforcement_required` — bool
- **what:** Whether dealers are required to electronically transmit transaction records to law enforcement.
- **states:** CT, DE, FL, HI, OH, WA
- **sample (OH):** "The dealer shall electronically transfer, by twelve noon eastern standard time, the report for inclusion in the registry created pursuant to division (E) of section 4737.045 of the Revised Code."

### `reporting_frequency` — enum[daily, weekly, next business day, within 24 hours, upon request]
- **what:** How frequently dealers must submit transaction reports to law enforcement.
- **states:** AK, CT, DE, FL, OH, WA
- **sample (WA):** "Upon request, every pawnbroker and secondhand dealer doing business in the state shall furnish a full, true, and correct transcript of the record of all transactions conducted on the preceding day."

### `seller_photo_required` — bool
- **what:** Whether dealers must photograph the person selling or delivering goods at the time of transaction.
- **states:** DE, FL, HI, OH, WA
- **sample (DE):** "Pawnbrokers and secondhand dealers shall collect a photograph of the seller and all information pertaining to the seller, required on the electronic form, for every transaction regardless of value."

### `seller_thumbprint_required` — bool
- **what:** Whether dealers must collect a thumbprint from the person selling goods.
- **states:** DE, FL, OH
- **sample (FL):** "The right thumbprint, free of smudges and smears, of the person from whom the goods were acquired."

### `seller_vehicle_info_required` — bool
- **what:** Whether dealers must record the license plate number and description of the vehicle used to deliver goods.
- **states:** AK, CT, DE, FL, OH
- **sample (AK):** "A description, including the license plate information, of a motor vehicle used to deliver the scrap metal to the dealer"

### `seller_ownership_statement_required` — bool
- **what:** Whether dealers must obtain a signed statement from the seller affirming ownership or right to sell the goods.
- **states:** AK, CT, DE, FL, OH, WA
- **sample (AK):** "A scrap metal dealer shall require a person from whom the dealer is purchasing scrap metal for $100 or more to sign a written or electronic statement that the scrap metal is not stolen property."

### `weekly_sworn_statement_to_authorities` — bool
- **what:** Whether dealers must submit a sworn statement of transactions to local authorities on a weekly basis.
- **states:** CT, LA, WA
- **sample (CT):** "Each such dealer shall make, weekly, sworn statements of all his or her transactions under such license, describing the goods received and setting forth the name and residence and a description of the person from whom such goods were received"

## holding period and stolen property

### `holding_period_days` — int
- **what:** Minimum number of days purchased goods must be held before resale or disposal.
- **states:** CT, DE, FL, HI, OH, SC, WA
- **sample (SC):** "A person or entity shall keep each article of junk purchased other than junk that consists of nonferrous metals, as defined by Section 16-17-680, and vehicles for a period of seventy-two hours following the purchase"

### `holding_period_varies_by_material` — bool
- **what:** Whether the required holding period differs depending on the type of material (e.g., precious metals vs. general scrap vs. catalytic converters).
- **states:** DE, FL, HI, OH, WA
- **sample (DE):** "Scrap metal processors must hold platinum, gold and silver articles for 18 days... Every scrap metal processor subject to this chapter must keep for a period of 72 hours from the date and time the item was electronically reported... all copper or brass articles"

### `law_enforcement_hold_order_authority` — bool
- **what:** Whether law enforcement may issue a hold order requiring the dealer to retain specific property beyond the standard holding period.
- **states:** AK, DE, FL, OH, WA
- **sample (FL):** "Upon probable cause that goods held by a secondhand dealer are stolen, a law enforcement officer with jurisdiction may place a 90-day written hold order on the goods."

### `minimum_holding_period_before_resale_days_general_junk` — int
- **what:** Minimum number of days general junk (non-precious-metal, non-scrap) must be held before resale.
- **states:** CT, FL, HI, OH, SC, WA
- **sample (SC):** "A person or entity shall keep each article of junk purchased other than junk that consists of nonferrous metals, as defined by Section 16-17-680, and vehicles for a period of seventy-two hours following the purchase"

## what can and cannot be bought or sold

### `prohibited_items_list` — list[str]
- **what:** Categories of items that dealers are specifically prohibited from purchasing or receiving without special authorization.
- **states:** CT, DE, FL, LA, OH, SC
- **sample (DE):** "A scrap metal processor may not purchase the following items from an individual unless the individual, at the time of purchase, provides appropriate authorization... Metal bleachers; Hard-drawn copper; Metal beer kegs; Cemetery urns; Grave markers; Materials related to railroad infrastructure"

### `catalytic_converter_special_rules` — bool
- **what:** Whether the statute imposes specific additional requirements or restrictions on the purchase and sale of catalytic converters.
- **states:** AK, CT, DE, FL, LA, OH
- **sample (CT):** "No scrap metal processor, junk dealer or junk yard owner or operator may receive a catalytic converter of a motor vehicle that is not attached to such motor vehicle unless such processor, dealer, owner or operator, at the time of receipt: Records the place and date of the transaction..."

### `payment_method_restrictions` — list[str]
- **what:** Restrictions on the form of payment a dealer may use when purchasing goods (e.g., check only, no cash above a threshold).
- **states:** AK, CT, DE, FL, OH, WA
- **sample (FL):** "A secondary metals recycler may not enter into any cash transaction in excess of $1,000 for the purchase of regulated metals property"

### `restricted_regulated_metals_list` — list[str]
- **what:** Specific metal items or infrastructure components that require proof of ownership or authorization before a dealer may purchase them.
- **states:** CT, DE, FL, LA, OH, SC
- **sample (FL):** "The purchase of any of the following regulated metals property is subject to the restrictions provided in paragraph (a): 1. A manhole cover. 2. An electric light pole or other utility structure... 3. A guard rail. 4. A street sign, traffic sign, or traffic signal... 8. Railroad equipment..."

## who dealers may and may not do business with

### `prohibited_seller_categories` — list[str]
- **what:** Categories of persons from whom dealers are prohibited from purchasing goods.
- **states:** AK, CT, DE, FL, HI, OH, WA
- **sample (OH):** "No person shall purchase or receive by sale, barter, exchange, or otherwise, an article mentioned in sections 4737.01 to 4737.03, inclusive, of the Revised Code, of a minor or apprentice, knowing or having reason to believe him to be such, or from any person between the hours of nine p.m. and seven a.m."

### `minimum_seller_age` — int
- **what:** Minimum age of a person from whom a dealer may purchase goods.
- **states:** AK, CT, DE, FL, HI, OH, WA
- **sample (HI):** "A dealer shall not receive or purchase any article from any person under the age of eighteen."

### `known_thief_list_check_required` — bool
- **what:** Whether dealers must check sellers against a law-enforcement-provided list of known thieves or persons convicted of theft-related offenses before completing a transaction.
- **states:** OH, WA
- **sample (OH):** "The law enforcement agency that serves the jurisdiction in which a scrap metal dealer or a bulk merchandise container dealer is located shall provide to the scrap metal dealer or bulk merchandise container dealer a searchable, electronic list... of the names and descriptions of persons known to be thieves or receivers of stolen property. No scrap metal dealer or bulk merchandise container dealer shall purchase or receive articles from any person who is either identified on the list"

### `hours_of_operation_restrictions` — bool
- **what:** Whether the statute restricts the hours during which dealers may conduct transactions.
- **states:** AK, DE, FL, OH, WA
- **sample (OH):** "No person shall purchase or receive by sale, barter, exchange, or otherwise, an article mentioned in sections 4737.01 to 4737.03, inclusive, of the Revised Code, of a minor or apprentice, knowing or having reason to believe him to be such, or from any person between the hours of nine p.m. and seven a.m."

## junkyard location and physical site rules

### `physical_location_screening_standards` — list[str]
- **what:** Factors authorities must consider when approving or denying a junkyard location, such as proximity to schools, churches, or highways.
- **states:** AK, OH
- **sample (AK):** "the commissioner of public safety, the city council, and organized borough assembly, in considering applications and regulations, shall take into account (1) the nature and development of surrounding property; (2) the need to protect the local economy, adjacent land owners, and the motoring public from economically depressing and unsightly roadside locations; (3) the proximity of churches, schools, hospitals, public buildings, recreation areas, or other places of public gathering"

### `fencing_or_screening_required` — bool
- **what:** Whether a junkyard must be enclosed by a fence or other screening to obscure its contents from public view.
- **states:** AK, OH
- **sample (OH):** "Any fence constructed under sections 4737.05 to 4737.11, inclusive, of the Revised Code, shall be neatly constructed, shall be non-transparent, shall be kept in good order and repair"

### `highway_proximity_restriction` — bool
- **what:** Whether the statute restricts or regulates junkyards based on their proximity to highways, particularly interstate or primary systems.
- **states:** AK, OH, SC
- **sample (OH):** "'Junk yard' means an establishment or place of business that is maintained or operated for the purpose of storing, keeping, buying, or selling junk. For the purposes of sections 4737.05 to 4737.99 of the Revised Code, 'junk yard' includes scrap metal processing facilities that are located within one thousand feet of the nearest edge of the right of way of a highway in the interstate or primary system."

## automated kiosks and technology

### `automated_kiosk_regulated` — bool
- **what:** Whether the statute specifically addresses and regulates automated kiosks used to purchase secondhand goods.
- **states:** CT, DE, FL, HI, WA
- **sample (WA):** "'Automated kiosk' means a self-serve interactive machine that purchases secondhand electronic devices."

### `automated_kiosk_holding_period_days` — int
- **what:** Minimum number of days goods purchased through an automated kiosk must be held before disposal.
- **states:** DE, FL, HI, WA
- **sample (WA):** "Property bought by any secondhand dealer through the use of an automated kiosk must be held for at least thirty days after the secondhand property was accepted by the automated kiosk."

## pawnbroker loan terms

### `pawnbroker_interest_rate_cap` — str
- **what:** Maximum interest rate or fee schedule a pawnbroker may charge on loans secured by pledged property.
- **states:** AK, CT, DE, WA
- **sample (DE):** "No person conducting the business of a pawnbroker shall ask, demand or receive a greater rate of interest than 30 percent per month on any loans secured by pledge of personal property."

### `pawnbroker_minimum_loan_term_days` — int
- **what:** Minimum number of days a pawnbroker must hold pledged property before it may be sold.
- **states:** AK, CT, DE, WA
- **sample (WA):** "A pawnbroker shall not sell any property received in pledge, until a minimum of ninety days has expired."

### `pawnbroker_fire_insurance_required` — bool
- **what:** Whether pawnbrokers are required to carry fire insurance to protect pledged goods.
- **states:** AK, DE
- **sample (DE):** "Every person applying for a license to conduct the business of a pawnbroker shall first effect an insurance policy against fire for $50,000 for the protection of goods, pawned or pledged."

### `surety_bond_required` — bool
- **what:** Whether licensees must file a surety bond as a condition of licensure.
- **states:** CT, DE
- **sample (CT):** "shall, at the time of receiving such license, file, with the licensing authority of such city or town, a bond to such city or town, with competent surety, in the penal sum of two thousand dollars"

## criminal history and character requirements

### `felony_conviction_bars_licensure` — bool
- **what:** Whether a felony conviction disqualifies an applicant from obtaining a license.
- **states:** AK, CT, DE, FL
- **sample (CT):** "No license shall be issued under this section by the licensing authority to any person who has been convicted of a felony."

### `criminal_history_lookback_years` — int
- **what:** Number of years back a criminal history check covers for disqualifying offenses.
- **states:** DE, FL, WA
- **sample (DE):** "Must not have been convicted of a felony within 5 years of application date."

### `fingerprinting_required` — bool
- **what:** Whether applicants must submit fingerprints for a criminal background check as part of the licensing process.
- **states:** CT, DE, FL
- **sample (FL):** "The secondhand dealer shall furnish with her or his registration a complete set of her or his fingerprints, certified by an authorized law enforcement officer"

### `employee_criminal_history_restrictions` — bool
- **what:** Whether the statute restricts dealers from employing persons with certain criminal convictions.
- **states:** AK, CT
- **sample (AK):** "A pawnbroker may not knowingly employ a person to work in a pawnshop if, within five years before the employment begins, the person was convicted of, entered a plea of guilty to, entered a plea of no contest to, or had adjudication withheld for a felony or for a misdemeanor involving dishonesty."

## exemptions from dealer requirements

### `exempt_seller_categories` — list[str]
- **what:** Categories of sellers or transaction types that are exempt from standard dealer recordkeeping or holding requirements.
- **states:** AK, CT, DE, FL, LA, OH, WA
- **sample (AK):** "The requirements of AS 08.60.200 and 08.60.210 do not apply to a person's transactions with a dealer if the person maintains on file with the dealer the name, address, and telephone number of the person, and a taxpayer identification number issued by the federal Internal Revenue Service or a valid government-issued photo identification card."

### `nonprofit_exemption` — bool
- **what:** Whether transactions involving nonprofit, charitable, or religious organizations are exempt from dealer regulations.
- **states:** CT, DE, FL, LA, OH, WA
- **sample (LA):** "Any bona fide charity possessing a valid exemption under Section 501(c)(3) of the Internal Revenue Code."

### `garage_sale_exemption` — bool
- **what:** Whether private residential sales (garage sales, yard sales, estate sales) are exempt from dealer licensing or recordkeeping requirements.
- **states:** CT, DE, FL, LA, WA
- **sample (LA):** "Private residential sales commonly known as 'garage sales' or 'yard sales' as long as such sales take place at a residential address."
