# Discovered fields — pharmacy

## support staff credentials and supervision

### `pharmacy_technician_registration_required` — bool
- **what:** Whether pharmacy technicians must register with the state board before practicing.
- **states:** PA
- **sample (PA):** "A pharmacy technician shall register with the board biennially on a form prescribed by the board and pay a registration fee established by the board by regulation."

### `pharmacy_technician_trainee_permit_available` — bool
- **what:** Whether the board may issue a temporary permit allowing a trainee to perform pharmacy technician duties under supervision before full registration.
- **states:** PA
- **sample (PA):** "'Pharmacy technician trainee' means an individual who has been issued a temporary permit by the board that authorizes the individual to perform the duties of a pharmacy technician under the direct and immediate personal supervision of a licensed pharmacist."

### `technician_to_pharmacist_supervision_model` — enum[direct and immediate personal supervision, general supervision, remote supervision]
- **what:** The level of pharmacist oversight required when a pharmacy technician performs duties.
- **states:** PA
- **sample (PA):** "A pharmacy technician shall be responsible to and under the direct and immediate personal supervision of a board-licensed pharmacist."

### `technician_data_entry_without_immediate_supervision_allowed` — bool
- **what:** Whether pharmacy technicians may perform prescription data entry without the pharmacist physically present, subject to documented safeguards.
- **states:** PA
- **sample (PA):** "A pharmacy technician may conduct data entry, including prescription entry, drug order or patient information, into a patient profile via technological means without the immediate supervision of a board-licensed pharmacist if all of the following apply."

### `technician_minimum_age` — int
- **what:** Minimum age required to register as a pharmacy technician.
- **states:** PA
- **sample (PA):** "Be at least seventeen years of age and possess a high school diploma or equivalent."

### `technician_trainee_minimum_age` — int
- **what:** Minimum age required to obtain a pharmacy technician trainee permit.
- **states:** PA
- **sample (PA):** "Be at least sixteen years of age."

## collaborative practice and drug therapy management

### `collaborative_drug_therapy_management_authorized` — bool
- **what:** Whether pharmacists are authorized to manage drug therapy under a written collaborative agreement with a licensed physician.
- **states:** PA
- **sample (PA):** "A pharmacist shall enter into a written collaborative agreement with a licensed physician authorizing the management of drug therapy for a disease or for a condition or symptom of a disease before practicing the management of drug therapy in a setting other than an institutional setting."

### `drug_therapy_management_settings` — list[str]
- **what:** Practice settings in which pharmacist drug therapy management is authorized (e.g., institutional, non-institutional/community).
- **states:** PA
- **sample (PA):** "A pharmacist shall be permitted to enter into a written agreement or protocol with a licensed physician authorizing the management of drug therapy in an institutional setting."

### `drug_therapy_management_protocol_max_duration_years` — int
- **what:** Maximum number of years a drug therapy management protocol or collaborative agreement may remain in effect before mandatory review.
- **states:** PA
- **sample (PA):** "Remain in effect for a period not to exceed two years upon the conclusion of which, or sooner, the parties shall review the agreement and make a determination as to its renewal, necessary modifications or termination."

### `prescriptive_authority_explicitly_excluded` — bool
- **what:** Whether the statute explicitly states that pharmacists do not obtain prescriptive authority through collaborative or drug therapy management provisions.
- **states:** PA
- **sample (PA):** "Nothing in this act shall be construed to provide prescriptive authority to a pharmacist."

### `professional_liability_insurance_required_for_cdtm` — bool
- **what:** Whether pharmacists engaged in collaborative drug therapy management must carry professional liability insurance.
- **states:** PA
- **sample (PA):** "A pharmacist who is a party to a written agreement or protocol authorizing the management of drug therapy shall obtain and maintain, to the satisfaction of the board, professional liability insurance coverage in the minimum amount of one million dollars ($1,000,000) per occurrence or claims made."

### `professional_liability_insurance_minimum_per_occurrence` — int
- **what:** Minimum professional liability insurance coverage amount (in dollars) required per occurrence for pharmacists in collaborative drug therapy management.
- **states:** PA
- **sample (PA):** "professional liability insurance coverage in the minimum amount of one million dollars ($1,000,000) per occurrence or claims made"

## pharmacy facility licensing and operation

### `pharmacy_permit_required` — bool
- **what:** Whether a separate permit issued by the board is required to operate a pharmacy location.
- **states:** PA
- **sample (PA):** "No person shall operate or advertise a pharmacy until the person has been granted a pharmacy permit by the board."

### `pharmacist_in_charge_required` — bool
- **what:** Whether a licensed pharmacist must be designated as in charge of and physically supervising each permitted pharmacy at all times it is open.
- **states:** PA
- **sample (PA):** "Every pharmacy shall, at all times when open, be under the constant direct and personal supervision and management of a pharmacist duly licensed in Pennsylvania who shall have personal supervision of not more than one pharmacy at the same time."

### `nonresident_pharmacy_registration_required` — bool
- **what:** Whether out-of-state pharmacies that ship or mail drugs into the state must register with the state board.
- **states:** PA
- **sample (PA):** "A nonresident pharmacy shall register on a biennial basis with the board and obtain a certificate of registration to conduct a pharmacy in accordance with this section."

### `nonresident_pharmacy_toll_free_number_required` — bool
- **what:** Whether nonresident pharmacies must provide a toll-free telephone number for patient communication with a pharmacist.
- **states:** PA
- **sample (PA):** "A nonresident pharmacy shall, during its regular hours of operation, but not less than six days per week, and for a minimum of forty hours per week, provide a toll-free telephone number to facilitate communication between patients in this Commonwealth and a pharmacist."

### `prescription_record_retention_years` — int
- **what:** Minimum number of years a pharmacy must retain prescription records.
- **states:** PA
- **sample (PA):** "Contains a suitable book or file in which shall be preserved, for a period of not less than two years, every prescription compounded or dispensed therein."

## prescription dispensing rules

### `emergency_prescription_refill_authorized` — bool
- **what:** Whether pharmacists may dispense an emergency refill of a prescription without prescriber authorization under defined conditions.
- **states:** PA
- **sample (PA):** "'Emergency prescription' means a refill of a prescription which is essential to the continuation of therapy in a chronic condition, for which the refill has not been authorized and for which the pharmacist notifies, within seventy-two hours, the prescriber that an emergency prescription has been dispensed."

### `emergency_prescription_max_supply_days` — int
- **what:** Maximum days' supply that may be dispensed as an emergency prescription refill (primary limit; a longer secondary limit may apply when the drug is not packaged in a 72-hour supply).
- **states:** PA
- **sample (PA):** "the quantity of that refill is in conformity with the prescribed directions for use, but limited to a seventy-two hour emergency supply. If the prescription is not dispensed or sold in a seventy-two hour supply, an amount not to exceed a thirty-day emergency supply may be dispensed or sold."

### `generic_substitution_authorized` — bool
- **what:** Whether pharmacists are authorized to substitute a generically equivalent drug for a brand-name prescription.
- **states:** PA
- **sample (PA):** "This restrictive clause shall not apply to proper substituting of generically equivalent drugs as stipulated under the act of November 24, 1976 (P.L.1163, No.259), referred to as the Generic Equivalent Drug Law."

### `prescription_transfer_between_pharmacies_authorized` — bool
- **what:** Whether pharmacies may transfer valid refillable prescriptions to another pharmacy, subject to recordkeeping requirements.
- **states:** PA
- **sample (PA):** "Adheres to the following requirements for transferring prescriptions between pharmacies in Pennsylvania: The prescription is for a drug which is lawfully refillable. The drug is not a Schedule II controlled substance."

## patient information and counseling rights

### `price_disclosure_to_patient_required` — bool
- **what:** Whether pharmacists must disclose drug pricing information (retail price, cost-sharing amount, generic alternatives) to patients upon request.
- **states:** PA
- **sample (PA):** "For every prescription medication that a consumer intends to purchase, a pharmacist shall, upon request, disclose the following: The current pharmacy retail price of the brand-name drug and any generically equivalent drug available at the pharmacy."

## reporting and disciplinary obligations

### `multiple_state_licensure_reporting_required` — bool
- **what:** Whether pharmacists licensed in multiple states must report that fact and any out-of-state disciplinary actions to the home-state board.
- **states:** PA
- **sample (PA):** "Any licensed pharmacist of this Commonwealth who is also licensed to practice pharmacy in any other state, territory or country shall report this information to the board on the biennial registration application. Any disciplinary action taken in other states, territories and countries shall be reported to the board on the biennial registration application or within ninety days of final disposition."

### `impaired_professional_program_available` — bool
- **what:** Whether the board operates or recognizes a formal program for impaired pharmacists that may defer or dismiss disciplinary action while the licensee participates in treatment.
- **states:** PA
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the professional is progressing satisfactorily in an approved treatment program."

### `mandatory_reporting_of_impaired_pharmacist` — bool
- **what:** Whether hospitals, health care facilities, peers, or colleagues are legally required to report a pharmacist who shows signs of active addiction, diversion, or incapacity.
- **states:** PA
- **sample (PA):** "Any hospital or health care facility, peer or colleague who has substantial evidence that a professional has an active addictive disease for which the professional is not receiving treatment, is diverting a controlled substance or is mentally or physically incompetent to carry out the duties of his or her license or certificate shall make or cause to be made a report to the board."

## poison and hazardous substance controls

### `poison_schedule_maintained_by_board` — bool
- **what:** Whether the board maintains statutory schedules of poisons with specific sale, labeling, and recordkeeping requirements separate from federal controlled substance schedules.
- **states:** PA
- **sample (PA):** "Poison means and includes the compositions of the following schedules: Schedule 'A'... Schedule 'B'... The board may add to, or delete from, any of the aforementioned schedules when, in the opinion of the board, it is in the interest of the public health."

### `poison_sale_minimum_age` — int
- **what:** Minimum age of a purchaser to whom a scheduled poison may be sold.
- **states:** PA
- **sample (PA):** "No poison enumerated in Schedule 'A' and 'B', or poisons which may hereinafter be added to said schedules, shall be sold, delivered or furnished to any person who is less than sixteen years of age."

### `poison_sale_recordkeeping_required` — bool
- **what:** Whether sales of Schedule A poisons must be recorded in a dedicated poison log including purchaser identity, quantity, and stated purpose.
- **states:** PA
- **sample (PA):** "No person shall sell, distribute or furnish any poisons included in Schedule 'A'... without making or causing to be made at the time of selling an entry in a poison book kept solely for that purpose, stating the date of sale, the name, address and signature of the purchaser, the name and quantity of the poison sold."
