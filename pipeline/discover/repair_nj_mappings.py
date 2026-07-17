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
import re

from pipeline.paths import TEXT_DIR, PROFESSION_INDEX_DIR
from pipeline._records import write_json_atomic

_NJ_CITE = re.compile(r"(\d+):([0-9A-Za-z]+?)-")  # "45:5A-1" -> ("45", "5A")


def _nj_chapters_from_corpus(prof: str) -> list[str]:
    """The distinct chapter URLs the committed NJ corpus's sections belong to,
    derived from their citations (45:5A → …/title-45/chapter-5a/)."""
    p = TEXT_DIR / prof / "NJ.json"
    try:
        secs = json.loads(p.read_text()).get("sections") or []
    except (OSError, json.JSONDecodeError):
        return []
    chapters: dict[tuple, str] = {}
    for s in secs:
        m = _NJ_CITE.match((s.get("citation") or ""))
        if m:
            t, ch = m.group(1), m.group(2).lower()
            chapters[(t, ch)] = f"https://law.justia.com/codes/new-jersey/title-{t}/chapter-{ch}/"
    return [chapters[k] for k in sorted(chapters)]


def _is_broken(matched: list[dict]) -> bool:
    """A bare-title node (over-broad) or an individual-section node (incomplete)."""
    for n in matched:
        u = n.get("url", "")
        if "/section-" in u:
            return True
        if re.search(r"/title-[^/]+/?$", u) and "/chapter-" not in u:
            return True
    return False


def plan() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for f in sorted(PROFESSION_INDEX_DIR.glob("*.json")):
        try:
            idx = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        matched = ((idx.get("by_state") or {}).get("NJ") or {}).get("matched") or []
        if matched and _is_broken(matched):
            chs = _nj_chapters_from_corpus(f.stem)
            if chs:
                out[f.stem] = chs
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true", help="Write the index files (default: dry-run).")
    args = ap.parse_args(argv)
    to_fix = plan()
    for prof, chapters in sorted(to_fix.items()):
        f = PROFESSION_INDEX_DIR / f"{prof}.json"
        idx = json.loads(f.read_text())
        nj = idx.setdefault("by_state", {}).setdefault("NJ", {})
        old = [n.get("url", "").split("justia.com")[-1] for n in (nj.get("matched") or [])]
        nj["matched"] = [{"url": u, "label": "", "slug": "", "via": "nj_mapping_repair"}
                         for u in chapters]
        print(f"  {prof}/NJ: {len(old)} node(s) -> {len(chapters)} chapter(s): "
              f"{[u.split('justia.com')[-1] for u in chapters]}")
        if args.apply:
            write_json_atomic(f, idx)
    tail = "" if args.apply else "  (dry-run — pass --apply)"
    print(f"\n{'repaired' if args.apply else 'would repair'} {len(to_fix)} NJ cell(s){tail}")


if __name__ == "__main__":
    main()
