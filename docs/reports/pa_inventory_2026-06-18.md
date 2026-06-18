# PA occupation inventory — published 7

**Status:** 2026-06-18. Branch `feat/pa-legis-puller-25-26`. Not yet published/deployed.

Per-occupation structure for Pennsylvania, so we can say exactly what "PA coverage"
means rather than claiming blanket coverage. Scope: the **7 published professions**
(live map/blob payloads). The other 72 held-out professions are a separate backlog
(see bottom). All acts pulled via the `pa_legis` puller (legis.state.pa.us WU01
static endpoint); see [pa_puller_plan_2026-06-17.md](pa_puller_plan_2026-06-17.md).

## Result: all 7 published professions have real, verified PA records

| Profession | PA act(s) | WU01 coords | Structure | Fields | Evidence |
|---|---|---|---|---|---|
| optometry | Optometric Practice & Licensure Act (57/1980) | 1980/0/0057 | standalone | 14/33 | 45✓ / 1 |
| medicine | Medical Practice Act of 1985 (112/1985) | 1985/0/0112 | standalone | 8/21 | 35✓ / 0 |
| dentistry | The Dental Law (76/1933) | 1933/0/0076 | standalone | 12/30 | 43✓ / 0 |
| podiatry | Podiatry Practice Act (375/1955 sess.) | 1955/0/0375 | standalone | 7/36 | 34✓ / 0 |
| public_accountancy | CPA Law (140/1947) | 1947/0/0140 | standalone | 24/38 | 55✓ / 0 |
| nursing | Professional Nursing Law (69/1951) **+** Practical Nurse Law (376/1955 sess.) | 1951/0/0069 + 1955/0/0376 | **multi-act** | 12/29 | 45✓ / 0 |
| dietetics | Professional Nursing Law (69/1951) — LDN sections only | 1951/0/0069 (keep-list) | **embedded** | 8/30 | 39✓ / 0 |

Notes:
- **1955-session quirk:** podiatry, the LPN law, and other mid-50s acts were
  signed in 1956 but belong to the 1955 session — the WU01 `{year}` segment is
  **1955**, not 1956. A 1956 URL 404s.
- **nursing** spans two acts; `pull_text` pulls `url` + every PA URL in
  `section_url_list`.
- **dietetics** is embedded in the Nursing Law. `pa_keep_sections` scopes the
  corpus to the 21 LDN + act-wide-administrative sections, dropping the
  nursing-scope blocks (§3 RN/CNS, §4 unauthorized practice, §8.1–8.9
  CRNP/CNS/CRNA, §6.1/6.2 nursing education, §12.1 nursing CE) and repealed stubs.
- **dietetics regulatory_model = voluntary_certification** (title protection):
  §3.1 makes it unlawful to *hold oneself forth* as a "licensed
  dietitian-nutritionist" / use "L.D.N." but does **not** restrict practice
  (scope_protection=false). NOTE: this rung is **unstable** run-to-run — the model
  has flipped between `voluntary_certification` and `license`, and on the
  voluntary_certification run still left `is_mandatory=true` (a cross-field
  inconsistency the prompt already forbids at prompts.yaml:145–153). Title-
  protection professions are a known soft spot, not PA-specific.

## Two coverage illusions caught

1. **public_accountancy** was counted "matched" (50/50) but pointed at a Justia
   node (`act-27`) that was **never pulled** — no text/structured record. matched
   ≠ extracted. Now a real CPA Law record.
2. **medicine** was a 1-section Justia "VISITING TEAM PHYSICIAN" stub; now the
   full 64-section act.

## Umbrella / cross-board general provisions

PA has cross-board acts that apply to every BPOA licensing board:
- **Act 6 of 2018** (2018/0/0006) — BPOA reporting of sanctions & criminal
  proceedings, suspension, civil penalties. *Confirmed pullable (4 sections).*
- **Act 53 of 2020** (2020/0/0053, Cl. 18) — criminal history & licensure
  (limits on denial for convictions). *Confirmed pullable (6 sections).*
- **Act 48 of 1993** (63 P.S. §§ 2201–2207) — foundational civil-penalty
  authority. **Not in the WU01 HTM viewer** (404 at 1993/0/0048); its actual
  civil-penalty *schedule* lives in regulation (49 Pa. Code Ch. 43b), which we
  do not pull (we do statutes).

**Decision: NOT wired into the corpus.** Unlike WA (Ch 18.130) or NY (Art. 130),
**PA practice acts are self-contained** — each act carries its own disciplinary
grounds (optometry §7, nursing §14, dentistry, podiatry, CPA all populated
`disciplinary_grounds` from their own act). And the current schema has **no
dedicated civil-penalty or criminal-history field**; the only field the umbrella
would feed (`disciplinary_grounds`) is already filled. So folding the umbrella in
would cost a full re-extract of all 7 (plus citation-collision disambiguation
across acts) for marginal field gain.

**Revisit when:** a civil-penalty or criminal-history field is added to the
schema, OR a held-out PA profession turns out to defer discipline to a general
act. Then attach Act 6/2018 + Act 53/2020 per-profession (WA pattern:
`section_url_list`), and tag PA citations with the act to avoid `§ N` collisions.

## Held-out professions (backlog, not done)

72 other professions in `professions.yaml` still lack PA. The `pa_legis` puller is
general — each needs (a) its PA act number/year, (b) standalone/embedded/none
classification, (c) for embedded ones a `pa_keep_sections` list. Not started; do
not claim coverage for these.
