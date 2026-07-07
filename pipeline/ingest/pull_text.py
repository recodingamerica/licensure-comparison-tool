"""Pull full statute text for a profession across all states.

Reads scrape_probe/results/profession_chapters.csv, filters by --profession
(case-insensitive substring on chapter_label, e.g. "podiatr"), and for each
matched URL:

  - if it's a section URL, fetches and extracts text directly
  - if it's a chapter URL, fetches it as an index, drills into section URLs,
    then extracts each section's text

Output: extract/results/text/<profession>/<STATE>.json with a list of sections,
each carrying {url, label, citation, text}. Per-state files merge multiple
chapter rows into one.

Usage:
  python pull_text.py --profession podiatry [--label-match podiatr]
                      [--states AL,AK,...] [--limit-sections 50]
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import time
import urllib.parse
from dataclasses import asdict, dataclass, field

from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests  # type: ignore

import sys
from pipeline.paths import TEXT_DIR, LOGS_DIR, PROFESSION_INDEX_DIR
from pipeline._records import record_files
from pipeline._runlog import record_run
from pipeline.config.loaders import load_limits, load_state_structure

LOG_PATH = LOGS_DIR / "pull_text.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

TIMEOUT = 25
# Per-section pause. Overridable via PULL_HOST_DELAY (seconds) — set it high for
# a polite Justia/CDP crawl through the real browser (e.g. 7) so we're not
# flipping pages every second. Each pause adds up to 60% random jitter so the
# cadence is human-irregular rather than a steady machine-gun rhythm.
import random as _random  # local alias; std random is allowed in pipeline code
_DELAY_DEFAULT = str(load_limits()["fetch"]["per_host_delay_seconds"])
try:
    PER_HOST_DELAY = float(os.environ.get("PULL_HOST_DELAY", _DELAY_DEFAULT))
except ValueError:
    PER_HOST_DELAY = float(_DELAY_DEFAULT)


def polite_sleep() -> None:
    """Sleep PER_HOST_DELAY plus up to 60% jitter (human-irregular pacing)."""
    time.sleep(PER_HOST_DELAY * (1.0 + _random.random() * 0.6))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("pull_text")

# Maximum recursion depth when walking a chapter down to leaf sections.
# Read from config/limits.yaml so all data-shaping numbers are visible in one place.
SECTION_WALK_MAX_DEPTH: int = load_limits()["pull"]["section_walk_max_depth"]

# A path's last segment looks like a Justia section
SECTION_SEG = re.compile(
    r"^(section[-_]|§|s[-_]\d|statute[-_]|rs[-_]|\d+[a-z]?[-_:.]\d|\d{3,}\b)",
    re.IGNORECASE,
)


@dataclass
class Section:
    url: str
    label: str
    citation: str  # short cite extracted from label, e.g. "20-50"
    text: str
    text_len: int = 0
    error: str | None = None


@dataclass
class StateCorpus:
    state: str
    profession: str
    chapter_urls: list[str] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    total_chars: int = 0
    errors: list[str] = field(default_factory=list)
    section_cap_hit: int | None = None  # set to the cap value when --limit-sections fires


# --- Cloudflare handling (Justia, which CF-blocks our IPs) ---
# Justia sits behind a Cloudflare JS challenge that curl_cffi can't solve from
# datacenter IPs. The ONLY thing that reliably clears it is a hand-started
# debug Chrome attached over CDP (JUSTIA_CDP_URL) — see _get_browser_page().
# A residential proxy and ScraperAPI were both tried as no-human-required
# fallbacks and NEITHER actually clears Justia's challenge (2026-07-08); that
# code was removed rather than left as a backup that silently doesn't work.
# Only hosts in _UNBLOCK_HOSTS get browser treatment — official state sources
# (le.utah.gov, sdlegislature.gov, …) fetch direct, free, as before.
_UNBLOCK_HOSTS = ("law.justia.com",)


def _env_get(name: str) -> str | None:
    v = os.environ.get(name)
    if not v:
        try:
            from pipeline._env import load_env
            load_env()
            v = os.environ.get(name)
        except Exception:
            pass
    return v


# --- Headful-browser fetch for Cloudflare (Justia) via a CDP-attached Chrome ---
# Cloudflare's "Just a moment" challenge is beaten only by a REAL, hand-driven
# browser session. We keep ONE headful Chromium open (CDP-attached): the first
# Justia page solves the challenge, and the cf_clearance cookie carries the rest
# (fast). Heavy resources (images/media/fonts/css) are blocked to conserve proxy
# bandwidth. Lazily started, reused across the whole run, closed at exit.
_BROWSER: dict | None = None

# Exclusive lock on the shared CDP Chrome. Two pull_text processes hitting the
# SAME debug Chrome concurrently garble each other's pages (the page object is
# shared global state) — corpora come back as 1-section "partials" that silently
# overwrite good data. This bit us when an orphaned grind child kept pulling
# after the parent was killed. Acquire an exclusive flock before first using the
# browser so a second Justia pull WAITS instead of colliding. Other hosts
# (MD/SD/NY APIs, curl_cffi) don't use the browser and never contend for it.
_CDP_LOCK_FH = None
_CDP_LOCK_PATH = "/tmp/justia_cdp_pull.lock"


def _acquire_cdp_lock() -> None:
    global _CDP_LOCK_FH
    if _CDP_LOCK_FH is not None:
        return
    import fcntl
    fh = open(_CDP_LOCK_PATH, "w")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        log.warning("  ⏸ another Justia pull holds the CDP lock (%s) — waiting for "
                    "it to finish (one pull per Chrome)…", _CDP_LOCK_PATH)
        waited = 0
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                time.sleep(5)
                waited += 5
                if waited % 60 == 0:
                    log.warning("  …still waiting for CDP lock (%ds)", waited)
                if waited >= 3600:
                    fh.close()
                    raise SystemExit("CDP lock held >1h — aborting to avoid a "
                                     "concurrent-pull collision; check for a stray "
                                     "pull_text process.")
        log.info("  ▶ acquired CDP lock, proceeding")
    _CDP_LOCK_FH = fh


def _get_browser_page():
    global _BROWSER
    if _BROWSER is None:
        import atexit
        # CDP attach (preferred): connect to a REAL Chrome the user started with
        # --remote-debugging-port. Cloudflare can't see an in-page automation
        # fingerprint (the automation is out-of-process), so the challenge clears
        # where a launched/automated Chromium — even headful on a clean home IP —
        # is blocked. The user solves the first challenge by hand; cf_clearance
        # then persists in the debug profile. See docs/.../trades_official_sources.
        cdp = _env_get("JUSTIA_CDP_URL")
        if cdp:
            _acquire_cdp_lock()  # serialize: one pull per shared debug Chrome
            from playwright.sync_api import sync_playwright
            pw = sync_playwright().start()
            browser = pw.chromium.connect_over_cdp(cdp)
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            # Always open OUR OWN dedicated tab — never reuse ctx.pages[0]. That tab
            # is often a chrome:// page (newtab, or whats-new after an auto-update),
            # and page.goto() from a chrome:// URL to an https Justia URL hangs the
            # whole pull (no error, no timeout escape — the classic "wedge"). It also
            # hijacked/closed the user's visible tab. A fresh new_page() starts at
            # about:blank (navigates cleanly) and shares the context's cf_clearance
            # cookie, so nothing is lost. We close it on exit.
            page = ctx.new_page()
            # Self-heal leaked tabs: a prior pull killed by `timeout`/SIGTERM never
            # runs its atexit cleanup, so its Justia tab lingers. Close any OTHER
            # Justia tabs now (the debug profile isn't used for browsing, and the
            # flock guarantees no concurrent pull owns one). Keeps Chrome from
            # accumulating dozens of tabs across a long harvest.
            for _p in list(ctx.pages):
                if _p is not page and "justia.com" in (_p.url or ""):
                    try:
                        _p.close()
                    except Exception:
                        pass
            _BROWSER = {"pw": pw, "browser": browser, "ctx": ctx, "page": page, "cdp": True, "own_page": True}
            atexit.register(_close_browser)
            # Also close our own tab on SIGTERM (timeout-kill) — atexit doesn't run then.
            try:
                import signal
                signal.signal(signal.SIGTERM, lambda *_a: (_close_browser(), os._exit(143)))
            except Exception:
                pass
            return page
        # No CDP URL set. A launched/automated Chromium (with or without a
        # residential proxy) does NOT clear Justia's Cloudflare challenge — both
        # were tried and neither works (2026-07-08) — so there is no fallback
        # left to attempt. Fail clearly instead of silently launching a browser
        # that will just sit on the challenge page forever.
        raise RuntimeError(
            "JUSTIA_CDP_URL is not set. Justia's Cloudflare challenge can only be "
            "cleared by attaching to a hand-started debug Chrome over CDP — start "
            "one and set JUSTIA_CDP_URL (see docs/runbooks/cdp_repull_lessons_2026-07-02.md)."
        )
    return _BROWSER["page"]


def _close_browser() -> None:
    global _BROWSER
    if _BROWSER:
        try:
            # Over CDP: don't close the user's real Chrome — but DO close the
            # dedicated tab we opened, so tabs don't pile up across pulls.
            # Never close the user's real Chrome — just our own dedicated tab.
            try:
                _BROWSER["page"].close()
            except Exception:
                pass
            _BROWSER["pw"].stop()
        except Exception:
            pass
        _BROWSER = None


def _challenge_showing(page) -> bool:
    t = (page.title() or "").lower()
    return "just a moment" in t or "attention required" in t


def fetch_via_browser(url: str) -> tuple[int | None, str | None, str | None]:
    """Fetch a Cloudflare-protected URL through the persistent browser (CDP-
    attached real Chrome, or residential-proxy headful Chromium). Waits for the
    challenge to clear before returning HTML.

    On a long crawl the cf_clearance cookie expires (~30 min) and the challenge
    reappears mid-run. Rather than failing the section after 60s (which would
    drop data), we PAUSE up to CHALLENGE_WAIT and log once, so the user can
    re-solve it in the Chrome window and the crawl resumes where it left off.
    """
    CHALLENGE_WAIT = 360  # seconds to wait for a (re)solve before giving up
    try:
        page = _get_browser_page()
        page.goto(url, timeout=90000, wait_until="domcontentloaded")
        warned = False
        waited = 0.0
        while _challenge_showing(page) and waited < CHALLENGE_WAIT:
            if not warned:
                log.warning("  ⏸ Cloudflare challenge on %s — SOLVE IT in the Chrome "
                            "window; waiting up to %ds…", url, CHALLENGE_WAIT)
                warned = True
            page.wait_for_timeout(2000)
            waited += 2
        html = page.content()
        if _challenge_showing(page):
            return 403, html, "cloudflare challenge did not clear (timed out)"
        if warned:
            log.info("  ▶ challenge cleared, resuming")
        return 200, html, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def _use_browser(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    if not any(h in host for h in _UNBLOCK_HOSTS):
        return False
    return bool(_env_get("JUSTIA_CDP_URL"))


def fetch(url: str) -> tuple[int | None, str | None, str | None]:
    if _use_browser(url):
        return fetch_via_browser(url)
    try:
        r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT,
                              allow_redirects=True)
        return r.status_code, r.text, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def fetch_bytes(url: str) -> tuple[int | None, bytes | None, str | None]:
    """Like fetch() but returns raw bytes, so the caller controls decoding.
    Needed for Word-export state sites (NV/OR/…) served as latin1/cp1252, which
    curl_cffi's text auto-decode mangles into replacement chars. Retries with
    verify=False on a cert error (some state sites ship an incomplete cert chain,
    e.g. cga.ct.gov)."""
    try:
        r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT,
                              allow_redirects=True)
        return r.status_code, r.content, None
    except Exception as e:
        if "certificate" in str(e).lower() or "ssl" in str(e).lower():
            try:
                r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT,
                                      allow_redirects=True, verify=False)
                return r.status_code, r.content, None
            except Exception as e2:
                return None, None, f"{type(e2).__name__}: {e2}"
        return None, None, f"{type(e).__name__}: {e}"


# A bare path segment that is a 4-digit year (Justia year-versioned snapshots).
YEAR_SEG = re.compile(r"^(?:19|20)\d\d$")


def is_section_url(url: str) -> bool:
    last = [s for s in urllib.parse.urlparse(url).path.split("/") if s][-1]
    return bool(SECTION_SEG.match(last))


def extract_child_links(html: str, base_url: str) -> tuple[list[dict], list[dict]]:
    """Find child links under a chapter page.

    Returns (sections, intermediates). Sections are leaf statute URLs;
    intermediates (subchapter, subpart, ...) need another drill level.

    Year-versioned Justia copies are de-duplicated (issues #6/#7): some chapter
    pages link to several prior-year snapshots of the same content
    (/codes/<state>/2023/..., /2024/...). Following all of them pulls the same
    text once per year. We collapse links that are identical apart from a year
    segment, keeping the unversioned copy if present, else the latest year — so
    states that only publish year-stamped pages (KY, OR, IL, ...) still get
    their current text, while true duplicates are dropped.
    """
    soup = BeautifulSoup(html, "html.parser")
    parsed = urllib.parse.urlparse(base_url)
    base_segments = [s for s in parsed.path.split("/") if s]
    title_slug = base_segments[-1].lower() if base_segments else None
    base_canon = tuple(s for s in base_segments if not YEAR_SEG.match(s))

    sections: list[dict] = []
    intermediates: list[dict] = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        u = urllib.parse.urlparse(absolute)
        if u.netloc != parsed.netloc:
            continue
        path_segments = [s for s in u.path.split("/") if s]
        if not path_segments:
            continue
        # Skip year-versioned snapshots of THIS page (issues #6/#7): a link whose
        # path, with year segments stripped, equals the current page's is just a
        # prior/parallel-year copy of the page we're already on (e.g. the page at
        # /<state>/title-43/chapter-43-44/ linking to /<state>/2024/title-43/
        # chapter-43-44/). Following it re-pulls the same chapter under a year.
        # Year-stamped *children* (deeper sections) are NOT dropped here — some
        # states only publish year-stamped section pages; those are de-duplicated
        # by canonical path after the full walk (_dedupe_year_versions).
        link_years = {s for s in path_segments if YEAR_SEG.match(s)}
        canon_path = tuple(s for s in path_segments if not YEAR_SEG.match(s))
        if link_years and canon_path == base_canon:
            continue
        last = path_segments[-1]
        if title_slug and title_slug not in [s.lower() for s in path_segments]:
            continue
        label = (a.get_text(strip=True) or "")[:300]
        if not label:
            continue
        if u.path in seen:
            continue
        seen.add(u.path)
        item = {"url": absolute, "label": label, "slug": last}
        if SECTION_SEG.match(last):
            sections.append(item)
        elif INTERMEDIATE_SEG.match(last):
            intermediates.append(item)
        elif len(canon_path) > len(base_canon) and canon_path[:len(base_canon)] == base_canon:
            # Plain-word sub-group page under this chapter (not a keyworded
            # subchapter/article). Justia uses these for chapters split by a
            # heading rather than a numbered subchapter — e.g. MS title-73/
            # chapter-13/{engineers,land-surveyors}/. It strictly extends the
            # chapter path and isn't a leaf section, so drill it.
            intermediates.append(item)
    return _dedupe_year_versions(sections), _dedupe_year_versions(intermediates)


def _dedupe_year_versions(items: list[dict]) -> list[dict]:
    """Collapse links that differ only by a Justia year segment (#6/#7).

    Group by the path with year segments stripped; within each group keep the
    unversioned URL if one exists, otherwise the highest year. Original order is
    preserved. Links with no year segment are unaffected.
    """
    best: dict[tuple, tuple] = {}  # canon path -> (rank, url)
    for it in items:
        segs = [s for s in urllib.parse.urlparse(it["url"]).path.split("/") if s]
        years = [int(s) for s in segs if YEAR_SEG.match(s)]
        canon = tuple(s for s in segs if not YEAR_SEG.match(s))
        rank = (1, 0) if not years else (0, max(years))  # unversioned beats any year
        if canon not in best or rank > best[canon][0]:
            best[canon] = (rank, it["url"])
    keep = {url for _, url in best.values()}
    return [it for it in items if it["url"] in keep]


# --- Pennsylvania legacy static endpoint (legis.state.pa.us /WU01/.../HTM) ---
# PA isn't on Justia; it publishes each act's FULL text on one HTML page, with
# sections delimited by hidden `div.Comment` markers of the form
# "{year}{act:04d}u{sec}s" (e.g. "19800057u4.1s"). Unlike Justia (one URL per
# section), one PA URL yields the whole act, so we split it here into per-section
# records rather than fetching a URL per section. See docs/reports/pa_puller_plan.
PA_LEGIS_HOST = "legis.state.pa.us"
# marker = 4-digit year + 4-digit act + 'u' + suffix; section markers end in 's'
# with a numeric section id ("1", "2.1", "4.3"); 'a'/'ax'/'c'/'h'/<sec>'v' are
# act bounds, table-of-contents, enactment header, and per-section amendment notes.
_PA_MARKER = re.compile(r"^(\d{4})(\d{4})u(.+)$")
_PA_SECTION_SUFFIX = re.compile(r"^(\d+(?:\.\d+)?)s$")


def is_pa_legis_url(url: str) -> bool:
    return PA_LEGIS_HOST in urllib.parse.urlparse(url).netloc


def parse_pa_act(html: str, url: str) -> list[Section]:
    """Split one legis.state.pa.us act page into per-section records.

    Walks the BodyContainer's direct children in document order. A `div.Comment`
    whose marker is a section start ("...u<sec>s") opens a new section; every
    following <p>/<table> accumulates into it until the next section start (so a
    section's amendment-note marker "...<sec>v" stays inside that section).
    Content before the first section marker (act header, table of contents,
    enactment clause) is skipped. Returns [] if no markers are found.
    """
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("div", class_="BodyContainer") or soup
    sections: list[Section] = []
    cur_num: str | None = None
    cur_parts: list[str] = []

    def flush() -> None:
        nonlocal cur_num, cur_parts
        if cur_num is not None:
            text = "\n".join(p for p in cur_parts if p).strip().replace("\xa0", " ")
            if text:
                heading = text.split("\n", 1)[0][:300]
                sections.append(Section(
                    url=url, label=heading, citation=f"§ {cur_num}",
                    text=text, text_len=len(text),
                ))
        cur_num, cur_parts = None, []

    for child in body.children:
        name = getattr(child, "name", None)
        if name is None:
            continue
        if name == "div" and "Comment" in (child.get("class") or []):
            m = _PA_MARKER.match(child.get_text(strip=True))
            if not m:
                continue
            sm = _PA_SECTION_SUFFIX.match(m.group(3))
            if sm:
                flush()
                cur_num, cur_parts = sm.group(1), []
            elif m.group(3) == "ax":
                flush()
        elif cur_num is not None and name in ("p", "table"):
            cur_parts.append(child.get_text(" ", strip=True))
    flush()
    return sections


# --- Utah official source (le.utah.gov publishes structured XML per chapter) ---
# Justia is Cloudflare-blocked, but Utah's own site serves a clean, machine-
# readable XML for each chapter: one file holds every <section> with its
# <catchline> (title), statutory text, and <effdate>/<enddate> version dates.
# So one fetch per chapter replaces section-by-section HTML scraping — and the
# version dates let us keep CURRENTLY-EFFECTIVE law (Utah ships future-enacted
# re-enactments in the same file, e.g. the 2026/2027 Title 58 Ch. 55 renumber).
UTAH_LE_HOST = "le.utah.gov"


def is_utah_le_url(url: str) -> bool:
    return UTAH_LE_HOST in urllib.parse.urlparse(url).netloc


def _utah_xml_url_from_chapter(chapter_html: str, chapter_url: str) -> str | None:
    """The chapter page references its content fragment `C<chap>_<id>.html`; the
    same id with a .xml extension is the structured chapter file."""
    m = re.search(r'(C[\w.-]+?_\d+)\.html', chapter_html)
    if not m:
        return None
    base = chapter_url.rsplit("/", 1)[0]
    return f"{base}/{m.group(1)}.xml"


def _utah_parse_date(s: str | None):
    """Parse Utah's M/D/YYYY effective/end dates; None if absent/unparseable."""
    if not s:
        return None
    try:
        from datetime import datetime
        return datetime.strptime(s.strip(), "%m/%d/%Y").date()
    except ValueError:
        return None


def parse_utah_chapter_xml(xml_bytes: bytes, chapter_url: str) -> list[Section]:
    """Parse a le.utah.gov chapter XML into per-section records, keeping only the
    version of each section that is in effect today (Utah co-ships future
    re-enactments tagged with a future <effdate>). Returns [] if unparseable."""
    from datetime import date
    from lxml import etree

    try:
        root = etree.fromstring(xml_bytes)
    except etree.XMLSyntaxError:
        return []

    today = date.today()
    chap_dir = chapter_url.rsplit("/", 1)[0]
    # Collect candidate versions per section number, then pick the effective one.
    by_num: dict[str, list[tuple]] = {}
    for sec in root.findall(".//section"):
        number = sec.get("number")
        if not number:
            continue
        catchline = (sec.findtext("catchline") or "").strip()
        eff = _utah_parse_date(sec.findtext("effdate"))
        end = _utah_parse_date(sec.findtext("enddate"))
        # Strip metadata children, then flatten remaining statutory text.
        for tag in ("histories", "catchline", "effdate", "enddate"):
            for e in sec.findall(tag):
                sec.remove(e)
        text = " ".join("".join(sec.itertext()).split())
        if not text:
            continue
        is_current = (eff is None or eff <= today) and (end is None or end > today)
        # Sort key: current first; among current, latest effdate; among future,
        # earliest effdate (soonest to take effect) as a fallback.
        rank = (1 if is_current else 0, eff or date.min)
        by_num.setdefault(number, []).append((rank, is_current, number, catchline, text))

    sections: list[Section] = []
    for number, cands in by_num.items():
        cands.sort(key=lambda c: c[0], reverse=True)
        _, _, num, catchline, text = cands[0]
        sec_part = num.rsplit("-", 1)[-1]
        url = f"{chap_dir}/{num.rsplit('-', 1)[0]}-S{sec_part}.html"
        label = f"Section {sec_part} - {catchline}" if catchline else f"Section {sec_part}"
        sections.append(Section(
            url=url, label=label, citation=num, text=text, text_len=len(text),
        ))
    # Document order by section number (numeric where possible).
    def _key(s: Section):
        tail = s.citation.rsplit("-", 1)[-1]
        return (int(tail) if tail.isdigit() else 1_000_000, s.citation)
    sections.sort(key=_key)
    return sections


# --- South Dakota official source (sdlegislature.gov JSON API) ---
# SD's site is a JS SPA, but it's backed by a clean public JSON API:
#   /api/Statutes/Statute/<cite>  → one node (Title / Chapter / Section), with
#   CatchLine, Html (the body), Type, Repealed, and a `Next` cite pointer.
# A chapter node points (via Next) at its first section; we walk Next forward,
# staying within the chapter prefix, to enumerate every section in one pass.
SD_API_HOST = "sdlegislature.gov"
_SD_STATUTE_PATH = "/api/Statutes/Statute/"


def is_sd_api_url(url: str) -> bool:
    return SD_API_HOST in urllib.parse.urlparse(url).netloc and _SD_STATUTE_PATH in url


def _sd_html_to_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["style", "head", "script"]):
        t.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def _sd_get(cite: str) -> dict | None:
    status, text, err = fetch(f"https://{SD_API_HOST}{_SD_STATUTE_PATH}{cite}")
    if err or not text or (status and not 200 <= status < 300):
        return None
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        return None
    if isinstance(d, list):
        return d[0] if d else None
    return d if isinstance(d, dict) else None


def pull_sd_chapter(chapter_url: str) -> tuple[list[Section], list[str]]:
    """Walk the SD JSON API from a chapter cite through its sections.
    Returns (sections, errors)."""
    cite = chapter_url.rstrip("/").rsplit("/", 1)[-1]  # .../Statute/36-4 -> 36-4
    errors: list[str] = []
    chap = _sd_get(cite)
    if not chap:
        return [], [f"sd_api fetch chapter {cite}: failed"]
    prefix = cite + "-"
    sections: list[Section] = []
    seen: set[str] = set()
    cur = chap.get("Next")
    while cur and cur.startswith(prefix) and cur not in seen:
        seen.add(cur)
        polite_sleep()
        d = _sd_get(cur)
        if not d:
            errors.append(f"sd_api fetch {cur}: failed")
            break
        if d.get("Type") == "Section":
            text = _sd_html_to_text(d.get("Html") or "")
            label = (d.get("CatchLine") or "").strip()
            # clean_text drops repealed/reserved; keep them but flag in label.
            sections.append(Section(
                url=f"https://{SD_API_HOST}/Statutes/{d.get('Statute')}",
                label=label or f"Section {d.get('Statute')}",
                citation=str(d.get("Statute") or cur),
                text=text, text_len=len(text),
            ))
        cur = d.get("Next")
    return sections, errors


# --- Nevada official source (leg.state.nv.us, whole-chapter HTML) ---
# NV serves one HTML page per NRS chapter (every section inline). The page's
# Word-export markup carries a TOC (p.COLeadline) plus the body (p.SectBody);
# 201-ish SectBody paragraphs, of which the section OPENERS start with
# "NRS <chap>.<sec> <catchline>." and the rest are continuation paragraphs.
# Split on the openers. (Exemplar for the whole-chapter-HTML cluster: OR/NC/WI/
# CT/DE share the one-fetch-per-chapter granularity but each needs its own
# opener rule.)
NV_HOST = "leg.state.nv.us"
_NV_OPENER = re.compile(r"^NRS\s+(\d+[A-Za-z]?\.[0-9A-Za-z]+)\s+(.*)$")


def is_nv_url(url: str) -> bool:
    return NV_HOST in urllib.parse.urlparse(url).netloc and "/nrs/" in url.lower()


def parse_nv_chapter_html(html: str, chapter_url: str) -> list[Section]:
    soup = BeautifulSoup(html, "html.parser")
    sections: list[Section] = []
    cur: dict | None = None

    def flush() -> None:
        nonlocal cur
        if cur:
            text = " ".join(" ".join(cur["body"]).split())
            label = cur["title"].split(". ")[0][:200] or f"NRS {cur['num']}"
            sections.append(Section(
                url=f"https://{NV_HOST}/nrs/NRS-{cur['num'].split('.')[0]}.html#NRS{cur['num'].replace('.', 'Sec')}",
                label=label, citation=f"NRS {cur['num']}",
                text=text, text_len=len(text),
            ))
        cur = None

    for p in soup.find_all("p", class_="SectBody"):
        t = " ".join(p.get_text(" ", strip=True).split())
        if not t:
            continue
        m = _NV_OPENER.match(t)
        if m:
            flush()
            cur = {"num": m.group(1), "title": m.group(2).rstrip("."), "body": [t]}
        elif cur is not None:
            cur["body"].append(t)
    flush()
    return sections


# --- New York official source (OpenLegislation API; lawId-based) ---
# NY isn't title/chapter — it's lawId codes (EDN, EXC, PBH) + articles. The
# Justia hierarchy still maps profession→article (e.g. .../new-york/edn/title-8/
# article-131/), so we keep the Justia url in the index and intercept it here:
# parse lawId+article out of the path and pull the article's sections from the
# free OpenLegislation API (one call, sections + text inline). Needs a free key
# in env as NY_OPENLEG_KEY (sign up at legislation.nysenate.gov). Client ported
# from the newyork repo's backend/scripts/ny_statutes.py.
NY_API = "https://legislation.nysenate.gov/api/3"
_NY_JUSTIA_RE = re.compile(r"/codes/new-york/([a-z]+)/.*?article-(\d+)", re.I)


def is_ny_justia_url(url: str) -> bool:
    return "law.justia.com" in urllib.parse.urlparse(url).netloc and "/new-york/" in url.lower()


def _ny_openleg_key() -> str | None:
    k = os.environ.get("NY_OPENLEG_KEY")
    if not k:
        try:
            from pipeline._env import load_env
            load_env()
            k = os.environ.get("NY_OPENLEG_KEY")
        except Exception:
            pass
    return k


def _ny_walk_sections(node: dict, out: list[dict]) -> None:
    if not node:
        return
    if node.get("docType") == "SECTION":
        out.append(node)
    for c in (node.get("documents") or {}).get("items", []) or []:
        _ny_walk_sections(c, out)


def pull_ny_article(url: str, key: str) -> tuple[list[Section], list[str]]:
    """Pull one NY law article's sections from OpenLegislation, mapping from the
    Justia article url (.../new-york/<law>/.../article-<n>/)."""
    m = _NY_JUSTIA_RE.search(url)
    if not m:
        return [], [f"ny: cannot parse lawId/article from {url}"]
    law, article = m.group(1).upper(), m.group(2)
    q = urllib.parse.urlencode({
        "key": key, "fromLocation": f"A{article}",
        "detail": "true", "full": "true", "depth": "2",
    })
    status, body, err = fetch(f"{NY_API}/laws/{law}?{q}")
    if err or not body or (status and not 200 <= status < 300):
        return [], [f"ny_openleg {law} A{article}: {err or f'http {status}'}"]
    try:
        docs = (json.loads(body).get("result") or {}).get("documents") or {}
    except json.JSONDecodeError:
        return [], [f"ny_openleg {law} A{article}: bad JSON"]
    nodes: list[dict] = []
    _ny_walk_sections(docs, nodes)
    sections: list[Section] = []
    for n in nodes:
        text = (n.get("text") or "").strip()
        if not text:
            continue
        sec = n.get("docLevelId") or ""
        title = (n.get("title") or "").strip()
        sections.append(Section(
            url=f"https://www.nysenate.gov/legislation/laws/{law}/{sec}",
            label=f"{sec} - {title}" if title else f"{law} {sec}",
            citation=f"{law} {sec}", text=text, text_len=len(text),
        ))
    return sections, []


# --- Connecticut official source (cga.ct.gov, whole-chapter HTML) ---
# CT serves one HTML page per chapter (every section inline), Word-export latin1,
# behind an incomplete SSL cert chain (fetch_bytes retries verify=False).
# Sections are delimited inline by "Sec. <title>-<n>." markers; split on those.
CT_HOST = "cga.ct.gov"
_CT_MARKER = re.compile(r'(Sec\.\s+\d+-[0-9]+[a-z]*\.)')


def is_ct_url(url: str) -> bool:
    return CT_HOST in urllib.parse.urlparse(url).netloc and "/pub/chap_" in url


def parse_ct_chapter_html(html: str, chapter_url: str) -> list[Section]:
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    parts = _CT_MARKER.split(text)
    sections: list[Section] = []
    for i in range(1, len(parts), 2):
        num_m = re.search(r'\d+-[0-9]+[a-z]*', parts[i])
        body = " ".join((parts[i + 1] if i + 1 < len(parts) else "").split())
        if not num_m or len(body) < 20:
            continue
        num = num_m.group(0)
        label = body.split(". ")[0][:200]
        sections.append(Section(
            url=f"{chapter_url}#sec_{num}", label=label,
            citation=f"Sec. {num}", text=body, text_len=len(body),
        ))
    return sections


# --- Vermont / Washington / Virginia (whole-chapter HTML, one fetch) ---
# Each serves an entire chapter on one page with section bodies inline; split on
# the state's section-heading marker. Same shape as CT/NV.
WA_HOST = "leg.wa.gov"
VA_HOST = "law.lis.virginia.gov"


def is_wa_url(url: str) -> bool:
    return WA_HOST in urllib.parse.urlparse(url).netloc and "/RCW/" in url


def is_va_url(url: str) -> bool:
    return VA_HOST in urllib.parse.urlparse(url).netloc and "/vacodefull/" in url


def _split_whole_chapter(html: str, marker: re.Pattern, chapter_url: str,
                         cite_prefix: str = "") -> list[Section]:
    """Generic whole-chapter splitter: break the page text on a section-heading
    marker; each chunk is one section. Drops TOC/short fragments."""
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    parts = marker.split(text)
    sections: list[Section] = []
    for i in range(1, len(parts), 2):
        head = parts[i].strip()
        body = " ".join((parts[i + 1] if i + 1 < len(parts) else "").split())
        if len(body) < 25:
            continue
        num_m = re.search(r'[\d.][\d.A-Za-z-]*', head)
        num = num_m.group(0).rstrip(".") if num_m else head
        sections.append(Section(
            url=f"{chapter_url}#{num}",
            label=body.split(". ")[0][:200],
            citation=f"{cite_prefix}{num}".strip(),
            text=body, text_len=len(body),
        ))
    return sections


# --- Per-section via TOC (ME / ID / MO) ---
# These states publish a chapter table-of-contents page that links to one HTML
# page per section. Shared shape: fetch the TOC, regex out the section ids
# (capture group 1), fetch each section page, pull the body with a state-specific
# extractor. The profession→chapter MAP still rides the Justia hierarchy; a
# chapter_url_template in state_structure.yaml rewrites the matched node to the
# state's TOC url (filling {title}/{chapter}), and the handler re-parses what it
# needs from that url. (MD is the odd one out — no TOC; it walks a GetNext API —
# handled separately below.)
def _toc_section_ids(toc_html: str, link_regex: str) -> list[str]:
    """Ordered-unique section ids from a TOC page via a capture-group regex."""
    ids: list[str] = []
    seen: set[str] = set()
    for m in re.finditer(link_regex, toc_html):
        sid = m.group(1)
        if sid not in seen:
            seen.add(sid)
            ids.append(sid)
    return ids


def pull_via_toc(toc_url: str, link_regex: str, make_url, body_fn, make_cite,
                 source: str) -> tuple[list[Section], list[str]]:
    """Generic per-section-via-TOC puller. Fetch the chapter TOC, enumerate its
    section ids, fetch + extract each section page. body_fn(html, sid) returns
    (text, label); empty text drops the section. Returns (sections, errors)."""
    status, html, err = fetch(toc_url)
    polite_sleep()
    if err or not html or (status and not 200 <= status < 300):
        return [], [f"{source} toc {toc_url}: {err or f'http {status}'}"]
    ids = _toc_section_ids(html, link_regex)
    if not ids:
        return [], [f"{source} toc {toc_url}: no section links (regex {link_regex!r})"]
    sections: list[Section] = []
    errors: list[str] = []
    for sid in ids:
        surl = make_url(sid)
        status, shtml, serr = fetch(surl)
        polite_sleep()
        if serr or not shtml or (status and not 200 <= status < 300):
            errors.append(f"{source} section {surl}: {serr or f'http {status}'}")
            continue
        text, label = body_fn(shtml, sid)
        if not text:
            errors.append(f"{source} section {surl}: empty body")
            continue
        sections.append(Section(url=surl, label=label or make_cite(sid),
                                citation=make_cite(sid), text=text, text_len=len(text)))
    return sections, errors


# Maine — legislature.maine.gov. TOC title{T}ch{N}sec0.html lists the chapter's
# sections as title{T}sec{n}.html; section body is in div.row.section-content.
ME_HOST = "legislature.maine.gov"


def is_me_url(url: str) -> bool:
    return ME_HOST in urllib.parse.urlparse(url).netloc and "/statutes/" in url


def _me_body(html: str, sid: str) -> tuple[str, str]:
    el = BeautifulSoup(html, "html.parser").select_one("div.row.section-content")
    if not el:
        return "", ""
    text = " ".join(el.get_text(" ", strip=True).split())
    return text, text.split(". ", 1)[0][:200]


def pull_me(toc_url: str) -> tuple[list[Section], list[str]]:
    m = re.search(r"/statutes/(\d+)/", toc_url)
    if not m:
        return [], [f"me: cannot parse title from {toc_url}"]
    t = m.group(1)
    return pull_via_toc(
        toc_url,
        rf"title{t}sec(\d+)\.html",
        lambda sid: f"https://{ME_HOST}/statutes/{t}/title{t}sec{sid}.html",
        _me_body,
        lambda sid: f"{t} M.R.S. §{sid}",
        "me",
    )


# Idaho — legislature.idaho.gov. TOC T{T}CH{N}/ links sections as SECT{T}-{n}/.
# The section page repeats TITLE/CHAPTER headers as span.f11s; the statute text
# (+ trailing bracketed history note) are the f11s spans from the one that opens
# with the section number onward.
ID_HOST = "legislature.idaho.gov"


def is_id_url(url: str) -> bool:
    return ID_HOST in urllib.parse.urlparse(url).netloc and "/idstat/" in url


def _id_body(html: str, sid: str) -> tuple[str, str]:
    spans = [" ".join(s.get_text(" ", strip=True).split())
             for s in BeautifulSoup(html, "html.parser").select("span.f11s")]
    start = next((i for i, t in enumerate(spans)
                  if re.match(rf"^{re.escape(sid)}[.\s]", t)), None)
    if start is None:
        return "", ""
    body = " ".join(t for t in spans[start:] if t)
    return body, spans[start].split(". ", 1)[0][:200]


def pull_id(toc_url: str) -> tuple[list[Section], list[str]]:
    m = re.search(r"/Title(\d+)/", toc_url)
    if not m:
        return [], [f"id: cannot parse title from {toc_url}"]
    t = m.group(1)
    toc = toc_url if toc_url.endswith("/") else toc_url + "/"
    return pull_via_toc(
        toc,
        rf"SECT({t}-[0-9]+[A-D]?)",
        lambda sid: f"{toc}SECT{sid}/",
        _id_body,
        lambda sid: f"Idaho Code § {sid}",
        "id",
    )


# Missouri — revisor.mo.gov. TOC OneChapter.aspx?chapter={N} links sections as
# PageSelect.aspx?section={N.NNN}; body served at OneSection.aspx?section={N.NNN}
# in div.norm (regex anchored to this chapter so cross-chapter refs don't leak).
MO_HOST = "revisor.mo.gov"


def is_mo_url(url: str) -> bool:
    return MO_HOST in urllib.parse.urlparse(url).netloc and "OneChapter.aspx" in url


def _mo_body(html: str, sid: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    el = soup.select_one("div.norm")
    if not el:
        return "", ""
    text = " ".join(el.get_text(" ", strip=True).split())
    return text, text.split(". ", 1)[0][:200]


def pull_mo(toc_url: str) -> tuple[list[Section], list[str]]:
    m = re.search(r"chapter=(\d+)", toc_url)
    if not m:
        return [], [f"mo: cannot parse chapter from {toc_url}"]
    chap = m.group(1)
    return pull_via_toc(
        toc_url,
        rf"PageSelect\.aspx\?section=({chap}\.[0-9]+)",
        lambda sid: f"https://{MO_HOST}/main/OneSection.aspx?section={sid}",
        _mo_body,
        lambda sid: f"RSMo § {sid}",
        "mo",
    )


# Maryland — mgaleg.maryland.gov. No chapter TOC page; instead a GetNext API
# returns the next section code within an article. We map the Justia path
# (.../maryland/<article-slug>/title-<n>/) to MD's article code, then walk
# GetNext from {title}-101 until the title prefix changes (= next title) or the
# walk runs out. Section body lives at StatuteText in div#StatuteText. The
# matched node keeps its Justia url (no chapter_url_template) and is intercepted
# here by host, so Justia is never fetched.
MD_HOST = "mgaleg.maryland.gov"
_MD_JUSTIA_RE = re.compile(r"/codes/maryland/([a-z0-9-]+)/title-([0-9a-z]+)", re.I)
# Justia groups MD articles under prose slugs; MD's own site keys them by short
# article code. Extend as new (trade) articles are added.
_MD_ARTICLE_CODE = {
    "business-occupations-and-professions": "gbo",
    "business-regulation": "gbr",
    "health-occupations": "gho",      # most licensed health professions (pharmacy, psychology, ...)
    "health-general": "ghg",
    "insurance": "gin",
    "financial-institutions": "gfi",
    "education": "ged",
    "criminal-procedure": "gcp",
}


def is_md_justia_url(url: str) -> bool:
    return ("law.justia.com" in urllib.parse.urlparse(url).netloc
            and "/maryland/" in url.lower())


def _md_body(html: str, sec: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    el = soup.find(id="StatuteText")
    if not el:
        return "", ""
    text = " ".join(el.get_text(" ", strip=True).split())
    # Strip the leading "Article - <name> Previous Next" navigation boilerplate.
    text = re.sub(r"^Article\s*-\s*.*?\bNext\b\s*", "", text)
    if not text:
        return "", ""
    return text, text.split(". ", 1)[0][:200]


def pull_md(justia_url: str, limit: int | None = None) -> tuple[list[Section], list[str]]:
    m = _MD_JUSTIA_RE.search(justia_url)
    if not m:
        return [], [f"md: cannot parse article/title from {justia_url}"]
    slug, title = m.group(1).lower(), m.group(2).upper()
    code = _MD_ARTICLE_CODE.get(slug)
    if not code:
        return [], [f"md: unknown article slug {slug!r} (add to _MD_ARTICLE_CODE)"]
    sections: list[Section] = []
    errors: list[str] = []
    sec: str | None = f"{title}-101"
    seen: set[str] = set()
    # Bound the GetNext walk by the section cap: a MD title's Health-Occupations
    # walk can be 1000+ sections; without this the per-section cap (applied by the
    # caller only AFTER pull_md returns) never stops the fetch loop, so a single
    # MD state could run for half an hour and stall the whole harvest.
    while sec and sec not in seen and sec.startswith(f"{title}-"):
        if limit and len(sections) >= limit:
            break
        seen.add(sec)
        surl = (f"https://{MD_HOST}/mgawebsite/Laws/StatuteText"
                f"?article={code}&section={sec}&enactments=false&archived=false")
        status, html, err = fetch(surl)
        polite_sleep()
        if err or not html or (status and not 200 <= status < 300):
            errors.append(f"md section {surl}: {err or f'http {status}'}")
            break
        text, label = _md_body(html, sec)
        if text:
            sections.append(Section(
                url=surl, label=label or f"§ {sec}",
                citation=f"Md. Code, {code.upper()} § {sec}",
                text=text, text_len=len(text)))
        # Advance via GetNext (returns the next section code as a quoted string).
        nurl = (f"https://{MD_HOST}/mgawebsite/api/Laws/GetNext"
                f"?articleCode={code}&sectionCode={sec}&enactments=False")
        nstatus, nbody, nerr = fetch(nurl)
        polite_sleep()
        if nerr or not nbody or (nstatus and not 200 <= nstatus < 300):
            break
        # GetNext content-negotiates: bare JSON ("6-102") under some headers, an
        # XML wrapper (<string ...>6-102</string>, empty when the title ends)
        # under curl_cffi's. Pull the inner code out of either shape.
        xm = re.search(r"<string[^>]*>(.*?)</string>", nbody, re.S)
        nxt = (xm.group(1) if xm else nbody).strip().strip('"').strip()
        sec = nxt if nxt and nxt.lower() != "null" else None
    if not sections and not errors:
        errors.append(f"md: walk from {title}-101 yielded 0 sections")
    return sections, errors


# === Medium tier (RI / VT / MT / AZ / FL) ===
# Rhode Island and Vermont are plain per-section-via-TOC (reuse pull_via_toc).
# Montana is a nested parts->sections walk; Arizona is a title-page slice; Florida
# is whole-chapter. See docs/reports/trades_official_sources_plan_2026-06-23.md.

# Rhode Island — webserver.rilegislature.gov (UTF-8). Chapter INDEX.HTM links one
# .htm page per section; the page repeats a citation line then the section as a run
# of <p> from the "§ {sec}." heading until the "History of Section." note.
RI_HOST = "webserver.rilegislature.gov"


def is_ri_url(url: str) -> bool:
    return RI_HOST in urllib.parse.urlparse(url).netloc and "/Statutes/" in url


def _ri_body(html: str, sec: str) -> tuple[str, str]:
    ps = [" ".join(p.get_text(" ", strip=True).split())
          for p in BeautifulSoup(html, "html.parser").find_all("p")]
    ps = [p for p in ps if p]
    start = next((i for i, p in enumerate(ps)
                  if re.match(rf"^§\s*{re.escape(sec)}\.", p)), None)
    if start is None:
        return "", ""
    end = next((i for i in range(start, len(ps))
                if ps[i].startswith("History of Section")), len(ps))
    body = " ".join(ps[start:end])
    label = ps[start].split(". ", 1)[0][:200]
    return body, label


def pull_ri(toc_url: str) -> tuple[list[Section], list[str]]:
    m = re.search(r"/TITLE(\d+)/([^/]+)/INDEX", toc_url, re.I)
    if not m:
        return [], [f"ri: cannot parse title/chapter from {toc_url}"]
    chap = m.group(2)
    toc_dir = toc_url.rsplit("/", 1)[0]
    return pull_via_toc(
        toc_url,
        rf'href="({re.escape(chap)}-[0-9.]+\.[Hh][Tt][Mm])"',
        lambda fn: f"{toc_dir}/{fn}",
        lambda html, fn: _ri_body(html, fn.rsplit(".", 1)[0]),
        lambda fn: f"R.I. Gen. Laws § {fn.rsplit('.', 1)[0]}",
        "ri",
    )


# Vermont — legislature.vermont.gov (UTF-8). Chapter page is TOC-only; section
# bodies live at /statutes/section/{title}/{chap3}/{sec5} in div#main-content,
# after a "(Cite as: ...)" header. The 5-digit url id zero-pads the display number.
VT_HOST = "legislature.vermont.gov"


def is_vt_url(url: str) -> bool:
    return VT_HOST in urllib.parse.urlparse(url).netloc and "/statutes/chapter/" in url


def _vt_body(html: str, disp: str) -> tuple[str, str]:
    el = BeautifulSoup(html, "html.parser").find(id="main-content")
    if not el:
        return "", ""
    txt = " ".join(el.get_text(" ", strip=True).split())
    m = re.search(rf"§\s*{re.escape(disp)}\.", txt)
    if not m:
        return "", ""
    body = txt[m.start():]
    return body, body.split(". ", 1)[0][:200]


def pull_vt(toc_url: str) -> tuple[list[Section], list[str]]:
    m = re.search(r"/statutes/chapter/(\d+)/(\d+)", toc_url)
    if not m:
        return [], [f"vt: cannot parse title/chapter from {toc_url}"]
    title, chap3 = m.group(1), m.group(2)
    return pull_via_toc(
        toc_url,
        rf"statutes/section/{title}/{chap3}/(\d{{5}})",
        lambda sid: f"https://{VT_HOST}/statutes/section/{title}/{chap3}/{sid}",
        lambda html, sid: _vt_body(html, str(int(sid))),
        lambda sid: f"{title} V.S.A. § {int(sid)}",
        "vt",
    )


# Montana — leg.mt.gov MCA (UTF-8). Nested: parts_index -> per-part sections_index
# -> section page (div.section-content). URL components are value*10 zero-padded
# to 4 digits (title 37 -> 0370), and the positional url number != the displayed
# statute number, so URLs are built from the index links, and the citation is
# read from the section body. Intercepted from the Justia montana url (like MD).
MT_HOST = "leg.mt.gov"
_MT_JUSTIA_RE = re.compile(r"/codes/montana/.*?title-(\d+)/chapter-(\d+)", re.I)


def is_mt_justia_url(url: str) -> bool:
    return ("law.justia.com" in urllib.parse.urlparse(url).netloc
            and "/montana/" in url.lower())


def _mt_body(html: str) -> tuple[str, str]:
    el = BeautifulSoup(html, "html.parser").find("div", class_="section-content")
    if not el:
        return "", ""
    txt = " ".join(el.get_text(" ", strip=True).split())
    m = re.match(r"(\d+-\d+-\d+)\s*\.?\s*", txt)
    if not m:
        return "", ""
    return txt, m.group(1)


def pull_mt(justia_url: str) -> tuple[list[Section], list[str]]:
    m = _MT_JUSTIA_RE.search(justia_url)
    if not m:
        return [], [f"mt: cannot parse title/chapter from {justia_url}"]
    title, chap = int(m.group(1)), int(m.group(2))
    base = f"https://{MT_HOST}/bills/mca/title_{title*10:04d}/chapter_{chap*10:04d}"
    pstatus, phtml, perr = fetch(f"{base}/parts_index.html")
    polite_sleep()
    if perr or not phtml or (pstatus and not 200 <= pstatus < 300):
        return [], [f"mt parts_index {base}: {perr or f'http {pstatus}'}"]
    parts = []
    for p in re.findall(r"part_(\d{4})/sections_index\.html", phtml):
        if p not in parts:
            parts.append(p)
    sections: list[Section] = []
    errors: list[str] = []
    for part in parts:
        pdir = f"{base}/part_{part}"
        sstatus, shtml, serr = fetch(f"{pdir}/sections_index.html")
        polite_sleep()
        if serr or not shtml or (sstatus and not 200 <= sstatus < 300):
            errors.append(f"mt sections_index {pdir}: {serr or f'http {sstatus}'}")
            continue
        links = []
        for ln in re.findall(r"(section_\d{4}/[\d-]+\.html)", shtml):
            if ln not in links:
                links.append(ln)
        for ln in links:
            surl = f"{pdir}/{ln}"
            status, html, err = fetch(surl)
            polite_sleep()
            if err or not html or (status and not 200 <= status < 300):
                errors.append(f"mt section {surl}: {err or f'http {status}'}")
                continue
            text, num = _mt_body(html)
            if not text:
                errors.append(f"mt section {surl}: empty body")
                continue
            sections.append(Section(url=surl, label=text.split(". ", 1)[0][:200],
                                    citation=f"MCA § {num}", text=text, text_len=len(text)))
    return sections, errors


# Arizona — azleg.gov (UTF-8). The title page lists every chapter inline; slice the
# HTML between id="chapter{N}" and id="chapter{N+1}", harvest ars/{T}/{id}.htm
# links, fetch each section page (small, near-chrome-free). Title 32 Ch 10 =
# Contractors. (AZ HVAC is not a separate license — folded into contractor.)
AZ_HOST = "azleg.gov"


def is_az_url(url: str) -> bool:
    return AZ_HOST in urllib.parse.urlparse(url).netloc and "arsDetail" in url


def _az_body(html: str, num: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style"]):
        t.decompose()
    txt = " ".join(soup.get_text(" ", strip=True).split())
    m = re.search(rf"{re.escape(num)}\s*\.\s*", txt)  # the "32-1101 . " body marker
    if not m:
        return "", ""
    body = txt[m.start():]
    return body, body.split(". ", 1)[0][:200]


def pull_az(detail_url: str) -> tuple[list[Section], list[str]]:
    q = urllib.parse.parse_qs(urllib.parse.urlparse(detail_url).query)
    title = (q.get("title") or [""])[0]
    chap = (q.get("chapter") or [""])[0]
    if not title or not chap:
        return [], [f"az: need title & chapter in {detail_url}"]
    status, html, err = fetch(f"https://www.{AZ_HOST}/arsDetail/?title={title}")
    polite_sleep()
    if err or not html or (status and not 200 <= status < 300):
        return [], [f"az title {title}: {err or f'http {status}'}"]
    a = html.find(f'id="chapter{chap}"')
    if a < 0:
        return [], [f"az: chapter{chap} anchor not found in title {title}"]
    b = html.find(f'id="chapter{int(chap)+1}"', a)
    chunk = html[a:b if b > 0 else len(html)]
    ids = []
    for sid in re.findall(rf"ars/{title}/(\d+)\.htm", chunk):
        if sid not in ids:
            ids.append(sid)
    sections: list[Section] = []
    errors: list[str] = []
    for sid in ids:
        num = f"{title}-{int(sid)}"  # 01101 -> 32-1101
        surl = f"https://www.{AZ_HOST}/ars/{title}/{sid}.htm"
        status, shtml, serr = fetch(surl)
        polite_sleep()
        if serr or not shtml or (status and not 200 <= status < 300):
            errors.append(f"az section {surl}: {serr or f'http {status}'}")
            continue
        text, label = _az_body(shtml, num)
        if not text:
            errors.append(f"az section {surl}: empty body")
            continue
        sections.append(Section(url=surl, label=label,
                                citation=f"A.R.S. § {num}", text=text, text_len=len(text)))
    return sections, errors


# Florida — leg.state.fl.us (UTF-8). One whole-chapter page; each section is a
# div.Section with SectionNumber / Catchline / SectionBody spans. The top index
# also emits SectionNumber spans, so require a non-trivial SectionBody.
FL_HOST = "leg.state.fl.us"


def is_fl_url(url: str) -> bool:
    return FL_HOST in urllib.parse.urlparse(url).netloc and "Display_Statute" in url


def parse_fl_chapter(html: str, url: str) -> list[Section]:
    sections: list[Section] = []
    for d in BeautifulSoup(html, "html.parser").select("div.Section"):
        num_el = d.find(class_="SectionNumber")
        body_el = d.find(class_="SectionBody")
        if not num_el or not body_el:
            continue
        num = " ".join(num_el.get_text(" ", strip=True).split())
        body = " ".join(body_el.get_text(" ", strip=True).split())
        if len(body) < 25:
            continue
        cat_el = d.find(class_="Catchline")
        catch = " ".join(cat_el.get_text(" ", strip=True).split()) if cat_el else ""
        full = f"{num} {catch} {body}".strip()
        sections.append(Section(
            url=f"{url}#{num}", label=(f"{num} {catch}").strip()[:200] or num,
            citation=f"Fla. Stat. § {num}", text=full, text_len=len(full)))
    return sections


# --- Illinois (Justia serves a whole ILCS act on one page) ---
# Like PA, IL acts arrive as ONE inline blob rather than per-section URLs, but the
# text carries an ILCS citation marker at the head of every section
# ("(225 ILCS 80/4.5)"). Split on those so IL gets section-level citations and a
# navigable browse view instead of one ~80k-char blob (issue #6). Reusable as a
# local transform on already-committed IL corpora — no re-fetch needed.
_IL_ILCS_MARKER = re.compile(r"\((\d+\s+ILCS\s+\d+/[0-9A-Za-z.\-]+)\)")


def looks_like_il_ilcs(text: str) -> bool:
    return len(_IL_ILCS_MARKER.findall(text)) >= 3


# North Dakota chapter pages render the WHOLE chapter as one inline blob (no
# per-section links), with line-anchored "title-chapter-section." markers
# (e.g. "43-09-01.", "43-44.1-02."). Split on those so ND gets per-section
# records instead of one 30-50k-char blob (was 1-3 "sections" across 13
# professions). Reusable as a local transform on committed ND corpora — no
# re-fetch (per CLAUDE.md).
_ND_SEC_MARKER = re.compile(r"(?m)^\s*(\d+-\d+(?:\.\d+)?-\d+(?:\.\d+)?)\.\s")


def looks_like_nd_blob(text: str, url: str) -> bool:
    return "north-dakota" in url.lower() and len(_ND_SEC_MARKER.findall(text)) >= 3


def split_nd_blob(text: str, url: str) -> list[Section]:
    """Split an ND chapter blob into per-section records on the line-anchored
    section markers. citation = the ND section number; url stays the chapter
    page. Returns [] if fewer than 3 markers."""
    hits = list(_ND_SEC_MARKER.finditer(text))
    if len(hits) < 3:
        return []
    sections: list[Section] = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        body = text[m.start():end].strip()
        if not body:
            continue
        label = body.split("\n", 1)[0][:300]
        sections.append(Section(url=url, label=label, citation=m.group(1),
                                text=body, text_len=len(body)))
    return sections


def split_il_inline(text: str, url: str) -> list[Section]:
    """Split one ILCS act blob into per-section records on the '(NNN ILCS MM/SS)'
    markers. citation = the ILCS ref (e.g. '225 ILCS 80/4.5'); url stays the act
    page (IL has no reliable per-section URLs). Returns [] if no markers found."""
    hits = list(_IL_ILCS_MARKER.finditer(text))
    sections: list[Section] = []
    for i, m in enumerate(hits):
        end = hits[i + 1].start() if i + 1 < len(hits) else len(text)
        body = text[m.start():end].strip()
        if not body:
            continue
        cite = m.group(1)
        label = cite
        title = re.search(r"Sec\.?\s+[0-9A-Za-z.\-]+\.?\s*(.{0,120})", body)
        if title:
            label = f"Sec. {cite.rsplit('/', 1)[-1]}. {title.group(1).strip()}"[:300]
        sections.append(Section(url=url, label=label, citation=cite,
                                text=body, text_len=len(body)))
    return sections


# A fetched section can come back HTTP 200 yet contain NO statute text — an empty
# extraction (selectors + fallback both miss) or a Cloudflare/bot page that returns
# 200 (a soft rate-block, or a challenge whose wording the CDP check missed). If we
# save that as an ok section, downstream stages treat the corpus as complete and the
# only fix is re-fetching from Justia. So flag these as errors (the grind re-pulls
# flagged sections) instead of silently shipping them. CF markers are page-specific
# so they won't appear in real statute text.
_BLOCK_MARKERS = (
    "just a moment",
    "verifying you are human",
    "attention required! | cloudflare",
    "needs to review the security of your connection",
    "enable javascript and cookies to continue",
    "cloudflare ray id",
)


def bad_section_text(text: str) -> str | None:
    """Reason the extracted text is not real statute content, else None."""
    t = (text or "").strip()
    # 15-char floor: a real Justia/CDP section always extracts >100 chars (nav +
    # catchline + history), so only a failed extraction lands here. Kept low so
    # legit title-only sections from official-source handlers (e.g. CT
    # "Ownership of businesses.") aren't false-flagged on a re-pull.
    if len(t) < 15:
        return f"empty/thin extraction ({len(t)} chars) — re-pull"
    low = t.lower()
    if any(m in low for m in _BLOCK_MARKERS):
        return "looks like a Cloudflare/bot block page — re-pull"
    return None


def extract_section_text(html: str) -> str:
    """Extract the main statute text from a section page across known sources.

    Selector cascade (first hit wins, must yield > 200 chars):
      Justia                  #codes-content, div.primary-content
      MN revisor.mn.gov       .section
      MI legislature.mi.gov   div[class*="section"] (Sec. NNNN block)
    Falls back to the largest plausible content div if none match.
    """
    soup = BeautifulSoup(html, "html.parser")
    for sel in [
        "#codes-content",
        "div.primary-content",
        ".section",                      # MN revisor
        'div[class*="section"]',         # MI legislature
        "main #main-content",
    ]:
        el = soup.select_one(sel)
        if el:
            text = el.get_text("\n", strip=True)
            if len(text) > 200:
                return text
    # Fallback: largest div between 500 and 200_000 chars
    best = ""
    for div in soup.find_all(["div", "article", "section", "main"]):
        text = div.get_text("\n", strip=True)
        if 500 < len(text) < 200_000 and len(text) > len(best):
            best = text
    return best


# Justia URL slugs that are intermediate (drill-able) rather than leaf sections.
# Includes nested chapter/subtitle layouts seen in IN, MD, etc.
INTERMEDIATE_SEG = re.compile(
    r"^(subchapter|subpart|part|division|subdivision|chapter|subtitle|article)[-_][0-9a-z]",
    re.IGNORECASE,
)


def short_citation(label: str) -> str:
    """Pull a short '§ X' or 'X-Y' style cite from a section label."""
    # e.g. "Section 20-50. - Podiatric medicine defined." -> "20-50"
    m = re.search(r"(?:section\s+|§\s*)?([0-9]+[A-Za-z]?(?:[-:.][0-9A-Za-z]+)+)", label, re.IGNORECASE)
    if m:
        return m.group(1)
    return label[:60]


def collect_section_targets(url: str, label: str, slug: str, depth: int, max_depth: int = SECTION_WALK_MAX_DEPTH) -> tuple[list[dict], str | None]:
    """Walk a chapter/subchapter URL down to leaf section URLs.

    Returns (section_targets, error). Side-effect: sleeps PER_HOST_DELAY between
    fetches. If the URL itself contains substantial text and no children, treats
    the URL as a single leaf section (handles IL-style pages where the entire
    act lives at the chapter URL).

    max_depth defaults to 6 (from config/limits.yaml pull.section_walk_max_depth) —
    deep enough to cover any real Justia nesting (chapter→subchapter→sub-subchapter
    →sections).  The old default of 2 silently truncated chapters nested deeper than
    two levels; 6 terminates naturally when a level yields leaf sections or nothing.

    When the walk halts because depth >= max_depth but intermediates remain (i.e.
    it *wanted* to go deeper), a "depth_capped" string is returned as the error so
    callers can record it.  Already-collected sections are still returned intact.
    """
    status, html, err = fetch(url)
    polite_sleep()
    if err or not html or (status and not 200 <= status < 300):
        return [], f"fetch {url}: {err or status}"

    sections, intermediates = extract_child_links(html, url)
    if sections:
        return sections, None
    # Depth cap reached while intermediates still exist — this is a real truncation.
    if intermediates and depth >= max_depth:
        msg = f"depth_capped at {url} (depth={max_depth})"
        log.warning("collect_section_targets: %s — sections below this level were NOT fetched", msg)
        return [], msg
    # No leaf sections — try drilling intermediates (subchapter-*, etc.) up to depth
    if intermediates and depth < max_depth:
        all_secs: list[dict] = []
        any_depth_capped: str | None = None
        for inter in intermediates:
            secs, ierr = collect_section_targets(inter["url"], inter["label"], inter["slug"], depth + 1, max_depth)
            if ierr:
                if ierr.startswith("depth_capped"):
                    any_depth_capped = ierr  # bubble up so the top-level caller records it
                else:
                    log.info("    intermediate err: %s", ierr)
            all_secs.extend(secs)
        if all_secs:
            # Cross-page year duplicates can survive per-page dedup (e.g. a year
            # snapshot reached via one intermediate + the unversioned copy via
            # another). Collapse them once the whole walk is assembled.
            # Even if some branch was depth_capped, return what we got + the signal.
            return _dedupe_year_versions(all_secs), any_depth_capped
        if any_depth_capped:
            return [], any_depth_capped
    # No children at all — the URL itself may be the leaf (IL-style)
    text = extract_section_text(html)
    if len(text) > 500:
        return [{"url": url, "label": label, "slug": slug, "_inline_text": text}], None
    return [], None


# Over-broad chapter guard (config: PULL_OVER_BROAD_MAX; set very high to disable).
# 300 skips the true mis-picks (whole titles/departments run 400–3300 leaves) while
# letting a legitimately-mid-size chapter with an off-wording label (e.g. CA producers'
# "Production Agencies", 219) still pull.
_OVER_BROAD_MAX = int(os.environ.get("PULL_OVER_BROAD_MAX", "300"))

# Hard fetch-budget ceiling — OPT IN via PULL_BATCH_TIMEOUT_SECONDS (unset/0 disables;
# this is the default, so a plain/manual/one-off pull is unaffected and can grind through
# a legitimately huge chapter like Medicine's own 500+ section chapter with no artificial
# cap). gap_pull.sh (the automated gap-harvest driver) sets PULL_BATCH_TIMEOUT_SECONDS=900
# to match its own `timeout ... 900` wrapper, because at fetch.per_host_delay_seconds per
# section (plus up to 60% jitter -> ~1.3x average) a chapter with too many leaves CANNOT
# finish inside THAT specific 900s per-cell budget no matter how many times it's retried
# -- it just burns the full 900s and reverts empty every time (the 2026-07-07 lesson:
# NE/MA/CA chapters of 219-603 leaves whose labels happened to name-match the profession,
# e.g. "Chapter 45 - Interest, Loans, and Debt" matching "loan", sailed past the
# label-mismatch check below and looped for hours). This ceiling is independent of label
# match -- size alone determines fetchability within a fixed time budget. ~120s is
# reserved for the chapter-discovery walk + fetch/commit overhead before the per-section
# budget starts.
_DISCOVERY_OVERHEAD_SECONDS = 120


def _fetch_budget_max_leaves() -> int:
    """0 (disabled) unless the caller opts in via PULL_BATCH_TIMEOUT_SECONDS."""
    override = os.environ.get("PULL_FETCH_BUDGET_MAX_LEAVES")
    if override is not None:
        return int(override)
    timeout_s = int(os.environ.get("PULL_BATCH_TIMEOUT_SECONDS", "0"))
    if timeout_s <= 0:
        return 0
    per_page = load_limits()["fetch"]["per_host_delay_seconds"] * 1.3
    budget = timeout_s - _DISCOVERY_OVERHEAD_SECONDS
    return int(budget / per_page) if per_page > 0 else 0


def _should_skip_over_broad(profession: str, chapter_label: str, n_leaves: int) -> bool:
    """True when a chapter should be skipped rather than fetched in full: either it
    physically cannot finish inside an opted-in caller's per-cell timeout (size alone,
    regardless of label -- see _fetch_budget_max_leaves; disabled unless the caller sets
    PULL_BATCH_TIMEOUT_SECONDS), or it's an unscoped locator mis-pick (too many leaves
    AND its label does not name the profession). Never raises (a guard must not break
    a pull)."""
    budget_max = _fetch_budget_max_leaves()
    if budget_max and n_leaves > budget_max:
        return True
    if n_leaves <= _OVER_BROAD_MAX:
        return False
    try:
        from pipeline.config.loaders import load_professions
        from pipeline.discover.match_profession import label_matches
        meta = load_professions().get(profession, {}) or {}
        pats = meta.get("patterns") or []
        if not pats:                       # can't judge relevance → don't skip
            return False
        return not label_matches(chapter_label, pats, meta.get("excludes") or [])
    except Exception:
        return False


def _flag_over_broad(profession: str, state: str, url: str, label: str, n: int) -> None:
    """Append a skipped over-broad cell to results/gap_harvest/over_broad_auto.json for
    later narrowing/review. Best-effort — never raises."""
    try:
        from pipeline.paths import RESULTS_DIR
        p = RESULTS_DIR / "gap_harvest" / "over_broad_auto.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        data = json.loads(p.read_text()) if p.exists() else []
        budget_max = _fetch_budget_max_leaves()
        reason = ("fetch_budget" if budget_max and n > budget_max else "label_mismatch")
        data.append({"profession": profession, "state": state, "url": url,
                     "label": label, "leaves": n, "reason": reason})
        p.write_text(json.dumps(data, indent=1))
    except Exception:
        pass


def pull_state(state: str, profession: str, rows: list[dict], limit_sections: int | None) -> StateCorpus:
    corpus = StateCorpus(state=state, profession=profession)
    seen_section_urls: set[str] = set()

    # Official-source dispatch is gated on the state's `source` flag (not just the
    # URL) so removing a `source:` override in state_structure.yaml flips that
    # state back to the Justia/CDP path — the Justia-only migration mechanism.
    _source = (load_state_structure().get(state) or {}).get("source") or "justia"

    log.info("[%s] %d matching chapter rows", state, len(rows))
    for row in rows:
        url = row["chapter_url"]
        corpus.chapter_urls.append(url)

        # Utah official source: le.utah.gov ships a structured XML per chapter.
        # Fetch the chapter page, find its content fragment, swap .html->.xml,
        # and parse all sections in one shot (no per-section fetching). Handled
        # entirely here like PA — sections share the chapter url scheme but each
        # gets its own section url, so move on after.
        if is_utah_le_url(url):
            status, html, err = fetch(url)
            polite_sleep()
            if err or not html or (status and not 200 <= status < 300):
                corpus.errors.append(f"utah_le fetch {url}: {err or f'http {status}'}")
                continue
            xml_url = _utah_xml_url_from_chapter(html, url)
            if not xml_url:
                corpus.errors.append(f"utah_le {url}: no XML fragment ref found")
                continue
            xstatus, xhtml, xerr = fetch(xml_url)
            polite_sleep()
            if xerr or not xhtml or (xstatus and not 200 <= xstatus < 300):
                corpus.errors.append(f"utah_le xml {xml_url}: {xerr or f'http {xstatus}'}")
                continue
            ut_sections = parse_utah_chapter_xml(xhtml.encode("utf-8"), url)
            if not ut_sections:
                corpus.errors.append(f"utah_le parse {xml_url}: 0 sections")
            for sec in ut_sections:
                if limit_sections and len(corpus.sections) >= limit_sections:
                    break
                corpus.sections.append(sec)
                corpus.total_chars += sec.text_len
            log.info("  utah_le %s -> %d sections", xml_url, len(ut_sections))
            continue

        # South Dakota official source: walk the JSON API from the chapter cite
        # through its sections. Handled here (one logical chapter = many API
        # nodes), like PA/UT.
        if is_sd_api_url(url):
            sd_sections, sd_errors = pull_sd_chapter(url)
            corpus.errors.extend(sd_errors)
            for sec in sd_sections:
                if limit_sections and len(corpus.sections) >= limit_sections:
                    break
                corpus.sections.append(sec)
                corpus.total_chars += sec.text_len
            log.info("  sd_api %s -> %d sections", url, len(sd_sections))
            continue

        # Nevada official source: one HTML page per chapter; parse sections out.
        # NV serves Word-export latin1 HTML, so decode bytes ourselves.
        if is_nv_url(url) and _source == "nv_official":
            status, raw, err = fetch_bytes(url)
            polite_sleep()
            if err or not raw or (status and not 200 <= status < 300):
                corpus.errors.append(f"nv fetch {url}: {err or f'http {status}'}")
                continue
            html = raw.decode("latin1", "replace")
            nv_sections = parse_nv_chapter_html(html, url)
            if not nv_sections:
                corpus.errors.append(f"nv parse {url}: 0 sections")
            for sec in nv_sections:
                if limit_sections and len(corpus.sections) >= limit_sections:
                    break
                corpus.sections.append(sec)
                corpus.total_chars += sec.text_len
            log.info("  nv %s -> %d sections", url, len(nv_sections))
            continue

        # Connecticut official source: one HTML page per chapter, latin1.
        if is_ct_url(url):
            status, raw, err = fetch_bytes(url)
            polite_sleep()
            if err or not raw or (status and not 200 <= status < 300):
                corpus.errors.append(f"ct fetch {url}: {err or f'http {status}'}")
                continue
            ct_sections = parse_ct_chapter_html(raw.decode("latin1", "replace"), url)
            if not ct_sections:
                corpus.errors.append(f"ct parse {url}: 0 sections")
            for sec in ct_sections:
                if limit_sections and len(corpus.sections) >= limit_sections:
                    break
                corpus.sections.append(sec)
                corpus.total_chars += sec.text_len
            log.info("  ct %s -> %d sections", url, len(ct_sections))
            continue

        # Washington / Virginia: whole-chapter HTML, one fetch. Markers are
        # ANCHORED to this chapter's number so in-text cross-references to other
        # chapters don't create false section breaks. (VT's chapter page is
        # TOC-only — handled per-section elsewhere, not here.)
        _whole = None
        if is_wa_url(url):
            m = re.search(r'cite=([\d.]+)', url)
            if m:
                _whole = (re.compile(r'(?m)^\s*(RCW\s+' + re.escape(m.group(1)) + r'\.\d+\w*)'), "")
        elif is_va_url(url):
            mt = re.search(r'/title([\d.]+)/chapter(\d+\w*)/', url)
            if mt:
                _whole = (re.compile(r'(?m)^\s*(§\s*' + re.escape(mt.group(1)) + '-' + mt.group(2) + r'\d\d\w*\.)'), "§ ")
        if _whole is not None:
            marker, prefix = _whole
            status, html, err = fetch(url)
            polite_sleep()
            if err or not html or (status and not 200 <= status < 300):
                corpus.errors.append(f"whole-chapter fetch {url}: {err or f'http {status}'}")
                continue
            secs = _split_whole_chapter(html, marker, url, prefix)
            if not secs:
                corpus.errors.append(f"whole-chapter parse {url}: 0 sections")
            for sec in secs:
                if limit_sections and len(corpus.sections) >= limit_sections:
                    break
                corpus.sections.append(sec)
                corpus.total_chars += sec.text_len
            log.info("  whole-chapter %s -> %d sections", url, len(secs))
            continue

        # New York: Justia url carries lawId+article; pull from OpenLegislation.
        # Gated on source == ny_official (2026-07-02) so NY can flip to Justia like
        # MD/NV — with source: justia (the default) this intercept is skipped and NY
        # pulls directly from Justia. Set source: ny_official to keep nysenate.
        if is_ny_justia_url(url) and _source == "ny_official":
            key = _ny_openleg_key()
            if not key:
                corpus.errors.append("ny: NY_OPENLEG_KEY not set (sign up at legislation.nysenate.gov)")
                continue
            ny_sections, ny_errors = pull_ny_article(url, key)
            corpus.errors.extend(ny_errors)
            for sec in ny_sections:
                if limit_sections and len(corpus.sections) >= limit_sections:
                    break
                corpus.sections.append(sec)
                corpus.total_chars += sec.text_len
            log.info("  ny_openleg %s -> %d sections", url, len(ny_sections))
            continue

        # Per-section-via-TOC states (ME/ID/MO) and Maryland's GetNext walk.
        # Each is self-contained (one logical chapter -> many section fetches),
        # so handle here and move on like PA/UT/SD.
        _ps = None
        if is_me_url(url):
            _ps = pull_me(url)
        elif is_id_url(url):
            _ps = pull_id(url)
        elif is_mo_url(url):
            _ps = pull_mo(url)
        elif is_md_justia_url(url) and _source == "md_official":
            _ps = pull_md(url, limit_sections)
        elif is_ri_url(url):
            _ps = pull_ri(url)
        elif is_vt_url(url):
            _ps = pull_vt(url)
        elif is_mt_justia_url(url) and _source == "mt_official":
            _ps = pull_mt(url)
        elif is_az_url(url):
            _ps = pull_az(url)
        elif is_fl_url(url):
            status, html, err = fetch(url)
            polite_sleep()
            if err or not html or (status and not 200 <= status < 300):
                _ps = ([], [f"fl fetch {url}: {err or f'http {status}'}"])
            else:
                _ps = (parse_fl_chapter(html, url), [])
        if _ps is not None:
            ps_sections, ps_errors = _ps
            corpus.errors.extend(ps_errors)
            if not ps_sections:
                corpus.errors.append(f"per-section {url}: 0 sections")
            for sec in ps_sections:
                if limit_sections and len(corpus.sections) >= limit_sections:
                    break
                corpus.sections.append(sec)
                corpus.total_chars += sec.text_len
            log.info("  per-section %s -> %d sections", url, len(ps_sections))
            continue

        # Pennsylvania: each URL is a whole act; fetch once per act and split
        # locally into per-section records (sections share the act URL, so the
        # seen_section_urls URL-dedup below would wrongly collapse them — handle
        # PA entirely here and move on). A profession may span more than one act
        # (e.g. nursing = Professional Nursing Law + Practical Nurse Law); list
        # the extra acts in section_url_list and we pull them all.
        pa_urls = list(dict.fromkeys(
            u for u in [url, *(row.get("section_url_list") or [])] if is_pa_legis_url(u)
        ))
        if pa_urls:
            for pa_url in pa_urls:
                status, html, err = fetch(pa_url)
                polite_sleep()
                if err or not html or (status and not 200 <= status < 300):
                    corpus.errors.append(f"pa_legis fetch {pa_url}: {err or f'http {status}'}")
                    continue
                pa_sections = parse_pa_act(html, pa_url)
                if not pa_sections:
                    corpus.errors.append(f"pa_legis parse {pa_url}: 0 sections (markers not found)")
                # pa_keep_sections scopes an embedded profession to its own
                # sections within a shared act (e.g. dietetics inside the Nursing
                # Law). Citation is "§ <num>"; keep only the listed numbers.
                keep = {str(k) for k in (row.get("pa_keep_sections") or [])}
                if keep:
                    before = len(pa_sections)
                    pa_sections = [s for s in pa_sections
                                   if s.citation.replace("§", "").strip() in keep]
                    log.info("  pa_legis keep-filter: %d -> %d sections", before, len(pa_sections))
                for sec in pa_sections:
                    if limit_sections and len(corpus.sections) >= limit_sections:
                        break
                    corpus.sections.append(sec)
                    corpus.total_chars += sec.text_len
                log.info("  pa_legis %s -> %d sections", pa_url, len(pa_sections))
            continue

        # Manual-override "section filter" mode: pull a specific list of section
        # URLs, OR pull the chapter's children and filter by a slug regex.
        # Used for states whose podiatry law is a section range inside a much
        # bigger chapter (e.g. AZ §§32-801..32-859 within Title 32).
        section_url_list = row.get("section_url_list")
        section_slug_pattern = row.get("section_slug_pattern")

        if section_url_list:
            section_targets = [{"url": u, "label": "", "slug": u.rstrip("/").rsplit("/", 1)[-1]}
                               for u in section_url_list]
            log.info("  chapter %s -> %d explicit section URLs", url, len(section_targets))
        elif section_slug_pattern:
            status, html, err = fetch(url)
            polite_sleep()
            if err or not html or (status and not 200 <= status < 300):
                corpus.errors.append(f"chapter fetch {url}: {err or status}")
                continue
            all_sections = extract_child_links(html, url)[0]
            pat = re.compile(section_slug_pattern)
            section_targets = [s for s in all_sections if pat.match(s["slug"])]
            log.info("  chapter %s -> %d sections after slug filter %r",
                     url, len(section_targets), section_slug_pattern)
        elif is_section_url(url):
            section_targets = [{"url": url, "label": row["chapter_label"], "slug": row["chapter_slug"]}]
        else:
            section_targets, terr = collect_section_targets(
                url, row["chapter_label"], row["chapter_slug"], depth=0,
            )
            if terr:
                corpus.errors.append(terr)
            log.info("  chapter %s -> %d leaf sections", url, len(section_targets))
            # Over-broad guard: skip in seconds + flag for narrowing instead of grinding
            # a 900s timeout that produces nothing (all-or-nothing revert). Two distinct
            # reasons: (1) too many leaves to physically fetch inside the automated batch
            # driver's per-cell timeout, regardless of label — a big chapter that name-
            # matches the profession (e.g. NE "Chapter 45 - Interest, Loans, and Debt"
            # matching "loan") still can't finish in time; or (2) a locator mis-pick
            # (whole title/department) whose label doesn't name the profession at all.
            if _should_skip_over_broad(profession, row.get("chapter_label", ""), len(section_targets)):
                budget_max = _fetch_budget_max_leaves()
                n = len(section_targets)
                why = (f"exceeds fetch budget ({n} > {budget_max} leaves)"
                       if budget_max and n > budget_max else
                       f"label {row.get('chapter_label', '')!r} doesn't match {profession}")
                log.warning("  SKIP over-broad: %s -> %d leaves; %s — flagged", url, n, why)
                corpus.errors.append(f"over_broad_skip {url}: {len(section_targets)} leaves")
                _flag_over_broad(profession, state, url, row.get("chapter_label", ""), len(section_targets))
                continue

        for sec in section_targets:
            if sec["url"] in seen_section_urls:
                continue
            seen_section_urls.add(sec["url"])
            if limit_sections and len(corpus.sections) >= limit_sections:
                break

            # Inline text already captured by collect_section_targets (IL-style).
            # If it's an ILCS act blob, split it into per-section records so IL
            # gets section-level citations + browse instead of one blob (#6).
            if "_inline_text" in sec:
                text = sec["_inline_text"]
                inline_split = (split_il_inline(text, sec["url"]) if looks_like_il_ilcs(text)
                                else split_nd_blob(text, sec["url"]) if looks_like_nd_blob(text, sec["url"])
                                else [])
                if inline_split:
                    for s in inline_split:
                        if limit_sections and len(corpus.sections) >= limit_sections:
                            break
                        corpus.sections.append(s)
                        corpus.total_chars += s.text_len
                    log.info("  inline-blob split %s -> %d sections", sec["url"], len(inline_split))
                    continue
                corpus.sections.append(Section(
                    url=sec["url"], label=sec["label"],
                    citation=short_citation(sec["label"]),
                    text=text, text_len=len(text),
                ))
                corpus.total_chars += len(text)
                continue

            status, html, err = fetch(sec["url"])
            polite_sleep()
            if err or not html or (status and not 200 <= status < 300):
                # Aggregate into corpus.errors too — otherwise a state with
                # per-section failures looks healthy at the top level and
                # downstream stages extract from a silently partial corpus
                # (bit us 2026-06-12: 5 of 9 MI dietetics sections timed out
                # and nothing flagged it).
                corpus.errors.append(f"section fetch {sec['url']}: {err or f'http {status}'}")
                corpus.sections.append(Section(
                    url=sec["url"], label=sec["label"],
                    citation=short_citation(sec["label"]),
                    text="", error=err or f"http {status}",
                ))
                continue
            text = extract_section_text(html)
            bad = bad_section_text(text)
            if bad:
                # 200 OK but no real statute text (empty extraction or a block
                # page). Flag it so the resumable grind re-pulls rather than
                # silently shipping a partial/corrupt corpus (would force a
                # blind re-scrape). Keep the text for inspection.
                corpus.errors.append(f"section {sec['url']}: {bad}")
                corpus.sections.append(Section(
                    url=sec["url"], label=sec["label"],
                    citation=short_citation(sec["label"]),
                    text=text, text_len=len(text), error=bad,
                ))
                continue
            corpus.sections.append(Section(
                url=sec["url"], label=sec["label"],
                citation=short_citation(sec["label"]),
                text=text, text_len=len(text),
            ))
            corpus.total_chars += len(text)

    return corpus


def _corpus_health(d: dict) -> tuple[int, int]:
    """(ok_section_count, total_chars) for a corpus dict (asdict or loaded JSON)."""
    secs = d.get("sections") or []
    ok = sum(1 for s in secs if not s.get("error"))
    return ok, int(d.get("total_chars") or 0)


def _is_regression(new_d: dict, old_d: dict) -> str | None:
    """Return a reason string if writing new_d over old_d would lose good data,
    else None. Guards against Justia blocks / partial fetches (empty or collapsed
    bodies) silently clobbering a healthy committed corpus."""
    new_ok, new_chars = _corpus_health(new_d)
    old_ok, old_chars = _corpus_health(old_d)
    if old_ok == 0:
        return None  # old was already empty/partial — nothing to protect
    if new_ok == 0:
        return f"new pull has 0 ok sections vs {old_ok} committed"
    if new_ok < old_ok:
        return f"new pull has {new_ok} ok sections vs {old_ok} committed"
    if new_ok == old_ok and new_chars < old_chars * 0.5:
        return f"new pull text collapsed to {new_chars} chars vs {old_chars} committed (same {new_ok} sections)"
    return None


def _summary_row(state: str, d: dict) -> dict:
    secs = d.get("sections") or []
    return {
        "state": state,
        "sections": len(secs),
        "ok_sections": sum(1 for s in secs if not s.get("error")),
        "total_chars": int(d.get("total_chars") or 0),
        "errors": len(d.get("errors") or []),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True, help="Profession name from professions.yaml (e.g. 'podiatry')")
    ap.add_argument("--states", default="", help="Comma-separated subset of states; empty = all matching")
    ap.add_argument("--limit-sections", type=int,
                    default=load_limits()["pull"]["default_limit_sections"],
                    help="Per-state section cap (default %(default)s, from config/limits.yaml). "
                         "RUNAWAY GUARD: a whole-title over-match (a profession mapped to a "
                         "2500-section state-government title) is capped + loudly FLAGGED instead "
                         "of silently pulling thousands of sections. Pass 0 to disable, or a real "
                         "chapter rarely exceeds 500.")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite an existing committed corpus even if the new pull is worse "
                         "(fewer ok sections / collapsed text). Off by default so a Justia block "
                         "or partial fetch can't clobber good committed data.")
    args = ap.parse_args()

    profession = args.profession.lower()
    only_states = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    index_path = PROFESSION_INDEX_DIR / f"{profession}.json"
    if not index_path.exists():
        sys.exit(f"missing profession index: {index_path} — run match_profession first")
    index = json.loads(index_path.read_text())

    out_dir = TEXT_DIR / profession
    out_dir.mkdir(parents=True, exist_ok=True)

    # Convert profession_index → the per-state row shape pull_state expects:
    # one row per matched chapter URL, with chapter_label/chapter_slug/chapter_url.
    by_state: dict[str, list[dict]] = {}
    for state, payload in index.get("by_state", {}).items():
        if only_states and state not in only_states:
            continue
        for node in payload.get("matched", []):
            row = {
                "state": state,
                "chapter_url": node["url"],
                "chapter_label": node["label"],
                "chapter_slug": node.get("slug", ""),
            }
            # Pass-through for section-filter overrides
            if node.get("section_slug_pattern"):
                row["section_slug_pattern"] = node["section_slug_pattern"]
            if node.get("section_url_list"):
                row["section_url_list"] = node["section_url_list"]
            if node.get("pa_keep_sections"):
                row["pa_keep_sections"] = node["pa_keep_sections"]
            by_state.setdefault(state, []).append(row)

    log.info("profession=%s matched %d states from %s", profession, len(by_state), index_path.name)

    section_cap = args.limit_sections or None  # 0 → disabled
    capped_states: list[str] = []
    skipped = 0
    for state in sorted(by_state):
        try:
            corpus = pull_state(state, profession, by_state[state], section_cap)
            if section_cap and len(corpus.sections) >= section_cap:
                # Hit the runaway guard — almost always a whole-title over-match, not a
                # real chapter. Flag loudly so it's reviewed, not believed as coverage.
                log.warning("  ⚠ [%s] hit the %d-section cap — likely a whole-title over-match; "
                            "FLAGGED for review (re-map to the specific chapter / section-scope, "
                            "don't trust this corpus)", state, section_cap)
                corpus.section_cap_hit = section_cap
                capped_states.append(state)
        except Exception as e:
            log.exception("[%s] unhandled", state)
            corpus = StateCorpus(state=state, profession=profession, errors=[f"unhandled: {e}"])
        out_path = out_dir / f"{state}.json"
        new_d = asdict(corpus)

        # Overwrite-guard: don't let a worse pull clobber a healthy committed corpus.
        if out_path.exists() and not args.force:
            try:
                old_d = json.loads(out_path.read_text())
            except Exception:
                old_d = {}
            reason = _is_regression(new_d, old_d)
            if reason:
                log.warning("  [%s] SKIP overwrite: %s — keeping committed corpus (use --force to override)",
                            state, reason)
                skipped += 1
                continue

        out_path.write_text(json.dumps(new_d, indent=2))
        failed = sum(1 for s in corpus.sections if s.error)
        if failed:
            log.warning("  [%s] %d/%d sections FAILED to fetch — corpus is partial", state, failed, len(corpus.sections))
        log.info("  wrote %s (sections=%d, chars=%d)", out_path, len(corpus.sections), corpus.total_chars)

    # Cumulative summary: reflect every per-state corpus on disk, not just this
    # run's states (so a subset re-pull doesn't drop other states' rows).
    summary = []
    for path in record_files(out_dir):
        try:
            summary.append(_summary_row(path.stem, json.loads(path.read_text())))
        except Exception:
            continue
    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))
    if skipped:
        log.warning("done: %d states, %d overwrite(s) skipped (use --force to override)",
                    len(by_state), skipped)
    if capped_states:
        log.warning("%d state(s) hit the %d-section runaway cap — re-map to the specific chapter "
                    "(or section-scope) before trusting: %s",
                    len(capped_states), section_cap, ", ".join(capped_states))
    log.info("done: %d states", len(summary))
    record_run("pull_text", profession=profession, states=len(summary))


if __name__ == "__main__":
    main()
