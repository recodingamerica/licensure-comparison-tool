"""Pull text for the umbrella / cross-cutting chapters identified by
find_umbrella_chapters.py. Output: results/umbrella_text/<STATE>.json
with the same section-list shape as results/text/<profession>/<STATE>.json.

Once cached, extract_state can read this and include it as supplemental
context when extracting any profession in the state.

Usage:
  python -m pipeline.ingest.pull_umbrella_text --state TX
  python -m pipeline.ingest.pull_umbrella_text          # all states with umbrella files
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR, LOGS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402
from pipeline._fetch_config import PER_HOST_DELAY  # noqa: E402

# Reuse the existing pull infrastructure
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pull_text import (  # noqa: E402
    fetch, is_section_url, extract_section_text, collect_section_targets,
)

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
UMBRELLA_CHAPTERS_DIR = RESULTS_DIR / "umbrella_chapters"
LOG_PATH = LOGS_DIR / "pull_umbrella_text.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
UMBRELLA_TEXT_DIR.mkdir(parents=True, exist_ok=True)

# Cap per umbrella chapter — some states (IN) put thousands of leaf sections
# under one "General Provisions" chapter. We only need the topmost sections
# (definitions, board composition, fee rules) for context injection, not the
# entire administrative code.
MAX_SECTIONS_PER_CHAPTER = 50

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("pull_umbrella_text")


def pull_state_umbrella(state: str, force: bool) -> dict | None:
    umb_path = UMBRELLA_CHAPTERS_DIR / f"{state}.json"
    out_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    if not umb_path.exists():
        log.info("[%s] no umbrella_chapters file, skip", state)
        return None
    if out_path.exists() and not force:
        log.info("[%s] cached, skip", state)
        return json.loads(out_path.read_text())

    rec = json.loads(umb_path.read_text())
    chapters = rec.get("umbrella_chapters", [])
    if not chapters:
        log.info("[%s] no umbrella chapters declared", state)
        out_path.write_text(json.dumps({"state": state, "sections": []}, indent=2))
        return None

    all_sections = []
    for ch in chapters:
        url = ch["url"]
        label = ch.get("label", "")
        slug = ch.get("slug", "")
        log.info("[%s] umbrella chapter %s — %s", state, slug, label[:60])

        if is_section_url(url):
            section_targets = [{"url": url, "label": label, "slug": slug}]
        else:
            section_targets, err = collect_section_targets(url, label, slug, depth=0)
            if err:
                log.warning("  collect_section_targets error: %s", err)

        if len(section_targets) > MAX_SECTIONS_PER_CHAPTER:
            log.info("  capping %d -> %d sections per chapter (definitions / general provisions are typically at the top)",
                     len(section_targets), MAX_SECTIONS_PER_CHAPTER)
            section_targets = section_targets[:MAX_SECTIONS_PER_CHAPTER]
        log.info("  -> %d section targets", len(section_targets))
        for target in section_targets:
            sec_url = target["url"]
            status, html, err = fetch(sec_url)
            time.sleep(PER_HOST_DELAY)
            if err or not html:
                log.warning("    %s: %s", sec_url, err)
                continue
            text = extract_section_text(html)
            if not text:
                continue
            all_sections.append({
                "url": sec_url,
                "label": target.get("label", ""),
                "slug": target.get("slug", ""),
                "umbrella_chapter_slug": slug,
                "umbrella_chapter_label": label,
                "text": text,
                "text_len": len(text),
            })

    log.info("[%s] -> %d total umbrella sections", state, len(all_sections))
    record = {
        "state": state,
        "umbrella_chapter_count": len(chapters),
        "sections": all_sections,
    }
    out_path.write_text(json.dumps(record, indent=2))
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="")
    ap.add_argument("--states", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.state:
        targets = [args.state.upper()]
    elif args.states:
        targets = [s.strip().upper() for s in args.states.split(",") if s.strip()]
    else:
        targets = list(ALL_STATES)

    log.info("pulling umbrella text for %d states", len(targets))
    for st in targets:
        try:
            pull_state_umbrella(st, args.force)
        except Exception:
            log.exception("[%s] crashed", st)


if __name__ == "__main__":
    main()
