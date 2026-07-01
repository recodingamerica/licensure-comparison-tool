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

# A generically-named GROUPING that hides subtype professions one level deeper: FL
# "Part VI - Insurance Adjusters" holds §626.854 "Public adjuster"; "…Agents" hold
# producer subtypes; "General Provisions" parts hold the shared umbrella sections.
# Only nodes BELOW a container recurse on this (a top-level chapter needs _CONTAINER),
# so depth-2 is targeted at these groupings — not a blanket expand-everything.
_SUBGROUP = re.compile(
    r"adjusters?|agents?|brokers?|producers?|representatives?|"
    r"general provisions|licensing procedures?", re.I)


def _expandable(node: dict, max_depth: int) -> bool:
    depth = node.get("depth", 0)  # original chapters carry no depth → level 0
    lab, url = node.get("label") or "", node.get("url") or ""
    if depth >= max_depth or not url.startswith("http") or "law.justia.com" not in url:
        return False
    # level-0 chapters expand on the broad container regex; deeper nodes only if they
    # are a generic grouping (else every leaf section would trigger a wasted fetch).
    return bool(_CONTAINER.search(lab) or (depth >= 1 and _SUBGROUP.search(lab)))


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
                # absolutize — Justia hrefs are relative ("/codes/..."); a relative
                # URL breaks both _expandable (needs http) and a later fetch of this
                # node, which is why depth-2 never fired on the parts.
                out.append({"label": lab[:140], "url": up.urljoin(url, href)})
    return out[:5000]  # was 300 — get the full article/section list, don't truncate


def expand_state(state: str, force: bool, max_depth: int = 2) -> int:
    """BFS depth-expansion. Seeds every expandable, not-yet-expanded node (so a resume
    picks up grouping parts a prior level-1 run added), fetches its children, and
    queues any child that is itself a container/grouping — up to max_depth."""
    from collections import deque
    fp = HIER_DIR / f"{state}.json"
    if not fp.exists():
        print(f"  {state}: no hierarchy"); return 0
    d = json.loads(fp.read_text())
    chapters = d.get("chapters", []) or []
    existing_urls = {c.get("url") for c in chapters}
    expanded = {c.get("parent_chapter_url") for c in chapters if c.get("parent_chapter_url")}
    queue = deque(c for c in chapters
                  if _expandable(c, max_depth) and (force or c.get("url") not in expanded))
    queued = {c.get("url") for c in queue}
    added = 0
    while queue:
        c = queue.popleft()
        url = c.get("url")
        if url in expanded and not force:
            continue
        kids = container_children(url)
        new = [k for k in kids if k["url"] not in existing_urls]
        for k in new:
            k["parent_chapter_url"] = url
            k["source"] = "container_expand"
            k["depth"] = c.get("depth", 0) + 1
            chapters.append(k)
            existing_urls.add(k["url"])
            if _expandable(k, max_depth) and k["url"] not in queued:
                queue.append(k); queued.add(k["url"])
        expanded.add(url)
        added += len(new)
        print(f"  {state}: [d{c.get('depth', 0)+1}] {c.get('label','')[:40]} → +{len(new)}")
    if added:
        d["chapters"] = chapters
        fp.write_text(json.dumps(d, indent=1, ensure_ascii=False))
    return added


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--max-depth", type=int, default=2,
                    help="how deep to recurse: 1 = chapters→parts only; 2 (default) = also "
                         "expand generic grouping parts (Insurance Adjusters, …Agents) to sections")
    args = ap.parse_args()
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()] or ALL_STATES
    total = 0
    for st in states:
        n = expand_state(st, args.force, args.max_depth)
        total += n
        if n:
            print(f"{st}: +{n} article entries")
    print(f"\nexpand_containers: +{total} entries across {len(states)} states")


if __name__ == "__main__":
    main()
