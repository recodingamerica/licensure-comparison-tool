# Discovered fields — cosmetology

## extra credentials and tiered scope

### `license_tiers` — list[str]
- **what:** The distinct license types or tiers available within the cosmetology regulatory framework, beyond the full cosmetologist license.
- **states:** PA
- **sample (PA):** "The board shall issue the following limited licenses to qualified applicants: (1) Esthetician license... (2) Nail technician license..."

### `specialty_practice_areas` — list[str]
- **what:** Distinct sub-practice areas recognized by statute that may require separate licensure or have defined scopes.
- **states:** PA
- **sample (PA):** ""Esthetics" means the practice of massaging the face, applying cosmetic preparations, antiseptics, tonics, lotions or creams to the face, removing superfluous hair by tweezers, depilatories or waxes and the dyeing of eyelashes and eyebrows."

### `natural_hair_braiding_exempt` — bool
- **what:** Whether natural hair braiding is explicitly exempted from cosmetology licensure requirements.
- **states:** PA
- **sample (PA):** "Nothing in this act shall prohibit or regulate the practice of natural hair braiding by a person who desires to engage in the practice of natural hair braiding or to operate a business dedicated to the practice of natural hair braiding if the person or business does not engage in any other practices or activities that constitute the practice of cosmetology."

### `teacher_license_required` — bool
- **what:** Whether a separate teaching license is required to instruct cosmetology students or apprentices.
- **states:** PA
- **sample (PA):** "No person shall be permitted to receive a license to teach cosmetology, nail technology or esthetics unless such person shall have a license to practice cosmetology or a limited license, be at least eighteen years of age, shall have completed a twelfth grade education or the equivalent thereof and have had five hundred hours of specialized training."

### `teacher_minimum_age` — int
- **what:** Minimum age required to obtain a cosmetology teacher license.
- **states:** PA
- **sample (PA):** "No person shall be permitted to receive a license to teach cosmetology, nail technology or esthetics unless such person shall have a license to practice cosmetology or a limited license, be at least eighteen years of age."

### `teacher_training_hours` — int
- **what:** Number of specialized training hours required to qualify for a cosmetology teacher license.
- **states:** PA
- **sample (PA):** "have had five hundred hours of specialized training as set forth in section 6 of this act which hours shall be in addition to the hours necessary to qualify for a license to practice cosmetology or a limited license."

### `temporary_license_available` — bool
- **what:** Whether a temporary license may be issued to eligible applicants while awaiting examination results.
- **states:** PA
- **sample (PA):** "Upon payment of the required fee, a temporary license may be issued to any applicant who is eligible for admission to a cosmetologist's examination or to the examination for any of the limited licenses."

### `temporary_license_duration_months` — int
- **what:** Duration in months for which a temporary cosmetology license is valid.
- **states:** PA
- **sample (PA):** "Temporary licenses are granted for a nine-month period."

### `license_escrow_available` — bool
- **what:** Whether a licensee not currently practicing may place their license in escrow to preserve renewal rights.
- **states:** PA
- **sample (PA):** "An individual holding a license to practice cosmetology or an individual holding a limited license who is not engaged in practice shall request the board, in writing, to place his license in escrow and thus protect his right to obtain a license at any such time within a five-year period."

## training pathway options

### `apprenticeship_available` — bool
- **what:** Whether an apprenticeship pathway (in lieu of school hours) is available for cosmetology licensure.
- **states:** PA
- **sample (PA):** "shall have either (i) completed not less than one thousand two hundred fifty hours as a student in a duly registered school of cosmetology... or (ii) shall have been registered and served as an apprentice at least two thousand hours in a licensed cosmetology salon."

### `apprenticeship_hours_required` — int
- **what:** Number of apprenticeship hours required as an alternative to school-based training for cosmetology licensure.
- **states:** PA
- **sample (PA):** "shall have been registered and served as an apprentice at least two thousand hours in a licensed cosmetology salon as hereinafter provided in this act."

### `early_exam_eligibility_hours` — int
- **what:** Minimum training hours after which a student may sit for the written examination before completing the full required hours.
- **states:** PA
- **sample (PA):** "An applicant wishing to obtain licensure in the practice of cosmetology may be permitted to apply to take the written examination upon completion of at least nine hundred hours of instruction in a duly licensed school of cosmetology."

### `distance_education_permitted` — bool
- **what:** Whether cosmetology schools are permitted to deliver a portion of their curriculum through distance education.
- **states:** PA
- **sample (PA):** "A school of cosmetology may provide up to fifty percent of the school's curriculum through distance education. A student at a school of cosmetology may only earn training hours under this paragraph through distance education theory-based subjects."

### `distance_education_max_percent` — int
- **what:** Maximum percentage of the cosmetology school curriculum that may be delivered through distance education.
- **states:** PA
- **sample (PA):** "A school of cosmetology may provide up to fifty percent of the school's curriculum through distance education."

### `cross_profession_credit_available` — bool
- **what:** Whether applicants holding a license in a related profession (e.g., barbering) may receive training hour credits toward cosmetology licensure.
- **states:** PA
- **sample (PA):** "If a registered barber wishes to become a licensed cosmetologist, he or she shall have successfully completed the one thousand two hundred fifty-hour barber training course or shall possess a current barber license. Upon application to the board he or she shall be given five hundred fifty-five hours of credit for subjects previously covered in the barber training course."

## applicant health and character requirements

### `health_certificate_required` — bool
- **what:** Whether applicants must submit a health certificate from a licensed physician as part of the license application.
- **states:** PA
- **sample (PA):** "such person shall file with the board a written application for license, accompanied by a health certificate issued by a licensed physician of Pennsylvania on a form which shall be prescribed and supplied by the board."

### `disease_free_required` — bool
- **what:** Whether applicants must be free from contagious or infectious disease as a condition of licensure.
- **states:** PA
- **sample (PA):** "No apprentice permit shall be issued unless the prospective apprentice applying therefor shall have established to the satisfaction of the board that he or she is of good moral character... and is free from contagious or infectious disease."

### `education_waiver_for_veterans_or_older_applicants` — bool
- **what:** Whether the minimum education requirement is waived for veterans or applicants above a certain age.
- **states:** PA
- **sample (PA):** "A person thirty-five years of age or over, or a veteran desiring to take an examination to receive a license as a cosmetologist, shall not be required to have completed a tenth grade education, or the equivalent thereof."

## practice setting and facility rules

### `salon_floor_space_minimum_sqft` — int
- **what:** Minimum floor space in square feet required for a licensed cosmetology salon.
- **states:** PA
- **sample (PA):** "The floor space of a licensed cosmetology salon operated by one licensed cosmetologist must have a minimum area of one hundred twenty square feet with a minimum width of ten feet."

### `booth_rental_prohibited` — bool
- **what:** Whether renting booth space to licensed cosmetologists within a salon is explicitly prohibited by statute.
- **states:** PA
- **sample (PA):** "The rental of booth space by an owner of a cosmetology salon, or the owner of a salon limited to esthetics or nail technology to any holder of a license issued under this act is unlawful."

### `mobile_or_home_service_permitted` — bool
- **what:** Whether licensed cosmetologists may provide services at a client's residence by appointment.
- **states:** PA
- **sample (PA):** "A licensed cosmetologist or the holder of a limited license may furnish treatments to persons in their residences by appointment."

### `shared_shop_with_barbers_permitted` — bool
- **what:** Whether licensed cosmetologists and licensed barbers may work in the same shop or salon without physical barriers.
- **states:** PA
- **sample (PA):** "A licensed barber and a licensed cosmetologist shall be permitted to work in the same shop or salon if the requirements of this section are met. Any licensed shop or salon which employs a licensed barber and a licensed cosmetologist shall not be required to erect or install any physical barriers which separate the barber and the cosmetologist."

### `massage_therapy_colocation_permitted` — bool
- **what:** Whether licensed massage therapists may practice within a licensed cosmetology or esthetician salon under specified conditions.
- **states:** PA
- **sample (PA):** "An individual licensed under the act of October 9, 2008 (P.L.1438, No.118), known as the 'Massage Therapy Law,' shall be permitted to practice massage therapy within the approved premises of a licensed cosmetology salon or a licensed esthetician salon if the following conditions are met."

### `salon_manager_designation_required` — bool
- **what:** Whether salon owners are required to designate a responsible person in charge of the salon in the owner's absence.
- **states:** PA
- **sample (PA):** "Every salon owner shall designate a person in charge of the salon in the owner's absence. The name of the owner or designated person in charge shall be posted in a conspicuous place in the salon."

## school and training program standards

### `school_student_to_teacher_ratio` — str
- **what:** Required minimum ratio of teachers to students in a licensed cosmetology school.
- **states:** PA
- **sample (PA):** "A ratio of not less than one teacher for every twenty-five students."

### `school_quarterly_reporting_required` — bool
- **what:** Whether cosmetology schools must submit quarterly reports of student hours to the licensing board.
- **states:** PA
- **sample (PA):** "Provide the board with a quarterly report regarding student hours on forms provided by the board."

### `student_clinical_services_fee_permitted` — bool
- **what:** Whether cosmetology schools are permitted to charge the public a fee for services performed by students in clinical training.
- **states:** PA
- **sample (PA):** "A school of cosmetology shall be permitted to charge the public a reasonable fee, as approved by the board, for cosmetology services performed by students in their clinical training and education."

## what they can treat and where on the body

### `tanning_equipment_regulated` — bool
- **what:** Whether the statute explicitly defines or references tanning equipment (ultraviolet light devices) within the cosmetology regulatory framework.
- **states:** PA
- **sample (PA):** ""Tanning units" means equipment that utilizes ultraviolet light for the purpose of cosmetic tanning."
