# scrape_probe

Rerunnable pipeline that probes a list of statute / reference URLs and records, per target:

- HTTP status under three fetch strategies (plain `requests`, `requests` + browser UA, `curl_cffi` with Chrome TLS fingerprint)
- `robots.txt` allowance + crawl-delay
- Content signals (link count, text length, frames, JS-rendering heuristic, parsed `<title>`)
- A snapshot of the response body (`results/snapshots/<id>.html`) for spot-checking
- A classification: `ok` / `partial` / `js_required` / `blocked` / `error` with a one-line reason

## Usage

```sh
.venv/bin/python probe.py
```

Outputs (overwritten each run):

- `results/probe_results.json` — full structured records
- `results/probe_results.csv` — flat summary
- `results/probe_report.md` — readable per-classification table
- `results/snapshots/<id>.html` — raw response body (capped at 2 MB)
- `logs/probe.log` — run log

To compare runs, copy `results/` before rerunning.

## Adding / changing targets

Edit `targets.csv`. Columns: `id, tier_guess, kind, state, url, robots_url, probe_selector, notes`.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install requests beautifulsoup4 curl-cffi
```

## What classifications mean

- **ok** — static HTML or structured (JSON/XML/zip) response, no obvious need for a browser.
- **partial** — responded, but body is thin / frame-based / few links. Usable but each entry needs follow-up fetches.
- **js_required** — body parsed but content is JS-rendered (heavy scripts, few real links). Needs Playwright or an API.
- **blocked** — non-2xx (403/401/429). Often Cloudflare or auth.
- **error** — network error, 4xx other than blocked, or 5xx.

## Caveats

- The "needs JS" heuristic looks at body text length vs script weight + explicit hints. It can mislabel pages that are mostly script but still have a real link list (the classifier compensates by promoting any page with ≥50 links to `ok`).
- A single-URL probe per host doesn't prove every page on that host scrapes the same way. Once a site is classified `ok`, validate by deep-linking into a known statute chapter before building a full scraper.
- `robots.txt` allowance is a *publisher policy* signal, not a ban. Respect it; getting a 200 doesn't mean you should crawl.
