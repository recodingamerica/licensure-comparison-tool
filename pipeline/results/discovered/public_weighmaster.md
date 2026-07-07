# Discovered fields — public_weighmaster

## deputy and delegated weighing

### `deputy_weighmaster_license_required` — bool
- **what:** Whether deputies or agents who issue certified weight tickets on behalf of the principal weighmaster must hold their own separate license.
- **states:** AZ, CA, WA
- **sample (WA):** "Any weighmaster must file an application with the director for a license for any employee or agent to operate and issue certified weight tickets from each scale which such weighmaster is licensed to operate."

### `deputy_weighmaster_responsibility_on_principal` — bool
- **what:** Whether the principal weighmaster is legally responsible for all acts performed by deputy weighmasters acting under their authority.
- **states:** AZ, CA, WA
- **sample (CA):** "A weighmaster may employ or designate any person to act for the weighmaster as a deputy weighmaster and shall be responsible for all acts performed by that person."

### `deputy_training_required_by_principal` — bool
- **what:** Whether the principal weighmaster is explicitly required to provide training to deputy weighmasters who use the principal's seal.
- **states:** AZ, CA
- **sample (AZ):** "A public weighmaster shall provide the necessary training for any deputy weighmaster using the public weighmaster's seal to certify weigh tickets."

### `limited_government_employee_license_available` — bool
- **what:** Whether a no-cost limited license may be issued to qualified government officers or employees authorizing them to act as public weighmasters only within the scope of their official duties.
- **states:** AZ, CT, NV
- **sample (CT):** "The commissioner may, upon request and without charge, issue a limited public weighmaster license to any qualified officer or employee of a state commission, board, institution or agency, authorizing such officer or employee to act as a public weighmaster only within the scope of such officer's or employee's official employment."

## weighing equipment requirements

### `scale_certification_required_for_license` — bool
- **what:** Whether the applicant must have access to a scale that is licensed, certified, or approved by the state before a weighmaster license is issued.
- **states:** AZ, CT, NV, WA
- **sample (AZ):** "Have possession of, or have available for use, a scale that is of sufficient capacity and size and that is licensed and certified pursuant to section 3-3451."

### `scale_platform_must_accommodate_full_vehicle` — bool
- **what:** Whether the scale platform must be large enough to accommodate the entire vehicle or combination of vehicles as one complete unit.
- **states:** CA, CT, NV, WA
- **sample (WA):** "No weighmaster shall weigh a vehicle or combination of vehicles to determine the weight of such vehicle or combination of vehicles unless the weighing device has a platform of sufficient size to accommodate such vehicle or combination of vehicles fully and completely as one entire unit."

### `scale_capacity_must_not_be_exceeded` — bool
- **what:** Whether a weighmaster is prohibited from using a scale to weigh a load that exceeds the scale's rated or nominal capacity.
- **states:** CT, WA
- **sample (CT):** "A public weighmaster shall not use any scale to weigh a load the value of which exceeds the nominal or rated capacity of the scale."

### `scale_testing_interval_months` — int
- **what:** The maximum number of months within which a weighing device must have been tested and approved by a state weights and measures officer before it may be used for certification.
- **states:** CT, NV, WA
- **sample (CT):** "A public weighmaster shall use a weighing device that is of a type suitable for the weighing of the amount and kind of material to be weighed and that has been tested and approved for use by a weights and measures officer of this state within a period of twelve months immediately preceding the date of the weighing."

### `unattended_automated_weighing_system_authorized` — bool
- **what:** Whether an automated or unattended weighing system not directly supervised by a weighmaster may be used to weigh vehicles and issue certificates.
- **states:** CA, WA
- **sample (CA):** "Any weighmaster weighing any vehicle moving construction materials … may use an unattended weighing system to weigh the vehicle and to issue a weighmaster certificate to buyers who opt to utilize the unattended system."

## weight certificate content and format

### `weight_certificate_required_fields` — list[str]
- **what:** The specific data elements that must appear on every weight certificate issued by a public weighmaster.
- **states:** AZ, CA, CT, NV, WA
- **sample (WA):** "The certified weight ticket shall … contain the following information: (1) The date of issuance; (2) The kind of commodity weighed, measured, or counted; (3) The name of the owner, agent, or consignee of the commodity weighed; (4) The name of the seller, agent, or consignor; (5) The accurate weight, measure, or count … (6) The identifying numerals or symbols … (7) The means by which the commodity was being transported … (8) The name of the city or town where such commodity was weighed; (9) The complete signature of the weighmaster or weigher."

### `certificate_numbering_required` — bool
- **what:** Whether each weight certificate must be numbered consecutively.
- **states:** CA, NV, WA
- **sample (CA):** "Each certificate shall be numbered consecutively."

### `certificate_is_prima_facie_evidence` — bool
- **what:** Whether a properly completed and signed weight certificate constitutes prima facie evidence of the accuracy of the measurements shown.
- **states:** NV, WA
- **sample (NV):** "A certificate of weights and measures, when properly filled out and signed, is prima facie evidence of the accuracy of the measurements shown."

### `correction_certificate_required_for_errors` — bool
- **what:** Whether a separate correction certificate must be issued to all parties when an error is discovered on a previously issued certificate.
- **states:** CA, CT
- **sample (CA):** "A certificate on which a weight, measure, or count error is discovered after issuance shall be corrected by issuing a correction certificate to all parties who were issued the original certificate."

### `impression_seal_authorized` — bool
- **what:** Whether certification may be made by means of an official impression seal placed on the weight ticket by the weighmaster or weigher.
- **states:** AZ, WA
- **sample (WA):** "Certification must be made by means of an impression seal, the impress of which shall be placed by the weighmaster or weigher making the weight determination upon the weights shown on the weight tickets."

## recordkeeping obligations

### `certificate_record_retention_period_years` — int
- **what:** The minimum number of years a weighmaster must retain copies of all weight certificates issued.
- **states:** CA, CT, NV, WA
- **sample (CA):** "All weighmasters shall keep and preserve, as records, for a period of four years, all copies of voided certificates, records, and worksheets required by this chapter and true copies of all weighmaster certificates issued."

### `records_open_to_inspection` — bool
- **what:** Whether retained weight certificate records must be available for inspection by state weights and measures officials at all reasonable times.
- **states:** AZ, CA, CT, NV, WA
- **sample (WA):** "These records shall be made available at all reasonable business hours for inspection by the director."

## license fees and scale-based structure

### `license_fee_per_scale_location` — bool
- **what:** Whether the weighmaster license fee is assessed on a per-scale or per-location basis rather than as a single flat fee.
- **states:** CA, WA
- **sample (WA):** "Such annual application shall be accompanied by a license fee of eighty dollars for each scale from which certified weights will be issued."

### `license_posted_at_scale_site_required` — bool
- **what:** Whether the weighmaster license must be physically posted at the licensed scale site and accessible to regulators during normal business hours.
- **states:** AZ, CA
- **sample (AZ):** "A public weighmaster or deputy weighmaster license shall be posted at the licensed scale site in a manner that provides the division access to the license during normal business hours."

## who does not need a license

### `exempted_person_categories` — list[str]
- **what:** Categories of persons who are explicitly exempt from or not required to obtain a public weighmaster license.
- **states:** AZ, CA, CT, NV, WA
- **sample (CA):** "The following persons are not weighmasters: (a) Retailers weighing, measuring, or counting commodities for sale by them in retail stores in the presence of, and directly to, consumers. … (b) … producers of agricultural commodities or livestock, who weigh commodities produced or purchased by them … (c) Common carriers issuing bills of lading …"

### `mandatory_weighing_commodity_types` — list[str]
- **what:** Specific commodity types or transaction contexts for which weighing by a licensed public weighmaster and issuance of a certificate is legally required.
- **states:** CA, WA
- **sample (CA):** "Farm products sold by bulk weight or delivered to a processing or conditioning establishment for processing, conditioning, or sale, shall be weighed by a weighmaster, and a weighmaster certificate of the weight shall be issued to the producer."

## interstate recognition

### `reciprocal_certificate_recognition` — bool
- **what:** Whether the state will recognize and accept weight certificates issued by licensed public weighmasters of other states on a reciprocal basis.
- **states:** NV, WA
- **sample (NV):** "The State Sealer of Measurement Standards may recognize and accept certificates of weights and measures issued by licensed public weighmasters of any other state if that other state recognizes and accepts certificates of weights and measures issued by licensed public weighmasters of this state."

## additional eligibility conditions

### `child_support_compliance_required_for_license` — bool
- **what:** Whether an applicant must certify compliance with child support court orders as a condition of obtaining or renewing a weighmaster license.
- **states:** NV, WA
- **sample (NV):** "A license as a public weighmaster may not be issued or renewed by the State Sealer of Measurement Standards … if the applicant … Indicates on the statement submitted pursuant to subsection 1 that he or she is subject to a court order for the support of a child and is not in compliance with the order."

### `criminal_history_pre_screening_available` — bool
- **what:** Whether a person with a criminal history may petition the licensing authority for a preliminary determination of whether that history will disqualify them before investing in education or fees.
- **states:** CA, NV
- **sample (NV):** "The State Sealer of Measurement Standards shall develop and implement a process by which a person with a criminal history may petition the State Sealer of Measurement Standards to review the criminal history of the person to determine if the person's criminal history will disqualify the person from obtaining a license as a public weighmaster."

### `state_residency_required` — bool
- **what:** Whether an applicant must be a resident of the state in order to obtain a public weighmaster license.
- **states:** CT, WA
- **sample (CT):** "Any person who is a resident of the state of Connecticut, is eighteen years of age or older, is of good moral character and has the ability to weigh accurately and make correct weight certificates may apply to the commissioner for a public weighmaster license."
