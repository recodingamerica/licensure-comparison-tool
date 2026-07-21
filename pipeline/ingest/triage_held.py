"""Classify a refresh run's HELD (REGRESSION) cells so the post-run review is fast.

`refresh_corpus --review` builds an HTML page of the held candidates; this adds the
LLM-free triage that page doesn't: for each held cell it compares the committed corpus
(kept by the gate) against the rejected candidate on the gate's own key — the set of
error-free section CITATIONS — and buckets it into a clear action:

  FETCH_FLAKE  — candidate has fetch errors, or shares <30% of the committed citations
                 (it landed on the wrong page / a different article, or truncated). The
                 committed corpus is fine → RE-PULL; it usually resettles to NOCHANGE. A
                 flake that PERSISTS across a re-pull is a mapping problem (check the index).
  GROWTH       — candidate kept ~all committed citations AND added more: a MORE COMPLETE
                 pull the gate rejected over-conservatively → inspect, then ACCEPT (--apply).
  CHANGE       — candidate is the same chapter minus a few sections (high overlap, small
                 drop): a genuine repeal or a transient dropped section → re-pull to confirm;
                 if the drop is stable, ACCEPT it as a real change.

Nothing here fetches or writes — pure read over pending_review/<run-id>/ + results/text/.
No data is ever at risk: every held candidate was already reverted; this only decides what
to re-pull vs accept.

  python -m pipeline.ingest.triage_held --run-id annual2026 [--json]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from pipeline.paths import RESULTS_DIR, TEXT_DIR

FLAKE_OVERLAP = 0.30   # <30% of committed citations shared → wrong page / truncation
GROWTH_KEEP = 0.90     # kept ≥90% of committed citations …
# … and has more total → GROWTH; kept ≥GROWTH_KEEP but fewer → CHANGE.


def _citations(corpus: dict) -> set[str]:
    return {s.get("citation") for s in (corpus.get("sections") or [])
            if not s.get("error") and s.get("citation")}


def _errors(corpus: dict) -> int:
    return sum(1 for s in (corpus.get("sections") or []) if s.get("error"))


def triage(run_id: str) -> list[dict]:
    pending = RESULTS_DIR / "pending_review" / run_id
    if not pending.exists():
        return []
    out = []
    for f in sorted(pending.glob("*.json")):
        d = json.loads(f.read_text())
        prof, st = d["profession"], d["state"]
        cand = d.get("new_corpus", {})
        committed_path = TEXT_DIR / prof / f"{st}.json"
        committed = json.loads(committed_path.read_text()) if committed_path.exists() else {}

        cc, kc = _citations(committed), _citations(cand)
        overlap = len(cc & kc) / len(cc) if cc else 0.0
        cand_err = _errors(cand)

        if cand_err or overlap < FLAKE_OVERLAP:
            verdict, action = "FETCH_FLAKE", "re-pull (committed kept); persists → check the mapping"
        elif overlap >= GROWTH_KEEP and len(kc) > len(cc):
            verdict, action = "GROWTH", "inspect → --apply (candidate is more complete)"
        else:
            verdict, action = "CHANGE", "re-pull to confirm; stable drop → --apply (real repeal)"

        out.append({"cell": f"{prof}/{st}", "profession": prof, "state": st,
                    "committed": len(cc), "candidate": len(kc), "cand_errors": cand_err,
                    "overlap": round(overlap, 2), "verdict": verdict, "action": action})
    out.sort(key=lambda r: (r["verdict"], r["cell"]))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-id", required=True, help="run whose held cells to triage (e.g. annual2026)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args()

    rows = triage(args.run_id)
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print(f"no held cells for run {args.run_id!r} (pending_review/{args.run_id}/ empty or missing)")
        return
    print(f"{'verdict':<13}{'cell':<34}{'commit':>7}{'cand':>6}{'err':>5}{'overlap':>8}  action")
    print("-" * 118)
    for r in rows:
        print(f"{r['verdict']:<13}{r['cell']:<34}{r['committed']:>7}{r['candidate']:>6}"
              f"{r['cand_errors']:>5}{r['overlap']:>8.0%}  {r['action']}")
    print(f"\nsummary: {dict(Counter(r['verdict'] for r in rows))}   ({len(rows)} held)")
    print("Accept with:  python -m pipeline.ingest.refresh_corpus --apply --run-id "
          f"{args.run_id} --accept prof:ST,prof:ST")
    print("Re-pull with: python -m pipeline.ingest.refresh_corpus --profession <p> --states <ST>")


if __name__ == "__main__":
    main()
