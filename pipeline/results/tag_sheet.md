# Field Tag Sheet

_Generated 2026-08-01T07:08:22+00:00_

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

- **NAAB Accredited Degree** (19)
- **Accredited Degree (Flexible)** (9)
- **Board-Approved Program** (6)
- **Degree or Experience Alt.** (6)
- **Board Discretion** (9)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Named Program (AXP/IDP)** (11)
- **Supervised Practice** (6)
- **General Practical Experience** (16)
- **Diversified/Structured Training** (7)
- **Education or Experience** (3)

`licensure.post_degree_experience.duration` — states per tag:

- **Board Discretion** (2)
- **1–3 Years** (4)
- **Tiered by Education Path** (3)
- **8 Years Combined** (3)
- **10+ Years** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Architecture-Only Board** (24)
- **Arch + Interior Design Board** (11)
- **Multi-Profession Board** (12)
- **Dept / Agency (not a board)** (3)

`licensure.regulatory_authority.name` — states per tag:

- **Architects Only Board** (24)
- **Arch + Interior Design Board** (7)
- **Arch + Landscape Arch Board** (5)
- **Multi-Profession Board** (12)
- **Dept / Division (not a board)** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Basic Triad** (7)
- **Consult + Design + Construct Admin** (20)
- **Full Service + Coordination** (13)
- **Full Service + Engineering** (4)
- **Phased / Process-Oriented** (2)
- **Aesthetics / Tech Focused** (1)

`scope.definition_quote` — states per tag:

- **Human Occupancy Focus** (21)
- **Broad Professional Services** (6)
- **Life/Health/Property Safety** (11)
- **Design + Construction Admin** (9)
- **Registration/Title Only** (3)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Obtaining License** (52, 41 states)
- **Negligence Incompetence Misconduct** (97, 43 states)
- **Criminal Conviction** (38, 35 states)
- **Improper Seal or Signature** (36, 31 states)
- **Aiding Unauthorized Practice** (29, 25 states)
- **Violation of Law or Rules** (96, 49 states)
- **Prior Discipline Elsewhere** (24, 22 states)
- **Substance Abuse or Impairment** (19, 12 states)
- **Deceptive Advertising or Misrepresentation** (43, 24 states)
- **Conflict of Interest or Financial Impropriety** (19, 12 states)
- **Failure to Cooperate or Report** (31, 19 states)

### Other bucketed fields

#### Continuing education excluded topics

`profession_specific.continuing_education_excluded_topics` — items per tag:

- **Course Repetition** (1, 1 states)
- **Business Practice Topics** (2, 1 states)

#### Continuing education subject requirement

`profession_specific.continuing_education_subject_requirement` — items per tag:

- **Health Safety Welfare** (8, 8 states)
- **Building Codes** (1, 1 states)
- **Accessibility Design** (2, 2 states)
- **Sustainability Energy** (2, 2 states)
- **Professional Ethics** (1, 1 states)
- **General Professional Practice** (2, 2 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Health, Safety & Welfare** (6)
- **Technical/Professional Practice** (2)
- **Specific Code/Standard** (3)
- **Ethics** (1)
- **Public Protection** (1)

#### Continuing education waiver conditions

`profession_specific.continuing_education_waiver_conditions` — items per tag:

- **Military Service** (7, 7 states)
- **Illness or Disability** (8, 7 states)
- **Hardship or Emergency** (7, 6 states)
- **Retirement or Inactive** (7, 7 states)
- **New Licensee Exemption** (3, 3 states)
- **Out of State or Country** (2, 1 states)
- **Board Discretion** (7, 7 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **NAAB Only** (23)
- **NAAB + CACB** (2)
- **Board-Approved School** (6)
- **Any National Body** (3)
- **Accreditor Unspecified** (3)

#### Exams

`licensure.exams` — states per tag:

- **NCARB/ARE (Mandatory)** (14)
- **NCARB/ARE (Board May Adopt)** (16)
- **Board-Prescribed Exam** (19)
- **Dual Exam Required** (1)

#### Exempt building types

`profession_specific.exempt_building_types` — items per tag:

- **Single-Family Residential** (44, 35 states)
- **Small Multifamily Residential** (37, 31 states)
- **Agricultural / Farm Buildings** (42, 38 states)
- **Small Commercial / Industrial** (55, 33 states)
- **Nonstructural Alterations** (40, 32 states)
- **Pre-Engineered / Manufactured Buildings** (8, 8 states)
- **Federal / Government Employee Work** (18, 15 states)
- **Other Licensed Professional Work** (40, 24 states)

#### Firm design professional ownership minimum fraction

`profession_specific.firm_design_professional_ownership_minimum_fraction` — states per tag:

- **Two-Thirds Majority** (8)
- **Simple Majority (>50%)** (1)
- **100% Licensed** (1)
- **One Licensed Principal** (1)

#### Firm licensed architect ownership minimum fraction

`profession_specific.firm_licensed_architect_ownership_minimum_fraction` — states per tag:

- **At Least One** (10)
- **One-Third** (2)
- **Majority** (2)
- **Two-Thirds** (4)
- **All Principals/Officers** (1)
- **100% Licensed** (1)

#### National association

`licensure.national_association` — states per tag:

- **NAAB** (14)
- **NCARB** (2)
- **AIA** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCARB** (34)
- **NAAB** (1)
- **Board-Recognized Body** (1)

#### Permitted firm structures

`profession_specific.permitted_firm_structures` — items per tag:

- **Sole Proprietorship** (15, 15 states)
- **General Partnership** (40, 39 states)
- **Limited Partnership** (2, 2 states)
- **Limited Liability Partnership** (11, 11 states)
- **Corporation** (40, 39 states)
- **Professional Corporation** (15, 14 states)
- **Limited Liability Company** (28, 27 states)
- **Association / Trust** (13, 11 states)
- **Other Entity** (20, 20 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **NCARB Required** (5)
- **NCARB or Equivalent** (15)
- **Substantial Equivalence** (18)
- **Reciprocal Privilege Required** (2)
- **Multi-Path with Extras** (9)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Commerce / Economic Dev** (5)
- **Consumer Affairs / Protection** (2)
- **Professional Licensing Agency** (10)
- **Labor & Regulation** (4)
- **Secretary of State / Governor** (2)
- **Education / Health** (2)

#### Unauthorized practice criminal penalty first offense

`profession_specific.unauthorized_practice_criminal_penalty_first_offense` — states per tag:

- **Class A Misdemeanor** (8)
- **Class B/C Misdemeanor** (8)
- **Misdemeanor + Fine Specified** (14)
- **Misdemeanor (General)** (6)
- **Cross-Reference Only** (2)
- **Infraction/Summary** (2)

#### Unauthorized practice criminal penalty subsequent offense

`profession_specific.unauthorized_practice_criminal_penalty_subsequent_offense` — states per tag:

- **Felony** (4)
- **Gross Misdemeanor** (1)
- **Misdemeanor + Fine/Jail** (4)
- **Per-Day Violation** (2)
- **Fine or Jail Only** (1)

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

- **Bachelor's Degree** (1)
- **Trade/Vocational Program** (1)
- **Apprenticeship or Experience** (1)
- **Short Coursework Only** (2)
- **Flexible / Varies** (4)
- **Basic Education (HS or Below)** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General Trade Experience** (4)
- **Classification-Specific Experience** (5)
- **Supervised/Employed Experience** (3)
- **Journeyman/Apprenticeship** (2)
- **Full-Time Employment** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **~2 Years** (4)
- **~4 Years** (3)
- **~5 Years** (1)
- **Tiered by License Class** (3)
- **Varies by Trade** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Contractors Board** (21)
- **Commerce / Regulatory Dept** (8)
- **Labor / Industry Dept** (5)
- **Consumer Protection Agency** (3)
- **Revenue / Secretary of State** (4)
- **Multiple Boards** (1)
- **Local Jurisdiction Only** (2)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Contractors Board** (23)
- **Dept of Labor / Industry** (5)
- **Consumer Protection Agency** (3)
- **Broad Licensing Dept** (6)
- **Local / County Authority** (2)
- **Other State Agency** (5)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **General CRUD Verbs** (19)
- **Broad + Specialty Mix** (6)
- **Residential-Focused** (2)
- **Trade-Specific Lists** (6)
- **Engineering/Building/Specialty Tiers** (3)
- **Narrow/Niche Scope** (1)

`scope.definition_quote` — states per tag:

- **Broad General Contractor** (20)
- **Residential / Home Improvement** (8)
- **Trade-Specific Only** (6)
- **Cost-Threshold Based** (5)
- **Reference to External Standard** (2)
- **Minimal / Narrow Definition** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (112, 38 states)
- **Negligence & Incompetence** (43, 24 states)
- **Contract Performance Failures** (40, 21 states)
- **Financial Misconduct** (43, 23 states)
- **License Misuse & Unlicensed Activity** (94, 33 states)
- **Regulatory & Law Violations** (83, 36 states)
- **Insurance Bond & Financial Requirements** (25, 19 states)
- **Criminal Conviction** (23, 19 states)
- **Administrative & Procedural Violations** (83, 31 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Full Licensing Authority** (1)
- **Licensing with Board Approval** (1)
- **Advisory + Enforcement Powers** (3)
- **Recommend Only** (2)
- **Advise on Regulations Only** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Residential Contractor Body** (3)
- **Multiple Trade Boards** (2)
- **General Construction Advisory** (2)
- **Single Trade/Specialty Board** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Codes & Laws Focus** (3)
- **Business & Safety Mix** (2)
- **Trade-Specific Tracks** (2)
- **Board-Approved Curriculum** (2)
- **Broad Topic Menu** (2)

#### Deposit cap fraction

`profession_specific.deposit_cap_fraction` — states per tag:

- **10% or $1,000** (2)
- **One-Third (~33%)** (3)
- **One-Half (50%)** (2)
- **Conditional / Trigger-Based** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **College/University Only** (1)
- **DOL or DOE Accredited** (1)
- **Division-Approved College** (1)

#### Exams

`licensure.exams` — states per tag:

- **State Board Exam** (17)
- **State Exam (Multi-Trade)** (7)
- **National/ICC Exam** (1)
- **Business & Law Exam** (2)
- **Optional/Local Exam** (1)

#### National association

`licensure.national_association` — states per tag:

- **Home Inspector Orgs** (0)
- **Code Council Only** (1)
- **Elevator Industry Orgs** (0)
- **General Contractors / Builders** (1)
- **Mixed Multi-Trade** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NICET Only** (2)
- **NICET + Fire Sprinkler Orgs** (1)
- **NICET (Specific Level)** (1)
- **Crane Operator (NCCCO)** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Agreement Required** (8)
- **Substantially Equivalent Standards** (12)
- **Expedited/Endorsement Path** (2)
- **Exam Waiver Available** (4)
- **Experience Credit Only** (1)
- **Military/Emergency Only** (3)
- **Local/Intra-State Only** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Consumer Affairs** (3)
- **Business & Professional Reg** (3)
- **Licensing & Regulatory Affairs** (4)
- **Commerce Dept** (3)
- **Secretary / Attorney General** (2)
- **Governor / Cabinet Office** (2)

#### Voidable contract clauses

`profession_specific.voidable_contract_clauses` — items per tag:

- **Waiver of Statutory Rights** (3, 2 states)
- **Waiver of Legal Remedies** (3, 1 states)
- **Liability Release Clause** (2, 1 states)
- **Confession of Judgment** (2, 2 states)
- **Payment or Wage Assignment** (1, 1 states)
- **Complaint or Regulatory Bar** (1, 1 states)
- **Contract Formality Defect** (3, 3 states)

## Dentistry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **DDS/DMD + CODA Accredited** (16)
- **CODA Accredited (Degree Unspecified)** (24)
- **Board-Approved School** (7)
- **Doctoral Degree in Dentistry** (3)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General or Specialty Residency** (2)
- **CODA-Approved Residency** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Dental Examiners** (12)
- **Board of Dentistry** (21)
- **State Dental Board** (8)
- **Dept / Agency (no board)** (5)
- **Shared Authority** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Dental Examiners** (13)
- **Board of Dentistry** (20)
- **Dental Board** (6)
- **Dept / Office (Non-Board)** (5)
- **Other Named Board** (6)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad Enumerated List** (16)
- **Core Four Only** (4)
- **Surgical/Nonsurgical Framework** (12)
- **Moderate Detail** (11)
- **Extended + Emerging Tech** (7)

`scope.drug_authority` — states per tag:

- **Broad Prescribe & Dispense** (5)
- **Prescribe + Opioid Limits** (8)
- **Prescribe + Anesthesia Permits** (11)
- **Basic Prescribe Authority** (19)
- **Anesthesia/Sedation Focus** (2)
- **Delegation & Vaccines Emphasis** (5)

`scope.definition_quote` — states per tag:

- **ADA-Style Modern** (15)
- **Diagnosis & Treatment List** (12)
- **Holds-Out / Represents** (8)
- **Performs Operations** (9)
- **Healing Art** (4)
- **Minimal / Circular** (2)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (171, 50 states)
- **Criminal Conviction** (64, 43 states)
- **Clinical Incompetence & Negligence** (98, 42 states)
- **Unprofessional & Immoral Conduct** (136, 47 states)
- **Substance Abuse & Impairment** (59, 43 states)
- **Physical & Mental Incapacity** (46, 36 states)
- **Unlicensed Practice & Improper Delegation** (109, 48 states)
- **Advertising Violations** (63, 38 states)
- **Regulatory & Reporting Noncompliance** (260, 49 states)

### Other bucketed fields

#### Advanced practice eligible patient populations

`profession_specific.advanced_practice_eligible_patient_populations` — items per tag:

- **Long-Term Care Facilities** (35, 21 states)
- **Schools and Early Childhood Programs** (36, 22 states)
- **Community and Public Health Clinics** (60, 23 states)
- **Hospitals and Medical Facilities** (20, 14 states)
- **Homebound Individuals** (16, 14 states)
- **Correctional Facilities** (13, 10 states)
- **Underserved and Low-Income Populations** (19, 14 states)
- **Group and Residential Homes** (29, 14 states)
- **Mobile and Outreach Programs** (7, 7 states)

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Discipline & Policy Advice** (1)
- **Hygiene Licensing & Discipline** (1)
- **Discipline Only** (0)
- **Policy Advice Only** (0)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Dental Commission** (1)
- **Dental Hygiene Advisory** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substances** (9)
- **CPR/Emergency Skills** (4)
- **Ethics & Professionalism** (2)
- **Broad Multi-Topic Mandate** (7)
- **Infection Control Focus** (0)
- **Clinical Hours Requirement** (1)

#### Dental hygienist supervision levels

`profession_specific.dental_hygienist_supervision_levels` — items per tag:

- **Direct Supervision** (49, 48 states)
- **Indirect Supervision** (18, 18 states)
- **General Supervision** (44, 44 states)
- **Public Health Supervision** (5, 5 states)
- **Collaborative/Advanced Practice** (3, 3 states)
- **Telehealth Supervision** (3, 3 states)
- **Unsupervised Practice** (6, 6 states)

#### Dental therapist practice setting restrictions

`profession_specific.dental_therapist_practice_setting_restrictions` — items per tag:

- **Federally Qualified Health Centers** (10, 5 states)
- **Tribal & Indian Health Facilities** (5, 4 states)
- **Hospital & Medical Facilities** (5, 4 states)
- **School & Educational Settings** (7, 6 states)
- **Long-Term & Home Care Settings** (8, 4 states)
- **Nonprofit & Community Clinics** (8, 6 states)
- **Correctional Facilities** (2, 2 states)
- **Mobile & Underserved Practice** (7, 4 states)
- **Agreement-Defined Settings** (7, 6 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **CODA / ADA (full name)** (33)
- **CODA only** (10)
- **ADA only** (2)
- **Board-defined** (2)
- **Any Recognized Accreditor** (1)

#### National association

`licensure.national_association` — states per tag:

- **ADA Only** (29)
- **ADA + CODA** (17)
- **CODA Only** (2)
- **State Association** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **JCNDE** (6)
- **NBDE / NBDE-named** (3)
- **ADEX** (2)
- **ABOMS** (3)
- **Multiple Bodies** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Active Practice + Good Standing** (22)
- **Equivalent Standards Only** (8)
- **Jurisprudence Exam Required** (11)
- **Reciprocity Prohibited / Limited** (1)
- **Military / Special Pathway Only** (3)
- **Compact / Portability Program** (3)
- **Minimal / Procedural Requirements** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (8)
- **Consumer Affairs / Commerce** (5)
- **Licensing & Regulation** (5)
- **Professional Regulation Office** (3)
- **Labor & Industry** (2)

#### Sedation anesthesia permit types

`profession_specific.sedation_anesthesia_permit_types` — items per tag:

- **General Anesthesia** (33, 33 states)
- **Deep Sedation** (21, 21 states)
- **Moderate Sedation** (45, 35 states)
- **Minimal Sedation / Anxiolysis** (10, 10 states)
- **Nitrous Oxide / Inhalation Analgesia** (12, 12 states)
- **Local Anesthesia** (10, 9 states)
- **Facility / Office Permit** (3, 3 states)
- **Specialty / Other Permit** (13, 10 states)

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

- **No Degree Required** (3)
- **Apprenticeship / Training Only** (5)
- **Coursework Hours Required** (3)
- **Degree as Alternative Pathway** (6)
- **Multiple Tiered Pathways** (3)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Journeyman Experience** (11)
- **Supervised Field Work** (4)
- **Apprenticeship Program** (5)
- **General Trade Experience** (12)
- **Management / Supervisory** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **~1 Year** (2)
- **2–3 Years** (3)
- **4 Years** (5)
- **4–6 Years (Tiered)** (3)
- **6–8 Years / Hours Equiv** (2)
- **Multi-Tier by License Class** (19)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Electrical-Specific Board** (18)
- **General Contractors Board** (12)
- **Dept of Labor / Industry** (4)
- **Occupational Licensing Agency** (9)
- **Consumer / Business Services Dept** (2)

`licensure.regulatory_authority.name` — states per tag:

- **Electrical-Specific Board** (21)
- **General Contractors Board** (9)
- **State Dept / Agency** (10)
- **Construction Industry Board** (3)
- **Multi-Trade Board** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install & Repair Core** (6)
- **Install, Repair & Maintain** (14)
- **Install, Repair, Plan & Supervise** (10)
- **Broad Scope + Specialty Systems** (9)
- **Contracting Categories** (2)

`scope.definition_quote` — states per tag:

- **Work-Focused Definition** (19)
- **Person/Role Definition** (13)
- **Contractor Business Definition** (8)
- **General Contractor Broad Def** (4)
- **License/Category Reference** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud or Misrepresentation** (80, 39 states)
- **Incompetence or Negligence** (40, 31 states)
- **Criminal Conviction** (18, 17 states)
- **Regulatory or Code Violation** (83, 40 states)
- **License Misuse or Unlicensed Practice** (89, 32 states)
- **Contract or Financial Misconduct** (29, 13 states)
- **Administrative Non-Compliance** (82, 30 states)
- **Substance Abuse or Fitness** (4, 4 states)
- **Out-of-State Discipline** (7, 7 states)

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
- **Board-Set / By Rule** (2)

#### Approved continuing education providers

`profession_specific.approved_continuing_education_providers` — items per tag:

- **Named Trade Associations** (18, 6 states)
- **Academic Institutions** (5, 5 states)
- **Apprenticeship Programs** (2, 2 states)
- **Government Agency Providers** (3, 3 states)
- **Board Approved Generic** (16, 14 states)
- **Specialty Technical Programs** (4, 4 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **NEC Only** (4)
- **NEC + Broad Electrical Topics** (7)
- **NEC + Business/Safety Mix** (3)
- **Broad Electrical Topics** (1)
- **General/Vague** (4)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Accredited College/University** (5)
- **State Apprenticeship Board** (2)
- **Federal Apprenticeship (USDOL)** (1)
- **State Career/Tech Agency** (1)
- **Multiple / Flexible** (3)
- **Single State Institution** (1)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Apprentice / Trainee** (33, 22 states)
- **Journeyman / Journey Level** (50, 32 states)
- **Master Electrician** (31, 21 states)
- **Electrical Contractor** (63, 37 states)
- **Specialty / Limited Scope** (79, 28 states)
- **Administrator / Supervisor** (10, 5 states)
- **Inspector / Other** (4, 4 states)

#### National association

`licensure.national_association` — states per tag:

- **Standards Body** (1)
- **Fire/Safety Code Org** (1)
- **Trade & Labor Coalition** (1)
- **Regional Trade Council** (1)

#### Qualifier license requirement by contractor type

`profession_specific.qualifier_license_requirement_by_contractor_type` — items per tag:

- **Master Electrician Required** (19, 16 states)
- **Journeyman Electrician Required** (2, 2 states)
- **Specialty License Required** (18, 11 states)
- **Examination Required** (12, 6 states)
- **Experience Required** (3, 1 states)
- **Entity Type Qualifier Rule** (11, 8 states)
- **Supervising Electrician Required** (2, 1 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards + Mutual** (14)
- **Equivalent Standards Only** (11)
- **Formal Agreement Required** (6)
- **Universal/Endorsement Path** (3)
- **Extra Experience Required** (5)
- **Exam-Focused** (4)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Labor & Industry** (6)
- **Licensing & Regulation** (6)
- **Consumer Affairs** (3)
- **Commerce** (3)
- **Professional Regulation** (3)
- **Safety & Construction** (5)
- **Other Agency** (3)

#### Residential project definition

`profession_specific.residential_project_definition` — states per tag:

- **Single-Family Only** (1)
- **Up to Duplex/2-Unit** (1)
- **Up to 4 Units** (3)
- **Multi-Unit + Story Limit** (7)
- **By Wiring Type/Voltage** (1)
- **Broad Residential Scope** (5)
- **Farm & Residential** (2)

#### Scope exclusions

`profession_specific.scope_exclusions` — items per tag:

- **Utility and Grid Work** (69, 41 states)
- **Telecom and Low-Voltage Systems** (82, 34 states)
- **Owner and Homeowner Work** (59, 36 states)
- **Industrial and In-Plant Work** (50, 29 states)
- **Other Licensed Trade Work** (80, 34 states)
- **Agricultural and Farm Work** (14, 14 states)
- **Vehicles, Vessels, and Mobile Equipment** (21, 16 states)
- **Government and Public Entity Work** (42, 25 states)
- **Minor, Portable, and Incidental Work** (99, 38 states)

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
- **Degree Substitutes for Experience** (2)
- **Board-Defined Standards** (3)
- **Minimal Hours Only** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **General Trade Work** (7)
- **Supervised Field Work** (3)
- **Apprenticeship / Journeyman Path** (5)
- **Licensed Employer Employment** (3)
- **Board-Defined Rules** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~1–2 Years** (4)
- **~3 Years** (1)
- **~4 Years** (6)
- **~5 Years** (2)
- **Hours-Based** (2)
- **Tiered by License Type** (3)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **HVAC-Specific Board** (7)
- **General Contractor Board** (12)
- **Construction Industry Board** (5)
- **Dept of Labor / Licensing** (8)
- **Plumbing & Mechanical Board** (2)
- **Consumer / Professional Office** (6)

`licensure.regulatory_authority.name` — states per tag:

- **HVAC-Specific Board** (8)
- **General Contractors Board** (11)
- **Construction Industry Board** (5)
- **Dept of Labor / Licensing** (10)
- **Plumbing & Mechanical Board** (3)
- **Consumer / Other Agency** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install & Repair Core** (7)
- **Full Lifecycle (+ Design)** (8)
- **Install / Alter / Service** (8)
- **Construction & Demolition** (4)
- **Systems-Based Scope** (1)
- **Inspect & Verify Included** (1)
- **Multi-Trade Scope** (2)

`scope.definition_quote` — states per tag:

- **HVAC-Specific Definition** (18)
- **Broad Mechanical/Trade Scope** (9)
- **Specialty Contractor (Generic)** (4)
- **General Contractor (Generic)** (5)
- **License/Registration Focus** (3)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (87, 34 states)
- **Incompetence & Negligence** (35, 23 states)
- **Criminal Conviction** (15, 13 states)
- **Contract & Financial Violations** (48, 19 states)
- **Unlicensed or Unauthorized Practice** (71, 31 states)
- **Regulatory & Code Violations** (74, 29 states)
- **Insurance & Bond Failures** (15, 11 states)
- **Administrative Non-Compliance** (67, 29 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advise + Examine** (1)
- **Advise on Rules/Ads** (1)
- **Advise on Implementation** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Mechanical Examiners Committee** (1)
- **AC & Refrigeration Board** (1)
- **Residential Contractor Advisors** (1)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Refrigerant/Environmental** (1)
- **Code & Regulatory Focus** (2)
- **Business & Safety Mix** (3)
- **Trade-Specific Hours** (1)
- **Board-Defined Curriculum** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Manufacturer / College** (1)
- **DOL + Trade/Community College** (1)

#### Exams

`licensure.exams` — states per tag:

- **State Board Exam** (24)
- **State Exam + Business/Law** (4)
- **Two-Part Exam** (1)
- **Industry Standardized** (1)
- **Business/Law Only** (1)
- **Voluntary Exam** (1)

#### Financial responsibility demonstration methods

`profession_specific.financial_responsibility_demonstration_methods` — items per tag:

- **Surety Bond** (20, 19 states)
- **Cash or Deposit Equivalent** (7, 5 states)
- **General Liability Insurance** (19, 18 states)
- **Workers Compensation Insurance** (6, 6 states)
- **Net Worth or Financial Statement** (5, 5 states)
- **Letter of Credit** (2, 2 states)
- **Other Proof** (4, 4 states)

#### National certification

`licensure.national_certification` — states per tag:

- **EPA Refrigerant Cert** (1)
- **NICET Certification** (1)

#### Qualifier license type required

`profession_specific.qualifier_license_type_required` — items per tag:

- **Master HVACR License** (8, 6 states)
- **Mechanical Contractor License** (7, 7 states)
- **Air Conditioning Contractor License** (5, 2 states)
- **Heating Group License** (3, 1 states)
- **Conditioned Air Contractor License** (2, 1 states)
- **Fuel Gas License** (3, 1 states)
- **Specialty Trade License** (7, 5 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Reciprocity Required** (6)
- **Equivalent Standards Only** (9)
- **Exam Waiver Available** (6)
- **Endorsement / Flexible** (5)
- **Emergency / Temporary Only** (2)
- **Agreement-Based** (2)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Labor & Licensing Dept** (6)
- **Commerce Dept** (2)
- **Consumer Affairs Dept** (3)
- **Professional Regulation Div** (9)
- **Health / Governor / Other** (2)

#### System components included

`profession_specific.system_components_included` — items per tag:

- **Heating Systems** (27, 19 states)
- **Cooling and Refrigeration** (34, 15 states)
- **Ventilation and Air Distribution** (33, 14 states)
- **Ductwork and Plenums** (12, 9 states)
- **Piping and Hydronic Systems** (24, 11 states)
- **Gas and Fuel Systems** (21, 13 states)
- **Controls and Accessories** (24, 10 states)
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

- **OD Degree + Accredited School** (8)
- **Graduate of Accredited School** (18)
- **Graduate of Board-Approved School** (8)
- **OD Degree + Board-Approved School** (6)
- **Graduate + Minimum Years Specified** (8)
- **Board Standards / Equivalency** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Ophthalmologist-Supervised Internship** (1)
- **Optometric Internship** (1)
- **Supervised Clinical Experience** (1)
- **Board Discretion** (1)

`licensure.post_degree_experience.duration` — states per tag:

- **~100 Hours** (1)
- **6 Months** (1)
- **1 Year** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **State Board of Optometry** (14)
- **Board of Examiners in Optometry** (12)
- **Named Optometry Board** (15)
- **Shared / Dual Authority** (5)
- **State Dept / Agency** (4)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Optometry** (30)
- **Board of Examiners in Optometry** (9)
- **Board of Optometric Examiners** (2)
- **State Dept / Agency** (5)
- **Other Optometry Board** (4)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Basic Exam & Lenses** (4)
- **Exam + Pharma + Foreign Body** (19)
- **Broad Diagnostic & Therapeutic** (13)
- **Includes Minor Surgery** (8)
- **Includes Laser Procedures** (6)

`scope.drug_authority` — states per tag:

- **Broad Formulary, Few Limits** (6)
- **Sched III–V + Hydrocodone** (20)
- **Sched III–V Only** (8)
- **Topical + Limited Oral** (1)
- **Tiered/Cert-Based Levels** (9)
- **Board Formulary by Rule** (6)

`scope.definition_quote` — states per tag:

- **Broad Full Scope** (11)
- **Exam + Dx + Tx, No Surgery** (21)
- **Exam + Dx + Tx, Surgery Permitted** (3)
- **Exam + Refraction Focus** (11)
- **Concise Catch-All** (4)

`profession_specific.surgery_definition` — states per tag:

- **Broad Tissue-Alteration Definition** (15)
- **Enumerated Prohibited Procedures** (9)
- **Laser-Focused Definition** (5)
- **Scope Exclusion Only** (7)
- **Partial Exceptions Carved Out** (3)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (129, 48 states)
- **Criminal Conviction** (48, 42 states)
- **Clinical Incompetence & Negligence** (88, 46 states)
- **Substance Abuse & Impairment** (49, 36 states)
- **Physical & Mental Incapacity** (38, 30 states)
- **Unlicensed Practice & Supervision** (84, 44 states)
- **False & Deceptive Advertising** (63, 35 states)
- **Improper Fees & Financial Misconduct** (45, 31 states)
- **Regulatory & Reporting Violations** (222, 50 states)
- **Sexual & Serious Misconduct** (46, 31 states)

### Other bucketed fields

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Pharmacology / Therapeutics** (5)
- **Ocular Disease & Treatment** (2)
- **Opioid / Substance Use** (5)
- **Certification-Tiered Requirements** (12)
- **Mixed / Multiple Topics** (5)

#### Controlled substance schedule restrictions

`profession_specific.controlled_substance_schedule_restrictions` — items per tag:

- **Schedule I Prohibited** (20, 20 states)
- **Schedule II Prohibited** (15, 15 states)
- **Schedule II Hydrocodone Exception** (17, 17 states)
- **Schedules III–V Authorized** (18, 11 states)
- **Schedules III–V Limited Supply** (14, 11 states)
- **Route or Drug Class Restriction** (21, 14 states)
- **All Controlled Substances Prohibited** (4, 3 states)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ACOE / AOA** (9)
- **State Board** (11)
- **Board-Approved School** (21)
- **US Dept of Ed / CHEA** (6)
- **Other Named Body** (1)

#### Exams

`licensure.exams` — states per tag:

- **NBEO Required** (6)
- **National Exam (Board-Approved)** (6)
- **State Board Exam** (9)
- **State + National Combo** (21)
- **Board Discretion** (8)

#### Laser procedures authorized

`profession_specific.laser_procedures_authorized` — items per tag:

- **Laser Capsulotomy** (7, 7 states)
- **Laser Trabeculoplasty** (6, 6 states)
- **Laser Iridotomy** (4, 4 states)
- **Broad/General Authorization** (3, 3 states)
- **Diagnostic Laser Use** (2, 2 states)
- **Other Laser Procedures** (1, 1 states)

#### Minor surgical procedures authorized

`profession_specific.minor_surgical_procedures_authorized` — items per tag:

- **Foreign Body Removal** (38, 33 states)
- **Eyelash Epilation** (14, 14 states)
- **Corneal Procedures** (17, 10 states)
- **Lacrimal System Procedures** (24, 15 states)
- **Injections** (25, 16 states)
- **Eyelid Lesion Surgery** (22, 10 states)
- **Light and Device Therapy** (5, 3 states)
- **Other Ocular Procedures** (14, 11 states)

#### National association

`licensure.national_association` — states per tag:

- **AOA (General)** (6)
- **ACOE / Accreditation Body** (5)
- **ARBO / Regulatory Body** (1)
- **State Society** (1)
- **IABEO / Exam Board** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NBEO** (25)
- **ARBO / CELMO** (1)
- **IABEO** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalency + Practice History** (10)
- **Equivalency + Exam Required** (5)
- **Good Standing + Minimal Conditions** (13)
- **Detailed Multi-Criteria** (12)
- **Board Discretion / Rule-Based** (5)
- **Reciprocal Agreement Required** (5)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (7)
- **Consumer Affairs** (3)
- **Licensing & Regulatory** (4)
- **Commerce Dept** (2)
- **Professional Regulation Office** (5)
- **Labor & Industry** (2)
- **Secretary of State** (1)

#### Specialty certification types

`profession_specific.specialty_certification_types` — items per tag:

- **Diagnostic Pharmaceutical Agents** (16, 16 states)
- **Therapeutic Pharmaceutical Agents** (36, 36 states)
- **Oral Pharmaceutical Agents** (6, 6 states)
- **Glaucoma Specialty Certification** (7, 7 states)
- **Laser and Surgical Procedures** (6, 6 states)
- **Immunization and Injection Authority** (5, 5 states)
- **Advanced Procedures Endorsement** (2, 2 states)

#### Tiered license types

`profession_specific.tiered_license_types` — items per tag:

- **Basic License** (21, 21 states)
- **Diagnostic Drug Certification** (19, 19 states)
- **Therapeutic Drug Certification** (39, 35 states)
- **Glaucoma Specialty Certification** (6, 6 states)
- **Advanced Procedures Authorization** (12, 11 states)
- **Temporary / Provisional License** (11, 8 states)
- **Faculty / Teaching License** (5, 5 states)
- **Volunteer / Retired License** (6, 4 states)

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

- **No Degree Required** (3)
- **Apprenticeship / OJT** (5)
- **Trade School / Community College** (4)
- **Bachelor's Degree Option** (2)
- **Basic Schooling (HS/8th grade)** (2)
- **Board-Defined Requirements** (1)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Formal Apprenticeship** (9)
- **Supervised On-the-Job** (11)
- **General Trade Experience** (9)
- **Journeyman Experience** (3)

`licensure.post_degree_experience.duration` — states per tag:

- **~1–2 Years** (5)
- **~3–4 Years** (11)
- **~5+ Years** (5)
- **Hours-Based (<6000 hrs)** (2)
- **Hours-Based (6000+ hrs)** (1)
- **Tiered (Years + Hours)** (6)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Dedicated Plumbing Board** (18)
- **General Contractors Board** (11)
- **Dept of Labor / Commerce** (8)
- **Health / Public Safety Dept** (4)
- **Mixed Trade Board** (3)
- **Local Authority** (1)

`licensure.regulatory_authority.name` — states per tag:

- **Dedicated Plumbing Board** (19)
- **Broad Contractors Board** (10)
- **Dept of Labor / Licensing** (5)
- **Dept of Health / Public Safety** (4)
- **Multi-Trade Board** (5)
- **Dept of Commerce / Consumer** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Install / Repair / Replace** (4)
- **Install / Alter / Repair / Maintain** (15)
- **Install / Alter / Repair / Maintain / Design** (7)
- **Broad Construction Scope** (6)
- **Extended Systems Scope** (6)

`scope.definition_quote` — states per tag:

- **Detailed Plumbing Scope** (20)
- **Broad Contractor Scope** (4)
- **System-Listed Scope** (9)
- **License/Role Definition** (5)
- **Minimal or Vague Scope** (7)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud or Misrepresentation** (71, 38 states)
- **Incompetence or Negligence** (50, 32 states)
- **Criminal Conviction** (19, 19 states)
- **Regulatory or Code Violation** (75, 39 states)
- **License Misuse or Transfer** (27, 19 states)
- **Contract or Financial Misconduct** (29, 9 states)
- **Unlicensed Practice or Aiding** (35, 22 states)
- **Substance Use or Impairment** (6, 5 states)
- **Administrative Non-Compliance** (67, 32 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Rules & Exams Only** (2)
- **Rules Advisory** (3)
- **Advisory + Enforcement** (1)
- **Advisory + Hearings** (2)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Plumbing Examiners Board** (4)
- **Plumbers Advisory Board** (1)
- **Plumbers Council** (1)
- **Backflow Advisory Board** (1)
- **Broader Construction Board** (1)

#### Apprentice supervision requirement

`profession_specific.apprentice_supervision_requirement` — states per tag:

- **Direct On-Site Required** (10)
- **Personal Supervision Required** (5)
- **General Supervision** (14)
- **Ratio Limit Specified** (3)
- **Tiered by Experience** (2)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Code Updates** (4)
- **Broad Trade Topics** (2)
- **Safety / Energy Focus** (3)
- **Business & Compliance Mix** (1)

#### Contractor qualifier license requirement

`profession_specific.contractor_qualifier_license_requirement` — states per tag:

- **Master Plumber Required** (24)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **State Apprenticeship Council** (1)
- **Workforce/Training Board** (1)
- **Board/Dept Approval** (2)
- **Accredited College** (1)

#### Exams

`licensure.exams` — states per tag:

- **Master + Journey Exams** (24)
- **Journey Exam Only** (4)
- **Master Exam Only** (2)
- **Contractor Exam Only** (8)
- **Multi-Tier + Contractor** (4)
- **Local Board Exam** (2)

#### Journeyman experience pathways

`profession_specific.journeyman_experience_pathways` — items per tag:

- **Registered Apprenticeship Program** (19, 19 states)
- **Supervised Work Experience** (27, 24 states)
- **Academic or Technical Training** (15, 11 states)
- **Military Training or Service** (4, 4 states)
- **Out-of-State Licensure or Reciprocity** (5, 5 states)
- **Examination Requirement** (4, 4 states)
- **Board Discretion or Equivalency** (8, 8 states)

#### License tiers

`profession_specific.license_tiers` — items per tag:

- **Apprentice / Trainee** (40, 28 states)
- **Journeyman** (41, 35 states)
- **Master Plumber** (34, 26 states)
- **Contractor / Business License** (45, 27 states)
- **Gas Fitter** (13, 6 states)
- **Specialty / Limited Scope** (34, 17 states)
- **Endorsement / Add-On** (6, 4 states)

#### National certification

`licensure.national_certification` — states per tag:

- **NITC** (2)
- **NICET** (1)
- **Propane/Gas Assoc.** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Mutual Recognition Required** (13)
- **Substantial Equivalence Only** (10)
- **Equivalence + Experience Minimum** (9)
- **Formal Agreement / Discretionary** (3)
- **Universal / Umbrella Act** (3)
- **Restricted / Limited Scope** (1)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Consumer Affairs** (3)
- **Professional Licensing** (10)
- **Labor & Industry** (4)
- **Commerce** (2)
- **Business Regulation** (1)
- **Public Safety / Health** (3)
- **Secretary of State** (1)

## Podiatry

### Priority fields

#### Minimum Degree

`licensure.education.degree_required` — states per tag:

- **DPM Degree Named** (17)
- **Graduate of Accredited School** (14)
- **Diploma/Certificate of Graduation** (5)
- **Graduate + Hour/Year Requirements** (8)
- **Board-Approved School** (6)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Podiatric Residency** (16)
- **Residency Program** (6)
- **CPME-Approved Residency** (2)
- **Postgraduate Training** (8)
- **Residency or Preceptorship** (5)
- **Board-Approved Program** (3)
- **Flexible / Board Discretion** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (22)
- **2 Years** (4)
- **3 Years** (2)
- **Tiered / Conditional** (2)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Podiatry-Specific Board** (31)
- **Medical Board** (13)
- **State Health/Reg Agency** (6)

`licensure.regulatory_authority.name` — states per tag:

- **Podiatry-Specific Board** (32)
- **Medical Board** (13)
- **State Health/Other Agency** (5)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Med + Surg + Mech** (20)
- **Med + Surg + Mech + Electrical/Manip** (11)
- **Diagnosis-Forward List** (10)
- **Broad/Open-Ended** (5)
- **Detailed Enumeration** (4)

`scope.drug_authority` — states per tag:

- **Local Anesthetic Only** (5)
- **Broad Prescribing w/ Controlled Substances** (13)
- **General Prescribing, Scope-Limited** (21)
- **Controlled Substances w/ Opioid Limits** (5)
- **Prescribing + Dispensing Authority** (5)

`scope.definition_quote` — states per tag:

- **Foot Only** (9)
- **Foot & Ankle** (16)
- **Foot, Ankle & Leg** (18)
- **Broad Lower Extremity** (6)
- **Title/Holding-Out Based** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud & Misrepresentation** (139, 46 states)
- **Criminal Conviction** (59, 44 states)
- **Clinical Negligence & Incompetence** (67, 39 states)
- **Substance Abuse & Impairment** (51, 43 states)
- **Mental or Physical Disability** (46, 33 states)
- **Unprofessional & Unethical Conduct** (153, 47 states)
- **Drug Prescribing Violations** (47, 32 states)
- **Advertising Violations** (49, 36 states)
- **Regulatory & Administrative Violations** (171, 47 states)
- **Other Jurisdiction Action** (33, 32 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advise & Recommend Only** (2)
- **Advise + Disciplinary Role** (2)
- **Rule Proposal Authority** (1)
- **Advise + Exam/School Oversight** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Full Board** (1)
- **Advisory Board** (1)
- **Advisory Committee** (3)
- **Review Committee** (1)

#### Board certification body

`profession_specific.board_certification_body` — items per tag:

- **ABFAS (Foot and Ankle Surgery)** (4, 4 states)
- **ABPS (Podiatric Surgery)** (6, 6 states)
- **ABPM (Podiatric Medicine)** (2, 2 states)
- **ABOS / Orthopedic Surgery Boards** (2, 1 states)
- **ABMSP / Multi-Specialty Podiatry** (1, 1 states)
- **CPME / Education Council** (1, 1 states)
- **Generic / State-Discretion Board** (2, 2 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Opioid/Controlled Substance Prescribing** (8)
- **Substance Use & Addiction** (1)
- **Infection Control** (1)
- **Patient Safety & Error Prevention** (0)
- **Multi-Topic Required** (1)
- **Accreditation/Format Rules** (2)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **APMA (org name only)** (5)
- **CPME / Council on Education** (20)
- **Board-Approved School** (10)
- **State Board Authority** (6)
- **Recognized National Org** (2)

#### National association

`licensure.national_association` — states per tag:

- **APMA** (27)
- **CPME** (3)
- **American Podiatry Association** (5)
- **State/Local Association** (2)

#### National certification

`licensure.national_certification` — states per tag:

- **NBPME** (14)
- **NBPME (alt name)** (7)
- **ABFAS** (3)
- **ABPS / Surgery Board** (3)
- **Multiple Boards** (2)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantially Equivalent Standards** (16)
- **Active Practice Required** (12)
- **Mutual Reciprocity Required** (7)
- **National Exam + Full Credentials** (7)
- **Broad Portability / Endorsement** (6)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Dept of Health** (8)
- **Consumer Affairs / Commerce** (5)
- **Licensing & Regulatory Affairs** (5)
- **Professional Licensing Division** (3)
- **Labor & Industry** (2)
- **Dept of State / Secretary of State** (2)

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

- **ABET-Accredited 4-Year** (13)
- **Board-Approved 4-Year** (21)
- **Baccalaureate Degree** (6)
- **Multiple Pathways** (6)
- **Flexible / Experience-Based** (3)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Progressive Experience** (12)
- **General Engineering Work** (18)
- **Supervised Experience** (8)
- **Responsible Charge** (6)
- **Qualifying Experience** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **4 Years (Standard)** (25)
- **4–8 Years (Tiered by Degree)** (4)
- **6–8 Years (Elevated Base)** (4)
- **Wide Range (3+ Tiers)** (11)
- **Board Discretion** (1)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **PE-Only Board** (10)
- **PE + Surveyors Board** (21)
- **Multi-Profession Board** (14)
- **State Agency / Department** (4)

`licensure.regulatory_authority.name` — states per tag:

- **PE + Surveyors Board** (22)
- **PE + Surveyors + Architects Board** (9)
- **PE-Only Board** (10)
- **Technical Professions Board** (3)
- **Dept / Division (Non-Board)** (3)
- **PE + Geologists/Other Board** (2)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Core Only** (1)
- **Core + Construction Oversight** (20)
- **Core + Surveys/Studies** (8)
- **Core + Teaching** (4)
- **Core + Extended Services** (7)
- **Broad / Enumerated** (7)

`scope.definition_quote` — states per tag:

- **Full NCEES-Style** (17)
- **Consultation + Design Focus** (6)
- **Public Welfare Emphasis** (17)
- **Principles + Data Only** (4)
- **Minimal / Bare** (4)
- **Enumerated Services** (1)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Obtaining Licensure** (54, 42 states)
- **Negligence Incompetence Misconduct** (84, 40 states)
- **Criminal Conviction** (38, 32 states)
- **Seal and Document Violations** (42, 26 states)
- **Unlicensed or Unauthorized Practice** (70, 31 states)
- **Substance Abuse Impairment** (14, 11 states)
- **Out of State Discipline** (24, 21 states)
- **Regulatory Noncompliance** (92, 41 states)
- **Professional Ethics Violations** (72, 29 states)

### Other bucketed fields

#### Advisory board authority

`licensure.advisory_board.authority` — states per tag:

- **Advise + Recommend + Hearings** (1)
- **Advise on Licensing + Conduct** (1)

#### Advisory board name

`licensure.advisory_board.name` — states per tag:

- **Engineering Only** (1)
- **Engineering + Surveying/Geology** (1)

#### Board engineering disciplines represented

`profession_specific.board_engineering_disciplines_represented` — items per tag:

- **Civil Engineering** (8, 8 states)
- **Structural Engineering** (5, 5 states)
- **Electrical Engineering** (8, 8 states)
- **Mechanical Engineering** (8, 8 states)
- **Chemical Engineering** (4, 4 states)
- **Mining Metallurgical Engineering** (4, 3 states)
- **Specialized Disciplines** (12, 6 states)
- **Generic Board Representation** (8, 8 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ethics Only** (2)
- **Ethics + Practice Area** (1)
- **Ethics + Dual Discipline** (1)
- **Law & Ethics** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **ABET – EAC Only** (13)
- **ABET – Multiple Commissions** (3)
- **ABET Named (General)** (5)
- **Board Approved** (12)
- **State Board** (3)

#### Exams

`licensure.exams` — states per tag:

- **FE + PE (NCEES Named)** (16)
- **FE + PE (Generic Two-Part)** (26)
- **Single Exam Only** (4)
- **Two-Part, State-Specific Labels** (3)

#### Exemptions from licensure

`profession_specific.exemptions_from_licensure` — items per tag:

- **Supervised Subordinate Employees** (53, 44 states)
- **Federal Government Employees** (34, 31 states)
- **State and Local Government Employees** (25, 17 states)
- **Public Utility and Interstate Commerce Employees** (30, 25 states)
- **Industrial and Manufacturing Employees** (55, 33 states)
- **Nonresident Temporary Practice** (29, 21 states)
- **Small or Minor Structures** (57, 20 states)
- **Own Property or In-House Use** (36, 25 states)
- **Other Licensed Professions** (65, 39 states)
- **Contractors and Construction Workers** (37, 22 states)

#### National association

`licensure.national_association` — states per tag:

- **NCEES** (5)
- **State Engineering Society** (3)
- **State Surveying Society** (1)
- **Regional/Multi-Society Council** (1)
- **Accreditation Body** (1)
- **Geology Board** (1)

#### National certification

`licensure.national_certification` — states per tag:

- **NCEES** (12)
- **NCEE (Older Name)** (2)
- **Nat'l Bureau of Eng. Reg.** (1)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Equivalent Standards** (19)
- **Equivalent + NCEES Option** (14)
- **Equivalent + Extra Conditions** (12)
- **Streamlined/Universal Recognition** (1)
- **Restricted/Limited Only** (3)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Consumer Affairs / Protection** (3)
- **Commerce / Economic Dev** (3)
- **Professional Licensing Office** (5)
- **Business & Professional Reg** (3)
- **Labor & Industry / Regulation** (4)
- **Secretary / Dept of State** (2)
- **Other Agency** (3)

#### Seal document types

`profession_specific.seal_document_types` — items per tag:

- **Plans and Drawings** (67, 45 states)
- **Specifications** (46, 44 states)
- **Reports and Studies** (48, 44 states)
- **Plats Maps and Surveys** (40, 29 states)
- **Calculations and Design Info** (17, 11 states)
- **Construction Documents** (3, 3 states)
- **Catch-All General Documents** (29, 24 states)

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

- **Bach + 150 Hours** (21)
- **Bach + 150 Hours + Acctg Concentration** (16)
- **Bach Degree Only** (8)
- **120/150 Split** (3)
- **Board Discretion** (2)

#### Professional Experience

`licensure.post_degree_experience.kind` — states per tag:

- **Broad Skills List** (22)
- **Public Practice Only** (5)
- **Any Accounting Setting** (8)
- **CPA-Supervised General** (11)
- **CPA-Supervised Public Only** (2)

`licensure.post_degree_experience.duration` — states per tag:

- **1 Year** (26)
- **2 Years** (3)
- **Hours-Based** (3)
- **1 or 2 Years (Pathway-Dependent)** (10)
- **2+ Years (Tiered by Sector)** (1)
- **Transitional/Complex** (4)

#### Licensing Authority

`licensure.issuing_authority` — states per tag:

- **Board of Accountancy** (29)
- **Board of Public Accountancy** (11)
- **Board of CPA Examiners** (4)
- **State Department / Agency** (6)

`licensure.regulatory_authority.name` — states per tag:

- **Board of Accountancy** (30)
- **Board of Public Accountancy** (12)
- **Board of CPA Examiners** (3)
- **Examining Board** (2)
- **Dept / Division (Non-Board)** (3)

#### Scope of Practice

`scope.methods_authorized` — states per tag:

- **Broad General List** (19)
- **Attest-Centered List** (14)
- **Standards-Referenced Detail** (10)
- **Audit/Verification Focus** (4)
- **High-Level Summary** (3)

`scope.definition_quote` — states per tag:

- **Broad: Accounting & Tax Services** (19)
- **Attest-Focused Definition** (13)
- **Holding Out + Services** (9)
- **Licensee Performance Only** (5)
- **Minimal / Placeholder** (4)

#### Discipline

`licensure.disciplinary_grounds` — items per tag:

- **Fraud in Obtaining Credential** (60, 42 states)
- **Dishonesty Fraud Negligence in Practice** (95, 46 states)
- **Criminal Conviction** (58, 41 states)
- **Discipline by Other Jurisdiction** (98, 48 states)
- **Violation of Law or Board Rules** (141, 48 states)
- **Continuing Education or Peer Review Failure** (20, 13 states)
- **Impairment or Incapacity** (15, 9 states)
- **Unlicensed or Improper Practice** (44, 22 states)
- **Conduct Reflecting Adversely on Fitness** (48, 38 states)

### Other bucketed fields

#### Attest services types

`profession_specific.attest_services_types` — items per tag:

- **Audit / SAS Engagement** (46, 45 states)
- **Review / Compilation (SSARS)** (53, 48 states)
- **Attestation Examination (Prospective)** (30, 30 states)
- **Other Attestation / Agreed-Upon Procedures (SSAE)** (43, 40 states)
- **PCAOB Engagement** (38, 38 states)
- **Government Auditing Standards** (4, 4 states)
- **General / Broad Attest Service** (13, 9 states)

#### Continuing education topical requirements

`licensure.continuing_education.topical_requirements` — states per tag:

- **Ethics Only** (1)
- **Accounting & Auditing Core** (0)
- **Ethics + Accounting/Auditing Hours** (3)
- **Broad Topic List** (2)
- **Out-of-State Focused** (1)

#### Education accrediting body

`licensure.education.accrediting_body` — states per tag:

- **Board Discretion** (16)
- **Regional Accreditors Named** (3)
- **US Dept of Education List** (6)
- **Regional + Board Fallback** (3)
- **Business School Accreditors Included** (1)

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

- **Jurisdiction and Disciplinary Authority Consent** (52, 47 states)
- **Compliance with State Laws and Rules** (46, 46 states)
- **Cessation of Practice if Home-State License Invalid** (44, 41 states)
- **Agent Appointment for Service of Process** (46, 46 states)
- **Reporting and Notification Obligations** (3, 2 states)
- **Cooperation with Investigations** (2, 2 states)
- **Scope of Practice Limitation** (1, 1 states)
- **Employer Firm Consent** (1, 1 states)

#### Reciprocity requirements

`licensure.reciprocity.requirements` — states per tag:

- **Substantial Equivalency Only** (5)
- **SE + Traditional Fallback** (26)
- **Traditional Reciprocity** (5)
- **Practice Privilege Focused** (8)
- **Endorsement / Good Standing** (6)

#### Regulatory authority umbrella agency

`licensure.regulatory_authority.umbrella_agency` — states per tag:

- **Commerce / Economic Dev** (3)
- **Consumer Affairs / Protection** (4)
- **Professional Licensing Dept** (9)
- **Labor / Industry** (2)
- **Health / State Office** (2)
- **Independent / Self-Governing** (3)

#### Statute of limitations for accountant negligence

`profession_specific.statute_of_limitations_for_accountant_negligence` — states per tag:

- **Discovery + Hard Cap** (1)
- **Board Discovery Rule** (1)
- **External Statute Only** (1)

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

