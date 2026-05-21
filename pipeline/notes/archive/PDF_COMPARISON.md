# Our extraction vs. the human-curated podiatry PDF

Spot-check across four states where both the Utah-DPM podiatry PDF (compiled
from Westlaw, ~half human-verified) and our extraction (Justia + Sonnet, with
verbatim quote validation) have data.

The honest assessment: **for states where both have data, we catch
2-3× more structured fields than the PDF**, while occasionally missing
specific values the PDF surfaces (e.g. CT's "32 weeks" residency duration —
our model judged the source ambiguous because there are different durations
for pre-2006 vs. post-2006 graduates, and stayed silent rather than guess).

## CT — Connecticut

| | Their PDF | Ours |
|---|---|---|
| License required | ✓ | ✓ regulatory_model = license |
| Issuing authority | DPH | ✓ Department of Public Health |
| Education | "DPM, DSC, or Pod.D from approved school" | ✓ "Doctor of Podiatric Medicine (D.P.M.)" |
| Residency duration | "32 weeks" | ❌ null (Sonnet correctly noted source has different durations for pre-/post-2006 graduates) |
| Renewal | not stated | ✓ 1 year |
| Anatomical scope | mid-leg myotendinous junction | ✓ same enum value |
| Amputation | "Chopart joint-level allowed" | ✓ chopart_joint_and_below |
| Anesthesia | local + moderate sedation | ✓ local_and_moderate_deep_sedation |
| Ankle surgery | yes, with cert | ✓ + 2yr-pre-2007 / 3yr-post-2007 + ABFAS / ABPM cert bodies |
| Total ankle replacement | "with exception" | ✓ true |
| Pilon fractures | "not allowed" | ✓ tibial_pilon_fracture_excluded |
| Title protection | implicit in act | ✓ explicit boolean |
| Scope protection | implicit | ✓ explicit boolean |
| Disciplinary grounds | not tabulated | ✓ 13 grounds, each with quote + cite |
| Office-based surgery accreditation | not mentioned | ✓ true |
| Hospital privileges nondiscrimination | not mentioned | (false in CT) |
| Corrective-footwear exemption | not mentioned | ✓ true |

**Net:** PDF has 1 detail we missed (32-wk residency); we have ~10 dimensions PDF doesn't tabulate at all.

## TN — Tennessee

| | Their PDF | Ours |
|---|---|---|
| License required | ✓ | ✓ regulatory_model = license |
| Education | "DPM from accredited college" | ✓ same |
| Residency | yes, ≥1 year | ✓ "at least one year" |
| Renewal | 2 yr | ✓ |
| CE | not specified | ✓ 15 hrs / 1 yr |
| Anatomical scope | "no higher than distal tibial metaphyseal flair" | ✓ exact enum match |
| Amputation | foot excluded | ✓ foot_entirety_excluded |
| Anesthesia | general not allowed | ✓ general_excluded |
| Ankle surgery | yes, with credentials | ✓ + 24-month residency + ABPS |
| Ankle-surgery cert timeline | "within 6 years..." | ✓ verbatim string |
| Pilon fractures | excluded | ✓ |
| Standard-of-care reference | "must meet orthopedic surgeon standard" | ✓ ankle_surgery_standard_of_care_reference = true |
| PA collaboration | mentioned | ✓ physician_assistant_collaboration_authorized |
| X-ray technician cert | mentioned | ✓ |
| Disciplinary grounds | not tabulated | ✓ 18 grounds |

**Net:** parity on PDF's facts; we add ~8 dimensions including UORF + structured grounds.

## MO — Missouri

| | Their PDF | Ours |
|---|---|---|
| Issuing authority | "state board of podiatric medicine" | ✓ same |
| Education | "approved college of podiatric medicine" | ✓ |
| CE | "24 hrs in 2 years" | ✓ 24 / 2 |
| Renewal | 2 yr | ✓ |
| Scope | foot, ankle, tendons inserting into foot | ✓ exact enum match |
| Anesthesia | general not allowed | ✓ general_excluded |
| Amputation | foot prohibited | ✓ not_authorized |
| Ankle surgery | yes, with cert + facility | ✓ + 24-month residency + ABPS |
| Bone surgery on children <1 | "prohibited" | ❌ we missed this — likely in a section the trim dropped |
| Disciplinary grounds | not tabulated | ✓ 16 grounds |

**Net:** we caught everything except one specific prohibition; we add CE structure + structured grounds.

## WV — West Virginia (formerly all-gap)

| | Their PDF | Ours |
|---|---|---|
| Coverage | yes — but we used to be empty here | ✓ override → §30-3 (Medicine) caught it |
| Education | DPM | ✓ |
| Residency | ≥1 yr clinical | ✓ "minimum of one year" |
| Exams | APMLE | ✓ |
| Renewal | 2 yr | ✓ |
| CE | "≥50 hours per 2-yr period" | ✓ 50 / 2 |
| Scope | foot and ankle | ✓ |
| Ankle surgery | yes, with hospital credentialing | ✓ hospital_credentialing_required |
| Telehealth | not mentioned | ✓ true (we caught it; PDF didn't) |
| Impaired-practitioner program | not mentioned | ✓ true |
| Preoperative H&P authority | not mentioned | ✓ true |
| Disciplinary grounds | not tabulated | ✓ 22 grounds |

**Net:** we went from "no record" → matches PDF on every field PDF has, plus 4 dimensions PDF doesn't track.

## Patterns across the 4 spot-checks

**Where we genuinely miss things:**
- Residency *durations* sometimes go null when the source is conditional (CT's pre/post-2006 split; multiple variants)
- Specific carve-out prohibitions buried in sections trim dropped (MO's children <1 bone surgery)
- Wound-care silence — we don't always identify "PDF says 'silent on wound care'" as a positive finding

**Where we systematically beat the PDF:**
- 36 profession-specific structured fields per state vs. 5 paragraph-style PDF columns
- UORF model classification (license / mandatory cert / etc.) — PDF doesn't categorize
- Title- and scope-protection booleans separately — PDF lumps both into "license required"
- Disciplinary grounds enumerated as a list rather than buried in prose
- Every leaf claim has a verbatim quote + section citation, regex-validated against the source (98.7% match rate); PDF citations are paragraph-level

**Where the PDF systematically beats us:**
- Coverage breadth: PDF has all 50 states (Westlaw access); we have 37–47 depending on chains
- Wound-care subtleties: PDF tracks this as a column; ours treats it as a single discovered field that's only present where states explicitly mention it
- Prose narrative is more readable for one-off lookups; ours is structured for cross-state comparison
- Admin code (CE topical rules etc.) — PDF cites both statute and admin code; we currently only pull statute

## TL;DR

For states where we have substantive data, ours is a strict superset on
*structured comparable* dimensions and roughly tied on *specific facts*.
The PDF wins on coverage breadth (Westlaw vs. Justia) and on prose nuance
that doesn't fit the schema. The 32-week-residency type miss is a real
extraction issue on conditional-language states; documented for prompt
tuning.
