# How automatable is the occupation pipeline? (handoff assessment)

**Question (from the 2026-06-18 tech-transfer slides):** how much of "add / process
an occupation" can run hands-off, so OPLR (or anyone) can extend the tool without us?

This is the honest, stage-by-stage answer, updated as we automate more. The method:
run a profession through the chain; wherever a step needs a human *and that's
fixable*, convert it to automation (often a new LLM call); re-validate on the next.

## The lifecycle, stage by stage

| Stage | What it does | Automation today | The human part (if any) |
|---|---|---|---|
| **0. Discover the occupation** | decide it exists + is licensed | ✅ **automated today** — `discover_occupations.py` (LLM reads each state's chapter structure, surfaces untracked occupations incl. ones nested in a broader act) | review the candidate list (judgment, light) |
| **1. Register** (`professions.yaml`) | display name, family, match `patterns` | ⚠️ manual (hand-written patterns) | **next to automate** — draft the entry from the name via LLM |
| **2. Match → index** | which chapter each state maps to | ✅ automated — `match_profession` + `llm_map_profession` (LLM mapper handles umbrella-nested + judgment) | review mapper flags (`audit_llm_candidates`) |
| **3. Pull statute text (Justia)** | fetch the corpus | 🔴 **fragile ops** — CDP Chrome + Cloudflare, rate-limited, needs babysitting | **the real handoff risk.** BUT: see "nested" below — many occupations skip this entirely |
| **4. clean → trim → extract** | LLM → structured records | ✅ automated — `extract_state_batch` (durable, ~50% cheaper) | gated by `check_consistency` |
| **5. map_prep** | choropleth + tag normalization | ✅ automated (LLM, 2-pass) | — |
| **6. build + publish** | payloads + blobs + deploy | ✅ automated — `refresh_all` / `build_frontend` | add to one hardcoded `PROFESSIONS` list |
| **7. Coverage QA** | did we get the right chapters? records sane? | ⚠️ partial — `audit_llm_candidates` guardrail + `check_consistency` | spot-check (judgment) |

## The big unlock: nested occupations need NO new Justia pull

The PM's "occupations hiding in other occupations" turns out to be the cheapest
path to automate. Discovery flags occupations bundled inside an act we've **already
harvested** — Dental Hygienist inside the Dentistry corpus (present in **all 50
states**), Barber/Esthetician/Nail Tech inside Cosmetology, Pharmacy Tech inside
Pharmacy, Embalmer inside Funeral Services. For these the chain skips Stage 3
entirely: **discover → register → extract from existing text → publish.** That sidesteps
the one genuinely-hard-to-hand-off step.

## Bottom line (current)

- **Already hands-off:** discovery (new), matching, extract, map_prep, build/publish.
  Processing a profession whose text we already have is **push-button**.
- **Automate next (fixable manual steps):** (1) registration auto-draft from a name;
  (2) a tighter QA pass so the human only reviews flagged anomalies.
- **The irreducible-ish human/ops part:** the **Justia harvest** (Stage 3) for
  genuinely-new corpora — fragile, setup-heavy. Mitigations: nested occupations skip
  it; official-source pullers (PA, UT-XML, NV/SD APIs) are more robust than Justia
  where they exist. This is the piece to be candid with OPLR about in the transfer.

**So: ~5 of 7 stages are hands-off today; discovery just moved from manual to
automated; registration is next; the Justia harvest is the part that realistically
stays with whoever can run the scraper (or is avoided via nested + official sources).**

## Discovery output
`pipeline.discover.discover_occupations` → `results/discover_occupations/<STATE>.json`
+ `aggregate` → `_candidates.json` (untracked occupations ranked by # states regulating
them). The widely-regulated, currently-untracked ones are the highest-value adds.
