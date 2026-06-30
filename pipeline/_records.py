"""Tiny shared helper for iterating per-state record files.

Across the pipeline, dozens of stage scripts walk a `results/<stage>/<profession>/`
directory the same way: glob `*.json`, sort, and skip the `_`-prefixed bookkeeping
files (`_summary.json`, `_candidates.json`, …). This centralizes that loop so the
"skip underscore" convention lives in one place.

It yields **paths**, not parsed dicts, on purpose: callers differ on how a corrupt
record should be handled (some must fail loud — see publish/refresh_all — others
skip leniently), so the load + error policy stays with the caller.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator


def record_files(directory: Path) -> Iterator[Path]:
    """Yield the `*.json` record files in `directory`, sorted, skipping the
    `_`-prefixed bookkeeping files. Empty (no yields) if the dir doesn't exist."""
    if not directory.exists():
        return
    for p in sorted(directory.glob("*.json")):
        if p.name.startswith("_"):
            continue
        yield p
