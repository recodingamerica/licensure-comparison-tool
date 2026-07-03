# Playwright "cannot switch to a different thread" during bulk Justia harvest

**Status:** open. Mitigation in place (one state per process); root cause unconfirmed.
**Who/what:** `utah` pipeline, `pipeline/ingest/pull_text.py`, driven by
`pipeline/ingest/refresh_corpus.py`. Fetching law.justia.com through a CDP-attached
hand-started debug Chrome (Playwright **sync** API over `connect_over_cdp`).

---

## Symptom

During a long bulk re-pull (hundreds of chapters across ~50 professions × ~14 states),
a large fraction (~40%) of chapter fetches return **0 sections**, even for chapters
that demonstrably have content. The underlying error (surfaced once we logged it):

```
fetch https://law.justia.com/codes/washington/title-18/chapter-18-08/:
  error: cannot switch to a different thread (which happens to have exited)
```

This is a **Playwright sync-API greenlet/thread error**, not a network/Cloudflare/parse
error.

## Key evidence

1. **Isolated fetches always succeed.** Running the exact same URL in a fresh
   one-off process returns full content every time (SD ch-05 → 35 sections, WA 18.06
   → 19, VA ch-11 → 56). So: not a Justia gap, not a parser bug, not a bad URL.
2. **The failure is positional within a process, not per-URL.** In a multi-state
   `refresh_corpus --profession architecture --states WA,VA` run:
   - The **first** state processed (VA, chapter-4) pulled fully — **24 sections**,
     i.e. the chapter walk + ~24 section fetches all succeeded.
   - **Every** fetch for the **second** state (WA) then failed with the thread error,
     including retries.
   So the greenlet thread **survives the first state's ~25 fetches and dies at/after
   the transition to the second state's `pull_state` call.**
3. **Not Cloudflare.** The user never sees a "Just a moment" challenge in normal
   browsing; only ~3 of ~27 zeros had a challenge marker. cf_clearance is fine.
4. **Retrying on the same connection cannot recover it.** We added (a) a retry-on-zero
   and (b) `_refresh_browser_page()` (open a fresh *tab* in the same context). Both
   failed — the fresh tab is created *through the same dead greenlet*, so
   `ctx.new_page()` and every subsequent op raise the same thread error. (Reverted.)
5. **caffeinate helped but didn't fix it.** Wrapping the run in `caffeinate -i -s`
   removed a *separate* earlier failure mode (Mac idle/system sleep freezing the
   process), but the thread error persists while awake.

## Leading hypotheses (for review)

1. **macOS App Nap / background throttling when the user walks away.** ⭐ The user
   observes failures correlate with stepping away from the machine. "A thread which
   happens to have exited" is consistent with the OS suspending/killing the
   Playwright **node driver** subprocess (or its I/O thread) when the owning app
   loses focus / the machine idles, even with `caffeinate -i -s` (which prevents
   *sleep* but not App Nap / QoS throttling of a background process). If the node
   driver thread is reaped, the sync greenlet can't switch to it.
   - Worth testing: `defaults write NSGlobalDomain NSAppSleepDisabled -bool YES`, or
     launching under `caffeinate -disu`, or wrapping the python process so App Nap is
     disabled for it; and reproducing with the window focused vs. backgrounded.
2. **A signal handler corrupting the sync greenlet.** `_get_browser_page()` registers
   a `signal.signal(SIGTERM, …)` handler to close the debug tab on `timeout`-kill.
   Playwright's sync API is greenlet-based and is known to be fragile to signals
   delivered mid-greenlet. Even without a kill, interaction between the signal module
   and the greenlet run loop across a `pull_state` boundary is a suspect.
   - Worth testing: remove the SIGTERM handler (rely on atexit / the flock + tab
     self-heal) and see if multi-state processes stop dying.
3. **`sync_playwright()` object reused across a boundary it shouldn't be.** The
   browser/connection is cached in a module global (`_BROWSER`) and reused across
   `pull_state` calls. If anything (a nested loop, a `wait_for_timeout`, a GC of a
   page) causes the greenlet's parent thread to change or exit between states, the
   next access fails. A full teardown+reconnect (`pw.stop()` then a fresh
   `sync_playwright().start()`) per state may be required — which is essentially what
   the "one process per state" mitigation achieves cheaply.

## Current mitigation (in place)

`scratchpad/master_overnight.sh` now calls `refresh_corpus` **once per (profession,
state)** instead of per-profession-multi-state. Since the first state in any process
always succeeds, a fresh short-lived process per state sidesteps the between-state
death. Trade-off: extra process/browser-attach startup per state (~a few seconds).
**Open question:** does the thread also die between *chapters within one state* when a
state maps to multiple chapters? Not yet observed (the repro state had one chapter),
but if so, the fix must go deeper (teardown+reconnect per chapter, or fix the root
cause).

## Minimal repro

```
# from repo root, with a debug Chrome on 127.0.0.1:9222 (challenge cleared)
JUSTIA_CDP_URL=http://127.0.0.1:9222 \
  pipeline/.venv/bin/python -m pipeline.ingest.refresh_corpus \
  --profession architecture --states WA,VA
# => VA pulls fully; WA fails every fetch with the thread error.
```

## Relevant code

- `pipeline/ingest/pull_text.py`: `_get_browser_page()` (CDP attach, single cached
  page in `_BROWSER`, SIGTERM handler), `fetch_via_browser()` (the failing fetch),
  `_close_browser()`.
- `pipeline/ingest/refresh_corpus.py`: `refresh_item()` → `pull_with_timeout()` →
  `pull_text.pull_state()` per (profession, state).
- Env: macOS (Darwin), Playwright sync API, `connect_over_cdp`, Chrome 149 debug
  instance started by hand with `--remote-debugging-port=9222`.
