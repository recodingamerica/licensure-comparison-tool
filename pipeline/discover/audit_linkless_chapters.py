"""Audit Justia title-index pages for chapters listed WITHOUT a hyperlink.

Why: Justia sometimes renders a chapter as a plain-text <li> with no <a>
(found 2026-06-12: SC Title 40 "Chapter 20 - South Carolina Dietetics
Licensure Act"). build_hierarchy only collects anchors, so these chapters
silently never enter the hierarchy and label-match can't see them — even
though the chapter page itself exists at the year-versioned URL.

Scope: only title pages that host licensing-relevant chapters (>=2 chapters
in our hierarchy whose label matches a professions.yaml pattern), so we
fetch ~150 pages instead of ~1200.

Outputs:
  results/audit_linkless_chapters.json — all unlinked entries found
  results/audit_linkless_chapters.md   — human-readable report, profession-
                                         relevant entries first

Usage:
  python -m pipeline.discover.audit_linkless_chapters [--states SC,FL]
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import time
import urllib.parse
from collections import Counter, defaultdict

import yaml
from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

from pipeline.paths import HIERARCHY_DIR, CONFIG_DIR, RESULTS_DIR, LOGS_DIR
from pipeline._fetch_config import PER_HOST_DELAY
from pipeline.config.loaders import load_professions

LOG_PATH = LOGS_DIR / "audit_linkless_chapters.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("audit_linkless")

# A chapter-ish list item: "Chapter 20 - South Carolina Dietetics Licensure Act"
CHAPTERISH = re.compile(r"^(Chapter|Article|Part|Subtitle)\s+[\w.\-]+\s*[-–—]\s*\S", re.I)
NOISE = re.compile(r"\b(reserved|repealed|renumbered|transferred|omitted|expired)\b", re.I)


def profession_patterns() -> list[str]:
    cfg = load_professions()
    pats: set[str] = set()
    for k, v in cfg.items():
        if k.startswith("_") or not isinstance(v, dict):
            continue
        for p in v.get("patterns") or []:
            pats.add(p.lower())
    return sorted(pats)


def licensing_parent_pages(states: list[str] | None) -> dict[str, list[str]]:
    """Title-index URLs per state that host >=2 profession-pattern chapters."""
    pats = profession_patterns()
    hits: dict[str, Counter] = defaultdict(Counter)
    for f in sorted(HIERARCHY_DIR.glob("*.json")):
        st = f.stem
        if states and st not in states:
            continue
        for ch in json.loads(f.read_text()).get("chapters", []):
            u = ch.get("url", "")
            if "law.justia.com" not in u:
                continue
            path = urllib.parse.urlparse(u).path.rstrip("/")
            parent = "https://law.justia.com" + "/".join(path.split("/")[:-1]) + "/"
            if any(p in ch.get("label", "").lower() for p in pats):
                hits[st][parent] += 1
    return {st: sorted(p for p, c in cnt.items() if c >= 2) for st, cnt in hits.items() if any(c >= 2 for c in cnt.values())}


def unlinked_entries(html: str) -> list[str]:
    """Chapter-ish <li> items with no <a> anywhere inside them."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for li in soup.find_all("li"):
        if li.find("a"):
            continue
        text = " ".join(li.get_text(" ", strip=True).split())
        if text and CHAPTERISH.match(text):
            out.append(text)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", default="", help="Comma-separated subset; empty = all")
    args = ap.parse_args()
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()] or None

    pages = licensing_parent_pages(states)
    total = sum(len(v) for v in pages.values())
    log.info("auditing %d title pages across %d states", total, len(pages))

    pats = profession_patterns()
    findings: list[dict] = []
    fetched = errors = 0
    for st in sorted(pages):
        for url in pages[st]:
            time.sleep(PER_HOST_DELAY)
            try:
                r = cffi_requests.get(url, impersonate="chrome", timeout=30, allow_redirects=True)
            except Exception as e:
                log.warning("[%s] %s -> %s", st, url, e)
                errors += 1
                continue
            fetched += 1
            if r.status_code != 200:
                log.warning("[%s] %s -> HTTP %s", st, url, r.status_code)
                errors += 1
                continue
            for label in unlinked_entries(r.text):
                findings.append({
                    "state": st,
                    "title_page": url,
                    "label": label,
                    "noise": bool(NOISE.search(label)),
                    "profession_relevant": any(p in label.lower() for p in pats),
                })
        log.info("[%s] done (%d pages)", st, len(pages[st]))

    out_json = RESULTS_DIR / "audit_linkless_chapters.json"
    out_json.write_text(json.dumps({"fetched": fetched, "errors": errors, "findings": findings}, indent=2))

    relevant = [f for f in findings if f["profession_relevant"] and not f["noise"]]
    substantive = [f for f in findings if not f["profession_relevant"] and not f["noise"]]
    noise = [f for f in findings if f["noise"]]

    lines = [
        "# Link-less chapter audit (Justia title pages)",
        "",
        f"Fetched {fetched} title pages ({errors} errors). "
        f"Found {len(findings)} unlinked chapter-ish entries: "
        f"**{len(relevant)} profession-relevant**, {len(substantive)} other substantive, {len(noise)} reserved/repealed noise.",
        "",
        "## Profession-relevant (likely silent coverage gaps)",
        "",
    ]
    for f in relevant:
        lines.append(f"- **{f['state']}** — {f['label']}  \n  {f['title_page']}")
    lines += ["", "## Other substantive unlinked entries", ""]
    for f in substantive:
        lines.append(f"- {f['state']} — {f['label']}  \n  {f['title_page']}")
    lines += ["", f"## Reserved/repealed/renumbered ({len(noise)} entries — expected to be unlinked)", ""]
    for f in noise:
        lines.append(f"- {f['state']} — {f['label']}")
    out_md = RESULTS_DIR / "audit_linkless_chapters.md"
    out_md.write_text("\n".join(lines))
    log.info("wrote %s and %s", out_json, out_md)
    log.info("profession-relevant unlinked entries: %d", len(relevant))
    for f in relevant:
        log.info("  [%s] %s", f["state"], f["label"])


if __name__ == "__main__":
    main()
