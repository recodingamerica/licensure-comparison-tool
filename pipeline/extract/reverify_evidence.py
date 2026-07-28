"""Re-run the regex quote check against every Evidence in existing structured
records. Lets us tighten or loosen the matcher without paying for a full
Sonnet re-extraction.

For each state's structured record:
  1. Walk every Evidence-shaped node.
  2. Re-check `quote` against the corresponding state's trimmed corpus
     using the current `quote_in_corpus` implementation.
  3. Set / clear the `unverified` flag accordingly.
  4. Write back in place.

Usage:
  python -m pipeline.extract.reverify_evidence --profession podiatry
"""

from __future__ import annotations

import argparse
import json
import sys

from pipeline.extract.extract_state import annotate_evidence, load_umbrella_text  # noqa: E402
from pipeline.extract.locate_quote import normalize_for_match  # noqa: E402
from pipeline.paths import STRUCTURED_DIR, TRIMMED_DIR
from pipeline._records import record_files
from pipeline.extract.model_helpers import iter_quote_carriers, iter_evidence  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--report", action="store_true",
                    help="Do NOT write. Report, per cell, how many quotes no longer verify "
                         "against the CURRENT trimmed corpus — the test for whether a "
                         "re-clean/re-trim actually invalidated an extraction.")
    args = ap.parse_args()

    profession = args.profession.lower()
    structured_dir = STRUCTURED_DIR / profession
    trimmed_dir = TRIMMED_DIR / profession

    if not structured_dir.exists():
        sys.exit(f"missing {structured_dir}")

    overall_v = overall_u = 0
    newly_total = [0]
    states_changed = 0
    for path in record_files(structured_dir):
        record = json.loads(path.read_text())
        trim_path = trimmed_dir / f"{path.stem}.json"
        if not trim_path.exists():
            continue
        trim = json.loads(trim_path.read_text())
        text = "\n".join(s.get("text", "") for s in trim.get("sections", []))
        # Include the state's umbrella context if cached — extract_state
        # injects umbrella text at extraction time, so quotes pulled from
        # umbrella sections need to be verified against it too.
        umbrella = load_umbrella_text(path.stem)
        if umbrella:
            text = text + "\n" + umbrella
        normalized = normalize_for_match(text)

        # Which nodes were ALREADY failing before this re-check? Without that baseline
        # the report conflates "this quote never verified" with "the re-trim just broke
        # it", and only the second is a reason to re-extract.
        was_failing = {
            id(node) for _, node in iter_quote_carriers(record) if node.get("unverified")
        }
        # Strip stale unverified flags so we re-evaluate from scratch.
        # Must match what annotate_evidence walks, or a stale flag on a list item
        # would never be cleared on a later re-verify.
        for _, ev_node in iter_quote_carriers(record):
            ev_node.pop("unverified", None)

        v, u = annotate_evidence(record, normalized)
        # --report answers the question a hash cannot: an input CHANGED, but is the
        # extraction still VALID? If every quote is still present in the new corpus,
        # nothing was invalidated and the record stands — no re-extraction needed. Only
        # a quote that has gone missing means the extraction is describing text we no
        # longer have. (Surviving quotes prove nothing was LOST, not that nothing was
        # GAINED: a cell that grew may be under-extracted, which is a separate check.)
        if args.report:
            newly = sum(
                1 for _, node in iter_quote_carriers(record)
                if node.get("unverified") and id(node) not in was_failing
            )
            if newly:
                print(f"  [{path.stem}] {newly} quote(s) BROKEN by the re-trim "
                      f"({u} unverified in total) — re-extract")
            newly_total[0] += newly
        else:
            path.write_text(json.dumps(record, indent=2))
            print(f"  [{path.stem}] verified={v} unverified={u}")
        overall_v += v
        overall_u += u
        states_changed += 1

    total = overall_v + overall_u
    pct = (100 * overall_v / total) if total else 0.0
    print(f"\n{profession}: {overall_v}/{total} verified ({pct:.1f}%) across {states_changed} states")
    if args.report:
        print(f"{profession}: {newly_total[0]} quote(s) newly broken by the current corpus "
              f"— cells above need re-extraction; the rest stand.")


if __name__ == "__main__":
    main()
