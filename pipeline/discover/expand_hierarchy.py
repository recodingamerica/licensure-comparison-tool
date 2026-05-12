"""Expand each state's hierarchy to include chapters from every licensing
title the state has, not just the seed title from state_structure.yaml.

Reads results/licensing_titles/<STATE>.json (produced by find_licensing_titles.py)
and crawls each listed title that isn't already represented in the existing
hierarchy. Appends the new chapters to results/hierarchy/<STATE>.json with
provenance: each chapter carries `source_title_url` so downstream consumers
(match_profession, chapter mapper) know where it came from.

Idempotent: if a chapter slug already exists in the hierarchy, skip.

Usage:
  python -m pipeline.discover.expand_hierarchy --state TX
  python -m pipeline.discover.expand_hierarchy           # all states with a licensing_titles file
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# load env via shared helper (must come before any LLM-using import; not used here but kept consistent)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _env import load_env  # noqa: E402
load_env()

# Project imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _fetch import fetch_with, shutdown_pw  # noqa: E402
from _extract import extract_justia_chapters  # noqa: E402
from build_hierarchy import crawl_chapters, crawl_subtitles  # noqa: E402  reuse to handle year-versioned + section_fallback
from paths import HIERARCHY_DIR, RESULTS_DIR, LOGS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402

import re  # noqa: E402

# Subtitle wrappers between title and chapter on Justia. Match by SLUG only —
# label-based matching false-positives on real chapters ("Chapter 161 - ...").
_SUBTITLE_SLUG_RE = re.compile(r'^(title|subtitle|division|part|volume|subdivision)[-_]', re.IGNORECASE)


def _looks_like_subtitle_layer(entries: list[dict]) -> bool:
    """Heuristic: are the returned 'chapters' actually subtitles needing a drill?

    Slug-based only: real chapters always slug as `chapter-N` or `article-N`,
    while subtitle wrappers slug as `title-N`, `subtitle-a`, `division-2`, etc.
    Majority rule (at least half must match) to ignore the occasional stray.
    """
    if not entries:
        return False
    matches = sum(1 for c in entries if _SUBTITLE_SLUG_RE.match(c.get("slug", "")))
    return matches >= max(2, len(entries) // 2)


def _drill_one(parent: dict) -> list[dict]:
    """Fetch a subtitle URL and return its chapter children. If the page
    structure has sections (not chapters) underneath — e.g. MD
    business-occupations/title-2/subtitle-1 is a leaf containing statute
    sections — returns []. The caller should KEEP the parent as a chapter
    in that case rather than discarding it.
    """
    from _fetch import fetch_with  # avoid circular at import time
    from _extract import extract_justia_chapters
    import time
    status, html, err = fetch_with("curl_cffi", parent["url"])
    time.sleep(PER_HOST_DELAY)
    if err or not html or (status and not 200 <= status < 300):
        return []
    children = extract_justia_chapters(html, parent["url"])
    for c in children:
        c["parent_slug"] = parent["slug"]
    return children


def _drill_recursively(entries: list[dict], depth: int, max_depth: int = 3) -> list[dict]:
    """Drill subtitle wrappers into their children. Keep parent entries too —
    their labels are often the load-bearing ones for match_profession
    ("Title 2 - Accountants" is the CPA chapter on MD, even though it has
    7 subtitles underneath).

    Each level:
      - chapters (non-subtitle slugs): pass through, never drilled
      - subtitle parents: KEPT (in case label matters) AND drilled
      - children from drilling: recurse, since they may themselves be subtitles

    Only the new generation recurses, so parents aren't re-drilled.
    """
    if depth >= max_depth or not entries:
        return entries
    chapters = [e for e in entries if not _SUBTITLE_SLUG_RE.match(e.get("slug", ""))]
    parents = [e for e in entries if _SUBTITLE_SLUG_RE.match(e.get("slug", ""))]
    if not parents:
        return entries
    log.info("    %sdrilling %d subtitle entries (level %d), keeping %d chapters",
             "  " * depth, len(parents), depth + 1, len(chapters))
    next_gen: list[dict] = []
    for p in parents:
        children = _drill_one(p)
        if children:
            next_gen.extend(children)
    drilled = _drill_recursively(next_gen, depth + 1, max_depth)
    return chapters + parents + drilled


def fetch_title_chapters(title_url: str) -> tuple[list[dict], str, str | None]:
    """Crawl a title URL into chapters. Drills repeatedly through subtitle/
    division layers (e.g. TX Occupations Code → Title 1..15 → Subtitle A/B →
    chapters) up to 3 levels deep.
    """
    chapters, level, err = crawl_chapters(title_url, "curl_cffi")
    if err or not chapters:
        return chapters, level, err
    if any(_SUBTITLE_SLUG_RE.match(c.get("slug", "")) for c in chapters):
        chapters = _drill_recursively(chapters, 0)
        level = "chapter (drilled)"
    return chapters, level, None

LICENSING_TITLES_DIR = RESULTS_DIR / "licensing_titles"
LOG_PATH = LOGS_DIR / "expand_hierarchy.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
from pipeline._fetch_config import PER_HOST_DELAY  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("expand_hierarchy")


def expand_state(state: str, force: bool) -> dict | None:
    h_path = HIERARCHY_DIR / f"{state}.json"
    lt_path = LICENSING_TITLES_DIR / f"{state}.json"
    if not lt_path.exists():
        log.info("[%s] no licensing_titles file, skip", state)
        return None
    if not h_path.exists():
        log.warning("[%s] no hierarchy file — run build_hierarchy first", state)
        return None

    hierarchy = json.loads(h_path.read_text())
    lt = json.loads(lt_path.read_text())
    primary_url = (hierarchy.get("target_url") or "").rstrip("/") + "/"
    chapters = hierarchy.get("chapters") or []

    # Dedupe on (source_title_url, slug) — slug alone collides because different
    # codes use the same names (MD health-occupations Title 2 = Audiologists vs
    # business-occupations Title 2 = Accountants, both slug `title-2`). Including
    # the URL keeps them distinct.
    def _dedup_key(slug: str, source_url: str) -> tuple[str, str]:
        return (source_url, slug)

    existing_keys = {
        _dedup_key(c.get("slug", ""), c.get("source_title_url", primary_url))
        for c in chapters if c.get("slug")
    }

    additional_urls = [u for u in lt.get("licensing_title_urls", []) if u.rstrip("/") + "/" != primary_url]

    already_expanded = {c.get("source_title_url") for c in chapters if c.get("source_title_url")}

    appended = 0
    new_title_count = 0
    for title_url in additional_urls:
        if title_url in already_expanded and not force:
            log.info("[%s] %s already in hierarchy (skip)", state, title_url)
            continue
        log.info("[%s] fetching title %s", state, title_url)
        new_chapters, level, err = fetch_title_chapters(title_url)
        time.sleep(PER_HOST_DELAY)
        if err:
            log.warning("[%s] %s: %s", state, title_url, err)
            continue
        added_here = 0
        for c in new_chapters:
            slug = c.get("slug") or ""
            key = _dedup_key(slug, title_url)
            if key in existing_keys:
                continue
            existing_keys.add(key)
            c = dict(c)
            c["source_title_url"] = title_url
            chapters.append(c)
            added_here += 1
        appended += added_here
        new_title_count += 1
        log.info("[%s] %s: +%d new chapters (level=%s)", state, title_url, added_here, level)

    if appended == 0:
        log.info("[%s] no new chapters appended", state)
        return hierarchy

    # Annotate primary chapters with source_title_url so all chapters are tagged
    for c in chapters:
        c.setdefault("source_title_url", primary_url)

    hierarchy["chapters"] = chapters
    hierarchy["stats"] = hierarchy.get("stats") or {}
    hierarchy["stats"]["chapter_count"] = len(chapters)
    hierarchy["stats"]["expanded_titles"] = new_title_count
    hierarchy["expanded_at"] = datetime.now(timezone.utc).isoformat()
    h_path.write_text(json.dumps(hierarchy, indent=2))
    log.info("[%s] -> +%d chapters from %d additional titles (total %d)", state, appended, new_title_count, len(chapters))
    return hierarchy


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="")
    ap.add_argument("--states", default="")
    ap.add_argument("--force", action="store_true", help="re-crawl titles even if marked expanded")
    args = ap.parse_args()

    if args.state:
        targets = [args.state.upper()]
    elif args.states:
        targets = [s.strip().upper() for s in args.states.split(",") if s.strip()]
    else:
        targets = list(ALL_STATES)

    log.info("expanding hierarchy for %d states", len(targets))
    for st in targets:
        try:
            expand_state(st, args.force)
        except Exception:
            log.exception("[%s] crashed", st)
    shutdown_pw()


if __name__ == "__main__":
    main()
