"""ONE command to add an occupation end-to-end — the handoff capstone.

Chains the pieces we automated into a single, checkpointed run. The core idea is a
COMPLETENESS-FIRST corpus plan rather than a binary standalone/nested route: a state
is extractable if its text lives ANYWHERE on disk (own corpus, a global parent_corpus,
or a per-state corpus_override), and the density scan (mechanical_cross_ref) surfaces
sibling chapters register's LLM never sees. That plan sorts every state into three
buckets so the tool can't silently ship an "80%-ok" occupation:

  register (auto-draft parent_corpus)
  → corpus_plan:  extract-now   (text already on disk — own | parent | override)
                  review-first  (density-scan candidates; --apply-cross-ref to wire them)
                  needs-pull    (no text anywhere — a Justia harvest is genuinely required)
  → clean → trim → discover_schema → extract   (over ALL extract-now states, no new pull)
  → check_consistency
  → [--publish, if >=10 states] map_prep → bucket_text → build_frontend

A handler runs `add_occupation --from-candidate "Dental Hygienist" --write --publish`
and the tool does the rest, stopping with a clear message wherever a human decision is
genuinely required (unreviewed cross-ref candidates, a needed pull, a failed stage).
Idempotent: each stage is a normal pipeline CLI, safe to re-run.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.add_occupation --from-candidate "Public Adjuster"                 # dry-run plan (3 buckets)
  pipeline/.venv/bin/python -m pipeline.discover.add_occupation --from-candidate "Public Adjuster" --apply-cross-ref --write
  pipeline/.venv/bin/python -m pipeline.discover.add_occupation --from-candidate "Barber" --write --publish        # all the way to a payload
"""
from __future__ import annotations

import argparse
import glob
import os
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import CONFIG_DIR, TEXT_DIR, STRUCTURED_DIR  # noqa: E402
from discover import register_occupation as reg  # noqa: E402
from discover import mechanical_cross_ref as xref  # noqa: E402

PY = sys.executable
ROOT = Path(__file__).resolve().parents[2]
PROF_YAML = CONFIG_DIR / "professions.yaml"
OVERRIDES = CONFIG_DIR / "corpus_overrides.yaml"
MIN_PUBLISH = 10  # core_professions() threshold


def _run(mod_args: list[str], desc: str) -> bool:
    print(f"\n▶ {desc}\n  $ python -m {' '.join(mod_args)}")
    r = subprocess.run([PY, "-m", *mod_args], cwd=ROOT)
    ok = r.returncode == 0
    print(f"  {'✓' if ok else '✗ FAILED'} {desc}")
    return ok


def _parent_states(parent: str) -> list[str]:
    return sorted(os.path.basename(f)[:-5]
                  for f in glob.glob(str(TEXT_DIR / parent / "*.json"))
                  if "_summary" not in f)


def _n_structured(prof: str) -> int:
    return len([f for f in glob.glob(str(STRUCTURED_DIR / prof / "*.json"))
               if "_summary" not in f])


def _load_overrides() -> dict:
    return (yaml.safe_load(OVERRIDES.read_text()) if OVERRIDES.exists() else {}) or {}


def corpus_plan(key: str, patterns: list[str], parent: str | None) -> dict:
    """Per-state availability plan — the completeness backbone. A state is
    EXTRACTABLE if its text already lives somewhere on disk (own corpus, a global
    parent_corpus, or a per-state corpus_override). Anything the density scan finds
    beyond that is a CANDIDATE that needs a human OK before we trust it; whatever's
    left is genuinely blank and needs a Justia pull. This is what stops the tool from
    silently shipping an 80%-ok occupation: available text is never left unextracted,
    and an unreviewed mapping is never silently applied."""
    ov = _load_overrides()
    own = set(_parent_states(key))                       # own pulled corpus
    overridden = set((ov.get(key) or {}).keys())         # per-state siblings already wired
    parent_states = set(_parent_states(parent)) if parent else set()  # global parent_corpus
    extractable = own | overridden | parent_states
    # Density scan — the signal register's LLM never consults. brute_force_links
    # already skips states we _have (own+override); also drop any covered by a global
    # parent so we only surface genuinely-new sibling links.
    pool = xref._all_occupations()
    density = xref.brute_force_links(key, ov, patterns, pool, xref.DENSITY)
    candidates = {st: v for st, v in density.items() if st not in extractable}
    blank = set(xref.ALL_STATES) - extractable - set(candidates)
    return {"ov": ov, "own": own, "overridden": overridden, "parent_states": parent_states,
            "extractable": extractable, "candidates": candidates, "blank": blank}


def _apply_candidates(key: str, ov: dict, candidates: dict) -> None:
    """Write density-scan candidates into corpus_overrides.yaml (opt-in, --apply-cross-ref)."""
    ov.setdefault(key, {}).update({st: sib for st, (sib, _) in candidates.items()})
    OVERRIDES.write_text(
        "# Per-(profession, state) corpus reuse (cross_ref_siblings + mechanical_cross_ref).\n"
        + yaml.safe_dump(ov, default_flow_style=False, sort_keys=True))
    print(f"  ✓ applied {len(candidates)} cross-ref link(s) to {OVERRIDES.name}")


def add(name: str, from_candidate: bool, write: bool, publish: bool, states: str,
        apply_cross_ref: bool = False) -> None:
    # --- 1. register (auto-draft + self-validating parent_corpus) ---
    print(f"=== add_occupation: {name} ===")
    nested_hint = reg.candidate_nested(name) if from_candidate else None
    entry_model = reg.draft(name, nested_hint)
    if entry_model is None:
        sys.exit("register: LLM returned nothing — retry")
    conf = reg.tracked()
    keys = {k for k in conf if not k.startswith("_")}
    key = entry_model.key
    parent = entry_model.parent_corpus if entry_model.parent_corpus in keys else None

    # validate parent_corpus against real text (the gate for the no-pull path)
    if parent:
        hits = reg._parent_corpus_mentions(parent, entry_model.patterns)
        print(f"  parent_corpus={parent}: text matches {entry_model.patterns} in {hits} states")
        if hits == 0:
            sys.exit(f"  ✗ parent_corpus {parent!r} never matches — wrong parent. Stop & review.")
    print(f"  key={key}  family={entry_model.family}  parent={parent or '(standalone — needs Justia pull)'}")

    if key in keys:
        print(f"  (key {key} already registered — continuing with existing entry)")
    elif write:
        entry = {"display": entry_model.display, "family": [entry_model.family],
                 "patterns": entry_model.patterns}
        if parent:
            entry["parent_corpus"] = parent
        conf[key] = entry
        yaml.safe_dump(conf, PROF_YAML.open("w"), sort_keys=False, allow_unicode=True, width=200)
        print(f"  ✓ registered {key} in professions.yaml")
    else:
        print("  (dry-run) would register the above (pass --write to persist + extract).")

    # --- 2. corpus plan (per-state: own + global parent + per-state override + density scan) ---
    plan = corpus_plan(key, entry_model.patterns, parent)
    ov, extractable, candidates, blank = (plan["ov"], plan["extractable"],
                                          plan["candidates"], plan["blank"])
    print(f"\n  corpus plan for {key}:")
    print(f"    extract now : {len(extractable):>2} states "
          f"(own {len(plan['own'])}, parent {len(plan['parent_states'])}, override {len(plan['overridden'])})")
    print(f"    review first: {len(candidates):>2} density-scan candidate(s)")
    print(f"    needs pull  : {len(blank):>2} state(s) with no text anywhere")

    if candidates:
        for st_, (sib, score) in sorted(candidates.items()):
            print(f"      ? {st_} ← {sib}  ({score} pattern hits)")
        if apply_cross_ref:
            _apply_candidates(key, ov, candidates)
            extractable = extractable | set(candidates)
        else:
            print("      → eyeball these; re-run with --apply-cross-ref to wire + extract them")

    if not extractable:
        print("\n  No text on disk for any state. STANDALONE — needs a Justia harvest first:")
        print(f"    match_profession --profession {key}  →  pull_text --profession {key}")
        print("  Then re-run. (Or --apply-cross-ref above if the candidates look right.)")
        return

    if not write:
        print(f"\n  (dry-run) would extract {len(extractable)} state(s). Pass --write to proceed.")
        return

    st = states or ",".join(sorted(extractable))
    print(f"\n  extracting {len(st.split(','))} state(s) via clean→trim→schema→extract (no new pull)")

    # --- 3. clean → trim → schema → extract ---
    if not _run(["pipeline.ingest.clean_text", "--profession", key, "--states", st], "clean_text"):
        sys.exit("stop: clean failed")
    if not _run(["pipeline.ingest.trim_state", "--profession", key, "--states", st], "trim_state"):
        sys.exit("stop: trim failed")
    if not _run(["pipeline.extract.discover_schema", "--profession", key], "discover_schema"):
        sys.exit("stop: schema failed")
    if not _run(["pipeline.extract.extract_state", "--profession", key, "--states", st, "--force"], "extract_state"):
        sys.exit("stop: extract failed")

    # --- 4. consistency gate ---
    _run(["pipeline.eval.check_consistency"], "check_consistency")
    n = _n_structured(key)
    print(f"\n  {key}: {n} structured records")

    # --- 5. publish (optional, if core-eligible) ---
    if publish and n >= MIN_PUBLISH:
        for mod, desc in [
            (["pipeline.map_prep.run", key], "map_prep"),
            (["pipeline.map_prep.bucket_text", key], "bucket_text"),
            (["pipeline.publish.build_frontend", "--profession", key], "build_frontend"),
        ]:
            _run(mod, desc)
        print(f"\n=== DONE: {key} built ({n} states). Add to build_state_browse.PROFESSIONS + deploy to go fully live. ===")
    elif publish:
        print(f"\n=== {key}: {n} states (<{MIN_PUBLISH}) — extracted but not auto-published (not core-eligible yet). ===")
    else:
        print(f"\n=== {key}: extracted ({n} states). Re-run with --publish to build the payload. ===")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--occupation")
    ap.add_argument("--from-candidate", dest="cand")
    ap.add_argument("--states", default="", help="subset; default = all parent-corpus states")
    ap.add_argument("--write", action="store_true", help="actually register + run (default: dry-run plan)")
    ap.add_argument("--publish", action="store_true", help="also build the frontend payload if >=10 states")
    ap.add_argument("--apply-cross-ref", action="store_true",
                    help="wire the density-scan candidate links into corpus_overrides.yaml and "
                         "extract them too (default: surface for review, don't apply)")
    args = ap.parse_args()
    name = args.occupation or args.cand
    if not name:
        sys.exit("pass --occupation or --from-candidate")
    add(name, bool(args.cand), args.write, args.publish, args.states, args.apply_cross_ref)


if __name__ == "__main__":
    main()
