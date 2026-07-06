# pipeline/client — the client-facing handoff tooling

Everything a non-programmer needs to see pipeline state, pick occupations to turn into
data, run the (few) commands, publish, and re-fetch a state later. Read-only over the
committed repo; nothing here fetches or spends money on its own.

| File | What it is | Run |
|---|---|---|
| `status.py` | Data layer. Per (occupation, state): furthest stage, **freshness** (current/stale/unstamped via `pipeline.provenance`), cost-to-finish/refresh, **source URL(s)** (from corpus `chapter_urls`), **last-processed date**. Emits `results/status/status.json`. **Single source of the cost model** (`COST_TRIM=0.05`, `COST_EXTRACT=0.15`; clean/publish free). | `python -m pipeline.client.status` |
| `dashboard.py` | Builds the offline picker `results/status/dashboard.html` (embeds `status.build()`). Tick occupations → downloadable `my_queue.json` + copy-paste commands. Freshness colors, clickable source links, "what each step does". Fetch-needed cells are shown but never enter the queue. | `python -m pipeline.client.dashboard` |
| `run.py` | The client's commands over one queue file: `clean` (free) · `trim` (~$0.05/cell) · `extract` (~$0.15/cell) · `publish` (free, `--professions a,b,c`). Each paid step prints its estimate and waits for a typed `yes`. Orchestrates existing stage modules — no reimplementation. | `python -m pipeline.client.run {clean\|trim\|extract} --queue my_queue.json` / `... publish --professions a,b` |
| `refetch.sh` | Re-fetch one occupation/state via the CDP-Chrome path (the only internet step). Prints how to start Chrome if it isn't up. One fetch at a time. | `bash pipeline/client/refetch.sh <occupation> <STATE,...>` |

Client-facing guide (plain English, no jargon): `docs/runbooks/client_refetch.md`.

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
- **Fetching stays walled off.** It needs the CDP Chrome, so it's a separate script + guide,
  never mixed into the everyday clean/trim/extract/publish flow. A handed-off repo is already fetched.
