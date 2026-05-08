# utah

Pipeline that turns state statutes into a structured, evidence-backed view of
licensure and scope of practice for regulated professions, with a static
DataTables viewer.

Seeded from Utah's Title 58 (Occupations and Professions) — Utah's 46
licensed professions are the canonical registry; other states fill in those
same professions where they exist, plus get added as gaps when Utah doesn't
license something.

## Current status (2026-05-08)

The first end-to-end demo profession is **podiatry**. The full pipeline ran
across 50 states and produced an interactive viewer with verbatim statutory
quotes regex-validated against the source.

| Stage | What it does | Status |
|---|---|---|
| `discover/probe` | Verify each state's licensing parent URL is fetchable | Working — runs against `config/targets.csv` |
| `discover/build_hierarchy` | Per-state structural crawl (title → chapters) | Done for all 50 states. 4 states have known quality issues (NV empty, PA wrong target URL, AR/CO need depth-2). 6 states return section labels at the top level instead of chapters (AZ, OK, MI, WI, LA — `section_fallback` mode). |
| `discover/match_profession` | Match `professions.yaml` patterns → matched chapter nodes per state | Working. Coverage matrix at `results/profession_index/_coverage.csv`. Podiatry: **35/50** — same as our prior pull because the missing 15 are real (9 buried under Medicine chapters, 4 hierarchy-quality states, 2 misc). |
| `ingest/pull_text` | Fetch full text for each section under matched chapters | Currently reads from a legacy CSV; needs to be rewired to consume `profession_index/<prof>.json`. Not blocking the demo — last pull is cached. |
| `ingest/clean_text` | Source-keyed regex cleanup (Justia chrome, repealed sections) | Working. ~1.04M chars across 35 states after cleaning. |
| `ingest/trim_state` | Haiku keep/drop classifier — drops board-composition / fund / ministerial sections | Working. ~568 sections kept across 35 states. |
| `extract/discover_schema` | **Pass 1b** — Sonnet aggregator over all 35 trimmed corpora; outputs `discovered/<prof>.json` listing profession-specific fields with types/enums | Working. 36 podiatry-specific fields auto-discovered. |
| `extract/extract_state` | **Pass 2** — per-state structured extraction. Every leaf field is Evidence-wrapped (value + verbatim quote + citation); each quote regex-validated against the cleaned source. | Working. Sonnet 4.6 by default (Haiku produced known misses on residency/CE/renewal). |
| `publish/build_frontend` | Aggregate per-state records → `site/data.json` + summary stats | Working. |
| `publish/site/` | Static viewer (jQuery + DataTables + shared-ui) | Working. Universal columns + one anatomical-scope column for the podiatry demo. Per-row evidence-verification badge. Modal shows full record with quote + citation under every claim. |

## How to run it

Setup:

```bash
cd pipeline
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/playwright install chromium      # only if you'll hit JS-rendered state sites
```

End-to-end for one profession:

```bash
.venv/bin/python -m pipeline.discover.build_hierarchy           # one-time per state, cached
.venv/bin/python -m pipeline.discover.match_profession --profession podiatry
# (re-pulling text is currently broken on the new path — see Known gaps)
.venv/bin/python -m pipeline.ingest.clean_text       --profession podiatry
.venv/bin/python -m pipeline.ingest.trim_state       --profession podiatry
.venv/bin/python -m pipeline.extract.discover_schema --profession podiatry
.venv/bin/python -m pipeline.extract.extract_state   --profession podiatry
.venv/bin/python -m pipeline.publish.build_frontend  --profession podiatry
```

Serve the viewer:

```bash
cd pipeline/publish/site
python3 -m http.server 8767
# open http://localhost:8767/
```

## Architecture invariants

1. **Each stage reads from the previous stage's output dir, writes to its own.** No cross-stage coupling beyond filesystem paths.
2. **Profession is always a parameter.** "podiatry" appears only in `config/professions.yaml`.
3. **Hierarchy is profession-agnostic** (one crawl per state, reused for every profession).
4. **`pipeline/results/` is the only place outputs land.**
5. **Every claim is evidence-backed.** Pass 2 wraps every leaf field in `{value, quote, citation}` and a regex check verifies the quote appears in the cleaned source. Unverified quotes get flagged in the UI rather than silently dropped.

## Known gaps

- **`pull_text.py` reads from the old chapter-list CSV.** Once `match_profession.py` produces `profession_index/<prof>.json`, `pull_text.py` should consume that instead. The cached `text/podiatry/` directory still works for the current demo.
- **`run.py` orchestrator is a stub.** Stage scripts run individually for now.
- **15 states without podiatry coverage** — 9 are regulated under a Medicine/Healing-Arts chapter we never enumerated; 2 (NV, PA) had bad target URLs; 2 (AR, CO) need depth-2 hierarchy expansion; 2 (AZ, OK) return section_fallback mode where chapters aren't a level in the tree. Path forward is a `manual_overrides.yaml` plus a smarter section-level matcher.
- **Only one profession wired so far.** `professions.yaml` has 46 entries seeded from Utah Title 58; the rest are unrun. Adding a profession to the demo: run `match_profession --profession <name>` then the rest of the pipeline.
- **`config/sources.py` only has Justia.** Adding non-Justia sources (CA leginfo, MN revisor, PA legis) needs a new cleaner registered in `ingest/clean_text.py`.

## Layout

```
pipeline/
  config/
    states.py          # 50 US state codes
    sources.py         # URL host → cleaner registry
    professions.yaml   # canonical profession registry (46 from Utah Title 58)
    targets.csv        # per-state licensing parent URLs
    regs_targets.csv   # per-state admin code parent URLs
  discover/
    _fetch.py          # polite fetch helpers (requests → curl_cffi → playwright)
    _extract.py        # link extractors (Justia + generic official)
    probe.py
    build_hierarchy.py
    match_profession.py
    regs_probe.py      # admin code source probe (separate concern)
  ingest/
    pull_text.py
    clean_text.py
    trim_state.py
  extract/
    standard_model.py  # universal Pydantic base, Evidence-wrapped
    discover_schema.py
    extract_state.py
  publish/
    build_frontend.py
    site/
  results/
    hierarchy/
    profession_index/
    text/
    clean/
    trimmed/
    discovered/
    structured/
  logs/
  paths.py             # canonical path constants
  run.py               # orchestrator (stub)
```

## Decisions worth knowing

- **Trim is a Haiku binary classifier, never a text rewriter.** The model only emits `[{citation, keep, reason}]`; verbatim text is read from the cleaned corpus by citation. Eliminates one class of hallucination.
- **Schema discovery is a separate stage.** Pass 1b runs once per profession across all states' trimmed text → a profession-specific field list with normalized enum values. Pass 2 then composes a typed Pydantic model from that list and uses it per-state. Means the field set adapts to the profession's actual variation rather than being hard-coded.
- **Universal base + discovered profession-specific.** `standard_model.py` covers what's true for any licensed profession (license_required, education, post-degree experience, exams, renewal, CE, reciprocity). Profession-specific dimensions (anatomical scope for podiatry, CPE topics for accountancy, etc.) come from pass 1b.
- **Sonnet for both LLM-driven stages.** Pass 1b needs the 200k+ token corpus reasoning; pass 2 turned out to need it too — Haiku missed in-corpus fields (CT residency, ME CE, KS/WA renewal). Cost: ~$5 per profession-state run. Worth it.
