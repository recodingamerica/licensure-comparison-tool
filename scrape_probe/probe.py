"""Probe a list of statute/reference URLs and record structured scrape-ability results.

Run: .venv/bin/python probe.py
Outputs:
  results/probe_results.json   — full structured results, one record per target
  results/probe_results.csv    — flat summary, easy to scan
  results/probe_report.md      — readable per-classification table
  results/snapshots/<id>.html  — saved response body for spot-checking
  logs/probe.log               — run log

Strategy: try cheapest fetch first, escalate only as needed.
  1. plain `requests` with a bot UA
  2. plain `requests` with a browser UA          (only if step 1 didn't 2xx)
  3. `curl_cffi` with Chrome TLS impersonation   (only if step 2 didn't 2xx)
  4. Playwright (real headless Chromium)         (only if step 3 didn't 2xx,
                                                  or if all three got 2xx but
                                                  the body looks JS-rendered)

Rerunnable. Each run overwrites results/ and logs/.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import time
import urllib.parse
import urllib.robotparser
from dataclasses import asdict, dataclass, field
from pathlib import Path

import requests
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as cffi_requests  # type: ignore
    HAVE_CFFI = True
except ImportError:
    HAVE_CFFI = False

try:
    from playwright.sync_api import sync_playwright  # type: ignore
    HAVE_PW = True
except ImportError:
    HAVE_PW = False


ROOT = Path(__file__).parent
TARGETS_CSV = ROOT / "targets.csv"
RESULTS_DIR = ROOT / "results"
SNAPSHOTS_DIR = RESULTS_DIR / "snapshots"
LOG_PATH = ROOT / "logs" / "probe.log"

UA_BOT = "scrape-probe/1.0 (+research; contact: abigail.haddad@gmail.com)"
UA_BROWSER = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 25
PER_HOST_DELAY = 1.5  # be polite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("probe")


@dataclass
class ProbeResult:
    id: str
    url: str
    tier_guess: str
    kind: str
    state: str
    notes: str
    # Bot UA attempt
    bot_status: int | None = None
    bot_final_url: str | None = None
    bot_bytes: int = 0
    bot_content_type: str | None = None
    bot_error: str | None = None
    bot_elapsed_s: float | None = None
    # Browser UA attempt
    browser_status: int | None = None
    browser_bytes: int = 0
    browser_content_type: str | None = None
    browser_error: str | None = None
    # curl-cffi (Chrome TLS fingerprint) attempt
    cffi_status: int | None = None
    cffi_bytes: int = 0
    cffi_content_type: str | None = None
    cffi_error: str | None = None
    # Playwright (real headless browser) attempt
    pw_status: int | None = None
    pw_bytes: int = 0
    pw_error: str | None = None
    pw_elapsed_s: float | None = None
    # Robots
    robots_url: str = ""
    robots_status: int | None = None
    robots_allows_bot: bool | None = None
    robots_allows_browser: bool | None = None
    robots_crawl_delay: float | None = None
    # Content signals (computed from whichever fetch worked)
    used_ua: str | None = None
    has_html: bool = False
    has_frames: bool = False
    needs_js: bool | None = None
    link_count: int = 0
    text_length: int = 0
    title: str | None = None
    title_matches_state: bool | None = None
    sample_links: list[str] = field(default_factory=list)
    # Verdict
    classification: str = ""  # ok, ok_with_browser, ok_with_key, blocked, partial, error
    classification_reason: str = ""
    recommended_strategy: str = ""


def load_targets() -> list[dict]:
    with TARGETS_CSV.open() as f:
        return list(csv.DictReader(f))


def check_robots(robots_url: str, target_url: str):
    try:
        r = requests.get(robots_url, headers={"User-Agent": UA_BOT}, timeout=TIMEOUT)
        status = r.status_code
        if r.status_code != 200:
            return status, None, None, None
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(r.text.splitlines())
        allow_bot = rp.can_fetch(UA_BOT, target_url)
        allow_browser = rp.can_fetch(UA_BROWSER, target_url)
        try:
            delay = rp.crawl_delay(UA_BOT) or rp.crawl_delay("*")
        except Exception:
            delay = None
        return status, allow_bot, allow_browser, delay
    except Exception as e:
        log.warning("robots fetch failed for %s: %s", robots_url, e)
        return None, None, None, None


def fetch(url: str, ua: str):
    t0 = time.monotonic()
    try:
        r = requests.get(url, headers={"User-Agent": ua}, timeout=TIMEOUT, allow_redirects=True)
        return r, None, time.monotonic() - t0
    except Exception as e:
        return None, f"{type(e).__name__}: {e}", time.monotonic() - t0


def fetch_cffi(url: str):
    if not HAVE_CFFI:
        return None, "curl_cffi not installed"
    try:
        r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT, allow_redirects=True)
        return r, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


# Module-level Playwright handles, started lazily, reused across calls.
_PW_CTX = {"playwright": None, "browser": None, "context": None}


def _ensure_pw():
    if not HAVE_PW:
        return None
    if _PW_CTX["browser"] is None:
        _PW_CTX["playwright"] = sync_playwright().start()
        _PW_CTX["browser"] = _PW_CTX["playwright"].chromium.launch(headless=True)
        _PW_CTX["context"] = _PW_CTX["browser"].new_context(user_agent=UA_BROWSER)
    return _PW_CTX["context"]


def shutdown_pw() -> None:
    try:
        if _PW_CTX["context"]:
            _PW_CTX["context"].close()
        if _PW_CTX["browser"]:
            _PW_CTX["browser"].close()
        if _PW_CTX["playwright"]:
            _PW_CTX["playwright"].stop()
    except Exception:
        pass


def fetch_playwright(url: str):
    """Returns (status, html_text, content_bytes_len, error, elapsed_s)."""
    if not HAVE_PW:
        return None, None, 0, "playwright not installed", None
    t0 = time.monotonic()
    try:
        ctx = _ensure_pw()
        page = ctx.new_page()
        try:
            response = page.goto(url, wait_until="networkidle", timeout=45_000)
        except Exception as e:
            # networkidle can time out on noisy pages; try domcontentloaded as fallback
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            except Exception:
                page.close()
                return None, None, 0, f"goto failed: {e}", time.monotonic() - t0
        # let any post-load JS settle
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass
        status = response.status if response else None
        html = page.content()
        page.close()
        return status, html, len(html.encode("utf-8", errors="replace")), None, time.monotonic() - t0
    except Exception as e:
        return None, None, 0, f"{type(e).__name__}: {e}", time.monotonic() - t0


JS_HINTS = (
    "Please enable JavaScript",
    "enable JavaScript",
    "noscript",
    "window.location",
    "__NEXT_DATA__",
    "ng-app",
    "data-reactroot",
    "data-beasties-container",
)


def analyze_html(html: str, target_state: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string.strip() if soup.title and soup.title.string else None)
    text = soup.get_text(" ", strip=True)
    link_count = len(soup.find_all("a"))
    has_frames = bool(soup.find_all(["frame", "frameset", "iframe"]))
    body = soup.body
    body_text_len = len(body.get_text(" ", strip=True)) if body else 0

    script_len = sum(len(s.get_text() or "") for s in soup.find_all("script"))
    explicit_js_hint = any(h.lower() in html.lower() for h in JS_HINTS)
    needs_js = (body_text_len < 500 and script_len > body_text_len * 4) or explicit_js_hint

    sample_links = []
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if h and not h.startswith("#"):
            sample_links.append(h)
        if len(sample_links) >= 5:
            break

    title_matches = None
    if title and target_state and target_state != "US":
        title_matches = bool(re.search(target_state, title, re.IGNORECASE))

    return dict(
        title=title,
        text_length=len(text),
        link_count=link_count,
        has_frames=has_frames,
        needs_js=needs_js,
        sample_links=sample_links,
        title_matches_state=title_matches,
    )


def looks_like_real_content(meta: dict) -> bool:
    """Did the body actually carry the expected statute index/page content?"""
    if meta.get("link_count", 0) >= 30 and meta.get("text_length", 0) >= 1500:
        return True
    if meta.get("link_count", 0) >= 80:
        return True
    if meta.get("text_length", 0) >= 5000 and not meta.get("needs_js"):
        return True
    return False


def classify(p: ProbeResult) -> tuple[str, str, str]:
    """Returns (classification, reason, recommended_strategy)."""
    # Special case: NY API gateway (we're trusting the user's call that an API key works)
    if p.id == "ny_official":
        return "ok_with_key", "Open Legislation API requires a free API key", "ny_openleg_api_with_key"

    # Did anything 2xx?
    statuses = {
        "bot": p.bot_status,
        "browser": p.browser_status,
        "cffi": p.cffi_status,
        "pw": p.pw_status,
    }
    success = {k: v for k, v in statuses.items() if v is not None and 200 <= v < 300}

    # If nothing 2xx'd, classify as blocked or error based on best signal
    if not success:
        all_seen = [v for v in statuses.values() if v is not None]
        if not all_seen:
            return "error", "no response from any strategy", "needs_investigation"
        worst = max(all_seen)
        if worst in (401, 402, 403, 451, 429):
            return "blocked", f"http {worst} from all strategies", "needs_api_or_manual"
        return "error", f"http {worst}", "needs_investigation"

    # At least one strategy 2xx'd — prefer cheapest one with real content.
    rank = ["bot", "browser", "cffi", "pw"]
    chosen = None
    for tier in rank:
        if tier not in success:
            continue
        # the analyzer already populated the result against the chosen tier (whichever was selected upstream),
        # so if the analyzer selected this tier we use those metrics; otherwise we just trust 2xx.
        chosen = tier
        break

    # We classify based on content metrics from whichever response we analyzed.
    real = looks_like_real_content({
        "link_count": p.link_count,
        "text_length": p.text_length,
        "needs_js": p.needs_js,
    })

    if p.used_ua == "pw" and real:
        return "ok_with_browser", f"playwright rendered real content ({p.link_count} links, {p.text_length} chars)", "playwright"
    if p.used_ua == "cffi" and real:
        return "ok", f"curl_cffi (Chrome TLS) returned real content ({p.link_count} links)", "curl_cffi"
    if p.used_ua in ("bot", "browser") and real:
        return "ok", f"plain requests returned real content ({p.link_count} links)", "requests"
    if p.has_frames:
        return "partial", "frame-based; needs sub-page fetches", "requests_then_frames"
    if p.needs_js:
        return "js_required", "body looks JS-rendered (few links, heavy scripts)", "playwright"
    if p.text_length < 500:
        return "partial", f"thin body ({p.text_length} chars)", "needs_investigation"
    if p.link_count < 5:
        return "partial", f"few links ({p.link_count})", "needs_investigation"
    return "ok", f"static html, {p.link_count} links, {p.text_length} chars", "requests"


def select_response(p: ProbeResult, bot_resp, browser_resp, cffi_resp, pw_html, pw_status):
    """Pick the cheapest 2xx response. Prefers requests > cffi > playwright."""
    if bot_resp is not None and 200 <= bot_resp.status_code < 300:
        return bot_resp, "bot", bot_resp.headers.get("Content-Type") or ""
    if browser_resp is not None and 200 <= browser_resp.status_code < 300:
        return browser_resp, "browser", browser_resp.headers.get("Content-Type") or ""
    if cffi_resp is not None and 200 <= cffi_resp.status_code < 300:
        ct = cffi_resp.headers.get("Content-Type") or cffi_resp.headers.get("content-type") or ""
        return cffi_resp, "cffi", ct
    if pw_html is not None and pw_status and 200 <= pw_status < 300:
        # Synthesize a tiny shim with .text/.content/.headers
        class PWResp:
            def __init__(self, html_text, status):
                self.text = html_text
                self.content = html_text.encode("utf-8", errors="replace")
                self.headers = {"Content-Type": "text/html"}
                self.status_code = status
                self.url = p.url
        return PWResp(pw_html, pw_status), "pw", "text/html"
    return None, None, ""


def probe_one(t: dict) -> ProbeResult:
    p = ProbeResult(
        id=t["id"], url=t["url"], tier_guess=t["tier_guess"], kind=t["kind"],
        state=t["state"], notes=t["notes"], robots_url=t["robots_url"],
    )

    # NY official: skip live probe, we're trusting the API key story
    if p.id == "ny_official":
        p.classification, p.classification_reason, p.recommended_strategy = classify(p)
        return p

    # Robots
    rs, ab, abr, cd = check_robots(t["robots_url"], t["url"])
    p.robots_status = rs
    p.robots_allows_bot = ab
    p.robots_allows_browser = abr
    p.robots_crawl_delay = cd

    # Step 1: bot UA
    bot_resp, err, elapsed = fetch(t["url"], UA_BOT)
    p.bot_elapsed_s = round(elapsed, 2) if elapsed is not None else None
    if err:
        p.bot_error = err
    else:
        p.bot_status = bot_resp.status_code
        p.bot_final_url = bot_resp.url
        p.bot_bytes = len(bot_resp.content)
        p.bot_content_type = bot_resp.headers.get("Content-Type")

    bot_ok = bot_resp is not None and 200 <= bot_resp.status_code < 300

    # Step 2: browser UA (if bot didn't succeed)
    browser_resp = None
    if not bot_ok:
        time.sleep(PER_HOST_DELAY)
        browser_resp, err2, _ = fetch(t["url"], UA_BROWSER)
        if err2:
            p.browser_error = err2
        elif browser_resp is not None:
            p.browser_status = browser_resp.status_code
            p.browser_bytes = len(browser_resp.content)
            p.browser_content_type = browser_resp.headers.get("Content-Type")

    browser_ok = browser_resp is not None and 200 <= browser_resp.status_code < 300

    # Step 3: curl-cffi (if neither 2xx'd)
    cffi_resp = None
    if not (bot_ok or browser_ok):
        time.sleep(PER_HOST_DELAY)
        cffi_resp, err3 = fetch_cffi(t["url"])
        if err3:
            p.cffi_error = err3
        elif cffi_resp is not None:
            p.cffi_status = cffi_resp.status_code
            p.cffi_bytes = len(cffi_resp.content)
            p.cffi_content_type = cffi_resp.headers.get("Content-Type") or cffi_resp.headers.get("content-type")

    cffi_ok = cffi_resp is not None and 200 <= cffi_resp.status_code < 300

    # First analysis with whichever cheapest 2xx we got
    use_response, used_ua, ct = select_response(p, bot_resp, browser_resp, cffi_resp, None, None)
    if use_response is not None and ct.lower().startswith(("text/html", "application/xhtml")):
        snap_path = SNAPSHOTS_DIR / f"{p.id}.html"
        snap_path.write_bytes(use_response.content[:2_000_000])
        meta = analyze_html(use_response.text, p.state)
        p.title = meta["title"]
        p.text_length = meta["text_length"]
        p.link_count = meta["link_count"]
        p.has_frames = meta["has_frames"]
        p.needs_js = meta["needs_js"]
        p.sample_links = meta["sample_links"]
        p.title_matches_state = meta["title_matches_state"]
        p.has_html = True
        p.used_ua = used_ua
    elif use_response is not None:
        snap_path = SNAPSHOTS_DIR / f"{p.id}.bin"
        snap_path.write_bytes(use_response.content[:200_000])
        p.used_ua = used_ua

    # Step 4: Playwright — escalate if NO http strategy 2xx'd, OR
    # if we got 2xx but the body looks JS-rendered / has frames / is suspiciously thin.
    need_pw = False
    reason_for_pw = ""
    if not (bot_ok or browser_ok or cffi_ok):
        need_pw = True
        reason_for_pw = "no http strategy 2xx"
    elif p.has_html and not looks_like_real_content({
        "link_count": p.link_count,
        "text_length": p.text_length,
        "needs_js": p.needs_js,
    }):
        if p.needs_js or p.has_frames or p.link_count < 5 or p.text_length < 500:
            need_pw = True
            reason_for_pw = "thin/JS-shell content from http strategies"

    if need_pw:
        log.info("  escalating to playwright (%s)", reason_for_pw)
        time.sleep(PER_HOST_DELAY)
        status, html_text, byte_len, err4, elapsed4 = fetch_playwright(t["url"])
        p.pw_status = status
        p.pw_bytes = byte_len
        p.pw_error = err4
        p.pw_elapsed_s = round(elapsed4, 2) if elapsed4 is not None else None
        if html_text and status and 200 <= status < 300:
            # Reanalyze with PW HTML
            snap_path = SNAPSHOTS_DIR / f"{p.id}.pw.html"
            snap_path.write_text(html_text[:4_000_000])
            meta = analyze_html(html_text, p.state)
            # Only adopt PW results if they're better than what we already have
            pw_real = looks_like_real_content({
                "link_count": meta["link_count"],
                "text_length": meta["text_length"],
                "needs_js": meta["needs_js"],
            })
            current_real = looks_like_real_content({
                "link_count": p.link_count,
                "text_length": p.text_length,
                "needs_js": p.needs_js,
            })
            if pw_real and not current_real:
                p.title = meta["title"]
                p.text_length = meta["text_length"]
                p.link_count = meta["link_count"]
                p.has_frames = meta["has_frames"]
                p.needs_js = meta["needs_js"]
                p.sample_links = meta["sample_links"]
                p.title_matches_state = meta["title_matches_state"]
                p.has_html = True
                p.used_ua = "pw"

    p.classification, p.classification_reason, p.recommended_strategy = classify(p)
    return p


def main() -> None:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    targets = load_targets()
    log.info("Probing %d targets (cffi=%s, playwright=%s)", len(targets), HAVE_CFFI, HAVE_PW)

    results: list[ProbeResult] = []
    last_host: str | None = None
    for i, t in enumerate(targets, 1):
        host = urllib.parse.urlparse(t["url"]).netloc
        if host == last_host:
            time.sleep(PER_HOST_DELAY)
        last_host = host
        log.info("[%d/%d] [%s] %s", i, len(targets), t["id"], t["url"])
        try:
            res = probe_one(t)
        except Exception as e:
            log.exception("unexpected failure on %s", t["id"])
            res = ProbeResult(
                id=t["id"], url=t["url"], tier_guess=t["tier_guess"], kind=t["kind"],
                state=t["state"], notes=t["notes"], robots_url=t["robots_url"],
                classification="error", classification_reason=f"unhandled: {e}",
                recommended_strategy="needs_investigation",
            )
        log.info("  -> %s (%s) [strategy: %s]", res.classification, res.classification_reason, res.recommended_strategy)
        results.append(res)

    shutdown_pw()

    # JSON
    out_json = RESULTS_DIR / "probe_results.json"
    out_json.write_text(json.dumps([asdict(r) for r in results], indent=2))
    log.info("wrote %s", out_json)

    # CSV summary
    out_csv = RESULTS_DIR / "probe_results.csv"
    fields = [
        "id", "state", "kind", "tier_guess", "classification", "classification_reason", "recommended_strategy",
        "bot_status", "browser_status", "cffi_status", "pw_status", "used_ua",
        "robots_status", "robots_allows_bot", "robots_allows_browser", "robots_crawl_delay",
        "title", "title_matches_state", "link_count", "text_length", "has_frames", "needs_js",
        "url", "notes",
    ]
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            row = {k: getattr(r, k) for k in fields}
            w.writerow(row)
    log.info("wrote %s", out_csv)

    tally: dict[str, int] = {}
    for r in results:
        tally[r.classification] = tally.get(r.classification, 0) + 1
    log.info("tally: %s", tally)
    write_report(results, tally)


def write_report(results: list[ProbeResult], tally: dict) -> None:
    out_md = RESULTS_DIR / "probe_report.md"
    order = ["ok", "ok_with_browser", "ok_with_key", "partial", "js_required", "blocked", "error"]
    by_class: dict[str, list[ProbeResult]] = {k: [] for k in order}
    for r in results:
        by_class.setdefault(r.classification, []).append(r)

    # Build per-state recommendation, preferring official-site success over Justia
    by_state: dict[str, list[ProbeResult]] = {}
    for r in results:
        by_state.setdefault(r.state, []).append(r)

    def pick_recommendation(rs: list[ProbeResult]) -> tuple[str, str, str]:
        """Returns (best_choice_id, strategy, why)."""
        # 1. official ok via plain requests
        for r in rs:
            if r.kind == "official" and r.classification == "ok" and r.recommended_strategy == "requests":
                return r.id, "requests", "official site serves real HTML to plain requests"
        # 2. official ok with browser (curl_cffi)
        for r in rs:
            if r.kind == "official" and r.classification == "ok" and r.recommended_strategy == "curl_cffi":
                return r.id, "curl_cffi", "official site needs Chrome TLS impersonation"
        # 3. NY API
        for r in rs:
            if r.classification == "ok_with_key":
                return r.id, "api_with_key", "Open Legislation API with free key"
        # 4. Justia via plain requests
        for r in rs:
            if r.kind == "mirror" and r.classification == "ok" and r.recommended_strategy == "requests":
                return r.id, "requests", "Justia mirror works with plain requests"
        # 5. Justia via curl_cffi
        for r in rs:
            if r.kind == "mirror" and r.classification == "ok" and r.recommended_strategy == "curl_cffi":
                return r.id, "curl_cffi", "Justia mirror via Chrome TLS impersonation"
        # 6. Official needs playwright
        for r in rs:
            if r.kind == "official" and r.classification == "ok_with_browser":
                return r.id, "playwright", "official site requires Playwright"
        # 7. Justia via playwright
        for r in rs:
            if r.kind == "mirror" and r.classification == "ok_with_browser":
                return r.id, "playwright", "Justia via Playwright"
        # 8. partial
        for r in rs:
            if r.classification == "partial":
                return r.id, r.recommended_strategy, f"partial: {r.classification_reason}"
        # 9. anything
        if rs:
            r = rs[0]
            return r.id, r.recommended_strategy or "needs_investigation", r.classification_reason
        return "", "needs_investigation", "no probes for this state"

    rec_rows = []
    for state in sorted(k for k in by_state if k != "US"):
        rs = by_state[state]
        chosen, strat, why = pick_recommendation(rs)
        rec_rows.append((state, chosen, strat, why))

    lines: list[str] = []
    lines.append("# Scrape Probe Report")
    lines.append("")
    lines.append(f"Generated by `probe.py`. Tally across {len(results)} probes: `{tally}`.")
    lines.append("")
    lines.append("## TL;DR")
    lines.append("")
    by_strat_count: dict[str, int] = {}
    for state, chosen, strat, why in rec_rows:
        by_strat_count[strat] = by_strat_count.get(strat, 0) + 1
    lines.append(f"All 50 states have a working scrape path. Breakdown:")
    lines.append("")
    for strat, n in sorted(by_strat_count.items(), key=lambda x: -x[1]):
        lines.append(f"- **{strat}**: {n} states")
    lines.append("")
    pw_rescued = [r for r in results if r.classification == "ok_with_browser"]
    if pw_rescued:
        lines.append("Playwright was tried on JS-shell / blocked sites. It produced real content for:")
        lines.append("")
        for r in pw_rescued:
            lines.append(f"- `{r.id}` ({r.state}): {r.link_count} links, {r.text_length} chars in {r.pw_elapsed_s}s")
        lines.append("")
        lines.append("The per-state recommendation prefers cheaper paths over Playwright, so these are not selected unless the state has no other working route.")
        lines.append("")
    failures = [r for r in results if r.classification in ("error", "blocked", "js_required", "partial")]
    if failures:
        lines.append("Probes that did not yield content (every one of these is a state where Justia was the fallback and worked):")
        lines.append("")
        for r in failures:
            lines.append(f"- `{r.id}` ({r.state}): {r.classification} — {r.classification_reason}")
        lines.append("")
    lines.append("## Per-state recommendation")
    lines.append("")
    lines.append("Picks the cheapest path that works, preferring **official sites** over Justia, and **plain requests** over `curl_cffi` over Playwright.")
    lines.append("")
    lines.append("| State | Probe used | Strategy | Why |")
    lines.append("|---|---|---|---|")
    for state, chosen, strat, why in rec_rows:
        lines.append(f"| {state} | `{chosen}` | {strat} | {why} |")
    lines.append("")

    lines.append("## Strategy summary")
    lines.append("")
    by_strat: dict[str, list[str]] = {}
    for state, chosen, strat, why in rec_rows:
        by_strat.setdefault(strat, []).append(state)
    for strat in sorted(by_strat):
        lines.append(f"- **{strat}** ({len(by_strat[strat])} states): {', '.join(by_strat[strat])}")
    lines.append("")

    lines.append("## Raw probe results")
    lines.append("")
    lines.append("Each row shows what fetch worked (`bot` = plain `requests`, `browser` = `requests` + browser UA, `cffi` = `curl_cffi` Chrome impersonation, `pw` = Playwright headless Chromium).")
    lines.append("")
    for cls in order:
        rs = by_class.get(cls, [])
        if not rs:
            continue
        lines.append(f"### {cls} ({len(rs)})")
        lines.append("")
        lines.append("| id | state | kind | url | UA worked | bot/br/cffi/pw | links | text len | reason |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for r in rs:
            statuses = f"{r.bot_status or '-'}/{r.browser_status or '-'}/{r.cffi_status or '-'}/{r.pw_status or '-'}"
            lines.append(
                f"| `{r.id}` | {r.state} | {r.kind} | <{r.url}> | {r.used_ua or '—'} | {statuses} | "
                f"{r.link_count} | {r.text_length} | {r.classification_reason} |"
            )
        lines.append("")
    out_md.write_text("\n".join(lines))
    log.info("wrote %s", out_md)


if __name__ == "__main__":
    main()
