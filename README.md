# utah

Pipeline that turns state statutes into a structured, evidence-backed view of
licensure and scope of practice for regulated professions, with a static
DataTables viewer.

Built for Utah's Office of Professional Licensure Review (OPLR) as the
descriptive layer that feeds their Universal Occupational Regulation Framework
(UORF) — the prescriptive six-rung ladder OPLR uses to evaluate how strictly
each occupation should be regulated. We answer "what does each state currently
do?"; UORF answers "what should they do?".

Seeded from Utah's Title 58 — Utah's 46 licensed professions are the canonical
registry (`pipeline/config/professions.yaml`); other states fill in those
same professions where they exist.

## Current status

Two professions are wired through end-to-end: **podiatry** and
**public accountancy** (CPA). Demo at `localhost:8767/`.

| | Podiatry | Public Accountancy |
|---|---|---|
| States with substantive records | 41–47 (chains in flight) | 32 |
| Profession-specific fields auto-discovered | 36 | 38 |
| Evidence quotes regex-validated against source | 98.7% (857 / 868) | 95.9% (1,078 / 1,124) |

Pipeline stages, all working:

| Stage | What it does |
|---|---|
| `discover/probe` | Verify each state's licensing parent URL is fetchable |
| `discover/build_hierarchy` | Per-state structural crawl (title → chapters), 50 states cached |
| `discover/match_profession` | `professions.yaml` patterns + `state_structure.yaml` overrides → matched chapter nodes |
| `discover/suggest_overrides` | Haiku classifier that proposes chapter URLs for buried-under-parent cases (e.g. podiatry under Medicine) — proposals reviewed before promoting |
| `discover/fetch_section_bodies` | Bulk-fetches per-section body excerpts (cached per state) — only needed for section_fallback states |
| `discover/map_state_sections_v2` | For section_fallback states, asks Sonnet to assign each flat section to a profession using label + body excerpt |
| `ingest/pull_text` | Consumes `profession_index/<prof>.json`, fetches section text. Supports `section_url_list` and `section_slug_pattern` overrides |
| `ingest/clean_text` | Source-keyed regex cleanup (Justia chrome, repealed sections) |
| `ingest/trim_state` | Haiku binary keep/drop classifier — drops board-composition / fund / ministerial sections. Never rewrites text |
| `extract/discover_schema` | Pass 1b — Sonnet aggregator over all trimmed corpora. Outputs profession-specific fields with types, enum values, plain-English category labels |
| `extract/extract_state` | Pass 2 — per-state structured extraction. Every leaf field is Evidence-wrapped (`{value, quote, citation}`). Quote is regex-validated against the cleaned source |
| `extract/recategorize_fields` | Surgical re-grouping of an existing discovered file into LLM-named categories without re-extraction |
| `extract/reverify_evidence` | Re-runs the regex check against existing structured records (lets us tighten/loosen the matcher without re-extracting) |
| `publish/build_frontend` | Aggregates per-state records into `publish/web/public/data/<prof>.json` + refreshes `professions.json` |
| `publish/web/` | Next.js + Tailwind + shadcn static-export viewer. Home is profession picker; per-profession profile page shows table + per-row evidence-backed dialog |

## How to run it

Setup:

```bash
cd pipeline
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Add a profession (one that's already in `config/professions.yaml`):

```bash
# 1. Match — uses state_structure.yaml overrides + professions.yaml patterns
python -m pipeline.discover.match_profession --profession <name>

# 2. (optional) For unmatched states — let Haiku propose chapter URLs:
python -m pipeline.discover.suggest_overrides --profession <name>
# review pipeline/results/profession_index/<name>_suggestions.json,
# promote good ones into pipeline/config/state_structure.yaml,
# re-run match_profession.

# 3. Pull → clean → trim → discover schema → extract → publish
python -m pipeline.ingest.pull_text          --profession <name>
python -m pipeline.ingest.clean_text         --profession <name>
python -m pipeline.ingest.trim_state         --profession <name>
python -m pipeline.extract.discover_schema   --profession <name>
python -m pipeline.extract.extract_state     --profession <name>
python -m pipeline.publish.build_frontend    --profession <name>
```

Serve the viewer:

```bash
cd pipeline/publish/web
npm install
npm run build           # static export to pipeline/publish/web/out/
cd out && python3 -m http.server 8767
# open http://localhost:8767/
```

## Architecture invariants

1. **Each stage reads from the previous stage's output dir, writes to its own.** No cross-stage coupling beyond filesystem paths.
2. **Profession is always a parameter.** `"podiatry"` appears only in `config/professions.yaml`. Adding a third profession is a config edit.
3. **Hierarchy is profession-agnostic** — one crawl per state, reused for every profession.
4. **State structure is the single source of truth** for per-state quirks. `config/state_structure.yaml` records the source, layout, and per-profession URL/section pattern. Match-time precedence: state_structure > label match.
5. **Every claim is evidence-backed.** Pass 2 wraps every leaf field in `{value, quote, citation}` and a regex check verifies the quote appears in the cleaned source. Unverified quotes get flagged in the UI rather than silently dropped.
6. **LLM-driven over hand-curation, when it scales.** Buried-chapter detection, schema discovery, profession-field categorization, section-to-profession mapping — all LLM-driven with Pydantic Literal-constrained outputs as anti-hallucination guardrails. Hand-curation is the fallback for the long tail.

## Known gaps and limits

- **`run.py` orchestrator is a stub.** Stage scripts run individually for now.
- **PA podiatry coverage gap.** palegis.us is JS-rendered + query-string-driven; FindLaw is anti-scrape; Cornell LII doesn't host state statutes. Documented as a deferred gap; would need Playwright + custom navigation or a paid source (Westlaw).
- **Admin code (CE topical rules, application procedure specifics) not yet pulled.** `regs_targets.csv` exists but isn't wired into the ingest stage. Would close many of the visible "—" cells under CE hours.
- **Section-mapper accuracy varies** by state. v1 (label-only) is unreliable when section labels are generic ("Definitions", "License required") — see `pipeline/notes/LEARNINGS.md` for the LA mismap. v2 (label + body excerpt) trades a one-time per-state body fetch for accuracy.

## Layout

```
pipeline/
  config/
    states.py            # 50 US state codes
    sources.py           # URL host → cleaner registry
    professions.yaml     # canonical profession registry (46 from Utah Title 58)
    state_structure.yaml # per-state source/layout + per-profession URL or section pattern
    prompts.yaml         # LLM system prompts (loadable by name)
    targets.csv          # per-state licensing parent URLs
    regs_targets.csv     # per-state admin code parent URLs
  discover/
    _fetch.py            # polite fetch helpers (requests → curl_cffi → playwright)
    _extract.py          # Justia + generic link extractors
    probe.py
    build_hierarchy.py
    match_profession.py
    suggest_overrides.py
    fetch_section_bodies.py
    map_state_sections.py / _v2.py
    regs_probe.py
  ingest/
    pull_text.py
    clean_text.py
    trim_state.py
  extract/
    standard_model.py    # universal Pydantic base, Evidence-wrapped
    discover_schema.py
    extract_state.py
    recategorize_fields.py
    reverify_evidence.py
  publish/
    build_frontend.py
    site/
      index.html
      profile.html
      data/<profession>.json
      professions.json
  notes/
    LEARNINGS.md
    FIELDS.md
    PDF_COMPARISON.md
  results/
    hierarchy/
    profession_index/
    section_bodies/
    section_maps/
    text/
    clean/
    trimmed/
    discovered/
    structured/
  logs/
  paths.py               # canonical path constants
  run.py                 # orchestrator (stub)
  _prompts.py            # prompt loader
```

## Decisions worth knowing

- **Trim is a Haiku binary classifier, never a text rewriter.** The model only emits `[{citation, keep, reason}]`; verbatim text is read from the cleaned corpus by citation. Eliminates one class of hallucination.
- **Schema discovery is a separate stage.** Pass 1b runs once per profession across all states' trimmed text → a profession-specific field list with normalized enum values and plain-English category labels (LLM-named, not hand-coded). Pass 2 then composes a typed Pydantic model from that list and uses it per-state.
- **Universal base + discovered profession-specific.** `standard_model.py` covers what's true for any licensed profession (license_required, education, post-degree experience, exams, renewal, CE, reciprocity, plus four UORF-aligned fields: regulatory_model, title_protection, scope_protection, disciplinary_grounds). Profession-specific dimensions come from pass 1b.
- **Sonnet for both LLM-driven extraction stages.** Pass 1b needs the 200k+ token corpus reasoning; pass 2 turned out to need it too — Haiku missed in-corpus fields (CT residency, ME CE, KS/WA renewal). Cost: ~$5 per profession-state run.
- **`state_structure.yaml` over `manual_overrides.yaml`.** State-keyed registry is the long-term home for per-state quirks. `source` and `layout` are state-level facts every profession in that state inherits; per-profession URLs / section patterns sit one level deeper.
- **Frontend modal shows source link + in-context highlight.** Each evidence quote gets a `source ↗` link to the actual section page on Justia / revisor.mn.gov / etc., plus an `in context` toggle that shows the full section text with the quote highlighted in `<mark>` tags.

## Notes

Running notes on what we've learned during this build live in
`pipeline/notes/`:
- `LEARNINGS.md` — source coverage quirks, hierarchy issues per state, LLM extraction observations, architecture decisions
- `FIELDS.md` — universal base + per-profession discovered fields for podiatry and CPA
- `PDF_COMPARISON.md` — concrete diff vs the human-curated podiatry PDF on four states
