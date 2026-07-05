# Discovered fields — private_probation

## what they can and cannot do

### `peace_officer_authority_excluded` — bool
- **what:** Whether the statute explicitly states that a private probation provider does NOT have the authority of a peace officer.
- **states:** UT
- **sample (UT):** "A private probation provider does not have the authority of a peace officer."

### `offense_level_limitation` — list[str]
- **what:** The categories of criminal offenses for which a private probation provider may provide services (e.g., minor offenses, misdemeanors).
- **states:** UT
- **sample (UT):** "whose services are limited to minor offenses and misdemeanor violations"

### `presentence_investigation_authorized` — bool
- **what:** Whether the provider is authorized to prepare presentence investigation reports in addition to supervision services.
- **states:** UT
- **sample (UT):** "the preparation of presentence investigation reports and the performance of supervision services by a private probation provider"

## fees and financial rules

### `funding_mechanism` — enum[court-ordered defendant fee, government contract, mixed]
- **what:** How the private probation provider's services are funded.
- **states:** UT
- **sample (UT):** "funded by a court-ordered fee, to be paid by the defendant"

### `dual_service_prohibition` — bool
- **what:** Whether the provider is prohibited from simultaneously providing probation services and other compensated services (e.g., therapy, education, rehabilitation) to the same defendant.
- **states:** UT
- **sample (UT):** "a private probation provider that is a licensee may not simultaneously provide to a defendant private probation services and other services for which the private probation provider receives compensation"

### `dual_service_exception_distance_miles` — int
- **what:** The minimum distance (in miles) from the defendant's residence within which no alternative licensee exists, triggering an exception to the dual-service prohibition.
- **states:** UT
- **sample (UT):** "no other licensees that provide the services are located within 50 miles of the defendant's residence"

## ethics and conduct standards

### `conflict_of_interest_disclosure_required` — bool
- **what:** Whether the provider must disclose financial, personal, or relational conflicts of interest to all parties.
- **states:** UT
- **sample (UT):** "disclose any circumstance that may create or give the appearance of a conflict of interest and any circumstance that may reasonably raise a question as to the private probation provider's impartiality"

### `impartiality_required` — bool
- **what:** Whether the statute explicitly requires the provider to maintain impartiality toward all parties.
- **states:** UT
- **sample (UT):** "shall maintain impartiality toward all parties"

### `confidentiality_required` — bool
- **what:** Whether the provider is required to maintain confidentiality or advise parties when confidentiality is not protected.
- **states:** UT
- **sample (UT):** "shall maintain confidentiality or, in cases where confidentiality is not protected, the private probation provider shall so advise the parties"

### `solicitation_on_court_property_prohibited` — bool
- **what:** Whether the provider is prohibited from soliciting defendants as clients on court property.
- **states:** UT
- **sample (UT):** "may not solicit defendants as supervision clients on any property that operates as a court of justice"

## practice setting and geographic rules

### `local_government_overlap_restriction` — bool
- **what:** Whether the provider is restricted from operating in a county where a local government agency already provides probation services without a formal contract with that agency.
- **states:** UT
- **sample (UT):** "may not provide private probation in a county where an agency of local government provides probation services unless the private probation provider has entered into a contract with the agency of local government"

### `business_license_required` — bool
- **what:** Whether the applicant must hold a local business license in the political subdivision where they intend to operate as a condition of state licensure.
- **states:** UT
- **sample (UT):** "submit evidence that a business license to engage in private probation has been issued by the political subdivision of the state in which the applicant intends to establish a business office or offices"

## reporting and oversight obligations

### `monthly_reporting_to_county_sheriff_required` — bool
- **what:** Whether the provider must submit monthly reports to each county sheriff identifying supervised individuals, their offenses, supervision level, and other relevant information.
- **states:** UT
- **sample (UT):** "shall provide a report each month to each county sheriff where the private probation provider provides private probation identifying each individual currently supervised in the county"

### `court_notification_of_supervision_required` — bool
- **what:** Whether the provider must notify the court that it is providing supervision services to a defendant.
- **states:** UT
- **sample (UT):** "notify the court that the private probation provider is providing supervision services to a defendant"

## defendant rights and informed consent

### `defendant_service_choice_required` — bool
- **what:** Whether the provider must give defendants a list of all available licensees for required assessments or treatment and allow the defendant to choose among them.
- **states:** UT
- **sample (UT):** "provide the defendant a list of all available licensees that provide the assessment, treatment, or other services; and permit the defendant to select a licensee"

### `written_informed_consent_required_for_dual_services` — bool
- **what:** Whether written informed consent from the defendant is required before a provider may simultaneously deliver probation and other compensated services.
- **states:** UT
- **sample (UT):** "the private probation provider obtains the defendant's written informed consent"

## licensing board structure

### `board_composition` — list[str]
- **what:** The required membership categories of the licensing board.
- **states:** UT
- **sample (UT):** "one member representing the administrative office of the courts; one member representing the Department of Corrections; two members licensed as private probation providers; and one member from the general public"
