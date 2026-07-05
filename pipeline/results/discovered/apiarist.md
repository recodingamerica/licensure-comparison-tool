# Discovered fields — apiarist

## registration and identification of hives

### `registration_required` — bool
- **what:** Whether beekeepers must register their apiaries or hives with a state authority.
- **states:** IA, KY, ND, OH, VT, WA
- **sample (OH):** "Any person owning or possessing bees shall on or before the first day of June of each year, or thereafter within thirty days after coming into ownership or possession of bees, or upon moving bees into this state from outside the state, file with the director of agriculture an application for registration setting forth the exact location of the person's apiaries."

### `apiary_identification_required` — bool
- **what:** Whether each apiary must be physically marked with an identification number or owner contact information.
- **states:** ND, OH, WA
- **sample (ND):** "A beekeeper shall identify each apiary for which the beekeeper is responsible by: affixing a three-digit identification number, assigned by the agriculture commissioner, that is prominently displayed and visible upon approach to the apiary's main entrance."

### `colony_count_reporting_required` — bool
- **what:** Whether beekeepers must report the number of colonies they maintain as part of registration or annual reporting.
- **states:** IA, ND, OH, VT, WA
- **sample (ND):** "The application must include: the maximum number of colonies to be located in or placed in this state."

### `apiary_location_reporting_required` — bool
- **what:** Whether beekeepers must report the geographic location of each apiary to the state authority.
- **states:** IA, MO, ND, OH, VT, WA
- **sample (ND):** "Before placing or locating hives in this state, a beekeeper shall notify the agriculture commissioner of the location of each apiary to the nearest section, quarter section, township, and range."

## hive construction and equipment standards

### `movable_frame_hive_required` — bool
- **what:** Whether bees must be kept in hives with removable frames to allow inspection.
- **states:** IA, MO, NH, NV, OH, VT
- **sample (NH):** "It shall be unlawful for any person, firm or corporation to keep or maintain honey bees in any hives other than modern, moveable, frame hives which permit the thorough examination of every comb in order to detect the presence of bee diseases."

### `neglected_abandoned_hive_nuisance_declared` — bool
- **what:** Whether neglected or abandoned hives or equipment are declared a public nuisance subject to seizure or destruction.
- **states:** ND, NV, OH, VT
- **sample (NV):** "Neglected or abandoned used hives or appliances containing beeswax or bee comb, unless kept in an enclosure so constructed as to prevent access by bees, are hereby declared to be public nuisances, and it shall be unlawful to maintain them."

### `honey_extraction_bee_exclusion_required` — bool
- **what:** Whether honey extraction must occur in a location inaccessible to bees.
- **states:** NV
- **sample (NV):** "Any and all extracting of honey shall be done in a place to which bees cannot gain access either during or after such extracting process."

## importing and moving bees across state lines

### `import_permit_required` — bool
- **what:** Whether a permit is required to bring bees, colonies, or used equipment into the state.
- **states:** AK, IA, MO, NH, NV, OH, VT
- **sample (MO):** "It is unlawful to move, carry, transport or ship bees, combs or used beekeeping equipment into the state of Missouri unless accompanied by a valid permit issued by the director of the department of agriculture."

### `import_certificate_of_inspection_required` — bool
- **what:** Whether imported bees or used equipment must be accompanied by a certificate of inspection from the state or country of origin.
- **states:** AK, IA, MO, NH, NV, OH, VT, WA
- **sample (NH):** "No bees, or used bee supplies or equipment, shall be shipped or moved into the state without a certificate signed by a legally authorized inspector that they are free from any infectious or contagious disease."

### `import_certificate_validity_days` — int
- **what:** Maximum age in days of a certificate of inspection that is acceptable for importing bees or equipment.
- **states:** IA, MO, NV, OH, VT
- **sample (IA):** "A valid certificate of inspection or certificate of health dated within the last sixty days must have been submitted by the state apiarist or inspector of the state of origin."

### `combless_package_import_exemption` — bool
- **what:** Whether combless packages of bees or queens are exempt from the standard import permit requirement (though still requiring a certificate of inspection).
- **states:** AK, IA, MO
- **sample (MO):** "Combless packages of bees or queens, or both, are admitted into Missouri, without a Missouri permit, when accompanied by a valid certificate of inspection from the state of origin stating they are free of diseases and pests."

## pest and invasive species controls

### `africanized_bee_regulated` — bool
- **what:** Whether Africanized honey bees are specifically identified as a regulated pest subject to control, eradication, or import prohibition.
- **states:** IA, MO, ND, NV, OH, WA
- **sample (OH):** "No person shall ship or move into this state any Africanized honey bees."

### `regulated_diseases` — list[str]
- **what:** Named bee diseases or parasites explicitly listed in statute as subject to regulation, control, or eradication.
- **states:** AK, IA, KY, MO, NH, NV, OH, VT
- **sample (MO):** "'Disease' means American or European foulbrood and any other infectious, contagious or communicable disease affecting bees or their brood."

### `varroa_mite_mitigation_plan_required` — bool
- **what:** Whether beekeepers must submit a varroa mite and pest mitigation plan as part of registration or annual reporting.
- **states:** VT
- **sample (VT):** "A current varroa mite and pest mitigation plan for each registered apiary."

### `disease_reporting_required` — bool
- **what:** Whether beekeepers must notify the state authority upon discovering a disease in their apiary.
- **states:** IA, OH, VT
- **sample (VT):** "The owner of any bees, apiary, colony, or hive registered under subsection (a) of this section shall notify the Secretary as soon as practicable of the detection within an apiary or hive of American foulbrood disease or other disease designated by the Secretary."

## government enforcement powers

### `quarantine_authority` — bool
- **what:** Whether the state authority has power to declare quarantines restricting movement of bees or equipment.
- **states:** AK, IA, KY, MO, ND, NV, OH
- **sample (KY):** "The Commissioner may establish and maintain quarantines prohibiting the shipment into or within the state, or any subdivision thereof of any bees, queen bees, used hives or any part thereof, used appliances or any material capable of transmitting any bee diseases."

### `inspector_disinfection_required_after_inspection` — bool
- **what:** Whether inspectors are legally required to disinfect themselves, clothing, and tools before leaving an infected apiary.
- **states:** NV
- **sample (NV):** "After inspecting infected hives or fixtures, or handling diseased bees, the inspector shall, before leaving the premises or proceeding to any other apiary: thoroughly disinfect any portion of his or her own person and clothing, and any tools or appliances used by him or her which have come in contact with disease-infected material."

### `inspector_police_powers` — bool
- **what:** Whether state or deputy apiarists are explicitly vested with police officer powers for enforcement.
- **states:** KY, OH
- **sample (KY):** "The state apiarist and deputy state apiarists shall be vested with the powers of police officers in the enforcement of the provisions of KRS 252.180 to 252.240."

### `right_of_entry_scope` — enum[unrestricted during reasonable hours, probable cause required, daylight hours only, warrant required for dwellings]
- **what:** The legal standard under which inspectors may enter private premises to inspect apiaries.
- **states:** IA, KY, MO, ND, NH, NV, OH, VT
- **sample (KY):** "For the purposes of KRS 252.180 to 252.240 the Commissioner or his duly authorized representatives shall have access and egress to any apiary or any premises, buildings or other place, public or private, in which he has reason to believe that bees, honey, wax, used hives or used appliances are kept; provided, however, that no occupied dwelling may be entered without a search warrant."

## queen rearing and commercial bee sales

### `queen_rearing_apiary_certification_required` — bool
- **what:** Whether apiaries that raise or sell queen bees must obtain a special certification or inspection before selling.
- **states:** KY, OH, VT
- **sample (OH):** "Each person within the state that intends to sell, trade, gift, or otherwise distribute queen bees, packaged bees, nucs, or colonies shall file with the department of agriculture a request for the certification of all of the person's queen rearing apiaries."

### `transfer_permit_required_for_diseased_equipment` — bool
- **what:** Whether a permit is required before transferring ownership of bees, honeycombs, or used equipment, particularly to confirm freedom from disease.
- **states:** IA, MO, OH, VT
- **sample (OH):** "Upon request, the state or a deputy apiarist may issue a transfer permit if, upon inspection, the item is determined to be apparently free from serious bee diseases and pests. The permit, or a copy of it, may accompany any such transfer of ownership."

### `pollination_service_colony_strength_certification` — bool
- **what:** Whether the state may certify hives used in commercial pollination services based on colony strength standards.
- **states:** ND, NV, WA
- **sample (NV):** "The Department may, if the demand for pollination service is found by the Department to warrant such action: establish standards of colony strength based upon the number of bees per hive; the number of cells containing brood per hive; the health of the bees and brood; and any other factors which reasonably relate to the ability of the colony to pollinize horticultural and agricultural crops."

## where apiaries may be located

### `apiary_minimum_distance_rule` — bool
- **what:** Whether there are rules specifying minimum distances between apiaries or from property lines.
- **states:** VT, WA
- **sample (VT):** "No person shall locate an apiary within two miles of an existing apiary registered to a different person."

### `apiary_coordinated_area_authority` — bool
- **what:** Whether local government authorities may designate coordinated apiary areas with rules on hive density, site spacing, and setbacks.
- **states:** WA
- **sample (WA):** "Within thirty days after the conclusion of any such hearing the county legislative authority shall make an order describing the apiary coordinated areas within the county as to the maximum allowable number of hives per site, the minimum allowable distance between sites, and the minimum required setback from property lines."

### `beekeeping_classified_as_agricultural_practice` — bool
- **what:** Whether beekeeping is explicitly classified by statute as an agricultural practice or pursuit.
- **states:** ND, OH, WA
- **sample (ND):** "Beekeeping is deemed to be an agricultural practice."

## honey and product quality standards

### `honey_product_labeling_standards` — bool
- **what:** Whether the state has statutory labeling requirements for honey or honey products sold or distributed.
- **states:** NH
- **sample (NH):** "Every shipment, package or container of honey packed, sold, offered or exposed for sale or distribution by any person shall be plainly marked for packaging and labeling, and shall include: the name, address and zip code of the packer, distributor, or producer; the true name of the product; the grade, or the term 'not graded'; and the volume of the contents."

### `honey_adulteration_prohibited` — bool
- **what:** Whether statute explicitly prohibits adulteration of honey with foreign sweeteners or other substances.
- **states:** NH
- **sample (NH):** "Honey which is labeled as being pure honey and which is produced, packaged, handled or sold in this state shall not in any way be adulterated with cane sugar, corn sugar, or any other foreign sweetener."

### `pesticide_spray_restriction_near_blossoms` — bool
- **what:** Whether statute restricts the use of poisonous sprays or dusts on blossoming trees or shrubs to protect bees.
- **states:** NH
- **sample (NH):** "It shall be unlawful to use any poisonous material in the form of spray or dust upon fruit trees, shade trees, or shrubs that are in blossom."

## beekeeper training and education

### `voluntary_beekeeper_education_program` — bool
- **what:** Whether the state offers or mandates a voluntary educational or training program for beekeepers.
- **states:** IA, VT
- **sample (VT):** "The Secretary, in cooperation with the Vermont Beekeepers Association, shall establish a voluntary educational program to train a person who owns bees, apiaries, colonies, or hives in the State."

### `pollinator_health_monitoring_program` — bool
- **what:** Whether the state is required to monitor managed pollinator health and establish health benchmarks.
- **states:** VT
- **sample (VT):** "The Secretary of Agriculture, Food and Markets shall monitor managed pollinator health to establish pollinator health benchmarks for Vermont, including: presence of pesticides in hives; mite pressure; disease pressure; mite control methods; genetic influence on survival; winter survival rate; and forage availability."

### `beekeeper_civil_liability_limitation` — bool
- **what:** Whether registered beekeepers who comply with applicable ordinances receive statutory protection from civil liability except for gross negligence or willful misconduct.
- **states:** WA
- **sample (WA):** "A person who owns or operates an apiary, is a registered apiarist under RCW 15.60.021, and conforms to all applicable city, town, or county ordinances regarding beekeeping, is not liable for any civil damages for acts or omissions in connection with the keeping and maintaining of bees, bee equipment, queen breeding equipment, apiaries, and appliances, unless such acts or omissions constitute gross negligence or willful misconduct."

### `minor_beekeeper_license_allowed` — bool
- **what:** Whether persons under 18 may be licensed as beekeepers, typically with parental co-signature and imputed liability.
- **states:** ND
- **sample (ND):** "An individual who is less than eighteen years of age may be licensed as a beekeeper, if that individual's application for license is signed by the individual's parent. Any civil or administrative liability for a violation of this chapter by a beekeeper who is less than eighteen years of age is imputed to the parent who signed the application."

## fees and financial obligations

### `colony_assessment_fee` — bool
- **what:** Whether beekeepers must pay a per-colony assessment fee in addition to a base license or registration fee.
- **states:** ND, WA
- **sample (ND):** "In addition to the license fee required by section 4.1-16-06, an applicant for a license must submit a colony assessment in an amount equal to fifteen cents multiplied by the maximum number of colonies listed in the application."

### `inspection_fee_charged` — bool
- **what:** Whether the state charges a fee for apiary inspections, particularly owner-requested inspections.
- **states:** MO, ND, NV, OH
- **sample (MO):** "A fee shall be charged which is sufficient to cover the cost of the inspection plus the mileage of the inspector at the rate then authorized by the commissioner of administration for reimbursement of expenses of state employees."

### `broker_registration_required` — bool
- **what:** Whether persons who broker pollination services using hives owned by others must separately register with the state.
- **states:** WA
- **sample (WA):** "Each person owning one or more hives with bees, brokers renting hives, and apiarists resident in other states who operate hives in Washington shall register with the director by April 1st each year."
