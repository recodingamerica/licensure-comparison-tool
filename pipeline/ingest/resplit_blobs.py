"""Split committed inline-act blobs (ND/IL whole-chapter pages stored as ONE section)
into per-section records — a LOCAL transform, NO re-fetch.

Some states serve a whole chapter/act on ONE page with no per-section links, so the
walk stored the entire thing as a single 30-80k-char "section". pull_text already knows
how to split those (split_nd_blob / split_il_inline via _add_inline_section during a
fresh pull), but corpora pulled before that logic — or before its regex handled dotted
ND titles — are still committed as blobs. Re-fetching to fix them is unreliable (the
Scrapling session bug) and unnecessary: the blob text is complete, so we split it in
place. Same pattern as dedupe_corpora (a pure local transform on committed text/).

  python -m pipeline.ingest.resplit_blobs                       # dry-run report
  python -m pipeline.ingest.resplit_blobs --apply               # write the splits
  python -m pipeline.ingest.resplit_blobs --professions insurance_producer,apiarist --apply

NOTE (downstream): splitting text/ makes clean/trimmed/structured stale for those cells —
they need clean -> trim -> extract (+ republish) to reach the site. A separate,
cost-bearing step; this only splits the corpus text.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys

from pipeline.ingest.pull_text import (
    looks_like_nd_blob, split_nd_blob, looks_like_il_ilcs, split_il_inline,
)
from pipeline.paths import TEXT_DIR
from pipeline._records import record_files, read_json


def resplit_corpus(d: dict) -> dict | None:
    """If `d` is a single-section inline-act blob (ND/IL), return a copy split into
    per-section records; else None. Requires ≥2 resulting sections so a genuinely
    1-section chapter (or a non-blob) is left untouched."""
    secs = d.get("sections") or []
    if len(secs) != 1 or secs[0].get("error"):
        return None
    text, url = secs[0].get("text") or "", secs[0].get("url") or ""
    if looks_like_il_ilcs(text):
        split = split_il_inline(text, url)
    elif looks_like_nd_blob(text, url):
        split = split_nd_blob(text, url)
    else:
        return None
    if len(split) < 2:
        return None
    nd = dict(d)
    nd["sections"] = [dataclasses.asdict(s) for s in split]
    nd["total_chars"] = sum(s.text_len for s in split)
    return nd


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true",
                    help="Write the split corpora. Default is a dry-run report.")
    ap.add_argument("--professions", default="",
                    help="Comma-separated subset (e.g. insurance_producer,apiarist); empty = all.")
    args = ap.parse_args(argv)
    only = {p.strip() for p in args.professions.split(",") if p.strip()}

    changed = added = 0
    for prof_dir in sorted(TEXT_DIR.glob("*")):
        if not prof_dir.is_dir():
            continue
        if only and prof_dir.name not in only:
            continue
        for path in record_files(prof_dir):
            d = read_json(path)
            if not isinstance(d, dict):
                continue
            nd = resplit_corpus(d)
            if nd is None:
                continue
            before, after = len(d["sections"]), len(nd["sections"])
            changed += 1
            added += after - before
            print(f"  {prof_dir.name}/{path.stem}: {before} -> {after} sections")
            if args.apply:
                path.write_text(json.dumps(nd, indent=2))

    verb = "split" if args.apply else "would split"
    tail = "" if args.apply else "  (dry-run — pass --apply to write)"
    print(f"\n{verb} {changed} blob corpora into {added + changed} sections{tail}")
    if not changed:
        sys.exit(0)


if __name__ == "__main__":
    main()
