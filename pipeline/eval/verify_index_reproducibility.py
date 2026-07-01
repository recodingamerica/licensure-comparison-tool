"""Acceptance gate: every committed results/profession_index/<prof>.json must be
reproducible from committed inputs alone — hierarchies + professions.yaml +
state_structure.yaml + mapping_overrides.yaml. No gitignored dirs, no hand edits.

Per profession: regenerate the index IN MEMORY (match_profession.build_index_for
with loaded mapping overrides) and compare against the committed file:
  - per state: multiset equality of matched nodes (identity =
    json.dumps(node, sort_keys=True)); list order ignored.
  - state-record `note` fields must match, EXCEPT the documented
    no_hierarchy→matched transition (a committed "no_hierarchy" stub whose state
    now gets override-only add nodes loses the note on regeneration).
  - top-level coverage.states_matched must match; other coverage keys ignored.
    Known exception: a few committed files carry a STALE states_matched counter
    (pre-refactor hand injections appended nodes without updating coverage). When
    every state's nodes+notes match and the counter derived from the committed
    by_state equals the regenerated one, this is warned, not failed.

Read-only — writes nothing. Exit 0 = reproducible, 1 = mismatch.

Run:
  pipeline/.venv/bin/python -m pipeline.eval.verify_index_reproducibility [--profession X]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

from pipeline.paths import HIERARCHY_DIR, PROFESSION_INDEX_DIR
from pipeline.discover.match_profession import build_index_for, load_professions, load_state_structure
from pipeline.discover._mapping_overrides import load_mapping_overrides


def _node_key(n: dict) -> str:
    return json.dumps(n, sort_keys=True)


def verify_profession(prof: str, defn: dict, hierarchies: dict, state_structure: dict,
                      mapping_overrides: dict) -> tuple[bool, list[str]]:
    """Returns (ok, warnings). Prints mismatch details itself."""
    committed = json.loads((PROFESSION_INDEX_DIR / f"{prof}.json").read_text())
    regen = build_index_for(prof, defn, hierarchies, state_structure, mapping_overrides)
    committed_by_state = committed.get("by_state") or {}
    regen_by_state = regen["by_state"]

    ok = True
    warnings: list[str] = []
    for st in sorted(set(committed_by_state) | set(regen_by_state)):
        c_rec = committed_by_state.get(st) or {}
        r_rec = regen_by_state.get(st) or {}
        c_nodes = c_rec.get("matched") or []
        r_nodes = r_rec.get("matched") or []
        c_ms = Counter(_node_key(n) for n in c_nodes)
        r_ms = Counter(_node_key(n) for n in r_nodes)
        if c_ms != r_ms:
            ok = False
            missing = c_ms - r_ms   # in committed, not regenerated
            added = r_ms - c_ms     # in regenerated, not committed
            print(f"MISMATCH {prof} {st}:")
            for key in missing:
                print(f"  committed-only: {json.loads(key).get('url')}")
            for key in added:
                print(f"  regenerated-only: {json.loads(key).get('url')}")
        c_note, r_note = c_rec.get("note"), r_rec.get("note")
        if c_note != r_note:
            # documented transition: committed "no_hierarchy" stub, state now
            # matched via override-only add nodes (regenerated drops the note).
            if c_note == "no_hierarchy" and r_note is None and r_nodes:
                warnings.append(f"{prof} {st}: no_hierarchy→matched transition (override-only state)")
            else:
                ok = False
                print(f"MISMATCH {prof} {st}: note committed={c_note!r} regenerated={r_note!r}")

    c_cov = (committed.get("coverage") or {}).get("states_matched")
    r_cov = regen["coverage"]["states_matched"]
    if c_cov != r_cov:
        derived = sum(1 for v in committed_by_state.values() if (v or {}).get("matched"))
        if ok and derived == r_cov:
            warnings.append(
                f"{prof}: STALE committed coverage.states_matched={c_cov} "
                f"(actual from committed by_state={derived}, regenerated={r_cov}) — "
                f"pre-refactor direct-JSON injection artifact; nodes fully reproducible")
        else:
            ok = False
            print(f"MISMATCH {prof}: coverage.states_matched committed={c_cov} regenerated={r_cov}")
    return ok, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="", help="If set, only verify this profession")
    args = ap.parse_args()

    professions = {k: v for k, v in load_professions().items() if not k.startswith("_")}
    if args.profession:
        if args.profession not in professions:
            sys.exit(f"profession not in registry: {args.profession}")
        professions = {args.profession: professions[args.profession]}

    hierarchies = {}
    for path in HIERARCHY_DIR.glob("*.json"):
        d = json.loads(path.read_text())
        hierarchies[d["state"]] = d
    state_structure = load_state_structure()
    mapping_overrides = load_mapping_overrides()

    n_ok = n_bad = n_skipped = 0
    all_warnings: list[str] = []
    for prof, defn in sorted(professions.items()):
        if not (PROFESSION_INDEX_DIR / f"{prof}.json").exists():
            n_skipped += 1
            continue
        ok, warnings = verify_profession(prof, defn, hierarchies, state_structure, mapping_overrides)
        all_warnings.extend(warnings)
        if ok:
            n_ok += 1
        else:
            n_bad += 1

    for w in all_warnings:
        print(f"⚠ {w}")
    print(f"\n{n_ok} profession(s) OK, {n_bad} mismatched, {n_skipped} without a committed index")
    return 1 if n_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
