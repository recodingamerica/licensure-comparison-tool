# Discovered fields — wholesale_drug_distributor

## licensing and registration rules

### `license_per_facility_required` — bool
- **what:** Whether a separate license must be obtained for each physical facility operated by the distributor.
- **states:** PA
- **sample (PA):** "A person shall obtain a separate license to operate each facility."

### `surety_bond_required` — bool
- **what:** Whether applicants must submit a surety bond as part of the license application.
- **states:** PA
- **sample (PA):** "The applicant or owner shall submit a surety bond of $100,000 to the department with an application."

### `surety_bond_amount_dollars` — int
- **what:** Standard surety bond amount in dollars required with the license application.
- **states:** PA
- **sample (PA):** "The applicant or owner shall submit a surety bond of $100,000 to the department with an application."

### `surety_bond_minimum_dollars` — int
- **what:** Minimum surety bond amount in dollars after any department-approved reduction.
- **states:** PA
- **sample (PA):** "The surety bond may not be reduced to less than $25,000."

### `license_application_fee_dollars` — int
- **what:** One-time fee in dollars required when submitting the initial license application.
- **states:** PA
- **sample (PA):** "Each person who applies for a license shall submit a fee of $10 with the license application."

### `license_renewal_fee_dollars` — int
- **what:** Fee in dollars required when renewing the wholesale distributor license.
- **states:** PA
- **sample (PA):** "The license renewal fee shall be $100, unless changed by regulation, and shall be submitted with the completed license renewal form."

### `late_renewal_fee_per_month_dollars` — int
- **what:** Additional fee in dollars charged per month (or portion thereof) for late submission of a license renewal.
- **states:** PA
- **sample (PA):** "The late submission of a completed license renewal form shall be accompanied by a late payment fee of $25 for each month or portion thereof that expired after the license renewal was due."

### `revocation_reinstatement_waiting_period_years` — int
- **what:** Number of years a person must wait after license revocation before applying for reinstatement.
- **states:** PA
- **sample (PA):** "A person whose license has been revoked may not apply for reinstatement until five years have expired during which the license was revoked."

## facility and storage standards

### `facility_physical_requirements` — list[str]
- **what:** List of physical and environmental requirements that a licensed facility must meet for storage and handling of prescription drugs.
- **states:** PA
- **sample (PA):** "Have storage areas designed to provide adequate lighting, ventilation, temperature, sanitation, humidity, space, equipment and security conditions."

### `quarantine_area_required` — bool
- **what:** Whether the facility must maintain a designated quarantine area for outdated, damaged, deteriorated, misbranded, or adulterated drugs.
- **states:** PA
- **sample (PA):** "Have a quarantine area for storage of prescription drugs that are outdated, damaged, deteriorated, misbranded or adulterated or that are in immediate or sealed secondary containers that have been opened."

### `temperature_humidity_monitoring_required` — bool
- **what:** Whether the facility must use temperature and humidity recording equipment or logs to document proper drug storage conditions.
- **states:** PA
- **sample (PA):** "Appropriate manual, electromechanical or electronic temperature and humidity recording equipment, devices or logs shall be utilized to document proper storage of prescription drugs."

### `security_system_required` — bool
- **what:** Whether the facility must be equipped with an alarm and security system to detect unauthorized entry and protect against theft and diversion.
- **states:** PA
- **sample (PA):** "The facility shall be equipped with an alarm system to detect entry after hours."

### `incoming_outgoing_inspection_required` — bool
- **what:** Whether each incoming and outgoing shipment of prescription drugs must be visually inspected for identity, contamination, and damage.
- **states:** PA
- **sample (PA):** "Upon receipt, each outside shipping container shall be visually examined for identity and to prevent the acceptance of contaminated prescription drugs or prescription drugs that are otherwise unfit for distribution."

## recordkeeping and reporting

### `recordkeeping_retention_period_years` — int
- **what:** Number of years that distribution and inventory records must be retained and made available for inspection.
- **states:** PA
- **sample (PA):** "Inventories and records shall be made available for inspection and photocopying by authorized Federal, State or local law enforcement agency officials for a period of two years following disposition of the drugs."

### `records_remote_retrieval_deadline_days` — int
- **what:** Number of working days within which records stored off-site and not electronically retrievable must be made available upon authorized request.
- **states:** PA
- **sample (PA):** "Records kept at a central location apart from the facility and not electronically retrievable shall be made available for inspection within two working days of an authorized request by an authorized official of a Federal, State or local law enforcement agency."

### `written_policies_and_procedures_required` — bool
- **what:** Whether the licensee must establish, maintain, and adhere to written policies and procedures covering receipt, security, storage, inventory, and distribution of prescription drugs.
- **states:** PA
- **sample (PA):** "The licensee shall establish, maintain and adhere to written policies and procedures, which shall be followed for the receipt, security, storage, inventory and distribution of prescription drugs."

### `recall_withdrawal_procedure_required` — bool
- **what:** Whether the licensee's written procedures must include a specific protocol for handling drug recalls and withdrawals.
- **states:** PA
- **sample (PA):** "A procedure to be followed for handling recalls and withdrawals of prescription drugs."

### `application_change_notification_period_days` — int
- **what:** Number of days within which a licensee must notify the department of any change to information provided in the license application.
- **states:** PA
- **sample (PA):** "A change in any information provided in the application shall be submitted to the department within 30 days after the change or as otherwise required by the department."

## controlled substances handling

### `dea_registration_required_for_controlled_substances` — bool
- **what:** Whether a licensee dealing in controlled substances must separately register with the federal Drug Enforcement Administration.
- **states:** PA
- **sample (PA):** "The licensee that deals in controlled substances shall register with the Drug Enforcement Administration (DEA) and shall comply with all applicable DEA, State and local regulations."

## what counts as wholesale distribution

### `excluded_transaction_types` — list[str]
- **what:** Categories of drug transfers or sales explicitly excluded from the definition of wholesale distribution and therefore not subject to licensure.
- **states:** PA
- **sample (PA):** "Notwithstanding the foregoing, the phrase does not include: Intracompany sales or joining together of five or fewer pharmacies to place a direct order of medicine from the pharmaceutical manufacturer."

### `virtual_manufacturer_recognized` — bool
- **what:** Whether the statute recognizes a 'virtual manufacturer' category for entities that hold drug approvals but never take physical possession of the drug.
- **states:** PA
- **sample (PA):** "A person with a place of business located in this Commonwealth in the business of manufacturing and distributing a drug or medical device that: Holds the drug or device approval and label code or is otherwise identified on the product label from the United States Food and Drug Administration. At no time takes physical possession of any drug or device in this Commonwealth."

## penalties and enforcement

### `civil_penalty_per_day_dollars` — int
- **what:** Maximum civil penalty in dollars assessed per day for operating without a required license.
- **states:** PA
- **sample (PA):** "The department shall have authority to assess a civil penalty of up to $500 for each day that a person engages in the wholesale distribution of prescription drugs without a license as required by this act."

### `criminal_penalty_first_offense` — str
- **what:** Criminal classification and sentencing range for a first offense of operating without a license.
- **states:** PA
- **sample (PA):** "A person who engages in the wholesale distribution of prescription drugs without a license as required by this act commits a misdemeanor of the third degree and shall, upon conviction, be sentenced to pay a fine of not more than $2,000 and to imprisonment for not more than six months, or both, for the first violation."

### `criminal_penalty_subsequent_offense` — str
- **what:** Criminal sentencing range for second and subsequent offenses of operating without a license.
- **states:** PA
- **sample (PA):** "On the second and each subsequent conviction, the person shall be sentenced to pay a fine of not less than $5,000 nor more than $20,000 or to imprisonment for not less than six months nor more than one year, or both."

### `injunction_authority` — bool
- **what:** Whether the issuing authority may seek a court injunction to stop unlicensed wholesale distribution activity.
- **states:** PA
- **sample (PA):** "The department may maintain an action for an injunction to restrain a person from operating a facility within this Commonwealth through which it engages in the wholesale distribution of prescription drugs when that person does not have a license and a current renewal of that license."

## personnel and qualifications

### `responsible_persons_list_required` — bool
- **what:** Whether the licensee must maintain a list of officers, directors, managers, and other persons in charge of wholesale drug distribution, including their duties and qualifications.
- **states:** PA
- **sample (PA):** "Establish and maintain lists of officers, directors, managers and other persons in charge of wholesale drug distribution, storage and handling, including a description of their duties and a summary of their qualifications."
