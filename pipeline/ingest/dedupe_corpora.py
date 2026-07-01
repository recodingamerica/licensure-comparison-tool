"""Content-based de-duplication of already-fetched corpora (#7, generalized).

WHY NOT `pull_text._dedupe_year_versions`: that collapses sections by canonical
URL (year segment stripped), which is correct for true Justia year-version pages
(one URL per section, distinct year paths). But it is *destructive* for sources
where many distinct sections legitimately share ONE url — the NV/SD APIs, MD/VA/
WA HTML, MI act-pages, FL single-page chapters, and ND chapter-blobs split in
place. There a URL-dedup collapses e.g. construction_trades/FL 80 sections -> 1.

This pass dedupes by NORMALIZED TEXT instead: drop any section whose text we've
already seen (whitespace-normalized), keep first occurrence, preserve order.
- year-version duplicates (identical statute text across years) -> collapsed
- genuinely distinct sections (any source, shared URL or not)   -> kept
- a section amended between years (different text)              -> both kept
  (harmless over-keep; we never drop distinct content)

Operates IN PLACE on results/text/<prof>/<state>.json (no re-fetch — the corpora
are committed; Justia bulk-fetching is blocked). After running, re-run
clean_text (deterministic) so clean/ matches; trim+extract to refresh records.

Run:
  pipeline/.venv/bin/python -m pipeline.ingest.dedupe_corpora --dry-run        # report only
  pipeline/.venv/bin/python -m pipeline.ingest.dedupe_corpora --profession medicine
  pipeline/.venv/bin/python -m pipeline.ingest.dedupe_corpora                  # all corpora
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
from pathlib import Path

from pipeline.paths import TEXT_DIR


def _norm(t: str | None) -> str:
    return re.sub(r"\s+", " ", t or "").strip()


def content_dedupe(sections: list[dict]) -> list[dict]:
    """Keep first occurrence of each unique (normalized) section text, in order."""
    seen: set[str] = set()
    out: list[dict] = []
    for s in sections:
        h = hashlib.md5(_norm(s.get("text")).encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        out.append(s)
    return out


def process_file(fp: str, write: bool) -> tuple[int, int]:
    try:
        d = json.loads(Path(fp).read_text())
    except (json.JSONDecodeError, OSError):
        return (0, 0)
    secs = d.get("sections") or []
    if not secs:
        return (0, 0)
    deduped = content_dedupe(secs)
    before, after = len(secs), len(deduped)
    if write and after < before:
        d["sections"] = deduped
        Path(fp).write_text(json.dumps(d, indent=1, ensure_ascii=False))
    return (before, after)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="", help="limit to one profession (default: all)")
    ap.add_argument("--dry-run", action="store_true", help="report only, do not write")
    args = ap.parse_args()

    pat = f"{args.profession}/*.json" if args.profession else "*/*.json"
    files = sorted(f for f in glob.glob(str(TEXT_DIR / pat)) if "_summary" not in f)
    tb = ta = changed = 0
    for fp in files:
        b, a = process_file(fp, write=not args.dry_run)
        tb += b
        ta += a
        if a < b:
            changed += 1
            key = fp.replace(str(TEXT_DIR) + "/", "")
            print(f"  {key}: {b} -> {a}  (-{b - a})")
    verb = "would remove" if args.dry_run else "removed"
    print(f"\ncontent-dedupe: {verb} {tb - ta} duplicate sections across "
          f"{changed} corpora ({tb} -> {ta} total)")
    if args.dry_run:
        print("  (dry-run; re-run without --dry-run to apply, then re-run clean_text)")


if __name__ == "__main__":
    main()
