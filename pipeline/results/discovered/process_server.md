# Discovered fields — process_server

## who must register and when

### `annual_service_threshold_for_registration` — int
- **what:** Minimum number of services of process per calendar year that triggers mandatory registration.
- **states:** CA, MT
- **sample (CA):** "Any natural person who makes more than 10 services of process within this state during one calendar year, for specific compensation or in expectation of specific compensation... shall file and maintain a verified certificate of registration"

### `registering_authority` — enum[county clerk, county auditor, state department]
- **what:** The specific government office with which a process server must register.
- **states:** CA, MT, NV, WA
- **sample (WA):** "Register as a process server with the auditor of the county in which the process server resides or operates his or her principal place of business."

### `registration_jurisdiction_basis` — enum[county of residence, county of principal place of business, either residence or principal place of business]
- **what:** Whether registration is filed in the county of the registrant's residence, principal place of business, or either.
- **states:** CA, WA
- **sample (CA):** "file and maintain a verified certificate of registration as a process server with the county clerk of the county in which he or she resides or has his or her principal place of business"

### `state_residency_required` — bool
- **what:** Whether the applicant must be a resident of the state to register.
- **states:** CA, WA
- **sample (CA):** "A statement that the registrant has been a resident of this state for a period of one year immediately preceding the filing of the certificate."

### `state_residency_duration_months` — int
- **what:** Minimum number of months of state residency required prior to registration.
- **states:** CA
- **sample (CA):** "A statement that the registrant has been a resident of this state for a period of one year immediately preceding the filing of the certificate."

### `exempted_persons` — list[str]
- **what:** Categories of persons explicitly exempt from the registration or licensing requirement.
- **states:** CA, MT, NV, WA
- **sample (CA):** "This chapter shall not apply to any of the following: Any sheriff, marshal, or government employee who is acting within the course and scope of his or her employment. An attorney or his or her employees, when serving process related to cases for which the attorney is providing legal services. Any person who is specially appointed by a court to serve its process. A licensed private investigator or his or her employees."

### `registration_renewal_trigger_events` — list[str]
- **what:** Events beyond the passage of time that require a process server to renew or update their registration.
- **states:** MT, WA
- **sample (WA):** "A process server required to register under RCW 18.180.010 must renew the registration within one year of the date of the initial registration or when the registrant changes his or her name, the name of his or her business, business address, or business telephone number, whichever occurs sooner."

### `experience_required_years` — int
- **what:** Minimum years of prior experience as a process server required before a license will be granted.
- **states:** NV
- **sample (NV):** "If an applicant for a process server's license, have at least 2 years' experience as a process server, or the equivalent thereof, as determined by the Board."

### `written_examination_required` — bool
- **what:** Whether applicants must pass a written examination before a license is granted.
- **states:** NV
- **sample (NV):** "The Board shall require an applicant to pass a written examination for an initial license and may require an applicant to pass an oral examination."

### `entity_types_eligible_to_register` — list[str]
- **what:** Types of legal entities (natural persons, partnerships, corporations) that may register or obtain a license as a process server.
- **states:** CA, NV
- **sample (CA):** "Any corporation or partnership that derives or expects to derive compensation from service of process within this state shall also file and maintain a verified certificate of registration as a process server"

## financial responsibility and bonding

### `surety_bond_required` — bool
- **what:** Whether a surety bond or cash deposit is required as a condition of registration.
- **states:** CA
- **sample (CA):** "A certificate of registration shall be accompanied by a bond of two thousand dollars ($2,000), executed by an admitted surety insurer and conditioned upon compliance with the provisions of this chapter and all laws governing the service of process in this state."

### `surety_bond_amount_usd` — int
- **what:** Dollar amount of the required surety bond or cash deposit alternative.
- **states:** CA
- **sample (CA):** "A certificate of registration shall be accompanied by a bond of two thousand dollars ($2,000)"

### `liability_insurance_required` — bool
- **what:** Whether the registrant must maintain a liability insurance policy as a condition of licensure.
- **states:** NV
- **sample (NV):** "Before issuing any license or annual renewal thereof, the Board shall require satisfactory proof that the applicant or licensee is covered by a policy of insurance for protection against liability to third persons, with limits of liability in amounts not less than $200,000"

## proof of service documentation rules

### `registration_number_required_on_proof_of_service` — bool
- **what:** Whether the process server's registration number must appear on any proof of service they sign.
- **states:** CA, WA
- **sample (CA):** "Any proof of service of any process which is signed by a registrant under this chapter shall indicate the county in which he or she is registered and the number assigned to him or her by Section 22355."

### `county_of_registration_required_on_proof_of_service` — bool
- **what:** Whether the county of registration must be indicated on any proof of service signed by the process server.
- **states:** CA, WA
- **sample (WA):** "A process server required to register under RCW 18.180.010 shall indicate the process server's registration number and the process server's county of registration on any proof of service the process server signs."

### `employee_proof_of_service_requirements` — str
- **what:** Rules specifying what identifying information employees or independent contractors of a registrant must include on proofs of service.
- **states:** CA, WA
- **sample (WA):** "Employees of a process server required to register under RCW 18.180.010 shall indicate the employer's registration number and the employer's county of registration on any proof of service the registrant's employee signs."

### `fee_recovery_conditioned_on_registration` — bool
- **what:** Whether a party's ability to recover the costs of service of process is conditioned on the process server being properly registered.
- **states:** WA
- **sample (WA):** "any person who is otherwise entitled to collect the costs of service of process shall not be entitled to collect those costs if the person does not use a process server who under this chapter either is required to register or is exempt from the registration requirement."

## registration credentials and identification

### `identification_card_issued` — bool
- **what:** Whether the registering authority issues a physical identification card to the registered process server.
- **states:** CA, MT, NV
- **sample (CA):** "The county clerk shall maintain a register of process servers and assign a number and issue an identification card to each process server."

### `temporary_identification_card_available` — bool
- **what:** Whether a temporary identification card is issued while a background check is pending.
- **states:** CA, NV
- **sample (CA):** "The county clerk shall issue a temporary identification card, for no additional fee, to applicants who are required to submit Request for Live Scan forms for background checks to the Federal Bureau of Investigation and the Department of Justice. This card shall be valid for 120 days."

### `identification_card_must_be_carried_while_working` — bool
- **what:** Whether the process server is required to carry their identification card while performing duties.
- **states:** MT, NV
- **sample (MT):** "A holder of an identification card shall carry the card while performing the cardholder's duties. A peace officer of this state or any of its political subdivisions may request to see the card at any reasonable time, and the card must be shown."

### `license_or_registration_nontransferable` — bool
- **what:** Whether the license or registration is explicitly non-transferable to another person or entity.
- **states:** MT, NV
- **sample (MT):** "A license issued under this chapter is not transferable."

### `advertising_must_include_license_number` — bool
- **what:** Whether all advertising by a licensee must include the licensee's name and license number as they appear in official records.
- **states:** MT, NV
- **sample (MT):** "Every advertisement by a licensee soliciting or advertising business must contain the licensee's name, address, and license number as they appear in the records of the department."

## background check and criminal history

### `fingerprint_background_check_required` — bool
- **what:** Whether applicants must submit fingerprints for a criminal background check through state or federal agencies.
- **states:** CA, MT, NV
- **sample (CA):** "the registrant shall also submit a completed Request for Live Scan form confirming fingerprint submission to the Department of Justice and the Federal Bureau of Investigation, in order to verify that the registrant has not been convicted of a felony"

### `felony_conviction_disqualifying` — bool
- **what:** Whether a felony conviction disqualifies an applicant from registration or licensure.
- **states:** CA, MT, NV
- **sample (CA):** "A statement, signed by the registrant under penalty of perjury, that the registrant has not been convicted of a felony, or, if the registrant has been convicted of a felony, a copy of a certificate of rehabilitation, expungement, or pardon."

### `rehabilitation_or_pardon_may_overcome_disqualification` — bool
- **what:** Whether a certificate of rehabilitation, expungement, or pardon can overcome a felony disqualification.
- **states:** CA, NV
- **sample (CA):** "if the registrant has been convicted of a felony, a copy of a certificate of rehabilitation, expungement, or pardon"

## supervision and employer responsibility

### `registrant_responsible_for_employee_conduct` — bool
- **what:** Whether the registered process server is legally responsible for the conduct of their employees and independent contractors.
- **states:** CA, MT, NV
- **sample (CA):** "A registrant shall be responsible at all times for the good conduct of his or her employees acting within the course or scope of their employment, and any person acting as an independent contractor within the course or scope of the agency relationship with the registrant."

### `independent_contractor_use_permitted` — bool
- **what:** Whether a registrant may use independent contractors to perform service of process on their behalf.
- **states:** CA
- **sample (CA):** "No registrant shall permit any individual to sign any proof of service of any process as an independent contractor unless all of the following conditions are met: The independent contractor is performing pursuant to a written independent contractor agreement with the registrant."
