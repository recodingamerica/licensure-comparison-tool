# Discovered fields — veterinary

## extra credentials and tiered scope

### `veterinary_technician_certification_required` — bool
- **what:** Whether a separate certification (distinct from a veterinarian license) is required to practice as a veterinary technician.
- **states:** PA
- **sample (PA):** "Unless authorized to practice veterinary technology under this act, an individual may not practice veterinary technology nor use the title 'certified veterinary technician' or the abbreviation 'CVT.'"

### `veterinary_technician_ce_hours_per_period` — int
- **what:** Continuing education clock hours required for veterinary technician certificate holders per renewal period (distinct from the hours required for licensed veterinarians).
- **states:** PA
- **sample (PA):** "each holder of a certificate to practice veterinary technology under this act shall be required to complete sixteen clock hours of educational programs in the twenty-four months preceding each renewal date"

### `temporary_permit_available` — bool
- **what:** Whether the board may issue a temporary permit to practice veterinary medicine to a qualified applicant awaiting examination.
- **states:** PA
- **sample (PA):** "The board may issue, without examination, a temporary permit to practice veterinary medicine to an applicant for admission to the examination"

## supervision and delegation

### `technician_supervision_requirement` — str
- **what:** The level or type of veterinarian supervision required for a veterinary technician to practice.
- **states:** PA
- **sample (PA):** "who may practice veterinary technology under appropriate supervision of a licensed veterinarian as defined by board regulation"

### `veterinary_assistant_recognized` — bool
- **what:** Whether the statute recognizes a veterinary assistant as a distinct unlicensed/uncertified role that may perform tasks under veterinarian direction.
- **states:** PA
- **sample (PA):** "'Veterinary assistant' means an employe of a veterinarian who does not hold certification as a veterinary technician and whom the veterinarian deems competent to perform tasks involved in the care and treatment of animals as defined by board regulation."

## what they can treat and where on the body

### `veterinarian_client_patient_relationship_defined` — bool
- **what:** Whether the statute formally defines a veterinarian-client-patient relationship (VCPR) with specific conditions that must be met.
- **states:** PA
- **sample (PA):** "'Veterinarian-client-patient relationship' means a relationship satisfying all of the following conditions: (i) the veterinarian has assumed the responsibility for making veterinary medical judgments regarding the health of an animal..."

### `embryo_transfer_regulated` — bool
- **what:** Whether embryo removal, transfer, or cryopreservation in animals is explicitly included within (or exempted from) the practice of veterinary medicine.
- **states:** PA
- **sample (PA):** "removes any embryo from an animal for the purpose of transferring such embryo into another animal or cryopreserving such embryo"

### `electronic_identification_implantation_included` — bool
- **what:** Whether implanting electronic identification devices in animals is explicitly listed as part of the practice of veterinary medicine.
- **states:** PA
- **sample (PA):** "implants electronic identification, as determined by the board, upon any animal"

## practice setting and facility rules

### `practice_setting_inspection_required` — bool
- **what:** Whether veterinary establishments (including mobile clinics) are subject to mandatory periodic inspection by the board.
- **states:** PA
- **sample (PA):** "To inspect all animal hospitals or veterinary establishments, including mobile clinics, at least biennially to determine sanitary conditions, physical equipment and methods of operation."

### `mobile_clinic_recognized` — bool
- **what:** Whether mobile clinics are explicitly recognized as a regulated veterinary practice setting subject to board oversight.
- **states:** PA
- **sample (PA):** "To inspect all animal hospitals or veterinary establishments, including mobile clinics, at least biennially"

### `medical_records_retention_required` — bool
- **what:** Whether the statute requires veterinarians to maintain written or electronic medical records for animals treated and specifies access/transfer obligations.
- **states:** PA
- **sample (PA):** "A veterinarian subject to the provisions of this section shall, as required by regulation of the board, keep or cause to be kept a written record of all animals or groups of animals, as the case may be, receiving veterinary services"

## who is exempt from licensure

### `exempted_activities` — list[str]
- **what:** Categories of persons or activities explicitly exempted from the veterinary practice act.
- **states:** PA
- **sample (PA):** "Any person performing normal husbandry practices on bovine, porcine, caprine, ovine or equine animals or avis."

### `out_of_state_consultant_days_per_year` — int
- **what:** Maximum number of days per calendar year an out-of-state licensed veterinarian may practice as a consultant in the state without obtaining a local license.
- **states:** PA
- **sample (PA):** "do not practice veterinary medicine as consultants rendering services directly to the public without the direction and consultation of licensees of this State more than 16 days per calendar year"

## discipline and impairment

### `impaired_professional_program_available` — bool
- **what:** Whether the statute establishes a formal impaired-professional program allowing deferred discipline for licensees undergoing approved treatment.
- **states:** PA
- **sample (PA):** "The board may defer and ultimately dismiss any of the types of corrective action set forth in this act for an impaired professional so long as the professional is progressing satisfactorily in an approved treatment program"

### `mandatory_impairment_reporting_required` — bool
- **what:** Whether veterinary establishments, peers, or colleagues are legally required to report a licensee's active addictive disease, controlled substance diversion, or mental/physical incompetence to the board.
- **states:** PA
- **sample (PA):** "Any veterinary establishment, peer or colleague who has substantial evidence that a professional has an active addictive disease for which the professional is not receiving treatment, is diverting a controlled substance or is mentally or physically incompetent to carry out the duties of his or her license shall make, or cause to be made, a report to the board"
