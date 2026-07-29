# Field Tag Sheet

_Generated 2026-07-29T14:33:18+00:00_

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

- **DDS/DMD Named + CODA** (10)
- **DDS/DMD Named, Board Approved** (4)
- **Accredited School, CODA Named** (26)
- **Accredited School, Board Approved** (8)
- **Doctoral Degree, General** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **GPR or Specialty Residency** (2)
- **CODA-Approved Residency w/ Intern Title** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Dental Examiners** (12)
- **Board of Dentistry** (29)
- **State Dept / Agency** (6)
- **Dual Authority** (3)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Dental Examiners** (13)
- **Board of Dentistry** (20)
- **Dental Board** (6)
- **Dept / Office (Non-Board)** (5)
- **Other Dental Board** (6)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad Enumerated List** (14)
- **Concise Category List** (10)
- **Terse High-Level Only** (11)
- **Moderate Detail List** (15)

`scope.drug_authority` — states per tag:

- **Basic Prescribe/Dispense** (14)
- **Prescribe + Anesthesia** (17)
- **Prescribe + Opioid Limits** (6)
- **Prescribe + Anesthesia + Opioid Limits** (2)
- **Prescribe + Expanded Authority** (7)
- **Pharmacist Fill Reference** (4)

`scope.definition_quote` — states per tag:

- **Modern Comprehensive (ADA-style)** (14)
- **Enumerated Acts** (16)
- **Healing Art / Oral Cavity** (4)
- **Diagnosis & Treatment (Short Form)** (9)
- **Holds Out / Represents Self** (7)

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

- **Full Regulatory & Disciplinary** (1)
- **Advisory Only** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Dental Commission** (1)
- **Specialty Committee** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substances** (10)
- **CPR/Emergency Procedures** (5)
- **Ethics/Jurisprudence** (2)
- **Broad Clinical Topics** (4)
- **Mixed Mandatory Topics** (5)

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

- **ADA / CODA (full name)** (34)
- **CODA only** (9)
- **ADA only** (2)
- **Board-recognized school** (2)
- **Federal DOE standard** (1)

#### National association

`licensure.national_association` — states per tag:

- **ADA Only** (32)
- **ADA + CODA** (9)
- **CODA / ADA (CODA-emphasis)** (4)
- **AADB** (1)
- **State Association** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **JCNDE / NBDE** (10)
- **ADEX** (1)
- **ADEX + JCNDE** (2)
- **ADA Specialty Board** (1)
- **ABOMS (Oral Surgery)** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Active Practice + Years** (14)
- **Good Standing + Equivalency** (12)
- **Credentials + Exam Required** (16)
- **Compact / Portability Program** (3)
- **Restricted / Conditional** (4)
- **Minimal Requirements** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (6)
- **Dept of Commerce/Consumer Affairs** (4)
- **Professional Licensing Agency** (8)
- **Labor & Regulation Dept** (4)
- **Secretary of State Office** (1)

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

- **No Formal Degree** (1)
- **HS / Basic Schooling** (2)
- **Apprenticeship / Trade Training** (5)
- **College Coursework (Partial Credit)** (3)
- **Degree as Full Alternative** (4)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Journeyman Experience** (6)
- **Supervised Work Experience** (4)
- **Apprenticeship** (3)
- **Apprenticeship or Field Experience** (8)
- **Management/Supervisory Experience** (3)
- **General Trade Experience** (6)

`licensure.post_degree_experience.duration` — states per tag:

- **~1 Year** (2)
- **2 Years** (2)
- **3–4 Years** (4)
- **5–6 Years** (3)
- **7–8 Years / 8000 hrs** (2)
- **Multi-Tier (varies by class)** (17)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Electrician Board** (15)
- **General Contractor Board** (6)
- **Construction Industry Board** (4)
- **Dept of Labor** (3)
- **Broad Licensing Agency** (10)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Electrical Board** (21)
- **General Contractors Board** (6)
- **Construction Industry Division** (4)
- **Broad Commerce/Consumer Dept** (4)
- **Occupational Licensing Div** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install & Repair Only** (2)
- **Install, Repair & Maintain** (14)
- **Install, Repair, Maintain & Plan** (4)
- **Install, Repair, Maintain & Supervise** (4)
- **Broad Scope + Specialty Systems** (5)
- **Construction Trade Framing** (5)

`scope.definition_quote` — states per tag:

- **Install/Repair Wiring** (12)
- **Install/Repair + Design/Supervise** (7)
- **Broad Electrical Systems** (8)
- **Specialty Contractor (Generic)** (3)
- **Multi-Trade / Generic** (2)
- **Low-Voltage Included** (2)
- **Contractor Business Scope** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (76, 36 states)
- **Incompetence & Substandard Work** (46, 31 states)
- **Criminal Conviction** (18, 16 states)
- **Statutory & Code Violations** (65, 38 states)
- **Unlicensed Practice & License Misuse** (77, 31 states)
- **Contract & Financial Misconduct** (28, 11 states)
- **Insurance & Bond Failures** (13, 11 states)
- **Administrative & Procedural Violations** (78, 34 states)
- **Out-of-State Discipline** (7, 7 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Full Rulemaking & Enforcement** (1)
- **Broad Advisory & Exams** (2)
- **Advisory & Policy** (1)
- **Narrow Consultation** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Dedicated Electrical Board** (1)
- **Examiners Committee** (1)
- **Safety & Licensing Advisory** (1)
- **Combined Trades Board** (1)

#### Apprentice supervision ratio

`profession_specific.apprentice_supervision_ratio` — states per tag:

- **1:1 Ratio** (2)
- **1:2 Ratio** (2)
- **1:3 Ratio** (5)
- **Higher / Context-Dependent** (4)
- **Set by Authority** (1)

#### Approved continuing education providers

`profession_specific.approved_continuing_education_providers` — items per tag:

- **Named Trade Associations** (11, 4 states)
- **Academic Institutions** (5, 5 states)
- **Apprenticeship Programs** (2, 2 states)
- **Government Agencies** (3, 3 states)
- **Board-Approved Providers** (6, 6 states)
- **Specialized Training Programs** (4, 4 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **NEC / Code Updates Only** (7)
- **NEC + Broad Technical Topics** (3)
- **NEC + Business & Safety Mix** (2)
- **Broad Technical List** (2)
- **Minimal / General** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **State Board** (1)
- **Named State Institution** (1)
- **Generic Accredited College** (3)
- **Federal Agency** (1)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Apprentice / Trainee** (31, 20 states)
- **Journeyman / Wireman** (43, 32 states)
- **Master Electrician** (28, 23 states)
- **Electrical Contractor** (40, 30 states)
- **Residential Scope** (21, 14 states)
- **Specialty / Limited Scope** (79, 26 states)
- **Inspector / Administrator** (2, 2 states)
- **General / Engineering Contractor** (9, 4 states)

#### National association

`licensure.national_association` — states per tag:

- **Fire/Safety Body** (1)
- **Contractor Associations** (1)
- **Multi-Association** (1)

#### Qualifier license requirement by contractor type

`profession_specific.qualifier_license_requirement_by_contractor_type` — items per tag:

- **General Electrical Contractor** (22, 20 states)
- **Specialty Contractor** (15, 12 states)
- **Residential Contractor** (5, 5 states)
- **Low Voltage / Power Limited** (3, 3 states)
- **Business Entity Qualifier** (5, 2 states)
- **License Class Tier** (4, 2 states)
- **Experience / Exam Requirement** (3, 2 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Agreement Required** (16)
- **Equivalent Standards Only** (9)
- **Endorsement / Credential Review** (4)
- **Exam Waiver + Equivalency** (6)
- **Universal Recognition** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Labor & Industry** (6)
- **Licensing & Regulation** (6)
- **Consumer Affairs** (3)
- **Professional Regulation** (4)
- **Commerce Dept** (2)
- **Public Safety / Other** (4)

#### Residential project definition

`profession_specific.residential_project_definition` — states per tag:

- **1-4 Units / Low Rise** (5)
- **1-2 Units Only** (1)
- **Single Family Only** (2)
- **Stories / Floors Cap** (4)
- **Wiring / Technical Spec** (1)
- **Broad Residential Scope** (1)

#### Scope exclusions

`profession_specific.scope_exclusions` — items per tag:

- **Utility & Infrastructure Work** (68, 40 states)
- **Telecom & Low Voltage Systems** (65, 32 states)
- **Owner/DIY Work** (84, 38 states)
- **Industrial & Manufacturing Facilities** (51, 29 states)
- **Other Licensed Trades** (109, 39 states)
- **Alarm & Security Systems** (17, 15 states)
- **Government & Public Agencies** (32, 24 states)
- **Transportation & Mobile Equipment** (20, 15 states)
- **Educational & Nonprofit Programs** (16, 11 states)

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
- **Trade/Vocational Program** (2)
- **Bachelor's Degree Option** (2)
- **Board-Defined Requirements** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General Trade Work** (5)
- **Supervised/Directed Work** (2)
- **Apprenticeship** (3)
- **Contracting Employment** (4)
- **Journeyman/Foreman Level** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~1–2 Years** (4)
- **3 Years** (2)
- **4 Years** (4)
- **5 Years** (1)
- **Tiered / Multiple Paths** (4)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **HVAC-Specific Board** (4)
- **General Contractors Board** (6)
- **Construction Industry Board** (5)
- **Dept of Labor/Licensing** (8)
- **Plumbing & Mechanical Board** (2)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated HVAC Board** (5)
- **Plumbing & Mechanical Board** (3)
- **General Contractors Board** (6)
- **Construction Industry Board** (5)
- **State Dept / Agency** (6)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install & Repair Only** (3)
- **Install, Maintain & Repair** (7)
- **Full Service + Design** (1)
- **Full Service + Design + Alteration** (9)
- **Broad Mechanical Scope** (2)
- **System-Type Enumerated** (3)

`scope.definition_quote` — states per tag:

- **HVAC-Specific Scope** (4)
- **Mechanical/Multi-Trade Scope** (9)
- **Specialty Contractor (Generic)** (2)
- **Design+Install+Maintain** (6)
- **Install+Repair Only** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (88, 35 states)
- **Incompetence & Negligence** (35, 23 states)
- **Unlicensed & Unauthorized Practice** (67, 30 states)
- **Contract & Project Failures** (28, 14 states)
- **Financial Misconduct** (25, 15 states)
- **Regulatory & Code Violations** (68, 31 states)
- **Criminal Conviction** (15, 13 states)
- **Insurance & Bond Deficiency** (12, 11 states)
- **Administrative Non-Compliance** (68, 27 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advise & Exam Development** (1)
- **Advise Only** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Mechanical Examiners Committee** (1)
- **AC & Refrigeration Board** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Code & Regulations** (2)
- **Refrigerant/Environmental** (1)
- **Broad Industry Topics** (2)
- **Core HVAC Technical** (1)
- **Board-Defined Requirements** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Federal + Regional Accreditor** (1)
- **State Board / Equivalent** (1)

#### Exams

`licensure.exams` — states per tag:

- **State Board Exam** (11)
- **State Dept Exam** (3)
- **Two-Part Exam** (3)
- **Multi-Level Exam** (3)
- **Third-Party Approved** (3)

#### Financial responsibility demonstration methods

`profession_specific.financial_responsibility_demonstration_methods` — items per tag:

- **Surety Bond** (18, 17 states)
- **Cash or Deposit** (7, 6 states)
- **Letter of Credit** (3, 3 states)
- **Liability Insurance** (13, 10 states)
- **Workers Compensation Insurance** (3, 2 states)
- **Financial Statement** (7, 4 states)
- **Credit Assessment** (2, 1 states)
- **Other Compliance** (3, 3 states)

#### National certification

`licensure.national_certification` — states per tag:

- **EPA Certification** (1)
- **NICET Certification** (1)

#### Qualifier license type required

`profession_specific.qualifier_license_type_required` — items per tag:

- **Master HVACR License** (8, 5 states)
- **Mechanical Contractor License** (8, 8 states)
- **HVAC Contractor License** (10, 7 states)
- **Fuel Gas License** (5, 2 states)
- **Specialty Trade License** (6, 3 states)
- **Statutory Reference Only** (2, 2 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Reciprocity Required** (6)
- **Substantial Equivalence Only** (6)
- **Endorsement / Recognition** (5)
- **Emergency / Temporary Only** (2)
- **Formal Agreement Required** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Labor & Licensing** (3)
- **Commerce Dept** (2)
- **Consumer Affairs** (3)
- **Professional Regulation** (8)
- **Other State Office** (2)

#### System components included

`profession_specific.system_components_included` — items per tag:

- **Heating Systems** (47, 27 states)
- **Cooling and Refrigeration** (43, 24 states)
- **Ventilation and Air Distribution** (49, 22 states)
- **Piping and Fluid Systems** (31, 15 states)
- **Fuel and Gas Supply** (22, 13 states)
- **Controls and Electrical** (15, 9 states)
- **Auxiliary and Support Equipment** (20, 11 states)

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

- **MD or DO (any approved)** (17)
- **MD or DO (accredited only)** (12)
- **MD only** (4)
- **Graduate of Med School** (11)
- **Foreign School Provisions** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Residency Only** (17)
- **Residency or Internship** (12)
- **Residency, Internship, or Fellowship** (5)
- **General Postgrad Training** (12)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (9)
- **2 Years** (9)
- **3 Years** (2)
- **1–2 Years (Tiered)** (10)
- **1–3 Years (Tiered)** (6)
- **Board Discretion** (6)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **State Medical Board** (19)
- **Board of Medical Examiners** (6)
- **Board of Medical Licensure** (7)
- **Healing Arts Board** (2)
- **Dept / Agency Umbrella** (9)
- **Composite / Other Board** (7)

`licensure.regulatory_authority.name` — states per tag:

- **Medical Board** (23)
- **Board of Examiners** (8)
- **Board of Licensure** (9)
- **Board of Practice** (2)
- **Healing Arts Board** (2)
- **Dept / Commission** (4)
- **Multi-Profession Board** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Four (Dx/Tx/Rx/Sx)** (14)
- **Broad + Enumerated Methods** (16)
- **General Medical/Surgical** (4)
- **Extended Scope (Telehealth/Tech)** (4)
- **OB/Pregnancy Explicit** (8)

`scope.drug_authority` — states per tag:

- **Broad Authority** (11)
- **Broad + Opioid Limits** (7)
- **Broad + Delegation** (4)
- **Broad + Procedural Rules** (10)
- **Basic Prescribing Only** (10)

`scope.definition_quote` — states per tag:

- **Diagnose & Treat Core** (12)
- **Enumerated Acts List** (18)
- **Holding Out + Acts** (7)
- **Title Use Included** (3)
- **Narrow / Minimal** (7)
- **Exam-Based Definition** (1)

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

- **Opioids / Controlled Substances** (10)
- **Broad Multi-Topic Mandate** (6)
- **Specialty-Specific Topics** (3)
- **Abuse & Violence** (1)
- **Ethics / Risk / Safety** (3)
- **Patient Population Focus** (4)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **LCME Only** (3)
- **LCME + AOA** (10)
- **LCME + AOA + Canadian/Foreign** (7)
- **AMA / AAMC Named Bodies** (7)
- **Board Discretion** (14)
- **Federal/WHO Reference** (4)

#### Exams

`licensure.exams` — states per tag:

- **USMLE / COMLEX Primary** (10)
- **Multi-Exam Menu** (14)
- **State Board Exam** (7)
- **Board-Approved Flexible** (16)
- **USMLE + State Supplement** (3)

#### Foreign medical graduate requirements

`profession_specific.foreign_medical_graduate_requirements` — states per tag:

- **ECFMG + Extended Residency** (13)
- **ECFMG Only / Minimal** (8)
- **ECFMG + Standard Residency** (13)
- **Residency-Focused / No ECFMG Specified** (3)
- **Special Pathway / Limited License** (7)
- **Board Discretion / Flexible** (5)

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

- **AMA Only** (3)
- **AMA + AOA** (6)
- **AOA Only** (2)
- **Accreditation Body** (3)
- **Board/Specialty Focus** (1)
- **Multi-Org Broad** (6)
- **State/Regional Only** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NBME / Osteopathic Boards** (4)
- **ECFMG Only** (8)
- **ABMS / Specialty Boards** (3)
- **Multi-Body (NBME + ECFMG)** (1)
- **Multi-Body (ABMS + Canadian)** (3)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Hard Day-Supply Cap** (6)
- **MME/Dosage Cap** (2)
- **Chronic Pain Standards** (2)
- **Board Guidelines Required** (6)
- **Delegation/Telehealth Limits** (2)
- **Protections for Pain Relief** (2)
- **Schedule-Specific Restrictions** (3)

#### Physician assistant prescriptive authority

`profession_specific.physician_assistant_prescriptive_authority` — states per tag:

- **Broad / Full Schedule II-V** (7)
- **Schedule III-V Only** (3)
- **Schedule II-V with Restrictions** (5)
- **Delegated by Supervising MD** (4)
- **Board/Agreement Defined** (6)
- **No Independent Prescribing** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **IMLC Compact** (4)
- **Equivalent Standards** (20)
- **Equivalent + Active Practice** (11)
- **National Board / Exam** (8)
- **Comprehensive Multi-Factor** (4)
- **Credential Portability Program** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (8)
- **Consumer Affairs** (3)
- **Commerce / Trade** (3)
- **Professional Licensing Div** (5)
- **Labor & Industry** (2)
- **Education Dept** (1)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Prior In-Person Required** (6)
- **Same Standard as In-Person** (6)
- **Controlled Substance Restrictions** (7)
- **Licensure / Jurisdictional Focus** (12)
- **Permissive / Flexible** (6)

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

- **Approved Program Only** (18)
- **HS Diploma + Approved Program** (6)
- **Diploma/Degree, Approved Program** (11)
- **Multi-Level (RN/LPN/APRN Distinct)** (10)
- **Accredited Program Required** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Transition to Practice** (2)
- **Supervised Practice** (1)
- **Collaborative Practice** (1)
- **Supervised/Collaborative** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~1,000 hrs** (1)
- **~2,000 hrs** (2)
- **~2,000 hrs + Agreement** (1)
- **~4,600 hrs / 3 yrs** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Nursing** (19)
- **Named State Board of Nursing** (21)
- **Dept / Agency (non-board)** (4)
- **Board + Dept Joint** (2)
- **Specialized Board Name** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Nursing** (11)
- **State Board of Nursing** (11)
- **Named State Board of Nursing** (20)
- **Board of Examiners** (2)
- **Board of Registration** (3)
- **Dept / Division (non-board)** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Nursing Process + Medications + Teaching** (9)
- **Nursing Process + Delegation + Supervision** (16)
- **Diagnosis + Counseling + Medical Regimen** (6)
- **Broad Enumerated List** (11)
- **Minimal / Execution-Focused** (6)

`scope.drug_authority` — states per tag:

- **RN Administer Only** (13)
- **APRN Prescribe (Independent)** (9)
- **APRN Prescribe (Collaborative)** (6)
- **APRN Prescribe (Delegated)** (2)
- **Mixed RN+APRN Tiers** (12)
- **Narrow/Specific Authority** (2)

`scope.definition_quote` — states per tag:

- **Diagnose & Treat Responses** (5)
- **Nursing Process Centered** (18)
- **Observation, Care & Counsel** (5)
- **Optimal Health Attainment** (9)
- **Broad Collaborative Care** (6)
- **List of Acts** (7)

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
- **Abuse / Trafficking / Safety** (2)
- **Mental Health / Suicide** (1)
- **Broad Multi-Topic Mix** (7)
- **Bias / Cultural Competency** (1)
- **Jurisprudence / Scope** (1)

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
- **National Accreditor** (4)
- **USDOE Recognized** (4)
- **State Board + National** (6)
- **Regional/Legal Agency** (2)

#### Exams

`licensure.exams` — states per tag:

- **NCLEX Only** (28)
- **NCLEX + Jurisprudence** (2)
- **NCLEX + APRN Cert** (5)
- **NCLEX + Jurisprudence + APRN** (0)
- **Board-Prescribed Exam** (10)
- **National Exam (Generic)** (5)

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

- **ANA / General Nursing** (4)
- **Nurse Midwives** (2)
- **Nurse Practitioners** (1)
- **Nurse Anesthetists** (1)
- **State-Level Body** (1)
- **Credentialing / Accreditation** (1)
- **Multi-Association** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCLEX / NCSBN** (4)
- **Named Certifying Body** (4)
- **Board-Approved Body (APRN)** (5)
- **Board-Approved Body (General)** (5)
- **CGFNS International** (1)

#### Opioid prescribing limits

`profession_specific.opioid_prescribing_limits` — states per tag:

- **Short Supply Cap (≤7 days)** (6)
- **Day Supply Cap (>7 days)** (1)
- **MME/Dose Limit** (2)
- **Physician Oversight Required** (3)
- **Dispensing Prohibited** (1)
- **Rules-Based / Referential** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Meet State Standards** (19)
- **Substantially Equivalent** (12)
- **Active Practice Required** (2)
- **Compact + Endorsement** (4)
- **Compact Only** (2)
- **Strict / Multi-Step** (9)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (6)
- **Health Professions Agency** (1)
- **Consumer Affairs** (3)
- **Commerce / Economic Dev** (3)
- **Professional Licensing Office** (4)
- **Labor & Industry** (2)

#### Telehealth prescribing rules

`profession_specific.telehealth_prescribing_rules` — states per tag:

- **Standard of Care Parity** (5)
- **Controlled Substance Restrictions** (4)
- **In-Person Visit Required** (2)
- **Relationship & Consent Required** (2)
- **Collaborative Practice Rules** (3)
- **Board Rules Pending** (2)
- **Broad Telehealth Authorization** (2)

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

- **OD Degree Required** (15)
- **Graduate of Accredited School** (19)
- **Graduate of Board-Approved School** (7)
- **Graduate + Min Years Specified** (8)
- **Board Standards / Equivalency** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Optometry Internship** (1)
- **Supervised Clinical Experience** (1)
- **Ophthalmologist-Supervised Internship** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~100 Hours** (1)
- **6 Months** (1)
- **1 Year** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **State Optometry Board** (28)
- **Board of Examiners** (13)
- **Dept of Health** (5)
- **Other State Agency** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Optometry** (31)
- **Board of Examiners** (13)
- **Board of Registration** (2)
- **Dept / Agency (Non-Board)** (4)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Basic Exam & Lenses** (2)
- **Exam, Lenses & Topical Drugs** (7)
- **Exam, Lenses, Oral & Topical Drugs** (14)
- **Broad Scope + Minor Procedures** (20)
- **Expanded Scope + Surgery/Laser** (7)

`scope.drug_authority` — states per tag:

- **Broad Formulary, Few Exclusions** (7)
- **Topical + Oral, Sched III-V** (6)
- **Topical + Oral, Hydrocodone Allowed** (18)
- **Tiered/Certification Levels** (10)
- **Topical Only or Limited Oral** (2)
- **Board Formulary / Rule-Defined** (7)

`scope.definition_quote` — states per tag:

- **Broad Full Scope** (7)
- **Exam Diagnose Treat** (7)
- **No Surgery Explicit** (13)
- **Surgery Permitted** (4)
- **Narrow / Vision Focus** (4)
- **Enumerated Acts List** (15)

`profession_specific.surgery_definition` — states per tag:

- **Broad Tissue-Alteration Definition** (14)
- **Invasive Procedure + Laser** (8)
- **Anesthesia/Closure-Based Definition** (3)
- **Enumerated Prohibited Procedures** (8)
- **Vague / Minimal Definition** (7)

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
- **Opioid / Substance Use** (6)
- **Therapeutics Certification Add-On** (13)
- **Glaucoma-Specific** (1)
- **Jurisprudence / Admin** (1)
- **Broad Clinical Topics** (2)

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

- **ACOE / AOA** (10)
- **Board-Approved** (15)
- **State Board** (5)
- **US Dept of Ed / CHEA** (4)
- **Regional or Professional Org** (4)

#### Exams

`licensure.exams` — states per tag:

- **NBEO Required** (9)
- **National Exam (Board-Approved)** (10)
- **State Board Exam** (14)
- **State + NBEO Combined** (11)
- **Board Discretion** (6)

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

- **AOA (National)** (8)
- **AOA Accreditation Body** (2)
- **State Optometric Assoc.** (7)
- **Regulatory / Exam Board** (3)

#### National certification

`licensure.national_certification` — states per tag:

- **NBEO** (24)
- **NBEO (IABO variant)** (1)
- **ARBO / CELMO** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards + Practice Hours** (14)
- **Equivalent Standards Only** (14)
- **Equivalent Standards + Exams Required** (12)
- **Board Discretion** (4)
- **Expedited/Endorsement Path** (4)
- **Minimal / General Statement** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (9)
- **Consumer Affairs** (3)
- **Commerce / Economic Dev** (2)
- **Professional Licensing Office** (7)
- **Labor / Regulation Dept** (6)

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

- **DPM Degree** (21)
- **DPM or Equivalent** (7)
- **Graduate of Accredited School** (12)
- **Diploma/Certificate** (5)
- **Four-Year Course** (5)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Podiatric Residency** (18)
- **Residency Program** (5)
- **Postgraduate Training** (9)
- **Residency or Preceptorship** (5)
- **Residency or Fellowship** (2)
- **Residency or Active Practice** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (21)
- **2 Years** (3)
- **3 Years** (2)
- **Residency Required** (4)
- **Flexible / Conditional** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Podiatry Board** (17)
- **Podiatric Medicine Board** (12)
- **Medical Board** (13)
- **Health Department** (4)
- **Multi-Prof Licensing Dept** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Podiatry Board** (22)
- **Podiatric Medicine Board** (12)
- **Medical Board** (13)
- **Other State Agency** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Med/Surg/Mech Core** (16)
- **Med/Surg/Mech + Electrical** (5)
- **Med/Surg/Mech + Manipulative** (7)
- **Broad Enumerated** (7)
- **Diagnosis-Forward** (9)
- **Catch-All / General** (6)

`scope.drug_authority` — states per tag:

- **Broad Prescriptive Authority** (5)
- **Scope-Limited Prescribing** (8)
- **Controlled Substances Explicit** (12)
- **Local Anesthesia Only** (5)
- **Foot/Ankle Conditions Only** (8)

`scope.definition_quote` — states per tag:

- **Foot Only** (8)
- **Foot & Ankle** (24)
- **Foot, Ankle & Leg** (15)
- **Broad / Primary Care** (2)
- **Procedural / Title-Based** (1)

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

- **Full Board Role** (1)
- **Advisory + Rulemaking Input** (1)
- **Advisory + Disciplinary** (1)
- **Advice Only (Broad)** (1)
- **Advice Only (Disciplinary)** (1)

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
- **CPME Approved Board** (1, 1 states)
- **State-Recognized / Generic Body** (3, 3 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substance Prescribing** (7)
- **Substance Use Disorder & Treatment** (2)
- **Opioid + Drug Monitoring Program** (1)
- **Other Mandatory Topics** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **CPME / APMA** (18)
- **APMA Only** (6)
- **Council on Podiatry Education (older)** (6)
- **State Board** (4)
- **Board-Approved Flexibility** (7)

#### National association

`licensure.national_association` — states per tag:

- **APMA** (25)
- **American Podiatry Assoc** (5)
- **CPME / Colleges** (3)
- **Multiple Associations** (1)
- **State Society** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NBPME** (13)
- **ABPS / ABFAS** (7)
- **ABFAS + ABPM (Dual)** (1)
- **APMA / CPME** (3)
- **Specialty Board (General)** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantially Equivalent Standards** (17)
- **Equivalent + Practice History** (8)
- **Equivalent + Mutual Reciprocity** (8)
- **Exam + Endorsement Focus** (6)
- **Broad / Flexible Criteria** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (5)
- **Health Professions Agency** (2)
- **Consumer Affairs** (3)
- **Commerce / Economic Dev** (3)
- **Professional Licensing Div** (7)
- **Labor / Industry** (3)
- **Other State Agency** (2)

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

- **Bach + 150 Hours** (11)
- **Bach + Accounting Concentration** (15)
- **Bach + 150 + Concentration** (15)
- **Bach Degree Only** (6)
- **Board Discretion** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Broad Skills List** (25)
- **Public Practice Only** (10)
- **General Accounting** (7)
- **Multi-Sector Broad** (7)
- **Board-Defined** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (30)
- **2 Years** (3)
- **1–2 Years (Edu-Dependent)** (8)
- **1–3+ Years (Tiered)** (4)
- **Hours-Based** (3)
- **Board Discretion** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Accountancy** (29)
- **Board of Public Accountancy** (11)
- **Board of CPA Examiners** (4)
- **Dept / Division (non-board)** (6)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Accountancy** (30)
- **Board of Public Accountancy** (11)
- **Board of CPA Examiners** (3)
- **Board of Accountants** (2)
- **Dept / Education Dept** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Attest + Advisory + Tax** (30)
- **Attest + Advisory Only** (1)
- **Attest + Compilation Only** (11)
- **Broad Accounting + Tax** (5)
- **Standards-Referenced Scope** (1)

`scope.definition_quote` — states per tag:

- **Attest-Only Definition** (9)
- **Broad Skills + Attest** (14)
- **Broad Skills No Attest** (10)
- **Holding-Out + Broad Skills** (7)
- **Report Issuance Focus** (6)

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
- **Accounting & Auditing Core** (2)
- **Ethics + State Law** (2)
- **Broad Topic List** (1)
- **Attestation / Audit Specialty** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Regional Accreditor** (7)
- **Federal DOE Reference** (6)
- **Business-Specific Accreditor** (1)
- **Board Discretion** (7)
- **State Agency** (1)

#### Exams

`licensure.exams` — states per tag:

- **Uniform CPA Exam Only** (37)
- **Uniform CPA + Ethics Exam** (9)
- **Uniform CPA + Ethics + Other** (1)
- **State/Board-Defined Exam** (3)

#### National association

`licensure.national_association` — states per tag:

- **AICPA Only** (33)
- **AICPA + NASBA** (5)
- **AICPA + PCAOB** (3)
- **NASBA Only** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **AICPA (org only)** (11)
- **Uniform CPA Exam** (2)
- **AICPA + Uniform Exam** (1)
- **AICPA/NASBA Joint** (1)
- **Erroneous Reference** (1)

#### Practice privilege consent conditions

`profession_specific.practice_privilege_consent_conditions` — items per tag:

- **Jurisdiction and Disciplinary Authority** (50, 47 states)
- **Compliance with Laws and Rules** (48, 46 states)
- **Cessation if Home License Invalid** (42, 40 states)
- **Agent for Service of Process** (46, 46 states)
- **Notification and Reporting** (4, 3 states)
- **Scope of Practice Limits** (2, 2 states)
- **Other** (0, 0 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantial Equivalency Only** (7)
- **Substantial Equiv + Experience Fallback** (22)
- **Exam + Experience + CPE** (8)
- **Practice Privileges (No License)** (8)
- **Reciprocal / Comparable License** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Commerce / Consumer Affairs** (4)
- **Professional Licensing Division** (6)
- **Business & Professional Regulation** (1)
- **Labor & Industry** (2)
- **Secretary of State / Dept of State** (2)
- **Governor's Office** (1)

#### Statute of limitations for accountant negligence

`profession_specific.statute_of_limitations_for_accountant_negligence` — states per tag:

- **1-yr Discovery / 3-yr Absolute** (1)
- **2-yr Discovery** (1)

## Public Adjuster

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

