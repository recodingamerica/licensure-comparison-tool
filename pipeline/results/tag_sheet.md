# Field Tag Sheet

_Generated 2026-06-11T02:32:10+00:00_

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

- **DDS/DMD, CODA Accredited** (17)
- **DDS/DMD, Board Approved** (2)
- **DDS/DMD, No Accreditor Specified** (8)
- **Dental Graduate, CODA Accredited** (16)
- **Dental Graduate, Board Approved** (3)
- **Other Dental Credential** (2)

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

- **Board of Dental Examiners** (14)
- **Board of Dentistry** (26)
- **State Dept / Agency** (8)
- **Hybrid / Joint Authority** (1)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Dental Examiners** (15)
- **Board of Dentistry** (21)
- **Dental Board** (6)
- **Dental Commission/Other** (6)
- **Education Dept** (1)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad Enumerated List** (11)
- **Short General Terms** (10)
- **Surgical/Nonsurgical Framework** (13)
- **Detailed Procedural List** (9)
- **Minimal Catch-All** (4)

`scope.drug_authority` — states per tag:

- **Prescribe & Administer** (5)
- **Prescribe Only** (11)
- **Anesthesia + Prescribe** (10)
- **Controlled Substances Focus** (11)
- **Anesthesia Only** (4)
- **Vaccines Included** (2)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (127, 47 states)
- **Criminal Conviction** (57, 41 states)
- **Clinical Incompetence & Negligence** (69, 39 states)
- **Substance Abuse & Impairment** (123, 45 states)
- **Unprofessional Conduct** (113, 43 states)
- **Unlicensed Practice & Delegation** (92, 43 states)
- **False & Deceptive Advertising** (54, 35 states)
- **Fee Splitting & Billing Fraud** (56, 29 states)
- **Regulatory & Reporting Violations** (262, 47 states)

### Other bucketed fields

#### Advanced practice eligible patient populations

`profession_specific.advanced_practice_eligible_patient_populations` — items per tag:

- **Long-Term Care Residents** (37, 18 states)
- **School and Child Programs** (35, 17 states)
- **Homebound Individuals** (12, 11 states)
- **Correctional Facility Patients** (11, 6 states)
- **Community Health and Safety-Net Clinics** (46, 20 states)
- **Public Health Programs** (28, 19 states)
- **Low-Income and Underserved Populations** (18, 14 states)
- **Persons with Disabilities** (8, 6 states)

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advisory + Rulemaking Proposals** (1)
- **Advisory + Disciplinary Recs** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **State Dental Hygienists Committee** (2)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substances** (7)
- **Ethics & Law** (2)
- **Emergency & Safety** (2)
- **Broad Clinical Mix** (2)
- **Multi-Topic Required** (7)

#### Dental hygienist supervision levels

`profession_specific.dental_hygienist_supervision_levels` — items per tag:

- **Direct Supervision** (45, 42 states)
- **Indirect Supervision** (11, 11 states)
- **General Supervision** (41, 39 states)
- **Public Health Supervision** (8, 8 states)
- **Collaborative Practice** (4, 4 states)
- **Unsupervised Practice** (3, 3 states)
- **Other Supervision** (7, 6 states)

#### Dental therapist practice setting restrictions

`profession_specific.dental_therapist_practice_setting_restrictions` — items per tag:

- **Federally Qualified Health Centers** (7, 4 states)
- **Tribal and Indian Health Settings** (5, 3 states)
- **Public and Government Health Facilities** (7, 6 states)
- **Hospital and Medical Facilities** (5, 4 states)
- **School-Based Settings** (5, 4 states)
- **Nonprofit and Charitable Organizations** (5, 3 states)
- **Underserved Population Clinics** (8, 5 states)
- **Correctional Facilities** (2, 2 states)
- **Agreement-Defined Settings** (6, 5 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **CODA (full name)** (35)
- **CODA (abbreviation)** (7)
- **ADA only** (2)
- **Board-approved school** (2)
- **CODA or successor** (1)

#### Exams

`licensure.exams` — states per tag:

- **National + Clinical** (17)
- **National + Clinical + Jurisprudence** (12)
- **National + Regional** (7)
- **State Board Only** (4)
- **Board Discretion** (7)

#### National association

`licensure.national_association` — states per tag:

- **ADA** (33)
- **ADA with Accreditor** (3)
- **CODA Only** (1)
- **Other Association** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **National Board Exam** (3)
- **Specialty Board (ABOMS)** (1)
- **Multiple Bodies** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **5+ Yrs Practice Required** (13)
- **2–3 Yrs Practice Required** (4)
- **Hours-Based Threshold** (6)
- **Equivalent Standards + Good Standing** (4)
- **Exam-Heavy Requirements** (7)
- **Minimal / General Criteria** (4)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Health Dept** (7)
- **Consumer / Commerce** (5)
- **Licensing / Professional Reg** (8)
- **Labor & Industry** (2)

#### Sedation anesthesia permit types

`profession_specific.sedation_anesthesia_permit_types` — items per tag:

- **Minimal Sedation / Anxiolysis** (8, 8 states)
- **Moderate Sedation / Conscious Sedation** (35, 29 states)
- **Deep Sedation** (12, 12 states)
- **General Anesthesia** (28, 28 states)
- **Nitrous Oxide / Inhalation Analgesia** (2, 2 states)
- **Pediatric-Specific Authorization** (4, 2 states)
- **Combined / Unspecified Permit** (19, 16 states)

## Dietetics

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Bachelor's Min, Specific Major** (23)
- **Bachelor's Min, Any Field** (7)
- **Master's/Doctorate Required** (3)
- **Tiered by License Type** (5)
- **CDR Registration Proxy** (2)
- **Transitional Requirement** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Supervised Practice** (16)
- **Planned Continuous Program** (7)
- **Internship or Practice** (8)
- **Preprofessional Experience** (5)
- **General Experience** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **900 Hours** (21)
- **1,000 Hours** (3)
- **1,200 Hours** (1)
- **Multiple Pathways** (1)
- **Supervision-Based** (1)
- **Time-Based (Months)** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Dietetics Board** (18)
- **Medical/Physician Board** (6)
- **Health Department** (9)
- **Umbrella Licensing Agency** (4)
- **General Commerce/Prof Agency** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Dietetics Board** (19)
- **Medical/Health Board** (6)
- **Public Health Dept** (7)
- **General Licensing Dept** (8)
- **Other State Agency** (1)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad Assessment + Counseling** (11)
- **Clinical + Ordering Authority** (14)
- **Counseling + Care Plans** (7)
- **Science Domains Only** (2)
- **Basic Advisory Only** (2)

`scope.drug_authority` — states per tag:

- **Education Only** (1)
- **Counsel, No Alter** (1)
- **Protocol-Based Adjustments** (0)
- **Supplements + Protocol Adjustments** (2)

`scope.definition_quote` — states per tag:

- **Integration of Sciences Formula** (24)
- **Enumerated Services List** (7)
- **Medical Nutrition Therapy Focus** (5)
- **Counseling & Assessment Only** (2)
- **Regulatory/Authority Language** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Obtaining License** (33, 31 states)
- **Fraud or Deception in Practice** (34, 18 states)
- **Criminal Conviction** (40, 32 states)
- **Incompetence or Negligence** (28, 22 states)
- **Unprofessional or Unethical Conduct** (49, 29 states)
- **Impairment (Substance or Mental/Physical)** (37, 21 states)
- **Violation of Law or Board Order** (70, 37 states)
- **Discipline by Other Jurisdiction** (15, 13 states)
- **Aiding Unlicensed Practice or Other Misconduct** (14, 10 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advisory Only** (3)
- **Recommends on Licensing** (2)
- **Recommends on Rules & Discipline** (4)
- **Initiates Discipline** (1)
- **Proposes Rules (Required)** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Advisory Committee** (4)
- **Advisory Board/Group** (2)
- **Council** (2)
- **Practice Board** (1)
- **Allied Health Board** (1)
- **Standalone Board** (1)

#### Alternative credential pathways

`profession_specific.alternative_credential_pathways` — items per tag:

- **CNS Credential (BCNS)** (8, 8 states)
- **DACBN Diplomate** (6, 6 states)
- **ABN / AIN / ASCN Membership** (6, 2 states)
- **CDR / RD Registration** (2, 2 states)
- **Advanced Degree Pathway** (1, 1 states)
- **Reciprocity / Other State License** (1, 1 states)
- **General Department Discretion** (3, 2 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACEND / Dietetics-Specific** (9)
- **Regional Accreditor (Generic)** (7)
- **Named Regional Accreditor** (6)
- **Dual: ACEND + Regional** (3)
- **Federal DOE / CHEA** (7)
- **State / Other Body** (2)

#### Exams

`licensure.exams` — states per tag:

- **CDR Exam Only** (10)
- **CDR or Board-Approved** (11)
- **Board/State Exam** (9)
- **Multiple National Exams** (4)
- **Secretary/Dept Approved** (4)

#### Exempt professions list

`profession_specific.exempt_professions_list` — items per tag:

- **Other Licensed Health Professionals** (86, 29 states)
- **Students and Trainees** (29, 21 states)
- **Federal or Military Personnel** (19, 16 states)
- **Government or Public Agency Employees** (27, 21 states)
- **Dietetic Support Staff** (28, 19 states)
- **Food and Supplement Retailers** (26, 19 states)
- **General Nutrition Informers** (39, 21 states)
- **Weight Control Programs** (19, 18 states)
- **Religious or Traditional Practitioners** (7, 7 states)
- **Nonresident or Out-of-State Practitioners** (7, 7 states)

#### License type structure

`profession_specific.license_type_structure` — items per tag:

- **Licensed Dietitian** (23, 23 states)
- **Licensed Nutritionist** (10, 10 states)
- **Licensed Dietitian-Nutritionist** (11, 11 states)
- **Certified Dietitian or Nutritionist** (9, 6 states)
- **Dietetic Technician** (3, 3 states)
- **Provisional or Temporary License** (13, 12 states)
- **Title Protection Only** (2, 2 states)

#### National association

`licensure.national_association` — states per tag:

- **American Dietetic Assoc.** (15)
- **Academy of Nutrition & Dietetics** (8)
- **AND + ACEND** (4)
- **Multiple / Generic** (2)
- **State-Level Assoc.** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **CDR Only** (29)
- **CDR + Nutrition Specialists** (1)
- **CDR + Multiple Bodies** (5)
- **Board-Approved Body** (1)

#### Protected titles

`profession_specific.protected_titles` — items per tag:

- **Dietitian Title** (37, 29 states)
- **Nutritionist Title** (27, 15 states)
- **Combined Dietitian-Nutritionist Title** (9, 9 states)
- **Registered Credential** (16, 10 states)
- **Licensed Credential** (40, 27 states)
- **Certified Credential** (16, 9 states)
- **Provisional Credential** (3, 3 states)
- **Technician Specialist Title** (2, 2 states)
- **Abbreviation Only** (59, 29 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards** (18)
- **Equivalent + No Discipline** (5)
- **CDR Registration Accepted** (8)
- **Mutual Reciprocity Required** (2)
- **Board/Rule Discretion** (5)
- **Full Endorsement Criteria** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (5)
- **Professional Licensing Agency** (7)
- **Dept of Commerce/Labor** (3)
- **Consumer/Public Safety** (1)
- **Health & Human Services** (2)
- **Unique/Education Board** (1)

## Medicine

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **MD or DO** (18)
- **MD Only** (5)
- **Medical Degree (Broad)** (7)
- **Graduate of Med School** (11)
- **Accredited School + Foreign Pathway** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Residency Only** (17)
- **Residency or Internship** (12)
- **Residency, Internship, or Fellowship** (5)
- **General Postgrad Training** (9)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year Min** (7)
- **2 Years Min** (6)
- **3 Years Min** (2)
- **1–2 Yrs (Grad-Dependent)** (14)
- **2–3 Yrs (Origin-Dependent)** (4)
- **Board Discretion** (6)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **State Medical Board** (22)
- **Board of Examiners** (7)
- **Board of Licensure** (7)
- **Dept / Agency Umbrella** (9)
- **Composite / Healing Arts Board** (3)

`licensure.regulatory_authority.name` — states per tag:

- **Medical Board** (23)
- **Board of Examiners** (8)
- **Board of Licensure** (7)
- **Board of Practice/Registration** (3)
- **Healing Arts Board** (2)
- **Commission/Department** (3)
- **Combined Specialties Board** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Four** (13)
- **Broad + Modalities** (16)
- **Comprehensive Enumerated** (7)
- **High-Level Categories** (7)
- **Specialty Procedures** (1)

`scope.drug_authority` — states per tag:

- **Broad Full Authority** (7)
- **Standard with Opioid Limits** (6)
- **Standard with Rx Formalities** (6)
- **Delegation Emphasized** (3)
- **Basic Prescribing** (16)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (215, 46 states)
- **Criminal Conviction** (81, 40 states)
- **Negligence & Incompetence** (77, 42 states)
- **Substance Abuse & Impairment** (98, 43 states)
- **Unprofessional Conduct** (296, 47 states)
- **Drug Prescribing Violations** (98, 38 states)
- **Regulatory & Reporting Failures** (288, 47 states)
- **Sexual Misconduct** (27, 20 states)
- **Disciplinary Action Elsewhere** (54, 37 states)

### Other bucketed fields

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioids / Controlled Substances** (9)
- **Broad Multi-Topic Mandate** (8)
- **Specific Clinical Topic** (7)
- **Patient Safety & Ethics** (3)
- **Cultural & Social Competency** (0)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **LCME / AOA Only** (12)
- **LCME / AOA + Foreign** (6)
- **AMA / AAMC Based** (8)
- **ACGME / Grad Med Focus** (2)
- **Board Discretion** (11)
- **Federal / WHO Reference** (3)

#### Exams

`licensure.exams` — states per tag:

- **USMLE / COMLEX Required** (11)
- **National Exams (Multiple Options)** (13)
- **Board-Approved Exam** (15)
- **State-Administered Exam** (7)
- **USMLE + State Jurisprudence** (1)

#### License status types

`profession_specific.license_status_types` — items per tag:

- **Active Full License** (39, 32 states)
- **Inactive License** (30, 26 states)
- **Retired / Emeritus** (10, 10 states)
- **Temporary / Provisional** (38, 24 states)
- **Training / Resident Permit** (20, 19 states)
- **Limited / Restricted License** (33, 22 states)
- **Teaching / Academic License** (13, 10 states)
- **Administrative Medicine** (11, 11 states)
- **Volunteer / Pro Bono** (11, 11 states)

#### National association

`licensure.national_association` — states per tag:

- **AMA Only** (2)
- **AMA + AOA** (6)
- **AOA Only** (1)
- **AMA + AAMC** (2)
- **Accreditation Body** (2)
- **Specialty Boards** (5)
- **State Association Only** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NBME / NBEO / MCC** (4)
- **ECFMG** (6)
- **ABMS / AOA / Canadian Boards** (5)
- **Multi-Body Combination** (1)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Hard Day-Supply Cap** (7)
- **Dosage/MME Cap** (2)
- **Prescribing Standards Required** (2)
- **Board Rulemaking Authority** (5)
- **Narrow Scope Restriction** (4)
- **Protective/Permissive** (2)

#### Physician assistant prescriptive authority

`profession_specific.physician_assistant_prescriptive_authority` — states per tag:

- **Full Schedule II–V** (8)
- **Schedule III–V Only** (2)
- **Schedule II Limited** (4)
- **Board/Agreement Governed** (6)
- **Supervision/Delegation Required** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **IMLC Compact** (4)
- **Equivalent Standards** (18)
- **Exam Equivalency Focus** (10)
- **Experience + Good Standing** (7)
- **Broad Multi-Path** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (8)
- **Commerce / Consumer Affairs** (6)
- **Professional Licensing Agency** (5)
- **Education Dept** (1)
- **Labor & Industry** (2)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Prior In-Person Required** (6)
- **Same Standard as In-Person** (6)
- **Controlled Substance Restrictions** (7)
- **Licensure / Jurisdiction Focus** (12)
- **Flexible / Broad Allowance** (6)

## Nursing

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Approved Program Only** (20)
- **HS Diploma + Approved Program** (6)
- **Diploma/Degree from Approved Program** (12)
- **Tiered by License Type** (7)
- **Accredited Program Required** (4)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Transition to Practice** (2)
- **Supervised Practice** (1)
- **Collaborative Practice** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **~1,000–2,000 hrs** (1)
- **~2,000–2,500 hrs** (2)
- **4,600+ hrs / 3 yrs** (1)
- **Months-Based** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Nursing** (11)
- **State Board of Nursing** (10)
- **Named State Board** (22)
- **Dept / Agency (non-board)** (4)
- **Board + Dept Joint** (2)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Nursing** (11)
- **State Board of Nursing** (10)
- **Named State Board of Nursing** (21)
- **Board of Examiners** (2)
- **Board of Registration** (3)
- **Other Agency** (2)

#### Scope of Practice

`scope.drug_authority` — states per tag:

- **RN Administer Only** (16)
- **APRN Prescribe Independent** (6)
- **APRN Prescribe Collaborative** (6)
- **APRN Prescribe w/ Conditions** (7)
- **Mixed RN + APRN Tiers** (8)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Deception** (118, 46 states)
- **Criminal Conviction** (59, 42 states)
- **Substance Abuse & Impairment** (72, 41 states)
- **Incompetence & Negligence** (98, 44 states)
- **Unprofessional Conduct** (122, 41 states)
- **Mental/Physical Incapacity** (48, 36 states)
- **Law & Regulation Violation** (121, 47 states)
- **Prior Disciplinary Action** (40, 35 states)
- **Reporting & Cooperation Failures** (65, 26 states)

### Other bucketed fields

#### Aprn role categories

`profession_specific.aprn_role_categories` — items per tag:

- **Nurse Practitioner** (43, 43 states)
- **Nurse Anesthetist** (42, 42 states)
- **Nurse Midwife** (36, 36 states)
- **Clinical Nurse Specialist** (40, 40 states)
- **Psychiatric Mental Health CNS** (4, 4 states)
- **General APRN / Other** (3, 3 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Prescribing & Pharmacology** (6)
- **Abuse & Trafficking** (2)
- **Mental Health & Suicide** (1)
- **Bias & Cultural Competency** (1)
- **Mixed / Broad Requirements** (7)
- **Jurisprudence & Ethics** (1)

#### Controlled substance schedule authority

`profession_specific.controlled_substance_schedule_authority` — items per tag:

- **Schedule I** (2, 2 states)
- **Schedule II Unrestricted** (9, 9 states)
- **Schedule II With Restrictions** (12, 10 states)
- **Schedule III** (17, 16 states)
- **Schedule IV** (16, 16 states)
- **Schedule V** (16, 16 states)
- **Non-Controlled Drugs** (3, 2 states)
- **Multi-Schedule Bundled** (8, 6 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **State Board Only** (11)
- **National Accreditor** (2)
- **State Board + National** (5)
- **Federal DOE Reference** (6)
- **Named Agency (ACEN/CCNE)** (1)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Registered Nurse (RN)** (53, 49 states)
- **Licensed Practical Nurse (LPN/LVN)** (47, 47 states)
- **Advanced Practice RN (APRN)** (36, 33 states)
- **Nurse Practitioner (NP/CNP)** (22, 20 states)
- **Nurse Anesthetist (CRNA)** (21, 21 states)
- **Nurse Midwife (CNM)** (16, 16 states)
- **Clinical Nurse Specialist (CNS)** (20, 20 states)
- **Nursing Assistant / Aide** (9, 7 states)
- **Medication Aide / Other Support** (8, 7 states)

#### Lpn supervision requirements

`profession_specific.lpn_supervision_requirements` — items per tag:

- **Registered Nurse** (47, 44 states)
- **Advanced Practice Registered Nurse** (16, 16 states)
- **Physician** (41, 37 states)
- **Physician Assistant** (8, 8 states)
- **Dentist** (32, 32 states)
- **Podiatrist** (14, 14 states)
- **Other Eye/Spine Specialist** (5, 5 states)
- **General Licensed Practitioner** (21, 20 states)

#### National association

`licensure.national_association` — states per tag:

- **ANA / General Nursing** (3)
- **Advanced Practice Specialty** (3)
- **Nurse Anesthesia** (1)
- **State-Level Body** (1)
- **Accreditation / Exam Board** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCLEX Exam Body** (4)
- **APRN Specialty Cert** (4)
- **Board-Approved Certifier** (5)
- **Named Org (non-NCLEX)** (2)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Short Supply Cap** (6)
- **MME/Dose Limit** (2)
- **Dispense Prohibition** (1)
- **Physician Oversight Required** (3)
- **Broad Discretionary Rules** (2)
- **Process & Evaluation Requirements** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Compact / Multistate** (4)
- **Substantially Equivalent** (12)
- **Meet State Qualifications** (19)
- **Active Practice Required** (6)
- **Enhanced Requirements** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (7)
- **Consumer / Commerce** (6)
- **Professional Licensing** (4)
- **Labor & Industry** (2)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Standard of Care Parity** (5)
- **Prescribing Rules Detailed** (5)
- **Consent & Confidentiality** (2)
- **In-Person Visit Required** (1)
- **Board Rules Pending** (2)
- **Scope & Definition Only** (3)

## Optometry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **OD + Accredited School** (17)
- **Graduate of Accredited School** (14)
- **OD + Board-Approved School** (3)
- **Graduate of Board-Approved School** (9)
- **Vague / Non-Standard** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Optometry Internship** (1)
- **Ophthalmology Supervised** (1)
- **Clinical Experience** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **Hours-Based** (1)
- **Months-Based** (1)
- **Years-Based** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Optometry Board** (27)
- **Board of Examiners** (12)
- **Board of Registration** (2)
- **State Health Dept** (4)
- **Other State Agency** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Optometry** (30)
- **Board of Examiners** (13)
- **Board of Registration** (2)
- **Non-Dedicated Agency** (4)

#### Scope of Practice

`profession_specific.surgery_definition` — states per tag:

- **Broad Tissue-Alteration Definition** (6)
- **Instrument & Method List** (9)
- **Invasive Procedure (Simple)** (3)
- **Defined by Exclusions** (1)
- **Partial Scope Granted** (2)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (127, 47 states)
- **Criminal Conviction** (47, 39 states)
- **Clinical Incompetence** (64, 41 states)
- **Substance Abuse** (35, 32 states)
- **Unprofessional Conduct** (105, 42 states)
- **Unlicensed Practice** (71, 38 states)
- **False Advertising** (48, 33 states)
- **Regulatory Violation** (218, 46 states)
- **Impairment & Health** (34, 28 states)

### Other bucketed fields

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ocular Pharmacology/Disease** (13)
- **Opioid/Pain Management** (4)
- **Broad Multi-Topic Mix** (4)
- **Jurisprudence/Admin** (1)
- **Substance Use Screening** (1)

#### Controlled substance schedule restrictions

`profession_specific.controlled_substance_schedule_restrictions` — items per tag:

- **Schedule I Prohibited** (16, 16 states)
- **Schedule II Prohibited** (13, 13 states)
- **Schedule II Hydrocodone Exception** (18, 18 states)
- **Schedule III–V Permitted With Limits** (11, 8 states)
- **Supply Duration Limit** (11, 9 states)
- **Non-Controlled Drug Exclusion** (16, 6 states)
- **Statutory Code Reference** (5, 1 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACOE / AOA** (9)
- **State Board Approval** (16)
- **Federal / CHEA Recognition** (5)
- **Regional Accreditation** (2)
- **Other Optometry Body** (1)

#### Exams

`licensure.exams` — states per tag:

- **NBEO Only** (13)
- **NBEO + State Jurisprudence** (4)
- **NBEO + State Exam** (2)
- **State Board Only** (14)
- **National/Board-Approved** (14)
- **State Board + Jurisprudence** (2)

#### Laser procedures authorized

`profession_specific.laser_procedures_authorized` — items per tag:

- **Capsulotomy (YAG)** (6, 6 states)
- **Trabeculoplasty** (5, 5 states)
- **Peripheral Iridotomy** (3, 3 states)
- **Refractive Laser Surgery** (1, 1 states)
- **Diagnostic Laser Use** (2, 2 states)
- **Therapeutic Laser (Broad)** (3, 2 states)
- **Light Therapy (IPL/LLLT)** (2, 1 states)
- **Broad Scope With Exclusions** (3, 3 states)

#### Minor surgical procedures authorized

`profession_specific.minor_surgical_procedures_authorized` — items per tag:

- **Epilation / Lash Removal** (13, 13 states)
- **Corneal Procedures** (12, 8 states)
- **Lacrimal System Procedures** (20, 11 states)
- **Injections** (15, 8 states)
- **Eyelid Lesion Excision** (15, 9 states)
- **Foreign Body Removal** (9, 7 states)
- **Eyelid Repair / Surgery** (5, 5 states)
- **Light / Energy Therapy** (4, 3 states)
- **Diagnostic / Specimen Collection** (11, 6 states)

#### National association

`licensure.national_association` — states per tag:

- **AOA Only** (5)
- **AOA + Accreditation Body** (1)
- **AOA + Multiple Orgs** (1)
- **Accreditation Body Only** (1)
- **Other Board/Council** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NBEO** (11)
- **NBEO – TMOD Exam** (2)
- **NBPME** (1)
- **IABEO** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards Only** (12)
- **Equivalent + Active Practice** (4)
- **Equivalent + Practice + Exam** (4)
- **Comprehensive Multi-Requirement** (18)
- **Portability / Endorsement Framework** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Health Dept** (8)
- **Commerce / Consumer Affairs** (5)
- **Professional Licensing Agency** (5)
- **Labor & Industry** (2)
- **Secretary of State** (1)

#### Specialty certification types

`profession_specific.specialty_certification_types` — items per tag:

- **Diagnostic Pharmaceutical Agents** (9, 9 states)
- **Topical Therapeutic Agents** (21, 20 states)
- **Oral Pharmaceutical Agents** (7, 7 states)
- **Injectable Agents** (2, 2 states)
- **Glaucoma Specialty Certification** (3, 3 states)
- **Advanced Procedures Certification** (3, 3 states)
- **No Pharmaceutical Use** (1, 1 states)
- **Immunization Certification** (1, 1 states)

#### Tiered license types

`profession_specific.tiered_license_types` — items per tag:

- **Basic License** (15, 15 states)
- **Diagnostic Pharmaceutical Authority** (7, 7 states)
- **Therapeutic Pharmaceutical Authority** (16, 16 states)
- **Expanded Therapeutic Authority** (3, 3 states)
- **Glaucoma Specialist** (3, 3 states)
- **Advanced Procedures** (4, 4 states)
- **Limited Or Special Purpose License** (1, 1 states)

## Podiatry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **DPM Degree** (22)
- **DPM or Equivalent** (7)
- **Accredited School Graduate** (11)
- **Diploma/Certificate** (4)
- **Four-Year Course** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Podiatric Residency** (19)
- **Residency Program** (3)
- **Residency or Preceptorship** (6)
- **Residency or Fellowship** (2)
- **General Postgraduate Training** (9)
- **Residency or Active Practice** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (21)
- **2 Years** (3)
- **3 Years** (2)
- **Residency Required** (5)
- **Flexible / Conditional** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Podiatry Board** (27)
- **Medical Board** (12)
- **State Health Dept** (4)
- **Multi-Profession Board** (2)
- **Education/Licensing Dept** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Podiatry-Specific Board** (14)
- **Podiatric Medicine Board** (10)
- **Medical Board (Shared)** (13)
- **Examiners Board** (10)
- **Other State Agency** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Med / Surg / Mech Core** (15)
- **Med / Surg / Mech + Electrical** (2)
- **Med / Surg / Mech + Manipulative** (1)
- **Med / Surg / Mech + Manipulative + Electrical** (9)
- **Med / Surg + Diagnosis + Extras** (12)
- **Broad / Enumerated Detail** (8)
- **General / All Means** (2)

`scope.drug_authority` — states per tag:

- **Broad / Full Prescriptive** (5)
- **Scope-Limited Prescribing** (15)
- **Controlled Substances Explicit** (9)
- **Local Anesthesia Only** (3)
- **Restricted / Conditional** (5)

`scope.definition_quote` — states per tag:

- **Foot Only** (10)
- **Foot & Ankle** (24)
- **Foot, Ankle & Leg** (12)
- **Broad / Primary Care** (2)
- **Title-Based Definition** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (122, 45 states)
- **Criminal Conviction** (58, 40 states)
- **Negligence & Incompetence** (54, 34 states)
- **Substance Abuse & Impairment** (50, 40 states)
- **Physical or Mental Incapacity** (45, 33 states)
- **Unprofessional & Immoral Conduct** (99, 44 states)
- **Drug Prescribing Violations** (45, 30 states)
- **Advertising Violations** (43, 36 states)
- **Regulatory & Administrative Violations** (151, 44 states)
- **Aiding Unlicensed Practice** (33, 29 states)
- **Scope of Practice Violations** (16, 14 states)
- **Financial Misconduct** (41, 22 states)
- **Discipline in Another Jurisdiction** (31, 27 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Full Board Status** (1)
- **Advisory + Rulemaking** (2)
- **Advisory + Disciplinary** (0)
- **Broad Advisory Role** (1)
- **Disciplinary Only** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Advisory Committee** (2)
- **Advisory Board** (1)
- **Joint Advisory Committee** (1)
- **Association Representatives** (1)

#### Board certification body

`profession_specific.board_certification_body` — items per tag:

- **ABFAS** (3, 3 states)
- **ABPS / Podiatric Surgery Board** (6, 6 states)
- **ABPM** (1, 1 states)
- **CPME-Approved Board** (1, 1 states)
- **Generic / Approved Body** (3, 3 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substance Prescribing** (5)
- **Substance Use & Treatment** (1)
- **Conditional on Prescribing** (3)
- **Multi-Topic Requirement** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **CPME / APMA** (16)
- **APMA Only** (6)
- **Council on Podiatry Education** (6)
- **State Board** (4)
- **Board-Approved Flexible** (9)

#### National association

`licensure.national_association` — states per tag:

- **APMA** (25)
- **CPME** (2)
- **American Podiatry Assoc** (4)
- **Multiple / Combined** (2)
- **State-Specific Body** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NBPME** (13)
- **ABPS / ABFAS** (7)
- **ABFAS + ABPM (Dual)** (1)
- **CPME / APMA** (3)
- **Specialty Board (General)** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards Only** (19)
- **Equivalent + Years of Practice** (9)
- **Equivalent + Reciprocal Privilege** (3)
- **Equivalent + Practice + Reciprocal** (4)
- **Multi-Factor / Complex** (4)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (7)
- **Consumer Affairs** (3)
- **Commerce / Economic Dev** (3)
- **Professional Licensing Dept** (8)
- **Labor & Industry** (2)
- **Secretary of State / Education** (2)

## Public Accountancy

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Bach + 150 hrs + Accounting** (14)
- **Bach + Accounting Concentration** (16)
- **Bach + 150 hrs (No Concentration)** (9)
- **Bach Degree Only** (6)
- **Board Discretion** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Broad Service List** (23)
- **Public Practice Only** (8)
- **General Accounting** (7)
- **CPA-Supervised** (4)
- **Multi-Sector Broad** (6)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year Flat** (29)
- **1–2 Years (Degree-Dependent)** (7)
- **2 Years** (3)
- **2+ Years / Tiered** (4)
- **Hours-Based** (3)
- **Board Discretion** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Accountancy** (27)
- **Board of Public Accountancy** (11)
- **CPA/Examiner Board** (5)
- **State Dept / Agency** (5)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Accountancy** (28)
- **Board of Public Accountancy** (11)
- **Board of CPA Examiners** (2)
- **Board of Accountants** (4)
- **Education Department** (1)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Attest + Advisory + Tax** (27)
- **Attest + Compilation Only** (12)
- **Attest + Compilation + Tax** (0)
- **Broad Full Spectrum** (3)
- **High-Level Summary** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Obtaining License** (54, 40 states)
- **Dishonesty/Fraud/Negligence in Practice** (79, 43 states)
- **Criminal Conviction** (53, 38 states)
- **Out-of-State/Agency Discipline** (86, 43 states)
- **Violation of Rules/Standards** (83, 42 states)
- **Unauthorized/Unlicensed Practice** (42, 18 states)
- **Fitness/Conduct Issues** (57, 38 states)
- **CPE/Peer Review Failure** (19, 13 states)
- **Admin/Compliance Failure** (53, 29 states)

### Other bucketed fields

#### Attest services types

`profession_specific.attest_services_types` — items per tag:

- **Audit (SAS)** (44, 44 states)
- **Review (SSARS)** (41, 41 states)
- **Compilation (SSARS)** (10, 10 states)
- **Prospective Financial Examination (SSAE)** (30, 30 states)
- **Attestation / Agreed-Upon Procedures (SSAE)** (40, 38 states)
- **PCAOB Engagement** (31, 31 states)
- **Government Auditing** (3, 3 states)
- **Other Assurance Services** (6, 6 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ethics Only** (3)
- **Technical + Ethics** (3)
- **Technical Subjects Only** (2)
- **Broad Subject List** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Regional Accreditor** (7)
- **Federal ED List** (4)
- **Board Approved** (8)
- **Named Business Accreditor** (1)
- **State-Specific Body** (1)

#### Exams

`licensure.exams` — states per tag:

- **CPA Exam Only** (37)
- **CPA + Ethics Exam** (8)
- **CPA + Ethics + State Exam** (1)
- **State-Administered Exam** (2)

#### National association

`licensure.national_association` — states per tag:

- **AICPA Only** (31)
- **AICPA + NASBA** (4)
- **AICPA + PCAOB** (3)
- **State Society Only** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **AICPA (Org Only)** (12)
- **Uniform CPA Exam** (2)
- **AICPA + Exam Named** (1)
- **Erroneous/Mismatch** (1)

#### Practice privilege consent conditions

`profession_specific.practice_privilege_consent_conditions` — items per tag:

- **Jurisdiction and Disciplinary Authority** (46, 44 states)
- **Compliance with Laws and Rules** (44, 43 states)
- **Cease Practice if License Invalid** (40, 38 states)
- **Agent for Service of Process** (43, 43 states)
- **Reporting and Notification Obligations** (4, 3 states)
- **Cooperation with Investigations** (1, 1 states)
- **Scope of Practice Limitations** (2, 2 states)
- **Other Conditions** (0, 0 states)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Commerce / Consumer Affairs** (4)
- **Professional Licensing Division** (6)
- **Business & Professional Reg.** (2)
- **Labor & Industry** (2)
- **Secretary of State Office** (1)

#### Statute of limitations for accountant negligence

`profession_specific.statute_of_limitations_for_accountant_negligence` — states per tag:

- **1-Year Discovery / 3-Year Absolute** (1)
- **2-Year Discovery / 6-Year Absolute** (1)
- **2-Year Discovery Only** (1)

