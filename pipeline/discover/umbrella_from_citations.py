"""Turn the citation-based umbrella audit into a pull-list — the accurate driver for
pull_umbrella_text.

The problem (see corpus_status umbrella): a profession's pulled act heavily CITES a
shared general-provisions chapter (NM 61-1 "Uniform Licensing Act" — discipline, fees,
hearings — cited by 39 NM professions) that we never pulled, because that chapter is
nobody's profession-chapter so nothing targets it. find_umbrella_chapters (the old LLM
heuristic) picked a different, largely-empty set; the chapters professions actually cite
are essentially all unpulled.

This driver uses the REAL dependency signal — the citation audit's {state -> chapter ->
professions} — and maps each cited chapter id ("61-1") to its Justia URL via the
hierarchy we already have (the id is just the last two numbered URL segments), then
MERGES those into results/umbrella_chapters/<STATE>.json (source='citation_audit', with
`cited_by`). pull_umbrella_text then fetches the bodies and extract_state folds them in
as supplemental context for every profession in the state. LLM-free.

Run:
  python -m pipeline.discover.umbrella_from_citations                 # dry-run report
  python -m pipeline.discover.umbrella_from_citations --write         # merge pull-list
  python -m pipeline.discover.umbrella_from_citations --min-profs 3   # only chapters
                                                                        shared by >=3 profs
Then:  python -m pipeline.ingest.pull_umbrella_text   (→ re-extract the affected profs)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse as up
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import HIERARCHY_DIR, RESULTS_DIR  # noqa: E402
from eval.corpus_status import umbrella_candidates  # noqa: E402

UMBRELLA_DIR = RESULTS_DIR / "umbrella_chapters"


def citation_id_from_url(url: str) -> str | None:
    """The audit's 'A-B' chapter id = the last two NUMBERED path segments, leading
    zeros stripped. NM .../chapter-61/article-1/ -> '61-1'; GA .../title-43/chapter-1/
    -> '43-1'; SD .../title-36/chapter-01/ -> '36-1'."""
    segs = [s for s in up.urlparse(url).path.split("/") if re.search(r"\d", s or "")]
    nums = [str(int(re.search(r"\d+", s).group())) for s in segs[-2:]]
    return "-".join(nums) if len(nums) == 2 else None


def _chapter_nodes(state: str) -> list[dict]:
    """Original (non-depth-expanded) chapter nodes for a state."""
    fp = HIERARCHY_DIR / f"{state}.json"
    if not fp.exists():
        return []
    return [c for c in (json.loads(fp.read_text()).get("chapters", []) or [])
            if not c.get("parent_chapter_url") and "law.justia.com" in (c.get("url") or "")]


def _id_map(state: str) -> dict[str, dict]:
    """citation-id -> hierarchy node, for one state."""
    out: dict[str, dict] = {}
    for c in _chapter_nodes(state):
        cid = citation_id_from_url(c.get("url", ""))
        if cid and cid not in out:
            out[cid] = c
    return out


def build(min_refs: int, min_profs: int) -> dict[str, dict]:
    """{state: {"matched": [records], "unmatched": [chapter ids]}} from the audit."""
    audit = umbrella_candidates(min_refs=min_refs)  # {state: {chapter: [profs]}}
    result: dict[str, dict] = {}
    for state, chapters in audit.items():
        idmap = _id_map(state)
        matched, unmatched = [], []
        for ch, profs in chapters.items():
            if len(profs) < min_profs:
                continue
            node = idmap.get(ch)
            if node:
                matched.append({
                    "slug": node.get("slug") or up.urlparse(node["url"]).path.rstrip("/").rsplit("/", 1)[-1],
                    "label": node.get("label", ""),
                    "url": node["url"],
                    "source_title_url": node.get("source_title_url", ""),
                    "source": "citation_audit",
                    "cited_by": sorted(profs),
                })
            else:
                unmatched.append(ch)
        if matched or unmatched:
            result[state] = {"matched": matched, "unmatched": sorted(unmatched)}
    return result


def merge_into_umbrella_chapters(result: dict[str, dict]) -> dict[str, int]:
    """Merge matched records into results/umbrella_chapters/<STATE>.json (dedup by url)."""
    written: dict[str, int] = {}
    for state, data in result.items():
        if not data["matched"]:
            continue
        fp = UMBRELLA_DIR / f"{state}.json"
        rec = json.loads(fp.read_text()) if fp.exists() else {"state": state, "umbrella_chapters": []}
        chapters = rec.setdefault("umbrella_chapters", [])
        have = {c.get("url") for c in chapters}
        added = 0
        for m in data["matched"]:
            if m["url"] not in have:
                chapters.append(m); have.add(m["url"]); added += 1
        if added:
            UMBRELLA_DIR.mkdir(parents=True, exist_ok=True)
            fp.write_text(json.dumps(rec, indent=1, ensure_ascii=False))
            written[state] = added
    return written


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-refs", type=int, default=5,
                    help="min times a chapter is cited within ONE corpus to count (audit threshold)")
    ap.add_argument("--min-profs", type=int, default=3,
                    help="only chapters shared by >= this many professions in a state (the real umbrellas)")
    ap.add_argument("--write", action="store_true", help="merge the pull-list into umbrella_chapters/")
    args = ap.parse_args()

    result = build(args.min_refs, args.min_profs)
    tot_m = sum(len(d["matched"]) for d in result.values())
    tot_u = sum(len(d["unmatched"]) for d in result.values())
    print(f"citation audit (min-refs {args.min_refs}, min-profs {args.min_profs}): "
          f"{tot_m} shared chapters mapped to a Justia URL across {len(result)} states; "
          f"{tot_u} unmatched (no hierarchy node)")
    for state in sorted(result):
        m = result[state]["matched"]
        if m:
            top = max(m, key=lambda x: len(x["cited_by"]))
            print(f"  {state}: +{len(m)}  e.g. {top['label'][:38]} (cited by {len(top['cited_by'])})")

    if args.write:
        written = merge_into_umbrella_chapters(result)
        print(f"\nwrote {sum(written.values())} chapter(s) across {len(written)} states to "
              f"umbrella_chapters/  →  next: pull_umbrella_text")
    else:
        print("\n(dry-run) re-run with --write to merge into umbrella_chapters/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
