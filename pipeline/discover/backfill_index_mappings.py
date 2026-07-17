"""Restore lost index mappings from committed corpora (LLM-free repair; no fetch).

audit_mappings flags NO_MAPPING cells: a committed text/<prof>/<state>.json exists but
profession_index/<prof>.json has no `matched` chapters for that state, so the annual
refresh silently skips it (it's never in the worklist). Every such corpus still records
the `chapter_urls` it was pulled from — the ground truth. This writes those back into
the index's `matched` list, restoring the cell to the refresh's coverage.

Only touches cells the audit classifies as NO_MAPPING (real sections, empty mapping);
never overwrites an existing mapping.

  python -m pipeline.discover.backfill_index_mappings                        # dry-run
  python -m pipeline.discover.backfill_index_mappings --apply
  python -m pipeline.discover.backfill_index_mappings --professions electrician,hvac --apply
"""

from __future__ import annotations

import argparse
import collections
import json

from pipeline.paths import TEXT_DIR, PROFESSION_INDEX_DIR
from pipeline._records import write_json_atomic
from pipeline.eval.audit_mappings import audit


def _corpus_chapters(prof: str, state: str) -> list[str]:
    try:
        return json.loads((TEXT_DIR / prof / f"{state}.json").read_text()).get("chapter_urls") or []
    except (OSError, json.JSONDecodeError):
        return []


def plan() -> dict[str, dict[str, list[str]]]:
    """{profession: {state: [chapter_url, ...]}} for restorable NO_MAPPING cells."""
    out: dict[str, dict[str, list[str]]] = collections.defaultdict(dict)
    for prof, state, issue, _ in audit():
        if issue != "NO_MAPPING":
            continue
        chs = _corpus_chapters(prof, state)
        if chs:  # ground truth to restore from
            out[prof][state] = chs
    return out


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true", help="Write the index files (default: dry-run).")
    ap.add_argument("--professions", default="", help="Comma-separated subset; empty = all.")
    args = ap.parse_args(argv)
    only = {p.strip() for p in args.professions.split(",") if p.strip()}

    to_fix = plan()
    cells = chapters = 0
    for prof, states in sorted(to_fix.items()):
        if only and prof not in only:
            continue
        idx_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        if not idx_path.exists():
            continue
        idx = json.loads(idx_path.read_text())
        by_state = idx.setdefault("by_state", {})
        touched = False
        for state, chs in sorted(states.items()):
            node = by_state.setdefault(state, {})
            if node.get("matched"):
                continue  # never clobber an existing mapping
            node["matched"] = [{"url": u, "label": "", "slug": "", "via": "index_backfill"}
                               for u in chs]
            cells += 1
            chapters += len(chs)
            print(f"  {prof}/{state}: restore {len(chs)} chapter mapping(s)")
            touched = True
        if args.apply and touched:
            write_json_atomic(idx_path, idx)

    verb = "restored" if args.apply else "would restore"
    tail = "" if args.apply else "  (dry-run — pass --apply to write the index files)"
    print(f"\n{verb} {cells} cell(s) / {chapters} chapter mapping(s){tail}")


if __name__ == "__main__":
    main()
