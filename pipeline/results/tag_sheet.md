# Field Tag Sheet

_Generated 2026-06-22T16:53:02+00:00_

Plain-English tags for each profession's key licensure fields, derived
by `pipeline.map_prep.bucket_text` (no per-row hand-curation — the LLM
clustered each field's actual state values into a handful of buckets).
Counts are states per tag (or disciplinary grounds per tag, for the
Discipline field). Scope wording is profession-specific, so the bucketed
field name varies by profession.

## Dentistry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **DDS/DMD, CODA Accredited** (6)
- **DDS/DMD, Board/State Approved** (2)
- **DDS/DMD, No Accreditor Specified** (8)
- **Dental Degree, CODA Accredited** (10)
- **Dental Degree, Board/State Approved** (5)
- **Dental Degree, Accredited (General)** (8)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General Dentistry Residency** (2)
- **General or Specialty Residency** (2)
- **Internship or Residency** (1)
- **Supervised Clinical Practice** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year Minimum** (4)
- **Hours-Based** (1)
- **1 Year or Residency** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Dental Examiners** (12)
- **Board of Dentistry** (18)
- **State Dept / Agency** (9)
- **Dental Board (Named)** (6)
- **Specialty Board** (5)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Dental Examiners** (15)
- **Board of Dentistry** (20)
- **Dental Board** (6)
- **Commission or Dept** (4)
- **Includes Hygiene** (2)
- **Other Named Board** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Surgical + Nonsurgical** (10)
- **Diagnosis + Treatment Core** (10)
- **Comprehensive Enumerated** (12)
- **Broad Clinical Scope** (12)
- **Minimal Abstract** (4)

`scope.drug_authority` — states per tag:

- **Prescribe & Anesthesia** (9)
- **Prescribe Only** (12)
- **Anesthesia Only** (3)
- **Controlled Substances Focus** (11)
- **Vaccines Included** (3)
- **Anesthesia Permit Required** (6)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (132, 49 states)
- **Criminal Conviction** (60, 42 states)
- **Clinical Negligence & Incompetence** (124, 44 states)
- **Substance Abuse & Impairment** (95, 44 states)
- **Unlicensed Practice & Delegation** (98, 45 states)
- **Advertising Violations** (65, 39 states)
- **Billing & Fee Irregularities** (59, 30 states)
- **Sexual & Immoral Conduct** (34, 25 states)
- **Regulatory & Reporting Noncompliance** (287, 49 states)

### Other bucketed fields

#### Advanced practice eligible patient populations

`profession_specific.advanced_practice_eligible_patient_populations` — items per tag:

- **Long-Term Care and Residential Facilities** (39, 19 states)
- **Schools and Early Childhood Programs** (26, 17 states)
- **Correctional Facilities** (10, 6 states)
- **Community and Public Health Settings** (55, 24 states)
- **Homebound Individuals** (12, 11 states)
- **Underserved and Low-Income Populations** (26, 17 states)
- **Children and Youth in Social Services** (12, 6 states)
- **Hospitals and Medical Facilities** (24, 15 states)

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advisory + Rulemaking Proposals** (1)
- **Advisory + Discipline Recs** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Dental Hygienists Committee** (2)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substances** (7)
- **Ethics & Professionalism** (2)
- **Emergency & Life Support** (2)
- **Broad Clinical Topics** (2)
- **Infection Control** (0)
- **Multi-Topic Required** (7)

#### Dental hygienist supervision levels

`profession_specific.dental_hygienist_supervision_levels` — items per tag:

- **Direct Supervision** (45, 42 states)
- **Indirect Supervision** (11, 11 states)
- **General Supervision** (42, 40 states)
- **Public Health Supervision** (9, 9 states)
- **Collaborative Practice** (4, 4 states)
- **Unsupervised Practice** (3, 3 states)
- **Other Supervision Type** (8, 7 states)

#### Dental therapist practice setting restrictions

`profession_specific.dental_therapist_practice_setting_restrictions` — items per tag:

- **Federally Qualified Health Centers** (9, 4 states)
- **Tribal and Indian Health Settings** (5, 3 states)
- **Hospital or Medical Facility** (5, 4 states)
- **Public Health and Government Agency** (6, 5 states)
- **School-Based Settings** (5, 4 states)
- **Nonprofit and Charitable Organizations** (6, 3 states)
- **Underserved Population Clinics** (6, 3 states)
- **Correctional Facilities** (2, 2 states)
- **Agreement-Defined Settings** (6, 5 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **CODA (full name)** (40)
- **CODA (abbreviation)** (4)
- **ADA only** (2)
- **Board Discretion** (2)

#### Exams

`licensure.exams` — states per tag:

- **National + Clinical** (20)
- **National + Clinical + Jurisprudence** (10)
- **National + State Clinical** (5)
- **State Board Only** (4)
- **Board Discretion** (9)

#### National association

`licensure.national_association` — states per tag:

- **ADA** (29)
- **ADA (explicit acronym)** (5)
- **ADA + Accreditation Body** (4)
- **CODA Only** (1)
- **Other Association** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **JCNDE / National Board** (4)
- **ABOMS / Oral Surgery Board** (1)
- **Multi-Org Listing** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **5+ Yrs Practice** (6)
- **2–3 Yrs Practice** (7)
- **Hours-Based Threshold** (4)
- **Exam-Centric** (3)
- **Equivalent Standards Only** (5)
- **Comprehensive Multi-Factor** (14)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Health Dept** (7)
- **Consumer Affairs** (2)
- **Commerce Dept** (3)
- **Licensing & Regulation** (4)
- **Professional Regulation Office** (5)

#### Sedation anesthesia permit types

`profession_specific.sedation_anesthesia_permit_types` — items per tag:

- **General Anesthesia** (31, 31 states)
- **Deep Sedation** (17, 17 states)
- **Moderate Sedation** (36, 30 states)
- **Minimal Sedation** (9, 9 states)
- **Nitrous Oxide Analgesia** (3, 3 states)
- **Pediatric Endorsement** (3, 2 states)
- **Unspecified Credential Type** (13, 10 states)

## Dietetics

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Bachelor's Min, Field-Specific** (29)
- **Bachelor's Min, General** (7)
- **Master's/Doctoral Required** (2)
- **Tiered by License Type** (8)
- **Tiered by Grad Year** (1)
- **CDR/RD Registration** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Supervised Practice** (15)
- **Preprofessional Program** (15)
- **Internship / Program Options** (8)
- **Accredited Program** (4)
- **Work / Field Experience** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **900 Hours** (26)
- **1,000 Hours** (4)
- **1,200 Hours** (1)
- **Multiple Pathways** (1)
- **Time-Based** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Dietetics Board** (20)
- **Medical/Nursing Board** (7)
- **General Health Dept** (9)
- **General Licensing Agency** (10)
- **Other State Agency** (2)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Dietetics Board** (24)
- **Medical/Health Board** (7)
- **General Health Dept** (11)
- **General Licensing Agency** (6)

#### Scope of Practice

`scope.drug_authority` — states per tag:

- **Dose Adjust Only** (1)
- **Dose Adjust + Supplements** (2)
- **Protocol Prescribing** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Licensure** (50, 40 states)
- **Criminal Conviction** (46, 38 states)
- **Incompetence or Negligence** (36, 27 states)
- **Unprofessional or Unethical Conduct** (93, 40 states)
- **Substance Impairment** (25, 22 states)
- **Physical or Mental Incapacity** (24, 18 states)
- **False or Deceptive Advertising** (14, 12 states)
- **Regulatory Noncompliance** (85, 44 states)
- **Out-of-State Discipline** (18, 17 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Pure Advisory** (6)
- **Advisory + Disciplinary Role** (1)
- **Delegated Rulemaking** (2)
- **Binding Recommendations** (3)
- **Exam & Licensure Focus** (2)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Board / Practice Board** (3)
- **Council** (4)
- **Advisory Committee** (3)
- **Advisory Group / Panel** (3)
- **Allied Health Board** (1)

#### Alternative credential pathways

`profession_specific.alternative_credential_pathways` — items per tag:

- **CNS Certification (BCNS)** (10, 10 states)
- **DACBN Diplomate** (6, 6 states)
- **ABN Affiliation** (7, 3 states)
- **RD/RDN Registration** (2, 2 states)
- **Academic Degree** (2, 2 states)
- **Reciprocity / Endorsement** (1, 1 states)
- **Board-Approved Credential** (2, 2 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Pain & Symptom Mgmt** (1)
- **Nutrition & Metabolism** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACEND / ADA** (9)
- **Regional Accreditor (Generic)** (16)
- **Named Regional Body** (6)
- **CHEA + US Dept of Ed** (10)
- **CDR / Other Dietetics Body** (2)

#### Exempt professions list

`profession_specific.exempt_professions_list` — items per tag:

- **Licensed Health Professionals** (128, 35 states)
- **Students and Trainees** (33, 26 states)
- **Dietetic Support Staff** (32, 20 states)
- **Federal or Military Employees** (20, 18 states)
- **Government or Public Agency Employees** (32, 23 states)
- **Food and Supplement Retailers** (29, 23 states)
- **General Nutrition Information Providers** (41, 19 states)
- **Weight Control Program Providers** (21, 19 states)
- **Animal or Traditional Practitioners** (8, 7 states)

#### License type structure

`profession_specific.license_type_structure` — items per tag:

- **Licensed Dietitian** (27, 26 states)
- **Licensed Nutritionist** (10, 10 states)
- **Licensed Dietitian-Nutritionist** (15, 15 states)
- **Certified Dietitian** (8, 6 states)
- **Certified Nutritionist** (3, 3 states)
- **Provisional/Temporary License** (16, 15 states)
- **Dietetic Technician** (2, 2 states)
- **Special/Other Credential** (6, 5 states)

#### National association

`licensure.national_association` — states per tag:

- **American Dietetic Assoc** (18)
- **Academy of Nutrition & Dietetics** (11)
- **ACEND Accreditor** (2)
- **Multiple Associations** (3)
- **State Dietetic Assoc** (3)

#### National certification

`licensure.national_certification` — states per tag:

- **CDR Only** (40)
- **CDR + Multi-Body** (5)
- **Board-Approved Body** (2)

#### Protected titles

`profession_specific.protected_titles` — items per tag:

- **Dietitian Title** (90, 45 states)
- **Nutritionist Title** (42, 22 states)
- **Dietitian-Nutritionist Combined** (23, 16 states)
- **Nutrition Therapist Specialist** (9, 3 states)
- **Dietetic Technician** (3, 2 states)
- **Abbreviation Only** (61, 34 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards** (26)
- **Equivalent + Clean Record** (5)
- **CDR/Cert Recognition** (7)
- **Reciprocity Agreement** (2)
- **Endorsement/Fee Only** (3)
- **Temporary/Partial Practice** (2)
- **Full Reapplication** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Health Dept** (7)
- **Professional Licensing Office** (9)
- **Commerce / Labor / State** (4)
- **Consumer / Law Affairs** (1)
- **Aging / Disability Services** (1)

## Medicine

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **MD Only** (7)
- **MD or DO** (16)
- **Graduate of Approved School** (17)
- **Accredited Degree + Extra Requirements** (4)
- **Foreign School Provisions** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Residency Only** (18)
- **Residency + Internship** (12)
- **Residency + Fellowship** (2)
- **Residency + Internship + Fellowship** (3)
- **General Postgrad Training** (11)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (9)
- **2 Years** (9)
- **3 Years** (2)
- **1 Yr Domestic / 2 Yrs IMG** (9)
- **1 Yr Domestic / 3 Yrs IMG** (5)
- **Tiered by Grad Date** (2)
- **Board Discretion** (6)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Medical Board** (22)
- **Board of Examiners** (8)
- **Board of Licensure** (7)
- **Board of Practice/Arts** (4)
- **State Health Dept** (4)
- **Other State Agency** (5)

`licensure.regulatory_authority.name` — states per tag:

- **Medical Board** (23)
- **Board of Medical Examiners** (8)
- **Board of Medical Licensure** (10)
- **Board of Medical Practice** (2)
- **Healing Arts Board** (2)
- **Dept / Education Authority** (2)
- **Composite / Multi-Role Board** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Four** (11)
- **Core + Rx Detail** (5)
- **Core + Surgery Detail** (5)
- **Broad Enumerated** (9)
- **General Labels Only** (7)
- **Comprehensive + Telehealth** (9)

`scope.drug_authority` — states per tag:

- **Broad Full Authority** (12)
- **Standard + Opioid Limits** (7)
- **Standard + Delegation** (4)
- **Standard + Procedural Rules** (8)
- **Basic Prescribing Only** (10)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (239, 50 states)
- **Criminal Conviction** (74, 44 states)
- **Clinical Incompetence & Negligence** (114, 46 states)
- **Substance Abuse & Impairment** (97, 46 states)
- **Improper Prescribing & Drug Violations** (95, 39 states)
- **Sexual Misconduct** (34, 24 states)
- **Unprofessional & Unethical Conduct** (197, 47 states)
- **Regulatory & Reporting Violations** (353, 50 states)
- **Supervision & Delegation Failures** (79, 41 states)

### Other bucketed fields

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioids / Controlled Substances** (9)
- **Broad Multi-Topic Mandate** (5)
- **Patient Safety & Ethics** (3)
- **Specialty / Population Focus** (5)
- **Abuse & Violence** (3)
- **Pain Management** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **LCME / AOA Only** (11)
- **LCME + AOA + Canadian** (4)
- **LCME + AOA + Foreign** (5)
- **AMA / AAMC Based** (8)
- **Board Discretion** (14)
- **Federal / WHO Based** (3)

#### License status types

`profession_specific.license_status_types` — items per tag:

- **Active Full License** (39, 36 states)
- **Inactive / Retired Status** (42, 28 states)
- **Temporary / Provisional License** (47, 29 states)
- **Training / Resident Permit** (24, 23 states)
- **Limited / Restricted License** (39, 25 states)
- **Teaching / Faculty License** (15, 12 states)
- **Administrative Medicine License** (11, 11 states)
- **Volunteer / Pro Bono License** (14, 13 states)
- **Interstate / Compact License** (5, 5 states)

#### National association

`licensure.national_association` — states per tag:

- **AMA Only** (4)
- **AOA Only** (2)
- **AMA + AOA** (5)
- **ABMS Included** (5)
- **ACGME Included** (3)
- **Accreditation Body** (2)
- **State/Regional Only** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NBME / NBEO** (3)
- **ECFMG** (7)
- **ABMS / AOA / Canadian** (6)
- **NBME + ECFMG Combo** (0)
- **Multi-Board Combo** (2)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Hard Day-Supply Cap** (7)
- **MME/Dose Cap** (2)
- **Prescriber Discretion + Guidelines** (2)
- **Board Rulemaking Mandate** (5)
- **Delegation / Dispensing Restriction** (4)
- **Safe Harbor / Anti-Discipline** (2)
- **PDMP / Process Requirement** (1)

#### Physician assistant prescriptive authority

`profession_specific.physician_assistant_prescriptive_authority` — states per tag:

- **Full Schedule II–V** (7)
- **Schedule III–V Only** (3)
- **Schedule II–V w/ Limits** (4)
- **Delegated by Physician** (6)
- **Board/Agreement Governed** (6)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **IMLC Pathway** (5)
- **Equivalent Standards** (20)
- **Active Practice Required** (7)
- **Exam Equivalency Focus** (10)
- **Strict Additional Criteria** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (8)
- **Consumer Affairs** (3)
- **Commerce / Economic Dev** (3)
- **Professional Licensing Div** (5)
- **Labor & Industry** (2)
- **Education Dept** (1)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Controlled Substance Restrictions** (7)
- **Prior In-Person Required** (6)
- **Same Standard as In-Person** (6)
- **Licensure / Jurisdiction Focus** (12)
- **Permissive / Broad Telehealth** (6)

## Nursing

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Approved Program Only** (19)
- **HS Diploma + Approved Program** (6)
- **Diploma/Degree from Approved Program** (11)
- **Accredited Program Required** (5)
- **Multi-Level / Tiered Requirements** (6)
- **Graduate Degree for APRN** (3)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Transition to Practice** (2)
- **Supervised Practice** (1)
- **Collaborative Practice** (1)
- **Supervised/Collaborative** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~1,000 hrs** (1)
- **~2,000 hrs** (1)
- **~2,080 hrs** (1)
- **24 Months** (1)
- **4,600 hrs / 3 yrs** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Nursing** (8)
- **State Board of Nursing** (11)
- **Named State Board** (21)
- **Dept / Agency** (4)
- **Board + Dept Joint** (2)
- **Specialty Board Name** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Nursing** (11)
- **State Board of Nursing** (11)
- **Named State Board of Nursing** (21)
- **Board of Examiners/Registration** (4)
- **Dept/Division (Non-Board)** (3)

#### Scope of Practice

`scope.drug_authority` — states per tag:

- **RN Administer Only** (14)
- **APRN Independent Rx** (10)
- **APRN Collaborative Rx** (6)
- **APRN Delegated Rx** (2)
- **Mixed RN/APRN Tiered** (12)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Licensure** (74, 47 states)
- **Criminal Conviction** (61, 43 states)
- **Incompetence or Negligence** (77, 45 states)
- **Substance Abuse or Impairment** (65, 45 states)
- **Physical or Mental Incapacity** (45, 36 states)
- **Unprofessional Conduct** (168, 46 states)
- **Records and Documentation Violations** (24, 16 states)
- **Regulatory and Administrative Violations** (193, 50 states)
- **Adverse Action in Other Jurisdiction** (40, 36 states)

### Other bucketed fields

#### Aprn role categories

`profession_specific.aprn_role_categories` — items per tag:

- **Nurse Practitioner** (44, 44 states)
- **Nurse Anesthetist** (43, 43 states)
- **Nurse Midwife** (36, 36 states)
- **Clinical Nurse Specialist** (41, 41 states)
- **Psychiatric Mental Health Specialist** (4, 4 states)
- **General APRN Category** (3, 3 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Pharmacology / Prescribing** (5)
- **Opioids / Substance Use** (3)
- **Mental Health / Suicide** (1)
- **Abuse / Trafficking** (2)
- **Multi-Topic Mandate** (7)
- **Bias / Cultural Competency** (1)
- **Jurisprudence / Ethics** (1)

#### Controlled substance schedule authority

`profession_specific.controlled_substance_schedule_authority` — items per tag:

- **Schedule I** (2, 2 states)
- **Schedule II Unrestricted** (10, 10 states)
- **Schedule II Restricted** (13, 12 states)
- **Schedule II Partial** (1, 1 states)
- **Schedules III–V** (51, 18 states)
- **Non-Controlled Drugs** (3, 2 states)
- **Role/Statute Based Authority** (3, 1 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **State Board Only** (13)
- **National Accreditor** (2)
- **State Board + National** (7)
- **Federal DOE Reference** (4)
- **Named Accreditor** (2)

#### Exams

`licensure.exams` — states per tag:

- **NCLEX Only** (24)
- **NCLEX + Jurisprudence** (2)
- **NCLEX + APRN Exam** (5)
- **National Exam (Generic)** (9)
- **State/Board Exam** (10)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Licensed Practical Nurse** (48, 48 states)
- **Registered Nurse** (55, 50 states)
- **Nurse Practitioner** (23, 21 states)
- **Nurse Anesthetist** (22, 22 states)
- **Nurse Midwife** (16, 16 states)
- **Clinical Nurse Specialist** (21, 21 states)
- **APRN Umbrella** (35, 33 states)
- **Nursing Assistant / Aide** (9, 7 states)
- **Medication Aide / Other** (8, 7 states)

#### Lpn supervision requirements

`profession_specific.lpn_supervision_requirements` — items per tag:

- **Registered Nurse** (47, 45 states)
- **Advanced Practice Registered Nurse** (17, 16 states)
- **Physician** (42, 39 states)
- **Physician Assistant** (9, 9 states)
- **Dentist** (33, 33 states)
- **Podiatrist** (14, 14 states)
- **Other Specialist** (11, 7 states)
- **General Licensed Provider** (15, 15 states)

#### National association

`licensure.national_association` — states per tag:

- **ANA / General RN** (4)
- **Nurse Practitioners** (1)
- **Nurse Midwives** (2)
- **Nurse Anesthetists** (0)
- **State Association** (1)
- **Accreditation / Credentialing Body** (2)
- **Multi-Specialty List** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCLEX / NCSBN** (4)
- **APRN Required** (2)
- **Board-Approved Body** (7)
- **Named Org(s)** (4)
- **Foreign Grad Body** (1)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Short Supply Cap** (6)
- **MME/Dose Limit** (1)
- **Physician Oversight Required** (4)
- **Dispensing Prohibited** (1)
- **Rules-Based / Statutory Ref** (2)
- **Formulary / Lowest Dose** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Meet State Standards** (17)
- **Substantially Equivalent** (16)
- **Active Practice Required** (5)
- **NLC Compact Focus** (2)
- **Stringent Multi-Factor** (6)
- **Reentry Standards** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (7)
- **Commerce / Consumer Affairs** (6)
- **Professional Licensing Office** (2)
- **Labor & Regulation** (2)
- **Secretary of State** (2)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Standard of Care Parity** (5)
- **Controlled Substance Restrictions** (2)
- **Relationship & Consent Requirements** (3)
- **In-Person Follow-Up Required** (3)
- **Collaborative Practice Flexibility** (3)
- **Board Rules Pending** (2)
- **Broad Authorization** (2)

## Optometry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **OD Degree Required** (14)
- **Graduate of Accredited School** (14)
- **Graduate of Board-Approved School** (12)
- **Graduate + Min Years Specified** (8)
- **Board Standards / Equivalent** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Ophthalmologist-Supervised Internship** (1)
- **Optometry Internship** (1)
- **Supervised Clinical Experience** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~100 Hours** (1)
- **~6 Months** (1)
- **~1 Year** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **State Board of Optometry** (18)
- **Board of Examiners in Optometry** (12)
- **Named Optometry Board** (11)
- **Health Department / Agency** (9)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Optometry** (30)
- **Board of Examiners** (12)
- **Board of Registration** (2)
- **Optometry Examining Board** (1)
- **Non-Optometry Agency** (5)

#### Scope of Practice

`profession_specific.surgery_definition` — states per tag:

- **Broad Tissue-Based Definition** (10)
- **Invasive + Laser Named** (10)
- **Anesthesia-Based Threshold** (2)
- **Enumerated Exclusions List** (8)
- **Vague / Minimal Definition** (5)
- **Instrument + Closure Focused** (5)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (123, 48 states)
- **Criminal Conviction** (50, 42 states)
- **Incompetence & Negligence** (75, 44 states)
- **Substance Abuse & Impairment** (43, 36 states)
- **Physical & Mental Incapacity** (38, 31 states)
- **False or Deceptive Advertising** (44, 33 states)
- **Unlicensed Practice & License Misuse** (98, 43 states)
- **Unprofessional & Unethical Conduct** (119, 43 states)
- **Regulatory & Reporting Violations** (208, 49 states)

### Other bucketed fields

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ocular Disease & Pharmacology** (7)
- **TPA/Certified Licensees Only** (8)
- **Opioid/Substance Use Focus** (4)
- **Broad Optometry Topics** (1)
- **Glaucoma-Specific** (1)
- **Mixed Multi-Tier Requirements** (9)

#### Controlled substance schedule restrictions

`profession_specific.controlled_substance_schedule_restrictions` — items per tag:

- **Schedule I Prohibited** (15, 15 states)
- **Schedule II Prohibited** (13, 13 states)
- **Schedule II Hydrocodone Exception** (18, 18 states)
- **Schedule III-V Permitted With Limits** (11, 9 states)
- **Schedule III-V Analgesics Only** (8, 6 states)
- **All Controlled Substances Prohibited** (5, 4 states)
- **Drug Class Exclusions** (10, 9 states)
- **Supply Duration Limits** (11, 10 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACOE / AOA** (9)
- **Board Approved** (20)
- **US Dept of Education / CHEA** (4)
- **Regional / Professional Accreditor** (4)
- **Other Named Body** (1)

#### Laser procedures authorized

`profession_specific.laser_procedures_authorized` — items per tag:

- **Capsulotomy** (6, 6 states)
- **Trabeculoplasty** (5, 5 states)
- **Peripheral Iridotomy** (3, 3 states)
- **Diagnostic Laser Use** (4, 4 states)
- **Broad Laser Authority** (5, 4 states)
- **Other Laser Procedures** (3, 3 states)

#### Minor surgical procedures authorized

`profession_specific.minor_surgical_procedures_authorized` — items per tag:

- **Foreign Body Removal** (21, 16 states)
- **Corneal Procedures** (17, 10 states)
- **Eyelash Epilation** (14, 14 states)
- **Lacrimal System Procedures** (23, 14 states)
- **Eyelid Lesion Management** (18, 11 states)
- **Injections** (19, 9 states)
- **Light and Device Therapies** (6, 4 states)
- **Wound Repair and Suture** (5, 5 states)
- **General or Broad Authorization** (6, 6 states)

#### National association

`licensure.national_association` — states per tag:

- **National AOA** (8)
- **AOA Accreditation Body** (2)
- **State Optometric Assoc** (7)
- **Other National Body** (3)

#### National certification

`licensure.national_certification` — states per tag:

- **NBEO** (23)
- **NBEO (Alternate Label)** (1)
- **ARBO / CELMO** (1)
- **IABEO / NBEO** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (9)
- **Consumer Affairs** (3)
- **Professional Licensing Office** (7)
- **Commerce Dept** (3)
- **Labor & Regulation** (5)

#### Specialty certification types

`profession_specific.specialty_certification_types` — items per tag:

- **Diagnostic Pharmaceutical Agents** (17, 17 states)
- **Therapeutic Pharmaceutical Agents** (38, 37 states)
- **Glaucoma Treatment** (9, 8 states)
- **Oral Pharmaceutical Agents** (3, 3 states)
- **Laser / Surgical Procedures** (4, 4 states)
- **Advanced Scope Procedures** (7, 7 states)
- **Immunization / Injection** (3, 3 states)
- **Practice Setting / Other** (2, 2 states)

#### Tiered license types

`profession_specific.tiered_license_types` — items per tag:

- **Basic Optometrist License** (23, 23 states)
- **Diagnostic Pharmaceutical Certification** (12, 12 states)
- **Therapeutic Pharmaceutical Certification** (26, 24 states)
- **Glaucoma Specialist Certification** (5, 5 states)
- **Advanced Procedures Certification** (7, 7 states)
- **Limited or Specialty License** (8, 6 states)
- **Inactive or Volunteer License** (4, 3 states)

## Podiatry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **DPM Degree** (20)
- **DPM or Equivalent** (7)
- **Doctoral / Graduate Degree** (3)
- **Graduate of Accredited School** (11)
- **Diploma / Certificate** (4)
- **Four-Year Course** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Podiatric Residency** (19)
- **Residency Program** (3)
- **Residency or Preceptorship** (8)
- **Postgraduate Training** (9)
- **Residency or Active Practice** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (21)
- **2 Years** (3)
- **3 Years** (2)
- **Residency Required** (5)
- **Flexible / Conditional** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Podiatry Board** (29)
- **Medical Board** (13)
- **Health Department** (4)
- **Licensing Agency** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Podiatry Board** (14)
- **Podiatric Medicine Board** (10)
- **Podiatry Examiners Board** (10)
- **Medical Board** (13)
- **Other State Dept** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Med/Surg/Mech Core** (17)
- **Med/Surg/Mech + Electrical** (10)
- **Med/Surg/Mech + Manipulative** (1)
- **Diagnosis-Led Broad** (11)
- **Enumerated Procedures** (6)
- **General/All Means** (5)

`scope.drug_authority` — states per tag:

- **Full Rx + Controlled** (11)
- **Scope-Limited Rx** (11)
- **Local Anesthesia Only** (4)
- **Foot-Specific Drugs** (6)
- **Broad General Authority** (6)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (141, 47 states)
- **Criminal Conviction** (57, 42 states)
- **Negligence & Incompetence** (63, 37 states)
- **Substance Abuse & Impairment** (51, 42 states)
- **Physical & Mental Incapacity** (44, 34 states)
- **Unprofessional & Unethical Conduct** (146, 47 states)
- **Drug & Controlled Substance Violations** (51, 31 states)
- **Advertising Violations** (43, 37 states)
- **Regulatory & Administrative Violations** (218, 46 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Full Board Member** (1)
- **Advisory + Disciplinary** (2)
- **Advisory Only** (0)
- **Advisory + Rulemaking** (1)
- **Shared Administration** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Advisory Committee** (2)
- **Advisory Board** (1)
- **Joint Surgery Committee** (1)
- **Association Representatives** (1)

#### Board certification body

`profession_specific.board_certification_body` — items per tag:

- **ABFAS** (3, 3 states)
- **ABPS / Podiatric Surgery Board** (6, 6 states)
- **ABPM** (1, 1 states)
- **CPME Approved Board** (1, 1 states)
- **State-Recognized / Generic Body** (3, 3 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substances** (4)
- **Opioid + Addiction Treatment** (3)
- **Conditional Prescribers Only** (3)
- **Infection & Reporting** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **CPME / APMA** (17)
- **APMA Only** (6)
- **Council on Podiatry Education** (5)
- **State Board** (4)
- **Board-Approved Flexible** (9)

#### National association

`licensure.national_association` — states per tag:

- **APMA** (25)
- **CPME** (3)
- **American Podiatry Assoc** (5)
- **Multiple / Other** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NBPME / Exam Board** (12)
- **ABPS / Surgery Board** (6)
- **ABFAS Surgery Board** (2)
- **APMA / CPME Accreditation** (4)
- **Multiple Boards** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantially Equivalent Standards** (13)
- **Equivalent + Years of Practice** (9)
- **Equivalent + Mutual Reciprocity** (8)
- **Exam-Based Endorsement** (6)
- **Active License Only** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Health Dept** (7)
- **Consumer Affairs** (3)
- **Commerce Dept** (3)
- **Licensing & Regulation** (8)
- **Secretary of State** (2)
- **Labor Dept** (2)

## Public Accountancy

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Bach + 150hrs + Acctg Conc** (15)
- **Bach + 150hrs, No Conc** (10)
- **Bach + Acctg Conc, No 150hr** (16)
- **Bach Only / Minimal Req** (6)
- **Board Discretion** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Public Practice Only** (8)
- **Broad Skill List** (22)
- **Any Sector (Broad Skill List)** (7)
- **CPA-Supervised** (5)
- **Board Discretion** (1)
- **General Accounting** (7)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year Flat** (29)
- **2 Years Flat** (3)
- **1–2 Years (Edu-Based)** (8)
- **1–3+ Years (Tiered)** (5)
- **Hours-Based** (3)
- **Board Discretion** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Accountancy** (29)
- **Board of Public Accountancy** (11)
- **Board of CPA Examiners** (3)
- **Examining Board** (2)
- **State Department / Agency** (5)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Accountancy** (30)
- **Board of Public Accountancy** (12)
- **Board of CPAs** (2)
- **Examining Board** (2)
- **Dept / Other Agency** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Attest + Advisory + Tax** (28)
- **Attest + Compilation Only** (11)
- **Broad Accounting + Tax** (3)
- **Standards-Referenced** (2)
- **High-Level / Generic** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Obtaining License** (59, 44 states)
- **Dishonesty Fraud Negligence in Practice** (95, 45 states)
- **Criminal Conviction** (59, 41 states)
- **Out-of-State Discipline** (53, 44 states)
- **Agency Practice Revocation** (38, 36 states)
- **Violation of Rules or Standards** (137, 48 states)
- **CPE or Peer Review Failure** (21, 14 states)
- **Unauthorized Practice** (45, 21 states)
- **Fitness and Conduct** (60, 38 states)

### Other bucketed fields

#### Attest services types

`profession_specific.attest_services_types` — items per tag:

- **Audit (SAS)** (46, 46 states)
- **Review (SSARS)** (43, 43 states)
- **Compilation (SSARS)** (10, 10 states)
- **Examination of Prospective Info** (31, 31 states)
- **Attestation Engagements (SSAE)** (38, 35 states)
- **Agreed-Upon Procedures** (10, 10 states)
- **PCAOB Engagements** (34, 34 states)
- **Government Auditing** (4, 4 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ethics Only** (2)
- **Ethics + State Law** (1)
- **Accounting/Audit Core** (2)
- **Accounting + Ethics Mix** (2)
- **Broad Topic Menu** (1)
- **Attest Focus** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Regional Accreditor** (6)
- **Federal ED List** (6)
- **Board Discretion** (8)
- **Business Accreditor Included** (1)
- **State-Specific Body** (1)

#### National association

`licensure.national_association` — states per tag:

- **AICPA Only** (33)
- **AICPA + NASBA** (5)
- **AICPA + PCAOB** (3)
- **NASBA Only** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **AICPA Only** (11)
- **Uniform CPA Exam** (2)
- **AICPA + Uniform Exam** (1)
- **AICPA/NASBA Joint** (1)
- **Data Error** (1)

#### Practice privilege consent conditions

`profession_specific.practice_privilege_consent_conditions` — items per tag:

- **Jurisdiction and Disciplinary Authority** (50, 47 states)
- **Compliance with Laws and Rules** (48, 46 states)
- **Cessation if Home License Invalid** (42, 40 states)
- **Agent for Service of Process** (46, 46 states)
- **Notification and Reporting** (4, 3 states)
- **Scope of Practice Limits** (2, 2 states)
- **Other** (0, 0 states)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Commerce & Economic Dev** (3)
- **Professional Licensing Div** (6)
- **Business & Prof Regulation** (2)
- **Labor & Industry** (2)
- **Secretary of State** (2)
- **Office of Governor** (1)

#### Statute of limitations for accountant negligence

`profession_specific.statute_of_limitations_for_accountant_negligence` — states per tag:

- **1-Yr Discovery / 3-Yr Repose** (1)
- **2-Yr Discovery / 6-Yr Repose** (1)
- **2-Yr Board Discovery** (1)

