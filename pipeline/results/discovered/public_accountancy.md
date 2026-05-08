# Discovered fields — public_accountancy

## scope_inclusion

### `attest_services_types` — list[str]
- **what:** Enumerated types of attest services that constitute the regulated scope of practice, typically defined by reference to AICPA/PCAOB standards.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+24)
- **sample (DE):** ""Attest" means providing the following services: (a) Any audit or other engagement to be performed in accordance with the Statements on Auditing Standards (SAS); (b) Any review of a financial statement to be performed in accordance with the Statements on Standards for Accounting and Review Services (SSARS); (c) Any examination of prospective financial information to be performed in accordance with the Statements on Standards for Attestation Engagements (SSAE); (d) Any engagement to be performed in accordance with the standards of the PCAOB; and (e) Any examination, review, or agreed upon procedures engagement to be performed in accordance with the SSAE, other than an examination described in paragraph (c)."

### `compilation_services_authorized` — bool
- **what:** Whether compilation services (presenting financial statements as management's representation without assurance) are separately defined and regulated as a distinct service type.
- **states:** AK, AL, CT, DE, GA, HI, ID, IL, … (+18)
- **sample (AK):** ""Compilation" means providing a service to be performed in accordance with Statements on Standards for Accounting and Review Services (SSARS) that is presented in the form of financial statements information that is the representation of management (owners) without undertaking to express any assurance on the statements."

### `attest_services_require_firm_permit` — bool
- **what:** Whether individuals with practice privileges or individual licensees must perform certain attest services (audits, PCAOB engagements) only through a firm holding a valid permit.
- **states:** AK, AL, CT, DE, FL, GA, HI, ID, … (+20)
- **sample (AK):** "An individual who qualifies for the practice privilege under this section who, for any entity with its home office in this state, performs any financial statement audit or other engagement to be performed in accordance with Statements on Auditing Standards may only do so through a firm which has obtained a permit issued under this chapter."

### `independence_requirement_for_attest` — bool
- **what:** Whether the statute explicitly requires a CPA to be independent with respect to an enterprise before expressing an opinion on its financial statements.
- **states:** FL, UT, VA
- **sample (FL):** "A certified public accountant shall not express an opinion on the financial statements of an enterprise unless she or he and her or his firm are independent with respect to such enterprise."

## other

### `education_semester_hours_required` — int
- **what:** Total semester hours of college education required for initial CPA licensure (typically 150 hours post-2000).
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+22)
- **sample (AK):** "The education and experience requirements for an applicant are a baccalaureate degree or its equivalent conferred by a college or university acceptable to the board and additional semester hours or post-baccalaureate study so that the total educational program includes at least 150 hours."

### `exam_sit_hours_minimum` — int
- **what:** Minimum semester hours of college education required before a candidate may sit for the CPA examination (often 120 hours, less than the full 150 required for licensure).
- **states:** AK, CT, DE, FL, GA, ID, IL, IN, … (+13)
- **sample (ND):** "The board may permit a candidate to take the examination if the candidate has at least one hundred twenty semester hours of college education."

### `ethics_exam_required` — bool
- **what:** Whether a separate ethics examination (e.g., AICPA ethics exam or state-specific ethics exam) is required as a condition of initial licensure.
- **states:** DE, ID, MT, SC, SD, UT, WY
- **sample (DE):** "The applicant has successfully passed the AICPA self-study course and examination in professional ethics."

### `practice_privilege_no_notice_required` — bool
- **what:** Whether out-of-state CPAs with substantially equivalent qualifications may practice in the state without providing notice, paying a fee, or making any submission to the board.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (AK):** "Notwithstanding any other provision of law, an individual who offers or renders professional services, whether in person or by mail, telephone, or electronic means, under this section shall be granted practice privileges in this state and no notice, fee, or other submission shall be provided by any such individual."

### `practice_privilege_consent_conditions` — list[str]
- **what:** Conditions to which an out-of-state CPA exercising practice privileges must consent, including board jurisdiction, compliance with state law, cessation if license lapses, and appointment of home-state board as agent for service of process.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (AK):** "Any individual licensee of another state exercising the privilege afforded under this section and the firm that employs that licensee hereby simultaneously consent, as a condition of the grant of this privilege: (1) To the personal and subject matter jurisdiction and disciplinary authority of the board; (2) To comply with this chapter and the board's rules; (3) That in the event the license from the state of the individual's principal place of business is no longer valid, the individual will cease offering or rendering professional services in this state individually and on behalf of a firm; and (4) To the appointment of the state board which issued the individual's license as the individual's or firm's agent for service of process."

### `peer_review_required_for_firm_renewal` — bool
- **what:** Whether peer review is required as a condition for renewal of a firm permit or registration.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (AK):** "The board shall, not more frequently than once every three years, require as a condition for renewal of a permit of a firm that the applicant firm undergo a peer review conducted as required by the board by regulation."

### `peer_review_max_frequency_years` — int
- **what:** Maximum frequency (in years) at which peer review may be required for firm permit renewal.
- **states:** AK, AL, CT, DE, FL, GA, HI, ID, … (+19)
- **sample (AK):** "The board shall, not more frequently than once every three years, require as a condition for renewal of a permit of a firm that the applicant firm undergo a peer review."

### `peer_review_records_privileged` — bool
- **what:** Whether peer review proceedings, records, and work papers are privileged and not subject to discovery or introduction into evidence in civil or administrative proceedings.
- **states:** AZ, CT, FL, GA, HI, ID, IL, IN, … (+12)
- **sample (IL):** "The proceedings, records, and work papers of a review committee shall be privileged and shall not be subject to discovery, subpoena, or other means of legal process or introduction into evidence in any civil action, arbitration, administrative proceeding, or board proceeding."

### `inactive_license_status_available` — bool
- **what:** Whether a licensee who is not engaged in the practice of public accounting may place their license on inactive status, typically with reduced fees and no CPE requirement.
- **states:** AK, AL, CT, DE, FL, GA, ID, IL, … (+18)
- **sample (AK):** "Notwithstanding AS 08.04.105 or 08.04.195, an individual holding a license who is not engaged in the practice of public accounting may maintain the license in good standing by notifying the board that the individual is inactive and paying the required fee."

### `retired_license_status_available` — bool
- **what:** Whether a licensee may place their license on a retired status, typically with reduced or no fees and no CPE requirement, with restrictions on active practice.
- **states:** AL, FL, GA, ID, IN, ND, NH, SC, … (+3)
- **sample (WY):** "The board by regulation may allow persons to retire the certificate. A person classified as retired shall pay a fee to be established by board rule. A person classified as retired may assume or use the title or designation 'certified public accountant' or the abbreviation 'CPA' and shall use the words 'retired' adjacent to the designation."

### `client_confidentiality_privilege` — bool
- **what:** Whether communications between a licensee and client are confidential and privileged, with specified exceptions for professional standards, court proceedings, peer review, and ethical investigations.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+22)
- **sample (AK):** "A license holder, a permit holder, or a practice privilege holder or a partner, an officer, a shareholder, a member, or an employee of a license holder, a permit holder, or a practice privilege holder may not reveal information communicated to the license holder, permit holder or practice privilege holder by a client about a matter concerning which the client has employed the license holder, permit holder, or practice privilege holder in a professional capacity."

### `working_papers_ownership_by_licensee` — bool
- **what:** Whether working papers, schedules, and memoranda made by a licensee incident to professional services remain the property of the licensee (absent contrary agreement), with restrictions on transfer without client consent.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+22)
- **sample (AK):** "All statements, records, schedules, working papers, and memoranda made by a certified public accountant or a public accountant incident to or in the course of professional service to a client, except reports submitted to a client, are the property of the accountant, in the absence of an express agreement between the accountant and the client to the contrary."

### `single_act_evidence_sufficient` — bool
- **what:** Whether evidence of a single prohibited act is sufficient to justify a penalty, injunction, or conviction without evidence of a general course of conduct.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+20)
- **sample (AK):** "In any action, evidence of the commission of a single act prohibited by this chapter is sufficient to justify an injunction or a conviction without evidence of a general course of conduct."

### `cpa_emeritus_or_retired_status_available` — bool
- **what:** Whether the state provides a formal 'CPA Emeritus' or 'CPA Retired' status for licensees who have permanently ceased practice, with reduced or no fees and no CPE requirement.
- **states:** AL, FL, GA, ID, IN, ND, NH, SC, … (+3)
- **sample (UT):** "A person currently licensed as a certified public accountant may, on any renewal date of that license, apply for and obtain a transfer of that license to a status of CPA emeritus registration if the licensee is at least 60 years of age as of the date of renewal, has a disability, or the board finds other good cause for believing that the licensee will not return to the practice of public accountancy."

### `government_audit_cpe_requirement` — bool
- **what:** Whether the state imposes additional or specific continuing professional education requirements for CPAs engaged in auditing governmental entities.
- **states:** FL, OH
- **sample (FL):** "The board shall adopt rules establishing the continuing education requirements for Florida certified public accountants who are engaged in the audit of a governmental entity. The board shall approve subjects directly related to the governmental environment and to governmental auditing for purposes of satisfying the requirement of this subsection."

### `ethics_cpe_hours_required` — int
- **what:** Minimum hours of ethics-related continuing professional education required per renewal period.
- **states:** FL, SC, UT
- **sample (FL):** "Not less than 5 percent of the total hours required by the board shall be in ethics applicable to the practice of public accounting. This requirement shall be administered by providers approved by the board, and a majority of the hours shall include a review of the provisions of chapter 455 and this chapter and the related administrative rules."

### `hawaii_attest_work_supplement_required` — bool
- **what:** Whether Hawaii requires a state-specific supplemental peer review report covering Hawaii attest engagements when the primary peer review does not include Hawaii offices or engagements.
- **states:** HI
- **sample (HI):** "A firm required to undergo a peer review under this chapter shall engage the services of a practitioner or firm holding a permit issued under section 466-7 to perform the following procedures to supplement the peer review report: Obtain from the reviewed firm a list of Hawaii attest engagements included in the scope of the peer review."

### `liability_privity_limitation` — bool
- **what:** Whether the state limits CPA liability to third parties not in privity of contract, with exceptions for fraud, intentional misrepresentation, or known intended reliance.
- **states:** IL, IN, UT, WY
- **sample (UT):** "A licensee, a CPA firm registered under this chapter, and any employee, partner, member, officer, or shareholder of a licensee or CPA firm are not liable to persons with whom they are not in privity of contract for civil damages resulting from acts, omissions, decisions, or other conduct in connection with professional services performed by that person, except for acts, omissions, decisions, or conduct that constitute fraud or intentional misrepresentations."

### `statute_of_limitations_for_accountant_negligence` — str
- **what:** Specific statute of limitations period for actions based on negligence or breach of contract against accountants, typically shorter than general tort limitations.
- **states:** IN, ND, WY
- **sample (ND):** "An action covered by this section may not be brought in any court in this state unless the suit is commenced on or before the earlier of: (a) Two years from the date the alleged act, omission, or neglect is discovered or should have been discovered by the exercise of reasonable diligence; or (b) Six years after the service for which the suit is brought has been performed."

### `client_records_return_obligation` — bool
- **what:** Whether the statute explicitly requires a licensee to return client-provided records and furnish copies of working papers that constitute part of the client's records upon client request.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+20)
- **sample (AK):** "A licensee shall furnish to a client or former client, upon request and reasonable notice: (1) A copy of the licensee's working papers, to the extent that such working papers include records that would ordinarily constitute part of the client's records and are not otherwise available to the client; and (2) Any accounting or other records belonging to, or obtained from or on behalf of, the client that the licensee removed from the client's premises or received for the client's account."

## facility

### `firm_majority_cpa_ownership_required` — bool
- **what:** Whether a simple majority (more than 50%) of firm ownership in terms of financial interests and voting rights must belong to licensed CPAs.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (AK):** "Notwithstanding any other provision of law, a simple majority of the ownership of the firm, in terms of financial interests and voting rights of all partners, officers, shareholders, members, or managers, belongs to holders of a certificate who are licensed in some state."

### `nonlicensee_firm_owners_permitted` — bool
- **what:** Whether CPA firms may include owners who are not licensed CPAs, subject to specified conditions.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (AK):** "For the purposes of issuing a permit under this section, a firm may include owners who are not certified public accountants if (1) the firm designates a certified public accountant or an individual with practice privileges to be responsible for the proper registration of the entity; (2) all of the owners of the firm who are not certified public accountants are active individual participants in the firm or in an entity affiliated with the firm."

### `out_of_state_firm_no_office_exemption` — bool
- **what:** Whether a firm without an office in the state may provide certain services (compilation, review, or non-attest services) without obtaining a firm permit, subject to specified conditions.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (GA):** "A firm that does not have an office in this state may perform services described in subdivision (B) or (E) of paragraph (2) of Code Section 43-3-2 for a client that specifies a location in this state to which any service is directed and may use the title 'CPA' or 'CPA firm' without being licensed as provided in this Code section only if it meets the qualifications described in paragraph (1) of subsection (a) of this Code section, complies with the board's rules or regulations regarding peer review, and performs such services through an individual with substantial equivalency practice privileges."

### `firm_corrective_action_period_for_ownership_noncompliance` — bool
- **what:** Whether firms that fall out of compliance with ownership requirements due to changes in personnel are granted a reasonable period to take corrective action before facing permit suspension or revocation.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+20)
- **sample (AL):** "Firms which fall out of compliance with the provisions of this section due to changes in firm ownership or personnel, after receiving or renewing a permit, shall take corrective action to bring the firm back into compliance as quickly as possible. The board may grant a reasonable period of time for a firm to take such corrective action. Failure to bring the firm back into compliance within a reasonable period as defined by the board will result in the suspension or revocation of the firm permit."

### `firm_permit_required_for_attest_services` — bool
- **what:** Whether a firm must hold a valid permit or registration to provide attest or compilation services, separate from individual licensure requirements.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (AL):** "No firm shall provide attest services or assume or use the title or designation 'certified public accountants' or the abbreviation 'CPAs' or any other title, designation, words, letters, abbreviation, sign, card, or device tending to indicate that such firm is a CPA firm unless the firm holds a valid permit issued under this chapter."

## supervision_delegation

### `office_supervision_by_licensed_cpa_required` — bool
- **what:** Whether each office of a firm established in the state for the practice of public accounting must be under the direct supervision of a licensed CPA.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (AK):** "Each office established or maintained in this state for the practice of public accounting shall be under the direct supervision of an individual who holds a license issued under this chapter."

### `attest_report_signer_competency_requirement` — bool
- **what:** Whether individuals who sign or authorize signing of attest or compilation reports on behalf of a firm must meet specific competency requirements set out in professional standards.
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (IN):** "Any individual licensee who is responsible for supervising attest or compilation services and signs or authorizes an individual to sign the accountant's report on behalf of the firm shall meet the competency requirements set out in the professional standards adopted by the board for the services."

## scope_exclusion

### `commission_prohibition_during_attest` — bool
- **what:** Whether a licensee is prohibited from receiving commissions or referral fees when also performing attest or compilation services for the same client.
- **states:** AZ, CT, DE, FL, GA, ID, IL, IN, … (+15)
- **sample (ID):** "A licensee shall not for a commission recommend or refer to a client any product or service, or for a commission recommend or refer any product or service to be supplied by a client, or receive a commission, when the licensee or the licensee's firm also performs for that client: (i) An attest service; or (ii) A compilation when the licensee expects, or reasonably might expect, that a third party will use the compilation and the compilation report does not disclose a lack of independence."

### `contingent_fee_prohibition_during_attest` — bool
- **what:** Whether a licensee is prohibited from performing services for a contingent fee when also performing attest or compilation services for the same client, or from preparing tax returns for a contingent fee.
- **states:** AZ, CT, DE, FL, GA, ID, IL, IN, … (+15)
- **sample (ID):** "A licensee shall not perform for a contingent fee any professional services for, or receive such a fee from, a client for whom the licensee or the licensee's firm performs: (i) An attest service; or (ii) A compilation, when the licensee expects, or reasonably might expect, that a third party will use the compilation and the compilation report does not disclose a lack of independence. A licensee shall not prepare an original or amended tax return or claim for a tax refund for a contingent fee for any client."

### `safe_harbor_disclaimer_language_for_nonlicensees` — bool
- **what:** Whether the statute provides specific safe harbor disclaimer language that nonlicensees may use when preparing financial statements without expressing assurance, thereby avoiding unlicensed practice violations.
- **states:** AK, AL, AZ, CT, DE, FL, GA, ID, … (+20)
- **sample (AK):** ""I (we) have prepared the accompanying (financial statements) of (name of entity) as of (time period) for the (period) then ended. This presentation is limited to preparing in the form of financial statements information that is the representation of management (owners). I (we) have not audited or reviewed the accompanying financial statements and accordingly do not express an opinion or any other form of assurance on them.""

### `foreign_accountant_practice_exception` — bool
- **what:** Whether holders of foreign country accounting designations may practice in the state under limited conditions (serving only clients from their home country, using only their foreign title, not issuing reports on domestic entities).
- **states:** AK, AL, AZ, CT, DE, FL, GA, HI, … (+21)
- **sample (IN):** "This chapter does not apply to an individual or a firm that holds a designation granted in a foreign country entitling the holder to engage in the practice of accountancy or its equivalent in that country, whose activities in Indiana are limited to the provision of professional services to individuals or firms who are residents, to governments, or to business entities of the country in which the individual holds the entitlement, that does not issue reports with respect to the financial statements of another individual, firm, or governmental unit in Indiana, and that does not use in Indiana any title or designation other than the title or designation under which the individual practices in the individual's country."

## advanced_tier

### `registered_municipal_accountant_designation` — bool
- **what:** Whether the state has a specialized 'Registered Municipal Accountant' designation requiring additional examination, limited to auditing municipal or county financial statements.
- **states:** NJ
- **sample (NJ):** "A certified public accountant or public accountant holding an active license shall qualify as a registered municipal accountant by passing a registered municipal accountant's examination. Only a registered municipal accountant licensed in this State shall undertake the work of auditing the financial statements of any municipality or county."

### `public_school_accountant_designation` — bool
- **what:** Whether the state has a specialized 'Public School Accountant' designation required for auditing school district financial statements.
- **states:** NJ
- **sample (NJ):** "Any person who undertakes the work of auditing the financial statements of any school district in New Jersey shall qualify as a public school accountant (PSA) by submitting an application to the board, demonstrating satisfactorily to the board that the individual holds an active license in New Jersey as a certified public accountant, public accountant, or registered municipal accountant, and paying the required fee."

### `accounting_practitioner_tier` — bool
- **what:** Whether the state has a separate 'Accounting Practitioner' or 'Licensed Public Accountant' tier below CPA with its own examination, education, and scope-of-practice requirements.
- **states:** DE, HI, ID, IN, ME, ND, NH, NJ, … (+5)
- **sample (IN):** ""Accounting practitioner" means a person certified under IC 25-2.1-6. An individual registered as an accounting practitioner may not prepare or render accounting opinions or certificates for any purpose, including financial statements, schedules, reports, or exhibits for publication, credit purposes, and use in a court."
