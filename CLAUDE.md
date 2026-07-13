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
still lives in the `scraping-cloudflare-cdp` skill, and `pull_regulations.py` — admin-rule
SPAs, a different source — is the one remaining CDP-based tool.)

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

**Re-extract gotcha:** after re-pulling or locally transforming `text/`, you must
re-run **clean → trim → extract** in full. Skipping `clean_text` silently leaves
`clean/` (and therefore `trimmed/`) stale, so the new text never reaches the
model. Symptom: `text/` section count != `clean/` section count.

Run modules from the repo root with the project venv, e.g.
`pipeline/.venv/bin/python -m pipeline.ingest.pull_text --profession dietetics --states IA`.
For >2 (state, profession) re-extracts, prefer `pipeline.extract.extract_state_batch`
(Anthropic batch API — ~50% cheaper, durable across crashes).

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
  `refetch.sh`. Client guide: `docs/runbooks/client_refetch.md`.
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
