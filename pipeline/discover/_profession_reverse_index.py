"""Reverse the profession_index: build (state, chapter-slug) → [profession] mappings.

The forward index says "for podiatry, in UT, the practice act is chapter-5a."
We frequently need the reverse: "in UT, what profession is chapter-5a?"

Used by umbrella scope assignment (`assign_umbrella_scope.py`) to resolve
citations like "Title 58, Chapter 5a, Podiatric Physician Licensing Act" to
the canonical profession id `podiatry`.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from pipeline.paths import PROFESSION_INDEX_DIR
from pipeline.config.loaders import matched_for, all_profession_ids, load_profession_index


def build_reverse_index(state: str) -> dict[str, list[str]]:
    """Return `{chapter_slug: [profession_id, ...]}` for the given state.

    A slug can map to multiple professions when the state's chapter regulates
    several (e.g. UT chapter-20b covers environmental_health AND mental_health_counseling).
    A profession can also map to multiple slugs (e.g. UT nursing → 31b, 31d, 31e);
    that direction is in the forward index, this helper only inverts.
    """
    rev: dict[str, list[str]] = defaultdict(list)
    for prof in all_profession_ids():
        d = load_profession_index(prof)
        prof = d["profession"]
        for entry in matched_for(d, state):
            slug = entry.get("slug", "")
            if slug and prof not in rev[slug]:
                rev[slug].append(prof)
    return dict(rev)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    rev = build_reverse_index(args.state)
    for slug, profs in sorted(rev.items()):
        flag = "  (multi)" if len(profs) > 1 else ""
        print(f"  {slug:20} → {', '.join(profs)}{flag}")
    print(f"\n{len(rev)} chapter slugs mapped")
