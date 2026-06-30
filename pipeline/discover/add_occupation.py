"""ONE command to add an occupation end-to-end — the handoff capstone.

Chains the pieces we automated today into a single, checkpointed run:

  register (auto-draft + parent_corpus self-check)
    → [nested]    clean → trim → discover_schema → extract        (NO new Justia pull)
    → [standalone] match → pull_text → clean → trim → schema → extract
  → check_consistency
  → [--publish, if >=10 states] map_prep → bucket_text → build_frontend

A handler runs `add_occupation --from-candidate "Dental Hygienist" --write --publish`
and the tool does the rest, stopping with a clear message wherever a human decision is
genuinely required (a bad parent_corpus, a Justia pull, a failed stage). Idempotent:
each stage is a normal pipeline CLI, safe to re-run.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.add_occupation --from-candidate "Dental Hygienist"            # dry-run plan
  pipeline/.venv/bin/python -m pipeline.discover.add_occupation --from-candidate "Dental Hygienist" --write    # register + extract
  pipeline/.venv/bin/python -m pipeline.discover.add_occupation --from-candidate "Barber" --write --publish    # all the way to a payload
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

PY = sys.executable
ROOT = Path(__file__).resolve().parents[2]
PROF_YAML = CONFIG_DIR / "professions.yaml"
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


def add(name: str, from_candidate: bool, write: bool, publish: bool, states: str) -> None:
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
        print("\n  (dry-run) would register the above. Pass --write to proceed through the pipeline.")
        return

    # --- 2. corpus path ---
    if not parent:
        print("\n  STANDALONE occupation: needs its own Justia harvest. Next (manual, ops-gated):")
        print(f"    match_profession --profession {key}  →  pull_text --profession {key}")
        print("  Then re-run this with the corpus present. (Nested occupations skip all of this.)")
        return

    st = states or ",".join(_parent_states(parent))
    nstates = len(st.split(","))
    print(f"\n  NESTED path — extracting from text/{parent}/ ({nstates} states), no new pull")

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
    args = ap.parse_args()
    name = args.occupation or args.cand
    if not name:
        sys.exit("pass --occupation or --from-candidate")
    add(name, bool(args.cand), args.write, args.publish, args.states)


if __name__ == "__main__":
    main()
