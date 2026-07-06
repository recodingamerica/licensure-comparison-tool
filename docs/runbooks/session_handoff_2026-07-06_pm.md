# Session handoff — 2026-07-06 PM

Written so a fresh session (after `/clear`) can continue without re-deriving state.

## TL;DR
- A **gap-harvest pull is running in the background** and survives `/clear`. Do NOT
  relaunch it blindly — check first (`pgrep -f gap_pull.sh`).
- This session shipped the repo-review **P0/P1 fixes (6 commits)**, **hardened the harvest
  driver** against an orphan-cascade, and **skipped over-broad cells**.
- The progress **monitor stops at `/clear`** (session-scoped); re-arm it if you want pings.

## Background processes (survive /clear — they're detached)
- **Harvest driver:** `caffeinate -disu bash pipeline/discover/gap_harvest/gap_pull.sh`.
  Log: `pipeline/results/gap_harvest/gap_pull_resume2.log`. Resumable/idempotent (skips
  already-pulled, commits per profession). Check: `pgrep -f gap_pull.sh`.
- **Debug Chrome (CDP):** `127.0.0.1:9222`, `--user-data-dir=/Users/abigailhaddad/chrome-debug`.
  If it dies, restart durably:
  ```
  open -na "Google Chrome" --args --remote-debugging-port=9222 \
    --user-data-dir=/Users/abigailhaddad/chrome-debug --no-first-run --no-default-browser-check \
    https://law.justia.com/codes/kansas/
  ```
  Verify it can actually fetch: `python -c "from pipeline.ingest.refresh_corpus import chrome_live; print(chrome_live())"` → must be `True`.
  (Do NOT do fast manual Playwright fetches — they bypass the 3s per-host delay and provoke Cloudflare.)
- **Progress monitor** (`bwpq65pvu`): session-scoped, so it ends on `/clear`. Re-arm with a
  Monitor polling `git log` for `gap-harvest` commits if you want progress pings.

## Committed this session (6 commits, layered on the live gap-harvest chain via partial-commits)
- `2ed57052` client handoff layer + provenance freshness + P0 review fixes
- `deaec19d` P1 review cleanup: docs precedence, config map, deploy runbook, CI, remove dead workflows + 999 logs
- `ae2cfce3` add dashboard render test
- `ae36b00d` retire superseded CDP batch drivers; point docs at refresh_corpus + committed modules
- `f9114744` add client_refetch.md runbook
- `fa282fa4` gitignore *.egg-info/

Full punch list these came from: `docs/runbooks/repo_review_2026-07-06.md`.

## Harvest state
- Worklist: `pipeline/results/gap_harvest/pull_worklist.json` — ~183 cells remaining when this was written.
- `gap_pull.sh` now has a **`kill_pull_orphans`** step after each cell: `timeout` kills
  refresh_corpus but leaves its Playwright browser-child alive, and an orphaned child wedges
  the shared CDP Chrome for every later cell (the cascade that stalled the whole run earlier
  today). Reaping it means a slow cell only costs itself. **Validated:** athlete_agent/KY
  (437 sections) timed out and the driver rolled cleanly to the next cell.
- Per-cell timeout is 900s. At the 3–4.8s per-host delay, a cell over ~230 sections times out
  and produces **nothing** (the all-or-nothing no-wipe guard — a partial corpus is worse than
  a missing one). Consider lowering the timeout to ~8 min so mis-mapped mega-chapters fail fast.

## Over-broad / mis-mapped cells (need a NARROWER mapping, then re-pull)
- Logged in `pipeline/results/gap_harvest/over_broad_needs_remap.json` (removed from the worklist):
  insurance_producer/KS, private_investigator/WI, security_personnel/WI, public_weighmaster/ND,
  public_weighmaster/MD, wholesale_drug_distributor/CT, alcohol_drug_counseling/HI (ch321 = 304 sec).
- **PLUS `athlete_agent/KY`** (killed mid-pull this session): mapped to Kentucky ch-164 "State
  Universities and Colleges" = **437 sections**. The real athlete-agent law is the Uniform
  Athlete Agents Act at **~KRS 164.6901–164.6935** — re-map to just that section range, not the
  whole chapter. Add it to the remap file.
- Root cause: the `gap_locator` (web_search) step over-picks broad whole-chapters more often
  than a label scan catches. A **section-count-based over-broad guard** (skip/flag targets that
  expand to >~200 leaf sections) would catch these before they waste a timeout.

## Pending / next steps
1. **Commit the harvest-cleanup changes** (this session left them, committed alongside this doc):
   `gap_pull.sh` (orphan-reaper), `pull_worklist.json` (over-broad removed), `over_broad_needs_remap.json`.
2. **Let the harvest finish**, then re-map the over-broad cells and re-pull them narrow.
3. **When corpora land:** run clean → trim → extract via `pipeline.client.run` (the committed client path).
4. **Deferred review decisions** (see repo_review doc): extraction spend (~$150–210), does OPLR
   self-deploy to Vercel, kill-or-keep the Postgres path.

## Do NOT commit (not this session's work — leave for the harvester/owner)
- `docs/runbooks/gap_harvest_next_steps_2026-07-06.md`, `pipeline/config/mapping_overrides.yaml`
  (pre-existing uncommitted edits), and all `pipeline/results/**` data the harvester writes.
