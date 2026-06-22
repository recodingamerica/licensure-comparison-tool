"""Resumable, block-aware batch puller for the whole worklist.

Built for the GitHub-Actions rotate-on-block strategy: Justia blocks by IP, so
a fresh runner gets a fresh IP. This driver pulls slowly across every matched
(profession, state) pair that does not yet have a healthy committed corpus,
commits as it goes (caller commits the files), and exits with a code that tells
the workflow whether to spawn a fresh runner:

  exit 0   — worklist exhausted (everything healthy) OR clean time-budget stop
             with no work remaining.
  exit 75  — work remains: either we hit the consecutive-block threshold (this
             IP looks banned — rotate now) or the time budget ran out mid-list.
             The workflow re-dispatches on a fresh runner.
  exit 1   — unexpected error.

Resume is implicit: a state with a healthy committed corpus (>=1 ok section) is
skipped, so each fresh runner picks up exactly where the last left off. A state
that yields 0 ok sections (blocked / empty) is NEVER written, so it stays on the
worklist for the next runner instead of leaving a junk empty file behind.

Concurrency: run ONE of these at a time (Justia must not see parallel pulling).
The workflow enforces this with a concurrency group.

Usage:
  python -m pipeline.ingest.pull_all                      # everything missing
  python -m pipeline.ingest.pull_all --professions plumbing,electrician,hvac
  python -m pipeline.ingest.pull_all --max-minutes 50 --block-threshold 6
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict
from pathlib import Path

# Match pull_text's import shim: put pipeline/ingest on the path so `import
# pull_text` resolves, and pipeline/ on the path so pull_text's `from paths
# import ...` resolves when it loads.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Reuse the single-state machinery so corpus shape / fetch / guards stay identical.
import pull_text as pt  # noqa: E402

log = logging.getLogger("pull_all")

EXIT_DONE = 0
EXIT_WORK_REMAINS = 75
EXIT_ERROR = 1


def _healthy(path) -> bool:
    """True if a committed corpus has at least one successfully-fetched section."""
    try:
        d = json.loads(path.read_text())
    except Exception:
        return False
    return any(not s.get("error") for s in (d.get("sections") or []))


def _rows_for_state(payload: dict, state: str) -> list[dict]:
    """profession_index node(s) -> the per-state row shape pull_state expects.
    Mirrors pull_text.main()'s conversion exactly."""
    rows: list[dict] = []
    for node in payload.get("matched", []):
        row = {
            "state": state,
            "chapter_url": node["url"],
            "chapter_label": node["label"],
            "chapter_slug": node.get("slug", ""),
        }
        if node.get("section_slug_pattern"):
            row["section_slug_pattern"] = node["section_slug_pattern"]
        if node.get("section_url_list"):
            row["section_url_list"] = node["section_url_list"]
        if node.get("pa_keep_sections"):
            row["pa_keep_sections"] = node["pa_keep_sections"]
        rows.append(row)
    return rows


def build_worklist(professions: set[str] | None) -> list[tuple[str, str, list[dict]]]:
    """Every (profession, state, rows) pair that lacks a healthy committed corpus.
    Ordered profession-major, state-sorted, so progress is legible in logs."""
    work: list[tuple[str, str, list[dict]]] = []
    for index_path in sorted(pt.PROFESSION_INDEX_DIR.glob("*.json")):
        name = index_path.stem
        if name.startswith("_"):
            continue
        if professions and name not in professions:
            continue
        index = json.loads(index_path.read_text())
        out_dir = pt.TEXT_DIR / name
        for state in sorted(index.get("by_state", {})):
            payload = index["by_state"][state]
            if not payload.get("matched"):
                continue
            out_path = out_dir / f"{state}.json"
            if out_path.exists() and _healthy(out_path):
                continue
            work.append((name, state, _rows_for_state(payload, state)))
    return work


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", default="",
                    help="Comma-separated subset (default: all indexed professions)")
    ap.add_argument("--max-minutes", type=float, default=300.0,
                    help="Wall-clock budget; stop cleanly and let a fresh runner continue")
    ap.add_argument("--block-threshold", type=int, default=6,
                    help="Consecutive states yielding 0 ok sections before declaring the IP "
                         "blocked and bailing for a fresh runner (0 = never bail on blocks)")
    ap.add_argument("--limit-sections", type=int, default=None,
                    help="Cap sections per state (debug)")
    args = ap.parse_args()

    professions = {p.strip().lower() for p in args.professions.split(",") if p.strip()} or None
    deadline = time.monotonic() + args.max_minutes * 60

    work = build_worklist(professions)
    if not work:
        log.info("worklist empty — every matched (profession, state) has a healthy corpus. Done.")
        return EXIT_DONE

    log.info("worklist: %d (profession, state) pairs to pull (budget %.0f min, block-threshold %d)",
             len(work), args.max_minutes, args.block_threshold)

    pulled = 0
    failed_states = 0
    consecutive_blocked = 0
    processed = 0

    for profession, state, rows in work:
        if time.monotonic() >= deadline:
            log.warning("time budget reached after %d states — %d pairs left for the next runner",
                        processed, len(work) - processed)
            return EXIT_WORK_REMAINS

        processed += 1
        try:
            corpus = pt.pull_state(state, profession, rows, args.limit_sections)
        except Exception as e:  # noqa: BLE001 — never let one state kill the run
            log.exception("[%s/%s] unhandled", profession, state)
            corpus = pt.StateCorpus(state=state, profession=profession, errors=[f"unhandled: {e}"])

        new_d = asdict(corpus)
        ok, chars = pt._corpus_health(new_d)

        if ok == 0:
            # Blocked / empty — do NOT write (keeps the pair on the worklist and
            # avoids a junk empty file). Count toward the consecutive-block trip.
            failed_states += 1
            consecutive_blocked += 1
            log.warning("  [%s/%s] 0 ok sections (blocked/empty) — not written (%d/%d consecutive)",
                        profession, state, consecutive_blocked, args.block_threshold)
            if args.block_threshold and consecutive_blocked >= args.block_threshold:
                log.error("hit %d consecutive blocked states — this IP looks banned. "
                          "Bailing for a fresh runner. %d pulled, %d pairs remain.",
                          consecutive_blocked, pulled, len(work) - processed)
                return EXIT_WORK_REMAINS
            continue

        consecutive_blocked = 0
        out_dir = pt.TEXT_DIR / profession
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{state}.json"

        # Overwrite-guard, identical to pull_text.main(): never let a worse pull
        # clobber a healthy committed corpus.
        if out_path.exists():
            try:
                old_d = json.loads(out_path.read_text())
            except Exception:
                old_d = {}
            reason = pt._is_regression(new_d, old_d)
            if reason:
                log.warning("  [%s/%s] SKIP overwrite: %s", profession, state, reason)
                continue

        out_path.write_text(json.dumps(new_d, indent=2))
        pulled += 1
        partial = sum(1 for s in corpus.sections if s.error)
        log.info("  [%s/%s] wrote sections=%d ok=%d chars=%d%s  (%d pulled / %d done of %d)",
                 profession, state, len(corpus.sections), ok, chars,
                 f" PARTIAL({partial} failed)" if partial else "",
                 pulled, processed, len(work))

    remaining = len(build_worklist(professions))
    log.info("run complete: %d pulled, %d blocked/empty this run, %d pairs still remaining",
             pulled, failed_states, remaining)
    return EXIT_DONE if remaining == 0 else EXIT_WORK_REMAINS


if __name__ == "__main__":
    sys.exit(main())
