"""LLM-FREE sibling cross-reference by keyword density (#53).

The companion to `cross_ref_siblings.py` (which LLM-confirms). That LLM step has
false-NEGATIVES: it refused TN electrician even though the TN contractor corpus says
"limited licensed electrician" 39x. This version is deterministic — it greps a
sibling's already-pulled corpus for the trade's LICENSING terms and, if they appear
densely enough, wires `corpus_overrides.yaml` so clean_text reads the trade's text
from that sibling chapter. No fetch, no LLM.

Use it (a) when the API is capped, or (b) to catch the LLM cross-ref's misses. It is
deliberately conservative: it requires LICENSING phrases ("licensed electrician",
"electrical contractor"), not bare mentions, above a density threshold — a contractor
chapter that just name-drops "plumber" once won't trip it. The post-pull / pre-publish
gates still validate downstream.

Usage:
  python -m pipeline.discover.mechanical_cross_ref --profession electrician           # dry-run
  python -m pipeline.discover.mechanical_cross_ref --profession electrician --apply
  python -m pipeline.discover.mechanical_cross_ref --all-trades --apply
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
TEXT_DIR = REPO / "pipeline" / "results" / "text"
CONFIG_DIR = REPO / "pipeline" / "config"
OVERRIDES = CONFIG_DIR / "corpus_overrides.yaml"

ALL_STATES = set("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN "
                 "MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA "
                 "WA WV WI WY".split())

# Per-occupation: the LICENSING PHRASES that prove a sibling chapter actually regulates
# this occupation (deliberately specific — a passing mention doesn't count), and the
# SIBLING corpora most likely to hold the shared board/act, best first. Many occupations
# are licensed UNDER another board we already pulled: PAs/perfusionists under the medical
# act, midwives under nursing, surveyors under the PE board. This reuses that text — no
# fetch, no LLM. Extend freely; it's the LLM-free counterpart to cross_ref_siblings.
_TRADE_SIBS = ["construction_trades", "electrician", "plumbing", "hvac"]
CONFIG: dict[str, dict] = {
    # building trades — one contractor chapter often governs several
    "electrician": {"terms": ["licensed electrician", "electrical contractor", "limited licensed electrician",
                              "journeyman electrician", "master electrician"], "siblings": _TRADE_SIBS},
    "plumbing":    {"terms": ["licensed plumber", "plumbing contractor", "journeyman plumber",
                              "master plumber"], "siblings": _TRADE_SIBS},
    "hvac":        {"terms": ["hvac contractor", "mechanical contractor", "air conditioning contractor",
                              "refrigeration contractor", "hvacr"], "siblings": _TRADE_SIBS},
    # health professions licensed under the medical / nursing practice act
    "physician_assistant":       {"terms": ["physician assistant"], "siblings": ["medicine"]},
    "anesthesiologist_assistant": {"terms": ["anesthesiologist assistant"], "siblings": ["medicine"]},
    "perfusionist":              {"terms": ["perfusionist", "perfusion"], "siblings": ["medicine"]},
    "respiratory_care":          {"terms": ["respiratory therapist", "respiratory care practitioner"], "siblings": ["medicine"]},
    "genetic_counseling":        {"terms": ["genetic counselor"], "siblings": ["medicine"]},
    "polysomnography":           {"terms": ["polysomnographic technologist", "polysomnography"], "siblings": ["medicine", "respiratory_care"]},
    "nurse_midwifery":           {"terms": ["nurse-midwife", "certified nurse midwife", "nurse midwifery"], "siblings": ["nursing"]},
    # technical / design family — shared PE-surveyor-architect boards
    "land_surveying":            {"terms": ["land surveyor", "professional surveyor", "practice of surveying"],
                                  "siblings": ["professional_engineering", "architecture"]},
    "landscape_architecture":    {"terms": ["landscape architect"], "siblings": ["architecture", "professional_engineering"]},
}
DENSITY = 8  # total licensing-term hits in the sibling corpus to count as real coverage


def _corpus_text(profession: str, state: str) -> str:
    p = TEXT_DIR / profession / f"{state}.json"
    try:
        secs = json.loads(p.read_text()).get("sections", []) or []
    except (OSError, json.JSONDecodeError):
        return ""
    return " ".join(s.get("text", "") for s in secs if isinstance(s, dict))


def _have(profession: str, overrides: dict) -> set[str]:
    on_disk = {os.path.basename(f)[:-5] for f in glob.glob(str(TEXT_DIR / profession / "*.json"))
               if "_summary" not in f}
    return on_disk | set((overrides.get(profession) or {}).keys())


def find_links(profession: str, overrides: dict, terms: list[str], siblings: list[str]) -> dict[str, tuple[str, int]]:
    """For each blank state, the first sibling whose corpus covers this occupation densely."""
    blank = sorted(ALL_STATES - _have(profession, overrides))
    out: dict[str, tuple[str, int]] = {}
    for st in blank:
        for sib in siblings:
            if sib == profession:
                continue
            txt = _corpus_text(sib, st)
            if not txt:
                continue
            score = sum(len(re.findall(re.escape(t), txt, re.I)) for t in terms)
            if score >= DENSITY:
                out[st] = (sib, score)
                break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", help="one occupation key from CONFIG")
    ap.add_argument("--all", action="store_true", help="run every occupation in CONFIG")
    ap.add_argument("--all-trades", action="store_true", help="run electrician, plumbing, hvac")
    ap.add_argument("--siblings", help="comma-separated override of the sibling pool")
    ap.add_argument("--apply", action="store_true", help="write confirmed links to corpus_overrides.yaml")
    args = ap.parse_args()

    if args.all:
        profs = list(CONFIG)
    elif args.all_trades:
        profs = ["electrician", "plumbing", "hvac"]
    else:
        profs = [args.profession]
    if not profs or profs == [None]:
        return print("give --profession, --all-trades, or --all") or 2

    overrides = (yaml.safe_load(OVERRIDES.read_text()) if OVERRIDES.exists() else {}) or {}
    total = 0
    for prof in profs:
        if prof not in CONFIG:
            print(f"  {prof}: not in CONFIG (add its terms + siblings)"); continue
        terms = CONFIG[prof]["terms"]
        siblings = ([s.strip() for s in args.siblings.split(",")] if args.siblings else CONFIG[prof]["siblings"])
        links = find_links(prof, overrides, terms, siblings)
        for st, (sib, score) in links.items():
            print(f"  {prof}/{st} ← {sib}  ({score} licensing-term hits)")
        if links and args.apply:
            overrides.setdefault(prof, {}).update({st: sib for st, (sib, _) in links.items()})
        total += len(links)
    if args.apply and total:
        OVERRIDES.write_text("# Per-(profession, state) corpus reuse (cross_ref_siblings + mechanical_cross_ref).\n"
                             + yaml.safe_dump(overrides, default_flow_style=False, sort_keys=True))
        print(f"wrote {total} link(s) to {OVERRIDES.relative_to(REPO)}")
    elif total:
        print(f"\n{total} link(s) found — re-run with --apply to write them")
    else:
        print("no new mechanical cross-ref links found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
