# Discovered fields — bail_bond_agent

## license types and tiers within the profession

### `agent_type_tiers` — list[str]
- **what:** The distinct license categories or tiers recognized within the bail bond profession in a given state.
- **states:** AR, AZ, CT, FL, MN, MO, NC
- **sample (FL):** ""Professional bail bond agent" means any person who pledges United States currency, United States postal money orders, or cashier's checks as security for a bail bond... "Limited surety agent" means any individual appointed by an insurer by power of attorney to execute or countersign bail bonds."

### `runner_license_available` — bool
- **what:** Whether the state recognizes a separate 'runner' license for persons who assist bail bondsmen but do not independently write bonds.
- **states:** FL, NC
- **sample (NC):** ""Runner" - A person employed by a bail bondsman for the purpose of assisting the bail bondsman in presenting the defendant in court when required, assisting in the apprehension and surrender of defendant to the court, keeping the defendant under necessary surveillance, or executing bonds on behalf of the licensed bondsman when the power of attorney has been duly recorded."

### `bail_enforcement_agent_license_available` — bool
- **what:** Whether the state has a separate license category for bail enforcement agents (bounty hunters) who apprehend fugitive principals.
- **states:** CT, DE, FL
- **sample (CT):** "No person shall, as a surety on a bond in a criminal proceeding or an agent of such surety, engage in the business of taking or attempting to take into custody the principal on the bond who has failed to appear in court... unless such person is licensed as a professional bondsman under chapter 533, a surety bail bond agent under chapter 700f or a bail enforcement agent under sections 29-152f to 29-152i."

## supervision and delegation

### `first_year_supervision_required` — bool
- **what:** Whether new licensees must operate under the supervision of an experienced bail bondsman for an initial period before acting independently.
- **states:** FL, NC
- **sample (NC):** "Except as provided in subsection (d) of this section, a first-year licensee shall operate only under the supervision of and from the official business address of a licensed supervising bail bondsman for the first 12 months of licensure."

### `first_year_supervision_duration_months` — int
- **what:** The number of months a new licensee must work under a supervising bail bondsman before operating independently.
- **states:** FL, NC
- **sample (NC):** "a first-year licensee shall operate only under the supervision of and from the official business address of a licensed supervising bail bondsman for the first 12 months of licensure."

### `managing_general_agent_required` — bool
- **what:** Whether insurers writing bail bonds in the state must appoint a managing general agent to supervise their bail bond agents.
- **states:** CT, FL, MN, NC
- **sample (FL):** "Any insurer regularly engaged in the execution of bail bonds in this state shall have a managing general agent in this state to supervise its agents."

### `power_of_attorney_required` — bool
- **what:** Whether a bail bond agent must hold and attach a numbered power of attorney from the bail bond company or insurer to each bond executed.
- **states:** AR, AZ, CT, FL, MN, NC
- **sample (AR):** "A professional bail bondsman shall not execute, issue, or deliver an appearance bond in this state without holding a valid appointment from a professional bail bond company and without attaching to the appearance bond an executed and numbered power of attorney referencing the professional bail bond company."

## premium and fee rules

### `premium_rate_filed_and_approved` — bool
- **what:** Whether the premium rate charged for bail bonds must be filed with and approved by the state insurance regulator, and agents must charge exactly that rate.
- **states:** AR, AZ, CT, FL, MN, NC
- **sample (CT):** "No surety bail bond agent shall execute a bail bond without charging the premium rate approved by the commissioner pursuant to chapter 701."

### `premium_rate_percentage` — str
- **what:** The standard or maximum premium rate (as a percentage of bond face value) set by statute.
- **states:** AR, NC
- **sample (AR):** "the premium or compensation for giving bond or depositing money or property as bail on any bond shall be ten percent (10%)"

### `minimum_premium_amount` — int
- **what:** The minimum dollar amount that must be charged as a premium regardless of the bond amount.
- **states:** AR, MN
- **sample (AR):** "The minimum compensation for giving bond or depositing money or property as bail on any bond shall be not less than fifty dollars ($50.00)."

### `premium_financing_allowed` — bool
- **what:** Whether agents may enter into installment or deferred payment arrangements with principals for unpaid premium, and the rules governing such arrangements.
- **states:** CT, MN, NC
- **sample (CT):** "A surety bail bond agent may enter into a premium financing arrangement with a principal or any indemnitor in which such agent extends credit to such principal or indemnitor."

### `premium_financing_minimum_down_payment_pct` — str
- **what:** The minimum percentage of the total premium that must be collected before posting a bond when a deferred payment arrangement is used.
- **states:** CT, MN
- **sample (CT):** "the principal on the bail bond or any indemnitor to make a minimum down payment of thirty-five per cent of the premium due"

### `build_up_fund_allowed` — bool
- **what:** Whether a portion of the premium may be held in a trust account (build-up fund) by the insurer or managing general agent to cover future forfeitures or apprehension costs.
- **states:** CT, MN
- **sample (CT):** ""Build-up funds" means a percentage of the premium received by a surety bail bond agent for the execution of a bail bond, which are held in a trust account by the insurer or managing general agent."

## collateral rules

### `collateral_receipt_required` — bool
- **what:** Whether agents must provide a written, numbered receipt describing collateral accepted from the principal or indemnitor.
- **states:** AR, AZ, CT, FL, MN, NC
- **sample (AR):** "When a licensee accepts collateral, he or she shall give a prenumbered written receipt for it, and this receipt shall give in detail a full account of the collateral received."

### `collateral_held_in_fiduciary_capacity` — bool
- **what:** Whether statute explicitly requires collateral to be held in a fiduciary or trust capacity, separate from the agent's own funds.
- **states:** CT, FL, MN, NC
- **sample (FL):** "Collateral security shall be received and held in the insurer's name by the bail bond agent in a fiduciary capacity and, prior to any forfeiture of bail, shall be kept separate and apart from any other funds or assets of such bail bond agent."

### `collateral_return_deadline_days` — int
- **what:** The number of days after bond termination or discharge within which collateral must be returned to the depositor.
- **states:** CT, FL, MN, NC
- **sample (CT):** "the insurer, managing general agent or surety bail bond agent shall return the collateral security or other indemnity... not later than twenty-one days after receipt of a written report from the court that the bail bond has been terminated."

### `large_cash_collateral_threshold_and_handling` — str
- **what:** The dollar threshold above which cash collateral must be forwarded to the insurer in a specific form (e.g., cashier's check, wire transfer) rather than held by the agent.
- **states:** CT, FL, MN
- **sample (FL):** "A bail bond agent may accept collateral security in excess of $50,000 cash per bond, provided any amount over $50,000 cash is payable to the insurer in the form of a cashier's check, United States postal money order, certificates of deposit, or wire transfer and is remitted to and held by the insurer."

### `quitclaim_deed_as_collateral_prohibited` — bool
- **what:** Whether statute explicitly prohibits accepting a quitclaim deed on real property as collateral for a bail bond.
- **states:** FL, MN
- **sample (FL):** "A quitclaim deed for property may not be taken as collateral."

## prohibited conduct and advertising

### `solicitation_restrictions` — list[str]
- **what:** Specific locations or methods of solicitation that are prohibited for bail bond agents.
- **states:** AR, AZ, CT, FL, MN, NC
- **sample (FL):** "Directly or indirectly solicit business in or on the property or grounds of a jail, prison, or other place where prisoners are confined or in or on the property or grounds of any court."

### `attorney_referral_prohibited` — bool
- **what:** Whether agents are prohibited from suggesting, advising, or requiring the principal to engage a specific attorney.
- **states:** AR, AZ, CT, FL, MN, NC
- **sample (AR):** "Require as a condition of his or her executing a bail bond that the principal agree to engage the services of a specified attorney."

### `rebate_and_kickback_prohibition` — bool
- **what:** Whether agents are prohibited from paying fees, rebates, or anything of value to law enforcement, public officials, attorneys, or principals in connection with bail bond business.
- **states:** AR, AZ, CT, FL, MN, NC
- **sample (FL):** "Pay a fee or rebate or give or promise anything of value to a jailer, police officer, peace officer, committing trial court judge or any other person who has power to arrest or to hold in custody or to any public official or public employee in order to secure a settlement, compromise, remission, or reduction of the amount of any bail bond."

### `law_enforcement_prohibited_from_acting_as_agent` — bool
- **what:** Whether law enforcement officers, judicial officials, and similar public employees are explicitly prohibited from acting as bail bond agents or having a financial interest in bail bond businesses.
- **states:** AR, AZ, CT, FL, MN, NC
- **sample (NC):** "No sheriff, deputy sheriff, other law-enforcement officer, judicial official, attorney, parole officer, probation officer, jailer, assistant jailer, employee of the General Court of Justice, nor other public employee assigned to duties relating to the administration of criminal justice... may in any case become surety on a bail bond for any person."

### `impersonation_of_government_official_prohibited` — bool
- **what:** Whether agents are prohibited from wearing or displaying badges, uniforms, or insignia that imply they are government employees or law enforcement officers.
- **states:** CT, FL, NC
- **sample (CT):** "No professional bondsman licensed under chapter 533, surety bail bond agent licensed under chapter 700f or bail enforcement agent licensed under sections 29-152f to 29-152i, inclusive, shall wear, carry or display any uniform, badge, shield or other insignia or emblems that purport to indicate that such bondsman or agent is an employee, officer or agent of the state."

## apprehension and fugitive recovery rules

### `firearm_permit_required_for_enforcement` — bool
- **what:** Whether bail bond agents or bail enforcement agents must obtain a special permit to carry a firearm while performing their duties.
- **states:** CT, FL
- **sample (CT):** "No professional bondsman licensed under chapter 533, surety bail bond agent licensed under chapter 700f or bail enforcement agent licensed under sections 29-152f to 29-152i, inclusive, shall carry a pistol, revolver or other firearm while engaging in the business of a professional bondsman, surety bail bond agent or bail enforcement agent... unless such bondsman or agent obtains a special permit from the Commissioner."

### `law_enforcement_notification_before_apprehension` — bool
- **what:** Whether agents must notify local law enforcement before attempting to take a principal into custody.
- **states:** CT, MN
- **sample (CT):** "Prior to taking or attempting to take into custody the principal on a bond, a professional bondsman licensed under chapter 533, a surety bail bond agent licensed under chapter 700f or a bail enforcement agent licensed under sections 29-152f to 29-152i, inclusive, shall notify the police department or resident state trooper for, or state police troop having jurisdiction over, the municipality in which the principal is believed to be located."

### `surrender_of_principal_rules` — bool
- **what:** Whether the state has specific statutory procedures governing when and how a surety may surrender a principal before or after bond forfeiture.
- **states:** AR, CT, FL, MN, NC
- **sample (NC):** "At any time before there has been a breach of the undertaking in any type of bail or fine and cash bond the surety may surrender the defendant to the sheriff of the county in which the defendant is bonded to appear."

## financial security and bond forfeiture

### `security_deposit_required_for_company` — bool
- **what:** Whether bail bond companies or professional bondsmen must maintain a security deposit (letter of credit, certificate of deposit, or pledged securities) with the state as a condition of licensure.
- **states:** AR, AZ, NC
- **sample (AR):** "An applicant for a professional bail bond company license shall file with the Professional Bail Bond Company and Professional Bail Bondsman Licensing Board an irrevocable letter of credit from an Arkansas chartered bank or a federally chartered bank in Arkansas or a certificate of deposit."

### `security_deposit_minimum_amount` — str
- **what:** The minimum dollar amount of the security deposit or financial guarantee required from a bail bond company or professional bondsman.
- **states:** AR, AZ, NC
- **sample (AR):** "The minimum amount for a professional bail bond company initially licensed on or after July 1, 2009, shall be two hundred fifty thousand dollars ($250,000)."

### `unpaid_forfeiture_judgment_limit` — bool
- **what:** Whether the state imposes a cap on the total amount of unpaid bond forfeiture judgments a company may carry before its license is suspended.
- **states:** AR, FL, MO
- **sample (AR):** "There shall be an initial one hundred thousand dollars ($100,000) limit on active unpaid bond forfeiture judgments for each bail bonding company... When a company's unpaid bond forfeiture or forfeitures reach one hundred thousand dollars ($100,000) or the total amount of security deposit posted with the board, whichever is higher, the company license shall be suspended."

### `forfeiture_notice_and_reinstatement_deadline` — bool
- **what:** Whether the state specifies a deadline by which courts must order forfeiture and notify the surety after a principal fails to appear, with reinstatement rights if the deadline is missed.
- **states:** MN, MO
- **sample (MN):** "The court must order a bail bond forfeited and send notice to the surety, bail bond agency, or producer no later than 30 days from the date of a principal failing to appear at a scheduled hearing. If a court fails to forfeit a bail bond within 30 days... the court must allow for a reinstatement and discharge of the bail bond without penalty."

## recordkeeping and reporting

### `quarterly_bond_reporting_required` — bool
- **what:** Whether bail bond companies must file periodic (quarterly or monthly) reports with the licensing authority detailing bonds written, premiums collected, and bond status.
- **states:** AR, CT, FL, MN, NC
- **sample (AR):** "Each professional bail bond company shall file a bail bond report quarterly with the board. The report shall include the following information on each bail bond: The assigned number of the bond and current status of the bond, whether pending disposition or exonerated; To whom the bond was written; The date the bail bond was written..."

### `bond_register_required` — bool
- **what:** Whether agents must maintain a daily or permanent bond register recording details of every bond executed.
- **states:** AZ, MN, NC
- **sample (AZ):** "each bail bond agent and general lines agent who is engaged in the bail bond business shall maintain a daily bond register that is the original and permanent record of all bonds or undertakings executed by the licensee."

### `record_retention_period_years` — int
- **what:** The minimum number of years that bail bond records must be retained after a transaction is completed.
- **states:** AZ, CT, FL, MN, NC
- **sample (AZ):** "The licensee shall keep all the records as to any particular transaction available and open to the inspection of the director at any business time during the three years immediately after the date of completion of the transaction."

### `premium_trust_account_required` — bool
- **what:** Whether premiums collected must be deposited into a separate trust account before being remitted to the surety or bail bond agency.
- **states:** CT, FL, MN
- **sample (MN):** "A payment made to or received by the producer, bail bond agency, or surety must be deposited into a premium trust account that is maintained by the producer, bail bond agency, or surety within seven business days."

### `statewide_registry_of_licensees` — bool
- **what:** Whether the state maintains a centralized electronic or statewide registry of licensed bail bondsmen accessible to courts and law enforcement.
- **states:** AR, MO, NC
- **sample (NC):** "On or before October 1, 2006, the Administrative Office of the Courts shall establish a statewide Electronic Bondsmen Registry (Registry) for all licenses requiring registration under this section."

## applicant eligibility and background

### `residency_requirement` — bool
- **what:** Whether applicants must be residents of the state for a specified period before applying for a bail bond license.
- **states:** AR, AZ, CT, FL, NC
- **sample (AZ):** "An applicant for a bail bond agent license shall submit an affidavit attesting to the applicant's residency in this state for at least one year immediately preceding the date of application."

### `citizenship_or_work_authorization_required` — bool
- **what:** Whether applicants must be U.S. citizens or documented legal residents with work authorization.
- **states:** CT, FL, NC
- **sample (FL):** "Is a United States citizen or legal alien who possesses work authorization from the United States Bureau of Citizenship and Immigration Services and is a resident of this state."

### `high_school_diploma_required` — bool
- **what:** Whether applicants must hold a high school diploma or its equivalent as a condition of licensure.
- **states:** CT, FL, NC
- **sample (FL):** "Is a natural person who has reached the age of 18 years and holds a high school diploma or its equivalent."

### `disqualifying_criminal_offenses` — list[str]
- **what:** Categories of criminal convictions that automatically disqualify an applicant from licensure.
- **states:** AR, AZ, CT, DE, FL, MO, NC
- **sample (NC):** "The Commissioner shall deny, revoke, or refuse to renew any license under this Article if the applicant or licensee is or has ever been convicted of a felony."

## education before and after licensing

### `prelicense_education_hours` — int
- **what:** The number of hours of pre-license education required before an applicant may sit for the licensing examination.
- **states:** AR, FL, MO, NC
- **sample (NC):** "each person shall complete at least 12 hours of education as provided by an approved provider in subjects pertinent to the duties and responsibilities of a runner or bail bondsman"

### `prelicense_education_hours_classroom_required` — int
- **what:** The number of hours of classroom instruction specifically required as part of the pre-license education course.
- **states:** CT, FL
- **sample (FL):** "Within 2 years immediately before applying for the license, has successfully completed a basic certification course in the criminal justice system which consists of at least 120 hours of classroom instruction with a passing grade of 80 percent or higher."

### `continuing_education_hours_per_period` — int
- **what:** The number of continuing education hours required per renewal period to maintain a bail bond license.
- **states:** AR, CT, FL, MO, NC
- **sample (AR):** "Each person licensed as a professional bail bondsman shall annually complete not less than six (6) hours of continuing education in subjects relating to the authority and responsibilities of a bail bondsman as a condition of renewing his or her license."

### `continuing_education_period_years` — int
- **what:** The length of the renewal period (in years) over which continuing education hours must be completed.
- **states:** FL, MO, NC
- **sample (FL):** "Each person subject to this chapter must complete a minimum of 14 hours of continuing education courses every 2 years."

### `continuing_education_exemption_for_senior_licensees` — bool
- **what:** Whether long-tenured or elderly licensees are exempt from continuing education requirements.
- **states:** AR, NC
- **sample (AR):** "Any licensed professional bail bondsman who is sixty-five (65) years of age or older and who has been licensed as a bail bondsman for fifteen (15) years or more shall be exempt from both the education and continuing education requirements."

### `online_education_prohibited` — bool
- **what:** Whether the state explicitly prohibits offering required pre-license or continuing education courses solely online.
- **states:** FL, NC
- **sample (NC):** "The Commissioner shall not authorize educational courses to be offered solely online."

## special entity types and restrictions

### `charitable_bail_organization_regulated` — bool
- **what:** Whether the state has specific statutory provisions regulating charitable or nonprofit organizations that post bail on behalf of defendants.
- **states:** FL, KY
- **sample (KY):** ""Charitable bail organization" means an organization, including but not limited to an organization exempt under Section 501(c)(3) of the Internal Revenue Code, that solicits or accepts donations from the public for the purpose of furnishing bail, making bonds, or entering into undertakings, as surety."

### `bail_bond_agency_license_separate_from_agent_license` — bool
- **what:** Whether the state requires a separate license for the bail bond agency (business entity) distinct from the individual agent's license.
- **states:** AR, FL, MN
- **sample (FL):** "Effective January 1, 2024, the department may issue a bail bond agency license to any person only after such person files a written application with the department and qualifies for such license."

### `agency_ownership_experience_requirement` — bool
- **what:** Whether owners or operators of a bail bond agency must themselves be licensed and actively engaged as bail bond agents for a minimum period before owning or controlling an agency.
- **states:** AR, FL
- **sample (FL):** "A person may not own, control, manage, or otherwise have a pecuniary interest in a bail bond agency unless such individual is licensed pursuant to s. 648.27, appointed through the department, and actively engaged as a bail bond agent for at least the preceding 24 months."

### `bondsman_access_to_court_records` — bool
- **what:** Whether licensed bail bondsmen are granted statutory access to court criminal and civil records to evaluate defendants for bail purposes.
- **states:** MO, NC
- **sample (MO):** "Any bail bond agent licensed in the state of Missouri shall have access to all publicly available court records of the defendant by available means to make a realistic assessment of the defendant's probability of attending all court dates."
