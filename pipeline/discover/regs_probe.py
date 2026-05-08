"""Quick reachability probe for state administrative-code (regulations) sites.

For each state in regs_targets.csv: try plain requests → curl_cffi → playwright.
Record what came back. Output regs_probe_results.{csv,json} + regs_probe_report.md.

This is a reachability check ONLY — does NOT try to drill into the licensing
board's chapters. That's the next pass once we know which sites respond.
"""

from __future__ import annotations

import csv
import json
import time
import urllib.parse
from dataclasses import asdict, dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as cffi_requests
    HAVE_CFFI = True
except ImportError:
    HAVE_CFFI = False

try:
    from playwright.sync_api import sync_playwright
    HAVE_PW = True
except ImportError:
    HAVE_PW = False


ROOT = Path(__file__).parent
TARGETS = ROOT / "regs_targets.csv"
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

UA_BROWSER = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 25
DELAY = 1.5


@dataclass
class RegsProbe:
    id: str
    state: str
    url: str
    notes: str
    status: int | None = None
    strategy: str | None = None
    bytes_html: int = 0
    title: str | None = None
    body_text_len: int = 0
    link_count: int = 0
    looks_js_shell: bool = False
    error: str | None = None
    classification: str = ""


def fetch_requests(url: str):
    try:
        r = requests.get(url, headers={"User-Agent": UA_BROWSER}, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code, r.text, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def fetch_cffi(url: str):
    if not HAVE_CFFI:
        return None, None, "no_curl_cffi"
    try:
        r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT, allow_redirects=True)
        return r.status_code, r.text, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


_PW = {"p": None, "b": None, "c": None}


def _ensure_pw():
    if _PW["c"] is None:
        _PW["p"] = sync_playwright().start()
        _PW["b"] = _PW["p"].chromium.launch(headless=True)
        _PW["c"] = _PW["b"].new_context(user_agent=UA_BROWSER)
    return _PW["c"]


def shutdown_pw():
    try:
        if _PW["c"]: _PW["c"].close()
        if _PW["b"]: _PW["b"].close()
        if _PW["p"]: _PW["p"].stop()
    except Exception:
        pass


def fetch_pw(url: str):
    if not HAVE_PW:
        return None, None, "no_playwright"
    try:
        ctx = _ensure_pw()
        page = ctx.new_page()
        try:
            r = page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        except Exception as e:
            page.close()
            return None, None, f"goto: {e}"
        try:
            page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass
        # Extra settle time for client-rendered content (JS apps that finish after networkidle)
        try:
            page.wait_for_timeout(2_000)
        except Exception:
            pass
        s = r.status if r else None
        h = page.content()
        page.close()
        return s, h, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def analyze(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else None)
    body = soup.body
    body_text = body.get_text(" ", strip=True) if body else ""
    links = soup.find_all("a", href=True)
    scripts = sum(len(s.get_text() or "") for s in soup.find_all("script"))
    looks_js_shell = (len(body_text) < 500 and scripts > len(body_text) * 4)
    return {
        "title": title and title[:160],
        "body_text_len": len(body_text),
        "link_count": len(links),
        "looks_js_shell": looks_js_shell,
    }


def classify(p: RegsProbe) -> tuple[str, str]:
    if p.error and p.status is None:
        return "error", p.error
    if p.status is None:
        return "error", "no response"
    if p.status in (401, 402, 403, 451):
        return "blocked", f"http {p.status}"
    if p.status == 429:
        return "blocked", "rate limited"
    if p.status >= 400:
        return "error", f"http {p.status}"
    if p.looks_js_shell:
        return "js_required", f"js shell ({p.body_text_len} chars body)"
    if p.body_text_len < 300:
        return "thin", f"body {p.body_text_len} chars"
    if p.link_count < 5:
        return "thin", f"{p.link_count} links"
    return "ok", f"{p.link_count} links, {p.body_text_len} chars body"


def probe_one(row: dict, last_host: dict) -> RegsProbe:
    p = RegsProbe(id=row["id"], state=row["state"], url=row["url"], notes=row["notes"])
    host = urllib.parse.urlparse(row["url"]).netloc
    if last_host.get("h") == host:
        time.sleep(DELAY)
    last_host["h"] = host

    print(f"[{p.state}] {p.url}", flush=True)
    # Try requests → cffi → playwright. Escalate if response is thin even when 200.
    for strat, fn in (("requests", fetch_requests), ("cffi", fetch_cffi), ("playwright", fetch_pw)):
        status, html, err = fn(p.url)
        if status and 200 <= status < 300 and html:
            p.status = status
            p.strategy = strat
            p.bytes_html = len(html)
            meta = analyze(html)
            p.title = meta["title"]
            p.body_text_len = meta["body_text_len"]
            p.link_count = meta["link_count"]
            p.looks_js_shell = meta["looks_js_shell"]
            # Escalate to next strategy if: JS shell, or content is very thin (<300 chars / <5 links)
            thin = p.body_text_len < 300 or p.link_count < 5
            if not (p.looks_js_shell or thin):
                break
            # else: keep going, try the next strategy
        else:
            if err:
                p.error = err
            elif status:
                p.status = status
                p.error = f"http {status}"
            time.sleep(DELAY)
    p.classification, reason = classify(p)
    print(f"  -> {p.classification} ({reason}, strat={p.strategy})", flush=True)
    return p


def main() -> None:
    with TARGETS.open() as f:
        targets = list(csv.DictReader(f))
    last_host: dict = {}
    results: list[RegsProbe] = []
    for row in targets:
        try:
            results.append(probe_one(row, last_host))
        except Exception as e:
            results.append(RegsProbe(id=row["id"], state=row["state"], url=row["url"],
                                     notes=row["notes"], error=str(e), classification="error"))
    shutdown_pw()

    out_json = RESULTS / "regs_probe_results.json"
    out_json.write_text(json.dumps([asdict(r) for r in results], indent=2))
    out_csv = RESULTS / "regs_probe_results.csv"
    fields = ["state", "id", "classification", "strategy", "status", "title",
              "link_count", "body_text_len", "looks_js_shell", "error", "url", "notes"]
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            w.writerow({k: getattr(r, k) for k in fields})

    # Markdown report
    out_md = RESULTS / "regs_probe_report.md"
    tally: dict = {}
    for r in results:
        tally[r.classification] = tally.get(r.classification, 0) + 1
    lines = ["# State Regulations (Admin Code) Reachability Probe", "",
             f"50 states. Tally: `{tally}`.", "",
             "Each row is one state's administrative-code site (regulations, not statutes). Tested with cheap fetch first, escalating to curl_cffi and Playwright as needed.", "",
             "| State | Class | Strategy | Status | Links | Body chars | Title | URL |",
             "|---|---|---|---|---:|---:|---|---|"]
    for r in sorted(results, key=lambda x: x.state):
        title = (r.title or "").replace("|", "/")[:80]
        url = r.url
        lines.append(f"| {r.state} | {r.classification} | {r.strategy or '—'} | {r.status or ''} | {r.link_count} | {r.body_text_len} | {title} | <{url}> |")
    lines.append("")
    out_md.write_text("\n".join(lines))
    print(f"\nwrote {out_json}, {out_csv}, {out_md}")
    print(f"tally: {tally}")


if __name__ == "__main__":
    main()
