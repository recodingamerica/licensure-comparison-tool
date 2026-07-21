# Client guide: run the pipeline & re-fetch a state later

This repo already contains the fetched licensing law for every occupation and state we
harvested. To turn that law into structured data — or to refresh a state that changed
its statutes — you run a few short commands. You do **not** need to be a programmer.

Everything runs from the repo's top folder using the bundled Python at
`pipeline/.venv/bin/python`. If a command errors that a package is missing, first run
`pipeline/.venv/bin/pip install -r pipeline/requirements.txt`.

---

## 1. Pick what to process — the dashboard

Open the dashboard in any browser:

    open pipeline/results/status/dashboard.html

(Regenerate it any time to reflect the current state of the repo:
`pipeline/.venv/bin/python -m pipeline.client.dashboard`.)

Each occupation shows how far every state has gotten and what it would cost to finish:

- **green** — already finished (structured data exists)
- **blue** — *ready*: the law is in the repo, you can process it now
- **orange** — needs a fresh fetch first (see section 3)
- **grey** — no such licensing law in that state / not yet checked

Tick the occupations you want and watch the estimated cost at the bottom — the
dashboard shows you the exact commands to copy. There's nothing to download; the
commands just name the occupations.

---

## 2. Process what you picked — a few commands

Run these from the repo's top folder, in order, naming the occupations you picked
(comma-separated). Every state that has work to do for a named occupation is
included automatically — you never need to list states by hand. Only **trim** and
**extract** cost money, and each one shows the cell count, the estimated cost, **and
the AI model that price is based on** (the price moves if the model changes), then
asks you to type `yes` before spending.

    pipeline/.venv/bin/python -m pipeline.client.run clean   --professions court_reporter,forester   # FREE
    pipeline/.venv/bin/python -m pipeline.client.run trim    --professions court_reporter,forester   # ~$0.05/state
    pipeline/.venv/bin/python -m pipeline.client.run extract --professions court_reporter,forester   # ~$0.15/state

`extract` submits a batch and waits for the results. It's safe to close it and re-poll
later if needed — it prints the exact command to resume. The finished data lands in
`pipeline/results/structured/<occupation>/<state>.json`.

To make an occupation show up on the website, publish it (free):

    pipeline/.venv/bin/python -m pipeline.client.run publish --professions court_reporter,forester
    # add --deploy to also push the live site

A state that's already up to date is skipped automatically and never charged for again
— a green state in the dashboard is up to date; a red one is *stale* (the law or the
method changed) — re-run the three steps above and it picks the stale ones back up.

**The paid steps need an Anthropic API key.** Put it in a file named `.env` in the repo
top folder: `ANTHROPIC_API_KEY=sk-ant-...`

---

## 3. Re-fetch a state that changed (the only step that needs the internet)

If a state updates its statutes and you want fresh text, you re-fetch it. This is the
one step that goes out to the internet. The source (Justia) shows a "Just a moment…"
check, **but the fetcher clears it automatically — no browser window opens and there is
nothing to click.** You just run one command and wait:

    bash pipeline/client/refetch.sh <occupation> <STATE[,STATE,...]>
    # e.g.  bash pipeline/client/refetch.sh court_reporter UT
    #       bash pipeline/client/refetch.sh forester UT,ID,MT

It takes a couple of minutes per state. **Only run one fetch at a time** — don't start a
second `refetch.sh` while one is going.

After a re-fetch, process the new text with the commands from section 2, naming the
same occupation — the newly-fetched states are picked up automatically. (The script
prints those three commands for you when it finishes.)

---

## What each step does (and what it costs)

| Step | Command | Needs internet? | Cost |
|------|---------|-----------------|------|
| Fetch | `refetch.sh` | Yes — but automatic, nothing to click | free (just time) |
| Clean | `run clean` | No | free |
| Trim | `run trim` | No (calls an LLM) | ~$0.05 / state at today's model — `run` always prints the exact price and model before spending |
| Extract | `run extract` | No (calls an LLM) | ~$0.15 / state at today's model — same |
| Publish | `run publish` | No | free |

Already-finished states are skipped automatically, so re-running a command is always safe.
