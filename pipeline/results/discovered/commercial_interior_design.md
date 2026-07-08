# Discovered fields — commercial_interior_design

## extra credentials and tiered scope

### `credential_tier` — enum[registered interior designer, certified interior designer, certified interior designer with commercial designation, registered residential interior designer]
- **what:** The specific credential title or tier granted by the state, which may differ from a generic 'license' and may include commercial-specific or residential-specific designations.
- **states:** AL, AR, CA, CT, FL, GA, IA, IL, … (+1)
- **sample (CA):** "The council may issue a commercial designation to a Certified Interior Designer or qualified applicant who, in addition to the requirements in paragraph (1), passes additional interior design courses and examinations."

### `architect_pathway_available` — bool
- **what:** Whether licensed architects may obtain interior design registration or certification through a simplified or fee-only pathway without the standard examination.
- **states:** AR, CT, FL, GA, IL, IN
- **sample (IL):** "Upon payment of the required fee, which shall be determined by rule, an applicant who is an architect licensed under the laws of this State may, without examination, be granted registration as a registered interior designer."

### `ncidq_exam_required` — bool
- **what:** Whether passage of the NCIDQ (National Council for Interior Design Qualification) examination is explicitly required for registration or certification.
- **states:** AL, AR, CO, CT, FL, GA, IA, IL, … (+1)
- **sample (AR):** "Has passed the examination prepared and administered by the National Council for Interior Design Qualification or its successor in interest."

### `education_experience_pathways` — list[str]
- **what:** The specific combinations of interior design education years and post-degree work experience years that qualify an applicant for registration, expressed as tiered pathways.
- **states:** AR, CA, FL, IA, IL
- **sample (IA):** "Four years of interior design education plus two years of full-time work experience in registered interior design; Three years of interior design education plus three years of full-time work experience; Two years of interior design education plus four years of full-time work experience."

## what they can design and where in a building

### `nonstructural_scope_only` — bool
- **what:** Whether the statute explicitly limits the interior designer's authorized scope to nonstructural or nonseismic interior elements, excluding load-bearing and structural work.
- **states:** AL, AR, CA, CO, CT, FL, GA, IA, … (+2)
- **sample (IN):** "Nonstructural or nonseismic means interior elements or components that are not load bearing or do not assist in the seismic design of a building, do not require design computations for the structure of a building, and do not include the structural frame system supporting a building."

### `excluded_building_systems` — list[str]
- **what:** Specific building systems that interior designers are explicitly prohibited from designing or altering.
- **states:** AR, CO, CT, FL, GA, IA, IL, IN
- **sample (CO):** "Interior designers shall not be engaged in the construction of: The structural frame system supporting a building; Mechanical, plumbing, heating, air conditioning, ventilation, or electrical vertical transportation systems; Fire-rated vertical shafts in any multistory structure; Fire-related protection of structural elements; Smoke evacuation and compartmentalization; Emergency sprinkler systems; Emergency alarm systems."

### `square_footage_limit` — int
- **what:** Maximum contiguous square footage of a commercial interior space for which a registered interior designer may submit sealed construction documents without architect involvement.
- **states:** AL, GA
- **sample (AL):** "A registered interior designer may submit sealed, stamped drawings to building officials for a commercial interior project in any space of less than 5,000 contiguous square feet within a building of any size."

### `residential_practice_exempt` — bool
- **what:** Whether the statute explicitly exempts residential interior design from the registration requirement or from the scope of the commercial interior design act.
- **states:** AL, FL, GA, IA, IL, IN
- **sample (FL):** "This part shall not apply to: A person who performs interior design services or interior decorator services for any residential application. For purposes of this paragraph, 'residential applications' includes all types of residences, including, but not limited to, residence buildings, single-family homes, multifamily homes, townhouses, apartments, condominiums."

### `interior_decorator_exemption` — bool
- **what:** Whether the statute explicitly exempts persons offering only 'interior decorator' or 'interior decorating' services (e.g., surface materials, window treatments, loose furnishings) from registration requirements.
- **states:** AR, CT, FL, GA, IA, IL, IN
- **sample (AR):** "This subchapter does not apply to persons holding themselves out as 'interior decorators' or offering 'interior decorating services' such as selection or assistance in selecting surface materials, window treatments, wall coverings, paint, floor coverings, surface-mounted lighting, or loose furnishings not subject to regulation under applicable building codes."

### `permit_submission_authority` — bool
- **what:** Whether the statute explicitly grants registered interior designers the authority to submit sealed documents to building officials for permit approval.
- **states:** AL, CA, CO, FL, GA, IA, IL, IN
- **sample (IA):** "A registered interior designer may sign and seal an interior technical submission that is required for an interior alteration or construction project and that shall be kept as a public record. If a political subdivision of the state requires a seal or stamp on an interior technical submission, the political subdivision shall accept an interior technical submission impressed with the seal or stamp of a registered interior designer."

## professional documents and sealing

### `seal_required` — bool
- **what:** Whether the statute requires registered interior designers to obtain and use an official seal on documents submitted for public record or permitting.
- **states:** AL, AR, CA, CT, FL, GA, IA, IL, … (+1)
- **sample (IA):** "A registered interior designer shall have a seal with which to identify all interior technical submissions issued by the registered interior designer for use in this state."

### `seal_distinct_from_architect_seal` — bool
- **what:** Whether the statute requires that the interior designer's seal be visually distinct from the seals used by architects, engineers, or landscape architects.
- **states:** AR, FL, GA
- **sample (AR):** "The shape and design of the seal will be different from the seals of architects, engineers, or landscape architects."

### `document_disclaimer_required` — bool
- **what:** Whether the statute requires interior design documents to include a written statement that they are not architectural or engineering documents and may not be used for structural construction.
- **states:** AR, FL, IN
- **sample (AR):** "The registered interior designer's contract documents shall contain a statement that the document is not an architectural or engineering drawing, specification, or design and is not to be used for construction of any load-bearing columns, load-bearing framing, or load-bearing walls or structures or for the issuance of any building permit, except as otherwise provided by law."

### `responsible_control_defined` — bool
- **what:** Whether the statute provides an explicit statutory definition of 'responsible control' or 'responsible supervising control' as it applies to interior designers' oversight of documents.
- **states:** CO, FL, GA, IA, IL
- **sample (IL):** "Responsible control means the amount of control over detailed professional knowledge of the content of interior technical submissions during the preparation as is ordinarily exercised by registered interior designers applying the required professional standard of care."

## client and business conduct rules

### `written_contract_required` — bool
- **what:** Whether the statute requires interior designers to execute a written contract with clients before commencing work, specifying services, compensation, and other terms.
- **states:** CA, FL
- **sample (CA):** "A Certified Interior Designer shall use a written contract when contracting to provide interior design services to a client pursuant to this chapter. The written contract shall be executed by the Certified Interior Designer and the client, or the client's representative, prior to the Certified Interior Designer commencing work."

### `compensation_disclosure_required` — bool
- **what:** Whether the statute requires interior designers to fully disclose to clients all forms of compensation, including fees, commissions, or markups from suppliers.
- **states:** AL, FL, IA
- **sample (FL):** "The interior designer shall have the responsibility of fully disclosing to the client the manner in which all compensation is to be paid. Unless the client knows and agrees, the interior designer shall not accept any form of compensation from a supplier of goods and services in cash or in kind."

### `conflict_of_interest_rules` — bool
- **what:** Whether the statute includes explicit provisions governing conflicts of interest, including disclosure obligations and prohibitions on accepting undisclosed compensation from third parties.
- **states:** AL, IA, IL
- **sample (AL):** "The registered interior designer shall attempt to avoid all conflicts of interest with a client or employer. If a conflict of interest is unavoidable, the registered interior designer shall immediately inform the client or employer of any business association, interest, or circumstance which may influence the professional judgment, decisions, practices, or quality of services provided."

### `professional_liability_insurance_required` — bool
- **what:** Whether the statute requires interior designers to carry professional liability (errors and omissions) insurance as a condition of practice or permit submission.
- **states:** CA, CO
- **sample (CO):** "An interior designer shall, as a condition of filing interior design documents and specifications for the purpose of obtaining approval for a building permit, provide to the responsible building official of the jurisdiction proof of the interior designer's professional liability insurance coverage that is in force."

## practice setting and firm structure

### `business_entity_practice_permitted` — bool
- **what:** Whether the statute explicitly permits registered interior designers to practice through or co-own partnerships, corporations, LLCs, or other business entities, including with architects or engineers.
- **states:** AL, FL, GA, IL
- **sample (AL):** "It shall be lawful for any person registered pursuant to this chapter to participate as owners with architects or professional engineers, or both, in partnerships, corporations, professional corporations, professional associations, and other business entity relationships."

### `registration_number_display_required` — bool
- **what:** Whether the statute requires registered interior designers to display or include their registration number in advertisements, business cards, stationery, or other communications.
- **states:** AR, CT, FL
- **sample (AR):** "Shall require registrants to display their registration numbers on all business and advertising instruments, including business cards, stationery, and contracts."

### `inactive_status_available` — bool
- **what:** Whether the statute provides a formal inactive status option that allows registrants to avoid renewal fees while not practicing, with restrictions on use of the protected title.
- **states:** AL, FL, IL
- **sample (IL):** "Any registrant who notifies the Department in writing on forms prescribed by the Department may elect to place his or her certificate of registration on an inactive status and shall, subject to rules of the Department, be excused from payment of renewal fees until he or she notifies the Department in writing of his or her desire to resume active status."

## ongoing learning requirements

### `continuing_education_topical_focus` — list[str]
- **what:** Specific subject matter areas mandated for continuing education, beyond general interior design topics.
- **states:** CT, FL, IL
- **sample (CT):** "The continuing education shall be in areas related to the application of the State Building Code and the Fire Safety Code."

## discipline and enforcement

### `civil_judgment_disqualification` — bool
- **what:** Whether the statute provides that a civil court judgment against an interior designer for negligence or misconduct in practice results in automatic removal from the registry or disqualification from registration.
- **states:** AL, IN
- **sample (IN):** "If a civil judgment is entered against an interior designer by a court with jurisdiction in a civil judicial proceeding for negligence, recklessness, willful misconduct, or other breach of a standard of care in the practice of interior design, the interior designer must, within a reasonable time, remove the designer's name from the electronic registry maintained by the agency."
