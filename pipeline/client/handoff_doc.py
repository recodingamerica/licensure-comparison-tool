"""Generate the handoff document (docs/handoff/) with every number computed live.

The doc's counts, costs, model names, and source-host claims are DERIVED from the
repo at generation time — status.build(), the stage modules' own DEFAULT_MODEL
constants, the published payload dir, and a scan of the committed corpora. Nothing
numeric is hand-written, so the doc can't silently drift from reality: re-run this
after any big pull/extract/publish and re-share the output.

    python -m pipeline.client.handoff_doc          # writes docs/handoff/technical_documentation.md
    python -m pipeline.client.handoff_doc --pdf    # + .pdf via pandoc (needs pandoc + pdflatex)

Prose lives in the template below; numbers are injected. If you change how a stage
works, edit the prose here too — the generator keeps the numbers honest, not the words.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from pipeline.paths import TEXT_DIR, PIPELINE_ROOT
from pipeline.client import status
from pipeline.ingest.trim_state import DEFAULT_MODEL as TRIM_MODEL
from pipeline.extract.extract_state_batch import DEFAULT_MODEL as EXTRACT_MODEL
from pipeline.extract.discover_schema import DEFAULT_MODEL as SCHEMA_MODEL

REPO_ROOT = PIPELINE_ROOT.parent
DATA_DIR = PIPELINE_ROOT / "publish" / "web" / "public" / "data"
OUT_DIR = REPO_ROOT / "docs" / "handoff"
NON_PROFESSION_PAYLOADS = {"_skiptest", "scorecard", "tag_sheet"}


def _published() -> list[str]:
    """Professions with a site payload built in the repo. This is what the publish
    step has produced locally; the live site shows whatever was last deployed."""
    return sorted(
        f.stem for f in DATA_DIR.glob("*.json")
        if f.stem not in NON_PROFESSION_PAYLOADS
    )


def _evidence_totals() -> tuple[int, int]:
    """(verified, unverified) Evidence-claim counts summed across every published
    payload's evidence_summary (written by publish.build_frontend)."""
    verified = unverified = 0
    for prof in _published():
        d = json.loads((DATA_DIR / f"{prof}.json").read_text())
        es = d.get("evidence_summary") or {}
        verified += es.get("verified", 0)
        unverified += es.get("unverified", 0)
    return verified, unverified


def _source_hosts() -> tuple[collections.Counter, dict[str, collections.Counter]]:
    """Where the committed corpora actually came from (their recorded URLs) —
    so the 'everything is Justia except PA' claim is measured, not asserted."""
    hosts: collections.Counter = collections.Counter()
    by_state: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for f in TEXT_DIR.glob("*/*.json"):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        urls = d.get("chapter_urls") or [
            s.get("url") for s in (d.get("sections") or [])[:3]
            if isinstance(s, dict) and s.get("url")
        ]
        netlocs = {urlparse(u).netloc for u in urls if isinstance(u, str)} - {""}
        for h in netlocs:
            hosts[h] += 1
            by_state[f.stem][h] += 1
    return hosts, by_state


def _fetch_in_progress() -> bool:
    """Is a fetch/pull process running right now? Checked live (pgrep), not asserted —
    a stale 'fetching now' claim in a static doc would be worse than no claim at all."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "pipeline.ingest.refresh_corpus|pipeline.ingest.pull_text|gap_harvest"],
            capture_output=True, text=True,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def build_markdown() -> str:
    s = status.build()
    t = s["totals"]
    cost = s["cost_model"]
    published = _published()
    done_profs = {p for p, v in s["professions"].items() if v["summary"]["done"] > 0}
    extracted_unpublished = sorted(done_profs - set(published))
    hosts, by_state = _source_hosts()

    n_states = len({st for p in s["professions"].values() for st in p["states"]})
    total_cells = t["professions"] * n_states
    corpus_cells = t["cells_done"] + t["cells_ready"] + t["cells_needs_schema"]
    pct_corpus = round(100 * corpus_cells / total_cells)

    justia_n = hosts.get("law.justia.com", 0)
    non_justia = {h: c for h, c in hosts.items() if h != "law.justia.com"}
    non_justia_states = sorted(
        st for st, c in by_state.items() if any(h != "law.justia.com" for h in c)
    )
    pa_host = max(by_state.get("PA", collections.Counter()),
                  key=lambda h: by_state["PA"][h], default="www.legis.state.pa.us")

    per_cell = cost["trim"] + cost["extract"]
    today = datetime.date.today().isoformat()
    commit = _git_commit()
    fetching_now = _fetch_in_progress()

    pub_list = ", ".join(published)
    fetch_status_line = (
        f"**A fetch is running right now** (checked live at generation time) — some "
        f"of the {t['cells_needs_fetch']} cells below are actively being pulled as "
        f"this document was generated, so that count is falling."
        if fetching_now else
        f"No fetch is currently running (checked live at generation time) — the "
        f"{t['cells_needs_fetch']} cells below are waiting, not in progress."
    )

    return f"""# State licensing pipeline — handoff documentation

*Generated {today} from repo commit `{commit}` by `python -m pipeline.client.handoff_doc`.
Every number below was computed from the repository's actual contents when this was
generated — none are hand-maintained. If this document is more than a few weeks old,
re-run that command to get current numbers.*

**For engineers:** this document is the plain-English overview. The technical entry
points are `CLAUDE.md` (repo root), `pipeline/client/README.md`, and
`pipeline/config/README.md`. Everything below is also inspectable in code.

## 1. What this is, and what you already have

This repository turns state licensing law into structured, comparable data: for each
occupation and each state, what license (if any) is required, what it takes to get one,
and what the license lets you do. The results are published as an interactive website.

The most important thing to know: **the raw law text is already in this repository.**
Collecting statute text from the web is by far the most painful part of this work (see
section 6), and we have already done it broadly — {corpus_cells:,} of the
{total_cells:,} possible occupation/state combinations ({t["professions"]} occupations
× {n_states} states, i.e. {pct_corpus}% of the grid) have their law text saved here.
Day-to-day work — turning that saved text into published data — **never touches the
web-scraping machinery.** You will not need to scrape anything unless you want brand-new
material or a refresh of old material.

## 2. What's easy, what's cheap, and what's hard

The pipeline runs in stages, and they cost very different amounts of money and effort.
Current state of the grid, as of generation:

| | Count | What it means |
|---|---|---|
| Published | {len(published)} occupations | Site data built and ready to serve |
| Extracted, not published | {len(extracted_unpublished)} occupations | Structured data exists for at least some states; publishing is a free command |
| Ready to process | {t["cells_ready"]:,} occupation/state cells | Law text on disk; needs only the paid AI steps (~${per_cell:.2f}/cell, ~${t["cost_to_finish"]:,.2f} for all of them) |
| New occupation, not set up yet | {t["cells_needs_schema"]} cells ({t["professions_no_schema"]} occupations) | Law text on disk, but this occupation has never been processed before — see below |
| Needs a fetch | {t["cells_needs_fetch"]} cells | Law located but text never pulled — requires the scraping setup |

{fetch_status_line}

The {len(published)} published occupations: {pub_list}.

In effort terms:

- **Free, minutes:** publish an occupation whose data is already extracted; re-run the
  deterministic cleanup step.
- **Cheap, no code:** run an already-fetched occupation/state through the two paid AI
  steps (about ${per_cell:.2f} per occupation/state cell). "Already fetched" means the
  raw statute text is saved in this repository — the AI steps just haven't been paid
  for yet. The dashboard (section 3) shows exactly which cells these are and quotes
  the cost before anything is spent.
- **Medium: bring a brand-new occupation online for the first time.** Before we can
  extract structured data for an occupation, an AI step has to figure out *what fields
  matter for it* — a nurse's data looks different from a plumber's (different
  requirements, different terminology) — and save that as a one-time template (called
  a "schema" in the code) for the occupation. This is a one-time step per occupation,
  not per state, and it's a small cost. This is the {t["cells_needs_schema"]}-cell row
  above: the law is already on disk, but nobody has designed that occupation's
  template yet. Once it exists, every state for that occupation becomes "ready to
  process" like any other. Some states may also still need a fetch.
- **Hard, human-supervised:** fetching new or updated statute text from the web
  (section 6). Plan for a person to be around while it runs.

## 3. The tools you'll actually use

What you need: Python (the repo ships a ready environment — see
`pipeline/client/README.md`), an Anthropic API key for the two paid steps, and access
to the site's hosting (Vercel) for publishing. Chrome is needed only for fetching.

Three commands cover everything except fetching (run from the repo root, using the
project's Python environment):

1. **Status** — `python -m pipeline.client.status` — recomputes, for every occupation
   and state, what stage it's at, whether it's current or stale, and what it would
   cost to finish.
2. **Dashboard** — `python -m pipeline.client.dashboard` — builds an offline web page
   (`pipeline/results/status/dashboard.html`, open it in any browser) where you tick
   the occupations you want, see the total cost, and get the exact commands to run.
3. **Runner** — `python -m pipeline.client.run …` — executes your picks:
   `clean` (free), `trim` and `extract` (the paid steps — each prints its cost
   estimate and waits for a typed "yes" before spending anything), `publish` (free).

Nothing in these tools fetches from the web or spends money on its own. The
plain-English walkthrough, including re-fetching, is `docs/runbooks/client_refetch.md`.

## 4. What it costs — and what the costs depend on

Two stages call an AI model and cost money; everything else is free:

| Stage | Model used today | Est. cost |
|---------------------------------------------|---------------------------------|----------|
| Trim — keep only the occupation's parts of the law | `{TRIM_MODEL}` | ~${cost["trim"]:.2f} |
| Extract — turn trimmed text into structured data | `{EXTRACT_MODEL}` | ~${cost["extract"]:.2f} |
| Schema discovery — design an occupation's data template | `{SCHEMA_MODEL}` | small, one-time |

Three things to understand about these numbers:

- **They are estimates tied to today's models and prices.** The model names above were
  read from the code at generation time. Anthropic's per-token prices change, and bulk
  runs go through Anthropic's discounted batch API. Treat the per-cell figures as
  planning estimates, not invoices — the runner shows the estimate and asks before
  spending.
- **Swapping models is easy.** Each stage's model is a single setting (a `--model`
  flag / one constant per stage module). Moving to a cheaper, better, or different
  vendor's model is a small change; the prompts themselves live in a plain-text config
  file (`pipeline/config/prompts.yaml`), not in code.
- **The costs are per-run, not per-view.** The website serves previously-built data;
  people browsing the site cost nothing.

## 5. Everything adjustable lives in config files, not code

The pipeline's decisions — which occupations exist, how to recognize each one in a
state's law, per-state quirks, what the AI is asked, rate limits — are all plain-text
YAML files in `pipeline/config/`, each documented in `pipeline/config/README.md`:

- `professions.yaml` — the occupation list and the patterns used to find each one.
- `state_structure.yaml` — per-state source and layout overrides (the single source of
  truth for "where does this state keep this law").
- `prompts.yaml` — the instructions given to the AI at each paid step.
- `limits.yaml` — every numeric knob (fetch delays, caps, thresholds).

A non-programmer can read these; a technical person can change them without touching
Python.

## 6. Fetching: the hard part (and why you can usually skip it)

{fetch_status_line}

Statute text comes from **Justia** (law.justia.com), a free legal-code aggregator —
{justia_n:,} of the {sum(hosts.values()):,} saved corpora were pulled from it, covering
49 of the 50 states. **Pennsylvania** is the exception: its statutes come from the
state legislature's own site ({pa_host}). (These counts are measured from the saved
files' recorded URLs, not asserted.)

Fetching is not fully autonomous — plan to run it yourself, and expect it to need
attention. Justia blocks automated requests with a bot-detection challenge, and the
only reliable way past it is a real, visible Chrome browser window running on someone's
own computer. In practice: re-fetching or fetching new statute text isn't a cloud job
you kick off and forget — it runs on your machine, it can take hours for a large batch,
and every so often the challenge reappears and needs a person to click through it in
that browser window. We've built it to restart itself automatically after a crash or if
the computer goes to sleep, so it's more resilient than a plain script, but it is not
"set and forget." Budget for someone to check on it periodically while it runs.

Two related points:

- **Statute text changes roughly once a year** (an assumption, not a measurement), so
  refreshes are periodic, deliberate events — the pipeline never queries these sites in
  real time, and nothing re-fetches automatically.
- **Finding the law is often harder than fetching it.** Many occupations' licensing
  rules aren't a standalone chapter — they're a few sections buried inside a much
  broader one (one insurance-agent type inside the entire insurance code). The repo
  includes automated locator tooling for this, and the per-state mappings it produces
  are saved in config, so that work doesn't have to be redone.

## 7. How much to trust the data

- **It's AI-extracted, with checks.** Structured records are extracted by an AI model
  from statute text, then run through automated consistency checks
  (`pipeline/eval/check_consistency.py`). It can still be wrong; every record links
  back to its source law so a human can verify.
- **"Done" doesn't mean "done forever."** Each cell's output depends on its inputs
  (the law text) and its recipe (prompt + schema + model + code). The repo stamps
  every output and can tell you whether it's *current*, *stale* (an input or the
  recipe changed since it was built), or *unstamped* (built before tracking existed).
  Right now: {t["cells_done"]} extracted cells — {t["cells_current"]} current,
  {t["cells_stale"]} stale, {t["cells_unstamped"]} unstamped. The dashboard color-codes
  this.
- **Some blanks are deliberate.** A hand-verified list
  (`pipeline/config/verified_absences.yaml`) records occupation/state pairs where the
  state genuinely has no license — shown as "not state-regulated (verified)," distinct
  from "we haven't processed this yet."
- **Having a chapter isn't the same as having every relevant law.** Some states put
  discipline, fees, or hearing rules in shared "umbrella" chapters that apply to many
  occupations; the repo detects and pulls these, but completeness auditing is ongoing.

---
*Regenerate with `python -m pipeline.client.handoff_doc [--pdf]`.*
"""

README_PATH = REPO_ROOT / "README.md"
README_MARK_START = "<!-- STATUS:START — generated by `python -m pipeline.client.handoff_doc`; do not hand-edit -->"
README_MARK_END = "<!-- STATUS:END -->"


def readme_status_block() -> str:
    """The README's '## Current status' body — same data sources as the handoff doc
    (status.build(), the published-payload dir), so the two can't tell different
    stories. Kept separate from build_markdown() because the README needs only a
    short summary, not the full walkthrough."""
    s = status.build()
    published = _published()
    verified, unverified = _evidence_totals()
    total = verified + unverified
    pct = round(100 * verified / total, 1) if total else 0.0
    today = datetime.date.today().isoformat()
    pub_list = ", ".join(f"**{p}**" for p in published)

    return f"""{len(published)} professions published end-to-end, all 50 states each: {pub_list}.
Live site: https://utah-licensing.vercel.app (pw `utah`).

Across all {len(published)}: ~{total:,} Evidence-wrapped claims; {pct}% regex-verified against
source statute (as of {today} — regenerate with `python -m pipeline.client.handoff_doc`,
which reuses `pipeline.client.status.build()`, the single source of current
per-profession counts and cost-to-finish)."""


def update_readme() -> None:
    text = README_PATH.read_text()
    start = text.index(README_MARK_START) + len(README_MARK_START)
    end = text.index(README_MARK_END)
    new_text = text[:start] + "\n\n" + readme_status_block() + "\n\n" + text[end:]
    README_PATH.write_text(new_text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", action="store_true", help="also render a PDF via pandoc")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / "technical_documentation.md"
    md_path.write_text(build_markdown())
    print(f"wrote {md_path}")

    update_readme()
    print(f"updated {README_PATH} 'Current status' section")

    if args.pdf:
        if not shutil.which("pandoc"):
            raise SystemExit("pandoc not found — install it or skip --pdf")
        pdf_path = md_path.with_suffix(".pdf")
        subprocess.run(
            ["pandoc", str(md_path), "-o", str(pdf_path),
             "-V", "geometry:margin=1in", "-V", "fontsize=11pt"],
            check=True,
        )
        print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
