"""Preflight gate for the batch-extract queue.

Before spending any LLM budget, check every (profession, state) in a queue for
the failure modes that previously slipped through *silently* and either wasted
extract slots or produced junk:

  NO_SCHEMA      results/discovered/<prof>.json missing — extract can't build a
                 profile model, so submit would skip the whole profession.
  SCHEMA_DIRTY   the discovered schema differs from git HEAD. Schemas are stable
                 committed contracts; an uncommitted one on disk is almost always
                 accidental re-derivation churn (2026-07-29: two batches extracted
                 31 nursing states + acupuncture/UT against a schema that renamed
                 26 of 29 fields and was reverted minutes later). Commit the schema
                 deliberately, or restore it, before extracting. A brand-new
                 (untracked) schema is allowed — this only fires on tracked+modified.
  NO_TRIMMED     results/trimmed/<prof>/<state>.json missing — pull/clean/trim
                 never reached this pair.
  EMPTY_TRIMMED  trimmed file present but 0 sections (raw-empty or post-clean
                 empty); extracting it spends a slot on nothing.
  POISONED       trim degraded to keep-everything on LLM failure (see
                 ingest._trim_health.is_poisoned); the "trim" is not real signal.
  STALE_UPSTREAM the clean or trim on disk no longer reflects the current corpus
                 (provenance content-hash says stale) — extracting would silently
                 read OUT-OF-DATE law. This is exactly how 31 polluted nursing
                 trims reached a batch on 2026-07-29: the files existed and looked
                 healthy, but a revert had restored pre-de-pollution copies.
                 Re-run clean+trim for the flagged cells first.

A pair with none of the above is extract-ready.

One further category is reported but does NOT block, because it is a settled
answer rather than a problem:

  SKIP_ABSENCE   the cell's structured record is `source: verified_absence` — a
                 hand-verified "this state has no state-level license" from
                 config/verified_absences.yaml, carrying its own basis + note.
                 Such a cell has no licensing act to extract, so it normally has
                 no corpus and would otherwise surface as NO_TRIMMED forever
                 (2026-07-31: 22 of them held up a 648-cell wave that way).
                 Where one DOES have a corpus, that corpus is the local-enabling
                 hook (KS municipal art. 15, NY apprenticeship) or an outright
                 mis-map (hvac/SD held Social Work law) — extracting it would
                 overwrite the verified record with claims drawn from statutes
                 that do not license the profession, and apply_verified_absences
                 never clobbers an extracted record, so it is a one-way door.
                 These pairs are dropped from the queue by drop_skipped().

CLI:

    python -m pipeline.extract.preflight --queue path/to/queue.json

Prints a per-blocker report and exits nonzero if any blocker is found, so it
can gate a shell pipeline. `submit` calls run_preflight() directly and refuses
to submit a failing queue unless --force is passed.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from functools import lru_cache
from pathlib import Path


from pipeline import provenance
from pipeline.config.loaders import is_absence_record
from pipeline.paths import DISCOVERED_DIR, STRUCTURED_DIR, TRIMMED_DIR, REPO_ROOT
from pipeline.ingest._trim_health import is_poisoned

# Ordered worst-first; the first matching condition is the reported blocker.
BLOCKERS = ("NO_SCHEMA", "SCHEMA_DIRTY", "NO_TRIMMED", "EMPTY_TRIMMED", "POISONED",
            "STALE_UPSTREAM")
# Reported alongside the blockers, but never fails the gate — see module docstring.
SKIPS = ("SKIP_ABSENCE",)
CODES = BLOCKERS + SKIPS


@lru_cache(maxsize=None)
def schema_dirty(profession: str) -> bool:
    """True when the discovered schema is TRACKED and MODIFIED vs git HEAD — the
    signature of accidental re-derivation churn. Untracked (a brand-new profession's
    first schema) is allowed; so is any state we can't determine (no git)."""
    p = DISCOVERED_DIR / f"{profession}.json"
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", str(p)],
                             capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=10)
    except Exception:
        return False
    line = out.stdout.strip()
    return bool(line) and not line.startswith("??")


def is_verified_absence(profession: str, state: str) -> bool:
    """True when the cell's structured record is a hand-verified absence.

    Keyed on the record actually on disk, not on membership in
    config/verified_absences.yaml: a few pairs are listed there but carry a real
    extracted record from a real corpus (construction_trades OK/WY), and those
    should keep re-extracting normally.
    """
    path = STRUCTURED_DIR / profession / f"{state}.json"
    try:
        rec = json.loads(path.read_text())
    except Exception:
        return False
    return is_absence_record(rec)


def check_pair(profession: str, state: str) -> str | None:
    """Return the blocker/skip code for one (profession, state), or None if ready."""
    if is_verified_absence(profession, state):
        return "SKIP_ABSENCE"
    if not (DISCOVERED_DIR / f"{profession}.json").exists():
        return "NO_SCHEMA"
    if schema_dirty(profession):
        return "SCHEMA_DIRTY"
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
    # Existence isn't freshness: the file can be healthy-looking but built from a
    # corpus that has since changed (or been reverted). Only "stale" blocks —
    # "unstamped" cells (pre-provenance history) stay extractable.
    if (provenance.check("clean", profession, state) == "stale"
            or provenance.check("trim", profession, state) == "stale"):
        return "STALE_UPSTREAM"
    return None


def run_preflight(queue: dict[str, list[str]]) -> dict:
    """Check a {profession: [states]} queue.

    Returns {"ok": bool, "ready": [(p,s)...], "blocked": {CODE: [(p,s)...]}}.
    `ok` weighs only BLOCKERS — SKIPS are settled answers, not problems.
    """
    schema_dirty.cache_clear()   # dedup git calls within this run, never across runs
    blocked: dict[str, list[tuple[str, str]]] = {c: [] for c in CODES}
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


def drop_skipped(queue: dict[str, list[str]], report: dict) -> dict[str, list[str]]:
    """Return `queue` minus the pairs preflight marked as skips.

    Callers iterate the queue rather than report["ready"], so without this a
    non-blocking skip would sail through the gate and still be extracted.
    """
    skip = {pair for code in SKIPS for pair in report["blocked"].get(code, [])}
    if not skip:
        return queue
    out = {}
    for profession, states in queue.items():
        kept = [s for s in states if (profession, s) not in skip]
        if kept:
            out[profession] = kept
    return out


def format_report(report: dict) -> str:
    lines: list[str] = []
    total = len(report["ready"]) + sum(len(v) for v in report["blocked"].values())
    lines.append(f"PREFLIGHT: {total} (profession,state) pairs checked")
    lines.append(f"  READY: {len(report['ready'])}")
    for code in CODES:
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
