"""Promote locator_results.json URLs into profession_index/<prof>.json's `matched`
list -- the missing link between the web-search locator and the pull tools.

refresh_corpus / pull_text ONLY read chapter targets from profession_index's frozen
`matched` list (see refresh_corpus.py's build_worklist / pull_text.py's main). The
gap-harvest locator (locate.py) writes URLs to a completely separate file,
locator_results.json, that nothing else reads. A cell can be "located" there forever
without ever being pullable -- the pull stages will silently no-op on it,
producing an empty result every single time (discovered 2026-07-07: 128 of 134 queued
gap-harvest cells had a locator URL but no profession_index mapping, so an entire
worklist pass did nothing).

This writes the located {url, label} into `matched` ONLY where the state's `matched`
list is currently empty (never overwrites an existing real mapping) and no local
corpus already exists. It does not fetch anything -- the next pull does that, and can do
so safely: pull_text's over-broad guard (opt-in via PULL_BATCH_TIMEOUT_SECONDS) will
skip-and-flag anything too large to fetch within that per-cell timeout, regardless of
label match.

  python -m pipeline.discover.gap_harvest.promote [--via null_recovery] [--dry-run]
"""
from __future__ import annotations
import argparse, json

from pipeline.paths import PROFESSION_INDEX_DIR, TEXT_DIR
from pipeline.discover.gap_harvest import _common as C


def _has_corpus(prof: str, state: str) -> bool:
    f = TEXT_DIR / prof / f"{state}.json"
    if not f.exists():
        return False
    try:
        d = json.loads(f.read_text())
    except Exception:
        return False
    secs = d if isinstance(d, list) else d.get("sections", [])
    return len(secs) > 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--via", default=None,
                     help="Only promote locator entries with this 'via' tag (e.g. null_recovery).")
    ap.add_argument("--dry-run", action="store_true", help="Report what would change; write nothing.")
    args = ap.parse_args()

    locator = C.load_json("locator_results.json", {})
    # A hand-verified absence is a correct-blank: the state doesn't license this
    # occupation, and the locator's URL is a mis-location to a thematically-adjacent
    # chapter. Promoting it would make a wrong target look pullable (and re-appear as
    # a fetch gap every run). Skip these — the same class of noise status.build() now
    # filters. (2026-07-10: gap-harvest triage found 23 of 57 promoted cells were
    # verified absences.)
    from pipeline.config.loaders import load_verified_absences
    absences = load_verified_absences()
    promoted = []
    skipped_has_mapping = 0
    skipped_has_corpus = 0
    skipped_absence = 0

    for prof, states in locator.items():
        idx_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        idx = json.loads(idx_path.read_text()) if idx_path.exists() else {"by_state": {}}
        prof_absences = absences.get(prof) or {}
        changed = False
        for st, r in states.items():
            url = r.get("url")
            if not url or url == "null":
                continue
            if args.via and r.get("via") != args.via:
                continue
            if st in prof_absences:
                skipped_absence += 1
                continue
            if _has_corpus(prof, st):
                skipped_has_corpus += 1
                continue
            entry = idx["by_state"].setdefault(st, {"matched": []})
            if entry.get("matched"):
                skipped_has_mapping += 1
                continue
            entry["matched"] = [{"url": url, "label": r.get("label", "")}]
            promoted.append((prof, st))
            changed = True
        if changed and not args.dry_run:
            idx_path.parent.mkdir(parents=True, exist_ok=True)
            idx_path.write_text(json.dumps(idx, indent=1))

    print(f"{'would promote' if args.dry_run else 'promoted'} {len(promoted)} cells "
          f"across {len({p for p, _ in promoted})} professions into profession_index")
    print(f"  skipped {skipped_has_mapping} (already mapped), "
          f"{skipped_has_corpus} (already have a corpus), "
          f"{skipped_absence} (verified absence)")


if __name__ == "__main__":
    main()
