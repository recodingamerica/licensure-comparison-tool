# utah — state professional-licensing extraction pipeline

## The fetched statute data already exists locally — prefer it; re-fetch only when needed

Every profession/state corpus we've pulled is **committed in the repo** under
`pipeline/results/`. There is **no remote bucket** — the Vercel blob store holds only
the *published* frontend JSON (`data/<profession>.json`, browse files, tag sheet),
not raw statutes. So the default is local:

- Need a statute's text? Read it from `pipeline/results/text/<profession>/<state>.json`.
- Need to *transform* corpora (e.g. de-duplicate Justia year-versioned pages)? Do it
  **locally** on the committed files. `pull_text._dedupe_year_versions()` can be applied
  to already-fetched `sections` in place — no fetch required.

**Justia is fetched HEADLESS via Scrapling — the sole fetcher (2026-07-13).** `pull_text.fetch`
routes Justia through **Scrapling's `StealthyFetcher`** (headless camoufox, `solve_cloudflare`) —
no hand-started Chrome, no manual challenge solve, and no soft-block on rapid back-to-back
fetches (the old CDP pain). Validated: reproduced the CDP corpora on 6/8 A/B cells (incl.
the 426-section CA chapter + year-versioned KY/OR), ≥ CDP elsewhere — so the CDP fallback
was retired 2026-07-13 (see the Justia section below). It's in `pipeline/.venv`
(`pip install "scrapling[fetchers]"` + `scrapling install`); if it's not importable, Justia
fetches now **fail loud** (no CDP/cffi fallback). See [[reference_scrapling_fetch]]. **Year-selector handling:** an *undated* Justia URL for a
year-only state (some IL acts) can land on a year-SELECTOR page (only self-year links, 0
sections); `extract_child_links` now drills the latest-year copy — guarded against a
year→year loop by `base_has_year` and it only fires on a genuinely empty undated page
(tests: `test_pull_text_drill.py`). Separate caveat: Scrapling has occasional run-to-run
flakiness (an intermittent short pull — the 115-vs-172 nursing/IL wobble); a
retry-on-short-pull would harden it further if it recurs.

**Justia = Scrapling only (the CDP fallback was retired 2026-07-13).** Justia's wall is
a Cloudflare **fingerprint** challenge, *not* a rate/IP block; Scrapling's StealthyFetcher
clears it headless (see above). The old hand-started-debug-Chrome-over-CDP path was
removed — Scrapling reproduced its corpora with no manual Chrome and no hand-solve, so the
whole CDP apparatus is gone: `JUSTIA_CDP_URL`, the `JUSTIA_SCRAPLING` flag, the flock,
`relaunch_debug_chrome`, and `fetch_via_browser`. If Scrapling isn't installed, Justia
fetches now **fail loud** rather than silently pulling a challenge page. The per-host
delay lives in `config/limits.yaml` (`fetch.per_host_delay_seconds`, default 3.0,
+jitter); `PULL_HOST_DELAY` overrides. (`git log` for the CDP code; the general technique
still lives in the `scraping-cloudflare-cdp` skill. CDP is now fully out of the pipeline:
`pull_regulations.py` (admin-rule SPAs) and `probe_justia.py` were deleted 2026-07-13 —
no CDP-based tool remains.)

- **Tool choice matters**: `pipeline.ingest.refresh_corpus` is for RE-checking corpora
  you already have committed (the annual recodification-check use case) — it decides
  "changed" via `git diff` against HEAD, which silently treats every untracked (never-
  committed) file as unchanged. Point it at brand-new, first-time (profession, state)
  pairs and every real successful fetch gets misclassified NOCHANGE and discarded (fixed
  2026-07-09, but the underlying design intent hasn't changed). **For first-time pulls of
  new pairs, use plain `pipeline.ingest.pull_text` instead, supervised** — check section
  counts as they land, don't assume it worked unattended.
- **PA is the only state not on Justia** (`legis.state.pa.us`). MD/NV were flipped BACK
  to Justia 2026-07-02 (source-gated dispatch — comment out `source:` to flip a state);
  other official-source states keep their Justia URLs in the index.
- **CORPUS-SOURCE POLICY (enforced 2026-07-13): statute text is ingested from Justia + PA
  ONLY.** `pull_text.fetch()` is a closed allowlist — any host other than `law.justia.com`
  (Scrapling) or `legis.state.pa.us` (curl_cffi) RAISES. A cell with no Justia/PA source is
  an accepted `source_unavailable` gap — do NOT build an alternate-source scraper (ilga.gov,
  arkleg, admin code, state APIs); the earlier UT/SD/NY/NV official-source effort was deleted
  for exactly this reason. The guard covers ONLY corpus fetching — discovery/research
  (web_search, reading a state PDF to LEARN a citation) is a separate, unguarded layer.
  Test: `test_corpus_source_allowlist.py`.
- The `docs/runbooks/cdp_repull_lessons_*.md` runbooks are **historical** (CDP-era) — they
  describe the retired workflow, not the current default. Do NOT run two committing
  processes at once (git index.lock races).

## Pipeline stages (each reads the previous stage's output dir)

```
pull_text   → results/text/        (raw fetched corpus; COMMITTED)
clean_text  → results/clean/       (reads text/)
trim_state  → results/trimmed/     (reads clean/ — LLM drops irrelevant sections)
extract_state → results/structured/ (reads trimmed/ — the structured records)
build_frontend → publish/web/public/data/ + Vercel blob (the published payload)
```

**Re-extract because the CORPUS changed, not because the prompt did.** Measured
2026-07-31 on four professions re-run against an unchanged corpus: 3 of 4 came back
roughly break-even and were reverted (optometry 17.1:1 gain/loss and kept; electrician
1.6:1, medicine 1.5:1, nursing ~1:1). The losses are real errors — `electrician/CA`
flipped "Electrical Contractor" to absent. The one unambiguous win was corpus-driven:
29 cells the #118 trim bug had cut to 1-2 sections went 302 → 1136 quote-backed claims
for $3.69. So a whole-corpus "wave" after a prompt edit buys churn with embedded
regressions (#126); fix a cell's corpus and re-extract that cell instead. When judging
a re-run, count flips that DROPPED a quote vs added one — net quote-count nets the two
against each other and hides category errors.

**Re-extract gotcha — now automated; the danger is the BY-HAND path.** After re-pulling
or locally transforming `text/`, **clean → trim → extract** must all re-run. Skipping
`clean_text` silently leaves `clean/` (and therefore `trimmed/`) stale, so the new text
never reaches the model. Symptom: `text/` section count != `clean/` section count.

You do NOT have to sequence this yourself if you use the runner: `run_to` walks the
ordered `STAGES` prefix and re-runs whatever provenance says is stale, so fresh `text/`
re-cleans automatically. The gotcha bites in exactly two cases — invoking the stage
modules **by hand**, or passing `--start` to skip ahead (which is what `--start` is FOR,
so it warns rather than errors; see the comment at `pipeline_stages.run_to`). Prefer the
runner and this class of bug can't happen.

Run modules from the repo root with the project venv, e.g.
`pipeline/.venv/bin/python -m pipeline.ingest.pull_text --profession dietetics --states IA`.
For >2 (state, profession) re-extracts, prefer `pipeline.extract.extract_state_batch`
(Anthropic batch API — ~50% cheaper, durable across crashes).

**The ONE runner is `pipeline.pipeline_stages`** — it defines the stage order once
(`STAGES`) and every entry path (`refresh_all`, `client/run`, `add_occupation`, the
`--queue` batch re-extract that replaced `re_extract_queue`, the `refresh_corpus`
annual loop) is a thin caller of its `run_to(target, prof, states, *, start, ...)`.
The `start=` seam decides how much of the chain runs (`None`=full chain incl. the
committing pull stage; `"clean"`=no-pull; `target`=that stage only). Full guide with
the "what commits vs what doesn't" + refresh-pause rules:
[`docs/runbooks/pipeline_run_order.md`](docs/runbooks/pipeline_run_order.md).

**`--force` is CELL-scoped, and `schema` is derived ONCE.** When you name states,
`--force` re-runs those cells only — it will NOT re-derive profession-wide artifacts.
`schema` goes further (2026-07-29): an existing `discovered/<prof>.json` is a stable
contract and the chain will NEVER auto-re-derive it — not on staleness (every corpus
repair flips schema provenance stale), not on whole-profession `--force`. Re-derivation
is LLM churn (nursing renamed 26 of 29 fields on a same-corpus re-derive) and briefly
left 31 states extracted against a field set the repo didn't have. It runs only when
the file is missing (new profession) or when you explicitly run `--target schema`.
Two more guards back this up: batch preflight blocks `SCHEMA_DIRTY` (schema modified vs
git HEAD) and `STALE_UPSTREAM` (clean/trim provenance-stale vs the corpus), and `poll`
refuses to write a batch whose schema changed since submit (sha recorded in metadata).

## Publishing: the gate that can fail your build

`build_frontend` refuses to ship a payload where too few quoted claims can actually be
HIGHLIGHTED in the UI (`MIN_DISPLAYABLE_QUOTE_SHARE`, currently 0.90). A quote is
displayable only if its span resolves to a section shipped with that row — a span
pointing at a section the row doesn't carry renders nothing, silently. Every build
prints its share; a failure prints example citations.

It is a RATCHET, not a target. Measured 2026-07-27 across all 13: 93.0% (nursing) to
99.9% (hvac), 96.1% overall. **If a build trips it, read the examples before touching
the floor** — the honest fixes are usually a missing umbrella chapter or a citation the
row doesn't ship, not a lower number. Lower it only with a reason you'd write down.

**Auto-deploy is NOT armed.** `.github/workflows/deploy-web.yml` ships frontend code
changes on push (paths-filtered to `pipeline/publish/web/**` so the crawl's data commits
don't rebuild the site), but it skips with a notice until the `VERCEL_TOKEN` secret and
the `VERCEL_ORG_ID` / `VERCEL_PROJECT_ID` repo variables exist. Until then a web-code
push does NOT reach production — deploy with `publish --deploy`, or `vercel --prod`
from `pipeline/publish/web`. Data publishes are unaffected (they run `vercel --prod`
themselves).

## Where things live

- `pipeline/config/state_structure.yaml` — per-state source/layout overrides
  (single source of truth for which chapter/section a profession maps to).
- `pipeline/config/professions.yaml` — profession definitions + match patterns.
- `pipeline/config/prompts.yaml` — extraction prompts (the `regulatory_model`
  rung rules, cross-field consistency, etc.).
- Published professions = whatever has a payload in `pipeline/publish/web/public/data/`
  (13 as of 2026-07-07: the 7 health/finance originals + architecture, construction_trades,
  electrician, hvac, plumbing, professional_engineering). Don't trust a hand-written list —
  check the dir, or run `python -m pipeline.client.handoff_doc` which derives it.
- `pipeline/client/` — the non-coder handoff layer (README = module map): `status.py`
  (read-only state + cost + freshness → `results/status/status.json`), `dashboard.py`
  (offline `dashboard.html` picker), `run.py` (`clean`/`trim`/`extract`/`publish`), and
  `refetch.sh`. Client guide: `CLIENT_GUIDE.md`.
- `pipeline/provenance.py` — content-hash **freshness** (survives `git clone`): each stage
  stamps `results/provenance/<prof>/<state>.json`; `check()`→current/stale/unstamped, so
  "done" means "current" not just "a file exists." A prompt/corpus/schema change flips
  affected cells stale. `provenance report` / `backfill`. Bump `CODE_VERSION[stage]` when a
  stage's logic should invalidate old outputs.

## Completeness: pulling everything Justia has that's relevant to a profession

The north star is: for every occupation, have every Justia chapter that could regulate
it, mapped correctly, in every state. Pulling is easy (headless via Scrapling); the hard
part is knowing WHAT to pull. Three layers, each with LLM-free tooling:

1. **Own-chapter professions** — `match_profession` maps a profession to its named
   chapter via `results/hierarchy/<STATE>.json` (chapter-label index, all 50 states).
   Works when the profession has its own named chapter (Medicine, Podiatry).

2. **Section-nested professions** — a profession that lives as a *section inside a broad
   chapter* (public adjuster = §626.854 inside the Insurance title) is invisible to the
   chapter-label index. Loop:
   - `expand_containers` — depth-expands broad chapters into their section-title tree
     (headless via `pull_text.fetch`; `--max-depth` default 2; checkpoints every 5; ONE process at a time).
   - `match_sections --source hierarchy --profession X --write-targets` — LLM-free,
     matches patterns against SECTION titles, writes the parent container as a pull
     target into `profession_index/X.json`.
   - `pull_text --profession X` → clean → trim → extract.

3. **Shared umbrella chapters** — general-provisions chapters (NM 61-1 "Uniform
   Licensing": discipline, fees, hearings) that many professions CITE but nobody pulls
   (they're nobody's profession-chapter). Extraction silently misses that law.
   - `corpus_status umbrella` detects them by citation; `umbrella_from_citations` maps
     them to Justia URLs (two-factor: cited by ≥N professions AND an umbrella-style
     label — the citation signal alone also flags profession chapters, DON'T trust it).
   - `pull_umbrella_text --label-filter --force` pulls only genuine umbrellas (excludes
     the old find_umbrella_chapters profession-specific over-picks) → `umbrella_text/`,
     which `extract_state` folds in as context for every profession in the state.

**Harvest ops (hard-won):** run ONE `expand_containers`/`pull_text`/`pull_umbrella_text`
at a time (politeness + simpler to supervise; Scrapling handles Cloudflare challenges
itself, no manual solve). Commit before/after pulls — a bad/partial pull is then just
`git checkout --`. "has a corpus" ≠ "has the law": section-nesting + umbrella +
wrong-chapter (audit_corpus) are separate completeness axes.
