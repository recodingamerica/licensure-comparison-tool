# Discovered fields — podiatry

## anatomy_or_procedure

### `anatomical_scope_upper_boundary` — enum[foot_only, foot_and_ankle, foot_ankle_and_leg_below_knee, foot_ankle_and_soft_tissue_to_tibial_tuberosity, foot_ankle_and_soft_tissue_to_myotendinous_junction_triceps_surae, foot_ankle_and_soft_tissue_to_distal_tibial_metaphyseal_flare, foot_ankle_and_soft_tissue_below_mid_calf, foot_ankle_and_tendons_inserting_into_foot]
- **what:** The upper anatomical boundary of the podiatrist's authorized scope of practice, which varies significantly across states.
- **states:** AZ, CT, DE, FL, GA, HI, IA, ID, … (+25)
- **sample (TN):** "the ailments of the human foot, ankle and soft tissue structures extending no higher than the distal tibial metaphyseal flair"

## scope_inclusion

### `amputation_authorized` — enum[toes_only, toes_and_parts_of_foot, transmetatarsal_and_below, chopart_joint_and_below, foot_entirety_excluded, forefoot_excluded, not_authorized]
- **what:** The level of amputation a podiatrist is authorized to perform, ranging from toes only to parts of the foot, with the entire foot typically excluded.
- **states:** CT, DE, FL, GA, HI, IA, ID, IL, … (+14)
- **sample (FL):** "The practice of podiatric medicine shall include the amputation of the toes or other parts of the foot but shall not include the amputation of the foot or leg in its entirety."

### `systemic_disease_local_manifestations_included` — bool
- **what:** Whether the state explicitly includes treatment of local manifestations of systemic diseases as they appear on the foot or ankle.
- **states:** CT, OK, SC, SD, UT
- **sample (CT):** "'Podiatric medicine' includes treatment of local manifestations of systemic diseases as they appear on the foot and ankle"

### `telehealth_authorized` — bool
- **what:** Whether the state explicitly authorizes podiatrists to provide services via telehealth or telemedicine.
- **states:** DE, ME
- **sample (ME):** "A person licensed under this chapter may provide telehealth services as long as the licensee acts within the scope of practice of the licensee's license"

### `wound_debridement_authorized` — bool
- **what:** Whether the state explicitly authorizes podiatrists to perform wound debridement beyond the foot and ankle.
- **states:** UT
- **sample (UT):** "wound debridement on the limbs and torso, by all appropriate and lawful means"

### `vaccination_authority` — bool
- **what:** Whether the state explicitly authorizes podiatrists to administer vaccinations.
- **states:** IL
- **sample (IL):** "vaccination of patients 18 years of age and older in accordance with Section 20.6 upon completion of appropriate training"

### `cosmetic_procedures_included` — bool
- **what:** Whether the state explicitly includes cosmetic procedures of the foot, ankle, or leg within the podiatric scope of practice.
- **states:** GA
- **sample (GA):** "the term 'cosmetic' means a surgical or medical procedure intended to enhance the physical appearance or function of the foot, ankle, or leg, including, but not limited to, skin problems such as blemishes, spider veins, and scar revisions"

### `preoperative_history_and_physical_authorized` — bool
- **what:** Whether the state explicitly authorizes podiatrists to perform preoperative history and physical examinations on their patients.
- **states:** ME, ND
- **sample (ME):** "'Practice of podiatric medicine' includes the performance of a history and physical on a podiatrist's preoperative patient and upon the patient's admission into a hospital or ambulatory surgical center."

### `assistant_surgeon_role_authorized` — bool
- **what:** Whether the state explicitly authorizes podiatrists to function as assistant surgeons in non-podiatric procedures.
- **states:** ND
- **sample (ND):** "podiatrists may function as assistant surgeons in nonpodiatric procedures"

## drug_or_anesthesia

### `anesthesia_authority` — enum[local_only, local_and_conscious_sedation, local_and_moderate_deep_sedation, general_permitted_with_physician_supervision, general_excluded]
- **what:** The types of anesthesia a podiatrist is authorized to administer, with local anesthesia universally permitted and general anesthesia typically excluded or restricted.
- **states:** CT, DE, HI, IA, ID, IL, IN, KS, … (+15)
- **sample (HI):** "A podiatrist may not administer any anesthetic other than local anesthetic."

### `opioid_prescribing_rules_required` — bool
- **what:** Whether the state has specific statutory requirements or mandates for the board to adopt rules governing opioid prescribing by podiatrists.
- **states:** FL, ME, SC, WA
- **sample (WA):** "By January 1, 2019, the board must adopt rules establishing requirements for prescribing opioid drugs."

### `electronic_prescribing_required` — bool
- **what:** Whether the state requires podiatrists to use electronic prescribing for medications, particularly controlled substances.
- **states:** DE, ME
- **sample (DE):** "no person licensed under this chapter shall issue any prescription unless such prescription is made by electronic prescription from the person issuing the prescription to a pharmacy"

## advanced_tier

### `ankle_surgery_authorized` — bool
- **what:** Whether the state authorizes podiatrists to perform surgical treatment of the ankle, often subject to additional qualifications.
- **states:** CT, DE, FL, GA, HI, ID, IL, KS, … (+13)
- **sample (KS):** "No podiatrist shall perform surgery on the ankle unless such person has completed a two-year post-doctoral surgical residency program prior to July 1, 2007, or a three-year post-doctoral surgical residency program on or after July 1, 2007, in reconstructive rearfoot/ankle surgery"

### `ankle_surgery_residency_requirement` — enum[24_month_surgical_residency, 36_month_surgical_residency, 2_year_pre_2007_or_3_year_post_2007, board_certification_or_qualification_required, hospital_credentialing_required, board_certification_by_ABFAS]
- **what:** The specific residency length or certification required for a podiatrist to perform ankle surgery.
- **states:** CT, HI, KS, MO, MT, NE, SC, TN, … (+1)
- **sample (UT):** "graduated on or after June 1, 2006, from a three-year residency program in podiatric medicine and surgery that was accredited, at the time of graduation, by the Council on Podiatric Medical Education; and is board certified in reconstructive rearfoot and ankle surgery by the American Board of Foot and Ankle Surgery"

### `board_certification_body` — list[str]
- **what:** The recognized certifying body or bodies for advanced podiatric surgery, particularly for ankle surgery privileges.
- **states:** CT, HI, KS, MO, MT, SC, TN, UT
- **sample (CT):** "board certified or board qualified by the American Board of Foot and Ankle Surgery"

### `ankle_surgery_board_certification_timeline` — str
- **what:** The time period within which a podiatrist who qualifies for ankle surgery must obtain board certification, where specified by statute.
- **states:** TN, UT
- **sample (TN):** "must obtain certification to perform reconstructive rearfoot/ankle surgery from the American Board of Podiatric Surgery within six (6) years of May 24, 2000, or within six (6) years of first becoming eligible for certification"

### `total_ankle_replacement_authorized` — bool
- **what:** Whether the state explicitly addresses or authorizes total ankle replacement surgery by podiatrists.
- **states:** CT, UT
- **sample (CT):** "a licensed podiatrist who has provided documentation to the Department of Public Health of meeting the requirements set forth in subdivision (1) or (2) of subsection (c) of section 20-54 may apply to a hospital in the state for privileges to perform total ankle replacement surgery"

### `ankle_surgery_standard_of_care_reference` — bool
- **what:** Whether the state statute explicitly requires podiatrists performing ankle surgery to meet the same standard of care as orthopedic surgeons.
- **states:** TN
- **sample (TN):** "A licensed podiatrist who performs ankle surgery must meet the same standard of care applicable to orthopedic surgeons who perform ankle surgery."

## facility

### `ankle_surgery_facility_requirement` — enum[licensed_hospital_only, hospital_or_ambulatory_surgical_center, accredited_hospital_or_ASC, JCAHO_accredited_facility, multispecialty_ambulatory_surgical_facility]
- **what:** The type of facility in which ankle surgery must be performed by a podiatrist.
- **states:** CT, DE, ID, KS, MD, MO, MT, NC, … (+6)
- **sample (MO):** "Surgical treatment of the ankle by a podiatrist shall be performed only in a licensed acute care hospital or a licensed ambulatory surgical clinic."

### `hospital_privileges_nondiscrimination` — bool
- **what:** Whether the state has a statutory provision prohibiting hospitals from discriminating against podiatrists in granting privileges based solely on their degree type.
- **states:** RI, SC
- **sample (SC):** "medical staff governing documents shall include and provide for the right to pursue and practice full clinical and surgical surgical privileges for holders of a Doctor of Podiatric Medicine (DPM) degree within the scope of his licensure"

### `office_based_surgery_accreditation_required` — bool
- **what:** Whether the state requires that office-based surgeries performed by podiatrists be conducted in an accredited or licensed facility.
- **states:** CT, DE, GA, ID, MD, NC, SC, TN
- **sample (DE):** "No person licensed under this chapter shall perform any office-based surgery, as defined in § 122(3)y. of Title 16, in a facility unless it is accredited or licensed in accordance with § 122(3)z. of Title 16."

## scope_exclusion

### `systemic_disease_treatment_excluded` — bool
- **what:** Whether the state explicitly excludes treatment of systemic diseases from the podiatric scope of practice, except as manifested in the foot.
- **states:** CT, HI, IA, IL, MA, MO, MS, NE, … (+1)
- **sample (MO):** "The use of such drugs and medicines in the treatment of ailments of the human foot shall not include the treatment of any systemic diseases."

### `tibial_pilon_fracture_excluded` — bool
- **what:** Whether the state explicitly excludes treatment of tibial pilon fractures from the podiatric scope of practice.
- **states:** CT, TN
- **sample (CT):** "such podiatrist shall restrict treatment of displaced ankle fractures to the initial diagnosis and the initial attempt at closed reduction at the time of presentation and shall not treat tibial pilon fractures"

### `corrective_footwear_exemption` — bool
- **what:** Whether the state explicitly exempts the fitting, recommending, or sale of corrective shoes, arch supports, or similar appliances by retail dealers from the podiatry licensing requirement.
- **states:** AZ, CT, DE, FL, GA, HI, IA, ID, … (+24)
- **sample (MT):** "Nothing in this chapter shall be construed as prohibiting the fitting, recommending, advertising, adjusting, or sale of corrective shoes, arch supports, or similar mechanical appliances, or foot remedies by retail dealers or manufacturers."

### `clubfoot_surgery_restriction` — bool
- **what:** Whether the state explicitly restricts or excludes surgical correction of clubfoot from the podiatric scope of practice.
- **states:** MO, NC
- **sample (NC):** "Excluded from the definition of podiatry is the amputation of the entire foot, the administration of an anesthetic other than local, and the surgical correction of clubfoot of an infant two years of age or less."

## supervision_delegation

### `podiatric_assistant_authorized` — bool
- **what:** Whether the state explicitly authorizes podiatric medical assistants or podiatric assistants to assist under podiatrist supervision.
- **states:** AZ, FL, GA, ME, NE, NM, UT
- **sample (AZ):** "A podiatric medical assistant may assist a podiatrist pursuant to rules adopted by the board."

### `podiatric_assistant_supervision_level` — enum[direct_supervision_on_premises, indirect_supervision, general_supervision]
- **what:** The level of supervision required when a podiatrist delegates tasks to a podiatric assistant or medical assistant.
- **states:** AZ, ME, NE, UT
- **sample (UT):** "a medical assistant working under the indirect supervision of a licensed podiatric physician"

### `xray_technician_certification_required` — bool
- **what:** Whether the state requires certification or training for unlicensed personnel operating X-ray equipment in a podiatrist's office.
- **states:** FL, NE, TN, WY
- **sample (TN):** "no person shall perform X-ray procedures in a podiatrist office who does not meet these standards and who has not received a certificate of proficiency from the board"

### `physician_assistant_collaboration_authorized` — bool
- **what:** Whether the state explicitly authorizes podiatrists to collaborate with or supervise physician assistants.
- **states:** IL, NE, TN
- **sample (TN):** "A licensed podiatrist may collaborate with a physician assistant or an orthopedic physician assistant licensed pursuant to chapter 19 of this title."

### `advanced_practice_nurse_collaboration_authorized` — bool
- **what:** Whether the state explicitly authorizes podiatrists to collaborate with advanced practice registered nurses.
- **states:** IL
- **sample (IL):** "A podiatric physician in active clinical practice may collaborate with an advanced practice registered nurse in accordance with the requirements of the Nurse Practice Act."

## other

### `professional_liability_insurance_required` — bool
- **what:** Whether the state requires podiatrists to maintain professional liability (malpractice) insurance as a condition of licensure or renewal.
- **states:** CT, IN, KS, NJ
- **sample (CT):** "Each person licensed to practice podiatric medicine under the provisions of section 20-54 or 20-57 who provides direct patient care services shall maintain professional liability insurance or other indemnity against liability for professional malpractice."

### `controlled_substances_prescribing_ce_required` — bool
- **what:** Whether the state requires continuing education specifically related to controlled substances prescribing as part of license renewal.
- **states:** FL, SC, WY
- **sample (FL):** "a minimum of 2 hours of continuing education related to the safe and effective prescribing of controlled substances"

### `impaired_practitioner_program` — bool
- **what:** Whether the state has a statutory provision for a podiatrist health or rehabilitation program for impaired practitioners.
- **states:** FL, MD, ME, MS, RI
- **sample (ME):** "The board may establish protocols for the operation of a professional review committee... The board has the power to contract with other agencies, individuals, firms or associations for the conduct and operation of a podiatrist health program"

### `minor_patient_chaperone_requirement` — bool
- **what:** Whether the state has a statutory requirement for a chaperone or third party to be present when a podiatrist treats a minor patient.
- **states:** DE
- **sample (DE):** "A parent, guardian or other caretaker, or an adult staff member, shall be present when a person licensed under this chapter provides outpatient treatment to a minor patient who is disrobed or partially disrobed"

### `nondiscrimination_in_public_programs` — bool
- **what:** Whether the state has a statutory provision ensuring recipients of public aid programs may choose podiatric care.
- **states:** HI, SC
- **sample (HI):** "No department, office, or agency of the state or county government... shall deny to the recipient or beneficiary of podiatric aid or services the freedom to choose podiatric care or services which are within the scope of activities of a podiatrist"

### `noncompete_clause_restriction` — bool
- **what:** Whether the state has a statutory provision rendering noncompete clauses in podiatrist employment contracts unenforceable.
- **states:** NH
- **sample (NH):** "Any contract or agreement which creates or established the terms of a partnership, employment, or any other form of professional relationship with a podiatrist licensed by the board to practice in this state, which includes any restriction to the right of such podiatrist to also practice podiatry in any geographic area for any period of time after the termination of such partnership, employment, or professional relationship shall be void and unenforceable"
