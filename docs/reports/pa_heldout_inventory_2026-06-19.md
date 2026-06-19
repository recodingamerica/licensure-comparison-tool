# PA held-out professions — full inventory (all 64)

**Status:** 2026-06-19. Branch `pa-heldout-batch-2`. Completes the per-profession PA
classification for every held-out profession (the 64 that were not among the
7 published or the 8 pilot-batch-1 professions). Every WU01 act URL below was
verified to fetch `200` with the act title present before wiring.

The point is to say **exactly what "PA coverage" means** per profession rather
than claim blanket coverage — including the legitimate result that PA **does not
license** a profession by statute (24 of 64).

## Summary

| Bucket | Count | Status |
|---|---:|---|
| **Wired + extracted (batch 2)** | 29 | done this branch |
| Deferred — embedded in Medical Practice Act (need keep-list) | 6 | section numbers known |
| Deferred — embedded in Insurance Company Law (need keep-list) | 1 | section known |
| Deferred — consolidated Pa.C.S. (pa_legis parser doesn't split) | 3 | needs parser work |
| Deferred — act number not yet found | 1 | speech_language_audiology |
| **NONE — PA does not license by statute** | 24 | documented, not wired |
| **Total** | **64** | |

## Batch 2 — wired + extracted (29)

All pulled via `pa_legis` (legis.state.pa.us WU01), clean→trim→discover_schema→
extract_state_batch. Each row's WU01 URL verified 200 + title match.

| Profession | Act | WU01 | Notes |
|---|---|---|---|
| osteopathic_medicine | Osteopathic Medical Practice Act (261/1978) | 1978/0/0261 | `authoritative` (dropped Justia "Act 29" sibling) |
| naturopathic_medicine | Naturopathic Doctor Registration Act (128/2016) | 2016/0/0128 | title-protection/registration only |
| acupuncture | Acupuncture Licensure Act (2/1986) | 1986/0/0002 | co-admin Medicine + Osteopathic boards |
| veterinary | Veterinary Medicine Practice Act (326/1974) | 1974/0/0326 | |
| occupational_therapy | Occupational Therapy Practice Act (140/1982) | 1982/0/0140 | |
| hearing_instrument_specialist | Hearing Aid Sales Registration Law (262/1976) | 1976/0/0262 | Dept. of Health, Title 35 |
| massage_therapy | Massage Therapy Law (118/2008) | 2008/0/0118 | |
| surgical_technologist | Central Service Tech & Surgical Tech Regulation Act (80/2020) | 2020/0/0080 | DOH; registration/standards, not BPOA license |
| real_estate_appraiser | Real Estate Appraisers Certification Act (98/1990) | 1990/0/0098 | |
| auctioneer | Auctioneer Licensing & Trading Assistant Registration Act (85/1983) | 1983/0/0085 | |
| pawnbroker | Pawnbrokers License Act (51/1937) | 1937/0/0051 | Dept. of Banking |
| architecture | Architects Licensure Law (281/1982) | 1982/0/0281 | (Act 31/1998 = amendments) |
| landscape_architecture | Landscape Architects' Registration Law (535/1965) | 1965/0/0535 | session-year quirk: "(1966) 1965" |
| professional_engineering | Engineer, Land Surveyor and Geologist Registration Law (367/1945) | 1945/0/0367 | **SHARED** act ↓ |
| land_surveying | — same act — | 1945/0/0367 | surveying = Act §4.4 |
| professional_geology | — same act — | 1945/0/0367 | geology added by Act 151/1992, §4.3 |
| health_facility_admin | Nursing Home Administrators License Act (122/1970) | 1970/0/0122 | BPOA board |
| wholesale_drug_distributor | Wholesale Prescription Drug Distributors License Act (145/1992) | 1992/0/0145 | DOH, not Board of Pharmacy |
| private_investigator | Private Detective Act of 1953 (361/1953) | 1953/0/0361 | county Court of Common Pleas |
| security_personnel | Lethal Weapons Training Act (235/1974) | 1974/0/0235 | State Police; armed agents only |
| money_transmitter | Money Transmission Business Licensing Law (249/1965) | 1965/0/0249 | `authoritative`; Title 7 Banking |
| public_adjuster | Public Adjuster Licensing Law (72/1983) | 1983/0/0072 | Insurance Dept; codified Title 63 |
| building_inspector | Pennsylvania Construction Code Act (45/1999) | 1999/0/0045 | DLI certifies code officials |
| construction_trades | Home Improvement Consumer Protection Act / HICPA (132/2008) | 2008/0/0132 | AG registration, not licensure |
| insurance_producer | Insurance Producer Licensing Law / Ins. Dept Act Art. VI-A (147/2002) | 2002/0/0147 | Title 40 |
| loan_broker | Credit Services Act (150/1992) | 1992/0/0150 | Title 73; broker registration embedded |
| athlete_agent | Revised Uniform Athlete Agents Act (139/2022) | 2022/0/0139 | enacting act for 5 Pa.C.S. Ch. 35 |
| nurse_midwifery | Midwife Regulation Law (155/1929) | 1929/0/0155 | Board of Medicine (not Nursing); short old act |
| mental_health_counseling | SW/MFT/Professional Counselors Act (39/1987) | 1987/0/0039 | `authoritative`; **SHARED** with social_work (LPC/LMFT) |

## Deferred — embedded, need keep-lists (7)

These point at an already-pulled or large host act; pulling the whole act is
mostly noise, so they need a `pa_keep_sections` keep-list scoping the corpus to
their provision (the dietetics-in-nursing pattern). Section numbers known:

| Profession | Host act | WU01 | Provision |
|---|---|---|---|
| physician_assistant | Medical Practice Act of 1985 | 1985/0/0112 | §422.13 (+ Osteopathic §271.x for DO-supervised) |
| respiratory_care | Medical Practice Act of 1985 | 1985/0/0112 | §422.13a (added by Act 60/1993) |
| athletic_training | Medical Practice Act + Osteopathic | 1985/0/0112 + 1978/0/0261 | §422.51a / §271.7a |
| perfusionist | Medical Practice Act of 1985 | 1985/0/0112 | §422.13c (added by Act 19/2008) |
| prosthetist_orthotist | Medical Practice Act of 1985 | 1985/0/0112 | §422.13e (added by Act 90/2012) |
| genetic_counseling | Medical Practice + Osteopathic | 2011/0/0125 + 2011/0/0126 | §422.13d / §271.10c |
| applied_behavior_analysis | Insurance Company Law of 1921 (Autism Act 62/2008) | 2008/0/0062 | "Behavior Specialist", §635.2 / 40 P.S. §764h |

## Deferred — consolidated Pa.C.S. (parser TODO) (3)

WU01 serves the enacting act, but the `pa_legis` section-splitter (div.Comment
markers) returns **0 sections** for these because the page is a Title-amendment
("Title X is amended by adding a chapter…") rather than a standalone act with
per-section markers. Needs a consolidated-statute parse path or a different source.

| Profession | Act | WU01 (0 sections) | Consolidated cite |
|---|---|---|---|
| livestock_dealer | Domestic Animal Law (100/1996) | 1996/0/0100 | 3 Pa.C.S. § 2342 |
| public_weighmaster | Consolidated Weights & Measures Act (155/1996) | 1996/0/0155 | 3 Pa.C.S. §§ 4171 et seq. |
| home_inspector | Home Inspection Law (114/2000) | 2000/0/0114 | 68 Pa.C.S. Ch. 75 |

## Deferred — act number not found (1)

- **speech_language_audiology** — Speech-Language Pathologists and Audiologists
  Licensure Act, Act of Dec. 21, 1984, P.L. 1253 (63 P.S. §§ 1701-1719), State
  Board of Examiners in Speech-Language and Hearing. STANDALONE. The session-law
  **act number** wasn't surfaced by research (session year 1984); needs a lookup
  to build the `1984/0/{ACTNUM}` WU01 URL, then it joins batch 2.

## NONE — PA does not license by statute (24)

A legitimate, useful result: these are not gaps, they are professions PA does not
license at the state level. Do **not** wire or claim coverage.

| Profession | Why NONE |
|---|---|
| anesthesiologist_assistant | practice only under physician delegatory authority; licensure bills never enacted |
| opticianry | dispensing opticians unregulated; 1973 bill not enacted |
| direct_entry_midwifery | CPM/lay midwives unregulated; only the 1929 nurse-midwife license exists |
| recreational_therapy | not licensed (ATRA: only DC/NH/NJ/NC/OK/UT) |
| polysomnography | sleep techs not licensed; credentialing via RPSGT |
| electrology | unregulated; HB 1304 (cosmetology board) not enacted |
| radiologic_technology | RTs not licensed in PA; ARRT by employer policy; bills not enacted |
| community_health_worker | voluntary PCB certification only |
| medical_interpreter | not licensed; only court & sign-language interpreters are regulated (separately) |
| psychoanalysis | no distinct credential; practiced under psychologist/LCSW/LPC/MD |
| alcohol_drug_counseling | no statutory license; PCB (non-governmental) certifies; AOD → LPC pathway |
| music_therapy | not licensed; HB 2573 (amend Act 39) died in committee |
| environmental_health | sanitarians = employment qualification (16 P.S. §§ 12001+), no Title 63 license |
| court_reporter | court-administered (201 Pa. Code Rule 4004), no licensing statute |
| forester | unregulated (PA not among forester-licensing states) |
| soil_classifier | unregulated; PAPSS voluntary registry only |
| junk_dealer | municipal licensing only; no state occupational license |
| polygraph_examiner | not licensed; 18 Pa.C.S. § 7321 only restricts employer use |
| process_server | not licensed; service by sheriff or competent adult (Pa.R.C.P. 400) |
| private_probation | governmental function; PA is not a for-profit-probation state |
| plumbing | state-level NONE — plumber licensure is municipal (Phila., Allegheny Co.) |
| electrician | state-level NONE — electrician licensure is municipal |
| insurance_navigator | registration not licensure (Act 7/2015); Pennie certification (Act 42/2019) |
| commercial_interior_design | NONE (license) — 2024 SB 1319 adds only a voluntary "Certified Interior Designer" title under the Architects board |

## Provenance

All act numbers/years from parallel web research (PA board sites pa.gov/BPOA,
P.S. citations, Wikipedia, legal databases); WU01 URLs independently verified
against the project fetcher (`curl_cffi` chrome impersonation) — 200 + act-title
match — before wiring. legis.state.pa.us was not bulk-fetched during research.
