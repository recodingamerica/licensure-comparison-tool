"""End-cleanup for the gap-harvest pull. Two defect classes are worth fixing; a short
real chapter is NOT a defect and is left alone.

  DEAD        — the pull stored Justia's 404 page as a 1-section "corpus"
                (text says "page not found"). The located URL is dead.
  WRONG_LEVEL — the locator returned a SECTION url (…/section-x) instead of the chapter,
                so only that one section came down. Re-locate at chapter level.

  python -m pipeline.discover.gap_harvest.cleanup                 # report defects
  python -m pipeline.discover.gap_harvest.cleanup --relocate      # + re-locate them (web_search)

Re-located URLs are written back into locator_results.json (via="relocate") and the bad
(profession, state) cells are listed in gap_harvest/relocate_worklist.json for re-pull.
"""
from __future__ import annotations
import argparse, json

from pipeline.paths import TEXT_DIR
from pipeline.config.loaders import load_professions
from pipeline.discover.gap_harvest import _common as C
from pipeline.discover.gap_harvest.locate import _run

_404 = ("page not found", "requested page could not be found")


def _sections(prof: str, state: str) -> list | None:
    f = TEXT_DIR / prof / f"{state}.json"
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text())
    except Exception:
        return []
    return d if isinstance(d, list) else d.get("sections", [])


def classify(prof: str, state: str, located_url: str | None) -> str:
    """'dead' | 'wrong_level' | 'good' | 'missing' for one pulled cell."""
    secs = _sections(prof, state)
    if secs is None:
        return "missing"
    head = (secs[0].get("text", "") if secs else "").lower()[:200]
    if not secs or any(k in head for k in _404):
        return "dead"
    if located_url and "/section-" in located_url and len(secs) <= 2:
        return "wrong_level"
    return "good"


def find_defects(results: dict) -> dict[str, list[tuple[str, str]]]:
    defects = {"dead": [], "wrong_level": []}
    for prof in results:
        for st, r in results[prof].items():
            url = r.get("url")
            if not url or url == "null":
                continue
            verdict = classify(prof, st, url)
            if verdict in defects:
                defects[verdict].append((prof, st))
    return defects


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--relocate", action="store_true",
                    help="re-locate the defective cells at chapter level (web_search)")
    args = ap.parse_args()

    results = C.load_json("locator_results.json", {})
    defects = find_defects(results)
    bad = defects["dead"] + defects["wrong_level"]
    print(f"defects: {len(defects['dead'])} dead(404-stored), "
          f"{len(defects['wrong_level'])} wrong-level  ({len(bad)} total)")
    for kind in ("dead", "wrong_level"):
        for prof, st in defects[kind][:20]:
            print(f"  {kind:11s} {prof}/{st}: {results[prof][st].get('url','')[-55:]}")

    C.save_json("relocate_worklist.json", [f"{p}/{s}" for p, s in bad])
    if args.relocate and bad:
        profs = load_professions()
        print(f"\nre-locating {len(bad)} cells at chapter level…")
        n = _run(bad, profs, mode="chapter", via="relocate", results=results, overwrite=True)
        print(f"re-located {n}/{len(bad)}. Re-pull these, then extract.")
    elif bad:
        print(f"\n{len(bad)} cells written to gap_harvest/relocate_worklist.json "
              f"(run with --relocate to fix).")


if __name__ == "__main__":
    main()
