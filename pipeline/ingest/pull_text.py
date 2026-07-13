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
from pipeline.config.loaders import load_limits

LOG_PATH = LOGS_DIR / "pull_text.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

TIMEOUT = 25
# Per-section pause. Overridable via PULL_HOST_DELAY (seconds) — set it high for
# a polite Justia crawl (e.g. 7) so we're not
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
    # Set when the (profession, state) is REGULATED with a KNOWN citation but the
    # text isn't pullable from Justia (our only scraper) — e.g. a brand-new
    # session law Justia hasn't ingested, or a real act missing from Justia's
    # index. This is a THIRD state distinct from "empty pull" (a bug) and
    # "verified absence" (not regulated): the law exists, we have the cite, the
    # text just lives on the state's own legislature site. Carries {reason,
    # citation, official_url} so downstream tooling can show it correctly instead
    # of treating an empty corpus as a gap. Sourced from a mapping_overrides add
    # node's `source_unavailable:` key; no fetch is attempted.
    source_unavailable: dict | None = None


# --- Cloudflare handling (Justia, which CF-blocks our IPs) ---
# Justia sits behind a Cloudflare JS challenge that curl_cffi can't solve from
# datacenter IPs. It is cleared HEADLESS by Scrapling's StealthySession (camoufox
# + solve_cloudflare) — the DEFAULT and now ONLY Justia fetcher (see fetch()).
# The old hand-started-debug-Chrome-over-CDP fallback was retired 2026-07-13:
# Scrapling reproduced its corpora without a manual Chrome or a hand-solve, so the
# CDP machinery (locks, relaunch dance, wedge handling) was removed rather than
# kept as a break-glass path that itself required manual setup. `git log` for the
# CDP code (it was removed entirely; no CDP tool remains in the pipeline).
# Only hosts in _UNBLOCK_HOSTS need Scrapling — Pennsylvania's legacy static
# endpoint (the only other active source) fetches direct, free, via curl_cffi.
# (A parallel official-source-per-state effort — Utah XML, SD/NY APIs, NV/CT/WA/
# VA/ME/ID/MO/MD/RI/VT/MT/AZ/FL HTML — was removed 2026-07-08: unverified and
# unused. See git history if a source needs official-fetch again.)
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


_SCRAPLING_SESSION = None


def _get_scrapling_session():
    """Lazily open ONE headless StealthySession (camoufox stealth browser) and reuse
    it for every fetch. Unlike the CDP path it needs no hand-started Chrome and no
    manual Cloudflare solve, and it does NOT soft-block on rapid back-to-back fetches
    (validated 2026-07-10: 5/5 Justia fetches, no delay, no challenge — where CDP
    soft-blocked all-but-first). Closed at process exit."""
    global _SCRAPLING_SESSION
    if _SCRAPLING_SESSION is None:
        import atexit
        from scrapling.fetchers import StealthySession
        sess = StealthySession(headless=True, solve_cloudflare=True)
        sess.__enter__()
        atexit.register(lambda: sess.__exit__(None, None, None))
        _SCRAPLING_SESSION = sess
    return _SCRAPLING_SESSION


def _reset_scrapling_session() -> None:
    """Tear the StealthySession down so the next fetch opens a fresh camoufox — used
    between retries when the session may be wedged (an empty/challenge response)."""
    global _SCRAPLING_SESSION
    if _SCRAPLING_SESSION is not None:
        try:
            _SCRAPLING_SESSION.__exit__(None, None, None)
        except Exception:
            pass
        _SCRAPLING_SESSION = None


# One-off Scrapling flakiness (an intermittent empty/challenge response) silently
# drops a section -> a "short pull". Retry such responses, recreating the session on
# later attempts in case it's wedged. We only retry on a CLEARLY-bad body (exception,
# non-2xx, empty, or a challenge page) — never on a small-but-real page — so a genuine
# short section is returned as-is, not looped over.
_SCRAPLING_RETRIES = int(os.environ.get("SCRAPLING_RETRIES", "2"))
_CHALLENGE_SIGS = ("just a moment", "checking your browser", "attention required",
                   "cf-challenge", "cloudflare to restrict")


def fetch_via_scrapling(url: str) -> tuple[int | None, str | None, str | None]:
    """Fetch a Cloudflare-protected Justia URL headless via Scrapling's StealthyFetcher.
    Returns (status, html, err) — the shape every downstream step (leaf detection,
    section crawl, year-version dedup) expects, so all of that is unchanged. Retries a
    clearly-bad response (empty/challenge/error) up to _SCRAPLING_RETRIES times."""
    last: tuple[int | None, str | None, str | None] = (None, None, "no attempt")
    for attempt in range(_SCRAPLING_RETRIES + 1):
        try:
            sess = _get_scrapling_session()
            try:
                page = sess.fetch(url, network_idle=True)
            except TypeError:
                page = sess.fetch(url)
            html = page.html_content if hasattr(page, "html_content") else str(page)
            status = getattr(page, "status", 200) or 200
            challenged = any(s in (html or "").lower() for s in _CHALLENGE_SIGS)
            if html and status and 200 <= status < 300 and not challenged:
                if attempt:
                    log.info("  ▶ scrapling recovered %s on retry %d", url, attempt)
                return status, html, None
            last = (status, html, f"bad response (status={status}, chars={len(html or '')}, "
                                  f"challenge={challenged})")
        except Exception as e:
            last = (None, None, f"{type(e).__name__}: {e}")
        if attempt < _SCRAPLING_RETRIES:
            log.warning("  ⟳ scrapling %s — %s; recreating session, retry %d/%d",
                        url, last[2], attempt + 1, _SCRAPLING_RETRIES)
            _reset_scrapling_session()
            time.sleep(2)
    return last


def _scrapling_available() -> bool:
    try:
        import scrapling.fetchers  # noqa: F401
        return True
    except Exception:
        return False


def _is_justia(url: str) -> bool:
    """A host that needs Scrapling's Cloudflare solver (Justia). Everything else
    (PA's legacy static endpoint) fetches direct via curl_cffi."""
    host = urllib.parse.urlparse(url).netloc.lower()
    return any(h in host for h in _UNBLOCK_HOSTS)


def _normalize_url(url: str) -> str:
    """section_match writes root-relative Justia paths ('/codes/...') into the
    profession_index; make them absolute so host-based routing (scrapling/browser)
    and the fetch itself work instead of silently returning an empty page."""
    if url.startswith("/codes/"):
        return "https://law.justia.com" + url
    return url


def fetch(url: str) -> tuple[int | None, str | None, str | None]:
    url = _normalize_url(url)
    if _is_justia(url):
        # Scrapling is the sole Justia fetcher (the CDP/debug-Chrome fallback was
        # retired 2026-07-13). Fail loud rather than fall through to curl_cffi,
        # which just returns a Cloudflare challenge page that would be silently
        # mis-parsed as an empty corpus.
        if not _scrapling_available():
            raise RuntimeError(
                "Justia is fetched via Scrapling's headless Cloudflare solver, which "
                "is not installed. Run: pip install 'scrapling[fetchers]' && scrapling "
                "install. (The old hand-started-debug-Chrome CDP fallback was retired "
                "2026-07-13; see git history if you need it.)"
            )
        return fetch_via_scrapling(url)
    # Non-Justia hosts (PA's legacy static endpoint, etc.): direct curl_cffi.
    try:
        r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT,
                              allow_redirects=True)
        return r.status_code, r.text, None
    except Exception as e:
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
    base_has_year = any(YEAR_SEG.match(s) for s in base_segments)

    sections: list[dict] = []
    intermediates: list[dict] = []
    year_self: list[tuple] = []  # (year, url, label, slug) — year snapshots of THIS page
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
            year_self.append((max(int(y) for y in link_years), absolute,
                              a.get_text(strip=True) or "", path_segments[-1]))
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
    sections = _dedupe_year_versions(sections)
    intermediates = _dedupe_year_versions(intermediates)
    if not sections and not intermediates and year_self and not base_has_year:
        # Year-SELECTOR page: it links only to year snapshots of itself, with no
        # section list. Happens when a fetcher lands on the *undated* page for a
        # state that publishes only year-stamped content (e.g. IL acts — the section
        # list lives at /<state>/2024/... not the undated URL). The normal dedup
        # above drops these self-year links as duplicates, which would strand the
        # sections; here, with nothing else found, we drill the latest-year copy
        # instead. That copy is year-stamped, so on re-entry `base_has_year` is True
        # and this branch cannot fire again — no year->year loop, and it only ever
        # triggers on a genuinely empty undated page, never on one that has content.
        year_self.sort(reverse=True)
        yr, u, lab, sl = year_self[0]
        intermediates = [{"url": u, "label": lab or f"{yr} edition", "slug": sl}]
    return sections, intermediates


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
    # Justia's soft-404: a URL that 200s but has no #codes-content/primary-content
    # div (wrong slug, un-codified section, page removed) falls through the
    # extractor's selector cascade to generic site furniture -- a fixed-length
    # (1144-char) "Justia Legal Resources / Find a Lawyer" nav blob, not an
    # error page or a Cloudflare challenge, so neither prior marker caught it.
    # Found 2026-07-09 after it silently passed as "real content" (>500 chars)
    # in 53 already-committed files across many professions/states predating
    # this session -- see docs/runbooks/cdp_repull_lessons_2026-07-09.md.
    "justia legal resources\nfind a lawyer",
    # Second Justia soft-404 variant: a plain "not found" page rather than the
    # nav-blob one above (found 2026-07-09, community_health_worker/CA).
    "page not found\nthe requested page could not be found",
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


def _pull_pa_act(corpus: StateCorpus, row: dict, pa_urls: list[str], limit_sections: int | None) -> None:
    """Handle Pennsylvania acts: fetch each whole-act URL once and split locally
    into per-section records (sections share the act URL, so the caller's
    seen_section_urls dedup would wrongly collapse them — PA is handled here in
    full). A profession may span multiple acts (nursing = Professional Nursing
    Law + Practical Nurse Law)."""
    for pa_url in pa_urls:
        status, html, err = fetch(pa_url)
        polite_sleep()
        if err or not html or (status and not 200 <= status < 300):
            corpus.errors.append(f"pa_legis fetch {pa_url}: {err or f'http {status}'}")
            continue
        pa_sections = parse_pa_act(html, pa_url)
        if not pa_sections:
            corpus.errors.append(f"pa_legis parse {pa_url}: 0 sections (markers not found)")
        # pa_keep_sections scopes an embedded profession to its own sections
        # within a shared act (e.g. dietetics inside the Nursing Law). Citation
        # is "§ <num>"; keep only the listed numbers.
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


def _resolve_section_targets(
    corpus: StateCorpus, row: dict, url: str, profession: str, state: str,
) -> list[dict] | None:
    """Resolve the section targets for one chapter row. Returns the target list,
    or None to signal the caller should skip this row (fetch error / over-broad).

    Modes: explicit section_url_list; section_slug_pattern (fetch chapter +
    slug-filter its children); a URL that is itself a section; else collect the
    chapter's leaf sections (guarded against over-broad picks)."""
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
            return None
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
            return None

    return section_targets


def _add_inline_section(corpus: StateCorpus, sec: dict, limit_sections: int | None) -> None:
    """Add a section whose text was already captured inline by
    collect_section_targets (IL-style). If it's an ILCS/ND act blob, split it
    into per-section records so IL/ND get section-level citations + browse."""
    text = sec["_inline_text"]
    bad = bad_section_text(text)
    if bad:
        # Same soft-404/block-page check as the main fetch path — this branch
        # used to skip it entirely, letting Justia's fixed 1144-char "Justia
        # Legal Resources / Find a Lawyer" nav blob (a wrong/uncodified URL that
        # 200s with no real content div) through as real statute text. Found
        # 2026-07-09 after 53 files had it silently committed. See
        # docs/runbooks/cdp_repull_lessons_2026-07-09.md.
        corpus.errors.append(f"section {sec['url']}: {bad}")
        corpus.sections.append(Section(
            url=sec["url"], label=sec["label"],
            citation=short_citation(sec["label"]),
            text=text, text_len=len(text), error=bad,
        ))
        return
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
        return
    corpus.sections.append(Section(
        url=sec["url"], label=sec["label"],
        citation=short_citation(sec["label"]),
        text=text, text_len=len(text),
    ))
    corpus.total_chars += len(text)


def _fetch_and_add_section(corpus: StateCorpus, sec: dict) -> None:
    """Fetch one section URL and append the record (or an error stub)."""
    status, html, err = fetch(sec["url"])
    polite_sleep()
    if err or not html or (status and not 200 <= status < 300):
        # Aggregate into corpus.errors too — otherwise a state with per-section
        # failures looks healthy at the top level and downstream stages extract
        # from a silently partial corpus (bit us 2026-06-12: 5 of 9 MI dietetics
        # sections timed out and nothing flagged it).
        corpus.errors.append(f"section fetch {sec['url']}: {err or f'http {status}'}")
        corpus.sections.append(Section(
            url=sec["url"], label=sec["label"],
            citation=short_citation(sec["label"]),
            text="", error=err or f"http {status}",
        ))
        return
    text = extract_section_text(html)
    bad = bad_section_text(text)
    if bad:
        # 200 OK but no real statute text (empty extraction or a block page).
        # Flag it so the resumable grind re-pulls rather than silently shipping a
        # partial/corrupt corpus. Keep the text for inspection.
        corpus.errors.append(f"section {sec['url']}: {bad}")
        corpus.sections.append(Section(
            url=sec["url"], label=sec["label"],
            citation=short_citation(sec["label"]),
            text=text, text_len=len(text), error=bad,
        ))
        return
    corpus.sections.append(Section(
        url=sec["url"], label=sec["label"],
        citation=short_citation(sec["label"]),
        text=text, text_len=len(text),
    ))
    corpus.total_chars += len(text)


def pull_state(state: str, profession: str, rows: list[dict], limit_sections: int | None) -> StateCorpus:
    corpus = StateCorpus(state=state, profession=profession)
    seen_section_urls: set[str] = set()

    log.info("[%s] %d matching chapter rows", state, len(rows))
    for row in rows:
        url = row["chapter_url"]
        corpus.chapter_urls.append(url)

        # Pennsylvania: each URL is a whole act, handled entirely by _pull_pa_act.
        # A profession may span more than one act; list extras in section_url_list.
        pa_urls = list(dict.fromkeys(
            u for u in [url, *(row.get("section_url_list") or [])] if is_pa_legis_url(u)
        ))
        if pa_urls:
            _pull_pa_act(corpus, row, pa_urls, limit_sections)
            continue

        section_targets = _resolve_section_targets(corpus, row, url, profession, state)
        if section_targets is None:
            continue

        for sec in section_targets:
            if sec["url"] in seen_section_urls:
                continue
            seen_section_urls.add(sec["url"])
            if limit_sections and len(corpus.sections) >= limit_sections:
                break
            if "_inline_text" in sec:
                _add_inline_section(corpus, sec, limit_sections)
            else:
                _fetch_and_add_section(corpus, sec)

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
            if node.get("source_unavailable"):
                row["source_unavailable"] = node["source_unavailable"]
            by_state.setdefault(state, []).append(row)

    log.info("profession=%s matched %d states from %s", profession, len(by_state), index_path.name)

    section_cap = args.limit_sections or None  # 0 → disabled
    capped_states: list[str] = []
    skipped = 0
    for state in sorted(by_state):
        rows = by_state[state]
        # Regulated-but-not-on-Justia: every mapped node is flagged
        # source_unavailable → don't attempt a doomed fetch. Write a corpus that
        # records the citation + reason + official URL so it reads as
        # "source unavailable," not an empty/broken pull. (If only SOME nodes
        # carry the flag, fall through and pull the rest normally.)
        su_nodes = [r["source_unavailable"] for r in rows if r.get("source_unavailable")]
        if su_nodes and len(su_nodes) == len(rows):
            su = su_nodes[0]
            log.info("  [%s] source_unavailable (not on Justia) — recording, no fetch: %s",
                     state, su.get("reason", ""))
            corpus = StateCorpus(
                state=state, profession=profession,
                chapter_urls=[r["chapter_url"] for r in rows],
                source_unavailable=su,
            )
            out_path = out_dir / f"{state}.json"
            out_path.write_text(json.dumps(asdict(corpus), indent=2))
            continue
        try:
            corpus = pull_state(state, profession, rows, section_cap)
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
