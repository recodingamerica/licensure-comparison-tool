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
| `models.yaml` | The AI model each paid stage uses (`trim`/`extract`/`schema`) — swap models or vendors here instead of editing Python (see note below) | Hand |
| `limits.yaml` | Every number deciding what's fetched/kept (`fetch.per_host_delay_seconds`, caps, thresholds) | Hand |
| `field_semantics.yaml` | Field importance + value-closeness knobs for the Compare / similarity view | `analyze.gen_semantics` (then editable) |
| `publish_options.yaml` | Publish-time site toggles read by `publish.build_frontend` | Hand |

**`models.yaml` — swapping models / vendors.** Each stage reads its model from
`models.yaml` at startup (via `loaders.model_for(stage, default)`), so changing a model
is a one-line config edit, not a code change; the per-stage `--model` flag still
overrides for a one-off run. `trim` and `schema` — and `extract` run with
`--backend litellm` — go through LiteLLM, so any LiteLLM-supported model works (set the
vendor's API key in the env). The **default `extract` path uses Anthropic's Message
Batches API** for a ~50% bulk discount, which is Claude-only; to extract with a
non-Claude model use `run extract --backend litellm` (any vendor, no batch discount).

Loaders live in `pipeline/config/loaders.py`. Two use `safe_load_unique` (hard-errors
on duplicate top-level keys) because a silent last-wins drop bit us before —
`state_structure.yaml` and any file where a duplicate state/profession key would
quietly discard overrides.
