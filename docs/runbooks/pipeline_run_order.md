# Pipeline run order — the single "how do I run this" authority

This is the front door for **running** the pipeline. If you're asking "which command
do I run, and what does it touch?", start here. For what each *stage* does internally,
see the stages table in `README.md`; for adding a brand-new occupation end-to-end, see
[`adding_a_new_occupation.md`](adding_a_new_occupation.md).

All commands run from the repo root with the project venv:
`pipeline/.venv/bin/python -m <module>`.

---

## The one runner: `pipeline.pipeline_stages`

There is exactly **one** engine that walks the stage chain. Every other entry point
below is a thin caller of it. It defines the stage order **once** (`STAGES`), so
nothing else re-encodes "clean before trim".

```
STAGES:  pull → clean → trim → schema → extract → mapprep → publish → fanout
         └── cell ──┘   └cell┘  └prof─┘  └cell──┘  └prof──┘  └prof──┘  └global┘
```

**`run_to(target, prof, states, *, start, force, yes, dry_run, opts)`** runs the chain
from `start` up to and including `target`, for one profession, running only the units
that aren't already `current` (unless `force`). Because it walks the ordered `STAGES`
prefix, upstream can never run after downstream.

The **`start=` seam** is the whole trick — it decides how much of the chain a caller runs:

| `start=` | First stage run | Used by | Notes |
|---|---|---|---|
| `None` | `pull` (full chain) | full-chain runs, `--start pull` | **hits `pull`, which COMMITS to git** |
| `"clean"` | `clean` (no-pull) | `add_occupation` | text already on disk |
| `target` | only the target stage | `refresh_all` (`start="publish"`), `client/run` | treats upstream as a precondition |

**CLI** (this is the ex-`re_extract_queue` — batch re-extract from a `{prof: [states]}` file):

```bash
# batch re-extract a queue file up to the extract stage
python -m pipeline.pipeline_stages --queue my_queue.json --target extract

# a single profession/state chain, no pull (text already on disk)
python -m pipeline.pipeline_stages --profession optometry --states UT --target extract --start clean

# print the ordered plan, spend nothing
python -m pipeline.pipeline_stages --queue my_queue.json --target extract --dry-run
```

Flags: `--target` (default `extract`), `--start` (default `clean`), `--force` (re-run
even current cells), `--yes` (skip paid-stage cost prompts), `--dry-run`.

The cross-profession **fanout** (tag sheet, scope caps, scorecard, state/umbrella browse,
similarity, novel-direction) is `run_fanout(profs)` — a `global` stage that aggregates
across professions, so it runs **once per refresh**, not per profession. `refresh_all`
calls it after the per-profession publishes.

---

## Entry paths — pick by what you're doing

### `publish/refresh_all` — rebuild the site from existing extraction output
**No LLM. Deterministic reshaping of files already on disk.** Use after any data change
(re-extract, local corpus transform) to make the whole site consistent again, and to
deploy.

```bash
python -m pipeline.publish.refresh_all                       # incremental: changed professions only
python -m pipeline.publish.refresh_all --professions optometry
python -m pipeline.publish.refresh_all --force               # rebuild every profession
python -m pipeline.publish.refresh_all --deploy              # ...then redeploy Vercel (prod)
python -m pipeline.publish.refresh_all --dry-run             # print the plan, build nothing
```

Internally: `run_to("publish", p, start="publish")` per changed profession + `run_fanout`.
It **never re-extracts or re-runs map_prep** (those are the LLM stages) — if structured
data changed, run those first (via `client/run` or `pipeline_stages`), then run this.

- Incremental skip = **publish provenance** (a content hash of `structured/` + `map_prep/`).
  `--force` or an explicit `--professions` list rebuilds regardless of freshness.
- The publish adapter runs the **cross-field consistency gate** (hard-fail) before it ships.
- Gotchas: `build_frontend` is **slow** (~>2 min/profession — the per-state browse loop);
  run it backgrounded or with a long timeout. **Don't use `--payload-only` for a "just
  verify" run** — it zeros `browse_section_count` in the payload and uploads that (dirties
  Blob). `--deploy` runs `vercel --prod` from `pipeline/publish/web` (never from the repo
  root — the stray root `.vercel` links a different project).

### `client/run` — the non-coder handoff (per-stage, cost-gated, paid)
For running the **paid** stages a state at a time, with the cost gate and a status-derived
queue. This is the Utah OPLR operator path (`pipeline/client/`).

```bash
python -m pipeline.client.run clean   --professions podiatry,dentistry   # FREE
python -m pipeline.client.run schema  --professions podiatry             # ~$1.00/occupation, once — asks first
python -m pipeline.client.run trim    --professions podiatry             # ~$0.05/cell — asks first
python -m pipeline.client.run extract --professions podiatry             # ~$0.15/cell — asks first
python -m pipeline.client.run publish --professions podiatry             # FREE — build the payload
```

Each subcommand calls `run_to(stage, prof, states, start=stage)` — a **single stage** per
call. Queues + costs come from `pipeline.client.status` (one source of truth). See
[`CLIENT_GUIDE.md`](../../CLIENT_GUIDE.md).

### `discover/add_occupation` — a NEW occupation, full no-pull chain
The capstone for standing up an occupation whose parent corpus is already pulled. Runs
`clean → trim → schema → extract` via `run_to("extract", start="clean")`, then optionally
`map_prep → publish` if `--publish` and the occupation has ≥10 states.

```bash
python -m pipeline.discover.add_occupation --from-candidate "Public Adjuster"                 # dry-run plan
python -m pipeline.discover.add_occupation --from-candidate "Public Adjuster" --write         # register + extract
python -m pipeline.discover.add_occupation --from-candidate "Barber" --write --publish --yes  # all the way to a payload
```

- `--write` persists + runs (default is a dry-run plan); `--publish` also builds the payload
  (if ≥10 states); `--yes` skips the per-stage cost prompts; `--apply-cross-ref` wires
  density-scan candidate links into `corpus_overrides.yaml` and extracts them too.
- **Behavior note:** the cross-field consistency gate fires **only at publish**. Without
  `--publish` there is no consistency check — that's intended (nothing is shipping yet).
- Going *fully live* still needs a manual `build_state_browse.PROFESSIONS` edit + a deploy.

### `ingest/refresh_corpus` — the annual re-pull loop (the pull stage engine)
The `pull` stage's engine (`refresh_item`): re-pulls a committed corpus, health-checks it,
and **commits iff healthy** (a regression is reverted and reported). Normally run unattended
as the **annual refresh** with `--until-done` (self-healing) + `caffeinate`.

A single hung cell hits the per-item timeout and aborts the whole run *by design*; `--until-done`
relaunches (as `--resume --skip-held`) after each abort, skipping the timed-out/held cells so
every pass makes forward progress and the loop converges. It's bounded by max-passes and stops
on a no-progress pass, so it can't hot-loop. This replaced the old external
`annual2026_watchdog.sh` bash wrapper — the loop now lives inside the module.

The timeout / breaker / max-passes / retry defaults live in **`config/limits.yaml`** under
`refresh:` (item_timeout_seconds 1800, breaker 6, max-passes 120, pull_retries 2) — so the
invocation carries no hardcoded seconds. `--item-timeout` / `--breaker` / `--max-passes` still
override per-run.

```bash
# self-healing annual refresh, hand-started:
PY=pipeline/.venv/bin/python
nohup $PY -m pipeline.ingest.refresh_corpus --all-professions --run-id annual2026 \
  --until-done --yes \
  >> pipeline/results/status/annual2026_resume.log 2>&1 &
RC=$(pgrep -f 'refresh_corpus.*annual2026' | head -1); nohup caffeinate -i -s -w "$RC" &
```

---

## What commits to git vs what doesn't

| Path / stage | Writes | Commits to git? |
|---|---|---|
| `pull` stage / `refresh_corpus` / `refresh_item` | `results/text/` + corpus | **YES** (commit-iff-healthy) |
| clean · trim · schema · extract · mapprep | `results/*/` | no |
| publish · fanout / `refresh_all` | payloads + **Vercel Blob** | no (uploads to Blob) |
| `--deploy` | — | no (deploys to Vercel prod) |

### The refresh pause-before-commit rule (index.lock race)
The annual refresh auto-commits in the background. **Before you commit, or run anything
that commits (the `pull` stage — full chain `start=None`, or `--start pull`), pause it
first**, or you'll hit a git `index.lock` race:

```bash
pkill -f refresh_corpus
# ... do the thing (commit, or the pull run) ...
# relaunch (it resumes from the committed status file):
PY=pipeline/.venv/bin/python
nohup $PY -m pipeline.ingest.refresh_corpus --all-professions --run-id annual2026 \
  --until-done --yes \
  >> pipeline/results/status/annual2026_resume.log 2>&1 &
RC=$(pgrep -f 'refresh_corpus.*annual2026' | head -1); nohup caffeinate -i -s -w "$RC" &
```

Check it's alive: `pgrep -f 'refresh_corpus.*annual2026'`.
The publish/client/`add_occupation` paths start at `clean` or later and never touch the
pull stage, so they're safe to run alongside the refresh.

---

## Quick decision guide

- **Data already extracted, just rebuild/ship the site** → `refresh_all` (`--deploy` to ship).
- **Re-extract many (prof, state) cells** → `pipeline_stages --queue file.json --target extract`.
- **Run one paid stage, cost-gated, non-coder** → `client/run <stage> --professions ...`.
- **Stand up a brand-new occupation (corpus already pulled)** → `add_occupation --write [--publish]`.
- **Re-pull committed corpora (annual check)** → `refresh_corpus --until-done` (pause before any commit).
