# Session handoff — citation audit + tier3_absence.json grind (2026-07-08 night)

Read `docs/runbooks/session_handoff_2026-07-08.md` first — that's the earlier
handoff from the same day (watchdog/gap-harvest reliability work, 607-test suite,
the 16-occupation extract batch). This doc picks up from there.

## What happened this session

1. Verified 11 label-mismatch-flagged Justia citation cells (web research, no CDP).
   8 wrong, 3 confirmed correct. Wrote fixes.
2. **Correction to my own earlier framing**: mid-session I thought a "concurrent
   background session" was independently fixing cells in parallel. It wasn't a
   separate agent — it was `pull_8_confirmed.log`, the background `nohup ... &
   disown` job already documented as in-flight in `session_handoff_2026-07-08.md`
   (the earlier doc), working through the exact 8 cells listed there
   (`athlete_agent/NE`, `landscape_architecture/NE`, `auctioneer/NV`,
   `polygraph_examiner/CA`+`MA`, `public_weighmaster/KY`,
   `radiologic_technology/MI`+`MN`) plus a broader `narrow.py --detect-labels` sweep
   across other professions. It has since gone idle (no `pull_text`/`clean_text`/etc.
   process running as of this handoff) but **left ~185 files uncommitted** — see
   "Uncommitted work" below. Check
   `ps aux | grep -E "pull_text|clean_text|trim_state|extract_state"` before
   assuming it's still idle — if you see one running, do not start your own pull.
3. Worked through `pipeline/results/gap_harvest/parked_cells.json` (14 cells the
   locator gave up on after 3 misses) — fully resolved.
4. Started `pipeline/results/gap_harvest/tier3_absence.json` (the big prevalence-based
   backlog) — finished profession #1 of 78 (`polysomnography`).

**4 commits this session** (scoped narrowly — deliberately did NOT commit the
concurrent sweep's files):
- `7c3fe835` — 3 verified-absence citation fixes (polygraph_examiner/DE,
  public_weighmaster/KY, auctioneer/NE) + construction_trades IN/TX/NH verified absences
- `5ff27851` — auctioneer/NV, radiologic_technology/MI+MN verified absences
- `d51d0a93` — athlete_agent/NE + landscape_architecture/NE corpus expansion
  (found they were real gaps, not mismatches — only 2/19 and 3/25 sections were pulled),
  professional_geology/OK verified absence
- `6b18792e` — polysomnography: 33-state verified-absence batch + 6 confirmed real
  gaps (DE/MD/NY dedicated acts, ID/NH/ND via their Respiratory Care Act)

## IMPORTANT: uncommitted work sitting in the tree

Run `git status --short` before doing anything else. As of handoff there are ~185
uncommitted files from the concurrent sweep touching: acupuncture,
alcohol_drug_counseling, architecture, bail_bond_agent, building_inspector,
construction_trades, electrician, emergency_medical_technician, hvac, loan_broker,
massage_therapy, optician, opticianry, plumbing, professional_engineering,
professional_geology, prosthetist_orthotist, public_adjuster,
wholesale_drug_distributor — plus `state_structure.yaml`, `mapping_overrides.yaml`,
`locator_results.json`. **This looks like real, good work (fixes + a full clean→trim→
extract pass on several trades)** but it was never reviewed or committed. Before
building on top of it: skim the diff, sanity-check a few cells, then commit it
(scoped, not `git add -A` blindly — there may be partial/interrupted state).

## Priority queue — frontend-published professions first

Published today (check `pipeline/publish/web/public/data/` or run
`python -m pipeline.client.handoff_doc` to confirm, don't trust this list blindly):
architecture, construction_trades, dentistry, dietetics, electrician, hvac,
medicine, nursing, optometry, plumbing, podiatry, professional_engineering,
public_accountancy.

### Step 1 — finish the 5 published trades already in `tier3_absence.json`'s `likely_gap`

Cross-referencing `likely_gap` against the published list gives exactly these 5
(none of `likely_absent`/`sometimes` touch a published profession):
`professional_engineering`, `construction_trades`, `plumbing`, `electrician`, `hvac`.

**Good news: most of these already have corpora pulled** (likely by the concurrent
sweep) — they just need `clean_text` → `trim_state` → `extract_state` run, which is
LLM-only (no CDP, no Justia fetch, safe to run any time, use
`pipeline.extract.extract_state_batch` for >2 cells per the batch-extraction default).

As of handoff:
- `plumbing`, `electrician`: **fully done** already (KS/NE/NY/WY and IL/IN/KS/NY).
- `hvac`: 9/15 done; **ME, MA, MT, NH, ND, VT** have corpora pulled, just need extract.
- `construction_trades`: 3/16 done (IN/NH/TX — our verified absences); **KS, MD, MI,
  MO, MT, NE, NY, SD, WI** have corpora, need extract. **CO, DE, OK, WY** only have a
  1-3 section stub — check before extracting, may need a real re-pull.
- `professional_engineering`: 0/13 done but **12 of 13 have substantial corpora**
  (AZ, AR, CO, KS, ME, MI, MN, NE, NH, RI, TN, VA) — just need extract. **TX** only has
  1 section, needs a real re-pull.

So: run the clean→trim→extract batch on the "have corpora" cells first (cheap, no
CDP), then separately investigate the handful of 1-3-section stubs
(`construction_trades/CO,DE,OK,WY`, `professional_engineering/TX`) — likely need an
actual re-pull via CDP once free.

### Step 2 — keep grinding `tier3_absence.json`, `likely_absent` bucket next

11 professions total, 1 done (`polysomnography`). Remaining 10, none published, but
this is the cleanest-signal bucket (RARELY-regulated per prevalence) and the
methodology is now proven:

`apiarist`, `perfusionist`, `community_health_worker`, `medical_interpreter`,
`psychoanalysis`, `health_facility_admin`, `commercial_interior_design`,
`private_probation`, `insurance_navigator`, `soil_classifier`

**Do NOT batch-assume absence from a summary web search.** The polysomnography pass
caught 6 states (DE/MD/NY/ID/NH/ND) that actually DO regulate it, despite the
profession being tagged RARELY overall. Early signal on this next batch: perfusionist
searches already surfaced LA, MD, NE as likely real licensing states sitting in our
gap list — check those first before writing absences for that profession. Method that
worked:
1. Find an authoritative national tracker for the profession (professional
   association, state-licensure-board directory — NALLOA/ASRT/BRPT-style, not a
   marketing blog).
2. Cross-reference its regulating-state list against our gap-state list.
3. States NOT on the regulating list → `pipeline/config/verified_absences.yaml`
   (`basis: not_regulated`, cite the tracker) → `python -m
   pipeline.extract.apply_verified_absences --profession <p>`.
4. States that ARE regulating → find the actual statute citation + Justia URL (if it
   resolves), add to `profession_index/<p>.json`, do NOT write an absence. Queue for
   pull if no CDP available right now.
5. `apply_verified_absences.py` will refuse to overwrite a real extracted record
   (skip + log) — if that happens, trust the existing extraction over your absence
   conclusion (it happened for `polysomnography/GA` and the real record agreed with
   "not regulated" anyway, which is a nice cross-check).

### Step 3 — `sometimes` bucket (16 professions, 529 pairs) and the rest of `likely_gap` (46 non-published professions, most of the 1,061 pairs)

Lowest priority since none touch published professions. `sometimes` needs real
per-state judgment calls (that's why the heuristic couldn't classify it). Most of
`likely_gap` is "the state probably has a real corpus we just haven't found/pulled" —
same treatment as Step 1's trades, minus the frontend urgency.

## Operational reminders (from CLAUDE.md + this session)

- **Before any CDP pull**: `ps aux | grep -E "pull_text|clean_text|trim_state|extract_state"`
  — one pull process per Chrome, a flock guards it but don't rely on that alone.
- **Scoped commits only**: check `git status --short` before `git add`; stage exact
  files you verified, never `git add -A`/`git add .` while another process might be
  mid-write to shared files (`profession_index/*.json`, `verified_absences.yaml`,
  `gap_harvest/locator_results.json`).
- **Stage order**: after fixing a mapping, delete the stale `text/`+`clean/` corpus
  pulled from the wrong/incomplete URL (pull_text won't refetch if the file already
  exists) — then re-pull → clean → trim → extract in full.
- `pipeline/results/gap_harvest/tier3_absence.json` has the full backlog +
  `prevalence` tags; `pipeline/results/gap_harvest/parked_cells.json` and
  `label_audit.json` are now mostly/fully worked (check before redoing).

## CDP Chrome is idle right now (checked end of session) — ready-to-pull queue

No `pull_text`/`clean_text`/`trim_state`/`extract_state` process running, and no
watchdog/`gap_supervise.sh` auto-relaunching one. The debug Chrome
(`--remote-debugging-port=9222`, `--user-data-dir=~/chrome-debug`) is still open and
idle, sitting on a Kansas Justia page. **`pull_worklist.json` (123 entries) is stale —
do not run it blindly**, per the earlier handoff doc. Instead, these are the specific
cells this session confirmed need a real pull, with mapping already fixed and the
stale/wrong corpus already deleted — safe to fire immediately:

- `bail_bond_agent/MI`, `emergency_medical_technician/MT`,
  `emergency_medical_technician/OK` — mapping corrected, ready to re-pull.
- `athlete_agent/NE`, `landscape_architecture/NE` — `section_url_list` expanded to
  the full statute range, ready to re-pull.
- `polysomnography/DE`, `/MD`, `/NH` — newly mapped (real gaps caught during the
  tier3 pass), never pulled at all.
- `construction_trades/CO`, `/DE`, `/OK`, `/WY` and `professional_engineering/TX` —
  only have 1-3 section stubs on disk; likely need a real re-pull (verify the
  existing chapter mapping is even right before re-pulling — hasn't been checked).

Suggested command shape (adjust per `pipeline/ingest/pull_text.py`'s actual CLI):
`JUSTIA_CDP_URL=http://127.0.0.1:9222 pipeline/.venv/bin/python -m
pipeline.ingest.pull_text --profession <p> --states <ST> --force`, one profession at
a time, committing between pulls.
