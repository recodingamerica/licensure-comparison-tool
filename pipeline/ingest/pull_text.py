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
import re
import time
import urllib.parse
from dataclasses import asdict, dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests  # type: ignore

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import TEXT_DIR, LOGS_DIR, PROFESSION_INDEX_DIR  # noqa: E402

LOG_PATH = LOGS_DIR / "pull_text.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

TIMEOUT = 25
PER_HOST_DELAY = 1.2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("pull_text")


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


def fetch(url: str) -> tuple[int | None, str | None, str | None]:
    try:
        r = cffi_requests.get(url, impersonate="chrome", timeout=TIMEOUT, allow_redirects=True)
        return r.status_code, r.text, None
    except Exception as e:
        return None, None, f"{type(e).__name__}: {e}"


def is_section_url(url: str) -> bool:
    last = [s for s in urllib.parse.urlparse(url).path.split("/") if s][-1]
    return bool(SECTION_SEG.match(last))


def extract_child_links(html: str, base_url: str) -> tuple[list[dict], list[dict]]:
    """Find child links under a chapter page.

    Returns (sections, intermediates). Sections are leaf statute URLs;
    intermediates (subchapter, subpart, ...) need another drill level.
    """
    soup = BeautifulSoup(html, "html.parser")
    parsed = urllib.parse.urlparse(base_url)
    base_segments = [s for s in parsed.path.split("/") if s]
    title_slug = base_segments[-1].lower() if base_segments else None

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
    return sections, intermediates


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


def collect_section_targets(url: str, label: str, slug: str, depth: int, max_depth: int = 2) -> tuple[list[dict], str | None]:
    """Walk a chapter/subchapter URL down to leaf section URLs.

    Returns (section_targets, error). Side-effect: sleeps PER_HOST_DELAY between
    fetches. If the URL itself contains substantial text and no children, treats
    the URL as a single leaf section (handles IL-style pages where the entire
    act lives at the chapter URL).
    """
    status, html, err = fetch(url)
    time.sleep(PER_HOST_DELAY)
    if err or not html or (status and not 200 <= status < 300):
        return [], f"fetch {url}: {err or status}"

    sections, intermediates = extract_child_links(html, url)
    if sections:
        return sections, None
    # No leaf sections — try drilling intermediates (subchapter-*, etc.) up to depth
    if intermediates and depth < max_depth:
        all_secs: list[dict] = []
        for inter in intermediates:
            secs, ierr = collect_section_targets(inter["url"], inter["label"], inter["slug"], depth + 1, max_depth)
            if ierr:
                log.info("    intermediate err: %s", ierr)
            all_secs.extend(secs)
        if all_secs:
            return all_secs, None
    # No children at all — the URL itself may be the leaf (IL-style)
    text = extract_section_text(html)
    if len(text) > 500:
        return [{"url": url, "label": label, "slug": slug, "_inline_text": text}], None
    return [], None


def pull_state(state: str, profession: str, rows: list[dict], limit_sections: int | None) -> StateCorpus:
    corpus = StateCorpus(state=state, profession=profession)
    seen_section_urls: set[str] = set()

    log.info("[%s] %d matching chapter rows", state, len(rows))
    for row in rows:
        url = row["chapter_url"]
        corpus.chapter_urls.append(url)

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
            time.sleep(PER_HOST_DELAY)
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

        for sec in section_targets:
            if sec["url"] in seen_section_urls:
                continue
            seen_section_urls.add(sec["url"])
            if limit_sections and len(corpus.sections) >= limit_sections:
                break

            # Inline text already captured by collect_section_targets (IL-style)
            if "_inline_text" in sec:
                text = sec["_inline_text"]
                corpus.sections.append(Section(
                    url=sec["url"], label=sec["label"],
                    citation=short_citation(sec["label"]),
                    text=text, text_len=len(text),
                ))
                corpus.total_chars += len(text)
                continue

            status, html, err = fetch(sec["url"])
            time.sleep(PER_HOST_DELAY)
            if err or not html or (status and not 200 <= status < 300):
                corpus.sections.append(Section(
                    url=sec["url"], label=sec["label"],
                    citation=short_citation(sec["label"]),
                    text="", error=err or f"http {status}",
                ))
                continue
            text = extract_section_text(html)
            corpus.sections.append(Section(
                url=sec["url"], label=sec["label"],
                citation=short_citation(sec["label"]),
                text=text, text_len=len(text),
            ))
            corpus.total_chars += len(text)

    return corpus


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True, help="Profession name from professions.yaml (e.g. 'podiatry')")
    ap.add_argument("--states", default="", help="Comma-separated subset of states; empty = all matching")
    ap.add_argument("--limit-sections", type=int, default=None, help="Cap sections per state (debug)")
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
            by_state.setdefault(state, []).append(row)

    log.info("profession=%s matched %d states from %s", profession, len(by_state), index_path.name)

    summary = []
    for state in sorted(by_state):
        try:
            corpus = pull_state(state, profession, by_state[state], args.limit_sections)
        except Exception as e:
            log.exception("[%s] unhandled", state)
            corpus = StateCorpus(state=state, profession=profession, errors=[f"unhandled: {e}"])
        out_path = out_dir / f"{state}.json"
        out_path.write_text(json.dumps(asdict(corpus), indent=2))
        summary.append({
            "state": state,
            "sections": len(corpus.sections),
            "ok_sections": sum(1 for s in corpus.sections if not s.error),
            "total_chars": corpus.total_chars,
            "errors": len(corpus.errors),
        })
        log.info("  wrote %s (sections=%d, chars=%d)", out_path, len(corpus.sections), corpus.total_chars)

    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))
    log.info("done: %d states", len(summary))


if __name__ == "__main__":
    main()
