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

# Match pull_text's import shim: put pipeline/ingest on the path so `import
# pull_text` resolves, and pipeline/ on the path so pull_text's `from paths
# import ...` resolves when it loads.

# Reuse the single-state machinery so corpus shape / fetch / guards stay identical.
import pipeline.ingest.pull_text as pt  # noqa: E402
from pipeline._records import record_files

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
    for index_path in record_files(pt.PROFESSION_INDEX_DIR):
        name = index_path.stem
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
    ap.add_argument("--limit-sections", type=int, default=500,
                    help="Per-state section cap (default 500). A RUNAWAY GUARD: a whole-title "
                         "over-match (e.g. a profession mapped to a 2500-section state-government "
                         "title) would otherwise pull for hours and bloat the corpus. A state that "
                         "hits the cap is logged loudly + flagged — not silently truncated. Pass 0 to "
                         "disable (only for a known-huge legitimate chapter).")
    ap.add_argument("--no-audit", action="store_true",
                    help="Skip the post-pull corpus-correctness audit (on by default; ~$0.02/state).")
    ap.add_argument("--gate", action="store_true",
                    help="Exit non-zero if the post-pull audit flags any freshly-pulled corpus as "
                         "wrong_chapter/empty (so a harvest can fail loudly on a bad pull).")
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
    pulled_by_prof: dict[str, list[str]] = {}
    section_cap = args.limit_sections or None  # 0 → disabled
    capped_states: list[str] = []

    for profession, state, rows in work:
        if time.monotonic() >= deadline:
            log.warning("time budget reached after %d states — %d pairs left for the next runner",
                        processed, len(work) - processed)
            return EXIT_WORK_REMAINS

        processed += 1
        try:
            corpus = pt.pull_state(state, profession, rows, section_cap)
            if section_cap and len(corpus.sections) >= section_cap:
                # Hit the runaway guard — almost always a whole-title over-match, not a
                # real chapter. Flag loudly so it's reviewed, not believed as coverage.
                log.warning("  ⚠ [%s/%s] hit the %d-section cap — likely a whole-title over-match; "
                            "FLAGGED for review (re-map to the specific chapter, don't trust this corpus)",
                            profession, state, section_cap)
                corpus.section_cap_hit = section_cap
                capped_states.append(f"{profession}/{state}")
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
        pulled_by_prof.setdefault(profession, []).append(state)
        partial = sum(1 for s in corpus.sections if s.error)
        log.info("  [%s/%s] wrote sections=%d ok=%d chars=%d%s  (%d pulled / %d done of %d)",
                 profession, state, len(corpus.sections), ok, chars,
                 f" PARTIAL({partial} failed)" if partial else "",
                 pulled, processed, len(work))

    remaining = len(build_worklist(professions))
    log.info("run complete: %d pulled, %d blocked/empty this run, %d pairs still remaining",
             pulled, failed_states, remaining)
    if capped_states:
        log.warning("%d state(s) hit the %d-section runaway cap — re-map to the specific chapter "
                    "before trusting: %s", len(capped_states), section_cap, ", ".join(capped_states))

    # Post-pull corpus-correctness gate: discovery keys on chapter titles, so a pull
    # can land on the wrong law (a criminal/procurement chapter, another profession,
    # a repealed shell) and still look "healthy" by section count. Verdict each
    # freshly-pulled corpus so a wrong-chapter pull is caught here, before clean →
    # trim → extract trust it. Only audits states pulled THIS run (bounded cost).
    bad_pulls: dict[str, list[str]] = {}
    if pulled_by_prof and not args.no_audit:
        from pipeline.discover.audit_corpus import audit_states  # local import: heavy deps
        for prof, sts in sorted(pulled_by_prof.items()):
            verdicts = audit_states(prof, sorted(sts))
            flagged = [s for s, v in verdicts.items() if v["verdict"] != "correct_licensure_text"]
            for s in flagged:
                log.warning("  AUDIT [%s/%s] %s — %s", prof, s,
                            verdicts[s]["verdict"], verdicts[s]["reason"][:90])
            if flagged:
                bad_pulls[prof] = sorted(flagged)
        if bad_pulls:
            log.error("post-pull audit flagged %d wrong/empty corpus pull(s): %s — re-discover the "
                      "right chapter (cross_ref_siblings / a state_structure override) before trusting them.",
                      sum(len(v) for v in bad_pulls.values()),
                      "; ".join(f"{p}: {','.join(s)}" for p, s in bad_pulls.items()))
        else:
            log.info("post-pull audit: all %d freshly-pulled corpora are correct licensure text.", pulled)

    if args.gate and bad_pulls:
        return EXIT_ERROR
    return EXIT_DONE if remaining == 0 else EXIT_WORK_REMAINS


if __name__ == "__main__":
    sys.exit(main())
