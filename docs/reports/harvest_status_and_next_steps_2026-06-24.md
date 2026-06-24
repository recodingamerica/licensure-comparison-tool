# Full-corpus harvest — status & next steps (2026-06-24)

> ## ⏯ RESUME HERE (post-/clear handoff — read first)
> We are running a **full-corpus CDP-Justia harvest of all ~75 professions** (the
> effort grew past the 4 trades). Pulling is free (no LLM); extraction is separate
> (Anthropic batch API). Branch: `data/pull-all`. Everything commits + pushes per
> profession. See also the general technique in the `scraping-cloudflare-cdp` skill
> and the prior plan `trades_official_sources_plan_2026-06-23.md`.
>
> **Check live state:**
> - `pipeline/.venv/bin/python pipeline/results/batches/_cdp_progress.py` → % done.
> - `pgrep -f _cdp_grind.py` → grind alive?  `pgrep -f 'caffeinate -dimsu'` → awake?
> - `ps -ax | grep pull_text` → what's pulling (must be ONE; never two on one Chrome).
> - `pipeline/.venv/bin/python pipeline/results/batches/_cdp_audit.py` → corpus health.
>
> **As of 2026-06-24 ~07:00:** ~21% pulled (≈350/1683 states). Grind paused briefly
> for an MD re-pull (see in-flight). Disk ~13GB free (guard pauses grind <3GB).

## The toolkit (`pipeline/results/batches/_cdp_*.py`)
- `_cdp_grind.py` — resumable harvest driver. ONE process, walks professions by
  gap (PRIORITY list bumps some first), pulls each profession's mapped-but-unpulled
  states, **commits per profession**. `pulled_states()` counts a state done only if
  it has ≥1 ok section (so failed/empty pulls retry). SECTION_CAP=250 per state.
  Run: `JUSTIA_CDP_URL=http://localhost:9222 PULL_HOST_DELAY=3 pipeline/.venv/bin/python pipeline/results/batches/_cdp_grind.py`
- `_cdp_downstream.py --profession P` — clean→trim→discover_schema(if missing)→
  extract (batch); excludes states already in a submitted batch (no double-spend).
- `_cdp_audit.py` — health: error/empty/thin(≤3)/cap-hit(==250)/silent-bad.
- `_cdp_xref_audit.py` + `_cdp_umbrella_resolve.py` — umbrella detection + URL resolve.
- `_cdp_progress.py` — % done.  `_cdp_monitor.sh` — event monitor (profession-done +
  health + %, grind death, 20-min hang, **<3GB disk guard**). Re-arm after it fires.

## Operational rules (learned the hard way)
- **CDP-attach to the user's real Chrome** beats Cloudflare (fingerprint wall, not
  rate/IP). User starts `Chrome --remote-debugging-port=9222 --user-data-dir=$HOME/chrome-justia-debug`
  and solves the first challenge; `cf_clearance` self-renews (~4s) — no manual babysitting.
- **ONE pull process per Chrome.** Concurrent pulls = garbled corpora.
- **Restarting the grind fragments the gap-order** — professions end up partially
  pulled (this is why pharmacy/veterinary were partial overnight). Minimize restarts;
  prefer letting it run. On resume it recomputes gap and finishes partials eventually.
- **Umbrella-merge / scoped re-pull of an already-pulled state needs `--force`** (the
  content-check skips states that already have sections).
- Keep the Mac awake: `caffeinate -dimsu -w <grind_pid>` (AC power only).

## Fixes shipped this session (all in `pull_text.py` → apply going forward)
- **MD empty → fixed** (`_MD_ARTICLE_CODE` gained `health-occupations`=gho + ghg/gin/...).
  MD routes through `pull_md` (GetNext API); was erroring "unknown article slug" for
  health professions. **Re-pull in flight; VERIFY it produced sections.**
- **ND thin → fixed** (`split_nd_blob` + wired into the `_inline_text` path). ND renders
  each chapter as one blob; now split on line-anchored `NN-NN-NN.` markers. 6 non-published
  ND corpora transformed offline (+year-dedup); future ND pulls split automatically.
- **NJ flat-title → scoped** via `section_slug_pattern` on title-45 (electrician 6→71,
  plumbing 2→37, construction 1→22, hvac →42).
- **Trades completeness**: umbrella general-provisions merged (UT 58-1, SC 40-1, CO 12-20,
  IN 25-1); 15 missed-match chapters added (DE/IL/MA/OH/WI plumbing, etc.); 4 bucket-2
  contractor chapters (MS/NC/OH/OR); MI recovered from umbrella-hidden Skilled Trades Act.
- **Audit gained**: thin-flag, and the proactive overnight audit surfaced the MD/ND issues.

## In-flight (as of handoff)
- MD re-pull (pharmacy/psychology/chiropractic/funeral/mental_health × MD), then the
  grind auto-resumes + re-caffeinates (script `/tmp/md_then_grind.sh`).
- Trade extraction batches submitted (msgbatch_0156Ce…, 011EWSs…, 0169A3Q…, +1) — poll
  with `pipeline.extract.extract_state_batch poll <id>` to write results, then verify
  (`check_consistency` + count `unverified` nodes).

## NEXT STEPS (prioritized)
1. **Verify MD re-pull worked** (gho fix). If MD now pulls sections, the empty MD
   professions are fixed; if still 0, debug `pull_md` (GetNext code / starting section).
2. **Finish trade extraction**: poll the 4 trade batches, write results, verify, commit.
   Then trades are *usable* (specific + umbrella + missed-match + NJ-scoped + MI).
3. **Cap bumps** (offline policy + Chrome re-pull): CA (construction/funeral/pharmacy),
   IN (pharmacy/plumbing), MO/NC (mental_health), TX (psychology) hit the 250 cap —
   legit large chapters truncated. Re-pull those with a higher `--limit-sections`.
4. **OK flat-title scoping**: like NJ but numeric ranges — fetch title-59 TOC to bound
   each trade's act (elec ~§1698, plumb ~§1013, hvac ~§1850.8), then `section_slug_pattern`.
5. **Umbrella-container pass** (big completeness win — recovers the ~1,989 "not licensed"
   that are umbrella-hidden): 17 container states mapped in
   `docs/reports/umbrella_containers_2026-06-24.json`. Recipe (proven on MI): fetch the
   container's act page → read article labels (they name professions) → config
   `profession/STATE.matched = [general articles] + [profession's article]` → pull.
   Highest yield: **MI Act 299** (recovers ~30 MI professions), then WV ch30, NM 61, VA ch3.
6. **Published-profession refresh** (live data — deliberate): apply the ND blob-split +
   MD gho fix to the 7 published professions' ND/MD, then re-clean/trim/extract/publish.
7. **Let the broad harvest finish** (~days at 3s). Partials (pharmacy/veterinary/mental_health)
   fill in as the grind continues; check the audit for re-pull candidates at the end.

## Known residual gaps (tracked, lower priority)
- SD silent-bad (api empties), scattered fetch-error sections (NJ/TX/OK/WA published).
- Local-only states (no state license, e.g. NY electrician) — correctly "not licensed".
- The `_repull_candidates.json` (from `_cdp_audit.py`) is the targeted re-pull list.
