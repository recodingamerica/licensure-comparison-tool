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

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterator


def write_text_atomic(path: Path, text: str) -> None:
    """Write `text` to `path` atomically: to a temp file in the SAME directory, then
    os.replace() into place. On one filesystem os.replace is atomic, so a crash
    (Ctrl-C / OOM / disk-full) mid-write can no longer leave a TRUNCATED file at a
    committed stage-output path — either the old content survives intact or the full
    new content lands, never a half-written JSON the next stage would choke on. The
    temp file is removed if anything fails."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_json_atomic(path: Path, obj: Any, **dumps_kwargs: Any) -> None:
    """json.dumps(obj) written atomically (see write_text_atomic). Defaults to
    indent=2; pass e.g. ensure_ascii=False to match a call site's formatting."""
    dumps_kwargs.setdefault("indent", 2)
    write_text_atomic(path, json.dumps(obj, **dumps_kwargs))


def record_files(directory: Path) -> Iterator[Path]:
    """Yield the `*.json` record files in `directory`, sorted, skipping the
    `_`-prefixed bookkeeping files. Empty (no yields) if the dir doesn't exist."""
    if not directory.exists():
        return
    for p in sorted(directory.glob("*.json")):
        if p.name.startswith("_"):
            continue
        yield p
