# Discovered fields — dietetics

## types of credentials and license tiers

### `license_type_structure` — list[str]
- **what:** The distinct credential or license types recognized by the state (e.g., licensed dietitian, licensed nutritionist, dietitian-nutritionist, registered dietitian, provisionally licensed dietitian).
- **states:** AK, AL, AR, CA, CT, DE, GA, HI, … (+1)
- **sample (AL):** "LICENSED DIETITIAN/NUTRITIONIST. A person licensed under this chapter. TEMPORARILY LICENSED DIETITIAN/NUTRITIONIST. A person temporarily licensed under this chapter."

### `provisional_license_available` — bool
- **what:** Whether the state offers a provisional or temporary license allowing practice under supervision while completing full licensure requirements.
- **states:** AL, AR, GA
- **sample (AR):** "A provisional license to practice as a dietitian may be issued by the Arkansas Dietetics Licensing Board upon the filing of an application and submission of evidence of successful completion of the education requirements."

### `provisional_license_duration_months` — int
- **what:** Duration in months of a provisional or temporary license before it expires.
- **states:** AL, AR, GA
- **sample (AR):** "A provisional license shall expire eighteen (18) months from the date of issuance."

### `provisional_license_requires_supervision` — bool
- **what:** Whether a provisional or temporary license restricts the holder to practice only under the supervision of a fully licensed dietitian.
- **states:** AL, AR, GA
- **sample (AR):** "A provisional license shall permit the holder to practice only under the supervision of a dietitian licensed in this state."

### `dietetic_technician_recognized` — bool
- **what:** Whether the state statute explicitly recognizes a dietetic technician credential as a distinct, lower-tier role that may perform limited functions under supervision.
- **states:** AL, AR, CA, CT, DE, GA
- **sample (AL):** "DIETETIC TECHNICIAN. A person who is trained to perform specific dietetic functions of a licensed dietitian/nutritionist as defined by this chapter under the direct supervision of a licensed dietitian/nutritionist."

### `rd_credential_accepted_in_lieu_of_state_requirements` — bool
- **what:** Whether holding a current Registered Dietitian (RD/RDN) credential from the Commission on Dietetic Registration is explicitly accepted as satisfying all or most state licensure requirements.
- **states:** AK, AL, AR, CA, CT, DE, GA, HI, … (+1)
- **sample (DE):** "Persons who provide evidence of current registration as a registered dietitian awarded by the Commission on Dietetic Registration, credentialing agency of the American Dietetic Association shall be considered to have met the qualifications for licensure under this chapter."

### `alternative_credential_pathways` — list[str]
- **what:** Non-RD national credentials or membership bodies that the state accepts as an alternative pathway to licensure (e.g., Certified Nutrition Specialist, American Board of Nutrition diplomate).
- **states:** AK, AL
- **sample (AK):** "has qualified as a diplomate of the American Board of Nutrition or as a Certified Nutrition Specialist with the Certification Board for Nutrition Specialists"

## what they can do clinically

### `medical_nutrition_therapy_authorized` — bool
- **what:** Whether the statute explicitly authorizes the practice of 'medical nutrition therapy' as part of the dietitian's scope.
- **states:** AL, CA, CT, DE, GA
- **sample (AL):** "The practice of dietetics. The synthesis and application of dietetics, primarily for the provision of nutrition care services, including medical nutrition therapy, in person or via telehealth, to prevent, manage, or treat diseases or medical conditions and promote wellness."

### `enteral_parenteral_nutrition_authorized` — bool
- **what:** Whether the statute explicitly includes ordering or recommending enteral and/or parenteral nutrition within the dietitian's scope of practice.
- **states:** AL, AR, CA, CT, DE, GA, HI
- **sample (DE):** "Interpreting and recommending interventions to meet nutrient needs relative to individual health status, including but not limited to medically prescribed diets, tube feedings and specialized intravenous solutions."

### `diet_order_writing_authority` — bool
- **what:** Whether the statute explicitly grants dietitians authority to write or issue diet orders (including therapeutic diets) in institutional or hospital settings.
- **states:** AZ, CA, CT, DE
- **sample (CT):** "A certified dietitian-nutritionist may write an order for a patient diet, including, but not limited to, a therapeutic diet for a patient in an institution."

### `lab_test_ordering_authority` — bool
- **what:** Whether the statute explicitly grants dietitians authority to order medical laboratory tests related to nutrition therapy.
- **states:** CA, CT
- **sample (CA):** "A registered dietitian... may order medical laboratory tests related to medical nutrition therapy services when approved by the referring physician or the physician responsible for the care of the patient."

### `physician_referral_required` — bool
- **what:** Whether the statute requires a physician (or other authorized prescriber) referral or order before a dietitian may provide certain clinical nutrition services.
- **states:** AL, CA
- **sample (AL):** "a dietitian/nutritionist or registered dietitian meeting the qualifications set forth in Section 34-34-1, may, upon referral by a health care provider authorized to prescribe dietary treatments"

### `diagnosis_treatment_prohibition` — bool
- **what:** Whether the statute explicitly prohibits dietitians from diagnosing, treating, or prescribing for human illness or otherwise practicing medicine.
- **states:** AL, CA, CT
- **sample (AL):** "a person licensed to practice dietetics/nutrition or to provide nutritional care services shall not diagnose, treat, or prescribe for any human illness, injury, disease, impairment, or infirmity, or otherwise engage in the practice of medicine"

### `telehealth_practice_authorized` — bool
- **what:** Whether the statute explicitly authorizes dietitians to provide services via telehealth.
- **states:** AL
- **sample (AL):** "The practice of dietetics. The synthesis and application of dietetics, primarily for the provision of nutrition care services, including medical nutrition therapy, in person or via telehealth, to prevent, manage, or treat diseases or medical conditions and promote wellness."

### `nutrition_assessment_includes_biochemical_data` — bool
- **what:** Whether the statutory definition of nutritional assessment explicitly includes biochemical and anthropometric data as evaluation components.
- **states:** AL, AR, CT, DE, GA
- **sample (AR):** "Nutritional assessment means the evaluation of the nutritional needs of individuals and groups, based upon appropriate biochemical, anthropometric, physical, and dietary data, to determine nutrient needs and recommend appropriate nutritional intervention, including enteral and parenteral nutrition"

## supervision and delegation

### `supervision_ratio_limit` — int
- **what:** Maximum number of dietetic technicians a single registered dietitian may supervise at one time.
- **states:** CA
- **sample (CA):** "a registered dietitian shall not supervise more than two dietetic technicians, registered at one time."

### `direct_supervision_defined` — bool
- **what:** Whether the statute provides an explicit definition of 'direct supervision' for dietetic technicians or provisional licensees, including physical presence or availability requirements.
- **states:** AR, CA, GA
- **sample (CA):** "'direct supervision' means the supervising registered dietitian shall be physically available to the dietetic technician, registered for consultation whenever consultation is required."

## who is exempt from the license requirement

### `exempt_professions_list` — list[str]
- **what:** Categories of other licensed professionals explicitly exempted from the dietetics licensure requirement when performing nutrition-related activities incidental to their own profession.
- **states:** AL, AR, CA, CT, DE, GA, IA
- **sample (AR):** "A licensed physician, pharmacist, or nurse from engaging in the practice of dietetics if incidental to the practice of his or her profession, and if the person does not hold himself or herself out under the title of dietitian or licensed dietitian"

### `federal_employee_exemption` — bool
- **what:** Whether persons employed by the federal government (including armed forces, VA, or public health service) in a dietitian or nutritionist role are explicitly exempt from state licensure.
- **states:** AK, AL, AR, CT, DE, GA, HI, IA
- **sample (AR):** "A dietitian who is serving in the armed forces or the United States Public Health Service or is employed by the Department of Veterans Affairs from engaging in the practice of dietetics, provided that the practice is related to that service or employment"

### `weight_control_program_exemption` — bool
- **what:** Whether persons offering weight control programs are explicitly exempt from licensure, typically conditioned on the program being reviewed or approved by a licensed or registered dietitian.
- **states:** AL, AR, CT, DE, GA
- **sample (AR):** "A person who offers weight control programs prepared under the supervision of or approved by a registered dietitian or a licensed dietitian... if the person does not hold himself or herself out under the title of dietitian or licensed dietitian"

### `food_supplement_sales_exemption` — bool
- **what:** Whether persons who sell, market, or provide information about food, dietary supplements, vitamins, or herbs are explicitly exempt from the dietetics licensure requirement.
- **states:** AL, AR, CT, DE, GA, IA
- **sample (AL):** "Nothing in this chapter is intended to prohibit any person who does not hold himself or herself out to be a dietitian or nutritionist from furnishing general nutritional information on food, food materials, or dietary supplements or from engaging in the explanation to customers about foods or food products in connection with marketing and distribution of those products"

### `animal_nutrition_exemption` — bool
- **what:** Whether persons whose nutrition practice is limited to animals are explicitly exempt from the human dietetics licensure requirement.
- **states:** AK, AR
- **sample (AK):** "an animal nutritionist whose activities are limited to the nutritional care of animals; animal nutritionists may use the title 'nutritionist' as long as they provide nutrition services only to animals"

### `nonresident_temporary_practice_allowed` — bool
- **what:** Whether out-of-state dietitians may practice in the state for a limited period without obtaining a state license.
- **states:** AR, GA, IA
- **sample (AR):** "A nonresident dietitian practicing dietetics in this state, if: (A) The dietetics are performed for no more than one hundred eighty (180) consecutive working days"

### `nonresident_temporary_practice_max_days` — int
- **what:** Maximum number of days per year a nonresident dietitian may practice in the state without a state license.
- **states:** AR, GA
- **sample (AR):** "The dietetics are performed for no more than one hundred eighty (180) consecutive working days"

## interstate practice and portability

### `interstate_compact_member` — bool
- **what:** Whether the state has enacted the Dietitian Licensure Compact, enabling multistate practice privileges.
- **states:** AL
- **sample (AL):** "The purpose of this compact is to facilitate interstate practice of dietetics with the goal of improving public access to dietetics services."

### `compact_privilege_jurisprudence_requirement` — bool
- **what:** Whether a state may require applicants for a compact practice privilege to pass a jurisprudence (state law knowledge) assessment.
- **states:** AL
- **sample (AL):** "Meet any jurisprudence requirements established by the remote state in which the licensee is seeking a compact privilege"

## protected titles and credential abbreviations

### `protected_titles` — list[str]
- **what:** The specific titles, words, letters, or abbreviations that are legally restricted to licensed or certified practitioners under the statute.
- **states:** AK, AL, AR, CA, CT, DE, GA, HI, … (+1)
- **sample (DE):** "No person shall... use the title 'Licensed Dietitian,' 'Licensed Nutritionist,' 'Nutritionist,' 'Dietitian,' use the letters 'L.D.N.', or any combination of above terms and/or abbreviations unless such a person is licensed under this chapter."

## practice setting and facility rules

### `hospital_order_authority_requires_policy` — bool
- **what:** Whether a dietitian's authority to issue orders in a hospital setting is conditioned on the hospital having written policies and procedures authorizing such orders.
- **states:** AZ, CA
- **sample (AZ):** "A hospital... may allow a registered dietitian or other qualified nutrition professional to order diets, enteral feeding, nutritional supplementation or parenteral nutrition if... The hospital's written policies and procedures allow registered dietitians or other qualified nutrition professionals to issue such orders."

## license administration

### `inactive_license_status_available` — bool
- **what:** Whether the state allows a licensee to place their license in an inactive status for a defined period.
- **states:** DE, GA, HI
- **sample (HI):** "Upon request, the director may grant inactive status to a person licensed under this chapter."

### `ethics_code_violation_grounds_for_discipline` — bool
- **what:** Whether violation of a recognized professional code of ethics (e.g., the American Dietetic Association's code) is explicitly listed as a ground for disciplinary action.
- **states:** DE, HI
- **sample (DE):** "Has violated the Code of Ethics as established by the American Dietetic Association"
