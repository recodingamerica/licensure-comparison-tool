"""Discover licensed occupations we DON'T yet track — including ones HIDING inside
another occupation's chapter (the PM's "occupations hiding in other occupations").

Today, deciding which occupations exist is manual (someone reads code indexes and
writes professions.yaml patterns). This automates the discovery half: an LLM reads
each state's chapter/article titles, compares against the tracked list, and surfaces
regulated occupations that are missing — flagging sub-licenses bundled inside a
broader act (Cosmetology "and Associated Professions" → barber/esthetician/nail tech;
a Dental Practice Act → dental hygienist; an EMS Act → EMT/paramedic).

Per-state results -> results/discover_occupations/<STATE>.json. The `aggregate`
command rolls them into a frequency-ranked candidate list: occupations regulated in
the most states (but untracked) are the highest-value adds.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.discover_occupations --states UT,CA   # a few
  pipeline/.venv/bin/python -m pipeline.discover.discover_occupations                  # all states
  pipeline/.venv/bin/python -m pipeline.discover.discover_occupations aggregate        # rank candidates
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml
from pydantic import BaseModel

from pipeline._env import load_env
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _llm import call_structured, usage_summary  # noqa: E402
from paths import RESULTS_DIR, CONFIG_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402

HIER_DIR = RESULTS_DIR / "hierarchy"
OUT_DIR = RESULTS_DIR / "discover_occupations"
MODEL = "claude-sonnet-4-6"


class Occupation(BaseModel):
    name: str                    # the occupation (e.g. "Dental Hygienist")
    chapter_label: str           # statute chapter/article it appears under
    nested_in: str | None        # broader profession's act it hides inside, else null
    confidence: str              # high | medium | low


class DiscoveryResult(BaseModel):
    untracked_occupations: list[Occupation]


SYSTEM = """You find LICENSED/REGULATED OCCUPATIONS named in statute chapter titles.
Given a state's chapter/article titles and a list of occupations ALREADY tracked,
identify regulated occupations that are NOT already tracked — ESPECIALLY ones HIDING
inside a broader chapter (e.g. a "Cosmetology and Associated Professions" act also
licenses barbers, estheticians, nail technicians, electrologists; a Dental Practice
Act also licenses dental hygienists; an EMS act licenses EMTs and paramedics; a
medical practice act may license anesthesiologist assistants).

Only list occupations a person needs a state CREDENTIAL (license / registration /
certification) to practice. Skip facility/business licenses, boards/divisions/funds/
programs, and non-occupational chapters. Don't restate an already-tracked occupation.
For each: the occupation name (singular, generic — "Barber" not "Barbers"), the
chapter title it appears under, and if nested inside a broader profession's act, the
name of that broader profession (else null). confidence = how sure you are it's a
distinct licensed occupation."""


def _norm(name: str) -> str:
    n = re.sub(r"[^a-z0-9 ]", "", name.lower()).strip()
    n = re.sub(r"\s+", " ", n)
    return n[:-1] if n.endswith("s") and not n.endswith("ss") else n  # crude singularize


def tracked_professions() -> list[str]:
    d = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text())
    return sorted(k for k in d if not k.startswith("_"))


def discover_state(state: str, tracked: list[str], *, skip_existing: bool = True) -> DiscoveryResult | None:
    out_fp = OUT_DIR / f"{state}.json"
    if skip_existing and out_fp.exists():
        print(f"  {state}: already done, skipping"); return None
    fp = HIER_DIR / f"{state}.json"
    if not fp.exists():
        print(f"  {state}: no hierarchy"); return None
    labels = sorted({c.get("label", "") for c in json.loads(fp.read_text()).get("chapters", []) if c.get("label")})
    if not labels:
        return None
    user = (f"STATE: {state}\n\nALREADY TRACKED ({len(tracked)}): {', '.join(tracked)}\n\n"
            f"CHAPTER/ARTICLE TITLES:\n" + "\n".join(labels))
    res = call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=DiscoveryResult,
                          embed_schema=True, log_prefix=f"[{state}]")
    if res is None:  # transient API/schema failure — don't crash the whole sweep, retry next run
        print(f"  {state}: LLM call returned nothing — skipping (re-run to retry)"); return None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_fp.write_text(res.model_dump_json(indent=1))
    nested = sum(1 for o in res.untracked_occupations if o.nested_in)
    print(f"  {state}: {len(res.untracked_occupations)} untracked ({nested} nested inside other acts)")
    return res


def aggregate() -> None:
    """Roll per-state results into a frequency-ranked candidate list."""
    by_occ: dict[str, dict] = defaultdict(lambda: {"states": set(), "nested_in": defaultdict(int),
                                                    "names": defaultdict(int), "conf": defaultdict(int)})
    for fp in sorted(OUT_DIR.glob("*.json")):
        if fp.stem == "_candidates":
            continue
        st = fp.stem
        for o in json.loads(fp.read_text()).get("untracked_occupations", []):
            rec = by_occ[_norm(o["name"])]
            rec["states"].add(st)
            rec["names"][o["name"]] += 1
            rec["conf"][o.get("confidence", "?")] += 1
            if o.get("nested_in"):
                rec["nested_in"][o["nested_in"]] += 1
    ranked = sorted(by_occ.items(), key=lambda kv: len(kv[1]["states"]), reverse=True)
    out = []
    for norm, rec in ranked:
        disp = max(rec["names"].items(), key=lambda kv: kv[1])[0]
        nested = max(rec["nested_in"].items(), key=lambda kv: kv[1])[0] if rec["nested_in"] else None
        out.append({"occupation": disp, "n_states": len(rec["states"]),
                    "states": sorted(rec["states"]), "mostly_nested_in": nested,
                    "nested_state_count": sum(rec["nested_in"].values())})
    (OUT_DIR / "_candidates.json").write_text(json.dumps(out, indent=1))
    print(f"\n=== {len(out)} distinct untracked occupations across {len(list(OUT_DIR.glob('*.json'))) - 1} states ===")
    for r in out[:40]:
        tag = f"  [usually nested in {r['mostly_nested_in']}]" if r["mostly_nested_in"] else ""
        print(f"  {r['n_states']:2} states  {r['occupation']}{tag}")
    print(f"\nwrote {OUT_DIR / '_candidates.json'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", default="discover", choices=["discover", "aggregate"])
    ap.add_argument("--states", default="")
    args = ap.parse_args()
    if args.mode == "aggregate":
        aggregate(); return
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()] or list(ALL_STATES)
    tracked = tracked_professions()
    for st in states:
        discover_state(st, tracked)
    usage_summary()
    print(f"\nnext: pipeline/.venv/bin/python -m pipeline.discover.discover_occupations aggregate")


if __name__ == "__main__":
    main()
