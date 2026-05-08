"""Per-state structural crawl of the licensing parent URL.

Profession-agnostic: this builds a tree of (title → chapters) once per state
and caches it. match_profession.py then matches profession patterns against
chapter labels and lazily drills into matched chapters for sections.

By default, level-1 only: title → chapters. Pass `--depth 2` to also
enumerate sections under each chapter (slow — ~1 min per chapter-heavy state).

Inputs:  config/targets.csv (per-state licensing parent URLs)
Outputs: results/hierarchy/<STATE>.json

Output shape:
  {
    "state": "CT",
    "target_id": "justia_deep_ct",
    "target_url": "https://law.justia.com/codes/connecticut/title-20/",
    "strategy": "curl_cffi",
    "fetched_at": "2026-05-08T...",
    "extraction_level": "chapter" | "section_fallback" | "official_generic",
    "chapters": [
      { "label": "Chapter 375 - Podiatry", "url": "...", "slug": "chapter-375",
        "sections": [...]   # present iff --depth 2 was passed
      }, ...
    ],
    "stats": { "chapter_count": 87, "fetched_chapters": 0 }
  }

Usage:
  python -m pipeline.discover.build_hierarchy
  python -m pipeline.discover.build_hierarchy --states CT,NY --force --depth 2
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# Import siblings + paths
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _fetch import fetch_with, shutdown_pw  # noqa: E402
from _extract import extract_justia_chapters, extract_justia_sections, extract_official_chapters  # noqa: E402
from paths import HIERARCHY_DIR, CONFIG_DIR, LOGS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402


LOG_PATH = LOGS_DIR / "build_hierarchy.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
HIERARCHY_DIR.mkdir(parents=True, exist_ok=True)

PER_HOST_DELAY = 1.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("build_hierarchy")


# State-specific target IDs in targets.csv that don't follow justia_deep_<state>
SPECIAL_TARGET_IDS = {
    "NY": "justia_deep_ny_t8",
    "CA": "justia_deep_ca_bpc",
    "IL": "justia_deep_il_225",
    "MD": "justia_deep_md_health",
}

# Two states whose Justia URL 404s; fall back to the official site
OFFICIAL_FALLBACKS = {
    "MN": ("mn_revisor", "https://www.revisor.mn.gov/statutes/", "requests"),
    "PA": ("pa_legis_unc", "https://www.palegis.us/statutes/unconsolidated", "requests"),
}


def load_targets() -> dict[str, dict]:
    """id → row from config/targets.csv"""
    out: dict[str, dict] = {}
    targets_csv = CONFIG_DIR / "targets.csv"
    with targets_csv.open() as f:
        for row in csv.DictReader(f):
            out[row["id"]] = row
    return out


def pick_parent_url(state: str, targets: dict[str, dict]) -> tuple[str, str, str] | None:
    """(target_id, url, strategy) for the state's licensing parent URL."""
    if state in OFFICIAL_FALLBACKS:
        tid, url, strat = OFFICIAL_FALLBACKS[state]
        return tid, url, strat
    candidate_ids = [SPECIAL_TARGET_IDS.get(state), f"justia_deep_{state.lower()}"]
    for cid in candidate_ids:
        if cid and cid in targets:
            return cid, targets[cid]["url"], "curl_cffi"
    return None


def crawl_chapters(url: str, strategy: str) -> tuple[list[dict], str, str | None]:
    """Returns (chapters, extraction_level, error)."""
    status, html, err = fetch_with(strategy, url)
    if err or not html or (status and not 200 <= status < 300):
        return [], "", err or f"http {status}"
    if "justia.com" in url:
        chapters = extract_justia_chapters(html, url)
        if chapters:
            return chapters, "chapter", None
        # Fallback: parent IS the chapter, children are sections
        sections = extract_justia_sections(html, url)
        return sections, "section_fallback", None
    chapters = extract_official_chapters(html, url)
    return chapters, "official_generic", None


def crawl_sections_under(chapter_url: str) -> list[dict]:
    """Drill one level deeper for level-2 mode. Justia-only."""
    status, html, err = fetch_with("curl_cffi", chapter_url)
    if err or not html or (status and not 200 <= status < 300):
        return []
    return extract_justia_sections(html, chapter_url)


def build_state(state: str, targets: dict[str, dict], depth: int, force: bool) -> dict | None:
    out_path = HIERARCHY_DIR / f"{state}.json"
    if out_path.exists() and not force:
        log.info("[%s] cached, skip", state)
        return None

    pick = pick_parent_url(state, targets)
    if pick is None:
        log.warning("[%s] no target URL configured", state)
        record = {
            "state": state,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "error": "no target URL configured",
            "chapters": [],
        }
        out_path.write_text(json.dumps(record, indent=2))
        return record
    tid, url, strategy = pick

    log.info("[%s] %s (strategy=%s)", state, url, strategy)
    chapters, level, err = crawl_chapters(url, strategy)
    time.sleep(PER_HOST_DELAY)

    fetched_chapters = 0
    if depth >= 2 and chapters and "justia.com" in url:
        log.info("[%s] depth=2: drilling %d chapters", state, len(chapters))
        for c in chapters:
            sections = crawl_sections_under(c["url"])
            time.sleep(PER_HOST_DELAY)
            c["sections"] = sections
            fetched_chapters += 1

    record = {
        "state": state,
        "target_id": tid,
        "target_url": url,
        "strategy": strategy,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "extraction_level": level,
        "chapters": chapters,
        "stats": {"chapter_count": len(chapters), "fetched_chapters": fetched_chapters},
        "error": err,
    }
    out_path.write_text(json.dumps(record, indent=2))
    log.info("[%s] -> %d chapters (level=%s) saved %s", state, len(chapters), level, out_path.name)
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", default="", help="Comma-separated subset; empty = all")
    ap.add_argument("--depth", type=int, default=1, choices=[1, 2], help="1 = title→chapters; 2 = also chapter→sections")
    ap.add_argument("--force", action="store_true", help="Rebuild even if cached")
    args = ap.parse_args()

    only = {s.strip().upper() for s in args.states.split(",") if s.strip()}
    states = [s for s in ALL_STATES if not only or s in only]

    targets = load_targets()
    log.info("crawling %d states (depth=%d, force=%s)", len(states), args.depth, args.force)

    last_host: str | None = None
    for st in states:
        try:
            build_state(st, targets, args.depth, args.force)
        except Exception:
            log.exception("[%s] crashed", st)

    shutdown_pw()
    log.info("done")


if __name__ == "__main__":
    main()
