# Repo review — 2026-07-06 (working-tree review, pre-commit of session-3 work)

Four parallel read-only review passes over the working tree (client handoff layer,
provenance system, Justia-completeness story, repo hygiene/onboarding), synthesized
against the two goals: **(1) every occupation Justia covers, scraped and mapped;
(2) a client (Utah OPLR, non-coders) can pick occupations, run the pipeline, and
update the website.** Nothing was changed; this is the punch list.

Verdict up front: the architecture is right — the client layer's cost-gating,
the provenance model, the gap-harvest flywheel, and the DRY choices are all sound
design. What stands between today and a handoff is (a) one setup-breaking packaging
bug, (b) two financial-risk/correctness bugs in the new uncommitted layer, (c) a
handful of provenance false-current holes, and (d) docs that describe June, not July.

---

## P0 — must fix before any handoff (all small/medium)

1. **`pipeline/requirements.txt` cannot bootstrap the pipeline.** It lists only the
   scraping deps; missing `pyyaml`, `pydantic`, `litellm`, `anthropic`,
   `python-dotenv` — verified: a fresh venv + the README's own install command dies
   with `ModuleNotFoundError: No module named 'yaml'` on the first client command.
   `pyproject.toml` is also missing `anthropic` (imported at `pipeline/_batch.py:45`).
   Fix both, then verify with a truly clean venv. **(S — blocks 100% of client journeys)**

2. **`run.py`'s "safe to re-run" message is false for the paid steps.**
   `pipeline/client/run.py:81-82` promises already-done work is skipped, but
   `trim_state` reprocesses every `--states` cell unconditionally and
   `extract_state_batch.submit()` builds requests for every queue cell with no check
   against `structured/`. A partial failure + re-run **re-charges for cells that
   already succeeded**. Add already-done skip (or `--only-missing` default) at the
   run.py layer or in the stage CLIs. **(M — financial-risk bug)**

3. **`cmd_extract` reports success unconditionally.** `run.py:100-109` prints
   "extract done." regardless of `poll()`'s written/errored accounting. Read the
   batch metadata back and print "N of M written; failed: [...]". **(S)**

4. **~24 of 94 professions have no discovered schema** (`results/discovered/`), so
   extract preflights them out — but `status.py`/dashboard don't know, so a client
   can pay for `trim` on a profession that can never reach `extract`. Surface
   "needs schema" as a distinct dashboard state and gate the queue. **(S)**

5. **Provenance false-current holes** (the freshness colors are the client's spend
   signal, so these matter):
   - Extract's `input_hash` ignores `results/umbrella_text/<STATE>.json`
     (`provenance.py:35-36,64-65` vs `extract_state.py:210-253`) — umbrella
     re-pulls change every extraction's real input but nothing goes stale. **(S)**
   - Clean's `input_hash` hardcodes `TEXT_DIR/<profession>/` but
     `corpus_profession_for`/`corpus_from_overrides` (clean_text.py:39-52) redirect
     ~255 (prof,state) pairs across 34 professions + 2 `parent_corpus` professions
     to a sibling's dir. The hashed path never exists → `None == None` → those cells
     can **never** go stale. Resolve the actual source path. **(S)**
   - `--model` CLI overrides aren't captured; `recipe_hash` always uses the
     hardcoded default table. Thread the actually-used model into `record()`. **(S)**

## P1 — handoff docs & hygiene (before client sees the repo)

6. **One authoritative top-level doc.** README (Jun 9) references a
   `pipeline/run.py` "stub" that doesn't exist, and competes with ARCHITECTURE.md,
   STATUS.md, and CLAUDE.md with no stated precedence. Rewrite README to current
   reality: venv creation, the fixed install command, **`ANTHROPIC_API_KEY` in `.env`**
   (currently documented nowhere a client looks), pointer to `pipeline/client/` as
   the non-coder path, and which doc is canonical. Archive or delete the stale ones. **(M)**

7. **Vercel publish path is undocumented and ungated.** `publish --deploy` needs
   `npm install` in `publish/web`, `vercel login`, `vercel link` (to the specific
   org/project), and `vercel env pull` for `BLOB_READ_WRITE_TOKEN` — none in any
   client doc. Also `--deploy` goes straight to `npx vercel --prod --yes` with no
   typed-yes gate (unlike the $0.05 LLM steps). Either write the one-time-setup
   section + add a confirm gate, or drop `--deploy` from the client surface and
   keep deploys with the maintainer. **Decision needed: does OPLR self-deploy?** **(M)**

8. **Add a CI workflow that runs pytest.** 572 tests, offline/mocked, ~fast collect,
   zero automation. Meanwhile `.github/workflows/probe.yml` is dead (targets the
   deleted `scrape_probe/`) and `pull-statutes.yml`'s IP-rotation premise is
   superseded by the CDP understanding — delete or fix both. **(S)**

9. **Mechanical cleanup:** `git rm` the ~999 tracked `refresh_diff_*.md` session
   logs in `docs/reports/` (ignore rule already stops new ones); move the one-off
   drivers (`_cdp_grind.py`, `_justia_repull.py`, etc.) out of
   `pipeline/results/batches/` (data dir) into a tools/ location; add a 5-line
   `pipeline/config/README.md` mapping the 9 YAMLs; prune the 25+ stale branches.
   `refetch.sh` hardcodes the macOS Chrome path — note the Windows story or state
   the macOS-only assumption. **(S/M)**

## P2 — the completeness goal (mostly decisions, not code)

10. **Extraction go/no-go is THE bottleneck.** 533 harvest corpora pulled/reused,
    8 extracted. ~$150–210 pending the user's call (correctly held until the
    corpus shape settles: relocate re-pulls + 13 degenerate-reuse re-pulls first).

11. **PA is structurally invisible to the gap harvest** — 0 of 1,061 tier-3 cells;
    `locate()`'s web_search is domain-locked to `law.justia.com` and PA isn't on
    Justia. PA needs its own gap pass against `legis.state.pa.us`, or an explicit
    documented "PA: original 7 professions only" scope statement.

12. **Absence is two unreconciled tiers.** `verified_absences.yaml` (hand-verified,
    3 professions/23 cells, becomes a real structured record) vs the gap harvest's
    161 LLM "confirmed absent" + 421 never-searched "likely_absent" cells, which
    produce **no record at all** — a client can't distinguish "verified absent"
    from "not done yet". Design a promotion path (spot-check → verified_absences,
    or a third "LLM-absent, unreviewed" tier surfaced in the dashboard).

13. **Umbrella coverage is chicken-and-egg for gap professions.**
    `umbrella_from_citations` needs extractions to find umbrellas, so first-pass
    gap extractions will miss shared discipline/fee chapters. Plan a second cycle:
    extract → umbrella detection → re-extract flagged states. Budget it into #10.

14. **Automate the degenerate-reuse check.** The 13 index-only reuse stubs were
    caught by a hand audit; fold that check (reused corpus's only section == chapter
    landing page) into `cleanup.py` so it's a standing gate, not a session memory.

15. **Law freshness has no cadence.** Provenance tracks recipe changes, not statute
    amendments; nothing re-checks upstream law. Probably fine to make this an
    explicit documented policy ("re-pull annually via refetch.sh / CDP") rather
    than build automation — but say so somewhere the client reads.

## Decisions parked for the team (don't act unilaterally)

- Extraction spend (~$150–210) — go/no-go and timing (after relocate re-pulls).
- Does OPLR self-deploy to Vercel, or does the maintainer keep publish? (drives #7)
- Kill or keep the parallel Postgres ETL path (`DATABASE_URL`, `psycopg`,
  docs/POSTGRES_PLAN.md) — undocumented alongside the Blob path.
- Which held-out professions to publish; the ~72–90 sibling-chapter recovered nulls;
  the 421 never-searched `likely_absent` cells (11 professions).
- Repo growth: 762 MB working tree / 144 MB .git today, fine, but committed-corpus
  growth is unbounded — revisit LFS/pruning if clone time becomes a client problem.

## What's genuinely good (keep it)

- The typed-yes cost gates and free/paid command separation in `run.py`.
- Provenance's content-hash design: portable across clones, deterministic
  serialization, conservative toward false-stale; the DEFAULT_MODEL guard test is real.
- The dashboard queue UX (tick → cost estimate → my_queue.json → copy-paste commands).
- Single-source cost model in `status.py`; `run.py` orchestrates real stage CLIs
  instead of reimplementing.
- `reuse.py`'s URL-prefix invariant held across all 261 cells (0 leakage).
- Tests run offline with no API key; suite green (11/11 provenance, 25/25 client
  re-verified this session; 572 total per prior run).
