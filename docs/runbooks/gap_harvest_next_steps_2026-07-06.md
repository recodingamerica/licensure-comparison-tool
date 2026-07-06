# Gap harvest — next steps (handoff, 2026-07-06)

Pick up here. The search-driven gap harvest is mid-pull; everything downstream is built,
clean, and committed. Package: `pipeline/discover/gap_harvest/` (README = module map).

## ⭐ NEXT SESSION — START HERE (written end of session 2)

**State at clear:** main pull was RUNNING at 238/510 (46%), alphabetical, in the big
`money_transmitter`/`public_weighmaster`/`public_adjuster`/`pawnbroker` tail (~12 hrs left
at 2.8 min/cell). Session-2 analysis is UNCOMMITTED but safe in the working tree (a `/clear`
doesn't touch it):
```
 M docs/runbooks/gap_harvest_next_steps_2026-07-06.md   (this file — session-2 notes)
 M pipeline/results/gap_harvest/locator_results.json     (3 relocated cells)
?? pipeline/results/gap_harvest/recovered_nulls_review.json
?? pipeline/results/gap_harvest/reuse_audit_2026-07-06.json
?? pipeline/results/queues/gap_harvest_ready.json        (regenerable; harvest-scoped, ~471 cells now)
```

**Do these in order:**
1. **Check the pull** (`pgrep -f gap_pull.sh`; count via the snippet in "How to check / resume").
   If stopped before ~510, resume: `caffeinate -disu bash pipeline/discover/gap_harvest/gap_pull.sh`
   (idempotent). Needs debug Chrome at `127.0.0.1:9222`, challenge solved once.
2. **Commit the session-2 work** above (lock-retry if the pull is still committing per-profession;
   don't run two committing git processes at once).
3. **When the pull is DONE, re-pull the flagged cells via CDP** (the pull skips them — they look
   "done" but are stubs): the **3 relocate** cells (`relocate_worklist.json`) + the **13 degenerate
   reuse** cells (`reuse_audit_2026-07-06.json → repull_degenerate`). Write their corrected targets,
   then `pull_text` those specific (prof, state) pairs.
4. **Re-run cleanup** across everything: `python -m pipeline.discover.gap_harvest.cleanup` (report),
   `--relocate` if it finds new defects. Catches anything the completed tail introduced.
5. **Regenerate the extract queue** with the (corrected) snippet in step 3 below — scope is
   pulled ∪ reused, NOT a bare pull_worklist scan. Grows to ~771 cells minus skips.
6. **Extraction is the PAID step (~$150, real API $) and is on HOLD by the user's call.** Confirm
   with them before submitting. Then `clean_text → trim_state → extract_state_batch submit --queue
   pipeline/results/queues/gap_harvest_ready.json`. Consistency-gated; re-extract only flagged cells.

**Deferred / product decisions (don't act without the team):** which held-out professions to
publish; the ~72–90 novel recovered nulls (sibling/exemption chapters — see the deferred section);
the 6 all-repealed reuse cells (may be correct absence). Details in the sections below.

## Update — 2026-07-06 (session 2)

- **Pull verified healthy, ~220/510 (43%).** Corrected ETA: **~287 cells / ~13 hrs left**
  at the observed 2.8 min/cell (alphabetical; currently in `loan_broker`, everything after
  it at 0). The handoff's "~214" was near the start of this run, not near the end.
- **Cleanup report run across the 220 pulled cells: only 3 defects** (2 dead 404-stores,
  1 wrong-level) — `landscape_architecture/AZ`, `loan_broker/AZ`,
  `wholesale_drug_distributor/OK`. All 3 **re-located via `cleanup --relocate`** (web_search,
  no CDP) and written to `relocate_worklist.json`; they still need a re-pull once CDP frees.
  Note: a 1-section corpus is NOT automatically a stub — cleanup only flags it dead if it's a
  stored 404 page; most small corpora are legit single-section statutes.
- **Extraction DECISION: HOLD.** Extraction is the paid step (~$0.20/cell, real API $).
  Don't extract before the run's shape is settled (cleanup + relocate re-pull done), or you
  pay to extract cells you'll re-do. Overlap-extracting the ready cells was considered and
  rejected for this reason — the ~$45 isn't worth pre-committing to an unsettled corpus.
- **Reuse audit run** (`results/gap_harvest/reuse_audit_2026-07-06.json`). reuse.py is
  structurally sound — **0 prefix-leakage across all 261** (never grabbed a wrong sibling's
  sections; URL-prefix invariant holds in the files), **242/261 have live statutory law.** But
  **13 are degenerate stubs** (reused a sibling corpus that was itself index-only, so the only
  "section" is the chapter landing page — dental_hygienist/MS, hvac/ND, opticianry/MS+ND,
  osteopathic_medicine/MS+ND+TX, professional_engineering/TX, professional_geology/TX,
  land_surveying/WY, nurse_midwifery/IL+ND, wholesale_drug_distributor/OK) + **6 all-repealed**
  (osteopathic_medicine/MT etc.). **These pass `is_pulled` (1 section) so gap_pull SKIPS them
  and extract would produce nothing** — they must be explicitly RE-PULLED via CDP after the
  main pull (`repull_degenerate` in the audit JSON), same as the relocate cells. Review the 6
  empty ones (may be genuinely all-repealed = correct absence).
- **Extract queue pre-staged (uncommitted, regenerable):**
  `pipeline/results/queues/gap_harvest_ready.json` — {prof: [states]} for every cell with
  text, no structured record, and not in `relocate_worklist.json`. Left uncommitted so it
  doesn't race the pull's per-profession git commits. **Regenerate it post-pull** (it grows
  as the pull completes) with the snippet in step 3 below, then `submit --queue`.

## State at handoff

- **Main pull RUNNING** (detached, survives a session clear): ~214/510 cells pulled.
  Reused 261 more with no fetch. 0 empties, ~1% dead (cleanup handles it). ~2.8 min/cell.
- **All 50 gap professions have extraction schemas** (`results/discovered/`).
- **Code**: consolidated into a clean package (`_common`, `locate`, `reuse`, `cleanup`,
  `discover`, `coverage`, `gap_pull.sh`). Nothing else imports it.
- **Data** (committed, `results/gap_harvest/`): `tier3_absence.json` (1,061 gaps),
  `locator_results.json` (772 located + 128 recovered + 161 absent), `pull_worklist.json`
  (510), `reused.json` (261), `relocate_worklist.json`, `dead_cells.json`.
- **8 flywheel professions PARKED** in professions.yaml (pest_control, outfitter_guide,
  asbestos_abatement, meat_inspector, boxer, hawker_peddler, septage_pumper,
  managing_general_agent) — located but not pulled; do them in the flywheel round below.
- Status issue for Atharv: **#58**. Full plan: `gap_harvest_plan_2026-07-05.md`.

## How to check / resume the pull

Needs the debug Chrome up at `127.0.0.1:9222` (solved once). Check:
```
pgrep -f gap_pull.sh                      # running?
python -c "import json,os; wl=json.load(open('pipeline/results/gap_harvest/pull_worklist.json')); \
print(sum(1 for p in wl for s in wl[p] if os.path.exists(f'pipeline/results/text/{p}/{s}.json')),'/',sum(len(v) for v in wl.values()))"
```
If stopped before done, resume (idempotent — skips already-pulled, commits per profession):
```
caffeinate -disu bash pipeline/discover/gap_harvest/gap_pull.sh
```

## Next steps, in order

1. **Finish the pull** (wait, or resume as above). Done when the count hits ~510
   (minus genuine dead URLs).

2. **Cleanup dead + wrong-level cells:**
   ```
   python -m pipeline.discover.gap_harvest.cleanup            # report
   python -m pipeline.discover.gap_harvest.cleanup --relocate # re-find them (web_search)
   ```
   Then re-write targets for the relocated cells and re-pull them (small set).

3. **Extract the gap corpora** (do this AFTER step 2's relocate re-pull — cleanup gates ALL
   pulled cells, including the ~220 already done, not just the remaining pull). For every
   profession with new gap corpus: `clean_text → trim_state → extract_state_batch submit
   --queue <queue>`. Regenerate the queue (grows as the pull completes; excludes relocate
   cells):
   ```
   python - <<'PY'
   import json, os
   wl = json.load(open('pipeline/results/gap_harvest/pull_worklist.json'))
   reused = json.load(open('pipeline/results/gap_harvest/reused.json'))
   reloc = set(json.load(open('pipeline/results/gap_harvest/relocate_worklist.json')))
   aud = json.load(open('pipeline/results/gap_harvest/reuse_audit_2026-07-06.json'))
   skip = reloc | {f'{p}/{s}' for g in ('repull_degenerate','review_empty')
                   for p,ss in aud[g].items() for s in ss}
   # harvest cells = pull_worklist-that-got-pulled UNION reused (NOT a bare pull_worklist scan —
   # that silently drops all ~237 reused cells; NOT a glob of text/ — that pulls in pre-harvest backlog)
   cells = {(p,s) for p in wl for s in wl[p] if os.path.exists(f'pipeline/results/text/{p}/{s}.json')}
   cells |= {(p,s) for p in reused for s in reused[p]}
   q = {}
   for p,s in sorted(cells):
       if os.path.exists(f'pipeline/results/structured/{p}/{s}.json') or f'{p}/{s}' in skip: continue
       q.setdefault(p, []).append(s)
   json.dump(q, open('pipeline/results/queues/gap_harvest_ready.json', 'w'), indent=2)
   print(sum(len(v) for v in q.values()), 'cells staged')
   PY
   ```
   Consistency-gated — if the gate flags cells, re-extract just those (see the Jul-5
   republish for the pattern). Budget ~$0.20/cell (~$150–210 for the full harvest).

4. **De-dupe year-versioned corpora (optional tidy).** `corpus_drift` shows ~90 cells with
   duplicate year-versioned chapters (benign, 0 HOST_DRIFT). Apply
   `pull_text._dedupe_year_versions()` to those `sections` in place, then re-clean/trim/extract
   the affected cells. Low priority.

5. **Publish (product decision).** Only the original 7 professions are live. Making a
   held-out gap profession visible is a separate `build_frontend --profession X` (free,
   deterministic) — decide with the team which to surface.

6. **Flywheel round (grow the census).**
   ```
   python -m pipeline.discover.gap_harvest.discover           # find unknown occupations
   # add the real in-scope ones to professions.yaml
   python -m pipeline.discover.gap_harvest.locate --profession X --states …   # for each new one
   # write targets -> reuse -> pull -> extract
   ```
   Loop until a round finds <~5 new in-scope occupations. Exclude court-regulated
   (attorney/bar admission). The 8 parked professions are the current round's pull backlog.

## Deferred decisions

- The **128 recovered nulls** (exemption/certification chapters) — REVIEWED 2026-07-06,
  see `results/gap_harvest/recovered_nulls_review.json`. **~38–56 already on disk** (chapter
  held under another profession; 38 exact-URL, 56 with year/section-canonical matching — all
  16 optician→optometry cells confirmed held, optician law fully captured by the published
  optometry corpus) → `reuse` them (free), don't pull. **~72–90 not held**, overwhelmingly
  *sibling chapters* (radiologic_technology → the state RADIATION act, bail_bond_agent → the
  BAIL code) and broad code / general-provisions chapters concentrated in building_inspector
  (11), court_reporter (9), forester (6), public_weighmaster (6). So the open call on those is
  a PRODUCT decision — do these held-out professions
  warrant their own extraction when their law is a sibling profession's chapter? — not an
  automatic pull. Do NOT bulk-pull the 128.
- Which held-out professions to **publish**.
- **Disk** (unrelated to utah): user to clear ~19 GB of caches (`~/Library/Caches`, `~/.cache`).

## Guardrails
- ONE CDP process at a time; never two committing git processes at once (lock-retry the commit).
- `web_search` tool must be on the Anthropic key (absent in some headless runs).
- Batch extraction is the default for re-runs (durable, ~50% cheaper).
