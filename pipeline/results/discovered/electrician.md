# Discovered fields — electrician

## license types and tiers

### `license_tiers` — list[str]
- **what:** The named tiers or classifications of electrician license available in the state, from apprentice through master and including residential variants.
- **states:** UT
- **sample (UT):** "The division shall issue licenses under this chapter to qualified persons in the following classifications: ... apprentice electrician; ... journeyman electrician; ... master electrician; ... residential electrical contractor; residential journeyman electrician; ... residential master electrician"

## what they can work on and where

### `residential_project_definition` — str
- **what:** Statutory definition of what constitutes a 'residential project' for purposes of limiting or distinguishing residential electrician license scope.
- **states:** UT
- **sample (UT):** ""Residential project," as it relates to an electrician or electrical contractor, means buildings primarily wired with nonmetallic sheathed cable, in accordance with standard rules and regulations governing this work, including the National Electrical Code, and in which the voltage does not exceed 250 volts line to line and 125 volts to ground."

### `residential_wiring_method_restriction` — bool
- **what:** Whether the residential-tier electrician license is restricted to work on buildings primarily wired with nonmetallic sheathed (NM) cable.
- **states:** UT
- **sample (UT):** ""Residential journeyman electrician" means a person licensed under this chapter as a residential journeyman electrician having the qualifications, training, experience, and knowledge to wire, install, and repair electrical apparatus and equipment for light, heat, power, and other purposes on buildings using primarily nonmetallic sheath cable."

### `voltage_limit_residential` — int
- **what:** Maximum voltage (line-to-line) permitted under a residential electrician license classification.
- **states:** UT
- **sample (UT):** "in which the voltage does not exceed 250 volts line to line and 125 volts to ground"

### `scope_exclusions` — list[str]
- **what:** Specific categories of work explicitly excluded from the definition of the electrical trade and therefore not requiring an electrician license.
- **states:** UT
- **sample (UT):** ""Electrical trade" does not include: transporting or handling electrical materials; preparing clearance for raceways for wiring; work commonly done by unskilled labor on any installations under the exclusive control of electrical utilities; work involving cable-type wiring that does not pose a shock or fire-initiation hazard; work involving class two or class three power-limited circuits as defined in the National Electrical Code; or minor electrical work incidental to a mechanical or service installation when wiring is extended to no more than 10 feet from an existing outlet or disconnect and does not exceed 120 volts and 20 amperes."

### `minor_electrical_work_amperage_limit` — int
- **what:** Maximum amperage for minor electrical work incidental to a mechanical or service installation that is excluded from the licensed electrical trade.
- **states:** UT
- **sample (UT):** "minor electrical work incidental to a mechanical or service installation when wiring is extended to no more than 10 feet from an existing outlet or disconnect and does not exceed 120 volts and 20 amperes"

### `minor_electrical_work_distance_limit_feet` — int
- **what:** Maximum distance in feet that wiring may be extended from an existing outlet or disconnect to qualify as minor electrical work excluded from licensure.
- **states:** UT
- **sample (UT):** "minor electrical work incidental to a mechanical or service installation when wiring is extended to no more than 10 feet from an existing outlet or disconnect"

## supervision and apprentice rules

### `apprentice_supervision_ratio` — str
- **what:** The maximum ratio of licensed apprentice electricians permitted under the immediate supervision of one licensed supervisor, as set by rule.
- **states:** UT
- **sample (UT):** "rules made by the commission, with the concurrence of the director, in accordance with Title 63G, Chapter 3, Utah Administrative Rulemaking Act, regarding the ratio of apprentices allowed under the immediate supervision of a licensed supervisor, including the ratio of apprentices in their fourth year of training or later that are allowed to be under the immediate supervision of a licensed supervisor"

### `apprentice_unsupervised_hours_allowed` — int
- **what:** Maximum hours per 24-hour period that a fourth-year or later apprentice electrician may work without direct supervision.
- **states:** UT
- **sample (UT):** "beginning in a licensed apprentice electrician's fourth year of training, a licensed apprentice electrician may work without supervision for a period not to exceed eight hours in any 24-hour period"

### `apprentice_unsupervised_year_threshold` — int
- **what:** The year of apprenticeship training at which an apprentice electrician first becomes eligible to work limited hours without direct supervision.
- **states:** UT
- **sample (UT):** "beginning in a licensed apprentice electrician's fourth year of training, a licensed apprentice electrician may work without supervision for a period not to exceed eight hours in any 24-hour period"

### `residential_apprentice_supervisor_ratio_max` — int
- **what:** Maximum number of apprentice electricians a licensed supervisor may oversee on a residential project.
- **states:** UT
- **sample (UT):** "a licensed supervisor may have up to three licensed apprentice electricians on a residential project, or more if established by rules made by the commission, in concurrence with the director"

## contractor business and qualifier rules

### `qualifier_required` — bool
- **what:** Whether a licensed electrical contractor entity must designate a qualifying individual who holds the relevant journeyman or master license and exercises material authority over the business.
- **states:** UT
- **sample (UT):** "The division shall require a contractor to have a qualifier. A qualifier for a contractor shall demonstrate to the division that the qualifier is: licensed in accordance with this chapter; and an owner, officer, or manager of the contractor who exercises material authority in the conduct of the contracting business"

### `qualifier_license_requirement_by_contractor_type` — list[str]
- **what:** The specific electrician license tier that the qualifier for each type of electrical contractor must hold.
- **states:** UT
- **sample (UT):** "for residential electrical contractor licensure, the qualifier shall hold a master electrician or master residential electrician license; for electrical contractor licensure, the qualifier shall hold a master electrician license"

### `qualifier_replacement_notice_days` — int
- **what:** Number of days within which a contractor must notify the licensing division in writing after a qualifier ceases association with the business.
- **states:** UT
- **sample (UT):** "the licensee shall notify the division in writing within 10 days after cessation of association or employment"

### `qualifier_replacement_grace_period_days` — int
- **what:** Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named.
- **states:** UT
- **sample (UT):** "If notice is given, the license shall remain in force for 60 days after the date of cessation of association or employment. The licensee shall replace the original qualifier with another individual qualifier within the 60-day period or the license shall be automatically suspended."

### `long_term_compliance_qualifier_waiver_years` — int
- **what:** Number of consecutive years of violation-free licensure after which an electrical contractor business entity may substitute an active licensed employee name for a named individual qualifier at renewal.
- **states:** UT
- **sample (UT):** "If a plumbing or electrical business entity has maintained its license and has not violated the requirements of this chapter ... for a period of five consecutive years, the business entity may maintain its license under this chapter by recording an active employee name and registration/license number from the applicable trade on the renewal application"

## experience and training pathways

### `journeyman_electrician_apprenticeship_hours` — int
- **what:** Minimum hours of full-time apprenticeship training required to qualify for a journeyman electrician license via the apprenticeship pathway.
- **states:** UT
- **sample (UT):** "has successfully completed at least four years of full-time training and instruction as a licensed apprentice electrician under the supervision of a master electrician or journeyman electrician and in accordance with a planned training program approved by the division"

### `journeyman_electrician_experience_alternative_years` — int
- **what:** Years of full-time electrical experience accepted as an alternative pathway to journeyman electrician licensure in lieu of a formal apprenticeship.
- **states:** UT
- **sample (UT):** "has at least eight years of full-time experience approved by the division in collaboration with the Electricians and Plumbers Licensing Board"

### `master_electrician_journeyman_experience_years` — int
- **what:** Years of practical experience as a journeyman electrician required to qualify for a master electrician license via the experience pathway.
- **states:** UT
- **sample (UT):** "has four years of practical experience as a journeyman electrician"

### `master_electrician_engineering_degree_pathway` — bool
- **what:** Whether a graduate electrical engineering degree from an accredited institution, combined with reduced practical experience, is an accepted pathway to master electrician licensure.
- **states:** UT
- **sample (UT):** "is a graduate electrical engineer of an accredited college or university approved by the division and has one year of practical electrical experience as a licensed apprentice electrician"

### `master_electrician_trade_school_degree_pathway` — bool
- **what:** Whether an associate of applied sciences degree from an approved electrical trade school, combined with journeyman experience, is an accepted pathway to master electrician licensure.
- **states:** UT
- **sample (UT):** "is a graduate of an electrical trade school, having received an associate of applied sciences degree following successful completion of a course of study approved by the division, and has two years of practical experience as a licensed journeyman electrician"

### `residential_journeyman_training_program_years` — int
- **what:** Minimum years of training in a division-approved electrical training program accepted as a pathway to residential journeyman electrician licensure.
- **states:** UT
- **sample (UT):** "has successfully completed two years of training in an electrical training program approved by the division"

### `residential_master_electrician_journeyman_experience_years` — int
- **what:** Minimum years of practical experience as a residential journeyman electrician required to qualify for a residential master electrician license.
- **states:** UT
- **sample (UT):** "has at least two years of practical experience as a residential journeyman electrician"

### `expedited_licensure_pathway_available` — bool
- **what:** Whether an expedited licensure pathway exists for applicants who can clearly demonstrate equivalent knowledge and skills without meeting the standard experience or training requirements.
- **states:** UT
- **sample (UT):** "meets the qualifications for expedited licensure as established by rules made by the commission, with the concurrence of the director, in accordance with Title 63G, Chapter 3, Utah Administrative Rulemaking Act, that clearly demonstrate the applicant has the knowledge and skills to be a licensed master electrician"

## continuing education specifics

### `electrician_continuing_education_hours` — int
- **what:** Total hours of continuing education a licensed electrician (journeyman through master) must complete per two-year renewal cycle.
- **states:** UT
- **sample (UT):** "a licensed electrician shall complete 16 hours of continuing education under the continuing education program established under this section"

### `approved_continuing_education_providers` — list[str]
- **what:** Named organizations whose courses are approved to satisfy electrician continuing education requirements.
- **states:** UT
- **sample (UT):** "The commission may only approve courses for continuing education if offered by: ... the National Electrical Contractors Association Intermountain Chapter; ... the Independent Electrical Contractors of Utah; ... the Intermountain Electrical Association"

## applicable codes and standards

### `national_electrical_code_reference` — bool
- **what:** Whether the statute explicitly references the National Electrical Code as the governing standard for electrical work.
- **states:** UT
- **sample (UT):** "work involving class two or class three power-limited circuits as defined in the National Electrical Code"

### `gas_appliance_work_certification_required` — bool
- **what:** Whether electricians or contractors performing installation, repair, or replacement of gas appliances or combustion systems must obtain a separate certification beyond their electrician license.
- **states:** UT
- **sample (UT):** "Any person described in Subsection (2)(b) that performs work described in Subsection (2)(a): must first receive training and certification as specified in rules adopted by the commission"

## exemptions and unlicensed work limits

### `small_project_dollar_threshold_exemption` — int
- **what:** Maximum total project cost (labor and materials) below which a person may perform certain construction work without a contractor license, with electrical and plumbing work explicitly excluded from this exemption.
- **states:** UT
- **sample (UT):** "subject to Subsection 58-1-401(2) and Sections 58-55-501 and 58-55-502, a person engaged in the alteration, repair, remodeling, or addition to or improvement of a building with a contracted or agreed value of less than $7,000, including both labor and materials"

### `solar_panel_electrical_work_exemption` — bool
- **what:** Whether electrical work incidental to installing or repairing solar panels is exempt from standard electrician licensure requirements.
- **states:** UT
- **sample (UT):** "a solar panel worker if the construction trade is electrical work incidental to installing or repairing a solar panel"

### `hot_tub_sign_electrical_exemption` — bool
- **what:** Whether electrical work incidental to installing or repairing an above-ground prebuilt hot tub or on-premise signage is exempt from electrician licensure.
- **states:** UT
- **sample (UT):** "a person involved in minor electrical work incidental to a mechanical or service installation, including the outdoor installation of: an above-ground, prebuilt hot tub; or the installation, maintenance, or repair of on-premise signs"

### `utility_worker_exemption` — bool
- **what:** Whether persons employed by electric utilities, railroads, telephone corporations, or municipal utilities are exempt from electrician licensure for work incidental to those employers' operations.
- **states:** UT
- **sample (UT):** "a person who ordinarily would be subject to the electrician licensure requirements under this chapter when employed by: railroad corporations, telephone corporations or their corporate affiliates, elevator contractors or constructors, or street railway systems; or public service corporations, rural electrification associations, or municipal utilities who generate, distribute, or sell electrical energy for light, heat, or power"

## financial responsibility and insurance

### `financial_responsibility_bond_option` — bool
- **what:** Whether an electrical contractor applicant may satisfy the financial responsibility requirement by submitting a surety bond as an alternative to completing a financial questionnaire.
- **states:** UT
- **sample (UT):** "submitting a bond in an amount and form determined by the commission with the concurrence of the director"

### `workers_compensation_insurance_required` — bool
- **what:** Whether proof of workers' compensation insurance covering employees is required before the division will issue an electrical contractor license.
- **states:** UT
- **sample (UT):** "proof of workers' compensation insurance that covers employees of the applicant in accordance with applicable Utah law"

### `public_liability_insurance_required` — bool
- **what:** Whether proof of public liability insurance in division-specified amounts is required before the division will issue an electrical contractor license.
- **states:** UT
- **sample (UT):** "proof of public liability insurance in coverage amounts and form established by rule except for a construction trades instructor for whom public liability insurance is not required"
