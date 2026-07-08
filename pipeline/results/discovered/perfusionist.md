# Discovered fields — perfusionist

## license tiers and temporary credentials

### `provisional_license_available` — bool
- **what:** Whether the state offers a provisional or temporary license for graduates who have not yet passed the certification examination.
- **states:** AR, CT, GA, IL, LA, MD, MO, NC, … (+1)
- **sample (AR):** "A license as a provisional licensed clinical perfusionist may be issued by the board to a person who has successfully completed an approved perfusion education program and filed an application, paid the application fee, and submitted evidence satisfactory to the Department of Health of the successful completion of the education requirements set forth in this chapter."

### `provisional_license_duration_months` — int
- **what:** Maximum duration in months of the provisional or temporary license before it expires or must be converted to a full license.
- **states:** AR, GA, IL, LA, MD, NC, NV
- **sample (LA):** "A provisional license is valid for two years from the date it is issued and may be extended subject to rule by the board."

### `graduate_perfusionist_title` — str
- **what:** The specific title or designation used for a person who has completed training but not yet passed the certification examination.
- **states:** CA, IL
- **sample (CA):** "After completion of an approved perfusion training program, as defined in Section 2592, and until notification of passage of the entire examination of the American Board of Cardiovascular Perfusion, or its successor agency, that person shall identify himself or herself only as a 'graduate perfusionist.'"

### `graduate_perfusionist_title_validity_years` — int
- **what:** Maximum number of years the graduate or new-graduate perfusionist title or temporary status is valid after completing an approved training program.
- **states:** CA, IL
- **sample (CA):** "The use of the title 'graduate perfusionist' is valid for no more than three years from the date of completion of an approved perfusion training program."

### `inactive_license_status_available` — bool
- **what:** Whether the state allows a licensed perfusionist to place their license on inactive status, suspending renewal fees while not practicing.
- **states:** IL, LA, NC
- **sample (LA):** "Any individual licensed by this Part who is no longer practicing as a perfusionist in this state may, by submitting a written request to the board, be granted inactive status."

### `new_graduate_supervised_practice_period_months` — int
- **what:** Number of months after graduation during which a new graduate may perform perfusion services under direct supervision without a full license.
- **states:** IL
- **sample (IL):** "A new graduate from performing perfusion services for a period of 14 months after the date of his or her graduation from a perfusion education program that is accredited by the Commission on Accreditation of Allied Health Education Programs."

## supervision and oversight requirements

### `provisional_license_supervisor_physical_presence_required` — bool
- **what:** Whether the supervising licensed perfusionist must be physically present at all times when the provisional licensee is performing perfusion.
- **states:** AR, GA, LA, NC, NV
- **sample (AR):** "Rules governing the supervision and direction of the provisionally licensed perfusionist shall not require the immediate physical presence of the supervising licensed perfusionist."

### `physician_supervision_required` — bool
- **what:** Whether a licensed perfusionist must practice under the order and supervision of a licensed physician.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (NC):** "All persons licensed under this section shall practice perfusion under the supervision of a physician licensed under Article 1 of Chapter 90 of the General Statutes."

### `student_supervision_model` — enum[direct, immediate availability, on duty and immediately available]
- **what:** The level of supervision required when a student enrolled in an accredited perfusion program performs perfusion services.
- **states:** AR, CA, CT, GA, IL, LA, NC, NV
- **sample (AR):** "Performed under the direct supervision of a licensed perfusionist who is assigned to supervise the student and who is on duty and immediately available in the assigned patient care area."

### `coordination_with_registered_nurse_required` — bool
- **what:** Whether the statute explicitly requires the perfusionist to coordinate with a registered professional nurse in addition to physician supervision.
- **states:** IL
- **sample (IL):** "A perfusionist is responsible for the selection of appropriate equipment and techniques necessary for support, treatment, measurement, or supplementation of the cardiopulmonary and circulatory system of a patient, including the safe monitoring, analysis, and treatment of physiologic conditions under an order and under the supervision of a physician licensed to practice medicine in all its branches and in coordination with a registered professional nurse."

## certification and examination requirements

### `abcp_certification_required_for_licensure` — bool
- **what:** Whether holding a current certificate from the American Board of Cardiovascular Perfusion (ABCP) is required or accepted as a basis for licensure.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (NC):** "Is a certified clinical perfusionist."

### `abcp_certification_waives_exam` — bool
- **what:** Whether holding a current ABCP certificate allows an applicant to bypass the state licensing examination.
- **states:** AR, CA, GA, IL, LA, MO, NC, NV
- **sample (GA):** "The board may waive the examination and educational requirements for an applicant who at the time of application... holds a current certificate as a certified clinical perfusionist issued by the American Board of Cardiovascular Perfusion (ABCP) or its successor."

### `abcp_certification_required_to_maintain_licensure` — bool
- **what:** Whether ongoing ABCP certification must be maintained as a condition of keeping an active license.
- **states:** CA, NC
- **sample (NC):** "After December 31, 2007, all licensed perfusionists who are licensed under this Article shall maintain certification as defined in G.S. 90-682(1) in order to maintain licensure."

### `minimum_post_graduation_cases_required` — int
- **what:** Minimum number of perfusion cases that must be completed after graduating from an accredited program before the full license examination may be taken.
- **states:** CT
- **sample (CT):** "Completed a minimum of fifty cases after graduating from a perfusion education program accredited or approved pursuant to subdivision (1) of this subsection."

## education program standards

### `accrediting_body_for_education_program` — list[str]
- **what:** The accrediting body or bodies whose approval of a perfusion education program satisfies the state's educational requirement for licensure.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (CA):** "An 'approved perfusion training program' means a training program in perfusion reviewed by the Accreditation Committee on Perfusion Education and approved by the Commission on Accreditation of Allied Health Education Programs or its successor."

## scope exceptions and carve-outs

### `autotransfusion_exemption` — bool
- **what:** Whether persons performing autotransfusion or blood conservation techniques under physician supervision are explicitly exempt from the perfusionist licensure requirement.
- **states:** GA, LA, NC
- **sample (LA):** "Qualified health care providers who are not licensed perfusionists or provisional licensed perfusionists from performing autotransfusion under the direct or indirect supervision of a licensed perfusionist."

### `ecmo_monitoring_exemption` — bool
- **what:** Whether monitoring of the ECMO circuit by other trained medical professionals (in conjunction with a licensed perfusionist) is explicitly permitted without a perfusionist license.
- **states:** LA
- **sample (LA):** "The monitoring of the extracorporeal membrane oxygenation (ECMO) circuit by a properly trained medical professional, in conjunction and with the consultation of a licensed perfusionist."

### `dialysis_technician_exemption` — bool
- **what:** Whether dialysis care technicians working in licensed end-stage renal disease facilities or hospitals are explicitly exempt from the perfusionist licensure requirement.
- **states:** GA
- **sample (GA):** "A person working as a dialysis care technician in an end stage renal disease facility licensed pursuant to Chapter 44 of Title 31 or a licensed hospital."

## practice setting and business structure

### `professional_service_corporation_permitted` — bool
- **what:** Whether one or more licensed perfusionists are explicitly permitted to form a professional service corporation.
- **states:** IL, LA
- **sample (LA):** "One or more licensed perfusionists from forming a professional service corporation in accordance with the Professional Service Corporation Act."

### `license_display_requirement` — bool
- **what:** Whether the statute requires the licensed perfusionist to display or keep a copy of their license accessible at the health care facility where they work.
- **states:** AR, MD, NV
- **sample (AR):** "The licensed perfusionist shall display the license in an appropriate and public manner or maintain an accurate copy of the perfusionist's license on file in the healthcare facility in which the licensed perfusionist is working."

## governance and advisory bodies

### `advisory_committee_exists` — bool
- **what:** Whether the state statute establishes a dedicated perfusionist advisory committee to assist the licensing board.
- **states:** GA, IL, LA, MD, MO, NC, NV
- **sample (MO):** "There is hereby established an 'Advisory Commission for Clinical Perfusionists' which shall guide, advise and make recommendations to the board."

### `advisory_committee_perfusionist_member_count` — int
- **what:** Number of licensed perfusionist members required on the state's perfusionist advisory committee.
- **states:** GA, IL, LA, MO, NC, NV
- **sample (MO):** "The advisory commission shall consist of five perfusionist members and two public members."

### `advisory_committee_physician_member_required` — bool
- **what:** Whether the statute requires at least one physician (typically a cardiothoracic surgeon or cardiovascular specialist) to serve on the perfusionist advisory committee.
- **states:** IL, LA, MO, NC, NV
- **sample (IL):** "One member shall be a physician licensed under the Medical Practice Act of 1987 who is board certified in and actively engaged in the practice of cardiothoracic surgery."

### `code_of_ethics_required` — bool
- **what:** Whether the statute explicitly requires the board or advisory committee to establish a code of ethics for licensed perfusionists.
- **states:** LA, MO, NC, NV
- **sample (LA):** "Establish a code of ethics."

## scope of practice definitions

### `perfusion_protocols_definition_included` — bool
- **what:** Whether the statute includes a definition of 'perfusion protocols' as policies developed collaboratively by the facility, physicians, and perfusionists.
- **states:** AR, CA, CT, GA, IL, LA, MO, NC, … (+1)
- **sample (AR):** "'Perfusion protocols' means perfusion related policies and protocols developed or approved by a licensed health facility or a physician through collaboration with administrators, licensed perfusionists, and other health care professionals."

### `hemodialysis_in_scope` — bool
- **what:** Whether hemodialysis is explicitly listed as a function within the authorized scope of perfusion practice.
- **states:** AR, CT, GA, IL, LA, MD, NC
- **sample (AR):** "The performance and use of... hemodialysis."

### `isolated_limb_perfusion_in_scope` — bool
- **what:** Whether isolated limb perfusion is explicitly listed as a function within the authorized scope of perfusion practice.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (AR):** "Counterpulsation, ventricular assistance, autotransfusion, blood conservation techniques, myocardial and organ preservation, extracorporeal life support, and isolated limb perfusion."

### `ventricular_assist_device_management_in_scope` — bool
- **what:** Whether ventricular assist device management or counterpulsation is explicitly listed as a function within the authorized scope of perfusion practice.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (GA):** "Ventricular assist device management; Intra-aortic balloon counterpulsation."

### `organ_preservation_in_scope` — bool
- **what:** Whether myocardial and organ preservation is explicitly listed as a function within the authorized scope of perfusion practice.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (AR):** "Myocardial and organ preservation, extracorporeal life support, and isolated limb perfusion."

### `neonatal_pediatric_bypass_explicitly_in_scope` — bool
- **what:** Whether the statute explicitly includes cardiopulmonary bypass for neonatal and pediatric patients (not just adult) within the authorized scope of perfusion.
- **states:** GA, MD
- **sample (GA):** "Cardiopulmonary bypass for adult, pediatric, and neonatal patients."

### `platelet_gel_progenitor_cell_harvest_in_scope` — bool
- **what:** Whether platelet gel production, autologous hemocyte tissue matrix production, or nondifferentiated progenitor cell harvest is explicitly listed within the authorized scope of perfusion.
- **states:** GA, MD
- **sample (MD):** "Platelet gel production, autologous hemocyte tissue matrix production; Nondifferentiated progenitor cell harvest bone marrow aspirate concentrate."

### `perfusion_assisted_direct_coronary_artery_bypass_in_scope` — bool
- **what:** Whether perfusion-assisted direct coronary artery bypass is explicitly listed within the authorized scope of perfusion.
- **states:** MD
- **sample (MD):** "Perfusion-assisted direct coronary artery bypass."

## drugs and agents authorized during perfusion

### `anesthetic_agent_administration_restricted_to_extracorporeal_circuit` — bool
- **what:** Whether the administration of anesthetic agents is restricted to the extracorporeal circuit (or IV line) and only during performance of extracorporeal support functions, as opposed to being unrestricted.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (IL):** "The administration of pharmacological and therapeutic agents and blood products or anesthetic agents through the extracorporeal circuit or through an intravenous line in conjunction with extracorporeal support, as ordered by and under the direct supervision of a physician."

### `anesthetic_agent_administration_requires_anesthesiologist_direction` — bool
- **what:** Whether administration of anesthetic agents through the heart-lung machine specifically requires direction from an anesthesiologist (rather than any physician).
- **states:** MD
- **sample (MD):** "Administration of anesthetic agents through a heart lung machine at the direction of an anesthesiologist."

## reciprocity and endorsement

### `reciprocity_requires_substantially_equivalent_standards` — bool
- **what:** Whether the state grants reciprocal licensure to perfusionists licensed in other states only if those states' requirements are substantially equivalent to the home state's requirements.
- **states:** AR, CT, GA, IL, LA, MO, NC, NV
- **sample (NC):** "The Committee may grant, upon application and payment of proper fees, a license to a person who has been licensed to practice perfusion in another state or territory of the United States whose standards of competency are substantially equivalent to those provided in this Article."

## continuing education

### `continuing_education_standards_reference_abcp` — bool
- **what:** Whether the statute explicitly requires that continuing education standards for perfusionists be at least as stringent as those established by the American Board of Cardiovascular Perfusion.
- **states:** LA
- **sample (LA):** "Establish continuing professional education requirements for licensed perfusionists and provisional licensed perfusionists under this Part, the standards of which shall be at least as stringent as the didactic requirements established by the American Board of Cardiovascular Perfusion or its successor agency."

## license renewal and expiration

### `license_expiration_cycle` — enum[annual, biennial, triennial]
- **what:** The standard renewal cycle for a perfusionist license.
- **states:** AR, CA, CT, GA, IL, LA, MD, MO, … (+2)
- **sample (LA):** "A license is valid for two years from the date it is issued and may be renewed."

### `license_expired_reinstatement_without_reexam_years` — int
- **what:** Maximum number of years a license may be expired before the applicant must reapply and retake the examination rather than simply renewing.
- **states:** AR, NC, NV
- **sample (NC):** "A license that has been expired for more than three years shall not be renewed, but the applicant may apply for a new license by complying with the current requirements for licensure under this Article."
