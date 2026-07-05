# Discovered fields — optician (dispensing optician)

## license types and tiers

### `license_tier_structure` — list[str]
- **what:** The distinct credential tiers or categories of license available to opticians in a state (e.g., spectacle-only, contact lens, combined, registered vs. licensed).
- **states:** AK, AR, CA, HI
- **sample (AK):** "A license shall be issued for (1) the dispensing of contact lenses, or (2) the dispensing of other lenses, eyeglasses, spectacles, artificial eyes, and their appurtenances, or (3) both."

### `contact_lens_scope_included` — bool
- **what:** Whether the optician license authorizes fitting or dispensing contact lenses (as opposed to spectacles only).
- **states:** AK, AR, CA, GA, HI, KY, NC
- **sample (AR):** "The prescribing, adapting, fitting, duplicating, dispensing, modifying, selling, or supplying of contact lenses for or to the human eye is specifically excluded."

### `artificial_eye_scope_included` — bool
- **what:** Whether the optician license authorizes dispensing or fitting artificial eyes (ocular prosthetics).
- **states:** AK, HI
- **sample (AK):** "A license shall be issued for (1) the dispensing of contact lenses, or (2) the dispensing of other lenses, eyeglasses, spectacles, artificial eyes, and their appurtenances."

### `duplicate_without_prescription_allowed` — bool
- **what:** Whether a licensed optician may duplicate, replace, or reproduce lenses without a new written prescription.
- **states:** AK, GA, HI, KY, MA, NC
- **sample (NC):** "Duplications, replacements, reproductions or repetitions may be done without prescription, in which event any such act shall be construed to be ophthalmic dispensing, the same as if performed on the basis of a written prescription."

## prescription and dispensing rules

### `written_prescription_required` — bool
- **what:** Whether a written prescription from a licensed physician or optometrist is required before dispensing ophthalmic lenses or devices.
- **states:** AK, AR, CA, GA, HI, KY, MA, NC
- **sample (AR):** "It shall be unlawful for any dispensing optician or person engaged in the business of manufacturing, selling, or dispensing regular or safety ophthalmic materials to fill or duplicate an ophthalmic prescription without having a written prescription signed by the licensed optometrist or licensed physician skilled in disease of the eye."

### `prescription_expiration_enforced` — bool
- **what:** Whether the statute explicitly prohibits filling a prescription after its stated expiration date.
- **states:** CA, NC
- **sample (NC):** "No person, firm or corporation licensed under this Article shall fill a prescription beyond the expiration date stated on the face thereof."

### `contact_lens_followup_required` — bool
- **what:** Whether the optician is required to instruct contact lens recipients to return to the prescribing practitioner for evaluation after fitting.
- **states:** CA, GA, NC
- **sample (GA):** "Dispensing opticians who dispense contact lenses shall instruct the wearer at the time the lenses are delivered to return to the prescribing and responsible optometrist or physician skilled in diseases of the eye for evaluation, approval, and follow-up care."

### `contact_lens_supervision_required` — bool
- **what:** Whether fitting or dispensing contact lenses must be done under the supervision of or in conjunction with a licensed physician or optometrist.
- **states:** AK, HI, KY
- **sample (AK):** "Contact lenses shall be fitted in conjunction with and under the supervision of a licensed physician or an optometrist and with a written contact-lens prescription."

### `ophthalmic_materials_quality_standard` — list[str]
- **what:** Named quality or safety standards (e.g., ANSI Z80.1) that ophthalmic lenses and materials must meet.
- **states:** AR, CT
- **sample (AR):** "All ophthalmic materials, including eyeglasses, spectacles, lenses, or other optical devices or materials or parts thereof, sold in the State of Arkansas must conform to standards of quality as promulgated by the American National Standards Institute, commonly known as 'Z-80.1 standards'."

### `impact_resistant_lens_required` — bool
- **what:** Whether the statute requires that eyeglasses and sunglasses be fitted with impact-resistant lenses meeting specified standards.
- **states:** CT, NC
- **sample (CT):** "No person shall sell, distribute or deliver any eyeglasses or sunglasses unless they are fitted with impact resistant lenses that fully meet the definitions, specifications, test procedures and tolerances for impact resistance."

## supervision and delegation

### `apprentice_to_supervisor_ratio_limit` — int
- **what:** Maximum number of apprentices that one licensed optician may supervise simultaneously.
- **states:** AK, AR, CA, KY
- **sample (AK):** "No more than two apprentices may be under the direct supervision of one licensed dispensing optician at the same time."

### `unlicensed_assistant_tasks_permitted` — bool
- **what:** Whether unlicensed assistants (non-apprentices) may perform optician tasks under supervision of a licensed optician.
- **states:** AK, CA, HI, NC
- **sample (AK):** "A person who is not a licensed dispensing optician or a registered apprentice under AS 08.71.160 may perform dispensing optician tasks that are delegated by and performed under the regular supervision of a licensed physician, optometrist, or dispensing optician."

### `supervisor_physical_presence_required` — bool
- **what:** Whether the supervising licensed optician must be physically present on the premises when an unlicensed or apprentice person performs optician tasks.
- **states:** CA, CT, HI, NC
- **sample (CA):** "A supervising registered spectacle lens dispenser shall be physically present on the registered premises when an unregistered individual fits and adjusts spectacle lenses."

## practice setting and facility rules

### `licensed_optician_on_premises_required` — bool
- **what:** Whether a licensed optician must be present on the premises of an optical establishment during all hours that dispensing services are offered.
- **states:** AR, CA, CT, NC
- **sample (AR):** "All businesses providing retail ophthalmic dispensing services, as defined in § 17-89-102(4), to the public must have physically present a licensed or registered dispensing optician within the place of business at the time the services are provided."

### `optical_establishment_permit_required` — bool
- **what:** Whether a separate permit or registration is required for each optical establishment or place of business (distinct from the individual optician's license).
- **states:** AR, CA, CT, NC
- **sample (AR):** "It shall be unlawful for any person or legal entity to conduct an office or place of business in this state where ophthalmic dispensing services are offered or performed unless that person or entity shall have first secured an office permit from the Arkansas Board of Dispensing Opticians."

### `branch_office_limit_or_permit` — bool
- **what:** Whether the statute limits the number of branch offices an optician may operate or requires a special permit for additional locations.
- **states:** AR, CA
- **sample (AR):** "No licensed or registered dispensing optician or other person in this state shall establish more than two (2) ophthalmic dispensing branch offices in addition to his or her principal office unless he or she shall have first secured a branch office permit from the Arkansas Board of Dispensing Opticians."

### `colocation_with_prescriber_restrictions` — bool
- **what:** Whether the statute restricts or regulates an optician's business being located adjacent to or co-located with a prescribing physician or optometrist.
- **states:** AR, CA
- **sample (AR):** "Engaging in conduct, including, but not limited to, establishing an ophthalmic dispensing business immediately adjacent to the office of a licensed optometrist or physician skilled in diseases of the eye in what is commonly known as a 'side-by-side' operation."

### `physician_ownership_interest_prohibited` — bool
- **what:** Whether a prescribing physician or optometrist is prohibited from having a proprietary or ownership interest in a registered dispensing optician business.
- **states:** AR, CA
- **sample (CA):** "The board shall deny any application for registration under this chapter if any person licensed as a physician and surgeon, for whom the applicant proposes to fill any prescription, has any proprietary interest in or with the applicant."

### `nonresident_remote_dispenser_registration` — bool
- **what:** Whether out-of-state entities that ship or mail ophthalmic lenses to in-state patients must register with the state board.
- **states:** CA, NC
- **sample (CA):** "A person or entity located outside California shall not ship, mail, furnish, or deliver in any manner, ophthalmic lenses at retail to a patient at a California address unless the person is registered with the California State Board of Optometry."

## advertising and consumer protection

### `advertising_disclaimer_required` — bool
- **what:** Whether opticians are required to include a specific disclaimer in advertisements stating they are not licensed to perform eye examinations.
- **states:** AR, GA, NC
- **sample (AR):** "Any advertisement made by, for, or in behalf of any ophthalmic dispensing firm or any dispensing optician in this state shall cause to have printed thereon, or stated in oral advertisements, the following disclaimer: 'This firm is not licensed to make eye examinations.'"

### `advertising_eye_exam_claim_prohibited` — bool
- **what:** Whether the statute explicitly prohibits opticians from advertising in a way that implies they provide eye examinations or full eye care services.
- **states:** AR, GA, HI, NC
- **sample (NC):** "Advertising in any manner that conveys or intends to convey the impression that eyes are examined by persons licensed under this Article or optical places of business registered under this Article."

### `fee_splitting_with_prescriber_prohibited` — bool
- **what:** Whether the statute explicitly prohibits opticians from splitting fees, paying rebates, or giving kickbacks to referring physicians or optometrists.
- **states:** AK, GA, HI, NC
- **sample (GA):** "It shall be unlawful for any dispensing optician, either directly or indirectly, to participate in any manner in the division, assignment, rebate, splitting, or refunding of service fees or costs of completed eyeglasses or parts thereof with a physician, optometrist, or other person or persons."

## training pathway requirements

### `apprenticeship_minimum_hours` — int
- **what:** Minimum number of hours of apprenticeship or supervised practical training required for licensure eligibility.
- **states:** AK, GA, NC
- **sample (GA):** "Has had practical training and experience of a grade and character satisfactory to the board for not less than two years under the supervision of a licensed dispensing optician, a licensed physician, or a licensed optometrist... shall include, at a minimum, 3,000 hours of experience engaged in apprenticeship functions."

### `apprenticeship_curriculum_subjects` — list[str]
- **what:** Specific subject areas that must be covered during an apprenticeship or training program for opticians.
- **states:** AR, GA, NC
- **sample (GA):** "Shall include instruction in ophthalmic optics, optical laboratory materials and techniques, eye anatomy and physiology, related laws and regulations, ophthalmic dispensing theory and application, and basic contact lens theory."

### `school_program_substitution_for_apprenticeship` — bool
- **what:** Whether graduation from an accredited opticianry school or college program may substitute for the apprenticeship or work-experience requirement.
- **states:** AK, AR, CA, CT, GA, HI, KY, MA, … (+1)
- **sample (AK):** "Graduation from an associate degree program in a recognized school or college of opticianry may be substituted for the experience required by (a)(2) and (4) of this section."

### `apprentice_registration_required` — bool
- **what:** Whether apprentices must formally register with the state board before their training period begins and counts toward licensure.
- **states:** AK, AR, CT, GA, KY, MA, NC
- **sample (AK):** "An apprentice shall register with the department before beginning employment or service as an apprentice, shall be designated as an apprentice in the records of the department."

## what opticians cannot do

### `scope_excludes_eye_examination_and_prescribing` — bool
- **what:** Whether the statute explicitly prohibits opticians from examining eyes, diagnosing conditions, or prescribing remedies.
- **states:** AK, AR, GA, HI, KY, NC
- **sample (KY):** "Nothing in this chapter shall be construed to authorize or permit any ophthalmic dispenser to hold himself out as being able to, or to either offer, undertake or attempt, by any means or method, to examine or exercise eyes, to fit contact lenses, or to diagnose, treat, correct, relieve, operate or prescribe for any human ailment."

### `unlicensed_mechanical_work_exemption` — bool
- **what:** Whether the statute explicitly exempts unlicensed persons performing purely mechanical work on inert optical materials in a lab or shop from licensure requirements.
- **states:** AK, GA, KY, NC
- **sample (GA):** "Nothing in this chapter shall be construed to prohibit an unlicensed person from performing merely mechanical work upon inert materials in an optical office or laboratory."

### `ready_made_nonprescription_eyewear_exemption` — bool
- **what:** Whether the statute exempts the sale of completely preassembled, non-prescription eyeglasses or sunglasses as merchandise from optician licensure requirements.
- **states:** AK, AR, CA, GA, HI, KY, NC
- **sample (KY):** "Persons, firms, and corporations that sell completely assembled eyeglasses or spectacles without advice or aid as to their selection, as merchandise, from permanently located or established places of business shall not be subject to this chapter."
