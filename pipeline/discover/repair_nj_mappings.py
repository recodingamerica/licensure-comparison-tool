"""Repair New Jersey profession_index mappings that point at a whole TITLE or a few
cherry-picked SECTIONS instead of the profession's CHAPTER(s) (LLM-free; no fetch).

NJ nests sections flat under the title (…/title-45/section-45-5a-10/), and a batch of
NJ cells ended up mapped to the bare title (over-broad) or to a handful of section
URLs (incomplete). Both make the annual refresh unable to reproduce the corpus. The
committed corpus's citations name the real chapters (45:5A → title-45/chapter-5a),
so this rewrites each broken cell's `matched` to those chapter URLs — which, with the
NJ flat-layout walk fix, re-pull the full chapter.

Only rewrites NJ cells whose mapping is a bare title or a section list; leaves clean
chapter mappings alone.

  python -m pipeline.discover.repair_nj_mappings            # dry-run
  python -m pipeline.discover.repair_nj_mappings --apply
"""

from __future__ import annotations

import argparse
import json

from pipeline.paths import TEXT_DIR, PROFESSION_INDEX_DIR, HIERARCHY_DIR
from pipeline._records import write_json_atomic
from pipeline.ingest.pull_text import _OVER_BROAD_MAX
from pipeline.ingest import nj_flat
from pipeline.ingest._section_patterns import is_title_root

# A profession occupying at least this share of a chapter's sections OWNS it; below
# this it merely sits INSIDE it (see _nested_chapters). The NJ flat-layout URL grammar
# (citation/section-url/chapter-url ↔ (title, token)) lives in pipeline.ingest.nj_flat.
_OWNS_CHAPTER_MIN_COVERAGE = 0.5


def _chapter_census() -> dict[tuple[str, str], set[str]]:
    """(title#, chapter-token) → all of that chapter's section URLs, from the committed
    NJ hierarchy. Justia publishes NJ flat (2,286 sections under title-45, no chapter
    pages at all), so the hierarchy IS the full section list — this needs no fetch."""
    census: dict[tuple[str, str], set[str]] = {}
    try:
        nodes = json.loads((HIERARCHY_DIR / "NJ.json").read_text()).get("chapters") or []
    except (OSError, json.JSONDecodeError):
        return census
    for n in nodes:
        key = nj_flat.key_from_section_url(n.get("url", ""))
        if key:
            census.setdefault(key, set()).add(n["url"])
    return census


def _nested_chapters(prof: str, chapters: list[str], census) -> set[str]:
    """Of `chapters`, those the profession is merely NESTED INSIDE rather than owns:
    over the guard's leaf ceiling AND occupied only sparsely.

    NJ title-45 chapter-9 is the Board of Medical Examiners' 336-section chapter, and
    a dozen professions live as a handful of sections inside it (chiropractic is 10 of
    336). Remapping those to the bare chapter URL both over-broadens them and trips
    pull_text's over-broad guard, which zeroes the cell outright — their explicit
    section lists are correct and must be left alone. medicine, which owns 332 of the
    336, is remapped as normal.

    Only chapters big enough to trip the guard are judged: below that ceiling an
    over-broad remap is a scoping question for the section-title matcher, not a
    silent failure, and this tool leaves that decision where it already is."""
    mine = {s.get("url", "") for s in _corpus_sections(prof)}
    nested = set()
    for url in chapters:
        key = nj_flat.key_from_chapter_url(url)
        if not key:
            continue
        all_secs = census.get(key, set())
        if len(all_secs) <= _OVER_BROAD_MAX:
            continue
        if len(mine & all_secs) / len(all_secs) < _OWNS_CHAPTER_MIN_COVERAGE:
            nested.add(url)
    return nested


def _corpus_sections(prof: str) -> list[dict]:
    p = TEXT_DIR / prof / "NJ.json"
    try:
        return json.loads(p.read_text()).get("sections") or []
    except (OSError, json.JSONDecodeError):
        return []


def _nj_chapters_from_corpus(prof: str) -> list[str]:
    """The distinct chapter URLs the committed NJ corpus's sections belong to,
    derived from their citations (45:5A → …/title-45/chapter-5a/)."""
    chapters: dict[tuple, str] = {}
    for s in _corpus_sections(prof):
        key = nj_flat.key_from_citation(s.get("citation") or "")
        if key:
            chapters[key] = nj_flat.chapter_url(key)
    return [chapters[k] for k in sorted(chapters)]


def _is_broken(matched: list[dict]) -> bool:
    """A bare-title node (over-broad) or an individual-section node (incomplete)."""
    for n in matched:
        u = n.get("url", "")
        if "/section-" in u:
            return True
        if is_title_root(u):
            return True
    return False


def plan() -> dict[str, tuple[list[str], set[str]]]:
    """prof -> (chapter urls to map to, chapter urls left as section lists)."""
    census = _chapter_census()
    out: dict[str, tuple[list[str], set[str]]] = {}
    for f in sorted(PROFESSION_INDEX_DIR.glob("*.json")):
        try:
            idx = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        matched = ((idx.get("by_state") or {}).get("NJ") or {}).get("matched") or []
        if not (matched and _is_broken(matched)):
            continue
        chs = _nj_chapters_from_corpus(f.stem)
        nested = _nested_chapters(f.stem, chs, census)
        keep = [c for c in chs if c not in nested]
        if keep or nested:
            out[f.stem] = (keep, nested)
    return out


def _retained_nodes(matched: list[dict], nested: set[str]) -> list[dict]:
    """The original section nodes belonging to a chapter we declined to remap — the
    profession is nested inside it, so its curated section list stays as-is."""
    tokens = {k for k in (nj_flat.key_from_chapter_url(u) for u in nested) if k}
    return [n for n in matched if nj_flat.key_from_section_url(n.get("url", "")) in tokens]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true", help="Write the index files (default: dry-run).")
    args = ap.parse_args(argv)
    to_fix = plan()
    n_changed = 0
    for prof, (chapters, nested) in sorted(to_fix.items()):
        f = PROFESSION_INDEX_DIR / f"{prof}.json"
        idx = json.loads(f.read_text())
        nj = idx.setdefault("by_state", {}).setdefault("NJ", {})
        matched = nj.get("matched") or []
        retained = _retained_nodes(matched, nested)
        new = [{"url": u, "label": "", "slug": "", "via": "nj_mapping_repair"}
               for u in chapters] + retained
        if new == matched:
            continue
        n_changed += 1
        nj["matched"] = new
        note = (f"  [nested, section list kept: {sorted(u.split('/')[-2] for u in nested)}]"
                if nested else "")
        print(f"  {prof}/NJ: {len(matched)} node(s) -> {len(chapters)} chapter(s) "
              f"+ {len(retained)} section(s): "
              f"{[u.split('justia.com')[-1] for u in chapters]}{note}")
        if args.apply:
            write_json_atomic(f, idx)
    tail = "" if args.apply else "  (dry-run — pass --apply)"
    print(f"\n{'repaired' if args.apply else 'would repair'} {n_changed} NJ cell(s){tail}")


if __name__ == "__main__":
    main()
