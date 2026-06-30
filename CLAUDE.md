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

- Set `JUSTIA_CDP_URL=http://localhost:9222` (a debug Chrome the user started + cleared
  the challenge in once) and a polite `PULL_HOST_DELAY` (e.g. 7). `pull_text` routes
  Justia through CDP automatically when `JUSTIA_CDP_URL` is set.
- **ONE pull process per Chrome** — concurrent jobs against the same browser garble
  corpora (1-section partials). A flock guards this; don't bypass it.
- Bulk re-pull is fine this way; `_justia_repull.py` / `_cdp_grind.py` are resumable
  drivers that commit per profession.
- **PA is the only state not on Justia** (`legis.state.pa.us`); ~12 other states use
  official-source overrides by choice, but their Justia URLs are stored in the index.

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
- Published professions (have map/blob payloads): dentistry, dietetics, medicine,
  nursing, optometry, podiatry, public_accountancy. Others are held-out.
