# Discovered fields — architecture

## extra credentials and tiered scope

### `interior_designer_certification_available` — bool
- **what:** Whether the state offers a separate certification credential for interior designers alongside the architect license.
- **states:** PA
- **sample (PA):** ""Certified interior designer." An individual who is certified under this act to provide interior design services."

### `interior_design_services_defined` — bool
- **what:** Whether the statute separately defines 'interior design services' as a distinct regulated activity from the practice of architecture.
- **states:** PA
- **sample (PA):** ""Interior design services." The rendering or offering to render services in the preparation and administration of documents, including drawings, schedules and specifications which pertain to the design intent and planning of interior spaces... The term does not include the practice of architecture."

## practice setting and business structure

### `design_build_authorized` — bool
- **what:** Whether the statute explicitly authorizes and regulates design-build project delivery by architectural firms or entities.
- **states:** PA
- **sample (PA):** ""Design-build." A project delivery method whereby a design-build entity signs a single contract to provide a combination of architectural and construction services to a client."

### `permitted_firm_structures` — list[str]
- **what:** The legal business entity forms in which architects are permitted to practice.
- **states:** PA
- **sample (PA):** "An individual architect or a group of architects in Pennsylvania may practice architecture in one of the following forms of architectural firms: sole proprietorship; partnership; professional association; professional corporation; business corporation; limited liability company; or limited liability partnership."

### `firm_licensed_architect_ownership_minimum_fraction` — str
- **what:** The minimum fraction of ownership, directors, or partners in an architectural firm that must be licensed architects (as opposed to other licensed design professionals).
- **states:** PA
- **sample (PA):** "At least one-third of the partners are licensed under the laws of any state to practice architecture."

### `firm_design_professional_ownership_minimum_fraction` — str
- **what:** The minimum fraction of ownership, directors, or partners in an architectural firm that must be licensed in architecture, engineering, or landscape architecture combined.
- **states:** PA
- **sample (PA):** "At least two-thirds of the partners are licensed under the laws of any state to practice architecture, engineering or landscape architecture."

## professional seal and document signing

### `seal_required` — bool
- **what:** Whether a licensed architect is required to obtain and affix an official seal to drawings, specifications, and other design documents.
- **states:** PA
- **sample (PA):** "Every architect shall obtain a seal approved by rules and regulations promulgated by the board and shall impress said seal on drawings, specifications and other design documents prepared by the individual or under the architect's personal supervision for use in this State."

### `seal_surrender_required_on_license_termination` — bool
- **what:** Whether an architect must surrender their seal or stamp to the board upon forfeiture, revocation, suspension, expiration, or death.
- **states:** PA
- **sample (PA):** "Upon the forfeiture, revocation, suspension or annulment of a license or upon expiration of a license without renewal, an architect shall surrender the architect's seal or stamp to the board."

## continuing education topics

### `continuing_education_subject_requirement` — list[str]
- **what:** Specific subject-area requirements mandated for continuing education credit toward license renewal.
- **states:** PA
- **sample (PA):** "As a condition of biennial renewal, an architect shall provide the board with documentation of successful completion of a minimum of 24 hours of continuing education in the subject areas of health, safety and welfare."

### `continuing_education_excluded_topics` — list[str]
- **what:** Topics explicitly prohibited from counting toward continuing education requirements.
- **states:** PA
- **sample (PA):** "The board may not approve courses in office management or practice building for the purpose specified under subsection (e)."

### `continuing_education_waiver_conditions` — list[str]
- **what:** Circumstances under which the board may waive all or part of the continuing education requirement.
- **states:** PA
- **sample (PA):** "The board may waive all or part of the continuing education requirement under subsection (e) for a licensee who provides evidence satisfactory to the board that the licensee is unable to complete the requirement due to illness, emergency, hardship or active military service."

## what they can design and where exemptions apply

### `exempt_building_types` — list[str]
- **what:** Categories of structures or projects explicitly exempt from the architect licensure requirement.
- **states:** PA
- **sample (PA):** "The preparation of any drawings or other design documents for detached one-family or two-family dwellings not more than three stories in height and their accessory structures."

## reciprocity and national credentials

### `ncarb_certificate_reciprocity_prima_facie` — bool
- **what:** Whether possession of an NCARB certificate constitutes prima facie evidence of meeting the state's licensure qualifications for reciprocity purposes.
- **states:** PA
- **sample (PA):** "The possession of a certificate from the National Council of Architectural Registration Boards shall be prima facie evidence that the individual meets the qualifications required in this State."

### `ncarb_standards_adoptable` — bool
- **what:** Whether the board is explicitly authorized to adopt NCARB guidelines for minimum education, training, and experience equivalents.
- **states:** PA
- **sample (PA):** "The board may at its discretion adopt as its standards for minimum education and experience, the current guidelines on education, training and experience equivalents adopted by the National Council of Architectural Registration Boards."

## penalties for unauthorized practice

### `unauthorized_practice_criminal_penalty_first_offense` — str
- **what:** The criminal classification and maximum penalty for a first offense of unauthorized practice of architecture.
- **states:** PA
- **sample (PA):** "Any person who engages or who offers to engage in the practice of architecture... without holding a currently valid license... shall, for a first offense, be guilty of a summary offense and upon conviction thereof shall be sentenced to pay a fine not exceeding $500 or suffer imprisonment not exceeding 90 days, or both."

### `unauthorized_practice_criminal_penalty_subsequent_offense` — str
- **what:** The criminal classification and penalty range for a second or subsequent offense of unauthorized practice of architecture.
- **states:** PA
- **sample (PA):** "For a second or subsequent offense shall be guilty of a misdemeanor and upon conviction thereof shall be sentenced to pay a fine of not less than $2,000 but not more than $5,000, or to suffer imprisonment of not less than one year, but not more than two years, or both."

### `civil_penalty_maximum` — int
- **what:** Maximum civil penalty in dollars the board may levy on a current licensee or unauthorized practitioner for violations.
- **states:** PA
- **sample (PA):** "The board... may levy a civil penalty of up to $1,000 on any current licensee or certificate holder who violates any provision of this act or on any person who practices the profession of an architect without being properly licensed."
