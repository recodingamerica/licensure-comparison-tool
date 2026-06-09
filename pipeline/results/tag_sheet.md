# Field Tag Sheet

_Generated 2026-06-09T17:19:23+00:00_

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

`licensure.disciplinary_grounds` — grounds per tag:

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

`profession_specific.advanced_practice_eligible_patient_populations` — states per tag:

- **Broad Facility List** (16)
- **Underserved & Income-Based** (3)
- **Specific Vulnerable Groups** (3)
- **Public Health Settings** (8)
- **General Public / Minimal Restriction** (1)

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

`profession_specific.dental_hygienist_supervision_levels` — states per tag:

- **Direct + General Only** (19)
- **Direct + General + Indirect** (10)
- **Includes Unsupervised/Public Health** (10)
- **Includes Collaborative/Independent** (6)
- **Single Level Only** (2)

#### Dental therapist practice setting restrictions

`profession_specific.dental_therapist_practice_setting_restrictions` — states per tag:

- **Enumerated Underserved Sites** (3)
- **Broad Enumerated Settings** (3)
- **Agreement-Defined Settings** (3)
- **Tribal / Federal Focus** (1)

#### Disciplinary grounds

`licensure.disciplinary_grounds` — states per tag:

- **Enumerated Specific Grounds** (28)
- **Broad Unprofessional Conduct** (5)
- **Hybrid Specific + Catch-All** (10)
- **Criminal-Centric Focus** (4)
- **Impairment-Forward** (2)

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

`profession_specific.sedation_anesthesia_permit_types` — states per tag:

- **2-Tier System** (13)
- **3-Tier System** (12)
- **4-Tier System** (5)
- **5+ Tier System** (2)
- **Broad/Generic Only** (3)
- **Pediatric Distinctions** (2)

## Dietetics

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Bachelor's Min** (7)
- **Bachelor's + Field Specified** (23)
- **Master's/Doctoral Required** (2)
- **Tiered by License Type** (6)
- **Transitioning to Master's** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Supervised Practice** (19)
- **Internship or Supervised Practice** (8)
- **Planned Preprofessional Program** (9)
- **General Work Experience** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **900 Hours** (21)
- **1,000 Hours** (3)
- **1,200 Hours** (1)
- **Time-Based** (1)
- **Tiered / Multiple Paths** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Dietetics Board** (18)
- **General Health Board** (2)
- **Medical Board** (6)
- **State Health Dept** (8)
- **General Licensing Agency** (7)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Dietetics Board** (19)
- **Medical/Health Board** (6)
- **Public Health Agency** (8)
- **General Licensing Agency** (8)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad Clinical + Ordering** (10)
- **Standard Full Scope** (13)
- **Assessment + Counseling Only** (7)
- **Medical Nutrition Therapy Focus** (3)
- **Narrow / Advisory Only** (2)

`scope.drug_authority` — states per tag:

- **Education Only** (1)
- **Protocol-Based Adjustments** (0)
- **Order & Discontinue Supplements** (2)

`scope.definition_quote` — states per tag:

- **Sciences Integration** (14)
- **Sciences + Life Cycle** (9)
- **Sciences + Services List** (8)
- **MNT Focused** (5)
- **Counseling / Advisory** (2)
- **Regulatory / Administrative** (1)

#### Discipline

`licensure.disciplinary_grounds` — grounds per tag:

- **Fraud / Misrepresentation** (69, 34 states)
- **Criminal Conviction** (43, 33 states)
- **Incompetence / Negligence** (26, 20 states)
- **Unprofessional / Unethical Conduct** (46, 30 states)
- **Substance Abuse / Impairment** (20, 17 states)
- **Mental / Physical Incapacity** (18, 13 states)
- **Regulatory Violation** (74, 39 states)
- **Aiding Unlicensed Practice** (13, 9 states)
- **Prior Disciplinary Action** (14, 12 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advisory Only** (3)
- **Recommends to Board** (4)
- **Consulted on Licensing & Rules** (2)
- **Initiates Disciplinary Action** (1)
- **Proposes Binding Rules** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Advisory Committee** (3)
- **Advisory Board/Group** (2)
- **Council** (2)
- **Standalone Board** (2)
- **Allied Health Board** (1)

#### Alternative credential pathways

`profession_specific.alternative_credential_pathways` — states per tag:

- **CNS / DACBN Credentials** (7)
- **Professional Society Membership** (2)
- **Academic Degree Route** (1)
- **National Registry Accepted** (1)
- **Single Cert Body** (2)

#### Disciplinary grounds

`licensure.disciplinary_grounds` — states per tag:

- **Enumerated Specific Grounds** (21)
- **Broad Unprofessional Conduct** (11)
- **Statute/Rule Violation Focus** (4)
- **Cross-Reference Only** (3)
- **Narrow/Single Ground** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACEND / Dietetics-Specific** (13)
- **Regional Accreditation (Generic)** (7)
- **Named Regional Body** (6)
- **Federal / CHEA Reference** (5)
- **State / Dept Authority** (2)

#### Exempt professions list

`profession_specific.exempt_professions_list` — states per tag:

- **Broad Multi-Category** (23)
- **Other Licensed Professions** (6)
- **Narrow / Specific** (3)
- **Supervised Roles + Students** (0)
- **Government & Federal Only** (0)

#### License type structure

`profession_specific.license_type_structure` — states per tag:

- **Dietitian Only** (9)
- **Dietitian + Nutritionist** (13)
- **Dietitian + Provisional** (9)
- **Multi-Tier + Provisional** (4)
- **Certified (not Licensed)** (5)
- **Technician Tier Included** (2)

#### National association

`licensure.national_association` — states per tag:

- **American Dietetic Assoc.** (15)
- **Academy of Nutrition & Dietetics** (11)
- **Multiple / Dual Orgs** (2)
- **Generic / Unspecified** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **CDR Only** (29)
- **CDR + Nutrition Specialists** (1)
- **CDR + Multiple Bodies** (5)
- **Board-Approved Body** (1)

#### Protected titles

`profession_specific.protected_titles` — states per tag:

- **Dietitian Only** (15)
- **Dietitian + Nutritionist** (11)
- **Dietitian/Nutritionist Hyphenated** (6)
- **Certified Titles** (5)
- **Broad Scope (Many Titles)** (4)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards** (24)
- **CDR Registration Accepted** (8)
- **Mutual/Agreement Required** (2)
- **Board Discretion** (2)
- **Detailed Multi-Factor** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Health Department** (7)
- **Professional Licensing Agency** (8)
- **Consumer Affairs / Commerce** (2)
- **Education / Regents** (1)
- **Labor / Other** (2)

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

`licensure.disciplinary_grounds` — grounds per tag:

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

#### Disciplinary grounds

`licensure.disciplinary_grounds` — states per tag:

- **Broad Enumerated List** (21)
- **Fraud & Misrepresentation Focus** (10)
- **Conduct & Ethics Focus** (7)
- **Criminal Conviction Focus** (2)
- **Impairment Focus** (2)
- **Catch-All Unprofessional Conduct** (5)

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

`profession_specific.license_status_types` — states per tag:

- **Basic (3–4 types)** (11)
- **Moderate (5–7 types)** (15)
- **Expanded (8–11 types)** (6)
- **Comprehensive (12+ types)** (1)

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

`licensure.disciplinary_grounds` — grounds per tag:

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

`profession_specific.aprn_role_categories` — states per tag:

- **All 4 APRN Roles** (32)
- **4 Roles + Extra** (4)
- **3 Roles Only** (4)
- **2 Roles Only** (3)
- **Partial / Non-Standard** (2)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Prescribing & Pharmacology** (6)
- **Abuse & Trafficking** (2)
- **Mental Health & Suicide** (1)
- **Bias & Cultural Competency** (1)
- **Mixed / Broad Requirements** (7)
- **Jurisprudence & Ethics** (1)

#### Controlled substance schedule authority

`profession_specific.controlled_substance_schedule_authority` — states per tag:

- **Full II–V** (11)
- **II–V With Restrictions** (7)
- **III–V Only** (1)
- **Limited/Partial II** (2)
- **Role-Differentiated** (3)

#### Disciplinary grounds

`licensure.disciplinary_grounds` — states per tag:

- **Broad Multi-Ground List** (16)
- **Fraud + Crime + Competence** (18)
- **Fraud + Crime Core** (4)
- **Competence & Conduct Focus** (3)
- **Rules & Standards Focus** (7)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **State Board Only** (11)
- **National Accreditor** (2)
- **State Board + National** (5)
- **Federal DOE Reference** (6)
- **Named Agency (ACEN/CCNE)** (1)

#### Lpn supervision requirements

`profession_specific.lpn_supervision_requirements` — states per tag:

- **RN + MD + Dentist (Core)** (14)
- **Core + APRN** (10)
- **Core + APRN + PA/Other** (7)
- **Broad Multi-Provider** (9)
- **General Licensed Provider** (6)

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

`licensure.disciplinary_grounds` — grounds per tag:

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

`profession_specific.controlled_substance_schedule_restrictions` — states per tag:

- **Sched I–II Banned** (6)
- **Sched I–II Banned, Hydrocodone Excepted** (9)
- **Sched II Banned, Hydrocodone Excepted** (5)
- **Partial Schedules, Supply Limits** (4)
- **Specific Drug Limits Only** (4)
- **Broad Prohibition + Extra Exclusions** (5)

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

`profession_specific.specialty_certification_types` — states per tag:

- **Diagnostic Only** (0)
- **Diagnostic + Therapeutic** (7)
- **Therapeutic Only** (5)
- **Expanded Scope / Oral + Systemic** (6)
- **Specialty Procedure Cert** (4)

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

`licensure.disciplinary_grounds` — grounds per tag:

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

`profession_specific.board_certification_body` — states per tag:

- **ABPS Only** (6)
- **ABFAS Only** (2)
- **ABFAS + ABPM** (1)
- **CPME-Approved Board** (1)
- **Any Recognized Board** (3)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substance Prescribing** (5)
- **Substance Use & Treatment** (1)
- **Conditional on Prescribing** (3)
- **Multi-Topic Requirement** (2)

#### Disciplinary grounds

`licensure.disciplinary_grounds` — states per tag:

- **Fraud & Misrepresentation** (3)
- **Criminal Conviction** (0)
- **Negligence & Incompetence** (2)
- **Substance Abuse & Impairment** (4)
- **Unprofessional Conduct** (3)
- **Broad Multi-Ground Statute** (36)

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

`licensure.disciplinary_grounds` — grounds per tag:

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

`profession_specific.attest_services_types` — states per tag:

- **Full Standards List** (14)
- **Broad + PCAOB** (13)
- **Broad, No PCAOB** (4)
- **Includes Compilation** (9)
- **Concise / High-Level** (5)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ethics Only** (3)
- **Technical + Ethics** (3)
- **Technical Subjects Only** (2)
- **Broad Subject List** (1)

#### Disciplinary grounds

`licensure.disciplinary_grounds` — states per tag:

- **Fraud/Deceit Core List** (23)
- **Broad Statutory Violation** (6)
- **Criminal Conviction Focus** (3)
- **Unauthorized Practice/Title** (3)
- **Mixed/Comprehensive List** (12)

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

