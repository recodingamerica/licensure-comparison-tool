# CDP re-pull — new failure modes (2026-07-09)

Read `docs/runbooks/cdp_repull_lessons_2026-07-02.md` first — this is an addendum
from an overnight tier3_absence gap-fill run that failed completely (0 real
pulls landed across ~74 queued states, 0 corruption) plus the morning-after
debugging.

## `refresh_corpus` silently discards EVERY successful pull of a brand-new
## (profession, state) pair — FIXED

`refresh_corpus.file_changed()` used `git diff --quiet -- <path>` to decide
whether a re-pull actually fetched anything new. **`git diff` (no `--no-index`)
silently ignores untracked files** — it only compares tracked paths against
the index/HEAD, so it reports "no differences" (exit 0) for an untracked file
regardless of what's inside it. `refresh_corpus` was built and tested for the
*annual re-pull of an already-committed corpus* (catching recodifications) —
that blind spot never mattered until it was pointed at genuinely NEW
(profession, state) pairs with no prior commit, which is exactly what an
81-state tier3-gap-fill backlog is made of.

Result: every real, successful fetch last night (confirmed after the fact —
the correct chapter/section URLs were found, real substantive statute text was
written to disk, e.g. `health_facility_admin/AZ` got all 18 correct sections)
got classified `NOCHANGE` and the file was left sitting uncommitted in the
working tree. The circuit breaker then read 3 consecutive `NOCHANGE`/`EMPTY`
results as "Chrome died" and aborted each profession after 1-3 states — so the
whole ~74-state backlog "finished" in ~25 minutes with zero commits, looking
exactly like a real Chrome-death cascade.

**Fixed**: `file_changed()` now checks `git ls-files --error-unmatch` first —
an untracked path is unconditionally treated as changed (there's no baseline
to diff against, so any written content is real progress).

**Takeaway for next time**: `refresh_corpus` is for re-checking corpora you
already have. For first-time pulls of brand-new profession/state pairs, use
plain `pull_text` (supervised) — don't reach for `refresh_corpus` just because
it sounds more "hardened." Its circuit-breaker/completeness gates are real
value-adds for the annual-recodification use case, but the NOCHANGE bug meant
they were actively harmful here, silently eating good data.

## Chrome auto-update mid-run — happened again, still not prevented

The debug Chrome auto-updated overnight (150.7871.100 → 150.7871.115) while
the unattended `refresh_corpus` run was going — this is the exact failure
mode #3 already flagged in the 07-02 doc as "REAL wedge, NOT yet prevented."
It happened again because nothing changed to prevent it. Combined with the
`file_changed()` bug above, it's unclear how much of last night's cascade was
*actually* caused by the auto-update vs. just triggered by the NOCHANGE bug —
both were present simultaneously and both independently would have caused a
NOCHANGE-style false negative.

**Still unmitigated. If running an unattended overnight CDP job**, launch
Chrome with component-update-suppressing flags first (not yet tried in this
repo — worth doing before the next overnight attempt):
```
--disable-background-networking --disable-component-update
```
(unverified whether this fully blocks Chrome's self-updater; test before
trusting it for another overnight run.)

## Intermittent `Browser.setDownloadBehavior` / "Browser context management is
## not supported" CDP protocol error — UNRESOLVED, not a Playwright version fix

After relaunching Chrome fresh this morning, `pull_text`/`collect_section_targets`
intermittently failed with:
```
Protocol error (Browser.setDownloadBehavior): Browser context management is not supported.
```
and separately:
```
It looks like you are using Playwright Sync API inside the asyncio loop.
```
Ruled out:
- **Not a stale/dead Chrome** — `curl :9222/json/version` responded fine, and
  the failing calls were interleaved with calls that succeeded and fetched
  real content (confirmed by watching the actual browser tab navigate to
  correct, substantive Justia pages).
- **Not fixed by relaunching Chrome alone** — tried 3 times, same intermittent
  pattern each time (works 0-1 times, then fails repeatedly).
- **Not a Playwright version issue** — upgraded 1.58.0 → 1.61.0, error persisted
  identically. Reverted back to 1.58.0 (the version with health_facility_admin's
  one fully-clean 6-state run this morning) since the upgrade showed no benefit
  and there's a plausible-but-unconfirmed chance it made things *more* flaky.

**Current best guess (unconfirmed)**: something about how `pull_text.fetch()`
reuses vs. creates browser contexts (`browser.contexts[0] if browser.contexts
else browser.new_context()`, `pipeline/ingest/pull_text.py:193`) interacts
badly with this specific Chrome build when called repeatedly in quick
succession — but a fully clean 6-state run happened on the SAME Chrome
build+Playwright combo just an hour earlier, so it isn't a hard version
incompatibility. Possibly a resource/timing race that gets worse the more
CDP connections have been opened+closed in a session. Not root-caused.

**Practical mitigation that DOES work**: when a pull hits this error, kill all
`chrome-debug` processes (`pkill -f "user-data-dir=.*chrome-debug"`), confirm
the port is free (`curl :9222/json/version` should fail), relaunch fresh, and
retry. It doesn't fix the underlying flakiness permanently, but each fresh
relaunch does get you a clean window to make real progress in. Budget for
needing to do this multiple times per session right now, not zero.
