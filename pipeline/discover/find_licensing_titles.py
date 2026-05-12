"""Find every Justia title in a state that contains professional licensing
chapters, not just the primary one in state_structure.yaml.

Why: state_structure.yaml records ONE title URL per state — the one we built
for the health-professions seed (Utah Title 58 analog). But many professions
live in a different title (e.g. TX puts CPA in "Occupations Code" but
"Business & Commerce Code" might hold others; some states put financial
professions in a "Finance" or "Insurance" title; trades in a Construction
title). Picking one title misses every profession that lives elsewhere.

This script: fetches each state's Justia index, extracts the list of
top-level titles/codes, asks Sonnet (Pydantic-constrained Literal) which
ones contain professional licensing, caches the result. Re-running
build_hierarchy with these expanded title URLs gets the missing chapters.

One run covers every current and future profession in the state.

Usage:
  python -m pipeline.discover.find_licensing_titles --state TX
  python -m pipeline.discover.find_licensing_titles  # all states
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Literal as TLiteral

from pydantic import ValidationError, create_model

from pipeline._env import load_env  # noqa: E402
load_env()

import litellm  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import RESULTS_DIR, LOGS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402
from discover._fetch import fetch_with, shutdown_pw  # noqa: E402

LICENSING_TITLES_DIR = RESULTS_DIR / "licensing_titles"
LICENSING_TITLES_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOGS_DIR / "find_licensing_titles.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_RETRIES = 2
from pipeline._fetch_config import PER_HOST_DELAY  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("find_licensing_titles")


STATE_SLUG = {
    "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas",
    "CA": "california", "CO": "colorado", "CT": "connecticut", "DE": "delaware",
    "FL": "florida", "GA": "georgia", "HI": "hawaii", "ID": "idaho",
    "IL": "illinois", "IN": "indiana", "IA": "iowa", "KS": "kansas",
    "KY": "kentucky", "LA": "louisiana", "ME": "maine", "MD": "maryland",
    "MA": "massachusetts", "MI": "michigan", "MN": "minnesota", "MS": "mississippi",
    "MO": "missouri", "MT": "montana", "NE": "nebraska", "NV": "nevada",
    "NH": "new-hampshire", "NJ": "new-jersey", "NM": "new-mexico", "NY": "new-york",
    "NC": "north-carolina", "ND": "north-dakota", "OH": "ohio", "OK": "oklahoma",
    "OR": "oregon", "PA": "pennsylvania", "RI": "rhode-island", "SC": "south-carolina",
    "SD": "south-dakota", "TN": "tennessee", "TX": "texas", "UT": "utah",
    "VT": "vermont", "VA": "virginia", "WA": "washington", "WV": "west-virginia",
    "WI": "wisconsin", "WY": "wyoming",
}


_YEAR_LINK_RE = re.compile(r'href="(/codes/[a-z-]+/(\d{4})/?)"')
_TITLE_LINK_RE = re.compile(
    r'<a\s+[^>]*href="(/codes/[a-z-]+/[^"/]+/)"\s*>([^<]+)</a>',
    re.IGNORECASE,
)


def fetch_state_index(state: str) -> tuple[str | None, str | None]:
    """Return (final_url, html). Handles year-versioned roots by redirecting
    to the latest year's index."""
    slug = STATE_SLUG.get(state)
    if not slug:
        return None, None
    root = f"https://law.justia.com/codes/{slug}/"
    status, html, err = fetch_with("curl_cffi", root)
    if err or not html:
        log.warning("[%s] fetch %s failed: %s", state, root, err)
        return None, None

    # Year-versioned redirect
    year_links = sorted(set(int(y) for _, y in _YEAR_LINK_RE.findall(html)))
    # Find any title-shaped links on the bare root; if none, redirect to latest year
    titles = _extract_titles(html)
    if not titles and year_links:
        latest = max(year_links)
        url2 = f"{root}{latest}/"
        log.info("[%s] year-versioned root, redirecting to %s", state, url2)
        time.sleep(PER_HOST_DELAY)
        status, html, err = fetch_with("curl_cffi", url2)
        if err or not html:
            return None, None
        return url2, html
    return root, html


def _extract_titles(html: str) -> list[dict]:
    """Extract top-level title links from a state index HTML.

    Filters: only /codes/<state>/<slug>/ shape, where slug is non-numeric
    (year links excluded), and the visible text doesn't look like a year.
    """
    seen: dict[str, str] = {}
    for m in _TITLE_LINK_RE.finditer(html):
        href, text = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        # Path: /codes/<state>/<slug>/ → 3 parts after split
        parts = href.strip("/").split("/")
        if len(parts) != 3:
            continue
        slug = parts[2]
        # Skip year-stamped indexes
        if slug.isdigit():
            continue
        # Skip duplicates (links may repeat)
        if href in seen:
            continue
        # Skip year-like text
        if text.isdigit():
            continue
        seen[href] = text
    return [{"url": f"https://law.justia.com{href}", "label": label} for href, label in seen.items()]


SYSTEM_PROMPT = """\
You are deciding which of a state's statutory titles/codes contain
professional licensing law.

A "professional licensing" title is one that holds the licensure schemes,
scope of practice, and disciplinary frameworks for state-regulated
occupations — health professions (medicine, nursing, dentistry, podiatry,
etc.), trades (plumbing, electrical, contracting), finance/business
professions (CPA, real estate, insurance agents), legal (attorneys, court
reporters), beauty (cosmetology), and others.

Include a title if it contains licensing schemes for any of those.

EXCLUDE:
  - Pure regulatory codes that don't license individuals (Environmental
    Code, Tax Code, Health and Safety Code [unless it actually houses
    licensed-professional regulation], Insurance Code [unless it licenses
    agents — many states put agents in Occupations/Business titles
    instead]).
  - Substantive law codes (Family Code, Penal Code, Property Code, Civil
    Practice).
  - Government / administrative codes (Government Code, Election Code,
    Local Government Code) unless they explicitly house licensing.

When in doubt, INCLUDE — false positives are cheap (we just crawl an
extra title); false negatives mean missed coverage. Title labels like
"Occupations", "Business and Professions", "Professions and Occupations",
"Trades", "Professional Licensing", "Healing Arts", "Public Health" almost
always belong. "Education Code" often contains educator licensing.

Return JSON only.
"""


def classify_titles(state: str, titles: list[dict], model: str) -> list[str] | None:
    """Ask the LLM which title URLs contain professional licensing.
    Returns the selected list of URLs (subset of `titles`)."""
    if not titles:
        return []

    valid_urls = [t["url"] for t in titles]
    UrlLit = TLiteral[tuple(valid_urls)]  # type: ignore[valid-type]
    Result = create_model("LicensingTitleSelection", licensing_title_urls=(list[UrlLit], ...))

    title_block = "\n".join(f"- {t['url']}  →  {t['label']}" for t in titles)
    user = (
        f"State: {state}\n\n"
        f"All top-level titles/codes in this state:\n{title_block}\n\n"
        f"Return the subset of URLs that contain professional licensing law."
    )
    schema = Result.model_json_schema()
    system = (
        SYSTEM_PROMPT + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2)
    )

    from pipeline._llm import call_structured
    result = call_structured(
        model=model, system=system, user=user, schema_cls=Result,
        max_tokens=2000, max_retries=MAX_RETRIES, log_prefix=f"[{state}]", logger=log,
    )
    if result is None:
        return None
    return list(result.licensing_title_urls)  # type: ignore[attr-defined]


def find_for_state(state: str, model: str, force: bool) -> dict | None:
    out_path = LICENSING_TITLES_DIR / f"{state}.json"
    if out_path.exists() and not force:
        log.info("[%s] cached, skip", state)
        return json.loads(out_path.read_text())

    final_url, html = fetch_state_index(state)
    if not html:
        log.warning("[%s] no html; skipping", state)
        return None
    titles = _extract_titles(html)
    log.info("[%s] %d top-level titles at %s", state, len(titles), final_url)
    if not titles:
        return None

    # Flat-chapter states (NV, NC, IA, KS, NE, KY, WI) have many chapters at
    # the state index with no title layer. The multi-title concept doesn't
    # apply — all chapters are already reachable via the primary hierarchy
    # crawl. Skip the LLM call and record an empty selection.
    # Heuristics: (a) too many entries to be titles, OR (b) the majority of
    # entries' labels begin with "Chapter" (vs "Title"/"Code"/"Subtitle"/etc).
    n = len(titles)
    chapter_labeled = sum(1 for t in titles if re.match(r"^\s*(chapter|article)\s+[\dIVX]", t.get("label", ""), re.I))
    looks_flat = n > 60 or (n >= 5 and chapter_labeled >= n // 2)
    if looks_flat:
        # For flat-chapter states (IA, KS, NE, NC have target_url narrowed to
        # one chapter/title), record the state-index URL as a licensing
        # "title". expand_hierarchy will then crawl it and append every chapter
        # not already in the narrow hierarchy. States with already-broad targets
        # (KY/NV/WI) will dedupe to 0 new — harmless extra fetch.
        log.info("[%s] flat-chapter state (%d entries, %d chapter-labeled) — using state index as expansion source",
                 state, n, chapter_labeled)
        record = {
            "state": state,
            "index_url": final_url,
            "all_titles_count": n,
            "flat_state": True,
            "licensing_title_urls": [final_url],
        }
        out_path.write_text(json.dumps(record, indent=2))
        return record

    selected = classify_titles(state, titles, model)
    if selected is None:
        return None

    record = {
        "state": state,
        "index_url": final_url,
        "all_titles": titles,
        "licensing_title_urls": selected,
    }
    out_path.write_text(json.dumps(record, indent=2))
    log.info("[%s] -> %d licensing titles saved %s", state, len(selected), out_path.name)
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="", help="State code (e.g. TX); empty = all")
    ap.add_argument("--states", default="", help="Comma-separated list")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.state:
        targets = [args.state.upper()]
    elif args.states:
        targets = [s.strip().upper() for s in args.states.split(",") if s.strip()]
    else:
        targets = list(ALL_STATES)

    log.info("finding licensing titles for %d states (model=%s, force=%s)", len(targets), args.model, args.force)
    for st in targets:
        try:
            find_for_state(st, args.model, args.force)
            time.sleep(PER_HOST_DELAY)
        except Exception:
            log.exception("[%s] crashed", st)
    shutdown_pw()


if __name__ == "__main__":
    main()
