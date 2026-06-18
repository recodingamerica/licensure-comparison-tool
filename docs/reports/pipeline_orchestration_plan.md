# Plan: one-click pipeline orchestration

**Status:** drafted 2026-06-18. Two target capabilities:
1. **Run a new profession** end-to-end with one command.
2. **Update all statutes** (annual refresh from Justia / legis.state.pa.us) with one command.

Both have a designed home in the repo; #1 is a stub to finish, #2 needs a new
guarded refresher because the naive version corrupts data.

## What already exists (building blocks)

| Piece | State | Role |
|---|---|---|
| `pipeline/run.py` | **stub** ("not yet implemented") | intended canonical end-to-end orchestrator for one profession |
| `pipeline/run_for_new_matches.py` | works | runs pull→clean→trim→extract→publish for newly-*matched* (state,prof) pairs via a coverage diff |
| `pipeline/ingest/pull_text.py` | works | fetch + parse; `PER_HOST_DELAY=1.2s`; **writes `text/<state>.json` unconditionally** (no validation-before-overwrite) |
| `pipeline/publish/refresh_all.py` | works | incremental publish; fingerprints `structured/`+`map_prep/`, rebuilds only changed professions; `--deploy` runs `vercel --prod`; consistency gate |
| `pipeline/extract/extract_state_batch.py` | works | durable, ~50%-cheaper batch extraction (submit/poll) |
| `pipeline/map_prep/refresh.py` | works | batched map_prep (apply + per-state) + delegated per-item bucketing |
| `pipeline/eval/check_consistency.py` | works | cross-field invariant gate (also wired into refresh_all) |

Pipeline stage order (each reads the previous dir):
`hierarchy → match → pull → clean → trim → discover → extract → map_prep → build_frontend`.

## Path 1 — one-click new profession

**Mostly a wiring job.** Every stage already runs standalone; finish `run.py` to
chain them for one profession.

Steps:
1. Implement `run.py` to shell each stage in order for `--profession X`, with
   `--steps a,b,c` to resume/skip and `--states` passthrough. Stages:
   `match → pull → clean → trim → discover → extract → map_prep → publish`.
   (`hierarchy` is profession-agnostic + cached; skip unless missing.)
2. Stop-on-error + a per-stage summary line; honor the existing batch path for
   extract when >2 states.
3. End with a **coverage report**: states matched vs not, and which matched-but-
   empty (the `pull` produced 0 sections) — the to-do list for manual config.

**Non-automatable caveat (be explicit in the output):** a brand-new profession
hits states where it is **buried/embedded** (e.g. dietetics inside PA's Nursing
Law) or on a **non-Justia source** (PA `pa_legis`, IL ILCS blobs). Those need a
`state_structure.yaml` entry + the "which sections" judgment (keep-lists,
embedded scoping). `run.py` can't invent those — it should *surface* them as
gaps, not silently miss them (the coverage report above).

## Path 2 — one-click annual statute refresh

**The hard one.** A naive "re-pull everything from Justia" is exactly what the
repo warns against: Justia rate-limits/blocks bulk sequential fetches (we hit IL
403s on 2026-06-18), and `pull_text` would then **overwrite good committed
corpora with the 403/empty pages**. So the refresher must be guarded, throttled,
and resumable.

### Prerequisite (do FIRST): validation-before-overwrite guard
`pull_text` currently writes the corpus unconditionally. Before any bulk refresh:
- Pull to a **staging** path, not over `text/<state>.json` directly.
- **Validate** the new pull: HTTP 200, non-empty body, section count and total
  chars `>= 0.8×` the committed corpus (tunable). Reject 403/empty/partial.
- **Promote** to `text/` only if the new pull is as-good-or-better; otherwise keep
  the committed corpus and **log a "refresh skipped — degraded" warning**.
- This makes a refresh *safe to re-run* — a blocked host degrades to "no change",
  never to corruption.

### The refresher
6. Throttle + backoff: per-host rate limit, exponential backoff on 403/429, one
   host at a time. PA (`legis.state.pa.us`) is politer but same discipline.
7. **Resumable / durable**: a manifest of (profession, state) → last-good-pull
   hash + timestamp; the run is restartable and skips already-refreshed pairs
   (it *will* get blocked partway). Reuse the `refresh_all` fingerprint pattern.
8. Resolve **year-versioned URLs to current** (#6/#7) — drop the year segment or
   take the latest; `_dedupe_year_versions` already prefers unversioned/latest.
9. **Diff-driven re-extract**: only statutes whose text actually changed go to
   `extract_state_batch`. Unchanged law = no re-pull-cost, no re-extract-cost.
10. Then `map_prep.refresh` (changed professions) → `refresh_all --deploy`.

### Cost / cadence
Full re-extract of everything is the dominant cost; the diff in step 9 is what
keeps an annual refresh affordable (most statutes don't change year to year).
Run it as a slow background sweep, not a single blocking command.

## Recommended sequencing
1. **Guard first** (the prereq) — it's small and de-risks everything downstream.
2. **Finish `run.py`** (Path 1) — high value, low risk, mostly wiring.
3. **Build the refresher** (Path 2) on top of the guard + the diff/batch/fingerprint
   pieces that already exist.

## Open issues to file
- "Finish `pipeline/run.py` end-to-end orchestrator (Path 1)."
- "Guarded annual statute refresh: validation-before-overwrite + throttle/resume (Path 2)."
