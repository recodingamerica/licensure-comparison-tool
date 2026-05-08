"""Bulk-fetch section bodies for one state's hierarchy. Caches first-N chars
of each section's text to disk so map_state_sections_v2 can give Sonnet
enough context to disambiguate generic-labeled sections.

Output: pipeline/results/section_bodies/<STATE>.json
  { state, fetched_at, bodies: { slug: { url, label, excerpt } } }

Politeness: serialized fetches with PER_HOST_DELAY (1.2s default). For
2000-section states this means ~40 minutes. Use --max-sections to cap
during testing; production runs are one-time per state.

Usage:
  python -m pipeline.discover.fetch_section_bodies --state LA
  python -m pipeline.discover.fetch_section_bodies --state LA --max-sections 200
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _fetch import fetch_with  # noqa: E402
from paths import HIERARCHY_DIR, RESULTS_DIR, LOGS_DIR  # noqa: E402

# Reuse the section-text extractor from pull_text rather than duplicating selectors
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ingest"))
from pull_text import extract_section_text  # noqa: E402

BODIES_DIR = RESULTS_DIR / "section_bodies"
BODIES_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = LOGS_DIR / "fetch_section_bodies.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

PER_HOST_DELAY = 1.2
EXCERPT_CHARS = 300

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("fetch_section_bodies")


def fetch_all(state: str, max_sections: int | None) -> dict:
    h_path = HIERARCHY_DIR / f"{state}.json"
    if not h_path.exists():
        sys.exit(f"missing {h_path}")
    h = json.loads(h_path.read_text())
    sections = h.get("chapters", [])
    if max_sections:
        sections = sections[:max_sections]
    log.info("[%s] fetching %d section bodies (PER_HOST_DELAY=%ss)", state, len(sections), PER_HOST_DELAY)

    out_path = BODIES_DIR / f"{state}.json"
    cached = {}
    if out_path.exists():
        cached = json.loads(out_path.read_text()).get("bodies", {})
        log.info("[%s] %d already cached", state, len(cached))

    bodies = dict(cached)
    new_count = 0
    for i, sec in enumerate(sections):
        slug = sec["slug"]
        if slug in bodies:
            continue
        url = sec["url"]
        status, html, err = fetch_with("curl_cffi", url)
        time.sleep(PER_HOST_DELAY)
        if err or not html or (status and not 200 <= status < 300):
            bodies[slug] = {"url": url, "label": sec.get("label", ""), "excerpt": "", "error": err or f"http {status}"}
        else:
            text = extract_section_text(html)
            bodies[slug] = {"url": url, "label": sec.get("label", ""), "excerpt": text[:EXCERPT_CHARS]}
        new_count += 1
        if new_count % 50 == 0:
            log.info("[%s] %d new (%d total)", state, new_count, len(bodies))
            # Checkpoint every 50
            out_path.write_text(json.dumps({
                "state": state,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "bodies": bodies,
            }, indent=2))

    out_path.write_text(json.dumps({
        "state": state,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "bodies": bodies,
    }, indent=2))
    log.info("[%s] wrote %d bodies → %s", state, len(bodies), out_path.name)
    return bodies


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--max-sections", type=int, default=None, help="cap sections for testing")
    args = ap.parse_args()
    fetch_all(args.state.upper(), args.max_sections)


if __name__ == "__main__":
    main()
