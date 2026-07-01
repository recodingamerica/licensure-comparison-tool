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

There are two modes:
  - CONFIG mode (default): hand-curated licensing phrases + a curated sibling pool.
    Conservative, high-precision; the entries below were verified.
  - BRUTE-FORCE mode (--brute-force): no CONFIG needed — uses the occupation's own
    professions.yaml label patterns and scans EVERY pulled corpus, picking the
    densest-matching sibling per blank state. Auto-discovers shared-board links
    nobody configured (e.g. public_adjuster licensed under the insurance code,
    prosthetist_orthotist co-located with podiatry). Output is always a review
    CANDIDATE — the density threshold filters most noise but not all, so eyeball
    each before --apply.

Usage:
  python -m pipeline.discover.mechanical_cross_ref --profession electrician           # dry-run
  python -m pipeline.discover.mechanical_cross_ref --profession electrician --apply
  python -m pipeline.discover.mechanical_cross_ref --all-trades --apply
  python -m pipeline.discover.mechanical_cross_ref --profession public_adjuster --brute-force
  python -m pipeline.discover.mechanical_cross_ref --profession public_adjuster --brute-force --apply
"""
from __future__ import annotations

import argparse
import functools
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

from pipeline.config.loaders import load_professions, load_corpus_overrides

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
    "perfusionist":              {"terms": ["perfusionist", "perfusion"], "siblings": ["medicine", "respiratory_care"]},
    "respiratory_care":          {"terms": ["respiratory therapist", "respiratory care practitioner"], "siblings": ["medicine"]},
    "genetic_counseling":        {"terms": ["genetic counselor"], "siblings": ["medicine"]},
    "polysomnography":           {"terms": ["polysomnographic technologist", "polysomnography"], "siblings": ["medicine", "respiratory_care"]},
    "nurse_midwifery":           {"terms": ["nurse-midwife", "certified nurse midwife", "nurse midwifery"], "siblings": ["nursing"]},
    # technical / design family — shared PE-surveyor-architect boards
    "land_surveying":            {"terms": ["land surveyor", "professional surveyor", "practice of surveying"],
                                  "siblings": ["professional_engineering", "architecture"]},
    "landscape_architecture":    {"terms": ["landscape architect"], "siblings": ["architecture", "professional_engineering"]},
    "professional_geology":      {"terms": ["professional geologist", "licensed geologist", "practice of geology"],
                                  "siblings": ["professional_engineering", "soil_classifier"]},
    "soil_classifier":           {"terms": ["soil classifier", "soil scientist"], "siblings": ["professional_geology", "professional_engineering"]},
    # more health professions licensed under a board we already pulled
    "osteopathic_medicine":      {"terms": ["osteopathic physician", "doctor of osteopathy", "practice of osteopathy"], "siblings": ["medicine"]},
    "naturopathic_medicine":     {"terms": ["naturopathic physician", "naturopathic doctor", "practice of naturopathic"], "siblings": ["medicine"]},
    "direct_entry_midwifery":    {"terms": ["certified professional midwife", "licensed midwife", "direct-entry midwife", "lay midwife"], "siblings": ["nursing", "nurse_midwifery"]},
    "opticianry":                {"terms": ["dispensing optician", "licensed optician", "ophthalmic dispenser"], "siblings": ["optometry"]},
    "hearing_instrument_specialist": {"terms": ["hearing aid dealer", "hearing instrument specialist", "hearing aid dispenser"], "siblings": ["speech_language_audiology"]},
    "applied_behavior_analysis": {"terms": ["behavior analyst", "applied behavior analysis"], "siblings": ["psychology"]},
    "alcohol_drug_counseling":   {"terms": ["alcohol and drug counselor", "substance abuse counselor", "addiction counselor", "chemical dependency counselor"],
                                  "siblings": ["mental_health_counseling", "social_work", "psychology"]},
    # more shared-board candidates (density self-filters the separate-board ones)
    "electrology":               {"terms": ["electrologist", "electrolysis"], "siblings": ["cosmetology"]},
    "radiologic_technology":     {"terms": ["radiologic technologist", "radiographer", "radiation therapist"], "siblings": ["medicine"]},
    "athletic_training":         {"terms": ["athletic trainer", "athletic training"], "siblings": ["medicine"]},
    "private_investigator":      {"terms": ["private investigator", "private detective"], "siblings": ["security_personnel"]},
    "security_personnel":        {"terms": ["security guard", "security officer", "private security"], "siblings": ["private_investigator"]},
    "home_inspector":            {"terms": ["home inspector", "home inspection"], "siblings": ["construction_trades", "building_inspector"]},
    "public_adjuster":           {"terms": ["public adjuster", "public insurance adjuster"], "siblings": ["insurance_producer"]},
    "commercial_interior_design": {"terms": ["interior designer", "interior design"], "siblings": ["architecture"]},
    # speculative — separate-board ones self-filter to nothing via the density threshold
    "real_estate_appraiser":     {"terms": ["real estate appraiser", "certified appraiser"], "siblings": ["real_estate_broker"]},
    "surgical_technologist":     {"terms": ["surgical technologist", "surgical technician"], "siblings": ["nursing", "medicine"]},
    "recreational_therapy":      {"terms": ["recreational therapist", "recreation therapy"], "siblings": ["occupational_therapy"]},
    "prosthetist_orthotist":     {"terms": ["prosthetist", "orthotist", "prosthetics and orthotics"], "siblings": ["medicine"]},
    "music_therapy":             {"terms": ["music therapist", "music therapy"], "siblings": ["mental_health_counseling", "occupational_therapy"]},
}
DENSITY = 8  # total licensing-term hits in the sibling corpus to count as real coverage


@functools.lru_cache(maxsize=None)
def _corpus_text(profession: str, state: str) -> str:
    # Cached: --all-brute reads each sibling corpus once across every target
    # occupation instead of re-parsing it per occupation. Corpora don't change
    # mid-run, so the cache is always valid.
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


# --- Brute-force mode: no hand-curated CONFIG, scan EVERY pulled corpus ---------
# Where find_links uses a curated sibling pool + hand-picked licensing phrases,
# brute-force uses the occupation's own professions.yaml label patterns as the
# search terms and greps ALL other pulled corpora. It auto-discovers shared-board
# links nobody configured (e.g. a contractor act that licenses plumbers). The
# density threshold self-filters bare-noun noise — a corpus that merely name-drops
# the occupation stays well under it; one that regulates it clears it. Output is
# always a REVIEW candidate (best-scoring sibling per state), never auto-trusted.

def _all_occupations() -> list[str]:
    """Every occupation that has a pulled corpus dir under results/text/."""
    return sorted(d.name for d in TEXT_DIR.iterdir()
                  if d.is_dir() and not d.name.startswith("_"))


def load_patterns(profession: str) -> list[str]:
    """The occupation's label-match patterns from professions.yaml ([] if absent)."""
    defs = load_professions()
    return list((defs.get(profession) or {}).get("patterns") or [])


def incomplete_occupations(overrides: dict) -> list[str]:
    """Every professions.yaml occupation with patterns AND at least one blank state."""
    defs = load_professions()
    out = [occ for occ, d in defs.items()
           if (d or {}).get("patterns") and (ALL_STATES - _have(occ, overrides))]
    return sorted(out)


def write_candidate_report(results: dict[str, dict[str, tuple[str, int]]], path: Path,
                           min_score: int) -> int:
    """Write a markdown review worklist of brute-force candidates. Returns row count."""
    rows = [(occ, st, sib, score)
            for occ, links in sorted(results.items())
            for st, (sib, score) in sorted(links.items())]
    lines = [
        "# Brute-force cross-ref candidates (REVIEW before applying)",
        "",
        f"LLM-free scan: each occupation's professions.yaml patterns grepped across every "
        f"pulled corpus; density >= {min_score} pattern hits. These are CANDIDATES — a high "
        f"score means a sibling corpus regulates the occupation, but eyeball each (a broad "
        f"umbrella title can score high without being the right scoped chapter).",
        "",
        f"**{len(rows)} candidate link(s) across {len(results)} occupation(s).**",
        "",
        "| occupation | state | sibling corpus | pattern hits |",
        "| --- | --- | --- | --- |",
    ]
    lines += [f"| {occ} | {st} | {sib} | {score} |" for occ, st, sib, score in rows]
    path.write_text("\n".join(lines) + "\n")
    return len(rows)


def brute_force_links(profession: str, overrides: dict, patterns: list[str],
                      sibling_pool: list[str], min_score: int) -> dict[str, tuple[str, int]]:
    """For each blank state, the BEST-scoring sibling corpus that densely uses the
    occupation's patterns. Best (not first) because there's no preference order in
    a brute scan — the densest match is the most likely shared board."""
    blank = sorted(ALL_STATES - _have(profession, overrides))
    out: dict[str, tuple[str, int]] = {}
    for st in blank:
        best: tuple[str, int] | None = None
        for sib in sibling_pool:
            if sib == profession:
                continue
            txt = _corpus_text(sib, st)
            if not txt:
                continue
            score = sum(len(re.findall(re.escape(p), txt, re.I)) for p in patterns)
            if score >= min_score and (best is None or score > best[1]):
                best = (sib, score)
        if best:
            out[st] = best
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", help="one occupation key (from CONFIG, or any "
                                         "professions.yaml key with --brute-force)")
    ap.add_argument("--all", action="store_true", help="run every occupation in CONFIG")
    ap.add_argument("--all-trades", action="store_true", help="run electrician, plumbing, hvac")
    ap.add_argument("--siblings", help="comma-separated override of the sibling pool")
    ap.add_argument("--brute-force", action="store_true",
                    help="ignore CONFIG: use the occupation's professions.yaml patterns and scan "
                         "EVERY pulled corpus to auto-discover shared-board links. Use with "
                         "--profession (and optionally --siblings to narrow the pool).")
    ap.add_argument("--all-brute", action="store_true",
                    help="brute-force EVERY incomplete occupation (patterns + blank states) and "
                         "write a review worklist to results/brute_force_candidates.md.")
    ap.add_argument("--min-score", type=int, default=DENSITY,
                    help=f"density threshold for --brute-force/--all-brute (default {DENSITY})")
    ap.add_argument("--apply", action="store_true", help="write confirmed links to corpus_overrides.yaml")
    args = ap.parse_args()

    overrides = load_corpus_overrides()

    if args.all_brute and args.apply:
        return print("--all-brute is report-only (candidates need review). Re-run a specific "
                     "occupation with --brute-force --apply after reviewing the worklist.") or 2

    if args.all_brute:
        pool = ([s.strip() for s in args.siblings.split(",")] if args.siblings else _all_occupations())
        profs = incomplete_occupations(overrides)
        print(f"brute-forcing {len(profs)} incomplete occupation(s) over {len(pool)} corpora "
              f"(min-score {args.min_score})…")
        results = {}
        for prof in profs:
            links = brute_force_links(prof, overrides, load_patterns(prof), pool, args.min_score)
            if links:
                results[prof] = links
        total = sum(len(v) for v in results.values())
        report = REPO / "pipeline" / "results" / "brute_force_candidates.md"
        n = write_candidate_report(results, report, args.min_score)
        print(f"wrote {n} candidate(s) across {len(results)} occupation(s) to "
              f"{report.relative_to(REPO)} — REVIEW before --apply")
        return 0
    elif args.brute_force:
        if not args.profession:
            return print("--brute-force needs --profession") or 2
        prof = args.profession
        patterns = load_patterns(prof)
        if not patterns:
            return print(f"  {prof}: no patterns in professions.yaml — can't brute-force") or 2
        pool = ([s.strip() for s in args.siblings.split(",")] if args.siblings
                else _all_occupations())
        links = brute_force_links(prof, overrides, patterns, pool, args.min_score)
        for st, (sib, score) in sorted(links.items()):
            print(f"  {prof}/{st} ← {sib}  ({score} pattern hits)  [brute-force CANDIDATE — review]")
        results = {prof: links}
        total = len(links)
    else:
        if args.all:
            profs = list(CONFIG)
        elif args.all_trades:
            profs = ["electrician", "plumbing", "hvac"]
        else:
            profs = [args.profession]
        if not profs or profs == [None]:
            return print("give --profession, --all-trades, --all, or --brute-force") or 2
        results = {}
        total = 0
        for prof in profs:
            if prof not in CONFIG:
                print(f"  {prof}: not in CONFIG (add its terms + siblings, or use --brute-force)"); continue
            terms = CONFIG[prof]["terms"]
            siblings = ([s.strip() for s in args.siblings.split(",")] if args.siblings else CONFIG[prof]["siblings"])
            links = find_links(prof, overrides, terms, siblings)
            for st, (sib, score) in links.items():
                print(f"  {prof}/{st} ← {sib}  ({score} licensing-term hits)")
            results[prof] = links
            total += len(links)

    if args.apply and total:
        for prof, links in results.items():
            if links:
                overrides.setdefault(prof, {}).update({st: sib for st, (sib, _) in links.items()})
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
