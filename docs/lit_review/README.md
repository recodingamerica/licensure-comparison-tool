# Occupational licensing lit review — what other people's bucket frameworks look like

**Date:** 2026-05-29
**Purpose:** Before we invent our own bucket schema for characterizing Utah professions, see what's already out there. Five external sources reviewed. PDFs in `sources/`.

---

## TL;DR

Two of these (IJ, NCSL) already publish a clean per-profession × per-state × variable matrix that overlaps strongly with what `map_prep` is producing. **One — the Knee Center's database — is the single most useful artifact for our umbrella work**, because it has ~300 occupations across all 50 states + DC in downloadable Excel and it's the source the other libertarian indices build on.

The Obama 2015 report and the CLEAR 2020 report are framing documents, not data — useful for write-up vocabulary but not for buckets.

If we adopt one schema as our backbone, it should be the **IJ five-variable schema** (fees, education/experience days, exams, minimum age, minimum grade). It's the most concrete, most cited, and the closest fit to what's already in the pipeline. We can lean on Knee for broader profession coverage where IJ has gaps.

---

## Sources

| File | What it is | Year | Useful for |
|---|---|---|---|
| `Utah_OPLR_Occupational_Regulation_Framework_Dec2025.pdf` | **Utah OPLR's own published UORF framework** | Dec 2025 | **Authoritative ladder definition** — confirms our 6 rungs match exactly |
| `IJ_License_to_Work_2nd_edition.pdf` | Institute for Justice "License to Work" 2nd ed. (3rd ed is behind Cloudflare; uses same methods) | 2017 | **Variable schema** — gold standard |
| `Obama_2015_white_house_licensing_framework.pdf` | Treasury / CEA / DOL "Occupational Licensing: A Framework for Policymakers" | 2015 | **Conceptual buckets**, alternative regulation typology |
| `Archbridge_2023_State_Occupational_Licensing_Index.pdf` | Archbridge Institute State Occupational Licensing Index (SOLI) | 2023 | **Confirms Knee Center is the broadest occupation list** |
| `CLEAR_2020_state_regulatory_structures.pdf` | Council on Licensure, Enforcement and Regulation — state regulatory structures | 2020 | **Governance models** (umbrella vs. independent), not professions |
| *(not downloaded — web page only)* | NCSL National Occupational Licensing Database | 2017–22 | 48 occupations, public dashboard |
| *(not downloaded — Cloudflare block)* | Knee Regulatory Research Center OLLRP Database | live, last 2024–25 | **~300 occupations, Excel download, all states** |

---

## What each source actually has

### 1. Institute for Justice — *License to Work* (2nd ed.)

102 lower-income occupations × 50 states + DC. Five fixed variables per (occupation, state):

| Variable | Units | What gets summed in |
|---|---|---|
| **Fees** | $ | application + processing + licensing fees |
| **Education / experience** | calendar days lost | hours, weeks, months, years, degrees → days via fixed conversion (6 hr/day school; 5-day work week; degree = standard completion years × 365) |
| **Exams** | count of discrete exams | written + oral + practical, multi-part counted as one |
| **Minimum age** | years | |
| **Minimum grade** | grade number (12 = HS) | |

Composite "burden score" = weighted T-scores summed; weights are **education/experience × 20, grade × 1.5, others × 1**. State-level burden = average across occupations × number licensed in state.

Selection rules worth copying:
- Counts anything that *functions* as a license, even if state calls it "permit" or "certification."
- Title-only laws ("registered interior designer") **excluded**.
- For sole proprietors when possible; worker license when sole-prop isn't realistic.
- Multiple licenses required? Record all of them.
- Multiple alternative licenses? Use the **least restrictive** unless it's not the right occupation fit.
- Noted-but-excluded: surety bonds, character references, CPR training, tuition costs.

### 2. Knee Regulatory Research Center — OLLRP Database (WVU)

- ~300 occupations / license categories, all 50 states + DC.
- Two flavors: **universally licensed** (subset of variables, simpler) and **partially licensed** (full data dictionary, multiple pathways).
- Downloadable as **Excel + Word read-me per occupation**.
- Variables span: degrees, fees, education hours, experience, continuing education, reciprocity, "good moral character", criminal record, board structure (composition, appointment, term lengths).
- Covers 1870–2019 historically.
- This is the **dataset every other libertarian index uses as input** (Archbridge SOLI explicitly does).

### 3. NCSL National Occupational Licensing Database

48 occupations chosen by a fixed rule: licensed in 30+ states AND no 4-year degree required AND projected positive employment growth. Per occupation, per state:

- Numeric: education level, training hours, experience weeks, exam counts, renewal timeframes, continuing education, initial + renewal fees, minimum age.
- Categorical: moral character, criminal record restrictions, reciprocity, board independence.
- Structural: oversight mechanism, board composition, appointment method, term length.

Last updated summer 2022. Lives as a PowerBI dashboard, not a bulk download.

### 4. Obama 2015 — Framework for Policymakers

Not a dataset. Provides a **conceptual typology of regulatory intensity** that's useful vocabulary:

1. **License** — must have state permission to practice
2. **Certification ("right-to-title")** — anyone can do the work, only the certified can use the title
3. **Registration** — list of practitioners, low requirements
4. **Bonding / insurance** — financial backing instead of credential
5. **Establishment regulation / inspection** — regulate the firm, not the worker

Plus a sunset/sunrise review checklist with criteria policymakers should weigh (public health & safety risk, whether less-burdensome alternatives suffice, effect on supply, effect on prices, administrative costs).

### 5. Archbridge SOLI 2023

345 occupations from Knee, two simple counts per state: **total barriers** (occupation barred under any title) and **total licenses** (occupation barred under its own title), each normalized 0–10. Methodologically thin — really the value here is confirming the Knee occupation list and showing the "barred under another license" idea (acupuncturist → physician license; shampooer → cosmetologist) which is a *real* problem in our chapter-label data.

### 6. CLEAR 2020 — already discussed

Five **governance models** (A–E) for boards vs. central agencies. Utah is one of three Model E states. Useful as one sentence in writeups, nothing more.

---

## How to use this for our buckets

### Recommendation: anchor the variable schema to IJ's five, plus a small extension set

**Backbone (steal directly from IJ):**

| Our bucket | IJ analogue | Notes |
|---|---|---|
| Fees | sum of all $ at entry | Easy to populate from statute. Decide whether to include renewal fees (IJ doesn't; NCSL does). |
| Education / experience | calendar days lost (IJ conversion) | We already encode this as text — converting to a number unlocks comparability. |
| Exams | count | |
| Minimum age | years | |
| Minimum education level | grade or degree | IJ uses grade; degree is cleaner for higher-ed professions. Pick one. |

**Extension set (where IJ stops but Knee/NCSL/Obama frames matter for our audience):**

- **Continuing education** (hours/year) — Knee + NCSL both track. We should too; it's a recurring burden.
- **Reciprocity / endorsement** — Knee + NCSL track. Categorical: none / partial / full.
- **Criminal record / moral character** — Knee + NCSL track. Categorical: explicit bar / discretionary / no statutory bar.
- **Regulation type** — License / Certification / Registration / Other (Obama 2015 typology). This is the **one we're probably under-using** and it matters a lot for OPLR's "should this even be licensed" question.
- **Renewal frequency** (years) — NCSL tracks.
- **Bond / insurance requirement** — NCSL categorical.

**Suggested NOT to copy from IJ:**

- The T-score / weighted composite "burden rank." It's elegant for cross-occupation comparison but it bakes in IJ's prior (education × 20). For UORF/OPLR audience we should present raw values and let readers weigh; we're not running a national ranking exercise.
- The day-conversion table for degrees. Useful for IJ's "days lost" metric; for our profile pages, statute language ("Bachelor's degree + 2 yrs supervised experience") is more honest than "1,090 days."

### Recommendation: borrow the Obama "alternatives to licensing" typology as a separate bucket

This is the single most concrete improvement we can make for the OPLR audience: every profession in our table should be flagged with **regulation type** (License / Certification / Registration / Other). It directly answers the "is this the right tool" question OPLR is asking, and it's framework-grounded — we're not inventing a category.

### Recommendation: Knee turned out not to help us. *(Updated 2026-05-29 after spot check.)*

Pre-spot-check hypothesis was that Knee's ~300 occupations + statute citations would be a useful pointer/index. We pulled all 17 of their available data files into `sources/knee/` and ran a side-by-side on **optometry / UT** (where both we and Knee have data). Findings:

| Comparison point | Knee | Ours |
|---|---|---|
| Latest data year | **2016** | current |
| Schema width | 8 numeric requirement variables | ~25 structured fields |
| UT optometry citations | §58-16a-302 / 303 / 304 | same sections |
| Education representation | code = "5" + comment string | string + accrediting body |
| Exam representation | count = 1 | 3 named exams |
| Credential type | code = "0" (opaque) | `license` (semantic) |
| Title / scope protection, disciplinary grounds, advisory board, regulatory authority structure | absent | present |

**Net findings:**

1. **For the 6 professions we've already extracted, Knee adds zero signal** — they're shallower, ~10 years stale, and cite the exact same Title 58 sections we do.
2. **For the ~9 unextracted slots Knee has data on** (PA, dispensing optician, massage, professional counselor, respiratory care, cosmetology, funeral, mortgage), the only marginal benefit is "this is regulated in Utah, here's the chapter to look in" — which our own discover pass already gives us.
3. **Knee's "~300 occupations" headline is aspirational.** Only ~15 occupations have actual data files published. The rest of the catalog is forward-looking.
4. **The lumping concern stays open.** Knee splits barber / cosmetologist / esthetician / shampooer; our `cosmetology` lumps them per Utah Title 58. The sub-occupation credential variance (Utah may license cosmetologists but only register shampooers) won't surface in our extraction if we treat the chapter as one record. **Not a Knee-specific issue** — would matter even without Knee.

**Action**: keep `sources/knee/` for the record, but **don't build any workflow on top of it**. The spot-check is the close-out. See [[project_knee_dead_end]] memory note.

What we'd **not** do: bulk-import Knee's variable values (fees, hours, exams) into our DB and treat them as our extracted data — but moot, since we wouldn't get marginal value anyway.

### What this lit review does NOT solve

- It does not give us a fixed 67-id profession taxonomy. None of these sources have a clean canonical list that matches Utah Title 58 chapter structure.
- It does not help with state-level governance characterization beyond what CLEAR already gives us (Utah = Model E).
- It does not solve the umbrella-vs.-independent-board question per profession, because none of these sources track that at the profession level inside a state.

---

## Open questions / suggested next steps

1. ~~Pull Knee OLLRP Excel as an index only.~~ **Done 2026-05-29; turned out not to help.** Knee data is shallower, stale (last year = 2016), and cites the same Title 58 sections we already do. See updated "Knee turned out not to help us" section above.
2. **Add `regulation_type` column** (License / Certification / Registration / Other) to `map_prep`. Highest-value, cheapest add from this review.
3. **Decide on fees scope** — entry only (IJ) or entry + renewal (NCSL). Probably entry + renewal listed separately.
4. **Decide whether to convert education to "days lost."** Recommend no for the table cell (use statute text), but maybe yes for any cross-state comparison view.
5. **Format a one-line regulatory-structure note** for Utah using CLEAR (Model E). Probably belongs in `docs/STATUS.md` or the homepage, not per-profession.
