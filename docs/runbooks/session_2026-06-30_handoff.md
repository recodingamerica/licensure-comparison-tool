# Session handoff — 2026-06-30 (pick up here next time)

39 commits ahead of origin, **all local/unpushed**. Suite **429 passing** (was 378). Tree clean
except the running grind's in-flight text.

## ⭐ The headline discovery
**Justia is reachable** — the wall is a Cloudflare *fingerprint* challenge, not an IP/rate block,
and **CDP-attach to a hand-started debug Chrome clears it** (proven: KS 0→21 sections). This
invalidates the premise behind a lot of prior decisions (the official-source migration, the
"never re-fetch" doctrine, the "effectively-empty = unrecoverable" exclusions). `CLAUDE.md` updated.

## Grind: DONE (overnight, 2026-07-01 02:49)
**133 of 134 recovered (99%)** across 23 professions; raw-empty backlog **143 → 9**;
ready-to-extract **1268**. Only failure: `professional_geology/MD` (an official-source MD
state — belongs to the official→Justia shift bucket, not a Justia problem). The Chrome is
now **free** for the phase-2 / official-shift work below.

## First thing next session
1. **Push** the ~62 commits (grind added ~23): `git push`.
2. (optional) mop-up re-run — should be a no-op now: `… _justia_repull.py` (resumable).

## Gated on the CDP Chrome (do when it's free / up)
- **Phase-2 index-only re-pull** (11 Justia stubs that pulled only the chapter-index page):
  `… _justia_repull.py .scratch/jul1_prep/index_only_repull.json` (driver already treats index-only as not-done).
- **Official→Justia shift experiment** (8 failing WA/CT pairs in `.scratch/jul1_prep/official_repull_shift.json`):
  delete those states' `chapter_url_template`/`source` in `state_structure.yaml` → `match_profession` emits the
  stored Justia URLs → re-pull via CDP. Reversible (commit first). **Keep ~12 working official states as-is** —
  re-pulling 580 good corpora buys nothing. **PA is the ONLY state not on Justia** — it stays on legis.state.pa.us.

## Gated on the API (Jul-1+, needs LLM)
- **Bulk extract backlog (1261 ready)** — `.scratch/jul1_prep/RUNBOOK.md`: pilot insurance_producer →
  published refresh → chunks. `submit` now runs the **preflight gate** (refuses on missing-schema/empty/poisoned).
- **WA umbrella rollout** — re-pull→clean→trim→extract the 6 WA health profs so Ch 18.130 lands
  (`docs/runbooks/wa_umbrella_mechanism.md`).
- **⭐⭐ THE BIG ONE — 122 nationwide umbrella-missing chapters.** `corpus_status umbrella` found shared
  general-provisions chapters cited by dozens of professions but never pulled: **IN 25-1 (36 profs), SD 1-26
  (31), NM 61-1 (29), MS 93-11 (27), CO 12-20, GA 43-1, SC 40-1…**. These hold discipline/renewal/conduct
  for ~58 professions. Fill with the new state-level `umbrella:` mechanism: per (state, chapter), pull (CDP) +
  list the citing professions + re-extract. See memory `project_completeness_blind_spot`. Biggest coverage win available.

## New tools shipped this session (all tracked + tested)
- **`corpus_status`** (`pipeline/eval/corpus_status.py`): `sync` (honest STALE_CLEAN by mtime + INDEX_ONLY /
  THIN / JUNK_AS_200 / CLEAN_EMPTY / CLEAN_GT_TEXT flags), `backlog` (--write-queues), `umbrella`.
- **preflight gate** (`pipeline/extract/preflight.py`) + `trim_state` `trim_degraded`/`--strict`.
- **field dictionary** — `generate_field_dictionary --all` → `docs/methodology/` + `web/public/methodology/`
  + the `/methodology/index.html` viewer linked from the app header; auto-regenerated in `refresh_all`.
  Methodology that tracks the code (Pydantic schema + prompts), with `data_as_of` freshness.
- **run-log** (`python -m pipeline._runlog`) — every stage records when it last ran.
- **state-level `umbrella:` mechanism** in `match_profession` (additive shared chapters; WA 18.130 live).
- **re-pull drivers** in `pipeline/results/batches/` (`_justia_repull.py`).

## Worklists staged in `.scratch/jul1_prep/` (gitignored)
`justia_repull.json` (134 — grinding), `index_only_repull.json` (11), `official_repull_shift.json` (8),
`effectively_empty_REPULL.json`, `RUNBOOK.md`, plus the bulk-extract queues.
