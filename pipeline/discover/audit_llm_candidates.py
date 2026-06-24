"""Guardrail for the LLM mapper's candidate files.

Two checks, both offline (no Justia):
  1. Count summary — per profession: licensed / umbrella-flagged / not-licensed,
     and an effective licensed count (licensed + umbrella-flagged, since umbrella
     flags are "licensed pending expansion"). Flags professions whose effective
     count looks anomalous so the operator eyeballs them against reality
     (IJ/NCSL as a *pointer*, never ingested as our data).
  2. Not-licensed re-check (--recheck) — the mapper's main error class is
     not-licensed FALSE-NEGATIVES (it marks a state not-licensed when the license
     is just nested/oddly-labeled). Re-ask the LLM, adversarially, only about the
     not-licensed states ("are you SURE this isn't state-licensed?"), and report
     disagreements for review. Cheap: only the not-licensed states, one batched
     call per state.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.audit_llm_candidates            # count summary, all candidates
  pipeline/.venv/bin/python -m pipeline.discover.audit_llm_candidates --recheck --profession electrician
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from pipeline._env import load_env
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _llm import call_structured, usage_summary  # noqa: E402
from paths import RESULTS_DIR, CONFIG_DIR  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_map_profession import state_chapter_list, MODEL  # noqa: E402

CAND_DIR = RESULTS_DIR / "profession_index" / "_llm_candidates"

# Rough "should be widely licensed" priors — ONLY to flag anomalies for human
# review, never written into our data. A pointer, per the external-data rule.
WIDELY_LICENSED = {  # profession -> approx # states that license (for eyeballing)
    "cosmetology": 50, "barbering": 50, "real_estate_appraiser": 50,
    "real_estate_broker": 50, "nursing": 50, "electrician": 35, "plumbing": 40,
}


def summary() -> None:
    files = sorted(CAND_DIR.glob("*.json"))
    if not files:
        sys.exit(f"no candidate files in {CAND_DIR}")
    print(f"{'profession':28} {'lic':>4} {'umb':>4} {'no':>4} {'eff':>4}  flag")
    for f in files:
        d = json.loads(f.read_text())
        rows = d.get("states", [])
        lic = sum(1 for r in rows if r.get("licensed"))
        umb = sum(1 for r in rows if r.get("umbrella_container_url"))
        no = sum(1 for r in rows if not r.get("licensed"))
        eff = lic + sum(1 for r in rows if (not r.get("licensed")) and r.get("umbrella_container_url"))
        prof = d.get("profession", f.stem)
        flag = ""
        prior = WIDELY_LICENSED.get(prof)
        if prior and eff < prior - 8:
            flag = f"⚠ eff {eff} << ~{prior} expected — likely false-negatives, re-check"
        print(f"{prof:28} {lic:>4} {umb:>4} {no:>4} {eff:>4}  {flag}")


class Recheck(BaseModel):
    state: str
    actually_licensed: bool = Field(description="On a second look, IS this profession licensed/regulated at the STATE level here?")
    chapter_url: str | None = Field(default=None, description="if actually licensed, the chapter URL (or umbrella container URL) where")
    basis: str


class RecheckBatch(BaseModel):
    results: list[Recheck]


RECHECK_SYS = (
    "You are double-checking a prior pass that may have WRONGLY concluded a "
    "profession is not state-licensed. For each state below, look again at its "
    "chapter list and decide if this profession is actually licensed/regulated at "
    "the state level — the licensing chapter often does NOT contain the profession's "
    "name (it may be a broad 'Occupational Code', 'Contractors', or 'Construction "
    "Industries' chapter). Only return actually_licensed=true if you can point to a "
    "specific plausible chapter. Be skeptical of the prior 'not licensed' verdict."
)


def recheck(prof: str) -> None:
    f = CAND_DIR / f"{prof}.json"
    if not f.exists():
        sys.exit(f"no candidate file for {prof}")
    d = json.loads(f.read_text())
    defn = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text()).get(prof, {})
    nl = [r["state"] for r in d["states"] if not r.get("licensed")]
    if not nl:
        print(f"{prof}: no not-licensed states to re-check"); return
    print(f"{prof}: re-checking {len(nl)} not-licensed states: {nl}")
    flipped = []
    for st in nl:
        chapters = state_chapter_list(st)
        listing = "\n".join(f"- {c['label']}  [{c['url']}]" for c in chapters)
        user = (f"PROFESSION: {defn.get('display', prof)} (terms: {', '.join(defn.get('patterns') or [])})\n"
                f"STATE: {st}\nCHAPTERS:\n{listing}\n\nIs this profession actually state-licensed here?")
        res = call_structured(model=MODEL, system=RECHECK_SYS, user=user,
                              schema_cls=Recheck, embed_schema=True, log_prefix=f"[{st}]")
        if res and res.actually_licensed:
            flipped.append((st, res.chapter_url, res.basis))
            print(f"  ⚠ {st}: re-check says LICENSED — {(res.chapter_url or '')[:50]} | {res.basis[:60]}")
    print(f"\n{prof}: {len(flipped)}/{len(nl)} not-licensed verdicts flipped to licensed on re-check (review these)")
    print(f"USAGE: {json.dumps(usage_summary())}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recheck", action="store_true", help="LLM re-check of not-licensed verdicts")
    ap.add_argument("--profession", default="", help="profession for --recheck")
    args = ap.parse_args()
    if args.recheck:
        if not args.profession:
            ap.error("--recheck needs --profession")
        recheck(args.profession.lower())
    else:
        summary()


if __name__ == "__main__":
    main()
