# Discovered fields — forester

## license tiers and credential levels

### `tiered_license_classes` — list[str]
- **what:** Named tiers or classes of forestry credentials below or alongside the full forester license, such as intern forester or forest products harvester.
- **states:** CT, ME
- **sample (CT):** "There shall be three classifications for commercial forest practitioners: Forester, supervising forest products harvester and forest products harvester."

### `intern_forester_license_available` — bool
- **what:** Whether the state issues a formal intern forester (or equivalent pre-licensure) credential that allows supervised practice before full licensure.
- **states:** ME, MI
- **sample (ME):** "'Intern forester' means a person licensed under this chapter to practice forestry under the sponsorship of a forester."

### `specialty_certificate_available` — bool
- **what:** Whether the state allows issuance of certificates of specialization in defined fields of forestry in addition to the general forester license.
- **states:** CA, GA, MD
- **sample (CA):** "The board may by regulation provide for the issuance of certificates of specialization in such fields of specialization as the board may by regulation establish."

## supervision and delegation

### `sponsor_supervisor_role_defined` — bool
- **what:** Whether the statute formally defines a sponsor or supervisor role for a licensed forester who oversees an intern or unlicensed practitioner.
- **states:** AL, AR, GA, MD, ME, MI, MS
- **sample (ME):** "'Sponsor' means a forester who is responsible for overseeing the activities of an intern forester."

### `supervised_practice_without_license_permitted` — bool
- **what:** Whether an individual who meets educational but not experience requirements may practice forestry without a full license under the responsible charge of a licensed forester.
- **states:** AL, AR, GA, MD, ME, MI, MS
- **sample (MD):** "An individual who meets the educational requirements but does not meet the experience requirements under § 7-304 of this subtitle may practice forestry without a license if the individual practices forestry under the responsible charge of a licensed forester."

### `internship_duration_by_degree_level` — str
- **what:** The required internship or supervised-experience duration differentiated by the applicant's degree level (e.g., associate vs. bachelor's).
- **states:** AR, ME, MI
- **sample (ME):** "An applicant with an associate degree or no degree shall demonstrate 48 months of forestry experience as an intern forester... An applicant with a bachelor's degree or higher shall demonstrate 24 months of forestry experience."

## education and experience pathways

### `alternative_qualification_pathways` — list[str]
- **what:** Explicit alternative routes to licensure for applicants who lack an accredited forestry degree, specifying substitute degrees and additional experience years required.
- **states:** AR, CA, ME, MI
- **sample (AR):** "A bachelor's degree in a natural resources-related field from a college or university program, including, but not limited to, wildlife management, with at least twenty (20) semester hours of forestry courses approved by the commission and three (3) years' or more experience in forestry work."

### `saf_accreditation_recognized` — bool
- **what:** Whether the statute explicitly recognizes Society of American Foresters (SAF) accreditation of a forestry program as satisfying the educational requirement.
- **states:** AL, AR, CA, GA, MD, ME, MI, MS
- **sample (AR):** "A bachelor's or advanced degree in forestry from a college or university program accredited by the Society of American Foresters."

### `saf_certified_forester_recognized_for_supervision` — bool
- **what:** Whether an SAF-certified forester (as distinct from a state-registered forester) is recognized as a qualifying supervisor for experience credit.
- **states:** CT, MI
- **sample (MI):** "4 years of experience under the guidance of a registered forester, an SAF-certified forester, or a member of the Association of Consulting Foresters."

## professional documents and endorsements

### `document_seal_required` — bool
- **what:** Whether licensed foresters are required to obtain and use an official seal on plans, maps, specifications, and reports they prepare or supervise.
- **states:** AL, AR, GA, MD, ME, MI, MS
- **sample (AR):** "Each registrant may obtain a seal of a design authorized by the Arkansas Forestry Commission, bearing the registrant's name, serial number, and the legend 'Registered Forester, Arkansas'."

### `document_endorsement_required` — bool
- **what:** Whether the statute requires a licensed forester to endorse (sign with name and license number) all plans, maps, specifications, and reports they prepare or supervise.
- **states:** AL, AR, GA, MD, ME, MI, MS
- **sample (AL):** "Plans, maps, specifications, and reports issued by a registrant shall be endorsed with his or her name and license number during the life of the registrant's license."

### `endorsement_restricted_to_personally_prepared_documents` — bool
- **what:** Whether it is a violation for a forester to endorse any document that the forester did not personally prepare or directly supervise the preparation of.
- **states:** AL, AR, GA, MD, ME, MI, MS
- **sample (AL):** "It shall be a misdemeanor for any registered forester to endorse any plan, specification, estimate, or map unless he or she shall have actually prepared such plan, specification, estimate, or map, or shall have been in the actual charge of the preparation thereof."

## reporting and practice oversight

### `annual_activity_report_required` — bool
- **what:** Whether certified or licensed foresters must submit an annual report to the regulatory authority describing their forestry activities during the year.
- **states:** CT, MI, MS
- **sample (CT):** "Each certified forester... shall submit an annual report to the Commissioner of Energy and Environmental Protection on or before June first of each year... Such report shall include, but not be limited to, the following information: (1) The number of forest management plans completed and acres covered by said plans."

### `harvest_notification_required` — bool
- **what:** Whether landowners or practitioners must provide advance written notice to a state agency before commencing a timber harvest or cutting operation.
- **states:** CT, MA
- **sample (MA):** "Every owner of land who proposes to cut forest products on land devoted to forest purposes... shall send... written notice of his intention to begin any cutting operation... to the director or his agent at the appropriate regional office... at least ten days prior to operations."

### `timber_harvester_license_separate` — bool
- **what:** Whether the state maintains a separate license or certification for timber harvesters (loggers) distinct from the professional forester license.
- **states:** CT, MA
- **sample (MA):** "No person, firm or corporation engaged in the business of harvesting timber or other forest products for hire or profit shall cut such products on land devoted to forest purposes... without first obtaining a license to do so from the director."

## professional conduct standards

### `code_of_ethics_required` — bool
- **what:** Whether the statute requires the board to adopt a formal code of ethics or professional conduct for licensed foresters.
- **states:** GA, MD, MI, MS
- **sample (MD):** "With the advice of the established forestry associations, the Board shall adopt, by regulation, a code of ethics for practicing forestry."

### `conflict_of_interest_disclosure_required` — bool
- **what:** Whether the statute or codified conduct standards require a registered forester to disclose personal or financial interests in a forestry project where a conflict of interest may exist.
- **states:** MD, MI
- **sample (MI):** "Fully disclose personal or financial interests in any forestry project undertaken by the registered forester if there is a potential conflict of interest."

## license status and conditions

### `inactive_license_status_available` — bool
- **what:** Whether the state provides a formal inactive license status that allows a licensee to avoid full renewal requirements while not actively practicing.
- **states:** MD, ME
- **sample (MD):** "A licensee may apply to the Board for inactive status. The Board shall grant inactive status to a licensee if the licensee... pays to the Board an inactive license fee of $25."

### `continuing_education_exemption_conditions` — list[str]
- **what:** Conditions under which the continuing education requirement for license renewal may be waived or relaxed, such as age, retirement, hardship, illness, or military service.
- **states:** AL, AR, GA, MD, ME
- **sample (AL):** "The continuing education program herein required shall not apply to any licensee who is 65 years of age or older and shall not include testing or examination of the licensees in any manner. The board may relax or suspend the continuing annual education requirements for retirees or for reasons of the health, hardship, or other extenuating circumstances."

### `only_individuals_may_be_licensed` — bool
- **what:** Whether the statute explicitly prohibits firms, partnerships, or corporations from being licensed, restricting licensure to individual persons only.
- **states:** AL, AR, GA, ME, MS
- **sample (AL):** "Registration shall be determined upon a basis of individual, personal qualifications. No firms, companies, partnerships, or corporations can be licensed under this chapter."

## who must be licensed and who is exempt

### `exemption_for_own_land_management` — bool
- **what:** Whether landowners who manage or conduct forestry practices on their own land are explicitly exempt from the licensure requirement.
- **states:** AL, AR, CA, GA, ME, MS
- **sample (ME):** "An owner managing or otherwise conducting forestry practices on that owner's land."

### `exemption_for_federal_employees` — bool
- **what:** Whether officers or employees of the federal government practicing forestry on federally owned lands are explicitly exempt from state licensure.
- **states:** AL, GA, ME, MS
- **sample (AL):** "The practice of forestry by officers and employees of the United States government on federally owned lands."

### `exemption_for_state_employees` — bool
- **what:** Whether officers or employees of the state government practicing forestry on state-owned lands are explicitly exempt from licensure.
- **states:** AL, MS
- **sample (AL):** "The practice of forestry by officers and employees of the State of Alabama on state-owned lands."

### `exemption_for_uncompensated_practice` — bool
- **what:** Whether the statute exempts forestry activities that are not performed for compensation or hire from the licensure requirement.
- **states:** AR, MD, MS
- **sample (MS):** "Nothing contained in this chapter shall be construed as preventing any person, firm, partnership or corporation from practicing forestry or managing woodlands, forests or trees on any land, provided such acts are not performed or offered to the public for compensation."

## governing board composition

### `board_member_minimum_practice_years` — int
- **what:** The minimum number of years of professional forestry experience required for appointment as a member of the state forester licensing board.
- **states:** AL, GA, MI, MS
- **sample (AL):** "Each member of the board shall be a citizen of the United States and a resident of the State of Alabama, a 'registered forester' under the provisions of this chapter, and have been engaged in the practice of the profession of forestry for the last 10 years prior to such appointment."

### `board_includes_public_member` — bool
- **what:** Whether the statute requires at least one public (non-forester) member on the state forester licensing board.
- **states:** CA, GA, MA, ME
- **sample (GA):** "The board shall consist of a sixth member who shall be appointed by the Governor from the public at large and who shall have no connection whatsoever with the practice of professional forestry."

### `board_nominees_from_professional_society` — bool
- **what:** Whether the statute requires that board member nominees be recommended by a recognized professional forestry society such as the Society of American Foresters.
- **states:** AL, MI
- **sample (AL):** "The five members of the board shall be selected and appointed by the Governor of Alabama from among 10 nominees recommended by the Alabama Division of the Society of American Foresters."

## reciprocity and interstate recognition

### `automatic_registration_for_affiliated_organization_members` — bool
- **what:** Whether members of recognized affiliated professional forestry organizations may qualify for automatic or expedited registration without the standard application process.
- **states:** CT, MI
- **sample (MI):** "The board shall determine whether members of affiliated professional organizations within and outside of this state are eligible for automatic registration under this part."

## what the practice covers

### `scope_includes_urban_forestry` — bool
- **what:** Whether the statutory definition of forestry or the authorized scope of practice explicitly includes urban, municipal, or community forestry.
- **states:** MD, MI
- **sample (MI):** "Urban forestry and arboriculture."

### `scope_includes_watershed_and_environmental_values` — bool
- **what:** Whether the statutory definition of forestry explicitly includes evaluation or mitigation of impacts on watershed, ecological, or environmental values.
- **states:** CA, CT, MA, ME
- **sample (CA):** "The evaluation and mitigation of impacts from forestry activities on watershed and scenic values."

### `scope_includes_fuels_management` — bool
- **what:** Whether the statutory definition of forestry explicitly includes fuels management or forest fire protection as part of the authorized scope.
- **states:** CA, MI
- **sample (CA):** "The application of scientific knowledge and forestry principles in the fields of fuels management and forest protection."

### `scope_excludes_civil_engineering_and_surveying` — bool
- **what:** Whether the statute explicitly states that a forester license does not authorize the practice of civil engineering, land surveying, or landscape architecture.
- **states:** CA, ME
- **sample (CA):** "This article shall not be construed to authorize a registered professional forester to practice civil engineering... or to practice land surveying... or to practice landscape architecture."
