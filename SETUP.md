# Setup — start here

This repository turns state licensing law into structured, comparable data and a website.
This page gets you from "I just received the repo" to "I can run it." You do this **once**.

You do **not** need to be a programmer. You need a Mac or Linux computer, and about ten
minutes (mostly waiting on the install).

---

## 1. What you need first

- **Python 3.11 or newer.** Check by opening a terminal and running `python3 --version`.
  If it's missing or older, install it from <https://www.python.org/downloads/>.
- **An Anthropic API key** — but only for the two paid steps (`trim` and `extract`). If you
  only want to *look at* the data or rebuild the site, you don't need one. Get a key at
  <https://console.anthropic.com/>.

## 2. Run setup (one command)

From the repo's top folder, in a terminal:

```bash
bash setup.sh
```

It prints four steps as it goes and tells you if anything needs your attention:

1. Checks your Python version.
2. Creates the environment and installs everything (a few minutes the first time).
3. Optionally installs the fetch browser — **you can let this fail; you don't need it**
   unless you later re-fetch a state whose law changed. The repo you received is already fetched.
4. Checks for your API key. If it doesn't find one, it creates a `.env` file for you to
   paste your key into.

Re-running `setup.sh` is safe — it skips anything already done.

## 3. Add your API key (only if you'll run the paid steps)

If setup said it created a `.env` file, open it (it's in the top folder), paste your key
after `ANTHROPIC_API_KEY=`, and save. No quotes, no spaces. Example:

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

The `.env` file is private (git ignores it), so your key is never committed.

---

## 4. What you do from now on

You never run `setup.sh` again. Day to day you use the **dashboard** and **four commands**.
Full plain-English walkthrough: [`docs/runbooks/client_refetch.md`](docs/runbooks/client_refetch.md).

```bash
# See what's there — opens a page where you tick occupations and get copy-paste commands:
pipeline/.venv/bin/python -m pipeline.client.dashboard

# The four commands (clean + publish are free; trim + extract cost a little and ask first):
pipeline/.venv/bin/python -m pipeline.client.run clean   --professions <name>   # free
pipeline/.venv/bin/python -m pipeline.client.run trim    --professions <name>   # ~$0.05/state
pipeline/.venv/bin/python -m pipeline.client.run extract --professions <name>   # ~$0.15/state
pipeline/.venv/bin/python -m pipeline.client.run publish --professions <name>   # free
```

Re-fetching a state that changed its law is one more command (`refetch.sh`) — automatic,
no browser window, nothing to click. See section 3 of the walkthrough.

---

## What needs a developer (not the everyday flow)

Everything above is self-service. A couple of things still want someone technical:

- **Publishing the website to the internet** (a Vercel deploy). Building the data payload
  is free and self-service (`run publish`); pushing it live is a developer step — see
  [`docs/runbooks/client_deploy.md`](docs/runbooks/client_deploy.md).
- **Changing how extraction works** (the prompts, the schema, adding brand-new source
  states). That's pipeline development — see `CLAUDE.md` and `README.md`.

---

## If something goes wrong

| It says… | Do this |
|---|---|
| `python3: command not found` | Install Python 3.11+ from python.org, then re-run `bash setup.sh`. |
| `Found Python 3.x, but 3.11+ is required` | Install a newer Python and re-run. |
| A paid step says it can't authenticate | Your API key is missing or wrong — check `.env` (section 3). |
| A fetch comes back empty / stuck | The source's bot-wall may have changed; re-fetching needs a maintainer to update the fetch tool. Everyday clean/trim/extract still work on data you already have. |
| Anything else | The commands are safe to re-run — a step that already finished is skipped, and the paid steps always ask before spending. |
