# Session handoff — 2026-07-08

## What shipped this session

1. **Auto-generated technical documentation** (`pipeline/client/handoff_doc.py`) —
   builds `docs/handoff/technical_documentation.md`/`.pdf` and patches
   `README.md`'s status block, all numbers computed live from
   `pipeline.client.status.build()` (no hand-maintained counts). Section order
   (per client request): what this is → data sources & integrations → what's
   easy/cheap/hard → tools → costs → config files → trust the data. Rewrote the
   Cloudflare framing per user correction: it's not "a person clicks through a
   captcha," it's "the process dies for unclear reasons and needs a restart" —
   which is also what motivated the watchdog work below.

2. **Deleted all dormant/unverified official-source scraper code** from
   `pipeline/ingest/pull_text.py` (~1000 lines: UT/SD/NV/NY/CT/WA/VA/ME/ID/MO/MD/
   RI/VT/MT/AZ/FL parser functions + dispatch call-sites + orphaned helpers).
   User's call: "not confident we got that working," full removal not just the
   ones mentioned in the doc. `state_structure.yaml` comments scrubbed to match
   (kept the domain knowledge — which chapter is which trade — dropped the
   removed-parser mechanics).

3. **Gap-harvest reliability fixes** (root cause: large chapters structurally
   can't fetch inside a 15-min budget — not a Cloudflare block, per direct user
   correction):
   - `pull_text.py`'s over-broad guard now derives a hard leaf-count ceiling
     from `PULL_BATCH_TIMEOUT_SECONDS` when the caller opts in (0 = disabled,
     so manual/no-timeout pulls of legitimately-huge chapters aren't broken).
   - `gap_pull.sh` exports `PULL_BATCH_TIMEOUT_SECONDS=900` and adds a circuit
     breaker: after 3 consecutive misses a cell is parked (`parked_cells.json`)
     and dropped from the worklist instead of looping forever.
   - New `watchdog.sh`: polls every 5 min, relaunches `gap_supervise.sh` via
     `nohup caffeinate ... & disown` if it died, capped at 20 restarts.
   - Validated with a full overnight run: 120/120 succeeded, 14 correctly parked.

4. **Verified 4 more narrow.py "absence" findings via actual web research**
   (not just trusting the automated verdict) and added them to
   `pipeline/config/verified_absences.yaml`: `building_inspector/NE`,
   `optician/NE`, `optician/OK`, `opticianry/NE`. Ran
   `apply_verified_absences` — 27 records total now written with
   `source: verified_absence`.

5. **Two real bugs found and fixed** while wiring schema-discovery cost into
   the cost model (`pipeline/client/status.py`, `COST_SCHEMA = 1.00`):
   - `gap_harvest/reuse.py` wrote corpus files missing `state`/`profession`
     keys → 261-file `KeyError` on bulk clean. Fixed the writer, and added a
     path-derived fallback in `clean_text.py` as a second line of defense.
   - `client/run.py`'s clean/trim queue was wrongly schema-gated (used the
     `run` flag meant for extract), which meant a brand-new occupation could
     never get its first schema discovered. Split into `_queue_for_professions`
     (schema-gated, extract only) vs. `_queue_by_stage` (schema-independent,
     clean/trim).

6. **Client dashboard/run.py UX simplified** per direct request: removed the
   downloaded `my_queue.json` file entirely; every step (`clean`/`schema`/
   `trim`/`extract`/`publish`) now takes `--professions X,Y,Z` directly and
   auto-includes every state with actual work via a live status lookup. Cost
   estimates now always name the model they're priced against (previously
   ambiguous). `tests/test_client_run.py` rewritten around the new queue
   functions. Suite: 607 tests passing.

7. **Ran the real pipeline end-to-end**: clean → trim → discover_schema →
   extract for the 16 professions that were previously blocked on "no schema
   yet." Result: 273/285 cells extracted, $27.76 actual spend. Also cleaned
   and refreshed `professional_geology/OK` (0 → 1 section).

## In progress / needs attention next session

**Background pull job** (safe — `nohup ... & disown`, PPID 1, confirmed via
`ps`) still running as of this handoff:
```
pipeline/results/gap_harvest/pull_8_confirmed.log
```
Working through 8 narrow.py-confirmed cells: `athlete_agent/NE`,
`landscape_architecture/NE`, `auctioneer/NV`, `polygraph_examiner/CA`,
`polygraph_examiner/MA`, `public_weighmaster/KY`, `radiologic_technology/MI`,
`radiologic_technology/MN`. Status as of last check (16:44):
- `athlete_agent/NE` — done, committed (`47051f20`, 0→2 sections).
- `landscape_architecture/NE` — done, **4 real sections landed but NOT yet
  committed** (untracked file `pipeline/results/text/landscape_architecture/NE.json`).
- `auctioneer/NV` — done, safely came back 0→0 (no change). The chapter is 498
  leaf sections — this loop was launched *without* setting
  `PULL_BATCH_TIMEOUT_SECONDS`, so the over-broad *fetch-budget* guard wasn't
  active, but the pre-existing label-mismatch over-broad check still caught it
  and it self-protected (no timeout, no corruption, no charge). Confirmed safe
  after the fact — no intervention was needed.
- `polygraph_examiner/CA` — still running (~16 min elapsed at last check,
  narrow.py flagged this one as small, so the length is worth a glance but not
  alarming — likely a Cloudflare re-challenge pause mid-run).
- `polygraph_examiner/MA`, `public_weighmaster/KY`, `radiologic_technology/MI`,
  `radiologic_technology/MN` — not yet started.

**Next session should**: check `pull_8_confirmed.log` for completion, commit
`landscape_architecture/NE` (and any other real-content results) if not
auto-committed, and confirm nothing hung.

## Not yet started

- **6 cells never run through narrow.py**: `money_transmitter/NE`,
  `radiologic_technology/MA`, `loan_broker/NE`, `pawnbroker/MA`,
  `real_estate_broker/CA`, `insurance_producer/CA`. These were manually pulled
  out of an earlier worklist as "probably oversized" but never actually
  checked with narrow.py's live over-broad test.
- **`pull_worklist.json` (123 cells, ~24 professions) is stale** — many
  entries already succeeded via other paths and were never removed. Do not run
  it through `gap_pull.sh` blindly; reconcile against current `status.build()`
  output first.

## Uncommitted in the working tree (awaiting review, not yet asked to commit)

- `pipeline/config/verified_absences.yaml` (4 new entries, see above) +
  resulting `pipeline/results/structured/{building_inspector/NE,optician/NE,
  optician/OK,opticianry/NE}.json` written by `apply_verified_absences`.
- `pipeline/results/clean/professional_geology/OK.json` + provenance restamps
  across `professional_geology` (expected fallout of the clean-fix rerun).
- `pipeline/results/text/landscape_architecture/NE.json` (new corpus, see above).
- Assorted log files under `pipeline/results/gap_harvest/*.log` — cleanup
  candidates once the background job finishes.
