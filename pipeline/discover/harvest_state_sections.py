"""Scrape chapter section URLs from revisor.mn.gov and legislature.mi.gov.

MN and MI hierarchies as built by build_hierarchy.py don't expose useful
chapter contents (MN root returns nav-only HTML; MI root returns mostly
repealed Acts on Justia). For these states the existing pattern is to
hand-curate `section_url_list` overrides in state_structure.yaml, as
already done for MN podiatry (27 URLs) and MI podiatry (15 URLs).

This script automates the hand-curation: given a (state, chapter-or-part)
target, it fetches the chapter index page from the official source and
extracts the section URLs. Output is printed as a yaml snippet ready to
paste into state_structure.yaml under the relevant profession.

Usage:
  python -m pipeline.discover.harvest_state_sections MN 147 --profession medicine
  python -m pipeline.discover.harvest_state_sections MI 170 --profession medicine
  python -m pipeline.discover.harvest_state_sections MN --all-known

The --all-known mode runs a built-in mapping of profession → chapter/Part
for both states, covering the 6 currently-extracted professions plus the
broader taxonomy where the mapping is unambiguous.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import curl_cffi.requests as crq  # noqa: E402

# --- Known chapter mappings for MN and MI ---
# These are documented one-line mappings from canonical profession id → state-
# specific chapter (MN) or Part (MI). The mappings are derived from each
# state's published licensing-statute structure and are point-in-time facts
# (renumberings are rare but possible). Profession IDs match
# pipeline/config/professions.yaml.

MN_CHAPTERS: dict[str, dict] = {
    # Whole-chapter professions: one chapter, one profession
    "medicine":           {"chapter": "147",  "label": "MN Statutes Ch 147 — Medical Practice"},
    "dentistry":          {"chapter": "150A", "label": "MN Statutes Ch 150A — Dentistry"},
    "podiatry":           {"chapter": "153",  "label": "MN Statutes Ch 153 — Podiatry"},
    "public_accountancy": {"chapter": "326A", "label": "MN Statutes Ch 326A — Accountancy"},
    "physician_assistant":{"chapter": "147A", "label": "MN Statutes Ch 147A — Physician Assistants"},
    "chiropractic":       {"chapter": "148",  "section_prefix": "148.0", "label": "MN Statutes Ch 148 §§148.01-.108 — Chiropractic"},
    # Within-Ch-148 sub-ranges (148 is shared)
    "nursing":            {"chapter": "148",  "section_prefix_set": {"148.171", "148.172", "148.173", "148.174", "148.175", "148.176", "148.177", "148.178", "148.179", "148.18", "148.181", "148.183", "148.185", "148.19", "148.191", "148.20", "148.21", "148.211", "148.212", "148.214", "148.215", "148.22", "148.231", "148.233", "148.234", "148.235", "148.241", "148.243", "148.25", "148.251", "148.26", "148.261", "148.262", "148.263", "148.264", "148.27", "148.28", "148.281", "148.282", "148.283", "148.284", "148.285"}, "label": "MN Statutes Ch 148 §§148.171-.285 — Nursing"},
    "optometry":          {"chapter": "148",  "section_prefix_set": {"148.52", "148.521", "148.53", "148.54", "148.55", "148.56", "148.57", "148.571", "148.575", "148.58", "148.59", "148.595", "148.596", "148.597", "148.598", "148.599", "148.60", "148.61", "148.62", "148.624", "148.625", "148.626", "148.65", "148.66", "148.67", "148.68"}, "label": "MN Statutes Ch 148 §§148.52-.68 — Optometry"},
}

MI_PARTS: dict[str, dict] = {
    # MI Public Health Code (Act 368 of 1978, Article 15 = Occupations) — Part per profession.
    # Section addressing uses MCL chapter 333 as the alias.
    "medicine":           {"act": "368", "year": "1978", "article": "15", "part": "170", "mcl": "333", "label": "MI PHC Part 170 — Medicine"},
    "dentistry":          {"act": "368", "year": "1978", "article": "15", "part": "166", "mcl": "333", "label": "MI PHC Part 166 — Dentistry"},
    "nursing":            {"act": "368", "year": "1978", "article": "15", "part": "172", "mcl": "333", "label": "MI PHC Part 172 — Nursing"},
    "optometry":          {"act": "368", "year": "1978", "article": "15", "part": "174", "mcl": "333", "label": "MI PHC Part 174 — Optometry"},
    "podiatry":           {"act": "368", "year": "1978", "article": "15", "part": "180", "mcl": "333", "label": "MI PHC Part 180 — Podiatric Medicine and Surgery"},
    # CPA lives outside the Public Health Code, in MI Occupational Code (Act 299 of 1980).
    # MCL chapter alias is 339; Article 7 covers Accountancy.
    # MI Occupational Code Accountancy lives at the Article level (no Part below).
    "public_accountancy": {"act": "299", "year": "1980", "article": "7",  "part": None,  "mcl": "339", "label": "MI Occupational Code Article 7 — Accountancy"},
}


def fetch(url: str) -> str:
    """Fetch a URL with curl_cffi (same client used by Justia ingest)."""
    resp = crq.get(url, impersonate="chrome120", timeout=30)
    resp.raise_for_status()
    return resp.text


def harvest_mn_chapter(chapter: str) -> list[str]:
    """Return the list of section URLs in an MN chapter.

    revisor.mn.gov/statutes/cite/<chapter> shows the chapter's table of
    contents with one anchor per section. Section URLs follow the same
    cite/<chapter>.<section> pattern.
    """
    base = f"https://www.revisor.mn.gov/statutes/cite/{chapter}"
    html = fetch(base)
    # Section anchors look like: href="/statutes/cite/147.01"
    pat = re.compile(rf'href="(/statutes/cite/{re.escape(chapter)}\.[\w-]+)"')
    found = sorted(set(pat.findall(html)))
    return [urljoin("https://www.revisor.mn.gov", p) for p in found]


def harvest_mi_part(act_num: str, year: str, article: str, part: str | None, mcl_chapter: str) -> list[str]:
    """Return section URLs for one Part (or Article, if part is None) of an MI Act.

    The MI Legislature site exposes index pages as
    `Laws/MCL?objectName=mcl-<ACT>-<YEAR>-<ARTICLE>[-<PART>]`:
      - With Part: e.g. `mcl-368-1978-15-180` (PHC Article 15 Part 180,
        Podiatry).
      - Without Part: e.g. `mcl-299-1980-7` (Occupational Code Article 7,
        Accountancy — this Act doesn't have a Part level below Article).

    Sections are addressed as `mcl-<MCL-CHAPTER>-<NNN[a]>` where the MCL
    chapter is an alias (333 for the PHC; 339 for the Occupational Code)
    and the section ID is 3-5 digits with an optional letter suffix.
    """
    if part:
        base = f"https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-{act_num}-{year}-{article}-{part}"
    else:
        base = f"https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-{act_num}-{year}-{article}"
    html = fetch(base)
    pat = re.compile(rf'objectName=mcl-{re.escape(mcl_chapter)}-(\d{{3,5}}[a-z]?)')
    section_nums = sorted(set(pat.findall(html)))
    return [f"https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-{mcl_chapter}-{n}" for n in section_nums]


def render_yaml_block(state: str, mapping: dict, harvested: dict[str, list[str]]) -> str:
    """Render a state-level yaml snippet from harvested URLs."""
    lines: list[str] = []
    for prof, entry in mapping.items():
        urls = harvested.get(prof, [])
        if not urls:
            continue
        if state == "MN":
            ch = entry["chapter"]
            chapter_url = f"https://www.revisor.mn.gov/statutes/cite/{ch}"
        elif state == "MI":
            act, year, article, part = entry["act"], entry["year"], entry["article"], entry["part"]
            if part:
                chapter_url = f"https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-{act}-{year}-{article}-{part}"
            else:
                chapter_url = f"https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-{act}-{year}-{article}"
        else:
            raise ValueError(state)
        lines.append(f"    {prof}:")
        lines.append(f"      url: \"{chapter_url}\"")
        lines.append(f"      label: \"{entry['label']}\"")
        lines.append(f"      section_url_list:")
        for u in urls:
            lines.append(f"        - \"{u}\"")
    return "\n".join(lines)


def filter_mn_by_section_set(prof_entry: dict, all_urls: list[str]) -> list[str]:
    """For shared-chapter MN cases (Ch 148), filter URLs to the profession's section set."""
    if "section_prefix_set" not in prof_entry and "section_prefix" not in prof_entry:
        return all_urls
    keep = []
    for u in all_urls:
        cite = u.rsplit("/", 1)[-1]
        if "section_prefix_set" in prof_entry:
            if cite in prof_entry["section_prefix_set"]:
                keep.append(u)
        elif "section_prefix" in prof_entry:
            if cite.startswith(prof_entry["section_prefix"]):
                keep.append(u)
    return keep


def run_state(state: str) -> dict[str, list[str]]:
    """Harvest section URLs for every known profession in `state`. Returns {profession: [urls]}."""
    harvested: dict[str, list[str]] = {}
    if state == "MN":
        mapping = MN_CHAPTERS
        chapter_cache: dict[str, list[str]] = {}
        for prof, entry in mapping.items():
            ch = entry["chapter"]
            if ch not in chapter_cache:
                print(f"  [MN] fetching chapter {ch} index ...", file=sys.stderr)
                try:
                    chapter_cache[ch] = harvest_mn_chapter(ch)
                except Exception as e:
                    print(f"    error: {e}", file=sys.stderr)
                    chapter_cache[ch] = []
                time.sleep(0.5)
            urls = filter_mn_by_section_set(entry, chapter_cache[ch])
            harvested[prof] = urls
            print(f"  [MN] {prof}: {len(urls)} section URLs", file=sys.stderr)
    elif state == "MI":
        mapping = MI_PARTS
        for prof, entry in mapping.items():
            act, year, article, part, mcl = entry["act"], entry["year"], entry["article"], entry["part"], entry["mcl"]
            print(f"  [MI] fetching Act {act}/{year} Article {article} Part {part} index ...", file=sys.stderr)
            try:
                urls = harvest_mi_part(act, year, article, part, mcl)
            except Exception as e:
                print(f"    error: {e}", file=sys.stderr)
                urls = []
            harvested[prof] = urls
            print(f"  [MI] {prof}: {len(urls)} section URLs", file=sys.stderr)
            time.sleep(0.5)
    else:
        raise ValueError(f"unknown state: {state}")
    return harvested


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("state", choices=["MN", "MI"])
    args = ap.parse_args()

    harvested = run_state(args.state)
    mapping = MN_CHAPTERS if args.state == "MN" else MI_PARTS
    print(render_yaml_block(args.state, mapping, harvested))


if __name__ == "__main__":
    main()
