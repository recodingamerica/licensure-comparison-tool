# CDP re-pull — failure modes & lessons (2026-07-02)

Hard-won during the uncapped Justia re-pull of 30 corpora. Read this before any
large CDP harvest, and fold every item into `refresh_corpus` when it's built.

## The one rule: ONE scraper at a time

A single `flock` at `/tmp/justia_cdp_pull.lock` serializes pulls — concurrent
pulls on one debug Chrome garble corpora. The flock is released when the holding
process dies, so a cleanly-killed pull frees it. Verify with `lsof
/tmp/justia_cdp_pull.lock` (no output = free).

## Wedge diagnosis — three DIFFERENT causes that all "look stuck"

A pull that sits with no log output is NOT necessarily hung. Distinguish:

1. **`pages[0]` hijack (FIXED, commit bff6d0f).** The CDP fetch used to reuse
   `ctx.pages[0]` — whatever tab was already open. If that was a `chrome://`
   page (newtab, or `whats-new` after an auto-update), `page.goto()` from a
   chrome:// URL to https Justia **hangs**, and it also hijacked/closed the
   user's visible tab. Fixed: the pull now opens its own `ctx.new_page()`.
   Symptom was: no Justia tab ever appears; stuck right after "matched N rows".

2. **Official-source slowness (not a wedge).** `pull_md` / `pull_nv` / etc. walk
   a state's official API section-by-section at 3s each and DON'T log per
   section — 10-15 min of silence is normal. A "silent log" monitor will
   false-flag these. Check the faulthandler traceback (below) — if it's in
   `pull_md`/`polite_sleep`, it's slow-not-wedged. (MD/NV are now flipped to
   Justia, so this is rarer — but other official states remain.)

3. **Chrome auto-update mid-run (REAL wedge, NOT yet prevented).** Chrome's
   updater restarted the browser (.199→.201) underneath a running pull, breaking
   its CDP connection → indefinite hang, `whats-new` tab appears. **Mitigation
   until refresh_corpus handles it:** fully quit + relaunch the debug Chrome
   before a long run; consider launch flags to suppress component updates.

### Definitive wedge check: faulthandler traceback

```
PYTHONFAULTHANDLER=1 python -m pipeline.ingest.pull_text ... &  # (with JUSTIA_CDP_URL)
sleep 25; kill -ABRT $!    # dumps the exact stuck line
```
This ends the guessing — it prints the precise function the process is sitting
in (goto / polite_sleep / connect_over_cdp / flock).

## The no-wipe guard is ALL-OR-NOTHING (open gap)

`pull_text`'s overwrite-guard and pull_umbrella_text's cache guard only refuse a
**totally empty** pull. A per-chapter partial (chapter A full, chapter B empty,
total > 0) still writes/commits. When validating a re-pull, check EACH declared
chapter has sections — don't trust the total. (refresh_corpus must do this.)

## Real fetch vs stale cache — a "success" can be fake

If Chrome is down/wedged, a `--force` pull fetches nothing and the no-wipe guard
keeps the OLD (capped) data — which then looks like a successful pull. Detect a
REAL fetch by `git diff --quiet <file>`: a re-pull of a known-incomplete corpus
MUST change the file. Unchanged = nothing fetched (or already complete — for a
capped item, treat unchanged as suspect). The `.scratch/overnight_repull.py`
driver encodes this as `MISS-nochange`.

## Chrome liveness — the endpoint lies

`curl :9222/json/version` can be unresponsive while a pull drives the browser,
and can respond even when Chrome is in a bad post-update state. The reliable
check is a playwright `connect_over_cdp` + `new_page` + goto Justia + confirm the
title isn't "just a moment". The `.scratch` driver's `_chrome_live()` does this
at startup and the run aborts loudly if it fails.

## Throttle (block-risk, FIXED)

`pull_umbrella_text` used to import a flat 0.3s delay and ignore
`PULL_HOST_DELAY` — hammering Justia. Now BOTH pullers route through
`polite_sleep` (env-aware + 60% jitter) with the default in
`config/limits.yaml` (`fetch.per_host_delay_seconds: 3.0`).

## Reading the status/monitor

- A pull committing every ~10 min while another process runs `git`
  concurrently can hit `.git/index.lock` — DON'T run two committing processes
  at once (this includes committing subagents). Sequence them.
- caffeinate: wrap the driver in `caffeinate -is <cmd>` so the Mac stays awake
  exactly as long as the run.
- `git diff --stat pipeline/results/` after a `match_profession` run must be
  EMPTY (byte-identical) — the reproducibility gate.

## `refresh_corpus` — the durable, tested re-pull (supersedes the throwaways)

`pipeline/ingest/refresh_corpus.py` folds every lesson above into a tested command.
It **replaces** `.scratch/overnight_repull.py` and the `_cdp_*` batch drivers — those
can now be deleted.

```
python -m pipeline.ingest.refresh_corpus --profession X [--states A,B]
       [--all-professions] [--force] [--report-only]
       [--run-id ID] [--item-timeout SECONDS] [--breaker N]
```

It re-pulls the FROZEN url map (`results/profession_index/<prof>.json`) via
pull_text's `pull_state` (it does NOT reimplement fetching) and gates every commit:

- **Chrome-live precheck** (once at start, over CDP — the `/json/version` endpoint
  lies). Dead/challenged Chrome ⇒ abort before pulling.
- **Per-chapter completeness** (the gap fix): the all-or-nothing guard only refuses a
  *totally* empty pull. refresh_corpus attributes each section to its mapped chapter
  (canonical-path prefix; single-chapter states attribute all sections to that
  chapter, covering official-source url-rewrites) and if ANY declared chapter came
  back with 0 sections it records `PARTIAL` and reverts — never commits a partial.
- **Real-fetch detection**: `git diff --quiet` the corpus. Unchanged after a re-pull
  ⇒ `NOCHANGE` (Chrome down/wedged, or already complete) — NOT counted as success.
- **Mid-run CDP-death resilience**: a pull that raises a CDP/connection error
  re-checks Chrome; recovered ⇒ retry the item ONCE; still dead ⇒ abort the whole run
  loudly. A per-item wall-clock timeout (`--item-timeout`, default 2400s) stops a
  genuine hang from wedging the run forever.
- **Circuit breaker**: `--breaker` (default 3) consecutive non-productive results ⇒
  abort (Chrome likely died).
- **Per-item commit** (`git add <file>`, never `-A`), message naming prof/state +
  old→new section counts.
- Writes a status JSON (`results/refresh_status_<run-id>.json`).

### The year-over-year diff report (recodification detection)

After a run (and via `--report-only`, which rebuilds from the last status without
fetching), it writes `docs/reports/refresh_diff_<runid>.md`, comparing each re-pulled
corpus against its **pre-refresh committed** version (`git show HEAD:<file>` captured
BEFORE the item commits). Severity buckets:

- **likely recodification (chapter vanished)** — a chapter present last year is absent
  now (renumbered/repealed). **Needs human eyes.**
- **suspicious shrink (chapter dropped >30%)** — a chapter lost most of its sections.
- **grew** — more sections / a new chapter appeared (benign).
- **minor delta** / **no change** — noise.

## Golden tests move with the data

`tests/test_assign_umbrella_scope.py` GOLDEN_COUNTS freeze per-state scope
counts. An uncapped umbrella re-pull legitimately changes them — recompute with
`assign_for_state(ST)['scope_source_counts']` and update the golden as a REVIEWED
change (in the commit message), never silently.
