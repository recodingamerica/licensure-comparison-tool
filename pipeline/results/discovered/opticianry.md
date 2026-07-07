# Discovered fields — opticianry

## license types and tiers

### `license_tier_structure` — list[str]
- **what:** The distinct license or registration tiers available within the state's opticianry licensing scheme (e.g., spectacle-only, contact lens, combined, apprentice, board-certified).
- **states:** AK, AR, CA, FL, KY
- **sample (AK):** "A license shall be issued for (1) the dispensing of contact lenses, or (2) the dispensing of other lenses, eyeglasses, spectacles, artificial eyes, and their appurtenances, or (3) both."

### `contact_lens_license_separate` — bool
- **what:** Whether contact lens dispensing requires a separate license, registration, or certification distinct from spectacle dispensing.
- **states:** AK, CA, FL, HI
- **sample (FL):** "A board-certified optician qualified and operating under rules established by the board may fill, fit, adapt, or dispense any soft contact lens prescription."

### `nonresident_remote_dispenser_registration` — bool
- **what:** Whether out-of-state entities that ship or mail ophthalmic lenses to in-state patients must obtain a separate registration.
- **states:** CA, FL
- **sample (CA):** "A person or entity located outside California shall not ship, mail, furnish, or deliver in any manner, ophthalmic lenses at retail to a patient at a California address unless the person is registered with the California State Board of Optometry."

## practice setting and facility rules

### `optical_establishment_permit_required` — bool
- **what:** Whether a separate permit or registration is required for the physical location (optical establishment) where opticianry services are offered, distinct from the individual practitioner license.
- **states:** AR, AZ, CA, CT, FL, KY
- **sample (FL):** "Any person desiring to operate an optical establishment shall apply to the department, upon forms prescribed by the department, for a permit."

### `licensed_optician_must_be_present_on_premises` — bool
- **what:** Whether a licensed optician must be physically present on the premises whenever opticianry services are provided to the public.
- **states:** AR, AZ, CA, CT, KY
- **sample (AR):** "All businesses providing retail ophthalmic dispensing services, as defined in § 17-89-102(4), to the public must have physically present a licensed or registered dispensing optician within the place of business at the time the services are provided."

### `max_establishments_per_licensee` — int
- **what:** Maximum number of optical establishment locations a single licensed optician may supervise simultaneously.
- **states:** AR, KY
- **sample (AR):** "No licensed or registered dispensing optician or other person in this state shall establish more than two (2) ophthalmic dispensing branch offices in addition to his or her principal office unless he or she shall have first secured a branch office permit."

### `optical_product_quality_standards` — list[str]
- **what:** Named quality or safety standards (e.g., ANSI Z80.1) that ophthalmic lenses and materials must meet.
- **states:** AR, CT
- **sample (AR):** "All ophthalmic materials, including eyeglasses, spectacles, lenses, or other optical devices or materials or parts thereof, sold in the State of Arkansas must conform to standards of quality as promulgated by the American National Standards Institute, commonly known as 'Z-80.1 standards'."

## prescription and dispensing rules

### `contact_lens_prescription_required_on_file` — bool
- **what:** Whether a written contact lens prescription must be on file before contact lenses may be dispensed.
- **states:** AK, AZ, CA, FL, GA, HI, KY, MA
- **sample (AZ):** "contact lenses shall never be dispensed without a written contact lense prescription being on file in any optical establishment, office of an optometrist or office of a physician or verbal confirmation of that written prescription."

### `prescription_duplication_without_rx_permitted` — bool
- **what:** Whether a licensed optician may duplicate lenses (reproduce existing lenses to the same power) without a new written prescription.
- **states:** AK, AZ, FL, GA, HI, KY, MA
- **sample (GA):** "A dispensing optician may duplicate lenses without prescription, provided that a dispensing optician shall not substitute contact lenses for spectacles, eyeglasses, or other optical devices except as otherwise authorized in this chapter."

### `prescription_file_retention_period_years` — int
- **what:** Number of years a filled prescription must be retained on file by the optical establishment.
- **states:** CA, FL
- **sample (FL):** "Any prescription written by a duly licensed allopathic or osteopathic physician or optometrist for any lenses, spectacles, eyeglasses, contact lenses, or other optical devices shall be kept on file for a period of 2 years with the optical establishment that fills such prescription."

### `contact_lens_followup_referral_required` — bool
- **what:** Whether the optician is required to instruct the contact lens wearer to return to the prescribing physician or optometrist for follow-up evaluation after fitting.
- **states:** AK, AZ, CA, GA
- **sample (AZ):** "The dispensing optician shall advise the intended wearer at the time that contact lenses are delivered to return to the prescribing physician or optometrist for evaluation and follow-up care."

### `contact_lens_fitting_supervision_requirement` — str
- **what:** The level of physician or optometrist oversight required when an optician fits contact lenses (e.g., written prescription only, personal supervision, or prohibited entirely).
- **states:** AK, AR, HI, KY
- **sample (AK):** "Contact lenses shall be fitted in conjunction with and under the supervision of a licensed physician or an optometrist and with a written contact-lens prescription."

## advertising and business conduct rules

### `advertising_disclaimer_required` — bool
- **what:** Whether advertisements by dispensing opticians must include a specific statutory disclaimer (e.g., that the firm is not licensed to perform eye examinations).
- **states:** AR, AZ
- **sample (AR):** "Any advertisement made by, for, or in behalf of any ophthalmic dispensing firm or any dispensing optician in this state... shall cause to have printed thereon, or stated in oral advertisements, the following disclaimer: 'This firm is not licensed to make eye examinations.'"

### `fee_splitting_with_prescribers_prohibited` — bool
- **what:** Whether the statute explicitly prohibits opticians from paying or receiving referral fees, rebates, or commissions to or from prescribing physicians or optometrists.
- **states:** AK, AZ, GA, HI, KY
- **sample (GA):** "It shall be unlawful for any dispensing optician, either directly or indirectly, to participate in any manner in the division, assignment, rebate, splitting, or refunding of service fees or costs of completed eyeglasses or parts thereof with a physician, optometrist, or other person or persons."

### `optician_employment_of_prescriber_prohibited` — bool
- **what:** Whether the statute prohibits a registered dispensing optician from directly employing an optometrist or physician for eye examinations or treatment.
- **states:** AR, CA
- **sample (CA):** "it is unlawful for a registered dispensing optician or a person who engages in the business of, or holds himself or herself out to be, a dispensing optician to do any of the following: to advertise the furnishing of, or to furnish, the services of an optometrist or a physician and surgeon, to directly employ an optometrist or physician and surgeon for the purpose of any examination or treatment of the eyes."

## supervision and delegation

### `apprentice_to_supervisor_ratio_limit` — int
- **what:** Maximum number of apprentices that one licensed optician may supervise at the same time.
- **states:** AK, AR, CA, KY
- **sample (AK):** "No more than two apprentices may be under the direct supervision of one licensed dispensing optician at the same time."

### `unlicensed_assistant_delegation_permitted` — bool
- **what:** Whether a licensed optician may delegate opticianry tasks to unlicensed support personnel under supervision.
- **states:** AK, AZ, CA, CT, FL, GA, HI, KY, … (+1)
- **sample (FL):** "a licensed optician may delegate to nonlicensed supportive personnel those duties, tasks, and functions which fall within the purview of s. 484.002(3). All such delegated acts shall be performed under the direct supervision of a licensed optician."

### `supervision_definition` — enum[direct personal physical presence, on-premises availability, regular supervision with inspection, full-time licensed optician at location]
- **what:** How the statute defines the required level of supervision over apprentices or unlicensed assistants.
- **states:** AK, AR, AZ, CA, FL, GA, HI, KY
- **sample (HI):** "'Direct personal supervision' means the licensed optician is present on the premises of the optical dispensing establishment and is available for consultation by the unlicensed person."

### `apprentice_registration_required` — bool
- **what:** Whether apprentices must formally register with the state board or licensing authority before beginning their apprenticeship.
- **states:** AK, AR, CT, FL, GA, KY, MA
- **sample (AK):** "An apprentice shall register with the department before beginning employment or service as an apprentice, shall be designated as an apprentice in the records of the department."

## what opticians cannot do

### `scope_excludes_eye_examination_and_prescribing` — bool
- **what:** Whether the statute explicitly prohibits opticians from examining eyes, determining refractive power, diagnosing, treating, or prescribing for eye conditions.
- **states:** AK, AR, AZ, FL, GA, HI, KY, MA
- **sample (FL):** "It is unlawful for any optician to engage in the diagnosis of the human eyes, attempt to determine the refractive powers of the human eyes, or, in any manner, attempt to prescribe for or treat diseases or ailments of human beings."

## what they can dispense and fit

### `artificial_eye_dispensing_authorized` — bool
- **what:** Whether the scope of practice explicitly includes dispensing or fitting artificial eyes (ocular prosthetics).
- **states:** AK, AZ, FL, GA, HI
- **sample (AZ):** "dispenses lenses, contact lenses, frames, artificial eyes, optical devices, appurtenances thereto or parts thereof to the intended wearer on written prescription."

### `plano_cosmetic_contact_lens_included_in_scope` — bool
- **what:** Whether non-corrective (plano) cosmetic or colored contact lenses are explicitly included within the optician's scope or subject to the same dispensing rules.
- **states:** CA, CT, HI
- **sample (CT):** "No optical glasses or kindred products or other instruments to aid vision that are produced or reproduced to personalized given formulas, or plano cosmetic contact lenses shall be sold at retail except under the direct supervision of a licensed optician."

### `exempted_merchandise_categories` — list[str]
- **what:** Categories of eyewear or optical products explicitly exempt from licensure requirements (e.g., plano sunglasses, ready-made reading glasses, toys, binoculars).
- **states:** AK, AR, AZ, CA, CT, FL, GA, HI, … (+1)
- **sample (AK):** "This chapter may not be construed to prohibit an unlicensed person from engaging in the sale of eyeglasses, spectacles, magnifying glasses, goggles, sunglasses, telescopes, binoculars, or any like articles that are completely preassembled and sold only as merchandise."
