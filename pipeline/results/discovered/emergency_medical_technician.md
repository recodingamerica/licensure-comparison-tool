# Discovered fields — emergency_medical_technician

## types of credentials and what each level can do

### `certification_levels` — list[str]
- **what:** The tiered hierarchy of EMS personnel credential levels recognized by the state, from least to most advanced.
- **states:** AZ, CT, DE, FL, IA, KS, KY, MA, … (+2)
- **sample (CT):** "For the purposes of this section, the classification of licensure or certification from highest to lowest is: Paramedic, advanced emergency medical technician, emergency medical technician and emergency medical responder."

### `national_registry_exam_required` — bool
- **what:** Whether the state requires use of the National Registry of Emergency Medical Technicians (NREMT) examination as a condition of initial licensure.
- **states:** CT, DE, IA, KS, KY, MD, ME
- **sample (DE):** "Currently requires the use of the National Registry of Emergency Medical Technicians (NREMT) examination as a condition of issuing initial licenses at the EMT and paramedic levels."

### `advanced_practice_subspecialties` — list[str]
- **what:** Named subspecialty certifications available to paramedics beyond the base paramedic license, such as community paramedic or flight paramedic.
- **states:** DE, KY, ME
- **sample (KY):** "'Advanced practice paramedic' or 'APP' means a paramedic licensed by the board under this chapter as a paramedic and certified by the board under this chapter in at least one (1) emergency medical services subspecialty, including community paramedic, critical care paramedic, wilderness paramedic, tactical paramedic, or flight paramedic."

### `community_paramedicine_authorized` — bool
- **what:** Whether the state explicitly authorizes a community paramedicine or mobile integrated healthcare program allowing paramedics to provide non-emergency care outside the hospital.
- **states:** CT, DE, KY, MA, ME
- **sample (DE):** "'Community paramedicine' means a form of mobile-integrated healthcare that is a provider-led, patient-centered delivery care model using appropriately-trained paramedics or other emergency medical services providers in an expanded role to render care, facilitate a more efficient delivery of care, and enhance access to community resources that address the social determinants of health."

## physician oversight and medical control

### `medical_director_required` — bool
- **what:** Whether each ambulance service or EMS provider is required to designate a physician medical director to provide medical oversight.
- **states:** AZ, CT, DE, IA, KS, KY, MA, MD, … (+1)
- **sample (KS):** "Except as provided in subsection (b), each operator shall designate a medical director to provide medical oversight."

### `medical_director_board_certification_required` — bool
- **what:** Whether the state requires the EMS medical director to be board-certified in emergency medicine.
- **states:** DE, KY, MA, MD
- **sample (DE):** "Each EMS medical director shall be employed by the State, by contract or otherwise, and shall be a board certified emergency physician actually involved in the practice of emergency medicine."

### `standing_orders_authorized` — bool
- **what:** Whether EMS personnel may act under written standing orders or protocols without real-time physician contact.
- **states:** AZ, CT, DE, IA, KS, KY, MA, MD, … (+1)
- **sample (IA):** "If communications fail during an emergency or nonemergency situation, the emergency medical care provider may perform any emergency medical care procedure for which that individual is certified and which is included in written protocols if in the judgment of the emergency medical care provider the life of the patient is in immediate danger."

### `protocol_approval_process` — str
- **what:** The body or process responsible for reviewing and approving EMS treatment protocols and standing orders before they take effect.
- **states:** CT, DE, IA, KS, KY, ME
- **sample (KY):** "Each emergency medical services medical director for an ambulance service, or other emergency medical services provider, shall submit his or her protocols... to the board for approval prior to placing the document in use."

## service and vehicle licensing

### `ambulance_service_license_required` — bool
- **what:** Whether ambulance services must obtain a state-issued license or permit to operate.
- **states:** AZ, CT, DE, IA, KS, KY, MA, MD, … (+1)
- **sample (KS):** "It shall be unlawful for any person or municipality to operate an ambulance service within this state without obtaining a permit pursuant to this act."

### `ambulance_vehicle_inspection_required` — bool
- **what:** Whether ambulance vehicles must pass a state inspection and receive a certificate before operating.
- **states:** CT, DE, KS, MA, MD, ME
- **sample (CT):** "Each ambulance and invalid coach used by an emergency medical service organization shall be inspected to verify such ambulance or invalid coach has met the minimum standards prescribed by the Commissioner of Public Health."

### `minimum_staffing_requirements` — str
- **what:** The minimum number and credential level of personnel required to staff an ambulance during patient transport.
- **states:** CT, KS, KY, MA, MD, ME
- **sample (CT):** "The commissioner shall adopt regulations in accordance with the provisions of chapter 54 to require all ambulances to be staffed by at least one certified emergency medical technician, who shall be in the patient compartment attending the patient during all periods in which a patient is being transported, and one certified emergency medical responder."

### `rural_county_staffing_exception` — bool
- **what:** Whether the state provides a reduced staffing requirement or variance for ambulance services operating in rural or low-population counties.
- **states:** KS, ME
- **sample (KS):** "The board shall not require any ground vehicle providing emergency medical services in any county with a population of 30,000 or less to operate with more than one person who satisfies the requirements of subsection (c) if the driver of such vehicle is certified in cardiopulmonary resuscitation."

## system planning and governance

### `regional_ems_council_structure` — bool
- **what:** Whether the state organizes EMS oversight through designated regional councils that assist with planning, coordination, and quality improvement.
- **states:** AZ, CT, DE, IA, KY, MA, MD, ME
- **sample (MA):** "Each regional EMS council shall assist and support the department in carrying out the provisions of this chapter and in developing and implementing the state and regional EMS plans, by planning, guiding and coordinating the components of the EMS system serving their regions."

### `statewide_ems_medical_director_position` — bool
- **what:** Whether the state designates a single statewide EMS medical director responsible for clinical oversight of the entire EMS system.
- **states:** CT, DE, IA, KY, MA, MD, ME
- **sample (DE):** "'State EMS Medical Director' means a physician who is board-certified by the American Board of Emergency Medicine or by the Osteopathic Board of Emergency Medicine and who shall be the chief physician for the statewide emergency medical system and under whose license all EMS providers shall operate for the purpose of delivering the standing orders of the statewide standard treatment protocol."

### `trauma_system_designation` — bool
- **what:** Whether the state operates a formal trauma center designation program with defined levels of trauma care capability.
- **states:** AZ, CT, DE, IA, KY, MA, MD, ME
- **sample (MA):** "The department shall develop a statewide coordinated trauma care system. At a minimum, the department, by regulation and guideline, shall provide for (1) the designation of trauma centers at various levels."

### `service_zone_or_primary_service_area_system` — bool
- **what:** Whether the state uses a formal geographic service zone or primary service area system to assign ambulance services to defined territories.
- **states:** AZ, CT, MA
- **sample (MA):** "'Service zone' means a geographic area defined by and comprised of one or more local jurisdictions, in which a local jurisdiction may select and the department shall designate an EMS first response service and an ambulance service to provide EMS first response and primary ambulance response to the public within that defined geographic area."

## interstate recognition and reciprocity

### `interstate_compact_member` — bool
- **what:** Whether the state has enacted the Recognition of Emergency Medical Services Personnel Licensure Interstate Compact (REPLICA), allowing EMS personnel licensed in one member state to practice in other member states.
- **states:** CT, DE, IA, KS, KY, MD, ME
- **sample (DE):** "The Recognition of Emergency Medical Services Personnel Licensure Interstate Compact Act ('REPLICA') is hereby enacted into law and entered into with all other jurisdictions legally joining therein."

### `military_veteran_licensure_pathway` — bool
- **what:** Whether the state provides an expedited or alternative licensure pathway for military veterans or active-duty service members with equivalent EMS training.
- **states:** CT, DE, IA, KS, KY, MA, MD, ME
- **sample (CT):** "The Commissioner of Public Health shall issue an emergency medical technician certification to an applicant who is a member of the armed forces or the National Guard or a veteran and who presents evidence satisfactory to the commissioner that such applicant holds a current certification as a person entitled to perform similar services under a different designation by the National Registry of Emergency Medical Technicians."

## applicant screening and fitness requirements

### `criminal_background_check_required` — bool
- **what:** Whether applicants for EMS licensure or certification must submit to a criminal history background check, including fingerprinting.
- **states:** CT, DE, KS, KY, MD, ME
- **sample (KS):** "The emergency medical services board may require an original applicant for certification as an emergency medical services provider to be fingerprinted and submit to a state and national criminal history record check."

### `mental_health_training_required` — bool
- **what:** Whether the state requires EMS personnel to complete specific training on mental health topics such as suicide prevention, PTSD screening, or mental health first aid as a condition of initial certification or renewal.
- **states:** CT, KY
- **sample (CT):** "For applicants applying on and after January 1, 2020, completed mental health first aid training as part of a program provided by an instructor certified by the National Council for Behavioral Health."

## what each credential level is allowed to do clinically

### `scope_of_practice_by_level` — list[str]
- **what:** The specific clinical procedures, interventions, or medications authorized for each EMS certification level, as enumerated in statute.
- **states:** CT, DE, IA, KS, KY, MA, MD, ME
- **sample (KS):** "Notwithstanding any other provision of law to the contrary, after successfully completing an approved course of instruction, local specialized device training and competency validation and when authorized by medical protocols or upon the order of a qualified healthcare provider, an advanced emergency medical technician may: perform any of the activities identified by K.S.A. 65-6121 and 65-6144; and perform any of the following interventions: advanced airway management; veni-puncture for obtaining blood sample; initiation and maintenance of intravenous infusion or saline lock; initiation and maintenance of intraosseous infusion; manual defibrillation; cardiac monitoring; electrocardiogram interpretation; and administration of medications."

### `epinephrine_administration_authorized` — bool
- **what:** Whether EMS personnel are explicitly authorized by statute to administer epinephrine for anaphylaxis.
- **states:** CT, KY, MD, ME
- **sample (KY):** "Any emergency medical technician and any paramedic shall be authorized to administer epinephrine to any person whom the EMT or paramedic has been called to attend if the EMT or paramedic makes an assessment that the person is exhibiting symptoms consistent with an anaphylactic reaction."

### `naloxone_administration_authorized` — bool
- **what:** Whether EMS personnel are explicitly authorized or required by statute to carry and administer naloxone or another opioid overdose reversal drug.
- **states:** CT, DE, IA, MD, ME
- **sample (ME):** "An emergency medical services person licensed under this chapter shall administer and dispense naloxone hydrochloride or another opioid overdose-reversing medication in compliance with protocols and training developed in accordance with this chapter."

### `aed_program_regulated` — bool
- **what:** Whether the state has a formal regulatory program governing the placement, registration, and use of automated external defibrillators (AEDs) by the public or EMS personnel.
- **states:** CT, DE, KS, MD
- **sample (MD):** "There is a Public Access Automated External Defibrillator Program. The purpose of the Program is to coordinate an effective statewide public access defibrillation program."

## patient rights and transport decisions

### `patient_transport_refusal_rules` — bool
- **what:** Whether the state has specific statutory rules governing how EMS personnel must handle a patient's decision to decline transport, including prohibitions on counseling patients to refuse.
- **states:** AZ, CT, MA, ME
- **sample (AZ):** "An emergency medical care technician may not do either of the following: Provide a patient with a presumptive medical diagnosis and use that medical diagnosis as the basis for counseling the patient to decline emergency medical services transportation. Counsel a patient to decline emergency medical services transportation, except as part of a specific alternate destination or treat-and-refer program."

### `alternate_destination_transport_authorized` — bool
- **what:** Whether EMS personnel are authorized to transport patients to destinations other than a hospital emergency department, such as urgent care centers or mental health facilities.
- **states:** AZ, CT, MA
- **sample (CT):** "A licensed or certified emergency medical services organization or provider may transport a patient by ambulance to an alternate destination, in consultation with the medical director of a sponsor hospital."

### `patient_restraint_authorized` — bool
- **what:** Whether EMS personnel are explicitly authorized by statute to physically restrain a patient who poses an immediate threat of harm.
- **states:** MA, ME
- **sample (MA):** "Subject to regulations and guidelines promulgated by the department, an emergency medical technician may restrain a patient who presents an immediate or serious threat of bodily harm to himself or others."

### `treatment_of_police_dogs_authorized` — bool
- **what:** Whether EMS personnel are explicitly authorized by statute to provide emergency medical treatment and transport to injured law enforcement dogs.
- **states:** CT, DE, MA, ME
- **sample (DE):** "A paramedic or other EMS provider may provide emergency medical services to an injured police dog at the scene of an emergency that has resulted in the police dog's injury."

## quality improvement and data reporting

### `ems_data_collection_required` — bool
- **what:** Whether ambulance services and EMS providers are required by statute to collect and submit standardized patient care data to a state or regional authority.
- **states:** CT, DE, IA, KY, MA, MD, ME
- **sample (KY):** "Each licensed ambulance provider, mobile integrated healthcare program, and medical first response provider as defined in this chapter shall collect and provide to the board patient care record data and information required by the board by this chapter and administrative regulation."

### `quality_assurance_program_required` — bool
- **what:** Whether ambulance services are required to maintain a formal quality assurance or continuous quality improvement program.
- **states:** AZ, CT, DE, KS, KY, MA, MD, ME
- **sample (ME):** "The board shall establish and maintain a statewide quality assurance and improvement committee and shall adopt rules regarding the requirements and authority of the statewide quality assurance and improvement committee."

## training and education oversight

### `ems_instructor_certification` — bool
- **what:** Whether the state separately certifies or licenses EMS instructors or training institutions beyond the general EMS personnel certification.
- **states:** CT, DE, IA, KS, KY, ME
- **sample (CT):** "On or after January 1, 2020, each person seeking certification as an emergency medical services instructor shall apply to the department on forms prescribed by the commissioner."

### `emergency_medical_dispatcher_certification` — bool
- **what:** Whether the state separately certifies or licenses emergency medical dispatchers and regulates emergency medical dispatch centers.
- **states:** CT, DE, KY, MD, ME
- **sample (MD):** "'Emergency medical dispatcher' (EMD) means an individual who has completed an emergency medical dispatcher course approved by the EMS Board or its equivalent as determined by the EMS Board; demonstrated competence in medical protocols as determined by the EMS Board; and been examined by the EMS Board or has been recognized as an emergency medical dispatcher by an emergency medical dispatcher program approved by the EMS Board and licensed as an emergency medical dispatcher by the EMS Board."

### `inactive_license_status_available` — bool
- **what:** Whether the state allows EMS personnel to place their license or certification in an inactive status, suspending practice and continuing education requirements while not actively providing EMS.
- **states:** CT, KS, ME
- **sample (KS):** "There is hereby created the designation of inactive certificate. The board is authorized to issue an inactive certificate to any person currently certified by the board who makes written application for such inactive certificate... The holder of an inactive certificate shall not be required to submit evidence of satisfactory completion of the continuing education requirement prescribed by the board."

## liability and legal protections

### `civil_immunity_for_good_faith_care` — bool
- **what:** Whether the state provides statutory civil liability immunity to EMS personnel who render emergency care in good faith.
- **states:** AZ, CT, DE, IA, KS, KY, MA, MD, … (+1)
- **sample (MA):** "No EMS personnel certified, accredited or otherwise approved under this chapter, and no additional personnel certified or authorized under section 9, who in the performance of their duties and in good faith, render emergency first aid, cardiopulmonary resuscitation, transportation or other EMS to an injured person, a person incapacitated by illness or an injured police dog under section 9A shall be personally liable as a result of rendering such aid or services."

### `physician_online_medical_control_immunity` — bool
- **what:** Whether the state provides civil liability immunity to physicians who give real-time medical direction to EMS personnel by radio or telephone.
- **states:** AZ, DE, IA, KS, MA, ME
- **sample (MA):** "No physician duly registered under section 2, 2A, or 9 of chapter 112... shall be liable in a suit for damages as a result of acts or omissions related to advice, consultation or orders given in good faith to emergency medical services personnel who are qualified under section 9 and are acting on behalf of a service duly licensed under section 6, by radio, telephone or other remote means of communication."

### `scope_of_practice_cannot_be_exceeded` — bool
- **what:** Whether the state explicitly prohibits EMS personnel from performing procedures beyond their certification level and protects them from employer retaliation for refusing to do so.
- **states:** IA, KS, KY, ME
- **sample (KY):** "It is the legal duty of an emergency medical responder, emergency medical technician, advanced emergency medical technician, or paramedic to refuse to perform any act or procedure which is beyond the scope of practice for his or her level of certification or licensure regardless of whether that act or procedure is ordered by a physician, physician assistant, medical director, advanced practice registered nurse, registered nurse, or supervisor."

### `ems_personnel_death_benefit` — bool
- **what:** Whether the state provides a statutory death benefit payment to the survivors of EMS personnel who die in the line of duty.
- **states:** MD, ME
- **sample (ME):** "In a case in which the director determines under rules adopted pursuant to this section that an emergency medical services person has died while in the line of duty... the State shall pay a benefit of $100,000."
