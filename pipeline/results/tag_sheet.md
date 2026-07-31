# Field Tag Sheet

_Generated 2026-07-31T16:43:27+00:00_

Plain-English tags for each profession's key licensure fields, derived
by `pipeline.map_prep.bucket_text` (no per-row hand-curation — the LLM
clustered each field's actual state values into a handful of buckets).
Counts are states per tag (or disciplinary grounds per tag, for the
Discipline field). Scope wording is profession-specific, so the bucketed
field name varies by profession.

## Anesthesiologist Assistant

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Apiarist

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Applied Behavior Analysis

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Architecture

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **NAAB Accredited Degree** (9)
- **Accredited Degree (General)** (11)
- **NAAB or Board Equivalent** (7)
- **Experience May Substitute** (4)
- **Board-Defined Requirements** (7)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Named NCARB Program** (5)
- **Supervised Practical Experience** (5)
- **General Practical Experience** (15)
- **Diversified Training** (2)
- **Structured/Internship Program** (6)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (1)
- **2 Years** (1)
- **3 Years** (2)
- **8 Years Combined** (3)
- **Flexible / Up to 10 Years** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Architects-Only Board** (19)
- **Architects + Design Professions Board** (10)
- **Architects + Engineers Board** (5)
- **State Dept / Agency** (2)
- **Multi-Board / Shared Authority** (3)

`licensure.regulatory_authority.name` — states per tag:

- **Architects Only Board** (21)
- **Architects + Landscape Architects** (4)
- **Architects + Interior Design** (7)
- **Multi-Profession Board** (5)
- **Dept / Division (Non-Board)** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Minimal Core** (5)
- **Standard Scope** (20)
- **Extended Scope** (7)
- **Comprehensive Scope** (5)

`scope.definition_quote` — states per tag:

- **Design + Construction Services** (15)
- **Design + Safety/Welfare Focus** (7)
- **Broad Professional Services** (8)
- **Services + Enumerated List** (6)
- **Reference Only** (2)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Licensure** (43, 38 states)
- **Negligence or Incompetence** (78, 39 states)
- **Criminal Conviction** (34, 32 states)
- **Improper Seal Use** (35, 28 states)
- **Aiding Unauthorized Practice** (25, 23 states)
- **Substance Abuse or Impairment** (18, 12 states)
- **False Advertising or Misrepresentation** (50, 24 states)
- **Out-of-State Disciplinary Action** (27, 23 states)
- **Statutory or Rule Violation** (119, 45 states)
- **Conflict of Interest or Financial Misconduct** (21, 13 states)

### Other bucketed fields

#### Continuing education excluded topics

`profession_specific.continuing_education_excluded_topics` — items per tag:

- **DEI Ideology Restrictions** (3, 1 states)
- **Business Practice Topics** (2, 1 states)

#### Continuing education subject requirement

`profession_specific.continuing_education_subject_requirement` — items per tag:

- **Health Safety Welfare** (7, 7 states)
- **Building Codes** (1, 1 states)
- **Sustainability Energy** (1, 1 states)
- **Accessibility** (1, 1 states)
- **Professional Ethics** (1, 1 states)
- **General Professional Practice** (3, 2 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Health, Safety & Welfare** (5)
- **State Code / Law Specific** (1)
- **Multiple Specific Topics** (1)

#### Continuing education waiver conditions

`profession_specific.continuing_education_waiver_conditions` — items per tag:

- **Military Service** (5, 5 states)
- **Illness or Disability** (7, 6 states)
- **Hardship or Emergency** (6, 5 states)
- **Retirement or Inactive Status** (4, 4 states)
- **New Licensee First Renewal** (3, 3 states)
- **Age-Based Exemption** (2, 2 states)
- **Board Discretionary Waiver** (6, 6 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **NAAB Only** (18)
- **NAAB + CACB** (2)
- **NAAB (loose wording)** (2)
- **Board-Approved** (2)
- **Generic National Body** (4)

#### Exams

`licensure.exams` — states per tag:

- **NCARB/ARE Mandated** (14)
- **NCARB/ARE Adoptable** (10)
- **Board-Prescribed Exam** (12)
- **State Exam + NCARB Option** (3)

#### Exempt building types

`profession_specific.exempt_building_types` — items per tag:

- **Single Family Residential** (23, 23 states)
- **Small Multifamily Residential** (35, 32 states)
- **Agricultural Buildings** (35, 35 states)
- **Small Commercial Industrial** (39, 26 states)
- **Alterations Repairs** (30, 25 states)
- **Accessory Outbuildings** (12, 11 states)
- **Preengineered Buildings** (8, 8 states)
- **Owner Built Private Use** (12, 10 states)
- **Other Exempt** (26, 17 states)

#### Firm design professional ownership minimum fraction

`profession_specific.firm_design_professional_ownership_minimum_fraction` — states per tag:

- **Two-Thirds Majority** (5)
- **Simple Majority (>50%)** (1)
- **Responsible Control Only** (1)
- **Two-Thirds + Mixed Rules** (1)

#### Firm licensed architect ownership minimum fraction

`profession_specific.firm_licensed_architect_ownership_minimum_fraction` — states per tag:

- **All Must Be Licensed** (2)
- **Two-Thirds** (3)
- **Majority** (2)
- **One-Third** (2)
- **At Least One Principal** (5)
- **One Designated Officer** (3)

#### National association

`licensure.national_association` — states per tag:

- **NAAB** (12)
- **AIA** (2)
- **NCARB** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCARB Only** (29)
- **NCARB + NAAB** (1)
- **Board-Recognized Body** (1)

#### Permitted firm structures

`profession_specific.permitted_firm_structures` — items per tag:

- **Sole Proprietorship** (17, 17 states)
- **General Partnership** (39, 38 states)
- **Limited Partnership** (2, 2 states)
- **Limited Liability Partnership** (11, 11 states)
- **Limited Liability Company** (28, 27 states)
- **General Corporation** (38, 36 states)
- **Professional Corporation** (17, 15 states)
- **Joint Venture / Enterprise** (4, 4 states)
- **Other Entity** (31, 24 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **NCARB Required** (4)
- **NCARB or Equivalent** (13)
- **Substantial Equivalence Only** (10)
- **Equivalence + Extra Conditions** (6)
- **Mutual Reciprocity** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Consumer Affairs / Protection** (2)
- **Professional Licensing Agency** (7)
- **Business & Professional Regulation** (2)
- **Commerce / Trade Dept** (2)
- **Labor & Industry Dept** (3)
- **Secretary of State / Education** (2)
- **Other State Agency** (3)

#### Unauthorized practice criminal penalty first offense

`profession_specific.unauthorized_practice_criminal_penalty_first_offense` — states per tag:

- **Named Misdemeanor Class** (12)
- **Misdemeanor + Fine & Jail Specified** (11)
- **Misdemeanor Only** (2)
- **Infraction / Summary Offense** (2)
- **Statutory Reference Only** (3)

#### Unauthorized practice criminal penalty subsequent offense

`profession_specific.unauthorized_practice_criminal_penalty_subsequent_offense` — states per tag:

- **Felony** (2)
- **Gross Misdemeanor** (1)
- **Misdemeanor + Fine & Jail** (2)
- **Misdemeanor (Class Only)** (1)
- **Context-Specific Penalty** (1)

## Bail Bond Agent

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Commercial Interior Design

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Community Health Worker

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Construction Trades

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **No Degree Required** (1)
- **High School / GED** (1)
- **Short Pre-License Training** (1)
- **Associate / Technical Degree** (0)
- **Bachelor's Degree** (1)
- **Experience-Based Substitution** (1)
- **Tiered by License Type** (3)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General Trade Experience** (5)
- **Contractor/Supervisory Experience** (2)
- **Apprenticeship Program** (1)
- **Mixed / Combined Paths** (3)

`licensure.post_degree_experience.duration` — states per tag:

- **1–2 Years** (1)
- **3–4 Years** (3)
- **5 Years** (1)
- **Varies by License Type** (4)
- **4 Years (Recency Required)** (2)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Contractors Board** (16)
- **Construction Industry Board** (3)
- **Commerce / Economic Dev Dept** (1)
- **Labor & Industry Dept** (2)
- **Consumer Protection Agency** (3)
- **Multi-Board System** (1)
- **Other State Agency** (6)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Contractors Board** (17)
- **Construction Industry Board** (3)
- **Dept of Labor & Industry** (2)
- **Consumer Protection Agency** (3)
- **Broad Commerce/Licensing Dept** (7)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Build/Alter/Demo** (9)
- **Broad + Site/Utility Work** (7)
- **Trade Specialties Only** (1)
- **Tiered Contract Classes** (5)
- **Comprehensive Multi-Trade** (6)
- **Specialty Niche (UST/HVAC)** (2)

`scope.definition_quote` — states per tag:

- **Broad General Contractor** (18)
- **Residential / Home Improvement** (4)
- **Trade-Specific Only** (4)
- **Dual-Category (General + Mechanical)** (1)
- **Threshold-Anchored** (4)
- **Reference to Other Law** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud or Misrepresentation** (112, 37 states)
- **Negligence or Incompetence** (37, 22 states)
- **Contract Abandonment or Nonperformance** (33, 20 states)
- **Financial Misconduct** (53, 26 states)
- **License or Registration Violations** (87, 33 states)
- **Criminal Conviction** (21, 19 states)
- **Insurance or Bond Deficiency** (24, 18 states)
- **Regulatory or Code Violations** (115, 36 states)
- **Unlicensed Practice or Assistance** (60, 29 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Full Regulatory Power** (1)
- **Subcommittee Powers (Board Approval)** (1)
- **Advisory & Consultation Only** (2)
- **Rulemaking Consultation Required** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Residential Committee** (2)
- **Housing & Buildings Committee** (1)
- **Trades Licensing Board** (1)
- **General Advisors** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Code & Regulations** (3)
- **Business & Safety Mix** (2)
- **Board-Approved Courses** (1)
- **Trade-Specific Hours** (2)
- **Broad Topic Menu** (1)

#### Deposit cap fraction

`profession_specific.deposit_cap_fraction` — states per tag:

- **~33% Cap** (2)
- **~50% Cap** (1)
- **Low Fixed Cap** (1)
- **Greater-Of Formula** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **4-Year College/University** (1)
- **Any Accredited College** (0)
- **Board/Division Approved** (2)

#### Exams

`licensure.exams` — states per tag:

- **Trade/Technical Exam** (8)
- **Business & Law Exam** (1)
- **Both Trade & Law Exams** (6)
- **General Contractor Exam** (6)
- **Pre-License Course Exam** (1)

#### National association

`licensure.national_association` — states per tag:

- **Home Inspection Bodies** (1)
- **Elevator Industry Bodies** (1)
- **Home Builders Associations** (1)
- **General Contractors & Builders Mix** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NICET (General)** (2)
- **NICET (Fire Protection)** (1)
- **NCCCO (Crane)** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Reciprocity Required** (7)
- **Substantial Equivalency** (8)
- **Agreement-Based** (3)
- **Military / Emergency Only** (3)
- **Endorsement with Extra Steps** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Consumer Affairs** (2)
- **Business & Professional Reg** (5)
- **Commerce Dept** (2)
- **Labor, Licensing & Reg** (1)
- **Secretary of State** (1)
- **Other Executive Office** (3)

#### Voidable contract clauses

`profession_specific.voidable_contract_clauses` — items per tag:

- **Rights Waiver Clauses** (4, 2 states)
- **Liability Release Clauses** (3, 2 states)
- **Judgment and Legal Process Clauses** (2, 2 states)
- **Payment and Wage Clauses** (2, 2 states)
- **Code and Regulatory Waivers** (1, 1 states)
- **Contract Renewal Clauses** (1, 1 states)
- **Attorney Fees Clauses** (1, 1 states)

## Dentistry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **DDS/DMD + CODA Accredited** (12)
- **Graduate + CODA Accredited** (21)
- **Graduate + Board Approved** (7)
- **Degree + Accredited (General)** (5)
- **DDS/DMD Named Only** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General Practice Residency** (0)
- **GP or Specialty Residency** (2)
- **CODA-Approved Residency** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dental Examiners Board** (12)
- **Board of Dentistry** (17)
- **Dept / Agency Only** (5)
- **Dept + Dental Board** (4)
- **Other Dental Board** (12)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Dental Examiners** (13)
- **Board of Dentistry** (20)
- **Dental Board** (6)
- **Dept / Office (Non-Board)** (5)
- **Other Dental Board Name** (6)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad Enumerated List** (19)
- **Concise Category List** (7)
- **Standard Six-Domain** (6)
- **Minimal High-Level** (7)
- **Extended With Modern Procedures** (11)

`scope.drug_authority` — states per tag:

- **Broad Prescribing + Opioid Limits** (11)
- **Broad Prescribing, No Opioid Cap** (4)
- **Prescribe + Anesthesia Permits** (8)
- **Prescribe + Sedation/Anesthesia Detail** (14)
- **Basic Prescribing Only** (9)
- **Vaccine Authority Included** (4)

`scope.definition_quote` — states per tag:

- **ADA Model Language** (15)
- **Perform/Diagnose List** (15)
- **Healing Art Definition** (4)
- **Represents/Holds Out Standard** (8)
- **Broad Surgical + Body Impact** (6)
- **Minimal / Circular** (2)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud and Misrepresentation** (116, 49 states)
- **Criminal Conviction** (60, 43 states)
- **Clinical Incompetence or Negligence** (95, 40 states)
- **Substance Abuse or Impairment** (46, 41 states)
- **Physical or Mental Incapacity** (44, 35 states)
- **Unprofessional or Immoral Conduct** (125, 48 states)
- **Unlicensed Practice or Improper Delegation** (110, 48 states)
- **Advertising Violations** (62, 38 states)
- **Billing and Fee Irregularities** (60, 33 states)
- **Drug Prescribing Violations** (56, 33 states)
- **Record Keeping and Reporting Failures** (68, 24 states)
- **Regulatory and Order Noncompliance** (123, 49 states)
- **Out-of-State Discipline** (37, 35 states)

### Other bucketed fields

#### Advanced practice eligible patient populations

`profession_specific.advanced_practice_eligible_patient_populations` — items per tag:

- **Long-Term Care Residents** (45, 22 states)
- **School and Early Childhood** (37, 23 states)
- **Homebound Individuals** (16, 14 states)
- **Community and Public Health Clinics** (45, 22 states)
- **Correctional Facility Inmates** (13, 10 states)
- **Hospitals and Medical Facilities** (19, 14 states)
- **Low-Income and Underserved Populations** (17, 12 states)
- **Developmental Disability Facilities** (9, 8 states)
- **Other Approved Settings** (34, 18 states)

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Discipline & Rulemaking** (1)
- **Hygiene Licensing & Discipline** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Dental Commission** (1)
- **Dental Hygiene Advisory** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substances** (9)
- **CPR/Emergency Readiness** (4)
- **Ethics & Law** (2)
- **Broad Multi-Topic Mandate** (7)
- **Clinical Hours Focus** (1)
- **Infection Control & Safety** (0)

#### Dental hygienist supervision levels

`profession_specific.dental_hygienist_supervision_levels` — items per tag:

- **Direct Supervision** (48, 47 states)
- **Indirect Supervision** (17, 17 states)
- **General Supervision** (46, 46 states)
- **Public Health Supervision** (5, 5 states)
- **Collaborative/Advanced Practice** (3, 3 states)
- **Telehealth/Remote Supervision** (3, 3 states)
- **Unsupervised Practice** (6, 6 states)

#### Dental therapist practice setting restrictions

`profession_specific.dental_therapist_practice_setting_restrictions` — items per tag:

- **Federally Qualified Health Centers** (9, 5 states)
- **Tribal & Indian Health Facilities** (5, 4 states)
- **Hospital or Medical Facility** (5, 4 states)
- **School or Educational Setting** (7, 6 states)
- **Long-Term & Residential Care** (5, 4 states)
- **Nonprofit & Community Clinic** (8, 5 states)
- **Public Health Department** (3, 3 states)
- **Correctional Facility** (2, 2 states)
- **Mobile or Underserved Setting** (8, 5 states)
- **Agreement-Based Setting** (7, 6 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **CODA / ADA (full name)** (34)
- **CODA only** (9)
- **ADA only** (2)
- **Board-Approved School** (2)
- **Any Recognized Accreditor** (1)

#### National association

`licensure.national_association` — states per tag:

- **ADA Only** (29)
- **ADA + CODA** (16)
- **CODA Only** (2)
- **State Association** (1)
- **ADA + JCDNE** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **JCNDE** (7)
- **NBDE / NBDE-affiliated** (3)
- **ADEX** (2)
- **ABOMS** (3)
- **Multiple Bodies** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Active Practice + Good Standing** (29)
- **Equivalency Standards Only** (8)
- **Jurisprudence Exam Required** (3)
- **Reciprocity Prohibited / Limited** (1)
- **Military / Special Pathway Only** (3)
- **Compact / Portability Program** (3)
- **Conditional / Unclear** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (9)
- **Licensing & Regulatory Affairs** (5)
- **Consumer Affairs** (3)
- **Commerce Dept** (2)
- **Labor & Industry** (2)
- **Professional Regulation Office** (3)

#### Sedation anesthesia permit types

`profession_specific.sedation_anesthesia_permit_types` — items per tag:

- **General Anesthesia** (33, 33 states)
- **Deep Sedation** (22, 22 states)
- **Moderate Sedation** (45, 36 states)
- **Minimal Sedation** (10, 10 states)
- **Nitrous Oxide / Inhalation Analgesia** (12, 12 states)
- **Local Anesthesia** (10, 9 states)
- **Facility / Office Permit** (4, 4 states)
- **Specialty or Other Permit** (12, 10 states)

## Dietetics

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Bachelor's Min** (8)
- **Bachelor's Min, Named Field** (28)
- **Master's Min** (0)
- **Master's Min, Named Field** (2)
- **Tiered by License Type** (9)
- **CDR Registration Only** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Supervised Practice** (16)
- **Preprofessional Program** (15)
- **Internship / Practicum** (9)
- **Accredited Program** (2)
- **Work / Field Experience** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **900 Hours** (26)
- **1,000 Hours** (4)
- **1,200 Hours** (1)
- **Multiple Tiers** (1)
- **Time-Based** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Dietetics Board** (21)
- **Medical/Nursing Board** (7)
- **General Health Department** (9)
- **General Licensing Agency** (11)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Dietetics Board** (24)
- **Combined Health Professions Board** (2)
- **Medical Board** (6)
- **State Health Department** (7)
- **General Licensing Agency** (9)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Assess & Counsel** (14)
- **Core + Clinical Orders** (13)
- **Core + Advanced Clinical** (3)
- **Broad Clinical + Drug/Lab** (5)
- **Narrow / Advisory Only** (6)
- **Minimal / General Wellness** (2)

`scope.drug_authority` — states per tag:

- **Protocol-Based Dose Adjustment** (1)
- **Protocol + Vitamin/Mineral Orders** (2)
- **Protocol-Delegated Prescribing** (1)

`scope.definition_quote` — states per tag:

- **Science Integration Formula** (18)
- **Enumerated Services List** (10)
- **Medical Nutrition Therapy Focus** (5)
- **Assessment & Counseling Focused** (5)
- **Broad Health & Lifecycle** (7)

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

- **Advisory Only** (7)
- **Recommendations Basis for Rules** (3)
- **Delegated Rulemaking & Discipline** (2)
- **Required Proposal Power** (1)
- **Conducts Hearings** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Board / Practice Board** (2)
- **Advisory Board / Group** (2)
- **Advisory Committee** (2)
- **Council** (5)
- **Panel or Advisors** (2)
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

- **Pain & Symptom Management** (1)
- **Nutrition & Metabolic Health** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACEND Only** (4)
- **Regional Accreditor Only** (16)
- **ACEND + Regional** (3)
- **Named Regional Body** (6)
- **Profession Body (non-ACEND)** (5)
- **Dual Federal Bodies** (9)

#### Exams

`licensure.exams` — states per tag:

- **CDR Exam Only** (12)
- **CDR Exam (Waivable)** (13)
- **Board-Approved (CDR Eligible)** (13)
- **State/Dept Exam** (4)
- **Multiple Exams Required** (3)

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
- **ACEND / Accreditor** (2)
- **State Dietetic Assoc** (3)
- **Multiple Associations** (3)

#### National certification

`licensure.national_certification` — states per tag:

- **CDR Only** (40)
- **CDR + Multiple Bodies** (5)
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
- **Equivalent + Clean Record** (4)
- **CDR Registration Accepted** (6)
- **Exam Waiver / Endorsement** (1)
- **Reciprocity Agreement Required** (2)
- **Temporary / Limited Practice** (2)
- **Non-Standard Approach** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Health Department** (7)
- **Professional Licensing Office** (8)
- **Secretary of State / Commerce** (3)
- **Consumer / Labor Affairs** (3)
- **Aging / Disability Services** (1)

## Direct Entry Midwifery

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Electrician

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **No Degree Required** (2)
- **Apprenticeship / Hours Only** (7)
- **Vocational / Trade School** (1)
- **College Degree as Alt Path** (5)
- **Multiple Tiered Pathways** (4)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Journeyman Experience** (10)
- **Apprenticeship** (4)
- **On-the-Job / Practical** (8)
- **Supervised Experience** (3)
- **Management / Supervisory** (1)
- **General Trade Experience** (5)

`licensure.post_degree_experience.duration` — states per tag:

- **~1 Year** (2)
- **~2 Years** (3)
- **~3–4 Years** (4)
- **~4–6 Years (tiered)** (11)
- **~8000 hrs / 4 Yrs** (2)
- **Multi-tier Hours** (9)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Electrical Examining Board** (14)
- **Electrical Contractors Board** (5)
- **General Contractors Board** (11)
- **Dept of Labor / Industry** (4)
- **General Licensing Agency** (9)

`licensure.regulatory_authority.name` — states per tag:

- **Electrical-Specific Board** (21)
- **General Contractors Board** (7)
- **State Dept / Division** (11)
- **Construction Industry Board** (2)
- **Multi-Trade Board** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install/Repair/Maintain** (5)
- **Install/Alter/Repair/Maintain** (17)
- **Install + Plan/Supervise** (8)
- **Install + Plan/Supervise + Maintain** (3)
- **Broad Scope (Contracting Types)** (1)
- **Extended Scope (Specialty Systems)** (5)

`scope.definition_quote` — states per tag:

- **Electrical Work Defined** (10)
- **Electrical Installation Defined** (7)
- **Electrical Contracting Defined** (10)
- **Person/Role Defined** (11)
- **General Contractor Catch-All** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud or Misrepresentation** (61, 36 states)
- **Incompetence or Negligence** (35, 26 states)
- **Criminal Conviction** (15, 14 states)
- **Unlicensed Practice or License Misuse** (76, 29 states)
- **Regulatory or Code Violation** (82, 37 states)
- **Contract or Financial Misconduct** (22, 9 states)
- **Advertising Violations** (8, 8 states)
- **Insurance or Bond Deficiency** (11, 9 states)
- **Administrative or Procedural Failure** (77, 31 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advise & Administer Exams** (1)
- **Advise Only** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Examiners Committee** (1)
- **Safety & Licensing Board** (1)

#### Apprentice supervision ratio

`profession_specific.apprentice_supervision_ratio` — states per tag:

- **1-to-1** (2)
- **1-to-2** (1)
- **1-to-3** (6)
- **Tiered / Context-Dependent** (5)
- **Board-Set / Unspecified** (1)

#### Approved continuing education providers

`profession_specific.approved_continuing_education_providers` — items per tag:

- **Named Trade Associations** (17, 6 states)
- **Academic Institutions** (5, 5 states)
- **Government Agency Programs** (4, 4 states)
- **Board Approved Providers** (10, 9 states)
- **Labor Union Programs** (2, 2 states)
- **Specialty Training Programs** (3, 3 states)
- **Catch-All Approved Provider** (3, 3 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **NEC Only** (5)
- **NEC + Broad Electrical Topics** (4)
- **NEC + Code + Business/Safety Mix** (4)
- **Code + Industry Topics** (2)
- **General Electrical Subjects** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Accredited College/University** (6)
- **State Apprenticeship Body** (1)
- **Federal Apprenticeship Body** (1)
- **State Career/Tech Board** (1)
- **Multiple / Flexible** (3)
- **State-Specific Institution** (1)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Apprentice / Trainee** (32, 21 states)
- **Journeyman Electrician** (42, 30 states)
- **Master Electrician** (26, 22 states)
- **Electrical Contractor** (51, 34 states)
- **Residential License** (21, 15 states)
- **Specialty / Limited Scope** (78, 23 states)
- **Administrator / Supervisor** (5, 3 states)
- **Inspector / Qualifier** (4, 3 states)

#### National association

`licensure.national_association` — states per tag:

- **Standards Body** (1)
- **Fire & Safety Org** (1)
- **Contractor & Labor Coalition** (1)
- **Regional Contractor Council** (1)

#### Qualifier license requirement by contractor type

`profession_specific.qualifier_license_requirement_by_contractor_type` — items per tag:

- **Master Electrician Required** (18, 16 states)
- **Journeyman Electrician Required** (2, 2 states)
- **Specialty License Required** (14, 10 states)
- **Qualifying Party Exam Required** (14, 7 states)
- **Entity Structure Qualifier Rule** (11, 8 states)
- **Experience Requirement** (3, 1 states)
- **Scope Restriction by License Class** (4, 2 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Agreement Required** (8)
- **Equivalent Standards Only** (7)
- **Equivalent + Experience Threshold** (10)
- **Exam Waiver w/ Conditions** (7)
- **Formal Written Agreement** (6)
- **Discretionary / Case-by-Case** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Labor & Industry** (6)
- **Professional Licensing** (10)
- **Consumer Affairs** (3)
- **Commerce** (3)
- **Public Safety / Construction** (4)
- **Independent Division** (2)

#### Residential project definition

`profession_specific.residential_project_definition` — states per tag:

- **Single-Family Only** (1)
- **1–2 Family Dwellings** (3)
- **Up to 4 Units / Low-Rise** (3)
- **Multi-Unit with Story Limit** (6)
- **Technical / Wiring-Based** (2)
- **Broad Residential Scope** (4)

#### Scope exclusions

`profession_specific.scope_exclusions` — items per tag:

- **Utility & Power Distribution** (67, 39 states)
- **Telecom, Cable & Broadcast** (45, 27 states)
- **Homeowner & Owner-Occupant** (54, 32 states)
- **In-House Employer Maintenance** (61, 30 states)
- **Low Voltage & Signal Systems** (49, 27 states)
- **Other Licensed Trade Carve-Out** (129, 36 states)
- **Transportation & Mobile Equipment** (22, 15 states)
- **Agricultural & Farm Use** (13, 13 states)
- **Government & Federal Work** (35, 25 states)

## Electrology

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Emergency Medical Technician

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Environmental Health

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Genetic Counseling

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Health Facility Admin

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Home Inspector

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Hvac

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **No Degree Required** (2)
- **Degree Substitutes for Experience** (2)
- **Vocational/Trade Program** (2)
- **Board-Defined Standards** (3)
- **Minimal Coursework** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General Trade Work** (6)
- **Supervised/Apprenticeship** (4)
- **Journeyperson/License Path** (2)
- **Classification-Specific Work** (4)
- **Board-Defined Rules** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~1–2 Years** (4)
- **~3 Years / 3000–6000 hrs** (2)
- **~4 Years** (4)
- **~5 Years** (1)
- **Tiered by License Type** (5)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **HVAC-Specific Board** (7)
- **General Contractors Board** (14)
- **Plumbing/Mechanical Board** (3)
- **Labor/Licensing Dept** (7)
- **Commerce/Regulation Dept** (3)
- **Office of Prof. Licensure** (5)

`licensure.regulatory_authority.name` — states per tag:

- **HVAC-Specific Board** (8)
- **General Contractors Board** (11)
- **Plumbing & Mechanical Board** (4)
- **Dept of Labor / Licensing** (12)
- **Construction Industry Board** (4)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install + Repair + Maintain** (5)
- **Install + Repair + Alter** (6)
- **Full Lifecycle (Design–Demo)** (9)
- **Install + Service Only** (2)
- **Broad Construction + Demo** (4)
- **Inspect + Test + Restore** (1)
- **Multi-Trade Scope** (2)

`scope.definition_quote` — states per tag:

- **HVAC-Specific Definition** (17)
- **Broad Mechanical/Specialty** (7)
- **General Contractor Definition** (5)
- **Work Type List Only** (4)
- **License/Registration Focus** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud or Misrepresentation** (75, 31 states)
- **Incompetence or Negligence** (36, 23 states)
- **Criminal Conviction** (13, 11 states)
- **Contract or Financial Violations** (43, 17 states)
- **Unlicensed or Unauthorized Practice** (59, 28 states)
- **Regulatory or Permit Violations** (67, 28 states)
- **Insurance or Bond Failures** (12, 10 states)
- **Administrative Noncompliance** (67, 26 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Full Advisory + Exams** (1)
- **Advisory on Rules Only** (1)
- **Advisory on Implementation** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Mechanical Examiners Committee** (1)
- **AC & Refrigeration Board** (1)
- **Residential Contractors Advisors** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Refrigerant/Environmental** (1)
- **Code & Technical Hours** (1)
- **Business & Safety Mix** (3)
- **Trade-Specific Focus** (1)
- **Board-Defined Curriculum** (1)

#### Exams

`licensure.exams` — states per tag:

- **State-Administered Required** (14)
- **Board-Approved Required** (3)
- **Third-Party/Testing Service** (3)
- **Business & Law Focus** (3)
- **Multiple Exams Required** (6)
- **Voluntary Only** (1)

#### Financial responsibility demonstration methods

`profession_specific.financial_responsibility_demonstration_methods` — items per tag:

- **Surety Bond** (18, 17 states)
- **Cash or Deposit Instrument** (6, 4 states)
- **General Liability Insurance** (16, 16 states)
- **Workers Compensation Insurance** (6, 6 states)
- **Net Worth or Financial Statement** (5, 5 states)
- **Credit or Standing Verification** (2, 2 states)
- **Other Indemnity or Instrument** (4, 3 states)

#### National certification

`licensure.national_certification` — states per tag:

- **EPA Refrigerant Cert** (1)
- **NICET Certification** (1)

#### Qualifier license type required

`profession_specific.qualifier_license_type_required` — items per tag:

- **Master HVACR License** (6, 5 states)
- **Mechanical Contractor License** (8, 8 states)
- **AC Contractor License (Classed)** (5, 2 states)
- **Conditioned Air Contractor (Classed)** (2, 1 states)
- **Heating License (Grouped)** (3, 1 states)
- **Fuel Gas License** (5, 1 states)
- **Specialty Trade License** (2, 2 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantially Equivalent Standards** (10)
- **Mutual Reciprocity Required** (6)
- **Exam Waiver + Good Standing** (5)
- **Endorsement / Experience Focus** (3)
- **Emergency / Limited Scope** (2)
- **Discretionary / Case-by-Case** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Labor & Licensing Dept** (5)
- **Commerce Dept** (2)
- **Consumer Affairs Dept** (3)
- **Professional Regulation Div** (5)
- **Occupational Licensure Office** (3)
- **Other Agency** (3)

#### System components included

`profession_specific.system_components_included` — items per tag:

- **Heating Systems** (32, 18 states)
- **Cooling and Refrigeration** (34, 16 states)
- **Ventilation and Exhaust** (26, 14 states)
- **Ductwork and Air Distribution** (17, 9 states)
- **Piping and Hydronic Systems** (26, 12 states)
- **Gas and Fuel Supply** (16, 13 states)
- **Controls and Accessories** (26, 11 states)
- **Boilers and Pressure Vessels** (7, 5 states)

## Insurance Navigator

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Insurance Producer

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Junk Dealer

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Medical Interpreter

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Medicine

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **MD/DO Degree Named** (11)
- **Graduate of Accredited School** (14)
- **Named Accreditor (LCME/AOA)** (16)
- **Board-Approved School** (5)
- **Diploma + Coursework Details** (4)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Residency Only** (20)
- **Internship or Residency** (8)
- **Residency or Fellowship** (5)
- **Broad Postgraduate Training** (11)
- **Accredited Program Required** (4)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year (Domestic)** (10)
- **2 Years (Domestic)** (8)
- **1 Yr Domestic / 2 Yr Foreign** (9)
- **1 Yr Domestic / 3 Yr Foreign** (5)
- **2 Yr Domestic / 3 Yr Foreign** (2)
- **Tiered by Grad Date** (3)
- **Board Discretion** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Medical Board** (18)
- **Board of Examiners** (8)
- **Board of Licensure** (8)
- **Board of Practice/Arts** (8)
- **State Health Dept** (6)
- **Multi-Agency / Hybrid** (2)

`licensure.regulatory_authority.name` — states per tag:

- **Medical Board** (24)
- **Board of Medical Examiners** (7)
- **Board of Medical Licensure** (9)
- **Board of Healing Arts / Practice** (4)
- **Dept / Office (Non-Board)** (3)
- **Education Dept / Regents** (1)
- **Composite / Multi-Profession Board** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Four** (13)
- **Core + Telehealth** (4)
- **Core + Obstetrics/Midwifery** (7)
- **Broad Enumerated** (20)
- **Catch-All Phrase** (6)

`scope.drug_authority` — states per tag:

- **Broad Authority** (21)
- **Opioid Limits** (10)
- **Telehealth Restrictions** (8)
- **Dispense Restrictions** (5)
- **Multiple Restrictions** (6)

`scope.definition_quote` — states per tag:

- **Diagnose & Treat (Concise)** (19)
- **Enumerate Acts (Detailed List)** (14)
- **Holding Out + Acts** (8)
- **Prescribe/Recommend Focus** (2)
- **Broad/Conceptual** (5)
- **Title/Credential Based** (2)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (196, 49 states)
- **Criminal Conviction** (77, 45 states)
- **Clinical Incompetence & Negligence** (132, 46 states)
- **Impairment** (102, 45 states)
- **Controlled Substance Violations** (86, 41 states)
- **Sexual Misconduct** (32, 23 states)
- **Unprofessional & Unethical Conduct** (202, 49 states)
- **Billing & Fee Violations** (63, 27 states)
- **Regulatory & Reporting Failures** (318, 50 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Non-Binding Advisory** (1)
- **Adjudicatory Power** (1)
- **Nominates to Governor** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **State Board of Medical Examiners** (1)
- **State Medical Examining Board** (1)
- **Review Panel** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioids / Controlled Substances** (8)
- **Broad Multi-Topic Mandate** (7)
- **Abuse / Violence / Safety** (2)
- **Equity / Cultural Competency** (0)
- **Specialty / Population-Specific** (5)
- **Board-Discretion / Flexible** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **LCME + AOA/COCA** (14)
- **LCME Only** (2)
- **AMA / AAMC Named** (6)
- **Board Discretion** (18)
- **Federal/Dept of Ed** (2)
- **Multi-Body + Foreign** (7)

#### Foreign medical graduate requirements

`profession_specific.foreign_medical_graduate_requirements` — states per tag:

- **ECFMG + Postgrad Training** (24)
- **ECFMG + Extended Postgrad** (11)
- **ECFMG Only / Minimal Add-ons** (6)
- **Provisional/Limited Pathway** (7)
- **Employer-Sponsored Pathway** (1)
- **Board Discretion** (1)

#### License status types

`profession_specific.license_status_types` — items per tag:

- **Active Full License** (27, 25 states)
- **Inactive / Retired** (59, 41 states)
- **Temporary / Provisional** (71, 43 states)
- **Training / Postgraduate** (48, 39 states)
- **Limited / Restricted / Probationary** (63, 40 states)
- **Disciplinary / Adverse** (44, 18 states)
- **Specialty / Special Purpose** (87, 40 states)
- **Interstate Compact / Endorsement** (21, 19 states)

#### National association

`licensure.national_association` — states per tag:

- **AMA / AOA Only** (16)
- **ACGME + AOA** (7)
- **AMA + ACGME Mix** (5)
- **ABMS Included** (5)
- **FSMB / Exam Boards** (2)
- **State Society Only** (2)
- **Broad Multi-Org** (4)

#### National certification

`licensure.national_certification` — states per tag:

- **NBME / NBOME** (7)
- **ABMS / AOA Specialty** (8)
- **ECFMG Only** (11)
- **Mixed Boards** (9)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Hard Day/Supply Cap** (6)
- **MME or Dose Cap** (2)
- **Telehealth Restrictions** (5)
- **Board Rule Authority** (7)
- **Discipline-Based Only** (4)
- **Stimulant/Schedule II Restrictions** (3)

#### Physician assistant prescriptive authority

`profession_specific.physician_assistant_prescriptive_authority` — states per tag:

- **Full Rx incl. Schedule II** (7)
- **Schedule III–V Only** (4)
- **Schedule II Restricted** (4)
- **Delegated by Physician** (7)
- **Board/Agreement Defined** (8)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards** (19)
- **Active Practice Required** (7)
- **Board Discretion** (5)
- **IMLC Pathway** (5)
- **Exam Equivalency Focus** (6)
- **Multi-Path / Hybrid** (8)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (11)
- **Consumer / Commerce Dept** (4)
- **Professional Licensing Agency** (11)
- **Labor / Regulatory Dept** (3)
- **Education Dept** (1)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Same Standard as In-Person** (6)
- **Relationship Required** (5)
- **Controlled Substance Restrictions** (11)
- **In-Person Exam Required** (4)
- **Licensure / Jurisdiction Rule** (13)
- **Board Rule Authority** (2)

## Music Therapy

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Nursing

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Approved Program Only** (25)
- **Program + Diploma/Degree** (7)
- **RN/LPN Split** (8)
- **APRN Graduate Req** (9)
- **BSN Upgrade Required** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Supervised/Collaborative Practice** (3)
- **Transition to Practice** (1)
- **Clinical Experience** (2)
- **Prescriptive Authority Pathway** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~1,000 hrs** (2)
- **~2,000 hrs** (1)
- **~4,000+ hrs** (2)
- **Time-Based (Months)** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Nursing** (17)
- **Named State Board of Nursing** (24)
- **Dept / Agency (with Board)** (6)
- **Other State Board** (3)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Nursing** (10)
- **State Board of Nursing** (6)
- **Named State Board of Nursing** (26)
- **Board of Registered Nursing** (4)
- **Department / Division** (4)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Nursing Process + Care + Delegation** (16)
- **Traditional Care + Medication Execution** (8)
- **Broad Clinical + APRN Prescribing** (17)
- **Collaborative/Integrated Care Model** (6)
- **Minimal/Concise Scope** (3)

`scope.drug_authority` — states per tag:

- **Full Independent APRN Rx** (25)
- **Independent After Transition Period** (7)
- **Collaborative Agreement Required** (15)
- **Physician-Delegated Rx** (1)
- **Limited/Restricted Rx** (2)
- **CRNA Anesthesia Only** (0)

`scope.definition_quote` — states per tag:

- **Diagnose & Treat Responses** (7)
- **Specialized Knowledge + Nursing Process** (20)
- **Care & Counsel (Traditional)** (7)
- **Attain/Maintain Optimal Health** (6)
- **Enumerated Act List** (5)
- **Broad/Minimal Definition** (5)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (119, 49 states)
- **Criminal Conviction** (61, 46 states)
- **Substance Abuse & Impairment** (54, 41 states)
- **Clinical Incompetence & Negligence** (82, 45 states)
- **Unprofessional & Unethical Conduct** (141, 48 states)
- **Mental or Physical Incapacity** (51, 37 states)
- **Drug Diversion & Controlled Substance Misuse** (39, 24 states)
- **Regulatory & Reporting Violations** (162, 50 states)
- **Prior Disciplinary Action Elsewhere** (40, 36 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advisory Only** (2)
- **Advisory & Recommendatory** (1)
- **Drafts Rules & Advises** (1)
- **Recommends Standards (Structured Review)** (1)
- **Reviews Complaints & Advises** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **APRN Advisory Committee** (3)
- **Prescriptive Authority Focus** (1)
- **Autonomous Practice Council** (1)
- **Multiple Committees** (1)

#### Aprn role categories

`profession_specific.aprn_role_categories` — items per tag:

- **Nurse Practitioner** (49, 49 states)
- **Nurse Anesthetist** (47, 47 states)
- **Nurse Midwife** (42, 42 states)
- **Clinical Nurse Specialist** (49, 49 states)
- **APRN General** (2, 2 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioids / Prescribing Only** (6)
- **Pharmacology / Prescribing Broad** (6)
- **Abuse / Trafficking / Safety** (2)
- **Multi-Topic Mix** (7)
- **Single Specialty Topic** (2)
- **Law / Jurisprudence Only** (1)

#### Controlled substance schedule authority

`profession_specific.controlled_substance_schedule_authority` — items per tag:

- **Schedule II Unrestricted** (25, 25 states)
- **Schedule II Restricted** (6, 5 states)
- **Schedule III** (31, 31 states)
- **Schedule IIIN** (1, 1 states)
- **Schedule IV** (31, 31 states)
- **Schedule V** (29, 29 states)
- **Schedules II–V Combined** (1, 1 states)
- **Unscheduled Broad Authority** (3, 3 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **State Board Approved** (30)
- **National Accreditor (USDOE)** (6)
- **Named National Bodies** (2)
- **Regional/Other Gov Body** (2)
- **Board + National Option** (6)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Registered Nurse** (50, 50 states)
- **Licensed Practical Nurse** (50, 50 states)
- **Advanced Practice RN** (45, 44 states)
- **APRN Specialty Role** (143, 41 states)
- **Nurse Aide / Assistant** (22, 20 states)
- **Medication Aide** (21, 18 states)
- **Temporary / Interim Permit** (27, 24 states)
- **Multistate Compact License** (16, 16 states)
- **Other License Type** (19, 16 states)

#### Lpn supervision requirements

`profession_specific.lpn_supervision_requirements` — items per tag:

- **Registered Nurse** (49, 48 states)
- **Advanced Practice Registered Nurse** (18, 17 states)
- **Physician** (47, 46 states)
- **Physician Assistant** (11, 11 states)
- **Dentist** (38, 38 states)
- **Podiatrist** (18, 18 states)
- **Optometrist / Chiropractor** (9, 6 states)
- **Catch-All Licensed Provider** (10, 10 states)

#### National association

`licensure.national_association` — states per tag:

- **NCSBN / State Boards** (3)
- **Nurse Practitioner / Credentialing** (4)
- **Nurse-Midwifery** (4)
- **Nurse Anesthesia** (3)
- **Accreditation Body** (1)
- **State-Level Association** (2)
- **Multi-Role Mix** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCLEX Only** (3)
- **Named Specific Bodies** (11)
- **Board-Recognized Body** (23)
- **Accreditor-Validated Body** (2)
- **General APRN Specialty Cert** (3)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Short Supply Cap (≤7 days)** (7)
- **Longer Supply Cap (>7 days)** (3)
- **MME / Dose Limit** (1)
- **Physician Oversight Required** (2)
- **Training / CE Requirement** (2)
- **Rulemaking / Procedural** (2)
- **Telemedicine Restrictions** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Qualifications Equivalency** (19)
- **Clean License + Background Check** (6)
- **Compact / Portability Program** (4)
- **Exam + Education Verified** (6)
- **Active Practice Required** (3)
- **Multi-Condition Bundle** (12)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (7)
- **Consumer / Commerce Dept** (5)
- **Professional Licensing Agency** (9)
- **Dept of Commerce & Insurance** (1)
- **Labor / Safety Dept** (3)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Controlled Substance Restrictions** (3)
- **Prior Relationship Required** (3)
- **In-Person Visit Required** (3)
- **Scope of Practice Standard** (6)
- **Licensing / Admin Focus** (3)
- **Collaborative Practice Rules** (3)

## Optician

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Optometry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **OD Degree Required** (14)
- **Graduate of Accredited School** (20)
- **Graduate, Board-Approved School** (7)
- **Graduate, Min Years Specified** (8)
- **Board Standards Only** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Clinical Internship** (2)
- **Supervised Diagnostic Experience** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~100 Hours** (1)
- **6 Months** (1)
- **1 Year** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Optometry Board** (28)
- **Board of Examiners** (13)
- **State Dept / Agency** (4)
- **Dual Authority** (5)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Optometry** (32)
- **Board of Examiners (Optometry)** (11)
- **Board of Registration** (2)
- **State Dept / Agency** (5)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Basic Exam & Lenses** (5)
- **Exam + Pharma + Foreign Body** (18)
- **Exam + Pharma + Minor Procedures** (17)
- **Broad Scope + Surgery** (2)
- **Broad Scope + Laser/Injections** (8)

`scope.drug_authority` — states per tag:

- **Broad (Sched III–V + Hydrocodone)** (18)
- **Moderate (Sched III–V, No Hydrocodone)** (7)
- **Limited Oral + Topical** (8)
- **Topical/Diagnostic Only** (1)
- **Board Formulary / Rules-Defined** (7)
- **Tiered Certification Levels** (9)

`scope.definition_quote` — states per tag:

- **Broad Full-Scope** (12)
- **Exam + Treat + Drugs** (22)
- **Exam + Diagnose + Rx Only** (8)
- **Narrow / Refractive Focus** (2)
- **Includes Surgery / Laser** (3)
- **Behavior-Based Definition** (3)

`profession_specific.surgery_definition` — states per tag:

- **Broad Tissue-Alteration Definition** (8)
- **Invasive Procedure Definition** (6)
- **Enumerated Excluded Procedures** (10)
- **Simple Exclusion Only** (12)
- **Closure/Anesthesia-Based Definition** (3)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud and Misrepresentation** (150, 48 states)
- **Criminal Conviction** (51, 42 states)
- **Incompetence and Negligence** (97, 46 states)
- **Substance Abuse and Impairment** (52, 41 states)
- **False or Deceptive Advertising** (66, 37 states)
- **Unlicensed Practice and Aiding** (82, 39 states)
- **Sexual and Ethical Misconduct** (57, 32 states)
- **Improper Prescribing or Drug Violations** (34, 26 states)
- **Regulatory and Administrative Violations** (246, 50 states)

### Other bucketed fields

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Pharmacology / Therapeutics** (5)
- **Ocular Disease & Treatment** (2)
- **Opioids / Substance Use** (5)
- **Cert-Tiered Requirements** (9)
- **Jurisprudence / Practice Mgmt** (1)
- **Mixed / Multiple Topics** (7)

#### Controlled substance schedule restrictions

`profession_specific.controlled_substance_schedule_restrictions` — items per tag:

- **Schedule I Prohibited** (21, 21 states)
- **Schedule II Prohibited** (15, 15 states)
- **Schedule II Hydrocodone Exception** (19, 19 states)
- **Schedule III–V Permitted With Limits** (16, 14 states)
- **Schedule III–V Prohibited** (11, 7 states)
- **Supply Duration Limit** (10, 10 states)
- **Non-Controlled Exclusions** (11, 6 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACOE / AOA** (9)
- **State Board Approved** (26)
- **Federal / CHEA / USDE** (6)
- **ARBO** (1)
- **State Agency (Non-Board)** (1)

#### Exams

`licensure.exams` — states per tag:

- **NBEO Required** (5)
- **National Exam (Board-Approved)** (10)
- **State Board Exam** (13)
- **NBEO + State Jurisprudence** (5)
- **NBEO + State Board Exam** (13)
- **Board Discretion Only** (4)

#### Laser procedures authorized

`profession_specific.laser_procedures_authorized` — items per tag:

- **Laser Capsulotomy (YAG)** (7, 7 states)
- **Laser Trabeculoplasty** (6, 6 states)
- **Laser Peripheral Iridotomy** (4, 4 states)
- **Broad Laser Authorization** (4, 4 states)
- **General Laser Reference** (1, 1 states)

#### Minor surgical procedures authorized

`profession_specific.minor_surgical_procedures_authorized` — items per tag:

- **Foreign Body Removal** (28, 22 states)
- **Corneal Procedures** (16, 9 states)
- **Eyelid Lesion Surgery** (22, 11 states)
- **Epilation** (13, 13 states)
- **Lacrimal System Procedures** (22, 13 states)
- **Injections** (23, 13 states)
- **Light and Device Therapy** (5, 3 states)
- **Postoperative and Diagnostic Care** (11, 8 states)

#### National association

`licensure.national_association` — states per tag:

- **AOA Only** (5)
- **ACOE / AOA+ACOE** (6)
- **ARBO** (1)
- **IABEO** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NBEO** (23)
- **IABO** (2)
- **ARBO / CELMO** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Minimal / Broad Discretion** (4)
- **Good Standing + Equivalent Standards** (18)
- **Active Practice Requirement** (12)
- **Strict Multi-Condition** (13)
- **Jurisprudence Exam Required** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (6)
- **Dept of Commerce** (2)
- **Consumer Affairs** (3)
- **Professional Licensing Office** (4)
- **Licensing & Regulatory Dept** (5)
- **Labor & Industry Dept** (2)
- **Secretary of State** (1)

#### Specialty certification types

`profession_specific.specialty_certification_types` — items per tag:

- **Diagnostic Pharmaceutical Agents** (16, 15 states)
- **Therapeutic Pharmaceutical Agents** (39, 37 states)
- **Oral Pharmaceutical Agents** (6, 5 states)
- **Glaucoma Treatment Certification** (8, 7 states)
- **Laser Surgery Certification** (3, 3 states)
- **Advanced Procedures Endorsement** (7, 7 states)
- **Immunization Certification** (3, 3 states)

#### Tiered license types

`profession_specific.tiered_license_types` — items per tag:

- **Basic License** (26, 26 states)
- **Diagnostic Pharmaceutical Authority** (13, 13 states)
- **Therapeutic Pharmaceutical Authority** (32, 28 states)
- **Glaucoma Specialty Authorization** (6, 6 states)
- **Surgical / Laser / Injection Procedures** (10, 9 states)
- **Temporary / Training License** (7, 4 states)
- **Other Special Registration** (2, 2 states)

## Perfusionist

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Plumbing

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **No Formal Degree** (3)
- **Apprenticeship / Trade Program** (5)
- **High School / Equivalent** (2)
- **Associate Degree** (1)
- **Bachelor's Degree** (3)
- **Board Discretion** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Apprenticeship Only** (4)
- **Supervised Work Experience** (8)
- **Apprenticeship or Work Experience** (7)
- **Tiered by License Level** (2)
- **General Trade Experience** (7)

`licensure.post_degree_experience.duration` — states per tag:

- **~2 Years / Short** (2)
- **~3 Years / Mid** (1)
- **~4 Years / Standard** (7)
- **~5 Years / Long** (2)
- **Tiered by License Level** (9)
- **Hours-Based** (7)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Plumbing Board** (20)
- **General Contractors Board** (7)
- **Dept of Health / Public Health** (2)
- **Dept of Labor / Industry** (4)
- **Occupational Licensing Dept** (6)
- **Local Board** (1)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Plumbing Board** (16)
- **Broader Trade/Exam Board** (6)
- **Contractors Board** (7)
- **Dept of Labor / Industry** (7)
- **Dept of Health / Housing** (3)
- **Local Board** (1)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install / Repair / Replace** (7)
- **Install / Alter / Maintain** (4)
- **Install / Alter / Repair / Maintain** (9)
- **Design + Install + Supervise** (6)
- **Broad Construction Scope** (11)
- **Supervision / Direction Focus** (1)

`scope.definition_quote` — states per tag:

- **Full Systems Definition** (16)
- **Work & Materials Definition** (5)
- **Fixtures & Apparatus Only** (6)
- **Specialty Contractor (Generic)** (3)
- **Minimal / Partial Definition** (6)
- **Role-Based Definition** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Licensure** (44, 37 states)
- **Criminal Conviction** (19, 19 states)
- **Incompetence or Negligence** (47, 30 states)
- **Regulatory or Code Violation** (74, 42 states)
- **License Misuse or Transfer** (24, 18 states)
- **Unlicensed Practice or Employment** (44, 23 states)
- **Contract or Financial Misconduct** (46, 16 states)
- **Substance Abuse or Impairment** (6, 5 states)
- **Other Compliance Failures** (70, 34 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advisory Only** (3)
- **Advisory + Exam/Rules Input** (3)
- **Advisory + Enforcement Role** (2)
- **Rulemaking Authority** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Plumbing Examiners Board** (4)
- **Plumbing Board/Council** (2)
- **Plumbers Advisory Board** (1)
- **Broader Construction Board** (1)
- **Specialty Advisory Board** (1)

#### Apprentice supervision requirement

`profession_specific.apprentice_supervision_requirement` — states per tag:

- **Direct/On-Site Supervision** (6)
- **Direct Supervision** (11)
- **General Supervision** (10)
- **Supervision with Exceptions** (3)
- **Journeyman Supervised by Master** (3)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Code Updates** (4)
- **Trade General** (3)
- **Health/Safety/Environment** (3)
- **Business & Legal** (0)
- **Mixed Topics Required** (2)

#### Contractor qualifier license requirement

`profession_specific.contractor_qualifier_license_requirement` — states per tag:

- **Master Plumber Required** (22)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **State Board Approved** (1)
- **State Apprenticeship Council** (1)
- **State Workforce Board** (1)
- **Accredited College/University** (1)

#### Exams

`licensure.exams` — states per tag:

- **State Board Exam** (9)
- **Independent/Testing Service** (4)
- **Local Board Exam** (2)
- **Contractor License Exam** (6)
- **Multi-Tier (Master + Journey)** (18)

#### Journeyman experience pathways

`profession_specific.journeyman_experience_pathways` — items per tag:

- **Apprenticeship Program Completion** (12, 12 states)
- **On-the-Job Hours Experience** (24, 21 states)
- **Academic or Trade School Training** (11, 10 states)
- **Military Service Credit** (5, 5 states)
- **Out-of-State License or Experience** (8, 7 states)
- **Board Discretion or Equivalency** (6, 6 states)
- **Examination Requirement** (3, 3 states)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Apprentice / Trainee** (37, 29 states)
- **Journeyman / Journey-Level** (43, 35 states)
- **Master Plumber** (35, 26 states)
- **Plumbing Contractor** (34, 22 states)
- **General / Engineering Contractor** (7, 2 states)
- **Specialty / Limited Scope** (42, 19 states)
- **Endorsement / Add-On Credential** (6, 4 states)
- **Inspector / Administrator** (2, 2 states)

#### National certification

`licensure.national_certification` — states per tag:

- **NITC** (2)
- **NICET** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Recognition Required** (11)
- **Equivalent Standards Only** (10)
- **Exam Waiver Conditions** (4)
- **Endorsement / Endorsement-Plus** (6)
- **Limited / Specialty Scope** (2)
- **Expedited / Universal Recognition** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Consumer Affairs / Protection** (4)
- **Professional / Occupational Licensing** (8)
- **Business & Professional Regulation** (1)
- **Labor & Industry** (3)
- **Commerce** (2)
- **Health / Safety** (3)
- **Trade-Specific Agency** (2)

## Podiatry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **DPM Degree** (7)
- **DPM + Accreditation Body** (13)
- **Graduate of Accredited School** (10)
- **Graduate + Hour/Year Requirements** (8)
- **Diploma/Certificate** (5)
- **Board-Approved School** (7)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Podiatric Residency** (16)
- **Residency Program** (6)
- **CPME-Approved Residency** (2)
- **Residency or Preceptorship** (5)
- **Postgraduate Training (Broad)** (10)
- **Board-Discretion Experience** (3)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (22)
- **2 Years** (4)
- **3 Years** (2)
- **Tiered / Conditional** (2)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Podiatry Board** (31)
- **Medical Board** (13)
- **State Health/Licensing Dept** (6)

`licensure.regulatory_authority.name` — states per tag:

- **Podiatry-Specific Board** (32)
- **Medical Board** (13)
- **State Health/Other Agency** (5)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Triad (med/mech/surg)** (20)
- **Extended Triad + Electrical/Manip** (11)
- **Diagnosis-Forward List** (10)
- **Broad/All Means** (5)
- **Detailed Enumeration** (4)

`scope.drug_authority` — states per tag:

- **Local Anesthetic Only** (5)
- **General Prescribing (Scope-Limited)** (24)
- **Controlled Substances Explicit** (12)
- **Schedules Specified** (4)
- **Narcotics Authorized** (4)

`scope.definition_quote` — states per tag:

- **Foot Only** (7)
- **Foot & Ankle** (14)
- **Foot, Ankle & Leg/Lower Extremity** (22)
- **Broad / Health Profession framing** (6)
- **Title/Conduct-Based Definition** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (140, 46 states)
- **Criminal Conviction** (58, 44 states)
- **Clinical Negligence & Incompetence** (64, 39 states)
- **Substance Abuse & Impairment** (50, 42 states)
- **Physical or Mental Incapacity** (48, 35 states)
- **Unprofessional & Unethical Conduct** (159, 47 states)
- **Drug Prescribing Violations** (46, 32 states)
- **Advertising Violations** (46, 36 states)
- **Regulatory & Administrative Violations** (205, 48 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advisory Only** (2)
- **Advisory + Disciplinary** (2)
- **Must Consult Before Action** (1)
- **Rule Proposal Authority** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Full Board** (1)
- **Advisory Board** (1)
- **Advisory Committee** (3)
- **Review Committee** (1)

#### Board certification body

`profession_specific.board_certification_body` — items per tag:

- **ABFAS (Foot & Ankle Surgery)** (4, 4 states)
- **ABPS (Podiatric Surgery)** (6, 6 states)
- **ABPM (Podiatric Medicine)** (2, 2 states)
- **ABOS / Osteopathic Orthopedics** (2, 1 states)
- **Multi-Specialty / Other Podiatric** (2, 1 states)
- **Board-Approved / Generic Standard** (2, 2 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substance Prescribing** (7)
- **Substance Use & Addiction** (2)
- **Patient Safety / Error Prevention** (0)
- **Infection Control** (1)
- **Approved Source / Format Rules** (2)
- **Multi-Topic Required** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **APMA (org name only)** (5)
- **CPME / Council (named)** (20)
- **Board-Approved School** (10)
- **State Board Approval** (5)
- **National Accreditor (generic)** (3)

#### National association

`licensure.national_association` — states per tag:

- **APMA** (27)
- **CPME** (3)
- **American Podiatry Assoc (older name)** (5)
- **State Association** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NBPME** (14)
- **NBPE / NBP Examiners** (7)
- **ABFAS** (3)
- **ABPS / Podiatric Surgery** (3)
- **Multiple Boards Accepted** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantially Equivalent Standards** (17)
- **Equivalent + Practice Years** (12)
- **Equivalent + Mutual Reciprocity** (7)
- **Exam + Credentials Review** (9)
- **Broad Discretion / Light Touch** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (8)
- **Consumer Affairs / Commerce** (5)
- **Licensing & Regulatory Affairs** (4)
- **Professional Regulation Division** (3)
- **Dept of State / Secretary of State** (2)
- **Labor & Industry** (3)

## Polysomnography

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Private Probation

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Professional Engineering

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **4-Year Board-Approved** (18)
- **4-Year ABET-Accredited** (10)
- **Bachelor's+ with Alternatives** (6)
- **Flexible / Experience Substitution** (1)
- **Board Discretion / General** (0)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Progressive Experience** (8)
- **General Engineering Work** (13)
- **Active Practice** (2)
- **Supervised Experience** (6)
- **Responsible Charge** (5)

`licensure.post_degree_experience.duration` — states per tag:

- **4 Years (Flat)** (18)
- **4 Years (Standard), More for Others** (5)
- **Tiered by Degree/Path** (8)
- **8+ Years Possible** (1)
- **Board-Defined** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **PE+Surveying Board** (16)
- **Multi-Profession Board** (7)
- **PE-Only Board** (6)
- **Dept / Agency (Non-Board)** (4)
- **Examiner Board** (2)

`licensure.regulatory_authority.name` — states per tag:

- **PE + Surveyors Board** (15)
- **PE + Surveyors + Architects Board** (4)
- **PE + Surveyors + Geologists Board** (2)
- **PE-Only Board** (6)
- **Examiners Board** (4)
- **General Licensing Agency** (4)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Only** (0)
- **Core + Construction Oversight** (14)
- **Core + Surveys/Studies** (3)
- **Core + Teaching** (0)
- **Comprehensive** (16)

`scope.definition_quote` — states per tag:

- **Creative Work + Education + Services List** (15)
- **Professional Service + Public Welfare** (10)
- **Engineering Principles + Data** (4)
- **Broad Arts & Sciences** (1)
- **Minimal / High-Level Only** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Obtaining License** (50, 40 states)
- **Negligence Incompetence Misconduct** (70, 39 states)
- **Criminal Conviction** (36, 31 states)
- **Improper Seal Use** (31, 25 states)
- **Unlicensed or Unauthorized Practice** (69, 28 states)
- **Regulatory Violation Noncompliance** (104, 42 states)
- **Out of State Discipline** (22, 21 states)
- **Substance Abuse Impairment** (13, 10 states)
- **Unethical Business Conduct** (61, 24 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Recommend & Consult** (1)
- **Assist on Licensing & Conduct** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Engineering Only** (1)
- **Engineering + Other Disciplines** (1)

#### Board engineering disciplines represented

`profession_specific.board_engineering_disciplines_represented` — items per tag:

- **Civil Engineering** (9, 9 states)
- **Structural Engineering** (7, 7 states)
- **Mechanical Engineering** (9, 8 states)
- **Electrical Engineering** (9, 9 states)
- **Chemical Engineering** (5, 5 states)
- **Other Engineering Discipline** (42, 27 states)
- **Land Surveying** (11, 11 states)
- **General Public / Non-Professional** (6, 6 states)
- **Related Profession** (5, 3 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ethics + Practice Areas** (1)
- **Ethics Minimum Only** (1)
- **Discipline Hour Minimums** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **EAC/ABET Only** (10)
- **ABET (Multiple Commissions)** (2)
- **ABET Generic** (2)
- **Board-Approved** (6)
- **State Board** (1)

#### Exams

`licensure.exams` — states per tag:

- **FE + PE (NCEES Named)** (12)
- **FE + PE (Generic Two-Part)** (11)
- **FE + PE (State-Branded)** (6)
- **Single/Unitary Exam** (3)
- **FE + PE (Waiver Provisions)** (3)

#### Exemptions from licensure

`profession_specific.exemptions_from_licensure` — items per tag:

- **Supervised Employee or Subordinate** (68, 44 states)
- **Federal or Military Government** (32, 29 states)
- **State or Local Government** (26, 17 states)
- **Public Utility or Regulated Industry** (34, 27 states)
- **Manufacturing or Industrial Internal Use** (31, 25 states)
- **Other Licensed Profession Incidental Work** (88, 36 states)
- **Nonresident or Temporary Practice** (25, 19 states)
- **Small or Exempt Building Type** (59, 20 states)
- **Owner or Employer Self-Use** (53, 31 states)

#### National association

`licensure.national_association` — states per tag:

- **NCEES** (6)
- **ABET** (1)
- **State Society** (3)
- **Multiple Discipline Societies** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCEES (Full Name)** (6)
- **NCEES (Legacy Name)** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Comparable Standards** (11)
- **Comparable + Good Standing** (3)
- **NCEES Record Pathway** (8)
- **Equivalent + Active Years** (5)
- **Mutual Recognition** (2)
- **Exam May Be Required** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Commerce / Economic Dev** (3)
- **Consumer Affairs / Protection** (3)
- **Business & Professional Reg** (2)
- **Labor & Industry** (3)
- **Professional Licensing Agency** (3)
- **Secretary / Dept of State** (2)
- **Other** (3)

#### Seal document types

`profession_specific.seal_document_types` — items per tag:

- **Plans & Drawings** (61, 41 states)
- **Specifications** (41, 40 states)
- **Reports & Studies** (41, 38 states)
- **Plats, Maps & Surveys** (36, 27 states)
- **Calculations & Design Data** (14, 9 states)
- **Certifications & Submissions** (4, 4 states)
- **General or Catch-All Documents** (28, 23 states)

## Psychoanalysis

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Public Accountancy

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **Bach + 150 Hours** (23)
- **Bach + 150 Hours + Concentration** (16)
- **Bach Degree Only** (8)
- **150 Hours Only** (1)
- **Board Discretion** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Broad Skills List** (22)
- **Public Practice Only** (5)
- **Any Accounting Field** (8)
- **CPA-Supervised Required** (13)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (26)
- **2 Years** (3)
- **Hours-Based** (4)
- **1 or 2 Years (Pathway-Dependent)** (12)
- **2+ Years (Multi-Track)** (2)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **State Board of Accountancy** (29)
- **State Board of Public Accountancy** (12)
- **State Dept / Agency** (5)
- **Board of CPA Examiners** (3)
- **Education Board** (1)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Accountancy** (30)
- **Board of Public Accountancy** (12)
- **Board of CPA Examiners** (3)
- **Examining Board** (2)
- **Dept / broader agency** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad Enumerated List** (18)
- **Attest + Advisory Core** (16)
- **Standards-Referenced Detail** (9)
- **Audit/Assurance Focused** (4)
- **High-Level Summary** (3)

`scope.definition_quote` — states per tag:

- **Broad Services List** (20)
- **Attest-Focused** (7)
- **CPA Title + Services** (9)
- **Report/Opinion Issuance** (8)
- **Minimal/Terse** (6)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud or Deceit in Obtaining License** (55, 42 states)
- **Dishonesty or Negligence in Practice** (106, 46 states)
- **Criminal Conviction** (58, 41 states)
- **Out-of-State or Agency Discipline** (98, 48 states)
- **Violation of Statute or Board Rules** (131, 47 states)
- **Continuing Education or Peer Review Failure** (19, 12 states)
- **Unlicensed or Improper Practice** (48, 23 states)
- **Impairment or Incapacity** (15, 9 states)
- **Conduct Reflecting Unfitness** (49, 37 states)

### Other bucketed fields

#### Attest services types

`profession_specific.attest_services_types` — items per tag:

- **Audit / SAS Engagement** (46, 45 states)
- **Review / SSARS Engagement** (43, 42 states)
- **Compilation / SSARS Engagement** (10, 10 states)
- **Attestation / SSAE Engagement** (43, 40 states)
- **Prospective Financial Info Examination** (30, 30 states)
- **PCAOB Engagement** (38, 38 states)
- **Government Auditing Standards** (4, 4 states)
- **General Attest or Assurance Service** (13, 9 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ethics Only** (1)
- **Accounting/Audit + Ethics** (1)
- **Broad Subject List** (2)
- **State Law + Ethics** (1)
- **Detailed Hour Allocations** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Board Discretion** (16)
- **Regional Accreditors Named** (3)
- **US Dept of Education** (6)
- **Regional + Board Fallback** (3)
- **Business Accreditors Included** (1)

#### National association

`licensure.national_association` — states per tag:

- **AICPA Only** (37)
- **NASBA Only** (2)
- **AICPA + NASBA** (6)
- **AICPA + PCAOB** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **AICPA + NASBA Joint** (2)
- **NASBA NQAS** (4)
- **NASBA Only** (1)
- **AICPA Only** (1)

#### Practice privilege consent conditions

`profession_specific.practice_privilege_consent_conditions` — items per tag:

- **Jurisdiction and Disciplinary Authority Consent** (50, 47 states)
- **Compliance with Laws and Rules** (46, 46 states)
- **Cessation of Practice if Home-State License Invalid** (41, 41 states)
- **Agent for Service of Process Appointment** (45, 45 states)
- **Reporting and Cooperation Obligations** (5, 4 states)
- **Additional State-Specific Conditions** (8, 6 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantial Equivalency Only** (6)
- **SE + Traditional Fallback** (23)
- **Traditional Requirements** (10)
- **Practice Privilege Emphasized** (7)
- **Mutual Recognition Required** (4)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Consumer Affairs / Protection** (4)
- **Commerce & Economic Dev** (2)
- **Professional Licensing Dept** (9)
- **Business Regulation** (1)
- **Labor & Industry** (2)
- **Other State Agency** (5)

#### Statute of limitations for accountant negligence

`profession_specific.statute_of_limitations_for_accountant_negligence` — states per tag:

- **Discovery + Hard Cap** (1)
- **External Statute Governs** (1)
- **Board Discovery Rule** (1)

## Real Estate Broker

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

## Soil Classifier

### Priority fields

#### Minimum Degree

_No bucketed tags for this field (data too sparse or not yet run)._

#### Professional Experience

_No bucketed tags for this field (data too sparse or not yet run)._

#### Licensing Authority

_No bucketed tags for this field (data too sparse or not yet run)._

#### Scope of Practice

_No bucketed tags for this field (data too sparse or not yet run)._

#### Discipline

_No bucketed tags for this field (data too sparse or not yet run)._

