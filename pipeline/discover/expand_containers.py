"""Structure discovery — DEPTH expansion.

`build_hierarchy`/`expand_hierarchy` give each state's TOP-LEVEL chapters (breadth).
But profession licensing is often an ARTICLE inside a broad "umbrella" chapter
(NM ch 60 -> Article 13 Construction Industries; MI ch 339 Occupational Code ->
its occupation articles) whose children aren't in the hierarchy. The LLM mapper
can't see those, so it can only flag "umbrella" and guess.

This step fetches the children of container-ish chapters and appends them to
results/hierarchy/<STATE>.json (provenance: parent_chapter_url), so the mapper
sees the real article list. It's the "discover structure first, in order" crawl:
run it across states, THEN map, THEN pull text for the chapters that map.

Justia-bound: shares the CDP Chrome via the flock; run with the text-grind paused.
Idempotent: skips containers whose children are already present.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.expand_containers --states NM,MI   # validate
  pipeline/.venv/bin/python -m pipeline.discover.expand_containers                  # all states
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse as up
from pathlib import Path

from bs4 import BeautifulSoup

from pipeline._env import load_env
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import HIERARCHY_DIR as HIER_DIR  # noqa: E402
from ingest import pull_text as pt  # noqa: E402

ALL_STATES = ("AK AL AR AZ CA CO CT DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI "
              "MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT "
              "VA VT WA WI WV WY").split()

# Top-level chapters that commonly CONTAIN many professions as sub-articles.
# Container-ish = a broad chapter/title whose CHILDREN (articles/sections) hold the
# actual professions. Broadened beyond the occupational-code umbrellas to also reach
# where section-nested professions + shared umbrella provisions live: the Insurance
# title (public adjuster, producer, navigator, bail bond), Health/Healing-arts titles,
# and the general-provisions / administrative-procedure / uniform-licensing umbrellas
# (e.g. NM 61-1, cited by 39 professions). Generous by design — "pull everything that
# might relate to ANY profession, then map it with match_sections".
_CONTAINER = re.compile(
    r"occupational code|professions? and occupations?|business (and professions?|"
    r"regulation|licenses?)|professional and occupational|construction industries?|"
    r"\bcontractors?\b|miscellaneous .*(profession|occupation|business)|"
    r"regulation of .*(profession|occupation)|"
    r"\binsurance\b|health occupations?|healing arts|health.related|"
    r"general provisions|administrative procedure|uniform .*(licens|regulat)|"
    r"boards? and commissions?|department of (commerce|insurance|health|licens)",
    re.I)
_NOISE = re.compile(r"repealed", re.I)


def container_children(url: str) -> list[dict]:
    status, html, _ = pt.fetch(url)
    if not html:
        return []
    base = up.urlparse(url).path.rstrip("/")
    soup = BeautifulSoup(html, "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        path = up.urlparse(href).path
        if base in href and path.rstrip("/") != base:  # a child, one level deeper
            lab = " ".join(a.get_text(" ", strip=True).split())
            if lab and len(lab) > 4 and href not in seen and not _NOISE.search(lab):
                seen.add(href)
                out.append({"label": lab[:140], "url": href})
    return out[:5000]  # was 300 — get the full article/section list, don't truncate


def expand_state(state: str, force: bool) -> int:
    fp = HIER_DIR / f"{state}.json"
    if not fp.exists():
        print(f"  {state}: no hierarchy"); return 0
    d = json.loads(fp.read_text())
    chapters = d.get("chapters", []) or []
    existing_urls = {c.get("url") for c in chapters}
    # already-expanded parents (so re-runs skip)
    expanded = {c.get("parent_chapter_url") for c in chapters if c.get("parent_chapter_url")}
    containers = [c for c in chapters
                  if _CONTAINER.search(c.get("label") or "")
                  and (c.get("url") or "").startswith("http")
                  and "law.justia.com" in (c.get("url") or "")
                  and (force or c.get("url") not in expanded)]
    added = 0
    for c in containers:
        kids = container_children(c["url"])
        new = [k for k in kids if k["url"] not in existing_urls]
        for k in new:
            k["parent_chapter_url"] = c["url"]
            k["source"] = "container_expand"
            chapters.append(k)
            existing_urls.add(k["url"])
        added += len(new)
        print(f"  {state}: {c.get('label','')[:42]} → +{len(new)} articles")
    if added:
        d["chapters"] = chapters
        fp.write_text(json.dumps(d, indent=1, ensure_ascii=False))
    return added


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()] or ALL_STATES
    total = 0
    for st in states:
        n = expand_state(st, args.force)
        total += n
        if n:
            print(f"{st}: +{n} article entries")
    print(f"\nexpand_containers: +{total} entries across {len(states)} states")


if __name__ == "__main__":
    main()
