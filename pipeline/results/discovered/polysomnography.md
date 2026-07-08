# Discovered fields — polysomnography

## national certification and credentialing

### `credential_body` — list[str]
- **what:** The national organization(s) whose credential or examination is required or accepted for licensure.
- **states:** CA, DE, IA, ID, MD, NC, ND, NM, … (+1)
- **sample (NM):** "passed the national certifying examination given by the board of registered polysomnographic technologists"

### `credential_required_for_renewal` — bool
- **what:** Whether maintaining an active national credential (e.g., RPSGT) is required as a condition of license renewal.
- **states:** DE, MD, NC, NM, OR
- **sample (DE):** "To be eligible for renewal of a license to engage in the practice of polysomnography, a licensed polysomnographer must continue to be credentialed by BRPT, or other organization approved by the Council."

## approved education pathways

### `approved_education_pathways` — list[str]
- **what:** The specific accredited educational program types or tracks that satisfy the education requirement for licensure.
- **states:** CA, DE, IA, MD, NM, OR
- **sample (NM):** "graduation from a polysomnographic educational program that is accredited by the commission on accreditation of allied health education programs; graduation from a respiratory care educational program ... and completion of the curriculum for a polysomnography certificate; graduation from an electroneurodiagnostic technologist educational program with a polysomnographic technology track"

### `aasm_pathway_available` — bool
- **what:** Whether an AASM-accredited sleep technologist educational program (A-STEP) is recognized as an approved pathway to licensure.
- **states:** DE, IA, NM, OR
- **sample (DE):** "An Accredited Sleep Technologist Educational Program (A-STEP) that is accredited by the American Academy of Sleep Medicine"

### `grandfathering_provision` — bool
- **what:** Whether persons already practicing polysomnography before the law's effective date may obtain licensure without meeting the standard education requirement.
- **states:** CA, DE, IA, NM, OR
- **sample (NM):** "A person who is engaged in the practice of polysomnography on July 1, 2008 shall be eligible for a license under the Polysomnography Practice Act without meeting the educational requirement ... provided that the person meets the [examination/credential] requirements."

## supervision and physician oversight

### `supervision_level_definitions` — list[str]
- **what:** The distinct levels of supervision defined in statute (e.g., general supervision, direct supervision) and what each requires.
- **states:** CA, DE, GA, IA, ID, MD, NC, NM, … (+1)
- **sample (NM):** ""General supervision" means that the polysomnographic procedure is provided under a physician's direction and control, but the physician's presence is not required during the performance of the procedure. "Direct supervision" means that the polysomnographic technologist providing supervision shall be present in the area where the polysomnographic procedure is being performed and immediately available."

### `supervising_physician_specialty_required` — bool
- **what:** Whether the supervising or medical director physician must be certified or have special expertise in sleep medicine.
- **states:** DE, MD, NM, OR
- **sample (NM):** "one licensed physician who is certified in sleep medicine by a national certifying body recognized by the American academy of sleep medicine"

### `qualified_prescriber_types` — list[str]
- **what:** The types of licensed providers (beyond physicians) whose orders or prescriptions authorize polysomnography services.
- **states:** IA, NM, OR
- **sample (IA):** ""Qualified health care professional prescriber" means a physician assistant operating under the prescribing authority granted in section 147.107 or an advanced registered nurse practitioner operating under the prescribing authority granted in section 147.107."

## where and how services may be provided

### `practice_setting_restrictions` — list[str]
- **what:** The specific settings in which polysomnography may lawfully be performed (e.g., accredited sleep lab, hospital, patient's home).
- **states:** IA, MD, NC, NM, OR
- **sample (IA):** "The practice of polysomnography shall take place only in a hospital, a stand-alone sleep laboratory or sleep center, or in a patient's home pursuant to rules adopted by the board; provided, however, that the scoring of data and the education of patients may take place in another setting."

### `scoring_and_education_setting_exception` — bool
- **what:** Whether data scoring and patient education may be performed in settings other than the approved clinical facility.
- **states:** IA, NC, NM, OR
- **sample (NM):** "the scoring of data and the education of patients may take place in settings other than in a hospital, sleep laboratory, sleep center or patient's home"

### `oral_appliance_dentist_requirement` — bool
- **what:** Whether a licensed dentist must make, direct, or evaluate oral appliances used during polysomnography.
- **states:** MD, NM
- **sample (NM):** "A licensed dentist shall make or direct the making and use of any oral appliance used in the practice of polysomnography and shall evaluate the structures of a patient's oral and maxillofacial region for purposes of fitting the appliance."

## what technologists are authorized to do

### `oxygen_flow_limit_liters_per_minute` — int
- **what:** The maximum supplemental oxygen flow rate (in liters per minute) that a polysomnographic technologist is authorized to administer.
- **states:** CA, DE, IA, MD, NC, NM, OR
- **sample (DE):** "Supplemental low flow oxygen therapy (less than or equal to 6 liters per minute) during a polysomnogram utilizing a nasal cannula or approved airway pressure devices"

### `authorized_pap_modalities` — list[str]
- **what:** The positive airway pressure device types that polysomnographic technologists are explicitly authorized to titrate or use.
- **states:** CA, DE, GA, IA, MD, NC, NM, OR
- **sample (CA):** "continuous positive airway pressure (CPAP) and bilevel modalities, adaptive servo-ventilation, and maintenance of nasal and oral airways that do not extend into the trachea"

### `airway_device_tracheal_restriction` — bool
- **what:** Whether statute explicitly prohibits use of masks or oral appliances that extend into the trachea or attach to an artificial airway.
- **states:** CA, DE, GA, IA, MD, NC, NM, OR
- **sample (NC):** "provided, the mask or oral appliance does not attach to an artificial airway or extend into the trachea"

### `patient_population_restriction` — bool
- **what:** Whether statute explicitly limits polysomnographic technologists to treating or testing only patients with sleep or wake disorders.
- **states:** CA, GA, NC
- **sample (GA):** "Nothing in this Code section shall be construed to ... authorize a polysomnographic technologist to treat, manage, control, educate, or care for patients other than those with sleep or wake disorders or to provide diagnostic testing for patients other than those with suspected sleep or wake disorders."

### `home_cpap_management_authorized` — bool
- **what:** Whether statute explicitly authorizes polysomnographic technologists to initiate, monitor, or manage CPAP/BiPAP devices for home use.
- **states:** NM, OR
- **sample (NM):** "initiating and monitoring treatment, under the orders of a licensed provider, for sleep-related breathing disorders by providing continuous positive airway pressure and bi-level positive airway pressure devices and accessories ... to a patient for home use, together with educating the patient about the treatment and managing the treatment"

## credential tiers and trainee status

### `tiered_credential_levels` — list[str]
- **what:** The distinct credential or permit tiers recognized in statute below full licensure (e.g., technician, trainee, student).
- **states:** CA, DE, IA, NM, OR
- **sample (IA):** ""Polysomnographic technician" means a person who has graduated from a program approved by the board, but has not yet received an accepted national credential ... "Polysomnographic student" means a person who is enrolled in a program approved by the board"

### `technician_temporary_permit_duration_months` — int
- **what:** The maximum number of months a polysomnographic technician or equivalent may practice under a temporary permit while awaiting credentialing examination results.
- **states:** IA, NM
- **sample (IA):** "a polysomnographic technician ... who may provide sleep-related services under the direct supervision of a licensed respiratory care and polysomnography practitioner or a licensed polysomnographic technologist for a period of up to thirty days following graduation while awaiting credentialing examination scheduling and results"

## governance and advisory structure

### `advisory_committee_required` — bool
- **what:** Whether statute requires a dedicated polysomnography advisory committee to advise the licensing board.
- **states:** DE, MD, NM
- **sample (NM):** "The "polysomnography practice advisory committee" is created to advise the board on all matters related to the Polysomnography Practice Act."

### `advisory_committee_composition` — str
- **what:** The required membership composition of the polysomnography advisory committee, including number and type of members.
- **states:** DE, MD, NM
- **sample (NM):** "The committee shall have five members ... two members who are credentialed by the board of registered polysomnographic technologists; one licensed physician who is certified in sleep medicine by a national certifying body recognized by the American academy of sleep medicine; one person whose background is at the discretion of the board; and one member of the public who is not economically or professionally associated with the health care field."

### `listing_vs_licensure_model` — enum[full licensure, listing/registration only]
- **what:** Whether the state requires a full license issued by a board or merely a listing/registration with a state agency based on national credential.
- **states:** CA, DE, GA, IA, ID, MD, NC, ND, … (+2)
- **sample (NC):** "it shall be unlawful for a person to do any of the following unless the person is listed with the Medical Board as provided in this Article: Practice polysomnography."

### `respiratory_care_board_jurisdiction` — bool
- **what:** Whether polysomnography is regulated under the same board or statute that governs respiratory care practitioners.
- **states:** IA, ID, ND, OR
- **sample (ND):** "The board shall license as a registered polysomnographic technologist any applicant whom the board determines to be qualified to perform the duties of a registered polysomnographic technologist."

## exemptions and scope boundaries

### `respiratory_care_practitioner_exemption` — bool
- **what:** Whether licensed respiratory care practitioners are explicitly exempt from polysomnography licensure requirements.
- **states:** CA, DE, GA, MD, OR
- **sample (DE):** "The provisions of this subchapter shall not apply to licensed respiratory care practitioners."

### `eeg_diagnostic_exemption` — bool
- **what:** Whether diagnostic electroencephalograms conducted per American Clinical Neurophysiology Society guidelines are explicitly exempt from polysomnography licensure.
- **states:** DE, NM
- **sample (DE):** "The provision of diagnostic electroencephalograms conducted in accordance with the guidelines of the American Clinical Neurophysiology Society."

### `research_exemption` — bool
- **what:** Whether research investigations that monitor physiological parameters during sleep are exempt from polysomnography licensure requirements.
- **states:** NC, ND
- **sample (NC):** "Research investigation that monitors physiological parameters during sleep or wakefulness, provided that the research investigation has been approved and deemed acceptable by an institutional review board"
