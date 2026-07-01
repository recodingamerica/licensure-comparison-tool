# Mapping migration drift — 2026-07-01

Changes that will occur when committed profession_index files are regenerated from
config/mapping_overrides.yaml + committed inputs (regeneration WITH the written
overrides vs the committed index — i.e. exactly what `git diff` will show when the
indexes are regenerated). Each entry is one node that will be ADDED or DROPPED
relative to the current committed index.

Category D ('Other drift') should be nearly empty — anything there needs review.

## A. Official→Justia URL flip

Justia-only decision (2026-07-01, chapter_url_template retired): committed nodes
carrying an official-source url flip back to their remembered justia_url on
regeneration. Paired DROP (official url) / ADD (Justia url), same chapter.

### acupuncture
- CT DROP https://www.cga.ct.gov/current/pub/chap_384c.htm — Chapter 384c - Acupuncturists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-384c/ — Chapter 384c - Acupuncturists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-634A.html — NV chapter-634a — Chapter 634A - Doctors of Oriental Medicine (LLM-mapped)
- NV ADD  https://law.justia.com/codes/nevada/chapter-634a/ — NV chapter-634a — Chapter 634A - Doctors of Oriental Medicine (LLM-mapped)
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.06&full=true — Chapter 18.06 - Acupuncture and Eastern Medicine.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-06/ — Chapter 18.06 - Acupuncture and Eastern Medicine.

### alcohol_drug_counseling
- CT DROP https://www.cga.ct.gov/current/pub/chap_376b.htm — Chapter 376b - Alcohol and Drug Counselors
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-376b/ — Chapter 376b - Alcohol and Drug Counselors

### anesthesiologist_assistant
- NV DROP https://www.leg.state.nv.us/nrs/NRS-630.html — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care
- NV ADD  https://law.justia.com/codes/nevada/chapter-630/ — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.71d&full=true — Chapter 18.71D - Anesthesiologist Assistants.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-71d/ — Chapter 18.71D - Anesthesiologist Assistants.

### applied_behavior_analysis
- CT DROP https://www.cga.ct.gov/current/pub/chap_382a.htm — Chapter 382a - Behavior Analysts
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-382a/ — Chapter 382a - Behavior Analysts
- NV DROP https://www.leg.state.nv.us/nrs/NRS-437.html — Chapter 437 - Applied Behavior Analysis
- NV ADD  https://law.justia.com/codes/nevada/chapter-437/ — Chapter 437 - Applied Behavior Analysis
- NV DROP https://www.leg.state.nv.us/nrs/NRS-641D.html — Chapter 641D - Applied Behavior Analysis
- NV ADD  https://law.justia.com/codes/nevada/chapter-641d/ — Chapter 641D - Applied Behavior Analysis
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-38 — Chapter 38 - Behavior Analysts
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-38/ — Chapter 38 - Behavior Analysts
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.380&full=true — Chapter 18.380 - Applied Behavior Analysis.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-380/ — Chapter 18.380 - Applied Behavior Analysis.

### architecture
- CT DROP https://www.cga.ct.gov/current/pub/chap_390.htm — Chapter 390 - Architects
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-390/ — Chapter 390 - Architects
- ID DROP https://legislature.idaho.gov/statutesrules/idstat/Title54/T54CH3/ — Chapter 3 - ARCHITECTS
- ID ADD  https://law.justia.com/codes/idaho/title-54/chapter-3/ — Chapter 3 - ARCHITECTS
- ME DROP https://legislature.maine.gov/statutes/32/title32ch3-asec0.html — ME chapter-3-a — Chapter 3-A: ARCHITECTS, LANDSCAPE ARCHITECTS AND INTERIOR DESIGNERS (LLM-mapped)
- ME ADD  https://law.justia.com/codes/maine/title-32/chapter-3-a/ — ME chapter-3-a — Chapter 3-A: ARCHITECTS, LANDSCAPE ARCHITECTS AND INTERIOR DESIGNERS (LLM-mapped)
- NV DROP https://www.leg.state.nv.us/nrs/NRS-623.html — Chapter 623 - Architects, Interior Designers and Residential Designers
- NV ADD  https://law.justia.com/codes/nevada/chapter-623/ — Chapter 623 - Architects, Interior Designers and Residential Designers
- RI DROP http://webserver.rilegislature.gov/Statutes/TITLE5/5-1/INDEX.HTM — Chapter 5-1 Architects
- RI ADD  https://law.justia.com/codes/rhode-island/title-5/chapter-5-1/ — Chapter 5-1 Architects
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-18A — SD Title 36 Ch 18A — Technical Professions (architecture)
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-18a/ — SD Title 36 Ch 18A — Technical Professions (architecture)
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter4/ — VA chapter-4 — Chapter 4 - Architects, Engineers, Surveyors, Landscape Architects and Interior  (LLM-mapped)
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-4/ — VA chapter-4 — Chapter 4 - Architects, Engineers, Surveyors, Landscape Architects and Interior  (LLM-mapped)
- VT DROP https://legislature.vermont.gov/statutes/chapter/26/003 — Chapter 3 - Architects
- VT ADD  https://law.justia.com/codes/vermont/title-26/chapter-3/ — Chapter 3 - Architects
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.08&full=true — Chapter 18.08 - Architects.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-08/ — Chapter 18.08 - Architects.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=39.80&full=true — Chapter 39.80 - Contracts for Architectural and Engineering Services.
- WA ADD  https://law.justia.com/codes/washington/title-39/chapter-39-80/ — Chapter 39.80 - Contracts for Architectural and Engineering Services.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=70a.515&full=true — Chapter 70A.515 - Architectural Paint Stewardship Program.
- WA ADD  https://law.justia.com/codes/washington/title-70a/chapter-70a-515/ — Chapter 70A.515 - Architectural Paint Stewardship Program.

### athlete_agent
- CT DROP https://www.cga.ct.gov/current/pub/chap_400i.htm — Chapter 400i - Uniform Athlete Agents Act
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-400i/ — Chapter 400i - Uniform Athlete Agents Act
- NV DROP https://www.leg.state.nv.us/nrs/NRS-398A.html — Chapter 398A - Revised Uniform Athlete Agents Act
- NV ADD  https://law.justia.com/codes/nevada/chapter-398a/ — Chapter 398A - Revised Uniform Athlete Agents Act
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter5-1/ — Chapter 5.1 - Athlete Agents
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-5-1/ — Chapter 5.1 - Athlete Agents
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter5-2/ — Chapter 5.2 - Athlete Agents
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-5-2/ — Chapter 5.2 - Athlete Agents
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=19.225&full=true — Chapter 19.225 - Uniform Athlete Agents Act.
- WA ADD  https://law.justia.com/codes/washington/title-19/chapter-19-225/ — Chapter 19.225 - Uniform Athlete Agents Act.

### athletic_training
- CT DROP https://www.cga.ct.gov/current/pub/chap_375a.htm — Chapter 375a - Athletic Training
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-375a/ — Chapter 375a - Athletic Training
- NV DROP https://www.leg.state.nv.us/nrs/NRS-640B.html — Chapter 640B - Athletic Trainers
- NV ADD  https://law.justia.com/codes/nevada/chapter-640b/ — Chapter 640B - Athletic Trainers
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-29 — Chapter 29 - Athletic Trainers
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-29/ — Chapter 29 - Athletic Trainers
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.250&full=true — Chapter 18.250 - Athletic Trainers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-250/ — Chapter 18.250 - Athletic Trainers.

### auctioneer
- CT DROP https://www.cga.ct.gov/current/pub/chap_403.htm — Chapter 403 - Auctioneers
- CT ADD  https://law.justia.com/codes/connecticut/title-21/chapter-403/ — Chapter 403 - Auctioneers
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter6/ — Chapter 6 - Auctioneers
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-6/ — Chapter 6 - Auctioneers
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.11&full=true — Chapter 18.11 - Auctioneers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-11/ — Chapter 18.11 - Auctioneers.

### chiropractic
- CT DROP https://www.cga.ct.gov/current/pub/chap_372.htm — Chapter 372 - Chiropractic
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-372/ — Chapter 372 - Chiropractic
- NV DROP https://www.leg.state.nv.us/nrs/NRS-634.html — Chapter 634 - Chiropractic Physicians and Chiropractic Assistants
- NV ADD  https://law.justia.com/codes/nevada/chapter-634/ — Chapter 634 - Chiropractic Physicians and Chiropractic Assistants
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-5 — Chapter 05 - Chiropractors
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-05/ — Chapter 05 - Chiropractors
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.25&full=true — Chapter 18.25 - Chiropractic.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-25/ — Chapter 18.25 - Chiropractic.

### commercial_interior_design
- CT DROP https://www.cga.ct.gov/current/pub/chap_396a.htm — Chapter 396a - Interior Designers
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-396a/ — Chapter 396a - Interior Designers
- NV DROP https://www.leg.state.nv.us/nrs/NRS-623.html — Chapter 623 - Architects, Interior Designers and Residential Designers
- NV ADD  https://law.justia.com/codes/nevada/chapter-623/ — Chapter 623 - Architects, Interior Designers and Residential Designers
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter4/ — Chapter 4 - Architects, Engineers, Surveyors, Landscape Architects and Interior Designers
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-4/ — Chapter 4 - Architects, Engineers, Surveyors, Landscape Architects and Interior Designers

### community_health_worker
- CT DROP https://www.cga.ct.gov/current/pub/chap_383h.htm — Chapter 383h - Community Health Workers
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383h/ — Chapter 383h - Community Health Workers

### construction_trades
- CT DROP https://www.cga.ct.gov/current/pub/chap_393.htm — CT chapter-393 — Chapter 393 - Electricians, Plumbers, Solar, Heating, Piping and Cooling Contrac (LLM-mapped)
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-393/ — CT chapter-393 — Chapter 393 - Electricians, Plumbers, Solar, Heating, Piping and Cooling Contrac (LLM-mapped)
- NV DROP https://www.leg.state.nv.us/nrs/NRS-624.html — NV chapter-624 — Chapter 624 - Contractors (LLM-mapped)
- NV ADD  https://law.justia.com/codes/nevada/chapter-624/ — NV chapter-624 — Chapter 624 - Contractors (LLM-mapped)
- RI DROP http://webserver.rilegislature.gov/Statutes/TITLE5/5-65/INDEX.HTM — Title 5 Chapter 5-65 - Contractors' Registration and Licensing Act
- RI ADD  https://law.justia.com/codes/rhode-island/title-5/chapter-5-65/ — Title 5 Chapter 5-65 - Contractors' Registration and Licensing Act
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter11/ — VA chapter-11 — Chapter 11 - Contractors (LLM-mapped)
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-11/ — VA chapter-11 — Chapter 11 - Contractors (LLM-mapped)
- VT DROP https://legislature.vermont.gov/statutes/chapter/26/106 — VT chapter-106 — Chapter 106 - Residential Contractors (LLM-mapped)
- VT ADD  https://law.justia.com/codes/vermont/title-26/chapter-106/ — VT chapter-106 — Chapter 106 - Residential Contractors (LLM-mapped)

### cosmetology
- CT DROP https://www.cga.ct.gov/current/pub/chap_386.htm — Chapter 386 - Barbers
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-386/ — Chapter 386 - Barbers
- CT DROP https://www.cga.ct.gov/current/pub/chap_387.htm — Chapter 387 - Hairdressers and Cosmeticians, Estheticians, Eyelash Technicians and Nail Technicians
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-387/ — Chapter 387 - Hairdressers and Cosmeticians, Estheticians, Eyelash Technicians and Nail Technicians
- NV DROP https://www.leg.state.nv.us/nrs/NRS-643.html — Chapter 643 - Barbers and Barbering
- NV ADD  https://law.justia.com/codes/nevada/chapter-643/ — Chapter 643 - Barbers and Barbering
- NV DROP https://www.leg.state.nv.us/nrs/NRS-644A.html — Chapter 644A - Cosmetology
- NV ADD  https://law.justia.com/codes/nevada/chapter-644a/ — Chapter 644A - Cosmetology
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-14 — Chapter 14 - Barbers And Barbershops
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-14/ — Chapter 14 - Barbers And Barbershops
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-15 — Chapter 15 - Cosmetologists, Estheticians, Nail Technicians, And Salons
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-15/ — Chapter 15 - Cosmetologists, Estheticians, Nail Technicians, And Salons
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter7/ — Chapter 7 - Barbers and Cosmetologists
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-7/ — Chapter 7 - Barbers and Cosmetologists
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter12/ — Chapter 12 - Cosmetologists
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-12/ — Chapter 12 - Cosmetologists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.16&full=true — Chapter 18.16 - Cosmetologists, Hair Designers, Barbers, Manicurists, and Estheticians.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-16/ — Chapter 18.16 - Cosmetologists, Hair Designers, Barbers, Manicurists, and Estheticians.

### court_reporter
- CT DROP https://www.cga.ct.gov/current/pub/chap_400-i-l-i.htm — Chapter 400l- Shorthand Reporters
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-400-i-l-i/ — Chapter 400l- Shorthand Reporters
- CT DROP https://www.cga.ct.gov/current/pub/chap_874.htm — Chapter 874 - Court Reporters
- CT ADD  https://law.justia.com/codes/connecticut/title-51/chapter-874/ — Chapter 874 - Court Reporters
- NV DROP https://www.leg.state.nv.us/nrs/NRS-656.html — Chapter 656 - Certified Court Reporters; Court Reporting Firms
- NV ADD  https://law.justia.com/codes/nevada/chapter-656/ — Chapter 656 - Certified Court Reporters; Court Reporting Firms
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.145&full=true — Chapter 18.145 - Court Reporting Practice Act.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-145/ — Chapter 18.145 - Court Reporting Practice Act.

### dentistry
- CT DROP https://www.cga.ct.gov/current/pub/chap_379.htm — Chapter 379 - Dentistry
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-379/ — Chapter 379 - Dentistry
- CT DROP https://www.cga.ct.gov/current/pub/chap_379a.htm — Chapter 379a - Dental Hygienists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-379a/ — Chapter 379a - Dental Hygienists
- ID DROP https://legislature.idaho.gov/statutesrules/idstat/Title54/T54CH9/ — Chapter 9 - DENTISTS
- ID ADD  https://law.justia.com/codes/idaho/title-54/chapter-9/ — Chapter 9 - DENTISTS
- ME DROP https://legislature.maine.gov/statutes/32/title32ch143sec0.html — Chapter 143: DENTAL PROFESSIONS
- ME ADD  https://law.justia.com/codes/maine/title-32/chapter-143/ — Chapter 143: DENTAL PROFESSIONS
- NV DROP https://www.leg.state.nv.us/nrs/NRS-631.html — Chapter 631 - Dentistry, Dental Hygiene, Dental Therapy and Expanded Function Dental Assistance
- NV ADD  https://law.justia.com/codes/nevada/chapter-631/ — Chapter 631 - Dentistry, Dental Hygiene, Dental Therapy and Expanded Function Dental Assistance
- RI DROP http://webserver.rilegislature.gov/Statutes/TITLE5/5-31/INDEX.HTM — Chapter 5-31 Dentists and Dental Hygienists [Repealed.]
- RI ADD  https://law.justia.com/codes/rhode-island/title-5/chapter-5-31/ — Chapter 5-31 Dentists and Dental Hygienists [Repealed.]
- RI DROP http://webserver.rilegislature.gov/Statutes/TITLE5/5-31-1/INDEX.HTM — Chapter 5-31.1 Dentists and Dental Hygienists
- RI ADD  https://law.justia.com/codes/rhode-island/title-5/chapter-5-31-1/ — Chapter 5-31.1 Dentists and Dental Hygienists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-6A — Chapter 06A - Dentists, Dental Hygienists And Dental Auxiliaries
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-06a/ — Chapter 06A - Dentists, Dental Hygienists And Dental Auxiliaries
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter27/ — Chapter 27 - Dentistry
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-27/ — Chapter 27 - Dentistry
- VT DROP https://legislature.vermont.gov/statutes/chapter/26/012 — Chapter 12 - Dentists, Dental Therapists, Dental Hygienists, and Dental Assistants
- VT ADD  https://law.justia.com/codes/vermont/title-26/chapter-12/ — Chapter 12 - Dentists, Dental Therapists, Dental Hygienists, and Dental Assistants
- VT DROP https://legislature.vermont.gov/statutes/chapter/26/013 — Chapter 13 - Dentists and Dental Hygienists
- VT ADD  https://law.justia.com/codes/vermont/title-26/chapter-13/ — Chapter 13 - Dentists and Dental Hygienists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.29&full=true — Chapter 18.29 - Dental Hygienists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-29/ — Chapter 18.29 - Dental Hygienists.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.32&full=true — Chapter 18.32 - Dentistry.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-32/ — Chapter 18.32 - Dentistry.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.33&full=true — Chapter 18.33 - Dentist and Dental Hygienist Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-33/ — Chapter 18.33 - Dentist and Dental Hygienist Compact.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.92&full=true — Chapter 18.92 - Veterinary Medicine, Surgery, and Dentistry.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-92/ — Chapter 18.92 - Veterinary Medicine, Surgery, and Dentistry.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.260&full=true — Chapter 18.260 - Dental Professionals.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-260/ — Chapter 18.260 - Dental Professionals.

### dietetics
- CT DROP https://www.cga.ct.gov/current/pub/chap_384b.htm — Chapter 384b - Dietitian-Nutritionists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-384b/ — Chapter 384b - Dietitian-Nutritionists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-640E.html — Chapter 640E - Dietitians
- NV ADD  https://law.justia.com/codes/nevada/chapter-640e/ — Chapter 640E - Dietitians
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-10B — Chapter 10B - Dietetics And Nutrition
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-10b/ — Chapter 10B - Dietetics And Nutrition
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter27-1/ — Chapter 27.1 - Dietitians and Nutritionists
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-27-1/ — Chapter 27.1 - Dietitians and Nutritionists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.138&full=true — Chapter 18.138 - Dietitians and Nutritionists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-138/ — Chapter 18.138 - Dietitians and Nutritionists.

### direct_entry_midwifery
- CT DROP https://www.cga.ct.gov/current/pub/chap_377.htm — CT chapter-377 — Chapter 377 - Midwifery (LLM-mapped)
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-377/ — CT chapter-377 — Chapter 377 - Midwifery (LLM-mapped)
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-9C — SD chapter-09c — Chapter 09C - Certified Professional Midwives (LLM-mapped)
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-09c/ — SD chapter-09c — Chapter 09C - Certified Professional Midwives (LLM-mapped)

### electrician
- CT DROP https://www.cga.ct.gov/current/pub/chap_393.htm — Chapter 393 - Electricians, Plumbers, Solar, Heating, Piping and Cooling Contractors and Journeymen, Elevator and Fire Protection Sprinkler Craftsmen, Irrigation Contractors and Journeymen, Gas Hearth Installer Contractors and Journeymen and Residential Stair Lift Technicians
- CT ADD  /codes/connecticut/title-20/chapter-393/section-20-334d/ — Section 20-334d. - Continuing professional education requirements for electricians and plumbers. Regulations. Exemptions.
- ID DROP https://legislature.idaho.gov/statutesrules/idstat/Title54/T54CH10/ — Chapter 10 - ELECTRICAL CONTRACTORS AND JOURNEYMEN
- ID ADD  /codes/idaho/title-54/chapter-10/section-54-1010/ — Section 54-1010 - INSTALLATIONS BY ELECTRICAL CONTRACTOR PERFORMED BY LICENSED RESIDENTIAL OR JOURNEYMAN ELECTRICIAN — PRIOR CERTIFICATE HOL
- ME DROP https://legislature.maine.gov/statutes/32/title32ch17sec0.html — Chapter 17: ELECTRICIANS
- ME ADD  https://law.justia.com/codes/maine/title-32/chapter-17/ — Chapter 17: ELECTRICIANS
- RI DROP http://webserver.rilegislature.gov/Statutes/TITLE5/5-6/INDEX.HTM — Chapter 5-6 Electricians
- RI ADD  https://law.justia.com/codes/rhode-island/title-5/chapter-5-6/ — Chapter 5-6 Electricians
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-16 — Chapter 16 - Electricians And Electrical Contractors
- SD ADD  /codes/south-dakota/title-36/chapter-16/section-36-16-23/ — Section 36-16-23 - Reciprocal licenses to electricians from other states.
- VT DROP https://legislature.vermont.gov/statutes/chapter/26/015 — Chapter 15 - Electricians and Electrical Installations
- VT ADD  https://law.justia.com/codes/vermont/title-26/chapter-15/ — Chapter 15 - Electricians and Electrical Installations
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=19.28&full=true — Chapter 19.28 - Electricians and Electrical Installations.
- WA ADD  https://law.justia.com/codes/washington/title-19/chapter-19-28/ — Chapter 19.28 - Electricians and Electrical Installations.

### electrology
- CT DROP https://www.cga.ct.gov/current/pub/chap_388.htm — Chapter 388 - Electrologists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-388/ — Chapter 388 - Electrologists

### environmental_health
- CT DROP https://www.cga.ct.gov/current/pub/chap_395.htm — Chapter 395 - Sanitarians
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-395/ — Chapter 395 - Sanitarians
- NV DROP https://www.leg.state.nv.us/nrs/NRS-625A.html — Chapter 625A - Environmental Health Specialists
- NV ADD  https://law.justia.com/codes/nevada/chapter-625a/ — Chapter 625A - Environmental Health Specialists

### funeral_services
- CT DROP https://www.cga.ct.gov/current/pub/chap_385.htm — Chapter 385 - Embalmers and Funeral Directors
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-385/ — Chapter 385 - Embalmers and Funeral Directors
- CT DROP https://www.cga.ct.gov/current/pub/chap_743c.htm — Chapter 743c - Funeral Service Contracts
- CT ADD  https://law.justia.com/codes/connecticut/title-42/chapter-743c/ — Chapter 743c - Funeral Service Contracts
- NV DROP https://www.leg.state.nv.us/nrs/NRS-642.html — Chapter 642 - Funeral Directors, Funeral Arrangers and Embalmers; Operators of Funeral Establishments, Direct Cremation Facilities, Cemeteries and Crematories
- NV ADD  https://law.justia.com/codes/nevada/chapter-642/ — Chapter 642 - Funeral Directors, Funeral Arrangers and Embalmers; Operators of Funeral Establishments, Direct Cremation Facilities, Cemeteries and Crematories
- NV DROP https://www.leg.state.nv.us/nrs/NRS-689.html — Chapter 689 - Funeral and Burial Services
- NV ADD  https://law.justia.com/codes/nevada/chapter-689/ — Chapter 689 - Funeral and Burial Services
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-19 — Chapter 19 - Funeral Directors And Establishments
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-19/ — Chapter 19 - Funeral Directors And Establishments
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter28/ — Chapter 28 - Funeral Services
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-28/ — Chapter 28 - Funeral Services
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.39&full=true — Chapter 18.39 - Embalmers—Funeral Directors.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-39/ — Chapter 18.39 - Embalmers—Funeral Directors.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=68.05&full=true — Chapter 68.05 - Funeral and Cemetery Board.
- WA ADD  https://law.justia.com/codes/washington/title-68/chapter-68-05/ — Chapter 68.05 - Funeral and Cemetery Board.

### genetic_counseling
- CT DROP https://www.cga.ct.gov/current/pub/chap_383d.htm — Chapter 383d - Genetic Counselors
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383d/ — Chapter 383d - Genetic Counselors
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-36 — Chapter 36 - Genetic Counselors
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-36/ — Chapter 36 - Genetic Counselors
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.290&full=true — Chapter 18.290 - Genetic Counselors.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-290/ — Chapter 18.290 - Genetic Counselors.

### health_facility_admin
- NV DROP https://www.leg.state.nv.us/nrs/NRS-654.html — NV chapter-654 — Chapter 654 - Administrators of Facilities for Long-Term Care (LLM-mapped)
- NV ADD  https://law.justia.com/codes/nevada/chapter-654/ — NV chapter-654 — Chapter 654 - Administrators of Facilities for Long-Term Care (LLM-mapped)
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-28 — SD chapter-28 — Chapter 28 - Nursing Facility Administrators (LLM-mapped)
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-28/ — SD chapter-28 — Chapter 28 - Nursing Facility Administrators (LLM-mapped)
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter31/ — VA chapter-31 — Chapter 31 - Nursing Home and Assisted Living Facility Administrators (LLM-mapped)
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-31/ — VA chapter-31 — Chapter 31 - Nursing Home and Assisted Living Facility Administrators (LLM-mapped)
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.52&full=true — Chapter 18.52 - Nursing Home Administrators.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-52/ — Chapter 18.52 - Nursing Home Administrators.

### hearing_instrument_specialist
- CT DROP https://www.cga.ct.gov/current/pub/chap_398.htm — Chapter 398 - Hearing Instrument Specialists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-398/ — Chapter 398 - Hearing Instrument Specialists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-637B.html — Chapter 637B - Audiologists, Speech-Language Pathologists and Hearing Aid Specialists
- NV ADD  https://law.justia.com/codes/nevada/chapter-637b/ — Chapter 637B - Audiologists, Speech-Language Pathologists and Hearing Aid Specialists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-24 — Chapter 24 - Hearing Aid Dispensers And Audiologists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-24/ — Chapter 24 - Hearing Aid Dispensers And Audiologists
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter15/ — Chapter 15 - Hearing Aid Specialists and Opticians
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-15/ — Chapter 15 - Hearing Aid Specialists and Opticians

### home_inspector
- CT DROP https://www.cga.ct.gov/current/pub/chap_400f.htm — Chapter 400f - Home Inspectors
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-400f/ — Chapter 400f - Home Inspectors
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-21C — Chapter 21C - Home Inspectors
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-21c/ — Chapter 21C - Home Inspectors
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter5/ — Chapter 5 - Asbestos, Lead, and Home Inspection Contractors and Workers
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-5/ — Chapter 5 - Asbestos, Lead, and Home Inspection Contractors and Workers
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.280&full=true — Chapter 18.280 - Home Inspectors.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-280/ — Chapter 18.280 - Home Inspectors.

### hvac
- CT DROP https://www.cga.ct.gov/current/pub/chap_393b.htm — Chapter 393b - Mechanical Contractor Organizations
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-393b/ — Chapter 393b - Mechanical Contractor Organizations
- ID DROP https://legislature.idaho.gov/statutesrules/idstat/Title54/T54CH50/ — Chapter 50 - INSTALLATION OF HEATING, VENTILATION AND AIR CONDITIONING SYSTEMS
- ID ADD  https://law.justia.com/codes/idaho/title-54/chapter-50/ — Chapter 50 - INSTALLATION OF HEATING, VENTILATION AND AIR CONDITIONING SYSTEMS
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.27&full=true — WA Ch 18.27 — Registration of Contractors (HVAC via contractor registration)
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-27/ — WA Ch 18.27 — Registration of Contractors (HVAC via contractor registration)

### insurance_producer
- CT DROP https://www.cga.ct.gov/current/pub/chap_701a.htm — Chapter 701a - Insurance Producers, Agents and Third-Party Administrators
- CT ADD  https://law.justia.com/codes/connecticut/title-38a/chapter-701a/ — Chapter 701a - Insurance Producers, Agents and Third-Party Administrators
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=48.17&full=true — Chapter 48.17 - Insurance Producers, Title Insurance Agents, and Adjusters.
- WA ADD  https://law.justia.com/codes/washington/title-48/chapter-48-17/ — Chapter 48.17 - Insurance Producers, Title Insurance Agents, and Adjusters.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=48.170&full=true — Chapter 48.170 - Self-Service Storage Insurance Producers.
- WA ADD  https://law.justia.com/codes/washington/title-48/chapter-48-170/ — Chapter 48.170 - Self-Service Storage Insurance Producers.

### junk_dealer
- CT DROP https://www.cga.ct.gov/current/pub/chap_405.htm — Chapter 405 - Junk Dealers
- CT ADD  https://law.justia.com/codes/connecticut/title-21/chapter-405/ — Chapter 405 - Junk Dealers
- CT DROP https://www.cga.ct.gov/current/pub/chap_406.htm — Chapter 406 - Motor Vehicle Junk Yards (See Chapter 246)
- CT ADD  https://law.justia.com/codes/connecticut/title-21/chapter-406/ — Chapter 406 - Motor Vehicle Junk Yards (See Chapter 246)
- CT DROP https://www.cga.ct.gov/current/pub/chap_409.htm — Chapter 409 - Pawnbrokers and Secondhand Dealers
- CT ADD  https://law.justia.com/codes/connecticut/title-21/chapter-409/ — Chapter 409 - Pawnbrokers and Secondhand Dealers
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=19.60&full=true — Chapter 19.60 - Pawnbrokers and Secondhand Dealers.
- WA ADD  https://law.justia.com/codes/washington/title-19/chapter-19-60/ — Chapter 19.60 - Pawnbrokers and Secondhand Dealers.

### land_surveying
- CT DROP https://www.cga.ct.gov/current/pub/chap_391.htm — Chapter 391 - Professional Engineers and Land Surveyors
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-391/ — Chapter 391 - Professional Engineers and Land Surveyors
- NV DROP https://www.leg.state.nv.us/nrs/NRS-625.html — Chapter 625 - Professional Engineers and Land Surveyors
- NV ADD  https://law.justia.com/codes/nevada/chapter-625/ — Chapter 625 - Professional Engineers and Land Surveyors
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.43&full=true — Chapter 18.43 - Engineers and Land Surveyors.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-43/ — Chapter 18.43 - Engineers and Land Surveyors.

### landscape_architecture
- CT DROP https://www.cga.ct.gov/current/pub/chap_396.htm — Chapter 396 - Landscape Architects
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-396/ — Chapter 396 - Landscape Architects
- NV DROP https://www.leg.state.nv.us/nrs/NRS-623A.html — Chapter 623A - Landscape Architects
- NV ADD  https://law.justia.com/codes/nevada/chapter-623a/ — Chapter 623A - Landscape Architects
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter4/ — Chapter 4 - Architects, Engineers, Surveyors, Landscape Architects and Interior Designers
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-4/ — Chapter 4 - Architects, Engineers, Surveyors, Landscape Architects and Interior Designers
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.96&full=true — Chapter 18.96 - Landscape Architects.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-96/ — Chapter 18.96 - Landscape Architects.

### livestock_dealer
- CT DROP https://www.cga.ct.gov/current/pub/chap_437.htm — Chapter 437 - Livestock Dealers
- CT ADD  https://law.justia.com/codes/connecticut/title-22/chapter-437/ — Chapter 437 - Livestock Dealers

### massage_therapy
- CT DROP https://www.cga.ct.gov/current/pub/chap_384a.htm — Chapter 384a - Massage Therapists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-384a/ — Chapter 384a - Massage Therapists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-640C.html — Chapter 640C - Massage Therapy
- NV ADD  https://law.justia.com/codes/nevada/chapter-640c/ — Chapter 640C - Massage Therapy
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-35 — Chapter 35 - Massage Therapists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-35/ — Chapter 35 - Massage Therapists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.108&full=true — Chapter 18.108 - Massage Therapists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-108/ — Chapter 18.108 - Massage Therapists.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.240&full=true — Chapter 18.240 - Animal Massage Therapists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-240/ — Chapter 18.240 - Animal Massage Therapists.

### medicine
- CT DROP https://www.cga.ct.gov/current/pub/chap_369.htm — Chapter 369 - Healing Arts
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-369/ — Chapter 369 - Healing Arts
- CT DROP https://www.cga.ct.gov/current/pub/chap_370.htm — Chapter 370 - Medicine and Surgery
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-370/ — Chapter 370 - Medicine and Surgery
- NV DROP https://www.leg.state.nv.us/nrs/NRS-629.html — Chapter 629 - Healing Arts Generally
- NV ADD  https://law.justia.com/codes/nevada/chapter-629/ — Chapter 629 - Healing Arts Generally
- NV DROP https://www.leg.state.nv.us/nrs/NRS-629A.html — Chapter 629A - Interstate Medical Licensure Compact
- NV ADD  https://law.justia.com/codes/nevada/chapter-629a/ — Chapter 629A - Interstate Medical Licensure Compact
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-2 — Chapter 02 - Practitioners Of Healing Arts In General
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-02/ — Chapter 02 - Practitioners Of Healing Arts In General
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-4 — Chapter 04 - Physicians And Surgeons
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-04/ — Chapter 04 - Physicians And Surgeons
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter29/ — Chapter 29 - Medicine and Other Healing Arts
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-29/ — Chapter 29 - Medicine and Other Healing Arts
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.71&full=true — Chapter 18.71 - Physicians.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-71/ — Chapter 18.71 - Physicians.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.71b&full=true — Chapter 18.71B - Interstate Medical Licensure Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-71b/ — Chapter 18.71B - Interstate Medical Licensure Compact.

### mental_health_counseling
- CT DROP https://www.cga.ct.gov/current/pub/chap_383b.htm — Chapter 383b - Clinical Social Workers and Master Social Workers
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383b/ — Chapter 383b - Clinical Social Workers and Master Social Workers
- CT DROP https://www.cga.ct.gov/current/pub/chap_383c.htm — Chapter 383c - Professional Counselors
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383c/ — Chapter 383c - Professional Counselors
- NV DROP https://www.leg.state.nv.us/nrs/NRS-433A.html — Chapter 433A - Admission to Mental Health Facilities or Assisted Outpatient Treatment; Hospitalization
- NV ADD  https://law.justia.com/codes/nevada/chapter-433a/ — Chapter 433A - Admission to Mental Health Facilities or Assisted Outpatient Treatment; Hospitalization
- NV DROP https://www.leg.state.nv.us/nrs/NRS-433C.html — Chapter 433C - Community Mental Health Programs
- NV ADD  https://law.justia.com/codes/nevada/chapter-433c/ — Chapter 433C - Community Mental Health Programs
- NV DROP https://www.leg.state.nv.us/nrs/NRS-641A.html — Chapter 641A - Marriage and Family Therapists and Clinical Professional Counselors
- NV ADD  https://law.justia.com/codes/nevada/chapter-641a/ — Chapter 641A - Marriage and Family Therapists and Clinical Professional Counselors
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-32 — Chapter 32 - Professional Counselors
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-32/ — Chapter 32 - Professional Counselors
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-33 — Chapter 33 - Marriage And Family Therapists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-33/ — Chapter 33 - Marriage And Family Therapists
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter35/ — Chapter 35 - Professional Counseling
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-35/ — Chapter 35 - Professional Counseling
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.17&full=true — Chapter 18.17 - Interstate Counseling Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-17/ — Chapter 18.17 - Interstate Counseling Compact.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.225&full=true — Chapter 18.225 - Mental Health Counselors, Marriage and Family Therapists, Social Workers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-225/ — Chapter 18.225 - Mental Health Counselors, Marriage and Family Therapists, Social Workers.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=48.66&full=true — Chapter 48.66 - Medicare Supplemental Health Insurance Act.
- WA ADD  https://law.justia.com/codes/washington/title-48/chapter-48-66/ — Chapter 48.66 - Medicare Supplemental Health Insurance Act.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=71.32&full=true — Chapter 71.32 - Mental Health Advance Directives.
- WA ADD  https://law.justia.com/codes/washington/title-71/chapter-71-32/ — Chapter 71.32 - Mental Health Advance Directives.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=71.36&full=true — Chapter 71.36 - Coordination of Children's Mental Health Services.
- WA ADD  https://law.justia.com/codes/washington/title-71/chapter-71-36/ — Chapter 71.36 - Coordination of Children's Mental Health Services.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=72.06&full=true — Chapter 72.06 - Mental Health.
- WA ADD  https://law.justia.com/codes/washington/title-72/chapter-72-06/ — Chapter 72.06 - Mental Health.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=72.27&full=true — Chapter 72.27 - Interstate Compact on Mental Health.
- WA ADD  https://law.justia.com/codes/washington/title-72/chapter-72-27/ — Chapter 72.27 - Interstate Compact on Mental Health.

### money_transmitter
- NV DROP https://www.leg.state.nv.us/nrs/NRS-671.html — Chapter 671 - Money Transmission
- NV ADD  https://law.justia.com/codes/nevada/chapter-671/ — Chapter 671 - Money Transmission
- VA DROP https://law.lis.virginia.gov/vacodefull/title6.2/chapter19-1/ — Chapter 19.1 - Money Transmitters
- VA ADD  https://law.justia.com/codes/virginia/title-6-2/chapter-19-1/ — Chapter 19.1 - Money Transmitters

### music_therapy
- CT DROP https://www.cga.ct.gov/current/pub/chap_383f.htm — Chapter 383f - Music Therapists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383f/ — Chapter 383f - Music Therapists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-640D.html — Chapter 640D - Music Therapists
- NV ADD  https://law.justia.com/codes/nevada/chapter-640d/ — Chapter 640D - Music Therapists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.233&full=true — Chapter 18.233 - Music Therapists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-233/ — Chapter 18.233 - Music Therapists.

### naturopathic_medicine
- CT DROP https://www.cga.ct.gov/current/pub/chap_373.htm — Chapter 373 - Naturopathy
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-373/ — Chapter 373 - Naturopathy
- NV DROP https://www.leg.state.nv.us/nrs/NRS-630A.html — NV chapter-630a — Chapter 630A - Homeopathic Physicians, Advanced Practitioners of Homeopathy and  (LLM-mapped)
- NV ADD  https://law.justia.com/codes/nevada/chapter-630a/ — NV chapter-630a — Chapter 630A - Homeopathic Physicians, Advanced Practitioners of Homeopathy and  (LLM-mapped)
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.36a&full=true — Chapter 18.36A - Naturopathy.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-36a/ — Chapter 18.36A - Naturopathy.

### nurse_midwifery
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-9A — SD chapter-09a — Chapter 09A - Certified Nurse Practitioners And Certified Nurse Midwives (LLM-mapped)
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-09a/ — SD chapter-09a — Chapter 09A - Certified Nurse Practitioners And Certified Nurse Midwives (LLM-mapped)

### nursing
- CT DROP https://www.cga.ct.gov/current/pub/chap_378.htm — Chapter 378 - Nursing
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-378/ — Chapter 378 - Nursing
- CT DROP https://www.cga.ct.gov/current/pub/chap_378a.htm — Chapter 378a - Nurse's Aides
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-378a/ — Chapter 378a - Nurse's Aides
- NV DROP https://www.leg.state.nv.us/nrs/NRS-632.html — Chapter 632 - Nursing
- NV ADD  https://law.justia.com/codes/nevada/chapter-632/ — Chapter 632 - Nursing
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-9 — Chapter 09 - Registered And Practical Nurses
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-09/ — Chapter 09 - Registered And Practical Nurses
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-9A — Chapter 09A - Certified Nurse Practitioners And Certified Nurse Midwives
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-09a/ — Chapter 09A - Certified Nurse Practitioners And Certified Nurse Midwives
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-9D — Chapter 09D - Advanced Practice Registered Nurse Compact
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-09d/ — Chapter 09D - Advanced Practice Registered Nurse Compact
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/34-12I — Chapter 12I - Video Or Audio Monitoring In Assisted Living Centers And Nursing Facilities
- SD ADD  https://law.justia.com/codes/south-dakota/title-34/chapter-12i/ — Chapter 12I - Video Or Audio Monitoring In Assisted Living Centers And Nursing Facilities
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/47-11E — Chapter 11E - Nursing Corporations
- SD ADD  https://law.justia.com/codes/south-dakota/title-47/chapter-11e/ — Chapter 11E - Nursing Corporations
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter30/ — Chapter 30 - Nursing
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-30/ — Chapter 30 - Nursing
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.52c&full=true — Chapter 18.52C - Nursing Pools.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-52c/ — Chapter 18.52C - Nursing Pools.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.79&full=true — Chapter 18.79 - Nursing Care.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-79/ — Chapter 18.79 - Nursing Care.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.80&full=true — Chapter 18.80 - Interstate Nurse Licensure Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-80/ — Chapter 18.80 - Interstate Nurse Licensure Compact.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.88a&full=true — Chapter 18.88A - Nursing Assistants.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-88a/ — Chapter 18.88A - Nursing Assistants.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=5.62&full=true — Chapter 5.62 - Witnesses—Registered Nurses.
- WA ADD  https://law.justia.com/codes/washington/title-5/chapter-5-62/ — Chapter 5.62 - Witnesses—Registered Nurses.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=60.44&full=true — Chapter 60.44 - Lien of Doctors, Nurses, Hospitals, Ambulance Services.
- WA ADD  https://law.justia.com/codes/washington/title-60/chapter-60-44/ — Chapter 60.44 - Lien of Doctors, Nurses, Hospitals, Ambulance Services.

### occupational_therapy
- CT DROP https://www.cga.ct.gov/current/pub/chap_376a.htm — Chapter 376a - Occupational Therapists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-376a/ — Chapter 376a - Occupational Therapists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-640A.html — Chapter 640A - Occupational Therapists and Occupational Therapy Assistants
- NV ADD  https://law.justia.com/codes/nevada/chapter-640a/ — Chapter 640A - Occupational Therapists and Occupational Therapy Assistants
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-31 — Chapter 31 - Occupational Therapists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-31/ — Chapter 31 - Occupational Therapists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-31A — Chapter 31A - Interstate Compact On Occupational Therapy Licensure
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-31a/ — Chapter 31A - Interstate Compact On Occupational Therapy Licensure
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/47-11G — Chapter 11G - Physical Therapy, Occupational Therapy, And Speech-Language Pathology Corporations
- SD ADD  https://law.justia.com/codes/south-dakota/title-47/chapter-11g/ — Chapter 11G - Physical Therapy, Occupational Therapy, And Speech-Language Pathology Corporations
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.59&full=true — Chapter 18.59 - Occupational Therapy.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-59/ — Chapter 18.59 - Occupational Therapy.

### opticianry
- CT DROP https://www.cga.ct.gov/current/pub/chap_381.htm — CT chapter-381 — Chapter 381 - Opticians (LLM-mapped)
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-381/ — CT chapter-381 — Chapter 381 - Opticians (LLM-mapped)
- NV DROP https://www.leg.state.nv.us/nrs/NRS-637.html — Chapter 637 - Dispensing Opticians
- NV ADD  https://law.justia.com/codes/nevada/chapter-637/ — Chapter 637 - Dispensing Opticians
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter17/ — VA chapter-17 — Chapter 17 - Opticians (LLM-mapped)
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-17/ — VA chapter-17 — Chapter 17 - Opticians (LLM-mapped)
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.34&full=true — Chapter 18.34 - Dispensing Opticians.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-34/ — Chapter 18.34 - Dispensing Opticians.

### optometry
- CT DROP https://www.cga.ct.gov/current/pub/chap_380.htm — Chapter 380 - Optometry
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-380/ — Chapter 380 - Optometry
- NV DROP https://www.leg.state.nv.us/nrs/NRS-636.html — Chapter 636 - Optometry
- NV ADD  https://law.justia.com/codes/nevada/chapter-636/ — Chapter 636 - Optometry
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-7 — Chapter 07 - Optometrists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-07/ — Chapter 07 - Optometrists
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter32/ — Chapter 32 - Optometry
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-32/ — Chapter 32 - Optometry
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.53&full=true — Chapter 18.53 - Optometry.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-53/ — Chapter 18.53 - Optometry.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.54&full=true — Chapter 18.54 - Optometry Board.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-54/ — Chapter 18.54 - Optometry Board.

### osteopathic_medicine
- NV DROP https://www.leg.state.nv.us/nrs/NRS-633.html — Chapter 633 - Osteopathic Medicine
- NV ADD  https://law.justia.com/codes/nevada/chapter-633/ — Chapter 633 - Osteopathic Medicine
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.57&full=true — Chapter 18.57 - Osteopathy—Osteopathic Medicine and Surgery.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-57/ — Chapter 18.57 - Osteopathy—Osteopathic Medicine and Surgery.

### pawnbroker
- CT DROP https://www.cga.ct.gov/current/pub/chap_409.htm — Chapter 409 - Pawnbrokers and Secondhand Dealers
- CT ADD  https://law.justia.com/codes/connecticut/title-21/chapter-409/ — Chapter 409 - Pawnbrokers and Secondhand Dealers
- NV DROP https://www.leg.state.nv.us/nrs/NRS-646.html — Chapter 646 - Pawnbrokers
- NV ADD  https://law.justia.com/codes/nevada/chapter-646/ — Chapter 646 - Pawnbrokers
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter40/ — Chapter 40 - Pawnbrokers
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-40/ — Chapter 40 - Pawnbrokers
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=19.60&full=true — Chapter 19.60 - Pawnbrokers and Secondhand Dealers.
- WA ADD  https://law.justia.com/codes/washington/title-19/chapter-19-60/ — Chapter 19.60 - Pawnbrokers and Secondhand Dealers.

### perfusionist
- CT DROP https://www.cga.ct.gov/current/pub/chap_381b.htm — Chapter 381b - Perfusionists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-381b/ — Chapter 381b - Perfusionists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-630.html — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care
- NV ADD  https://law.justia.com/codes/nevada/chapter-630/ — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care

### pharmacy
- CT DROP https://www.cga.ct.gov/current/pub/chap_382.htm — Chapter 382 - Pharmacy (See Chapter 400j)
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-382/ — Chapter 382 - Pharmacy (See Chapter 400j)
- CT DROP https://www.cga.ct.gov/current/pub/chap_400j.htm — Chapter 400j - Pharmacy
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-400j/ — Chapter 400j - Pharmacy
- CT DROP https://www.cga.ct.gov/current/pub/chap_319e.htm — Chapter 319e - Connecticut Pharmaceutical Assistance Contract to the Elderly and the Disabled Program (See Chapter 319ff)
- CT ADD  https://law.justia.com/codes/connecticut/title-17a/chapter-319e/ — Chapter 319e - Connecticut Pharmaceutical Assistance Contract to the Elderly and the Disabled Program (See Chapter 319ff)
- CT DROP https://www.cga.ct.gov/current/pub/chap_518c.htm — Chapter 518c - Pharmaceutical Preparedness
- CT ADD  https://law.justia.com/codes/connecticut/title-28/chapter-518c/ — Chapter 518c - Pharmaceutical Preparedness
- NV DROP https://www.leg.state.nv.us/nrs/NRS-577.html — Chapter 577 - Animal Remedies, Veterinary Biologics and Pharmaceuticals
- NV ADD  https://law.justia.com/codes/nevada/chapter-577/ — Chapter 577 - Animal Remedies, Veterinary Biologics and Pharmaceuticals
- NV DROP https://www.leg.state.nv.us/nrs/NRS-639.html — Chapter 639 - Pharmacists and Pharmacy
- NV ADD  https://law.justia.com/codes/nevada/chapter-639/ — Chapter 639 - Pharmacists and Pharmacy
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-11 — Chapter 11 - Pharmacies And Pharmacists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-11/ — Chapter 11 - Pharmacies And Pharmacists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/58-29E — Chapter 29E - Pharmacy Benefits Management
- SD ADD  https://law.justia.com/codes/south-dakota/title-58/chapter-29e/ — Chapter 29E - Pharmacy Benefits Management
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/58-29F — Chapter 29F - Pharmacy Audit Integrity Program
- SD ADD  https://law.justia.com/codes/south-dakota/title-58/chapter-29f/ — Chapter 29F - Pharmacy Audit Integrity Program
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter33/ — Chapter 33 - Pharmacy
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-33/ — Chapter 33 - Pharmacy
- VA DROP https://law.lis.virginia.gov/vacodefull/title59.1/chapter22-16/ — Chapter 22.16 - Pharmaceutical Manufacturing Grant Program
- VA ADD  https://law.justia.com/codes/virginia/title-59-1/chapter-22-16/ — Chapter 22.16 - Pharmaceutical Manufacturing Grant Program
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.64&full=true — Chapter 18.64 - Pharmacists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-64/ — Chapter 18.64 - Pharmacists.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.64a&full=true — Chapter 18.64A - Pharmacy Assistants.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-64a/ — Chapter 18.64A - Pharmacy Assistants.

### physical_therapy
- CT DROP https://www.cga.ct.gov/current/pub/chap_376.htm — Chapter 376 - Physical Therapists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-376/ — Chapter 376 - Physical Therapists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-640.html — Chapter 640 - Physical Therapists, Physical Therapist Assistants and Physical Therapist Technicians
- NV ADD  https://law.justia.com/codes/nevada/chapter-640/ — Chapter 640 - Physical Therapists, Physical Therapist Assistants and Physical Therapist Technicians
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-10 — Chapter 10 - Physical Therapists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-10/ — Chapter 10 - Physical Therapists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/47-11G — Chapter 11G - Physical Therapy, Occupational Therapy, And Speech-Language Pathology Corporations
- SD ADD  https://law.justia.com/codes/south-dakota/title-47/chapter-11g/ — Chapter 11G - Physical Therapy, Occupational Therapy, And Speech-Language Pathology Corporations
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter34-1/ — Chapter 34.1 - Physical Therapy
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-34-1/ — Chapter 34.1 - Physical Therapy
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.74&full=true — Chapter 18.74 - Physical Therapy.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-74/ — Chapter 18.74 - Physical Therapy.

### physician_assistant
- NV DROP https://www.leg.state.nv.us/nrs/NRS-630.html — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care
- NV ADD  https://law.justia.com/codes/nevada/chapter-630/ — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-4A — Chapter 04A - Physician Assistants
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-04a/ — Chapter 04A - Physician Assistants
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/47-11D — Chapter 11D - Physician's Assistants Corporations
- SD ADD  https://law.justia.com/codes/south-dakota/title-47/chapter-11d/ — Chapter 11D - Physician's Assistants Corporations
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.71a&full=true — Chapter 18.71A - Physician Assistants.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-71a/ — Chapter 18.71A - Physician Assistants.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.71c&full=true — Chapter 18.71C - Physician Assistant Licensure Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-71c/ — Chapter 18.71C - Physician Assistant Licensure Compact.

### plumbing
- CT DROP https://www.cga.ct.gov/current/pub/chap_393.htm — Chapter 393 - Electricians, Plumbers, Solar, Heating, Piping and Cooling Contractors and Journeymen, Elevator and Fire Protection Sprinkler Craftsmen, Irrigation Contractors and Journeymen, Gas Hearth Installer Contractors and Journeymen and Residential Stair Lift Technicians
- CT ADD  /codes/connecticut/title-20/chapter-393/section-20-334d/ — Section 20-334d. - Continuing professional education requirements for electricians and plumbers. Regulations. Exemptions.
- ID DROP https://legislature.idaho.gov/statutesrules/idstat/Title54/T54CH26/ — Chapter 26 - PLUMBING AND PLUMBERS
- ID ADD  https://law.justia.com/codes/idaho/title-54/chapter-26/ — Chapter 26 - PLUMBING AND PLUMBERS
- ME DROP https://legislature.maine.gov/statutes/32/title32ch49sec0.html — Chapter 49: PLUMBERS
- ME ADD  https://law.justia.com/codes/maine/title-32/chapter-49/ — Chapter 49: PLUMBERS
- RI DROP http://webserver.rilegislature.gov/Statutes/TITLE5/5-20/INDEX.HTM — Chapter 5-20 Plumbers, Irrigators, and Water System Installers
- RI ADD  https://law.justia.com/codes/rhode-island/title-5/chapter-5-20/ — Chapter 5-20 Plumbers, Irrigators, and Water System Installers
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-25 — Chapter 25 - Plumbers
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-25/ — Chapter 25 - Plumbers
- VT DROP https://legislature.vermont.gov/statutes/chapter/26/039 — Chapter 39 - Plumbers and Plumbing
- VT ADD  https://law.justia.com/codes/vermont/title-26/chapter-39/ — Chapter 39 - Plumbers and Plumbing
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.106&full=true — Chapter 18.106 - Plumbers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-106/ — Chapter 18.106 - Plumbers.

### podiatry
- CT DROP https://www.cga.ct.gov/current/pub/chap_375.htm — Chapter 375 - Podiatry
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-375/ — Chapter 375 - Podiatry
- NV DROP https://www.leg.state.nv.us/nrs/NRS-635.html — Chapter 635 - Podiatric Physicians and Podiatry Hygienists
- NV ADD  https://law.justia.com/codes/nevada/chapter-635/ — Chapter 635 - Podiatric Physicians and Podiatry Hygienists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-8 — Chapter 08 - Podiatrists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-08/ — Chapter 08 - Podiatrists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.22&full=true — Chapter 18.22 - Podiatric Medicine and Surgery.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-22/ — Chapter 18.22 - Podiatric Medicine and Surgery.

### polygraph_examiner
- NV DROP https://www.leg.state.nv.us/nrs/NRS-648.html — Chapter 648 - Private Investigators, Private Patrol Officers, Polygraphic Examiners, Process Servers, Repossessors, Dog Handlers and Registered Employees
- NV ADD  https://law.justia.com/codes/nevada/chapter-648/ — Chapter 648 - Private Investigators, Private Patrol Officers, Polygraphic Examiners, Process Servers, Repossessors, Dog Handlers and Registered Employees
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-30 — Chapter 30 - Polygraph Examiners
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-30/ — Chapter 30 - Polygraph Examiners
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter18/ — Chapter 18 - Polygraph Examiners
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-18/ — Chapter 18 - Polygraph Examiners

### private_investigator
- CT DROP https://www.cga.ct.gov/current/pub/chap_534.htm — Chapter 534 - Private Detectives and Security Services
- CT ADD  https://law.justia.com/codes/connecticut/title-29/chapter-534/ — Chapter 534 - Private Detectives and Security Services
- NV DROP https://www.leg.state.nv.us/nrs/NRS-648.html — Chapter 648 - Private Investigators, Private Patrol Officers, Polygraphic Examiners, Process Servers, Repossessors, Dog Handlers and Registered Employees
- NV ADD  https://law.justia.com/codes/nevada/chapter-648/ — Chapter 648 - Private Investigators, Private Patrol Officers, Polygraphic Examiners, Process Servers, Repossessors, Dog Handlers and Registered Employees
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.165&full=true — Chapter 18.165 - Private Investigators.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-165/ — Chapter 18.165 - Private Investigators.

### process_server
- NV DROP https://www.leg.state.nv.us/nrs/NRS-648.html — Chapter 648 - Private Investigators, Private Patrol Officers, Polygraphic Examiners, Process Servers, Repossessors, Dog Handlers and Registered Employees
- NV ADD  https://law.justia.com/codes/nevada/chapter-648/ — Chapter 648 - Private Investigators, Private Patrol Officers, Polygraphic Examiners, Process Servers, Repossessors, Dog Handlers and Registered Employees
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.180&full=true — Chapter 18.180 - Process Servers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-180/ — Chapter 18.180 - Process Servers.

### professional_engineering
- CT DROP https://www.cga.ct.gov/current/pub/chap_391.htm — Chapter 391 - Professional Engineers and Land Surveyors
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-391/ — Chapter 391 - Professional Engineers and Land Surveyors
- NV DROP https://www.leg.state.nv.us/nrs/NRS-625.html — Chapter 625 - Professional Engineers and Land Surveyors
- NV ADD  https://law.justia.com/codes/nevada/chapter-625/ — Chapter 625 - Professional Engineers and Land Surveyors
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-18A — SD chapter-18a — Chapter 18A - Technical Professions (LLM-mapped)
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-18a/ — SD chapter-18a — Chapter 18A - Technical Professions (LLM-mapped)
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.43&full=true — Chapter 18.43 - Engineers and Land Surveyors.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-43/ — Chapter 18.43 - Engineers and Land Surveyors.

### professional_geology
- CT DROP https://www.cga.ct.gov/current/pub/chap_462.htm — Chapter 462 - State Geological and Natural History Survey
- CT ADD  https://law.justia.com/codes/connecticut/title-24/chapter-462/ — Chapter 462 - State Geological and Natural History Survey
- NV DROP https://www.leg.state.nv.us/nrs/NRS-514.html — Chapter 514 - Bureau of Mines and Geology
- NV ADD  https://law.justia.com/codes/nevada/chapter-514/ — Chapter 514 - Bureau of Mines and Geology
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter14/ — Chapter 14 - Geologists
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-14/ — Chapter 14 - Geologists
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter22/ — Chapter 22 - Soil Scientists, Wetland Professionals, and Geologists
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-22/ — Chapter 22 - Soil Scientists, Wetland Professionals, and Geologists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.220&full=true — Chapter 18.220 - Geologists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-220/ — Chapter 18.220 - Geologists.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=43.92&full=true — Chapter 43.92 - Geological Survey.
- WA ADD  https://law.justia.com/codes/washington/title-43/chapter-43-92/ — Chapter 43.92 - Geological Survey.

### psychology
- CT DROP https://www.cga.ct.gov/current/pub/chap_383.htm — Chapter 383 - Psychologists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383/ — Chapter 383 - Psychologists
- CT DROP https://www.cga.ct.gov/current/pub/chap_383e.htm — Chapter 383e - Psychology Technicians
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383e/ — Chapter 383e - Psychology Technicians
- NV DROP https://www.leg.state.nv.us/nrs/NRS-641.html — Chapter 641 - Psychologists
- NV ADD  https://law.justia.com/codes/nevada/chapter-641/ — Chapter 641 - Psychologists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-27A — Chapter 27A - Psychologists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-27a/ — Chapter 27A - Psychologists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-27B — Chapter 27B - Psychology Interjurisdictional Compact
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-27b/ — Chapter 27B - Psychology Interjurisdictional Compact
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter36/ — Chapter 36 - Psychology
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-36/ — Chapter 36 - Psychology
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.83&full=true — Chapter 18.83 - Psychologists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-83/ — Chapter 18.83 - Psychologists.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.83a&full=true — Chapter 18.83A - Psychology Interjurisdictional Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-83a/ — Chapter 18.83A - Psychology Interjurisdictional Compact.

### public_accountancy
- CT DROP https://www.cga.ct.gov/current/pub/chap_389.htm — Chapter 389 - Public Accountants
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-389/ — Chapter 389 - Public Accountants
- NV DROP https://www.leg.state.nv.us/nrs/NRS-628.html — Chapter 628 - Accountants
- NV ADD  https://law.justia.com/codes/nevada/chapter-628/ — Chapter 628 - Accountants
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-20B — Chapter 20B - Public Accountants
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-20b/ — Chapter 20B - Public Accountants
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/47-13B — Chapter 13B - Professional Corporations For The Practice Of Public Accounting
- SD ADD  https://law.justia.com/codes/south-dakota/title-47/chapter-13b/ — Chapter 13B - Professional Corporations For The Practice Of Public Accounting
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter20/ — Chapter 20 - Public Accountancy
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-20/ — Chapter 20 - Public Accountancy
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter44/ — Chapter 44 - Public Accountants
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-44/ — Chapter 44 - Public Accountants
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.04&full=true — Chapter 18.04 - Accountancy.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-04/ — Chapter 18.04 - Accountancy.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=28b.123&full=true — Chapter 28B.123 - Certified Public Accounting Scholarship Program.
- WA ADD  https://law.justia.com/codes/washington/title-28b/chapter-28b-123/ — Chapter 28B.123 - Certified Public Accounting Scholarship Program.

### public_adjuster
- CT DROP https://www.cga.ct.gov/current/pub/chap_701b.htm — Chapter 701b - Public Adjusters
- CT ADD  https://law.justia.com/codes/connecticut/title-38a/chapter-701b/ — Chapter 701b - Public Adjusters

### public_weighmaster
- CT DROP https://www.cga.ct.gov/current/pub/chap_751.htm — Chapter 751 - Public Weighmasters
- CT ADD  https://law.justia.com/codes/connecticut/title-43/chapter-751/ — Chapter 751 - Public Weighmasters
- NV DROP https://www.leg.state.nv.us/nrs/NRS-582.html — Chapter 582 - Public Weighmasters
- NV ADD  https://law.justia.com/codes/nevada/chapter-582/ — Chapter 582 - Public Weighmasters
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=15.80&full=true — Chapter 15.80 - Weighmasters.
- WA ADD  https://law.justia.com/codes/washington/title-15/chapter-15-80/ — Chapter 15.80 - Weighmasters.

### radiologic_technology
- CT DROP https://www.cga.ct.gov/current/pub/chap_376c.htm — Chapter 376c - Radiographers, Radiologic Technologists, Radiologist Assistants and Nuclear Medicine Technologists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-376c/ — Chapter 376c - Radiographers, Radiologic Technologists, Radiologist Assistants and Nuclear Medicine Technologists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-653.html — Chapter 653 - Radiation Therapy and Radiologic Imaging
- NV ADD  https://law.justia.com/codes/nevada/chapter-653/ — Chapter 653 - Radiation Therapy and Radiologic Imaging
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.84&full=true — Chapter 18.84 - Radiologic Technologists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-84/ — Chapter 18.84 - Radiologic Technologists.

### real_estate_appraiser
- CT DROP https://www.cga.ct.gov/current/pub/chap_400g.htm — Chapter 400g - Real Estate Appraisers and Appraisal Management Companies
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-400g/ — Chapter 400g - Real Estate Appraisers and Appraisal Management Companies
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-21B — Chapter 21B - Real Estate Appraisers
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-21b/ — Chapter 21B - Real Estate Appraisers
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter20-1/ — Chapter 20.1 - Real Estate Appraisers
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-20-1/ — Chapter 20.1 - Real Estate Appraisers
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.140&full=true — Chapter 18.140 - Certified Real Estate Appraiser Act.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-140/ — Chapter 18.140 - Certified Real Estate Appraiser Act.

### real_estate_broker
- CT DROP https://www.cga.ct.gov/current/pub/chap_392.htm — Chapter 392 - Real Estate Licensees
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-392/ — Chapter 392 - Real Estate Licensees
- NV DROP https://www.leg.state.nv.us/nrs/NRS-645.html — Chapter 645 - Real Estate Brokers and Salespersons
- NV ADD  https://law.justia.com/codes/nevada/chapter-645/ — Chapter 645 - Real Estate Brokers and Salespersons
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-21A — Chapter 21A - Real Estate Licensing
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-21a/ — Chapter 21A - Real Estate Licensing
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter21/ — Chapter 21 - Real Estate Brokers, Sales Persons and Rental Location Agents
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-21/ — Chapter 21 - Real Estate Brokers, Sales Persons and Rental Location Agents
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.85&full=true — Chapter 18.85 - Real Estate Brokers and Managing Brokers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-85/ — Chapter 18.85 - Real Estate Brokers and Managing Brokers.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.86&full=true — Chapter 18.86 - Real Estate Brokerage Relationships.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-86/ — Chapter 18.86 - Real Estate Brokerage Relationships.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=60.42&full=true — Chapter 60.42 - Commercial Real Estate Broker Lien Act.
- WA ADD  https://law.justia.com/codes/washington/title-60/chapter-60-42/ — Chapter 60.42 - Commercial Real Estate Broker Lien Act.

### recreational_therapy
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter37-1/ — VA chapter-37-1 — Chapter 37.1 - Recreation Specialists (LLM-mapped)
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-37-1/ — VA chapter-37-1 — Chapter 37.1 - Recreation Specialists (LLM-mapped)
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.230&full=true — Chapter 18.230 - Recreation Therapy.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-230/ — Chapter 18.230 - Recreation Therapy.

### respiratory_care
- CT DROP https://www.cga.ct.gov/current/pub/chap_381a.htm — Chapter 381a - Respiratory Care Practitioners
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-381a/ — Chapter 381a - Respiratory Care Practitioners
- NV DROP https://www.leg.state.nv.us/nrs/NRS-630.html — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care
- NV ADD  https://law.justia.com/codes/nevada/chapter-630/ — Chapter 630 - Physicians, Physician Assistants, Medical Assistants, Perfusionists, Anesthesiologist Assistants and Practitioners of Respiratory Care
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-4C — Chapter 04C - Respiratory Care Practitioners
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-04c/ — Chapter 04C - Respiratory Care Practitioners
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.89&full=true — Chapter 18.89 - Respiratory Care Practitioners.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-89/ — Chapter 18.89 - Respiratory Care Practitioners.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.91&full=true — Chapter 18.91 - Respiratory Care Interstate Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-91/ — Chapter 18.91 - Respiratory Care Interstate Compact.

### security_personnel
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter19/ — Chapter 19 - Private Security Services Businesses
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-19/ — Chapter 19 - Private Security Services Businesses
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.170&full=true — Chapter 18.170 - Security Guards.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-170/ — Chapter 18.170 - Security Guards.

### social_work
- CT DROP https://www.cga.ct.gov/current/pub/chap_383b.htm — Chapter 383b - Clinical Social Workers and Master Social Workers
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-383b/ — Chapter 383b - Clinical Social Workers and Master Social Workers
- NV DROP https://www.leg.state.nv.us/nrs/NRS-641B.html — Chapter 641B - Social Workers
- NV ADD  https://law.justia.com/codes/nevada/chapter-641b/ — Chapter 641B - Social Workers
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-26 — Chapter 26 - Social Workers
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-26/ — Chapter 26 - Social Workers
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-26A — Chapter 26A - Social Work Licensure Compact
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-26a/ — Chapter 26A - Social Work Licensure Compact
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter37/ — Chapter 37 - Social Work
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-37/ — Chapter 37 - Social Work
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.225&full=true — Chapter 18.225 - Mental Health Counselors, Marriage and Family Therapists, Social Workers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-225/ — Chapter 18.225 - Mental Health Counselors, Marriage and Family Therapists, Social Workers.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.320&full=true — Chapter 18.320 - Social Workers.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-320/ — Chapter 18.320 - Social Workers.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.321&full=true — Chapter 18.321 - Social Work Licensure Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-321/ — Chapter 18.321 - Social Work Licensure Compact.

### soil_classifier
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter22/ — Chapter 22 - Soil Scientists, Wetland Professionals, and Geologists
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-22/ — Chapter 22 - Soil Scientists, Wetland Professionals, and Geologists

### speech_language_audiology
- CT DROP https://www.cga.ct.gov/current/pub/chap_397a.htm — Chapter 397a - Audiologists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-397a/ — Chapter 397a - Audiologists
- NV DROP https://www.leg.state.nv.us/nrs/NRS-637B.html — Chapter 637B - Audiologists, Speech-Language Pathologists and Hearing Aid Specialists
- NV ADD  https://law.justia.com/codes/nevada/chapter-637b/ — Chapter 637B - Audiologists, Speech-Language Pathologists and Hearing Aid Specialists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-24 — Chapter 24 - Hearing Aid Dispensers And Audiologists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-24/ — Chapter 24 - Hearing Aid Dispensers And Audiologists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-37 — Chapter 37 - Speech-Language Pathologists
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-37/ — Chapter 37 - Speech-Language Pathologists
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/47-11G — Chapter 11G - Physical Therapy, Occupational Therapy, And Speech-Language Pathology Corporations
- SD ADD  https://law.justia.com/codes/south-dakota/title-47/chapter-11g/ — Chapter 11G - Physical Therapy, Occupational Therapy, And Speech-Language Pathology Corporations
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter26/ — Chapter 26 - Audiology and Speech-Language Pathology
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-26/ — Chapter 26 - Audiology and Speech-Language Pathology
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.35a&full=true — Chapter 18.35A - Audiology and Speech-Language Pathology Interstate Compact.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-35a/ — Chapter 18.35A - Audiology and Speech-Language Pathology Interstate Compact.

### surgical_technologist
- CT DROP https://www.cga.ct.gov/current/pub/chap_382d.htm — Chapter 382d - Surgical Technologists
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-382d/ — Chapter 382d - Surgical Technologists
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.215&full=true — Chapter 18.215 - Surgical Technologists.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-215/ — Chapter 18.215 - Surgical Technologists.

### veterinary
- CT DROP https://www.cga.ct.gov/current/pub/chap_384.htm — Chapter 384 - Veterinary Medicine
- CT ADD  https://law.justia.com/codes/connecticut/title-20/chapter-384/ — Chapter 384 - Veterinary Medicine
- NV DROP https://www.leg.state.nv.us/nrs/NRS-577.html — Chapter 577 - Animal Remedies, Veterinary Biologics and Pharmaceuticals
- NV ADD  https://law.justia.com/codes/nevada/chapter-577/ — Chapter 577 - Animal Remedies, Veterinary Biologics and Pharmaceuticals
- NV DROP https://www.leg.state.nv.us/nrs/NRS-638.html — Chapter 638 - Veterinary Medicine; Euthanasia Technicians
- NV ADD  https://law.justia.com/codes/nevada/chapter-638/ — Chapter 638 - Veterinary Medicine; Euthanasia Technicians
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-12 — Chapter 12 - Veterinarians
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-12/ — Chapter 12 - Veterinarians
- VA DROP https://law.lis.virginia.gov/vacodefull/title54.1/chapter38/ — Chapter 38 - Veterinary Medicine
- VA ADD  https://law.justia.com/codes/virginia/title-54-1/chapter-38/ — Chapter 38 - Veterinary Medicine
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=18.92&full=true — Chapter 18.92 - Veterinary Medicine, Surgery, and Dentistry.
- WA ADD  https://law.justia.com/codes/washington/title-18/chapter-18-92/ — Chapter 18.92 - Veterinary Medicine, Surgery, and Dentistry.
- WA DROP https://app.leg.wa.gov/RCW/default.aspx?cite=28b.121&full=true — Chapter 28B.121 - Food Animal Veterinarian Conditional Scholarship Program.
- WA ADD  https://law.justia.com/codes/washington/title-28b/chapter-28b-121/ — Chapter 28B.121 - Food Animal Veterinarian Conditional Scholarship Program.

### wholesale_drug_distributor
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-11A — Chapter 11A - Wholesale Drug Distributors
- SD ADD  https://law.justia.com/codes/south-dakota/title-36/chapter-11a/ — Chapter 11A - Wholesale Drug Distributors

## B. URL-form normalization

Same Justia path, relative vs absolute url (hierarchy-era churn — expand_containers
wrote relative-url duplicates). Paired DROP/ADD, same chapter; benign.

### architecture
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60b/ — Section 60b - Application for Registration as Architect; Fees; Examinations
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60b/ — Section 60b - Application for Registration as Architect; Fees; Examinations
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60d/ — Section 60d - Renewals of Certificates of Registration as Architect; Fee
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60d/ — Section 60d - Renewals of Certificates of Registration as Architect; Fee
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60e/ — Section 60e - Display of Certificate of Registration as Architect; Issuance of Duplicate Certificates; Fee
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60e/ — Section 60e - Display of Certificate of Registration as Architect; Issuance of Duplicate Certificates; Fee
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60f/ — Section 60f - Seal of Registered Architect
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60f/ — Section 60f - Seal of Registered Architect
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60g/ — Section 60g - Revocation, Suspension or Annulment of Certificate of Registration as Architect; Disciplining of Registrant; Grounds
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60g/ — Section 60g - Revocation, Suspension or Annulment of Certificate of Registration as Architect; Disciplining of Registrant; Grounds
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60h/ — Section 60h - Charges Against Architect; Hearing; Notice; Revocation, Suspension or Annulment of Certificate; Notice to Secretary of State; 
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60h/ — Section 60h - Charges Against Architect; Hearing; Notice; Revocation, Suspension or Annulment of Certificate; Notice to Secretary of State; 
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60j/ — Section 60j - Roster of Registered Architects
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60j/ — Section 60j - Roster of Registered Architects
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60k/ — Section 60k - Practice of Architecture; Use of Titles; Display of Signs and Other Advertising Matter
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60k/ — Section 60k - Practice of Architecture; Use of Titles; Display of Signs and Other Advertising Matter
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60l/ — Section 60l - Services in Practice of Architecture; Plans and Specifications; Registered Professional Engineer; Employees; Landscape Archite
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60l/ — Section 60l - Services in Practice of Architecture; Plans and Specifications; Registered Professional Engineer; Employees; Landscape Archite
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60m/ — Section 60m - Determination of Services as Practice of Architecture; Finality; Fraud
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60m/ — Section 60m - Determination of Services as Practice of Architecture; Finality; Fraud
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60n/ — Section 60n - Certificate of Registration as Architect Emeritus
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60n/ — Section 60n - Certificate of Registration as Architect Emeritus
- MA DROP /codes/massachusetts/part-i/title-xvi/chapter-112/section-60o/ — Section 60o - Enforcement by Board of Registration of Architects; Attorney General; Duties
- MA ADD  /codes/massachusetts/part-i/title-xvi/chapter-112/section-60o/ — Section 60o - Enforcement by Board of Registration of Architects; Attorney General; Duties

### construction_trades
- AZ DROP https://www.azleg.gov/arsDetail/?title=32&chapter=10 — AZ Title 32 Chapter 10 — Contractors
- AZ ADD  https://www.azleg.gov/arsDetail/?title=32&chapter=10 — 

### dentistry
- IA DROP /codes/iowa/title-vii/chapter-272c/section-272c-2c/ — Section 272C.2C - Continuing education minimum requirements — medicine and surgery and osteopathic medicine and surgery, nursing, dentistry,
- IA ADD  /codes/iowa/title-vii/chapter-272c/section-272c-2c/ — Section 272C.2C - Continuing education minimum requirements — medicine and surgery and osteopathic medicine and surgery, nursing, dentistry,
- MI DROP /codes/michigan/chapter-338/statute-act-297-of-1965/ — Act 297 of 1965 - Sale of Medical or Dental Practice (338.31-338.32)
- MI ADD  /codes/michigan/chapter-338/statute-act-297-of-1965/ — Act 297 of 1965 - Sale of Medical or Dental Practice (338.31-338.32)

### electrician
- AL DROP /codes/alabama/title-34/chapter-36/section-34-36-4/ — Section 34-36-4 - Board of Electrical Contractors.
- AL ADD  /codes/alabama/title-34/chapter-36/section-34-36-4/ — Section 34-36-4 - Board of Electrical Contractors.
- IA DROP /codes/iowa/title-iii/chapter-103/section-103-9/ — Section 103.9 - Electrical contractor license.
- IA ADD  /codes/iowa/title-iii/chapter-103/section-103-9/ — Section 103.9 - Electrical contractor license.
- IA DROP /codes/iowa/title-iii/chapter-103/section-103-10/ — Section 103.10 - Class A master electrician license — qualifications — class B master electrician license.
- IA ADD  /codes/iowa/title-iii/chapter-103/section-103-10/ — Section 103.10 - Class A master electrician license — qualifications — class B master electrician license.
- IA DROP /codes/iowa/title-iii/chapter-103/section-103-10a/ — Section 103.10A - Inactive master electrician license.
- IA ADD  /codes/iowa/title-iii/chapter-103/section-103-10a/ — Section 103.10A - Inactive master electrician license.
- IA DROP /codes/iowa/title-iii/chapter-103/section-103-12/ — Section 103.12 - Class A journeyman electrician license qualifications — class B journeyman electrician license.
- IA ADD  /codes/iowa/title-iii/chapter-103/section-103-12/ — Section 103.12 - Class A journeyman electrician license qualifications — class B journeyman electrician license.
- IA DROP /codes/iowa/title-iii/chapter-103/section-103-12a/ — Section 103.12A - Residential electrician and residential master electrician license — qualifications.
- IA ADD  /codes/iowa/title-iii/chapter-103/section-103-12a/ — Section 103.12A - Residential electrician and residential master electrician license — qualifications.
- IA DROP /codes/iowa/title-iii/chapter-103/section-103-13/ — Section 103.13 - Special electrician license — qualifications.
- IA ADD  /codes/iowa/title-iii/chapter-103/section-103-13/ — Section 103.13 - Special electrician license — qualifications.
- IA DROP /codes/iowa/title-iii/chapter-103/section-103-15/ — Section 103.15 - Apprentice electrician — unclassified person.
- IA ADD  /codes/iowa/title-iii/chapter-103/section-103-15/ — Section 103.15 - Apprentice electrician — unclassified person.
- KY DROP /codes/kentucky/chapter-227a/section-227a-140/ — 227A.140 Effect of disassociation of licensee on electrical contractor or other business -- Interim period for use of recently deceased lice
- KY ADD  /codes/kentucky/chapter-227a/section-227a-140/ — 227A.140 Effect of disassociation of licensee on electrical contractor or other business -- Interim period for use of recently deceased lice
- NC DROP /codes/north-carolina/chapter-87/article-4/ — Article 4 - Electrical Contractors.
- NC ADD  /codes/north-carolina/chapter-87/article-4/ — Article 4 - Electrical Contractors.

### hvac
- AL DROP /codes/alabama/title-34/chapter-31/section-34-31-20/ — Section 34-31-20 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Creation; Composition; Transfer of Property, Etc.
- AL ADD  /codes/alabama/title-34/chapter-31/section-34-31-20/ — Section 34-31-20 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Creation; Composition; Transfer of Property, Etc.
- AL DROP /codes/alabama/title-34/chapter-31/section-34-31-21/ — Section 34-31-21 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Officers; Meetings; Power and Duties.
- AL ADD  /codes/alabama/title-34/chapter-31/section-34-31-21/ — Section 34-31-21 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Officers; Meetings; Power and Duties.
- AL DROP /codes/alabama/title-34/chapter-31/section-34-31-22/ — Section 34-31-22 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Compensation.
- AL ADD  /codes/alabama/title-34/chapter-31/section-34-31-22/ — Section 34-31-22 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Compensation.
- AL DROP /codes/alabama/title-34/chapter-31/section-34-31-23/ — Section 34-31-23 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Regular Meetings.
- AL ADD  /codes/alabama/title-34/chapter-31/section-34-31-23/ — Section 34-31-23 - Board of Heating, Air Conditioning, and Refrigeration Contractors - Regular Meetings.
- MD DROP /codes/maryland/business-regulation/title-9a/subtitle-2/ — Subtitle 2 - State Board of Heating, Ventilation, Air-Conditioning, and Refrigeration Contractors
- MD ADD  /codes/maryland/business-regulation/title-9a/subtitle-2/ — Subtitle 2 - State Board of Heating, Ventilation, Air-Conditioning, and Refrigeration Contractors
- NC DROP /codes/north-carolina/chapter-87/article-5/ — Article 5 - Refrigeration Contractors.
- NC ADD  /codes/north-carolina/chapter-87/article-5/ — Article 5 - Refrigeration Contractors.
- TX DROP /codes/texas/occupations-code/title-8/chapter-1302/subchapter-e/ — Subchapter E. Air Conditioning and Refrigeration Contractors Advisory Board
- TX ADD  /codes/texas/occupations-code/title-8/chapter-1302/subchapter-e/ — Subchapter E. Air Conditioning and Refrigeration Contractors Advisory Board
- TX DROP /codes/texas/occupations-code/title-8/chapter-1302/subchapter-f/ — Subchapter F. Air Conditioning and Refrigeration Contractors
- TX ADD  /codes/texas/occupations-code/title-8/chapter-1302/subchapter-f/ — Subchapter F. Air Conditioning and Refrigeration Contractors
- TX DROP /codes/texas/occupations-code/title-8/chapter-1302/subchapter-k/ — Subchapter K. Air Conditioning and Refrigeration Technicians
- TX ADD  /codes/texas/occupations-code/title-8/chapter-1302/subchapter-k/ — Subchapter K. Air Conditioning and Refrigeration Technicians

### insurance_producer
- GA DROP https://law.justia.com/codes/georgia/title-33/chapter-23/ — GA Title 33 Ch 23 — Licensing of Agents (hand-found via probe_justia)
- GA ADD  https://law.justia.com/codes/georgia/title-33/chapter-23/ — GA Title 33 Ch 23 — Licensing of Agents (hand-found via probe_justia)
- NC DROP https://law.justia.com/codes/north-carolina/chapter-58/article-33/ — NC Ch 58 Art 33 — Licensing of Insurance Producers (hand-found via probe_justia)
- NC ADD  https://law.justia.com/codes/north-carolina/chapter-58/article-33/ — NC Ch 58 Art 33 — Licensing of Insurance Producers (hand-found via probe_justia)
- TN DROP https://law.justia.com/codes/tennessee/title-56/chapter-6/ — TN Title 56 Ch 6 — Agents, Solicitors (hand-found via probe_justia)
- TN ADD  https://law.justia.com/codes/tennessee/title-56/chapter-6/ — TN Title 56 Ch 6 — Agents, Solicitors (hand-found via probe_justia)
- VA DROP https://law.justia.com/codes/virginia/title-38-2/chapter-18/ — VA Title 38.2 Ch 18 — Insurance Agents (hand-found via probe_justia)
- VA ADD  https://law.justia.com/codes/virginia/title-38-2/chapter-18/ — VA Title 38.2 Ch 18 — Insurance Agents (hand-found via probe_justia)
- WI DROP https://law.justia.com/codes/wisconsin/chapter-628/ — WI Ch 628 — Insurance Marketing (agent licensing) (hand-found via probe_justia)
- WI ADD  https://law.justia.com/codes/wisconsin/chapter-628/ — WI Ch 628 — Insurance Marketing (agent licensing) (hand-found via probe_justia)

### plumbing
- IA DROP /codes/iowa/title-iii/chapter-91c/section-91c-1/ — Section 91C.1 - Definition — exemption — combined registration and licensing process for plumbers and mechanical professionals.
- IA ADD  /codes/iowa/title-iii/chapter-91c/section-91c-1/ — Section 91C.1 - Definition — exemption — combined registration and licensing process for plumbers and mechanical professionals.

### public_adjuster
- FL DROP https://law.justia.com/codes/florida/title-xxxvii/chapter-626/part-vi/ — Part VI - Insurance Adjusters (Ss. 626.851-626.8797)
- FL ADD  https://law.justia.com/codes/florida/title-xxxvii/chapter-626/part-vi/ — Part VI - Insurance Adjusters (Ss. 626.851-626.8797)

## C. WA umbrella (Ch 18.130)

Nodes added by the WA Uniform Disciplinary Act umbrella mechanism (shipped Jun-30;
indexes never regenerated since).

### dentistry
- WA ADD https://law.justia.com/codes/washington/title-18/chapter-18-130/ — WA Ch 18.130 — Uniform Disciplinary Act (grounds, complaints, sanctions)

### medicine
- WA ADD https://law.justia.com/codes/washington/title-18/chapter-18-130/ — WA Ch 18.130 — Uniform Disciplinary Act (grounds, complaints, sanctions)

### nursing
- WA ADD https://law.justia.com/codes/washington/title-18/chapter-18-130/ — WA Ch 18.130 — Uniform Disciplinary Act (grounds, complaints, sanctions)

### optometry
- WA ADD https://law.justia.com/codes/washington/title-18/chapter-18-130/ — WA Ch 18.130 — Uniform Disciplinary Act (grounds, complaints, sanctions)

### podiatry
- WA ADD https://law.justia.com/codes/washington/title-18/chapter-18-130/ — WA Ch 18.130 — Uniform Disciplinary Act (grounds, complaints, sanctions)

### public_accountancy
- WA ADD https://law.justia.com/codes/washington/title-18/chapter-18-130/ — WA Ch 18.130 — Uniform Disciplinary Act (grounds, complaints, sanctions)

## D. Other drift

REQUIRES HUMAN REVIEW — anything not explained above. Should be nearly empty after
the keep-rule preserved real losses. Remaining ADD lines = new base-only matches
(junk → hand `exclude` entries); remaining DROP lines = untagged nodes not caught
by the keep-rule (add by hand if needed).

### architecture
- NM DROP /codes/new-mexico/chapter-61/article-15/ — Article 15 - Architects
- WV DROP /codes/west-virginia/chapter-30/article-12/ — Article 12. Architects

### construction_trades
- UT ADD https://le.utah.gov/xcode/Title58/Chapter55/58-55.html — Chapter 55 - Utah Construction Trades Licensing Act (contractor scope)

### dentistry
- NM DROP /codes/new-mexico/chapter-61/article-5a/ — Article 5A - Dental Health Care
- NM DROP /codes/new-mexico/chapter-61/article-5b/ — Article 5B - Impaired Dentists and Dental Hygienists
- WV DROP /codes/west-virginia/chapter-30/article-4/ — Article 4. West Virginia Dental Practice Act
- WV DROP /codes/west-virginia/chapter-30/article-4a/ — Article 4A. Administration of Anesthesia by Dentists

### electrician
- CT DROP https://www.cga.ct.gov/current/pub/chap_393.htm — Section 20-334d. - Continuing professional education requirements for electricians and plumbers. Regulations. Exemptions.
- CT ADD https://law.justia.com/codes/connecticut/title-20/chapter-393/ — Chapter 393 - Electricians, Plumbers, Solar, Heating, Piping and Cooling Contractors and Journeymen, Elevator and Fire Protection Sprinkler Craftsmen, Irrigation Contractors and Journeymen, Gas Hearth Installer Contractors and Journeymen and Residential Stair Lift Technicians
- ID DROP https://legislature.idaho.gov/statutesrules/idstat/Title54/T54CH10/ — Section 54-1010 - INSTALLATIONS BY ELECTRICAL CONTRACTOR PERFORMED BY LICENSED RESIDENTIAL OR JOURNEYMAN ELECTRICIAN — PRIOR CERTIFICATE HOL
- ID ADD https://law.justia.com/codes/idaho/title-54/chapter-10/ — Chapter 10 - ELECTRICAL CONTRACTORS AND JOURNEYMEN
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-16 — Section 36-16-4 - Commission member involved in education of electrical engineers or electricians.
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-16 — Section 36-16-14 - Contractor license required for installation of wiring or parts--Farm and residential wiring by Class B electrician.
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-16 — Section 36-16-20 - Undertaking and insurance required of contractor or Class B electrician--Initial and renewal deposit--Disbursement from f
- SD DROP https://sdlegislature.gov/api/Statutes/Statute/36-16 — Section 36-16-23 - Reciprocal licenses to electricians from other states.
- SD ADD https://law.justia.com/codes/south-dakota/title-36/chapter-16/ — Chapter 16 - Electricians And Electrical Contractors
- SD ADD /codes/south-dakota/title-36/chapter-16/section-36-16-4/ — Section 36-16-4 - Commission member involved in education of electrical engineers or electricians.
- SD ADD /codes/south-dakota/title-36/chapter-16/section-36-16-14/ — Section 36-16-14 - Contractor license required for installation of wiring or parts--Farm and residential wiring by Class B electrician.
- SD ADD /codes/south-dakota/title-36/chapter-16/section-36-16-20/ — Section 36-16-20 - Undertaking and insurance required of contractor or Class B electrician--Initial and renewal deposit--Disbursement from f

### plumbing
- CT DROP https://www.cga.ct.gov/current/pub/chap_393.htm — Section 20-334d. - Continuing professional education requirements for electricians and plumbers. Regulations. Exemptions.
- CT ADD https://law.justia.com/codes/connecticut/title-20/chapter-393/ — Chapter 393 - Electricians, Plumbers, Solar, Heating, Piping and Cooling Contractors and Journeymen, Elevator and Fire Protection Sprinkler Craftsmen, Irrigation Contractors and Journeymen, Gas Hearth Installer Contractors and Journeymen and Residential Stair Lift Technicians

### podiatry
- VA ADD https://law.justia.com/codes/virginia/title-54-1/chapter-29/ — Chapter 29 — Medicine and Other Healing Arts

---

## Category totals

| Category | Lines |
|---|---|
| A. Official→Justia URL flip | 666 |
| B. URL-form normalization | 82 |
| C. WA umbrella (Ch 18.130) | 6 |
| D. Other drift | 22 |
| **Total** | **776** |

Residual adds migrated to mapping_overrides.yaml: 248

## Per-profession drift count

| Profession | Changed nodes |
|---|---|
| acupuncture | 6 |
| alcohol_drug_counseling | 2 |
| anesthesiologist_assistant | 4 |
| applied_behavior_analysis | 10 |
| architecture | 48 |
| athlete_agent | 10 |
| athletic_training | 8 |
| auctioneer | 6 |
| chiropractic | 8 |
| commercial_interior_design | 6 |
| community_health_worker | 2 |
| construction_trades | 13 |
| cosmetology | 18 |
| court_reporter | 8 |
| dentistry | 41 |
| dietetics | 10 |
| direct_entry_midwifery | 4 |
| electrician | 46 |
| electrology | 2 |
| environmental_health | 4 |
| funeral_services | 16 |
| genetic_counseling | 6 |
| health_facility_admin | 8 |
| hearing_instrument_specialist | 8 |
| home_inspector | 8 |
| hvac | 24 |
| insurance_producer | 16 |
| junk_dealer | 8 |
| land_surveying | 6 |
| landscape_architecture | 8 |
| livestock_dealer | 2 |
| massage_therapy | 10 |
| medicine | 19 |
| mental_health_counseling | 30 |
| money_transmitter | 4 |
| music_therapy | 6 |
| naturopathic_medicine | 6 |
| nurse_midwifery | 2 |
| nursing | 31 |
| occupational_therapy | 12 |
| opticianry | 8 |
| optometry | 13 |
| osteopathic_medicine | 4 |
| pawnbroker | 8 |
| perfusionist | 4 |
| pharmacy | 26 |
| physical_therapy | 12 |
| physician_assistant | 10 |
| plumbing | 18 |
| podiatry | 10 |
| polygraph_examiner | 6 |
| private_investigator | 6 |
| process_server | 4 |
| professional_engineering | 8 |
| professional_geology | 12 |
| psychology | 16 |
| public_accountancy | 17 |
| public_adjuster | 4 |
| public_weighmaster | 6 |
| radiologic_technology | 6 |
| real_estate_appraiser | 8 |
| real_estate_broker | 14 |
| recreational_therapy | 4 |
| respiratory_care | 10 |
| security_personnel | 4 |
| social_work | 16 |
| soil_classifier | 2 |
| speech_language_audiology | 14 |
| surgical_technologist | 4 |
| veterinary | 14 |
| wholesale_drug_distributor | 2 |

