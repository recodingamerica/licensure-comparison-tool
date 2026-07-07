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

**But re-fetching Justia IS possible and sometimes necessary** (failed/empty pulls,
index-only corpora, genuinely-new pairs). Justia's wall is a Cloudflare **fingerprint**
challenge, *not* a rate/IP block — `curl_cffi` and launched-headless browsers get
challenge pages, but **attaching to a hand-started debug Chrome over CDP clears it**
(see the `scraping-cloudflare-cdp` skill). To re-fetch:

- Set `JUSTIA_CDP_URL=http://127.0.0.1:9222` (a debug Chrome the user started + cleared
  the challenge in once; use `127.0.0.1`, not `localhost`). The per-host delay now
  lives in `config/limits.yaml` (`fetch.per_host_delay_seconds`, default 3.0, +jitter);
  `PULL_HOST_DELAY` still overrides. `pull_text` routes Justia through CDP automatically.
- **ONE pull process per Chrome** — concurrent jobs garble corpora. A flock guards this.
- Bulk re-pull is fine this way; use `pipeline.ingest.refresh_corpus` (resumable, per-item
  commits, hardened per the 2026-07-02 CDP lessons) — the tested replacement for the old
  throwaway `_cdp_*` / `_justia_repull` batch drivers (now removed).
- **PA is the only state not on Justia** (`legis.state.pa.us`). MD/NV were flipped BACK
  to Justia 2026-07-02 (source-gated dispatch — comment out `source:` to flip a state);
  other official-source states keep their Justia URLs in the index.
- **Before a LARGE CDP harvest, read `docs/runbooks/cdp_repull_lessons_2026-07-02.md`** —
  the wedge failure-modes (pages[0] hijack [fixed], official-source silence, Chrome
  auto-update mid-run), the faulthandler wedge-check, the all-or-nothing no-wipe guard,
  and the real-fetch-vs-stale-cache detection. Do NOT run two committing processes at
  once (git index.lock races).

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
it, mapped correctly, in every state. Pulling is easy (CDP); the hard part is knowing
WHAT to pull. Three layers, each with LLM-free tooling:

1. **Own-chapter professions** — `match_profession` maps a profession to its named
   chapter via `results/hierarchy/<STATE>.json` (chapter-label index, all 50 states).
   Works when the profession has its own named chapter (Medicine, Podiatry).

2. **Section-nested professions** — a profession that lives as a *section inside a broad
   chapter* (public adjuster = §626.854 inside the Insurance title) is invisible to the
   chapter-label index. Loop:
   - `expand_containers` — depth-expands broad chapters into their section-title tree
     (CDP; `--max-depth` default 2; checkpoints every 5; ONE process only).
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

**CDP harvest ops (hard-won):** ONE `expand_containers`/`pull_text`/`pull_umbrella_text`
process at a time — overlapping runs wedge a fetch (0% CPU, looks like a hang, is NOT a
challenge). Cloudflare DOES re-challenge mid-run ("⏸ … SOLVE IT"); it waits 360s then
records +0 (a real miss to re-run). Commit before/after pulls — a bad/partial pull is
then just `git checkout --`. "has a corpus" ≠ "has the law": section-nesting + umbrella +
wrong-chapter (audit_corpus) are separate completeness axes.
