# Discovered fields — plumbing

## license types and tiers

### `license_tiers` — list[str]
- **what:** The distinct license classification tiers available for plumbers, from apprentice through master and contractor levels.
- **states:** UT
- **sample (UT):** "The division shall issue licenses under this chapter to qualified persons in the following classifications: ... apprentice plumber; ... journeyman plumber; ... master plumber; ... residential journeyman plumber; ... residential master plumber; ... general plumbing contractor; ... residential plumbing contractor."

### `residential_scope_limited` — bool
- **what:** Whether a residential-tier plumber license restricts the licensee to work only on residential buildings (typically single or multi-family dwellings up to four units).
- **states:** UT
- **sample (UT):** ""Residential journeyman plumber" means a person licensed under this chapter as a residential journeyman plumber having the qualifications, training, experience, and knowledge to engage in the plumbing trade as limited to the plumbing of residential buildings."

### `residential_building_unit_cap` — int
- **what:** Maximum number of dwelling units in a building that a residential-tier plumber or contractor license authorizes work on.
- **states:** UT
- **sample (UT):** ""Residential building," as it relates to the license classification of residential journeyman plumber and residential master plumber, means a single or multiple family dwelling of up to four units."

## supervision and apprenticeship rules

### `apprentice_supervision_requirement` — str
- **what:** Description of which license types are authorized to directly supervise a licensed apprentice plumber.
- **states:** UT
- **sample (UT):** "while engaging in the trade of plumbing, a licensed apprentice plumber shall be under the immediate supervision of a licensed master plumber, licensed residential master plumber, licensed journeyman plumber, or licensed residential journeyman plumber"

### `apprentice_unsupervised_hours_allowed` — int
- **what:** Maximum number of hours per 24-hour period that a fourth-year or later apprentice plumber may work without direct supervision.
- **states:** UT
- **sample (UT):** "beginning in a licensed apprentice plumber's fourth year of training, a licensed apprentice plumber may work without supervision for a period not to exceed eight hours in any 24-hour period"

### `apprentice_unsupervised_training_year_threshold` — int
- **what:** The year of apprenticeship training at which an apprentice plumber first becomes eligible to work limited hours without direct supervision.
- **states:** UT
- **sample (UT):** "beginning in a licensed apprentice plumber's fourth year of training, a licensed apprentice plumber may work without supervision for a period not to exceed eight hours in any 24-hour period"

### `apprentice_to_supervisor_ratio_regulated` — bool
- **what:** Whether the statute establishes or delegates authority to set a maximum ratio of apprentice plumbers per supervising licensee.
- **states:** UT
- **sample (UT):** "rules made by the commission, with the concurrence of the director, in accordance with Title 63G, Chapter 3, Utah Administrative Rulemaking Act, regarding the ratio of apprentices allowed under the immediate supervision of a licensed supervisor"

## experience and training pathways

### `journeyman_experience_pathways` — list[str]
- **what:** Alternative pathways an applicant may use to satisfy the experience requirement for journeyman plumber licensure.
- **states:** UT
- **sample (UT):** "A journeyman plumber applicant shall provide satisfactory evidence that the applicant: completed at least four-years' full-time training and instruction as a licensed apprentice plumber under supervision of a licensed master plumber or journeyman plumber ... has at least eight-years' full-time experience the division approves ... or meets the qualifications for expedited licensure"

### `master_plumber_supervisory_experience_required` — bool
- **what:** Whether a master plumber applicant must demonstrate supervisory experience as a journeyman plumber in addition to time-in-grade.
- **states:** UT
- **sample (UT):** "A master plumber applicant shall provide satisfactory evidence that the applicant: has two-years' supervisory experience as a licensed journeyman plumber in accordance with division rule"

### `expedited_licensure_pathway_available` — bool
- **what:** Whether the statute provides an expedited licensure pathway for applicants who can otherwise demonstrate equivalent knowledge and skills.
- **states:** UT
- **sample (UT):** "meets the qualifications for expedited licensure as established by rules made by the commission, with the concurrence of the director, in accordance with Title 63G, Chapter 3, Utah Administrative Rulemaking Act, that clearly demonstrate the applicant has the knowledge and skills to be a licensed master plumber"

## what plumbers can work on and where

### `plumbing_trade_geographic_limit_feet` — int
- **what:** How many feet beyond the outside walls of a building the plumbing trade definition extends.
- **states:** UT
- **sample (UT):** ""Plumbing trade" means the performance of any mechanical work pertaining to the installation, alteration, change, repair, removal, maintenance, or use in buildings, or within three feet beyond the outside walls of buildings"

### `gas_supply_work_included_in_scope` — bool
- **what:** Whether the delivery of gas for lighting, heating, and industrial purposes is explicitly included within the plumbing trade scope.
- **states:** UT
- **sample (UT):** ""Plumbing trade" means the performance of any mechanical work pertaining to ... delivery of gases for lighting, heating, and industrial purposes."

### `natural_gas_appliance_certification_required` — bool
- **what:** Whether a separate certification (beyond the plumbing license) is required before a licensee may install, repair, or replace a residential or commercial gas appliance or combustion system.
- **states:** UT
- **sample (UT):** "Any person described in Subsection (2)(b) that performs work described in Subsection (2)(a): must first receive training and certification as specified in rules adopted by the commission"

### `fire_sprinkler_work_authorized` — bool
- **what:** Whether a licensed journeyman plumber is authorized to perform installation, repair, or replacement of water-based fire protection systems.
- **states:** UT
- **sample (UT):** "installation, repair, or replacement of water-based fire protection systems on a Subsection (1)(h)(i) project must be performed by a licensed fire suppression systems contractor or a licensed journeyman plumber"

### `natural_gas_facilities_installation_authorized` — bool
- **what:** Whether a licensed plumber (as a qualifying installer) is authorized to install natural gas mains and service lines beyond the building.
- **states:** UT
- **sample (UT):** ""Qualifying installer" means a person who: a gas corporation approves to install natural gas facilities; and is: licensed under this chapter; and authorized to install natural gas facilities within the person's scope of practice as established by statute or administrative rule."

## contractor business and qualifier rules

### `contractor_qualifier_license_requirement` — enum[master plumber required for general plumbing contractor, master plumber or master residential plumber required for residential plumbing contractor]
- **what:** The specific individual plumber license tier that the qualifier for a plumbing contractor entity must hold.
- **states:** UT
- **sample (UT):** "for plumbing contractor licensure, the qualifier shall hold a master plumber license; ... for residential plumbing contractor licensure, the qualifier shall hold a master plumber license or master residential plumber license"

### `qualifier_replacement_notice_days` — int
- **what:** Number of days within which a contractor must notify the licensing division after a qualifier ceases association with the business.
- **states:** UT
- **sample (UT):** "the licensee shall notify the division in writing within 10 days after cessation of association or employment"

### `qualifier_replacement_grace_period_days` — int
- **what:** Number of days a contractor license remains in force after a qualifier ceases association, during which a replacement qualifier must be named.
- **states:** UT
- **sample (UT):** "If notice is given, the license shall remain in force for 60 days after the date of cessation of association or employment."

### `long_term_compliance_qualifier_waiver_years` — int
- **what:** Number of consecutive violation-free years after which a plumbing or electrical contractor business entity may substitute an active employee license number for a named individual qualifier at renewal.
- **states:** UT
- **sample (UT):** "If a plumbing or electrical business entity has maintained its license and has not violated the requirements of this chapter ... for a period of five consecutive years, the business entity may maintain its license under this chapter by recording an active employee name and registration/license number from the applicable trade on the renewal application"

## exemptions and unlicensed work limits

### `minor_plumbing_repair_exemption` — bool
- **what:** Whether the statute provides an exemption from licensure for minor plumbing repair work incidental to fixing a fixture or appliance in a residential or small commercial building, provided no piping or gas system is altered.
- **states:** UT
- **sample (UT):** "a person engaged in minor plumbing work that is incidental, as defined by the division by rule, to the repair of a fixture or an appliance in a residential or small commercial building ... provided that no modification is made to: existing culinary water, soil, waste, or vent piping; or a gas appliance or combustion system"

### `small_project_dollar_threshold` — int
- **what:** Maximum total project cost (labor and materials) below which an unlicensed person may perform certain construction work, with plumbing and electrical systems explicitly excluded from this exemption.
- **states:** UT
- **sample (UT):** "a person working on a project that has a total cost of less than $7,000 including labor, material, and changes to the agreed upon work if the construction trade: does not involve an electrical or plumbing system"

## continuing education specifics

### `continuing_education_hours_plumber` — int
- **what:** Number of continuing education hours a licensed plumber (individual, not contractor) must complete per two-year renewal cycle.
- **states:** UT
- **sample (UT):** "a licensed plumber shall complete 12 hours of continuing education under the continuing education program established under this section"

### `continuing_education_hours_contractor` — int
- **what:** Number of continuing education hours a licensed plumbing contractor must complete per two-year renewal cycle.
- **states:** UT
- **sample (UT):** "a contractor licensee under a license issued under this chapter shall complete six hours of approved continuing education during each two-year renewal cycle"
