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


# --- Illinois (Justia serves a whole ILCS act on one page) ---
# Like PA, IL acts arrive as ONE inline blob rather than per-section URLs, but the
# text carries an ILCS citation marker at the head of every section
# ("(225 ILCS 80/4.5)"). Split on those so IL gets section-level citations and a
# navigable browse view instead of one ~80k-char blob (issue #6). Reusable as a
# local transform on already-committed IL corpora — no re-fetch needed.
_IL_ILCS_MARKER = re.compile(r"\((\d+\s+ILCS\s+\d+/[0-9A-Za-z.\-]+)\)")


def looks_like_il_ilcs(text: str) -> bool:
    return len(_IL_ILCS_MARKER.findall(text)) >= 3


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
            # Cross-page year duplicates can survive per-page dedup (e.g. a year
            # snapshot reached via one intermediate + the unversioned copy via
            # another). Collapse them once the whole walk is assembled.
            return _dedupe_year_versions(all_secs), None
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
                time.sleep(PER_HOST_DELAY)
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

            # Inline text already captured by collect_section_targets (IL-style).
            # If it's an ILCS act blob, split it into per-section records so IL
            # gets section-level citations + browse instead of one blob (#6).
            if "_inline_text" in sec:
                text = sec["_inline_text"]
                il_sections = split_il_inline(text, sec["url"]) if looks_like_il_ilcs(text) else []
                if il_sections:
                    for s in il_sections:
                        if limit_sections and len(corpus.sections) >= limit_sections:
                            break
                        corpus.sections.append(s)
                        corpus.total_chars += s.text_len
                    log.info("  il_ilcs split %s -> %d sections", sec["url"], len(il_sections))
                    continue
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
            if node.get("pa_keep_sections"):
                row["pa_keep_sections"] = node["pa_keep_sections"]
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
        failed = sum(1 for s in corpus.sections if s.error)
        if failed:
            log.warning("  [%s] %d/%d sections FAILED to fetch — corpus is partial", state, failed, len(corpus.sections))
        log.info("  wrote %s (sections=%d, chars=%d)", out_path, len(corpus.sections), corpus.total_chars)

    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2))
    log.info("done: %d states", len(summary))


if __name__ == "__main__":
    main()
