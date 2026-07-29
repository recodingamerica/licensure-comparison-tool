# Client guide — set up, run, and publish the pipeline

Everything a non-programmer needs, start to finish: install once, then turn licensing law
into structured data, refresh a state that changed, and (optionally) publish to the live
site. You do **not** need to be a programmer — a Mac or Linux computer and a terminal.

The repo you received already contains the fetched licensing law for every occupation and
state we harvested; day to day you're just processing and publishing it.

---

## 1. First-time setup (once per machine)

**You need:**
- **Python 3.11 or newer** — check with `python3 --version`; install from
  <https://www.python.org/downloads/> if missing.
- **An Anthropic API key** — only for the two paid steps (`trim`, `extract`). To just *look
  at* the data or rebuild the site you don't need one. Get one at <https://console.anthropic.com/>.

**Run one command** from the repo's top folder:

```bash
bash setup.sh
```

It prints four steps and flags anything needing attention: checks Python, installs
everything (a few minutes the first time), optionally installs the fetch browser (**you can
let this fail** — you only need it to re-fetch a changed state), and checks for your API key.
Re-running `setup.sh` is safe; it skips what's done.

**Add your API key** (only if you'll run the paid steps): if setup created a `.env` file in
the top folder, open it, paste your key after `ANTHROPIC_API_KEY=` (no quotes, no spaces),
and save. `.env` is git-ignored, so your key is never committed.

---

## 2. Everyday — pick occupations and process them

**Pick with the dashboard.** Open it in any browser:

```bash
open pipeline/results/status/dashboard.html
# regenerate any time: pipeline/.venv/bin/python -m pipeline.client.dashboard
```

Each occupation shows how far every state has gotten and what finishing would cost:
- **green** — finished (structured data exists)   · **blue** — ready to process now
- **orange** — needs a fresh fetch first (§3)      · **grey** — no such law there / not checked

Tick what you want; the dashboard shows the exact commands to copy (nothing to download).

**Process what you picked** — run these from the top folder, naming the occupations
(comma-separated). Every state with work to do is included automatically. Only **trim** and
**extract** cost money, and each prints its cell count, the estimated cost, **and the AI
model that price is based on**, then waits for you to type `yes`:

```bash
pipeline/.venv/bin/python -m pipeline.client.run clean   --professions court_reporter,forester   # FREE
pipeline/.venv/bin/python -m pipeline.client.run trim    --professions court_reporter,forester   # ~$0.05/state
pipeline/.venv/bin/python -m pipeline.client.run extract --professions court_reporter,forester   # ~$0.15/state
pipeline/.venv/bin/python -m pipeline.client.run publish --professions court_reporter,forester   # FREE (shows it on the site)
```

`extract` submits a batch and waits; it's safe to close and re-poll later (it prints the
resume command). Finished data lands in `pipeline/results/structured/<occupation>/<state>.json`.
An already-current state is skipped and never charged again; a *stale* one (law or method
changed) is picked back up when you re-run the steps.

---

## 3. Re-fetch a state that changed (the only step that needs the internet)

If a state updates its statutes and you want fresh text, re-fetch it. The source (Justia)
shows a "Just a moment…" check, **but the fetcher clears it automatically — no browser
window, nothing to click.** Run one command and wait (a couple of minutes per state):

```bash
bash pipeline/client/refetch.sh <occupation> <STATE[,STATE,...]>
# e.g.  bash pipeline/client/refetch.sh court_reporter UT
#       bash pipeline/client/refetch.sh forester UT,ID,MT
```

**Only run one fetch at a time.** When it finishes it prints the §2 commands to run next for
the newly-fetched states.

---

## 4. Publish to the live website (optional — needs a one-time Vercel setup)

`run publish` (no flag) rebuilds an occupation's payload and uploads it — free and safe.
Adding `--deploy` also **pushes the public live site** (utah-licensing.vercel.app) so it
picks up the new data.

> If the maintainer handles deploys, you never need this — run `publish` without `--deploy`
> and tell them there's new data to push.

**One-time setup** (needs Node.js installed):

```bash
cd pipeline/publish/web
npm install                                       # site build deps
npx vercel login                                  # sign in to the account that owns the site
npx vercel link --yes --project utah-licensing    # connect this folder to the project
npx vercel env pull .env.local                    # pull BLOB_READ_WRITE_TOKEN + SITE_PASSWORD
cd ../../..
```

`vercel link` must target the **same Vercel project/org that hosts the live site** — if
unsure, ask the maintainer before linking.

**Deploy** (from the repo root, after building the data you want live):

```bash
pipeline/.venv/bin/python -m pipeline.client.run publish --professions dentistry,nursing --deploy
```

It prints exactly what will go live and waits for a typed `yes`. A deploy rebuilds the whole
site from the current blob payloads, so it reflects every uploaded occupation, not just the
ones you named. The site stays behind its password (`SITE_PASSWORD`); deploying doesn't change that.

---

## What each step does, and what it costs

| Step | Command | Internet? | Cost |
|------|---------|-----------|------|
| Fetch | `refetch.sh` | Yes — but automatic, nothing to click | free (just time) |
| Clean | `run clean` | No | free |
| Trim | `run trim` | No (calls an LLM) | ~$0.05/state — `run` prints the exact price + model first |
| Extract | `run extract` | No (calls an LLM) | ~$0.15/state — same |
| Publish | `run publish` | No | free (`--deploy` pushes the live site) |

Already-finished states are skipped, so re-running any command is always safe.

## If something goes wrong

| It says… | Do this |
|---|---|
| `python3: command not found` / `Python 3.x but 3.11+ required` | Install Python 3.11+ from python.org, re-run `bash setup.sh`. |
| A command errors that a package is missing | `pipeline/.venv/bin/pip install -r pipeline/requirements.txt`, then re-run. |
| A paid step can't authenticate | Your API key is missing/wrong — check `.env` (§1). |
| A paid step errors with "model not found" / "deprecated" | The AI vendor retired a model name. Open `pipeline/config/models.yaml` and change the retired name to the vendor's current equivalent (their deprecation notice names it). Everything reads models from that one file. |
| A step refuses with `SCHEMA_DIRTY` or `STALE_UPSTREAM` | The safety gate is protecting you: an input changed underneath. For `STALE_UPSTREAM` re-run the earlier steps (clean, then trim) for that occupation; for `SCHEMA_DIRTY` a schema file was modified without being saved to git — ask a maintainer before overriding. |
| A fetch comes back empty / stuck | The source's bot-wall may have changed; re-fetching needs a maintainer to update the fetch tool. Everyday clean/trim/extract still work on data you already have. |
| Anything else | Commands are safe to re-run — finished steps are skipped, and paid steps always ask before spending. |

---

For pipeline development (changing prompts/schema, adding source states) see `README.md` and
`CLAUDE.md`. Module map for this client tooling: [`pipeline/client/README.md`](pipeline/client/README.md).
