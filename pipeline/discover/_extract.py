"""Link extractors for Justia and generic official-site index pages.

Extractor selection: callers check the URL host and pick the matching
extractor. extract_justia_chapters tries chapter-level links first; if it
finds none, callers should fall back to extract_justia_sections.
"""

from __future__ import annotations

import re
import urllib.parse

from bs4 import BeautifulSoup


# A path's last segment looks like a Justia section
SECTION_SEG = re.compile(
    r"^(section[-_]|§|s[-_]\d|statute[-_]|rs[-_]|\d+[a-z]?[-_:.]\d)",
    re.IGNORECASE,
)
# Intermediate path segments (subchapter, etc.) we may want to drill into
INTERMEDIATE_SEG = re.compile(
    r"^(subchapter|subpart|part|division|subdivision|chapter|subtitle|article)[-_][0-9a-z]",
    re.IGNORECASE,
)

JUSTIA_CHAPTER_RE = re.compile(
    r"^/codes/[a-z\-]+/(?:\d{4}/)?[^/]+/(?:chapter|article|division|part|subtitle|subdivision)-[a-z0-9\-]+/?$",
    re.IGNORECASE,
)

CHAPTER_SEG = re.compile(
    r"^(chapter|article|division|subtitle|subdivision|part)[-_][0-9a-z][0-9a-z\-\.]*$",
    re.IGNORECASE,
)
YEAR_NAV_LABEL = re.compile(r"^\s*\d{4}\s+", re.IGNORECASE)
SIBLING_NAV_LABEL = re.compile(r"^\s*(previous|next)\s*$", re.IGNORECASE)
SECTION_LABEL = re.compile(r"^\s*(§|section\s|\d+[a-z]?[-:.]\d)", re.IGNORECASE)


def extract_justia_chapters(html: str, base_url: str) -> list[dict]:
    """Chapter-level child links under a Justia title page."""
    soup = BeautifulSoup(html, "html.parser")
    parsed_base = urllib.parse.urlparse(base_url)
    base_segments = [s for s in parsed_base.path.split("/") if s]
    title_slug = None
    for seg in reversed(base_segments):
        if re.fullmatch(r"\d{4}", seg):
            continue
        title_slug = seg.lower()
        break

    chapters: list[dict] = []
    seen: set[tuple] = set()
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
        if SECTION_SEG.match(last):
            continue
        label = (a.get_text(strip=True) or "").strip()
        if not label:
            continue
        if YEAR_NAV_LABEL.match(label) or SIBLING_NAV_LABEL.match(label):
            continue
        lower_segs = [s.lower() for s in path_segments]
        if title_slug and title_slug not in lower_segs:
            continue
        if title_slug:
            try:
                idx = lower_segs.index(title_slug)
            except ValueError:
                continue
            children = lower_segs[idx + 1:]
            if not children:
                continue
            if any(SECTION_SEG.match(c) for c in children):
                continue
            if SECTION_LABEL.match(label):
                continue
            if any(CHAPTER_SEG.match(c) for c in children):
                pass
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
    """Section-level child links under a Justia chapter page (or where the
    parent URL IS already a chapter)."""
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
    seen: set[tuple] = set()
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
        looks_like_section = bool(SECTION_SEG.match(last) or SECTION_LABEL.match(label))
        if not looks_like_section:
            continue
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
    """Best-effort extraction for non-Justia parent-title pages."""
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
        if absolute in seen:
            continue
        seen.add(absolute)
        chapters.append({"url": absolute, "label": label, "slug": u.path.rsplit("/", 1)[-1]})
    return chapters
