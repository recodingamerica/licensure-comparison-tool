# utah — state professional-licensing extraction pipeline

## The fetched statute data already exists locally — do NOT re-fetch from Justia

Every profession/state corpus we've pulled is **committed in the repo** under
`pipeline/results/`. We are not missing data and there is **no remote bucket** to
pull from — the Vercel blob store holds only the *published* frontend JSON
(`data/<profession>.json`, browse files, tag sheet), not raw statutes.

Justia **rate-limits / blocks bulk sequential fetching** (a mass re-pull will
return empty/partial pages and corrupt corpora). So:

- Need a statute's text? Read it from `pipeline/results/text/<profession>/<state>.json`.
- Need to *transform* corpora (e.g. de-duplicate Justia year-versioned pages)?
  Do it **locally** on the committed files — never by re-fetching. `pull_text`'s
  `_dedupe_year_versions()` can be applied to already-fetched `sections` in place.
- Only fetch from Justia for a genuinely new (profession, state) not yet pulled,
  and one at a time (the fetcher uses `curl_cffi` chrome impersonation + a
  per-host delay; don't run two pulling processes against Justia at once).

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
