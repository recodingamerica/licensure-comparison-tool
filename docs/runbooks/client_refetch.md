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

Tick the occupations you want, watch the estimated cost at the bottom, then click
**Download my_queue.json**. Save that file into the repo's top folder.

---

## 2. Process the queue — a few commands

Run these from the repo's top folder, in order. Only **trim** and **extract** cost
money, and each one shows the estimate and asks you to type `yes` before spending.

    pipeline/.venv/bin/python -m pipeline.client.run clean   --queue my_queue.json   # FREE
    pipeline/.venv/bin/python -m pipeline.client.run trim    --queue my_queue.json   # ~$0.05/state
    pipeline/.venv/bin/python -m pipeline.client.run extract --queue my_queue.json   # ~$0.15/state

`extract` submits a batch and waits for the results. It's safe to close it and re-poll
later if needed — it prints the exact command to resume. The finished data lands in
`pipeline/results/structured/<occupation>/<state>.json`.

To make an occupation show up on the website, publish it (free):

    pipeline/.venv/bin/python -m pipeline.client.run publish --professions court_reporter,forester
    # add --deploy to also push the live site

The dashboard generates this line for whatever you selected. A green state in the
dashboard is up to date; a red one is *stale* (the law or the method changed) — re-run the
three steps above for it to rebuild.

**The paid steps need an Anthropic API key.** Put it in a file named `.env` in the repo
top folder: `ANTHROPIC_API_KEY=sk-ant-...`

---

## 3. Re-fetch a state that changed (the only step that needs a browser)

If a state updates its statutes and you want fresh text, you re-fetch it. Fetching is
the one step that needs a real Chrome window, because the source (Justia) shows a
"Just a moment…" check that only a genuine browser clears. This is usually quick.

    bash pipeline/client/refetch.sh <occupation> <STATE[,STATE,...]>
    # e.g.  bash pipeline/client/refetch.sh court_reporter UT
    #       bash pipeline/client/refetch.sh forester UT,ID,MT

If the fetch browser isn't running, the script prints the exact command to start Chrome
and what to click. In short:

1. In a new terminal, start Chrome with a debugging port:

       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
         --remote-debugging-port=9222 --user-data-dir=/tmp/justia-chrome

2. In that Chrome window, visit <https://law.justia.com/>. If a "Verify you are human"
   screen appears, wait for it to finish (or click the checkbox) until a normal page shows.
3. Leave Chrome open and re-run the `refetch.sh` command above.

**Only run one fetch at a time** — don't start a second `refetch.sh` while one is going.

After a re-fetch, process the new text with the commands from section 2 (the script
prints a ready-made queue line for exactly the states you fetched).

---

## What each step does (and what it costs)

| Step | Command | Needs internet? | Cost |
|------|---------|-----------------|------|
| Fetch | `refetch.sh` | Yes — a real Chrome | free (just time) |
| Clean | `run clean` | No | free |
| Trim | `run trim` | No (calls an LLM) | ~$0.05 / state |
| Extract | `run extract` | No (calls an LLM) | ~$0.15 / state |
| Publish | `run publish` | No | free |

Already-finished states are skipped automatically, so re-running a command is always safe.
