"""Preflight gate for the batch-extract queue.

Before spending any LLM budget, check every (profession, state) in a queue for
the failure modes that previously slipped through *silently* and either wasted
extract slots or produced junk:

  NO_SCHEMA      results/discovered/<prof>.json missing — extract can't build a
                 profile model, so submit would skip the whole profession.
  NO_TRIMMED     results/trimmed/<prof>/<state>.json missing — pull/clean/trim
                 never reached this pair.
  EMPTY_TRIMMED  trimmed file present but 0 sections (raw-empty or post-clean
                 empty); extracting it spends a slot on nothing.
  POISONED       trim degraded to keep-everything on LLM failure (see
                 ingest._trim_health.is_poisoned); the "trim" is not real signal.

A pair with none of the above is extract-ready.

CLI:

    python -m pipeline.extract.preflight --queue path/to/queue.json

Prints a per-blocker report and exits nonzero if any blocker is found, so it
can gate a shell pipeline. `submit` calls run_preflight() directly and refuses
to submit a failing queue unless --force is passed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


from pipeline.paths import DISCOVERED_DIR, TRIMMED_DIR
from pipeline.ingest._trim_health import is_poisoned

# Ordered worst-first; the first matching condition is the reported blocker.
BLOCKERS = ("NO_SCHEMA", "NO_TRIMMED", "EMPTY_TRIMMED", "POISONED")


def check_pair(profession: str, state: str) -> str | None:
    """Return the blocker code for one (profession, state), or None if ready."""
    if not (DISCOVERED_DIR / f"{profession}.json").exists():
        return "NO_SCHEMA"
    tpath = TRIMMED_DIR / profession / f"{state}.json"
    if not tpath.exists():
        return "NO_TRIMMED"
    try:
        d = json.loads(tpath.read_text())
    except Exception:
        # An unreadable/corrupt trim is unusable — treat like empty.
        return "EMPTY_TRIMMED"
    # Trims are written either as a bare list of sections or as {"sections": [...]};
    # normalize so a bare-list corpus isn't mistaken for empty/corrupt.
    if isinstance(d, list):
        d = {"sections": d}
    if not (d.get("sections") or []):
        return "EMPTY_TRIMMED"
    if is_poisoned(d):
        return "POISONED"
    return None


def run_preflight(queue: dict[str, list[str]]) -> dict:
    """Check a {profession: [states]} queue.

    Returns {"ok": bool, "ready": [(p,s)...], "blocked": {CODE: [(p,s)...]}}.
    """
    blocked: dict[str, list[tuple[str, str]]] = {b: [] for b in BLOCKERS}
    ready: list[tuple[str, str]] = []
    for profession, states in queue.items():
        for state in states:
            code = check_pair(profession, state)
            if code is None:
                ready.append((profession, state))
            else:
                blocked[code].append((profession, state))
    ok = not any(blocked[b] for b in BLOCKERS)
    return {"ok": ok, "ready": ready, "blocked": blocked}


def format_report(report: dict) -> str:
    lines: list[str] = []
    total = len(report["ready"]) + sum(len(v) for v in report["blocked"].values())
    lines.append(f"PREFLIGHT: {total} (profession,state) pairs checked")
    lines.append(f"  READY: {len(report['ready'])}")
    for code in BLOCKERS:
        pairs = report["blocked"][code]
        lines.append(f"  {code}: {len(pairs)}")
        if pairs:
            by_prof: dict[str, list[str]] = defaultdict(list)
            for p, s in pairs:
                by_prof[p].append(s)
            for prof in sorted(by_prof):
                lines.append(f"      {prof:32s} {' '.join(sorted(by_prof[prof]))}")
    lines.append(f"PREFLIGHT: {'PASS' if report['ok'] else 'FAIL'}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", required=True, help="JSON file: {profession: [states]}")
    args = ap.parse_args()

    queue = json.loads(Path(args.queue).read_text())
    report = run_preflight(queue)
    print(format_report(report))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
