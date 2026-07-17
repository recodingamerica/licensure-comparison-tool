"""Auto-draft a professions.yaml entry for an occupation (the registration step,
automated). Today registration is hand-written; this drafts it from a name — and,
crucially, derives `parent_corpus` so a nested occupation wires straight into the
no-new-pull path (see clean_text.corpus_profession_for + the handoff assessment).

Pairs with discover_occupations: pass `--from-candidate "Dental Hygienist"` and it
pulls the discovered `nested_in` to seed the parent. The LLM maps that free-text
parent ("Dentistry") to our tracked profession KEY (dentistry) and writes the entry.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.register_occupation --occupation "Dental Hygienist"
  pipeline/.venv/bin/python -m pipeline.discover.register_occupation --from-candidate "Barber" --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel

from pipeline._env import load_env
load_env()

from pipeline._llm import call_structured
from pipeline.paths import CONFIG_DIR, RESULTS_DIR, TEXT_DIR
from pipeline.config.loaders import load_professions
from pipeline.config.loaders import model_for

PROF_YAML = CONFIG_DIR / "professions.yaml"
CAND = RESULTS_DIR / "discover_occupations" / "_candidates.json"
MODEL = model_for("register_occupation")
FAMILIES = ["health", "building_design", "business", "public_safety"]


class Entry(BaseModel):
    key: str                     # snake_case profession key
    display: str
    family: str                  # one of FAMILIES
    patterns: list[str]          # lowercase substrings matching this occupation's chapter titles
    parent_corpus: str | None    # tracked profession KEY whose harvested chapters contain this
                                 # occupation's statutes (nested), else null
    reasoning: str


SYSTEM = f"""You draft one professions.yaml entry for a licensed occupation in a
state professional-licensing tool. Output:
- key: snake_case identifier (e.g. "dental_hygienist")
- display: human label
- family: EXACTLY one of {FAMILIES}
- patterns: lowercase substrings that match this occupation's statute CHAPTER titles
  (e.g. Dental Hygienist -> ["dental hygien"]; Barber -> ["barber"]). Specific, not generic.
- parent_corpus: if this occupation is regulated INSIDE a broader profession's statute
  chapters that we ALREADY TRACK (so its text lives in that profession's corpus and needs
  NO new fetch), the KEY of that tracked profession (e.g. dental_hygienist -> "dentistry",
  barber -> "cosmetology", pharmacy_technician -> "pharmacy"). Otherwise null.
- reasoning: one sentence.

You'll be given the occupation, an optional hint about where it was found nested, and the
list of tracked profession keys. parent_corpus MUST be one of the tracked keys or null."""


def tracked() -> dict:
    return load_professions()


def _parent_corpus_mentions(parent: str, patterns: list[str]) -> int:
    """How many of the parent's harvested-text states mention any of the patterns —
    the empirical check that this occupation's statutes really live in that corpus."""
    import glob
    pats = [p.lower() for p in patterns if p]
    hits = 0
    for f in glob.glob(str(TEXT_DIR / parent / "*.json")):
        if "_summary" in f:
            continue
        try:
            blob = Path(f).read_text().lower()
        except OSError:
            continue
        if any(p in blob for p in pats):
            hits += 1
    return hits


def candidate_nested(name: str) -> str | None:
    if not CAND.exists():
        return None
    for r in json.loads(CAND.read_text()):
        if r["occupation"].lower() == name.lower():
            return r.get("mostly_nested_in")
    return None


def draft(occupation: str, nested_hint: str | None) -> Entry:
    keys = [k for k in tracked() if not k.startswith("_")]
    hint = f"\nDiscovered nested inside (free text): {nested_hint}" if nested_hint else ""
    user = (f"OCCUPATION: {occupation}{hint}\n\nTRACKED PROFESSION KEYS ({len(keys)}):\n"
            + ", ".join(sorted(keys)))
    return call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=Entry,
                           embed_schema=True, log_prefix=f"[{occupation}]")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--occupation", help="occupation name to register")
    ap.add_argument("--from-candidate", help="occupation name; pulls nested_in from discovery candidates")
    ap.add_argument("--write", action="store_true", help="append to professions.yaml (default: dry-run)")
    args = ap.parse_args()

    name = args.occupation or args.from_candidate
    if not name:
        sys.exit("pass --occupation or --from-candidate")
    nested = candidate_nested(name) if args.from_candidate else None

    e = draft(name, nested)
    if e is None:
        sys.exit("LLM returned nothing — retry")

    conf = tracked()
    keys = {k for k in conf if not k.startswith("_")}
    warns = []
    if e.family not in FAMILIES:
        warns.append(f"family {e.family!r} not in {FAMILIES}")
    if e.parent_corpus and e.parent_corpus not in keys:
        warns.append(f"parent_corpus {e.parent_corpus!r} is not a tracked profession key")
    elif e.parent_corpus:
        # Self-check: does the parent's harvested text actually MENTION this occupation?
        # (How we confirmed dental_hygienist before trusting parent_corpus=dentistry.)
        hits = _parent_corpus_mentions(e.parent_corpus, e.patterns)
        if hits == 0:
            warns.append(f"parent_corpus {e.parent_corpus!r} text never matches {e.patterns} "
                         f"— likely the wrong parent (or it has its own chapter)")
        else:
            print(f"  ✓ parent_corpus check: {e.parent_corpus} text matches {e.patterns} in {hits} states")
    if e.key in keys:
        warns.append(f"key {e.key!r} already exists")

    entry = {"display": e.display, "family": [e.family], "patterns": e.patterns}
    if e.parent_corpus and e.parent_corpus in keys:
        entry["parent_corpus"] = e.parent_corpus
    print(f"\n=== drafted professions.yaml entry: {e.key} ===")
    print(yaml.safe_dump({e.key: entry}, sort_keys=False, allow_unicode=True), end="")
    print(f"  reasoning: {e.reasoning}")
    if entry.get("parent_corpus"):
        print(f"  → NESTED: cleans from text/{entry['parent_corpus']}/ — no new Justia pull")
    else:
        print("  → standalone: needs its own statute pull (match_profession + pull_text)")
    for w in warns:
        print(f"  ⚠ {w}")

    if args.write and not warns:
        conf[e.key] = entry
        yaml.safe_dump(conf, PROF_YAML.open("w"), sort_keys=False, allow_unicode=True, width=200)
        print(f"\n  WROTE {e.key} to {PROF_YAML}")
        nxt = (f"clean_text/trim_state/discover_schema/extract_state --profession {e.key}"
               if entry.get("parent_corpus")
               else f"match_profession + pull_text --profession {e.key}")
        print(f"  next: {nxt}")
    elif args.write:
        print("\n  NOT written — resolve the ⚠ warnings first")
    else:
        print("\n  (dry-run; pass --write to append)")


if __name__ == "__main__":
    main()
