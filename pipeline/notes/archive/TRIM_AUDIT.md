# Trim audit — 2026-05

Scanned all dropped sections across podiatry / CPA / medicine / dentistry
for labels that suggest substantive licensure/scope content.

## Method

`pipeline/notes/trim_audit.py` scans `results/trimmed/<profession>/<STATE>.json`
for sections marked dropped, classifies labels against substantive-pattern
regex (scope of practice, license required, continuing education, etc.) AND
against admin-pattern exclusions (notice of hearing, fee schedule, member
qualifications, etc.). Output: 45 candidate "potentially substantive but
dropped" sections out of 804 raw keyword hits.

## Findings

The 45 flagged sections fall into three buckets:

**Correctly dropped (~35 of 45)** — the trim's stated reason is accurate.
Examples:
- *"Notice of Hearing Before Revocation of License"* → procedural, not scope
- *"Renewal certificate" definition / data request availability* → admin
- *"Practicing without license: Reporting requirements of Board"* → reporting
  procedures, not licensure content
- *"Application for Reciprocity to Be Certified"* → application form, not
  reciprocity criteria
- *"Refusal of Admittance to Examination"* (TX podiatry 202.258) → judicial
  review process for admin denials, not the exam itself

**Repealed-section drops (~5 of 45)** — explicitly marked repealed in source.
Universal repealed-exclude (in `match_profession`) handles these at the
chapter level; trim correctly drops at the section level.

**Possibly load-bearing — chapter "Definitions" sections (~5 of 45)**.
A few states' top-level "Definitions" sections got dropped. Examples:
- TN podiatry §63-3-102 "Chapter definitions" — trim said it only defined
  administrative terms ("board", "division") with no scope content.
  Plausible but a chapter's definitions section sometimes also defines
  "practice of podiatry" or "podiatrist" which IS scope.
- TX podiatry §202.401, §202.451 — sub-subchapter definitions for
  "privilege" and "peer review". Trim correctly identified as scoped to
  admin procedures, defensible drop.
- IN CPA §25-2.1-1-2 "Applicability of Definitions" — applicability stub,
  defensible drop.
- AR medicine §17-95-101 "'Good Samaritan' law — Definition" — immunity
  provision unrelated to licensure, defensible drop.

## Recommendation

The trim is **doing the right thing on the substantive/administrative
distinction**. The trim prompt language ("KEEP if it covers scope /
qualifications / discipline; DROP if it's about board composition / fees /
forms / records") matches reality.

Two minor adjustments worth considering for the next prompt revision:

1. **Default-keep top-level chapter "Definitions" sections** when the label
   doesn't clearly scope to a sub-procedure. A chapter's main definitions
   usually contain "practice of X means..." which is scope. False drops
   here have a higher cost than false keeps (definitions are short).

2. **For "Practicing without a license"** sections, KEEP rather than DROP
   when the section CONTAINS the prohibition itself, not just the reporting
   procedure. The current trim drops these as "reporting requirements" but
   some of them ALSO contain the substantive prohibition ("a person shall
   not practice without a license"). Cheap to keep, supports the
   scope_protection field.

These two changes would add maybe 5-10 sections back per profession across
~50 states — negligible token cost, possible accuracy gain on the
scope-protection / definitions-of-practice fields. Not urgent.

## Numbers

| Profession         | Total dropped sections | Suspicious drops | Likely false drops |
| ------------------ | ---------------------- | ---------------- | ------------------ |
| dentistry          | ~hundreds              | 6                | ~1 (NV definitions of 'renewal certificate' — defensible) |
| medicine           | ~hundreds              | 15               | ~3 (definitions sections in some states) |
| podiatry           | ~hundreds              | 18               | ~2-3 (TN/TX definitions sections) |
| public_accountancy | ~hundreds              | 6                | ~1 (IN applicability stub — defensible) |

Bottom line: trim is sound. The 90-98% verification rate across professions
isn't being held back by aggressive trimming.
