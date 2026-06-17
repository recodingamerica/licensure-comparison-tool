# Plan: `pa_legis` puller — unlock Pennsylvania statutes (#25/#26)

**Status:** researched & validated 2026-06-17; ready to execute.

## Why
PA is missing for **every profession except medicine** (and medicine's is a 1-section stub).
Root cause: PA uses unconsolidated **pamphlet-law** numbering (`63 P.S. § 244.x`), so
`state_structure.yaml` marks it `source: pa_complex, layout: broken` and the team deferred it
("Justia sparse; palegis.us JS/query-string; FindLaw anti-scrape; Cornell no PA").

This is the whole of #25 (dietetics gaps) and #26 (optometry gaps): the other states Atharv
listed are actually filled now (FL/WI/MN/MO/SC dietetics 33–43 fields; MI/MN/NY optometry
32–41); CO dietetics is correctly sparse (credential bill vetoed). The gaps reduce to **PA**.

## The breakthrough (validated)
The **legacy static endpoint** serves each act's FULL text on one clean HTML page, fetchable
with the **existing curl_cffi chrome method**, sections delimited by `Section N.` anchors
(`...&act=57&...&sctn=N&subsctn=M`):

```
https://www.legis.state.pa.us/WU01/LI/LI/US/HTM/{year}/{sessInd}/{act:04d}..HTM
```

Confirmed working (status 200, full text, distinct sections parsed):
- Optometric Practice & Licensure Act — 1980, act 57 → `.../1980/0/0057..HTM` (13 sections)
- Medical Practice Act of 1985 — 1985, act 112 → `.../1985/0/0112..HTM` (54 sections)
- Pharmacy Act — 1961, act 699 → `.../1961/0/0699..HTM` (14 sections)

(The modern `uconsCheck.cfm?...act=NN` URL 301-redirects to the JS palegis.us site — avoid it;
the `/WU01/.../HTM` static page does NOT redirect.)

## Implementation steps
1. **Section parser** for the WU01 page (BeautifulSoup): the page is a TOC of
   `<a ... sctn=N ...>Section N.</a> <title>` followed by the body. Split into sections; for
   each emit `{citation, text, source_url}`. Body text is in `<p>` tags. Citation: derive
   `63 P.S. § <base>.<N>` where possible (base 244 for optometry), else
   `"Act {act} of {year} § {N}"`. `source_url` = the WU01 URL (+ `#`/anchor if useful).
2. **Wire `source: pa_legis`** through `match_profession.py` (produce the act URL per
   profession) and `pull_text.py` `extract_section_text` (parse WU01), mirroring how
   `mi_legis` / `revisor_mn` are dispatched. Read those two handlers first.
3. **Config** (`state_structure.yaml` PA block): replace `pa_complex/broken` with
   `source: pa_legis` + per-profession act coords `{year, sessInd, act}`.
   - **Pilot: optometry** = `{1980, 0, 57}` (clean standalone act, named in #26).
4. **Run pipeline for PA optometry**: pull → clean → trim → extract. Validate (fields filled,
   quotes verify, no coverage_gap). Spot-check the record vs the statute.
5. **Expand** per-profession act coords (lookup each PA practice act number):
   - dietetics → **Professional Nursing Law** (1951 P.L. 317, **No. 69**) — dietetics/LDN is
     *embedded* in the Nursing Law, not standalone; corpus is large, lean on trim to drop the
     nursing-only sections. Try `.../1951/0/0069..HTM`.
   - medicine = 1985/112 (already has a justia stub; switch to pa_legis for the full act).
   - others: research act numbers as needed.
6. **Publish**: `refresh_all --deploy` once PA states are in.

## "Do it well" caveats
- **Citations don't deep-link to Justia** (PA isn't on Justia) — point PA source links at
  legis.state.pa.us instead; make sure the frontend citation link handles a non-Justia URL.
- **Embedded professions** (dietetics in Nursing Law) need the right act + good trimming so the
  corpus isn't dominated by other professions.
- Be polite to legis.state.pa.us (per-host delay); it's not Justia so lighter rate-limit risk,
  but one profession at a time still.

## Value
Unlocks PA across **all 15 professions**, not just the two issues. Pilot optometry first, prove
the end-to-end, then expand.
