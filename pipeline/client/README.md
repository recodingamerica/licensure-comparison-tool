# pipeline/client — the client-facing handoff tooling

Everything a non-programmer needs to see pipeline state, pick occupations to turn into
data, run the (few) commands, publish, and re-fetch a state later. Read-only over the
committed repo; nothing here fetches or spends money on its own.

| File | What it is | Run |
|---|---|---|
| `status.py` | Data layer. Per (occupation, state): furthest stage, **freshness** (current/stale/unstamped via `pipeline.provenance`), cost-to-finish/refresh, **source URL(s)** (from corpus `chapter_urls`), **last-processed date**. Emits `results/status/status.json`. **Single source of the cost model** (`COST_TRIM=0.05`, `COST_EXTRACT=0.15`; clean/publish free). | `python -m pipeline.client.status` |
| `dashboard.py` | Builds the offline picker `results/status/dashboard.html` (embeds `status.build()`). Tick occupations → see the cost preview + copy-paste commands (no file to download — the commands take the occupation name directly). Freshness colors, clickable source links, "what each step does". Fetch-needed cells are shown but are never runnable via these commands. | `python -m pipeline.client.dashboard` |
| `run.py` | The client's commands, by occupation name: `clean` (free) · `trim` (~$0.05/cell) · `extract` (~$0.15/cell) · `publish` (free) — all take `--professions a,b,c`. Every state with work to do for each named occupation is looked up live and included automatically (same `run` flag the dashboard uses). Each paid step prints its cell count, cost estimate, **and the model it's priced against** (moves if the model changes), then waits for a typed `yes`. Orchestrates existing stage modules — no reimplementation. | `python -m pipeline.client.run {clean\|trim\|extract\|publish} --professions a,b,c` |
| `refetch.sh` | Re-fetch one occupation/state (the only internet step). Justia is fetched headless via Scrapling — it clears the Cloudflare check itself, no browser window, nothing to click. One fetch at a time. | `bash pipeline/client/refetch.sh <occupation> <STATE,...>` |

Client-facing guide (plain English, no jargon): `CLIENT_GUIDE.md`.

## Freshness (why "done" isn't forever)

A cell's output depends on its input AND its recipe (prompt + schema + model + code). Re-pull a
corpus or change a prompt and a "done" cell is stale even though the file exists.
`pipeline/provenance.py` stamps each stage's output (content hashes, in `results/provenance/`,
so they survive `git clone`) and `check()` recomputes to report current/stale/unstamped. The
dashboard surfaces this: green = current, red = stale (rebuild, $), pale-green = provenance not
tracked yet. Baseline: the 7 published professions were backfilled `current` (re-extracted
Jul 2–6); the held-out cells are honestly `unstamped` until re-run. `provenance report` /
`provenance backfill [--professions …]`.

## Design constraints (why it's shaped this way)

- **Fewest commands, but every paid step separate from the free ones.** `clean`/`publish` are
  free and never prompt; `trim`/`extract` each cost money, so each is its own command and each
  confirms before spending. Bundling them would hide the cost.
- **DRY.** Cost numbers live only in `status.py`. `run.py` shells out to the real stage CLIs
  and calls `extract_state_batch.submit/poll` directly; the dashboard embeds `status.build()`.
  provenance's model strings are guarded by a test against each stage's `DEFAULT_MODEL`.
- **Fetching stays walled off.** It's the only step that touches the internet, so it's a
  separate script + guide, never mixed into the everyday clean/trim/extract/publish flow.
  A handed-off repo is already fetched. (Justia is headless via Scrapling — no browser to
  babysit — but the wall keeps the everyday flow offline and free.)
- **No queue file to download or pass around.** `run.py` takes `--professions <names>` and
  looks up which states are runnable itself, live, via `status.build()`'s `run` flag — the
  same thing the dashboard uses to color/count cells. One source of truth for "what's
  runnable," so a stale downloaded snapshot can't drift from what's actually on disk.
- **Costs are never a bare number.** Every printed estimate names the model it's priced
  against (`trim_state.DEFAULT_MODEL` / `extract_state_batch.DEFAULT_MODEL`), since the
  price is an Anthropic rate for that specific model, not a fixed cost of the step.
