# pipeline/config/

Every YAML the pipeline reads. Edit these instead of hard-coding values in Python.

| File | What it controls | Written/edited by |
|---|---|---|
| `professions.yaml` | Canonical profession registry (46 from Utah Title 58), match patterns, `parent_corpus` nesting, `_families` colors | Hand + `discover` |
| `state_structure.yaml` | Per-state source/layout + per-profession chapter/section URL overrides (single source of truth for per-state quirks) | Hand |
| `mapping_overrides.yaml` | Manual patches to the generated `profession_index` (which chapters a profession pulls) | Hand + `discover.migrate_mapping_overrides` |
| `corpus_overrides.yaml` | Per-(profession, state) corpus reuse — borrow a sibling's already-pulled combined chapter (`{profession: {STATE: sibling}}`) | `discover.cross_ref_siblings` |
| `verified_absences.yaml` | Hand-verified (profession, state) pairs with no state-level license — correct-blanks, not gaps | Hand |
| `prompts.yaml` | LLM system prompts, loaded by key (trim/extract/etc.) — edit prompt text without touching Python | Hand |
| `limits.yaml` | Every number deciding what's fetched/kept (`fetch.per_host_delay_seconds`, caps, thresholds) | Hand |
| `field_semantics.yaml` | Field importance + value-closeness knobs for the Compare / similarity view | `analyze.gen_semantics` (then editable) |
| `publish_options.yaml` | Publish-time site toggles read by `publish.build_frontend` | Hand |

Loaders live in `pipeline/config/loaders.py`. Two use `safe_load_unique` (hard-errors
on duplicate top-level keys) because a silent last-wins drop bit us before —
`state_structure.yaml` and any file where a duplicate state/profession key would
quietly discard overrides.
