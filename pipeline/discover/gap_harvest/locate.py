"""Search-driven locator — finds the Justia chapter for each (profession, state) via the
web_search tool (NO CDP). One CLI, three modes:

  # locate all Tier-3 likely-gap cells (default input: gap_harvest/tier3_absence.json)
  python -m pipeline.discover.gap_harvest.locate --gaps [--limit N]
  # re-check only the cells that came back null, with a looser prompt
  python -m pipeline.discover.gap_harvest.locate --recover-nulls
  # (re)locate specific cells, chapter-level (used by cleanup for dead/wrong-level)
  python -m pipeline.discover.gap_harvest.locate --profession pest_control --states CA,TX,NY

Results accumulate in gap_harvest/locator_results.json (checkpointed, resumable):
  {profession: {state: {url, label, confidence, via?}}}
"""
from __future__ import annotations
import argparse, json, threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from pipeline.config.loaders import load_professions
from pipeline.discover.gap_harvest import _common as C

RESULTS = "locator_results.json"
_lock = threading.Lock()


def _run(cells: list[tuple[str, str]], profs: dict, mode: str, via: str | None,
         results: dict, overwrite: bool) -> int:
    """Locate each (profession, state) cell concurrently, checkpointing as we go."""
    changed = 0

    def work(cell):
        prof, st = cell
        res = C.locate(prof, st, profs, mode=mode)
        if via and res.get("url"):
            res["via"] = via
        with _lock:
            if overwrite or res.get("url") not in (None, "null"):
                results.setdefault(prof, {})[st] = res
        return bool(res.get("url") and res["url"] != "null")

    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(work, c) for c in cells]
        for i, f in enumerate(as_completed(futs), 1):
            if f.result():
                changed += 1
            if i % 25 == 0:
                with _lock:
                    C.save_json(RESULTS, results)
    C.save_json(RESULTS, results)
    return changed


def _done(results: dict, prof: str, st: str) -> bool:
    return prof in results and st in results[prof]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--gaps", action="store_true", help="locate all Tier-3 likely-gap cells")
    g.add_argument("--recover-nulls", action="store_true",
                   help="re-check null cells with the looser 'addresses it' prompt")
    g.add_argument("--profession", help="(re)locate specific cells; needs --states")
    ap.add_argument("--states", help="comma-separated, with --profession")
    ap.add_argument("--mode", default=None, choices=list(C._PROMPTS),
                    help="override the prompt (default: strict for gaps, chapter for --profession)")
    ap.add_argument("--limit", type=int, default=0, help="cap cells processed this run")
    args = ap.parse_args()

    profs = load_professions()
    results = C.load_json(RESULTS, {})

    if args.gaps:
        gap = C.load_json("tier3_absence.json", {}).get("likely_gap", {})
        cells = [(p, st) for p in gap for st in gap[p] if not _done(results, p, st)]
        if args.limit:
            cells = cells[:args.limit]
        n = _run(cells, profs, args.mode or "strict", "gap_locator", results, overwrite=False)
        print(f"located {n}/{len(cells)} cells")
    elif args.recover_nulls:
        cells = [(p, st) for p in results for st, r in results[p].items()
                 if r.get("url") in (None, "null") and r.get("via") != "null_recovery"]
        if args.limit:
            cells = cells[:args.limit]
        n = _run(cells, profs, args.mode or "recover", "null_recovery", results, overwrite=False)
        print(f"recovered {n}/{len(cells)} chapters from nulls")
    else:
        if not args.states:
            ap.error("--profession requires --states")
        cells = [(args.profession, st) for st in args.states.split(",")]
        n = _run(cells, profs, args.mode or "chapter", "relocate", results, overwrite=True)
        print(f"located {n}/{len(cells)} cells for {args.profession}")

    still_null = sum(1 for p in results for r in results[p].values()
                     if r.get("url") in (None, "null"))
    located = sum(1 for p in results for r in results[p].values()
                  if r.get("url") and r["url"] != "null")
    multi = [(p, st) for p in results for st, r in results[p].items() if r.get("additional_urls")]
    print(f"totals: {located} located, {still_null} null → gap_harvest/{RESULTS}")
    if multi:
        print(f"⚠ {len(multi)} cells flagged possible multi-chapter (unverified, needs human review):")
        for p, st in multi[:20]:
            print(f"   {p}/{st}: {results[p][st]['additional_urls']}")


if __name__ == "__main__":
    main()
