"""Enumerate profession chapters under each state's licensing parent title.

Inputs:
  - targets.csv (the deep-link Justia URLs for each state, plus a few official-site overrides)
  - probe_results.json (so we know which fetch strategy works for each state)

For each state:
  1. Pick the deep-link target (parent licensing title, e.g. "Title 34 - Professions").
  2. Fetch it using the strategy chosen by probe.py.
  3. Parse the page for chapter-level links (regulated professions).
  4. Record (chapter_url, chapter_label) tuples.

Outputs:
  results/profession_chapters.json — full per-state list of chapter links + labels
  results/profession_chapters.csv  — flat one-row-per-chapter
  results/enumerate_report.md      — per-state summary: count, sample chapters, anomalies

Re-runnable. Uses the probe's existing strategies (requests / curl_cffi / playwright)
so it inherits the same bot-mitigation behavior.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import time
import urllib.parse
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
PROBE_RESULTS = ROOT / "results" / "probe_results.json"
RESULTS_DIR = ROOT / "results"
SNAPSHOTS_DIR = RESULTS_DIR / "enum_snapshots"
LOG_PATH = ROOT / "logs" / "enumerate.log"
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

UA_BOT = "scrape-probe/1.0 (+research; contact: abigail.haddad@gmail.com)"
UA_BROWSER = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
TIMEOUT = 25
PER_HOST_DELAY = 1.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("enumerate")


# Per-state deep-link target preference. Preference order is:
#   1. justia_deep_<state>  (from targets.csv) — uniform Justia structure
#   2. official-site fallback for the 2 states whose Justia URL 404'd
OFFICIAL_FALLBACKS = {
    # state -> (id, url, strategy)
    "MN": ("mn_revisor", "https://www.revisor.mn.gov/statutes/", "requests"),
    "PA": ("pa_legis_unc", "https://www.palegis.us/statutes/unconsolidated", "requests"),
}

# US states only
ALL_STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA",
    "HI","ID","IL","IN","IA","KS","KY","LA","ME","MD",
    "MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
]


@dataclass
class StateEnum:
    state: str
    target_id: str
    target_url: str
    strategy: str
    fetch_status: int | None = None
    fetch_error: str | None = None
    chapter_count: int = 0
    chapters: list[dict] = field(default_factory=list)  # {url, label}
    error: str | None = None
    sample_labels: list[str] = field(default_factory=list)
    extraction_level: str = ""  # "chapter", "section_fallback", "official_generic"


def load_targets() -> dict[str, dict]:
    """id -> row from targets.csv"""
    out = {}
    with TARGETS_CSV.open() as f:
        for row in csv.DictReader(f):
            out[row["id"]] = row
    return out


def load_probe_strategy() -> dict[str, str]:
    """state -> recommended strategy from probe_results.json"""
    if not PROBE_RESULTS.exists():
        log.warning("probe_results.json not found; defaulting all states to curl_cffi")
        return {s: "curl_cffi" for s in ALL_STATES}
    data = json.loads(PROBE_RESULTS.read_text())
    # The probe does per-target classifications, not per-state recommendations.
    # We derive: prefer official official>justia path matching probe verdicts.
    # Simple rule: if any official target for that state classified as ok with `requests`, use requests; else curl_cffi.
    strategy_by_state: dict[str, str] = {}
    for r in data:
        st = r["state"]
        if st == "US":
            continue
        if st in strategy_by_state:
            continue
        # We only care about deep-link probes for chapter enumeration
        if r["id"].startswith("justia_deep_"):
            if r.get("recommended_strategy") in ("requests", "curl_cffi"):
                strategy_by_state[st] = r["recommended_strategy"]
    # Fill defaults
    for s in ALL_STATES:
        strategy_by_state.setdefault(s, "curl_cffi")
    return strategy_by_state


def pick_targets(targets: dict[str, dict], strategies: dict[str, str]) -> list[tuple[str, str, str, str]]:
    """Returns list of (state, target_id, url, strategy)."""
    out = []
    for st in ALL_STATES:
        if st in OFFICIAL_FALLBACKS:
            tid, url, strat = OFFICIAL_FALLBACKS[st]
            out.append((st, tid, url, strat))
            continue
        # Look up justia_deep_<lowercase state> in targets.csv
        candidate_ids = [
            f"justia_deep_{st.lower()}",
            "justia_deep_ny_t8" if st == "NY" else None,
        ]
        for cid in candidate_ids:
            if cid and cid in targets:
                row = targets[cid]
                strat = strategies.get(st, "curl_cffi")
                out.append((st, cid, row["url"], strat))
                break
        else:
            log.warning("No deep-link target found for state %s", st)
    return out


def fetch_with(strategy: str, url: str) -> tuple[int | None, str | None, str | None]:
    """Returns (status, html_text, error). Falls back to curl_cffi if the chosen
    strategy returns 4xx (handles Cloudflare on Justia even when probe.py guessed
    plain requests would work)."""
    def _try(strat):
        try:
            if strat == "requests":
                r = requests.get(url, headers={"User-Agent": UA_BROWSER}, timeout=TIMEOUT, allow_redirects=True)
                return r.status_code, r.text, None
            if strat == "curl_cffi":
                if not HAVE_CFFI:
                    return None, None, "curl_cffi not installed"
                r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT, allow_redirects=True)
                return r.status_code, r.text, None
            if strat == "playwright":
                return fetch_playwright(url)
            return None, None, f"unknown strategy: {strat}"
        except Exception as e:
            return None, None, f"{type(e).__name__}: {e}"

    status, html, err = _try(strategy)
    if status and 200 <= status < 300:
        return status, html, err
    # Fall back: requests → curl_cffi → playwright
    if strategy == "requests" and HAVE_CFFI:
        log.info("  fallback to curl_cffi (initial: status=%s err=%s)", status, err)
        s2, h2, e2 = _try("curl_cffi")
        if s2 and 200 <= s2 < 300:
            return s2, h2, e2
    if strategy in ("requests", "curl_cffi") and HAVE_PW:
        log.info("  fallback to playwright")
        s3, h3, e3 = _try("playwright")
        if s3 and 200 <= s3 < 300:
            return s3, h3, e3
    return status, html, err


_PW = {"playwright": None, "browser": None, "context": None}


def _ensure_pw():
    if _PW["context"] is None:
        _PW["playwright"] = sync_playwright().start()
        _PW["browser"] = _PW["playwright"].chromium.launch(headless=True)
        _PW["context"] = _PW["browser"].new_context(user_agent=UA_BROWSER)
    return _PW["context"]


def shutdown_pw():
    try:
        if _PW["context"]: _PW["context"].close()
        if _PW["browser"]: _PW["browser"].close()
        if _PW["playwright"]: _PW["playwright"].stop()
    except Exception:
        pass


def fetch_playwright(url: str) -> tuple[int | None, str | None, str | None]:
    if not HAVE_PW:
        return None, None, "playwright not installed"
    try:
        ctx = _ensure_pw()
        page = ctx.new_page()
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except Exception as e:
            page.close()
            return None, None, f"goto failed: {e}"
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass
        status = response.status if response else None
        html = page.content()
        page.close()
        return status, html, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


# Patterns that identify Justia chapter-level links, e.g.:
#   /codes/alabama/title-34/chapter-1/
#   /codes/california/code-bpc/division-2/
#   /codes/new-york/edn/title-8/article-141/
JUSTIA_CHAPTER_RE = re.compile(
    r"^/codes/[a-z\-]+/(?:\d{4}/)?[^/]+/(?:chapter|article|division|part|subtitle|subdivision)-[a-z0-9\-]+/?$",
    re.IGNORECASE,
)
# Some Justia states use named segments without "chapter-" prefix
JUSTIA_NUMBERED_RE = re.compile(
    r"^/codes/[a-z\-]+/(?:\d{4}/)?[^/]+/[a-z]+-[0-9a-z\-]+/?$",
    re.IGNORECASE,
)


CHAPTER_SEG = re.compile(
    r"^(chapter|article|division|subtitle|subdivision|part)[-_][0-9a-z][0-9a-z\-\.]*$",
    re.IGNORECASE,
)
SECTION_SEG = re.compile(
    # Common Justia section URL patterns:
    #   section-X, §X, s-X, statute-X, rs-X (LA), bare numeric prefix '38-101'
    r"^(section[-_]|§|s[-_]\d|statute[-_]|rs[-_]|\d+[a-z]?[-_]\d)",
    re.IGNORECASE,
)
YEAR_NAV_LABEL = re.compile(r"^\s*\d{4}\s+", re.IGNORECASE)  # "2024 Mass. Gen. Laws"
SIBLING_NAV_LABEL = re.compile(r"^\s*(previous|next)\s*$", re.IGNORECASE)
# Labels that look like a section: starts with §, "Section ", or "X-Y" / "X:Y" patterns
SECTION_LABEL = re.compile(r"^\s*(§|section\s|\d+[a-z]?[-:.]\d)", re.IGNORECASE)


def extract_justia_chapters(html: str, base_url: str) -> list[dict]:
    """Extract chapter-like links from a Justia parent-title page.

    Justia's URL structure varies wildly across states — some titles have a
    chapter level, some go straight to sections, some redirect through a year
    prefix. Strategy: collect candidates two ways, dedupe, and exclude known
    non-content link types (year navigation, sibling-title nav, sections).

      Path A (preferred): the path's final segment matches chapter|article|...
      Path B (fallback): the path is one level deeper than the parent title slug
                         and doesn't look like a section

    Both paths require the link's URL to share the same title slug as the parent
    URL, so we don't pick up chapters from neighboring titles.
    """
    soup = BeautifulSoup(html, "html.parser")
    parsed_base = urllib.parse.urlparse(base_url)
    base_segments = [s for s in parsed_base.path.split("/") if s]
    # The "title slug" is the most-specific non-year segment of the parent URL.
    # For /codes/alabama/title-34/ → title-34
    # For /codes/massachusetts/2024/part-i/title-xvi/chapter-112/ → chapter-112
    title_slug = None
    for seg in reversed(base_segments):
        if re.fullmatch(r"\d{4}", seg):
            continue
        title_slug = seg.lower()
        break

    chapters: list[dict] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        u = urllib.parse.urlparse(absolute)
        if u.netloc and u.netloc != parsed_base.netloc:
            continue
        path_segments = [s for s in u.path.split("/") if s]
        if not path_segments:
            continue
        last = path_segments[-1]
        # Reject obvious non-content
        if SECTION_SEG.match(last):
            continue
        label = (a.get_text(strip=True) or "").strip()
        if not label:
            continue
        if YEAR_NAV_LABEL.match(label) or SIBLING_NAV_LABEL.match(label):
            continue
        # Path must include the title slug (keeps us scoped to this title's children)
        lower_segs = [s.lower() for s in path_segments]
        if title_slug and title_slug not in lower_segs:
            continue
        # The link must be deeper than the title slug (i.e. a child)
        if title_slug:
            try:
                idx = lower_segs.index(title_slug)
            except ValueError:
                continue
            children = lower_segs[idx + 1:]
            if not children:
                # Same level as the title itself (year-versioned twin) → skip
                continue
            # Skip if any child segment looks like a section (URL or label-based)
            if any(SECTION_SEG.match(c) for c in children):
                continue
            if SECTION_LABEL.match(label):
                continue
            # Path A: chapter-pattern segment somewhere in the children
            if any(CHAPTER_SEG.match(c) for c in children):
                pass
            # Path B: exactly one child segment, not a section, not a chapter pattern
            #   — accept as "untyped subdivision" (covers states where subtitles/etc.
            #   are the natural unit)
            elif len(children) == 1:
                pass
            else:
                continue
        key = (u.path,)
        if key in seen:
            continue
        seen.add(key)
        chapters.append({"url": absolute, "label": label, "slug": last})
    return chapters


def extract_justia_sections(html: str, base_url: str) -> list[dict]:
    """Fallback for states where the parent URL IS the chapter and children are sections.

    Used when extract_justia_chapters returns 0 — typically because the user-supplied
    parent URL is already a chapter (e.g., MA chapter-112, KY chapter-311) so children
    are sections, or because the title has only sections directly under it (e.g., AZ).
    Extracts links one level deeper than the title slug whose final segment looks
    section-like (starts with 'section-', '§', 's-N', or bare numeric pattern).
    """
    soup = BeautifulSoup(html, "html.parser")
    parsed_base = urllib.parse.urlparse(base_url)
    base_segments = [s for s in parsed_base.path.split("/") if s]
    title_slug = None
    for seg in reversed(base_segments):
        if re.fullmatch(r"\d{4}", seg):
            continue
        title_slug = seg.lower()
        break

    sections: list[dict] = []
    seen: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        u = urllib.parse.urlparse(absolute)
        if u.netloc and u.netloc != parsed_base.netloc:
            continue
        path_segments = [s for s in u.path.split("/") if s]
        if not path_segments:
            continue
        last = path_segments[-1]
        label = (a.get_text(strip=True) or "").strip()
        if not label or YEAR_NAV_LABEL.match(label) or SIBLING_NAV_LABEL.match(label):
            continue
        # Must look like a section by URL, label, or both
        looks_like_section = bool(SECTION_SEG.match(last) or SECTION_LABEL.match(label))
        if not looks_like_section:
            continue
        # Path scoping: must include the title slug
        lower_segs = [s.lower() for s in path_segments]
        if title_slug and title_slug not in lower_segs:
            continue
        key = (u.path,)
        if key in seen:
            continue
        seen.add(key)
        sections.append({"url": absolute, "label": label, "slug": last})
    return sections


def extract_official_chapters(html: str, base_url: str) -> list[dict]:
    """Best-effort extraction for non-Justia parent-title pages.

    Strategy: collect all anchors whose URL contains a chapter-ish segment
    (chapter, title, article, section, statute) and that share a host with the base.
    """
    soup = BeautifulSoup(html, "html.parser")
    base = urllib.parse.urlparse(base_url)
    chapters: list[dict] = []
    seen: set[str] = set()
    pat = re.compile(r"chapter|title|article|statute|section|act", re.IGNORECASE)
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "javascript:")):
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        u = urllib.parse.urlparse(absolute)
        if u.netloc and u.netloc != base.netloc:
            continue
        if not pat.search(u.path):
            continue
        label = (a.get_text(strip=True) or "")[:200]
        if not label or len(label) < 3:
            continue
        key = absolute
        if key in seen:
            continue
        seen.add(key)
        chapters.append({"url": absolute, "label": label, "slug": u.path.rsplit("/", 1)[-1]})
    return chapters


def enumerate_state(state: str, tid: str, url: str, strategy: str) -> StateEnum:
    res = StateEnum(state=state, target_id=tid, target_url=url, strategy=strategy)
    log.info("[%s] strategy=%s url=%s", state, strategy, url)
    status, html, err = fetch_with(strategy, url)
    res.fetch_status = status
    if err:
        res.fetch_error = err
        res.error = err
        return res
    if status is None or not (200 <= status < 300):
        res.error = f"http {status}"
        return res
    if not html:
        res.error = "empty body"
        return res

    # Snapshot
    (SNAPSHOTS_DIR / f"{state}.html").write_text(html[:4_000_000])

    # Pick extractor by strategy/source
    if "justia.com" in url:
        chapters = extract_justia_chapters(html, url)
        # Fallback: if zero chapters, the parent URL probably IS the unit
        # (e.g., MA chapter-112, KY chapter-311). Extract sections instead.
        if len(chapters) == 0:
            chapters = extract_justia_sections(html, url)
            res.extraction_level = "section_fallback"
        else:
            res.extraction_level = "chapter"
    else:
        chapters = extract_official_chapters(html, url)
        res.extraction_level = "official_generic"
    res.chapters = chapters
    res.chapter_count = len(chapters)
    res.sample_labels = [c["label"] for c in chapters[:8]]
    log.info("  -> %d chapters", res.chapter_count)
    return res


def main() -> None:
    targets = load_targets()
    strategies = load_probe_strategy()
    plan = pick_targets(targets, strategies)
    log.info("Enumerating %d states", len(plan))

    results: list[StateEnum] = []
    last_host: str | None = None
    for st, tid, url, strat in plan:
        host = urllib.parse.urlparse(url).netloc
        if host == last_host:
            time.sleep(PER_HOST_DELAY)
        last_host = host
        try:
            r = enumerate_state(st, tid, url, strat)
        except Exception as e:
            log.exception("unexpected failure on %s", st)
            r = StateEnum(state=st, target_id=tid, target_url=url, strategy=strat, error=f"unhandled: {e}")
        results.append(r)

    shutdown_pw()

    # Persist
    out_json = RESULTS_DIR / "profession_chapters.json"
    out_json.write_text(json.dumps([asdict(r) for r in results], indent=2))
    log.info("wrote %s", out_json)

    out_csv = RESULTS_DIR / "profession_chapters.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["state", "target_id", "strategy", "chapter_url", "chapter_label", "chapter_slug"])
        w.writeheader()
        for r in results:
            for c in r.chapters:
                w.writerow({
                    "state": r.state, "target_id": r.target_id, "strategy": r.strategy,
                    "chapter_url": c["url"], "chapter_label": c["label"], "chapter_slug": c["slug"],
                })
    log.info("wrote %s", out_csv)

    write_report(results)


def write_report(results: list[StateEnum]) -> None:
    out_md = RESULTS_DIR / "enumerate_report.md"
    total_chapters = sum(r.chapter_count for r in results)
    failures = [r for r in results if r.error]
    lines = [
        "# Profession Chapter Enumeration",
        "",
        f"Across {len(results)} states, found **{total_chapters} chapter-level entries** under each state's primary licensing title.",
        "",
        "Each row is one state's count and a sample of chapter labels (first 8). Full details in `profession_chapters.csv` / `profession_chapters.json`.",
        "",
        "## Per-state summary",
        "",
        "| State | Chapters | Source | Strategy | Sample labels |",
        "|---|---:|---|---|---|",
    ]
    for r in sorted(results, key=lambda x: x.state):
        sample = "; ".join(r.sample_labels[:5]) if r.sample_labels else (r.error or "—")
        sample = sample.replace("|", "/")[:300]
        host = urllib.parse.urlparse(r.target_url).netloc
        lines.append(f"| {r.state} | {r.chapter_count} | {host} | {r.strategy} | {sample} |")
    lines.append("")

    if failures:
        lines.append("## Failures")
        lines.append("")
        for r in failures:
            lines.append(f"- **{r.state}** ({r.target_id}): {r.error}")
        lines.append("")

    # Suspiciously low counts (likely extractor missed)
    low = [r for r in results if not r.error and r.chapter_count < 5]
    if low:
        lines.append("## Suspiciously low chapter counts (extractor may need state-specific tweak)")
        lines.append("")
        for r in low:
            lines.append(f"- **{r.state}**: {r.chapter_count} chapters from {r.target_url}")
        lines.append("")

    out_md.write_text("\n".join(lines))
    log.info("wrote %s", out_md)


if __name__ == "__main__":
    main()
