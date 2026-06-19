"""One-line LLM characterization of UTAH's regime per profession.

Utah-only by request: the structured similarity/outlier scores carry every state,
but the prose summary is just for Utah's view ("overall, what is Utah like, and
where is it doing something weird"). One cheap call per profession, fed the
already-computed neighbors + outliers + Utah's own field values as grounding.

Usage:
  python -m pipeline.analyze.utah_note --profession optometry
  python -m pipeline.analyze.utah_note --professions optometry,dietetics --write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import BaseModel, Field

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pipeline"))
from _env import load_env  # noqa: E402
load_env()
from _llm import call_structured  # noqa: E402
from analyze import similarity as S  # noqa: E402

MODEL = "claude-sonnet-4-6"
OUT_DIR = REPO / "pipeline" / "results" / "analysis"

SYSTEM = """You write ONE plain-English sentence summarizing how Utah regulates an occupation relative to other states, for a policy audience. Lead with the overall character (is Utah typical / strict / permissive, and most like which states), then name the one or two specific things Utah does that are unusual (rare category or much stricter/looser than peers). Be concrete and grounded ONLY in the data given — no hedging, no invented facts, no "confidence" language. One sentence, <= 45 words."""


class Note(BaseModel):
    sentence: str = Field(description="one-sentence Utah summary, <=45 words")


def note_for(profession: str) -> str:
    S.sem_for = S.load_semantics(profession)
    res = S.analyze(profession)
    if "UT" not in res["states"]:
        return f"(Utah not present in {profession} data)"
    nb = [f"{x['state']} ({x['sim']:.0%})" for x in res["neighbors"].get("UT", [])[:4]]
    ut_kind = [f"{o['field'].split('.')[-1]}={o['value']} (only {o['n_states']}/{o['total']} states)"
               for o in res["kind_outliers"] if o["state"] == "UT"][:5]
    ut_str = [f"{o['field'].split('.')[-1]}={o['value']} ({o['direction']}, z={o['z']})"
              for o in res["stringency_outliers"] if o["state"] == "UT"][:5]
    rank = list(res["distinctiveness"]).index("UT") + 1
    user = (
        f"Occupation: {profession}\n"
        f"Utah's most-similar states: {', '.join(nb) or 'n/a'}\n"
        f"Utah overall-distinctiveness rank: {rank} of {len(res['states'])} (1 = most distinctive)\n"
        f"Utah categorically-rare choices: {ut_kind or 'none'}\n"
        f"Utah much-stricter/looser-than-peers: {ut_str or 'none'}\n"
    )
    r = call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=Note, embed_schema=True, max_tokens=400)
    return r.sentence if r else "(LLM failed)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession")
    ap.add_argument("--professions", help="comma-separated")
    ap.add_argument("--write", action="store_true", help="store under results/analysis/<prof>.json utah_note")
    args = ap.parse_args()
    profs = [args.profession] if args.profession else (args.professions.split(",") if args.professions else [])
    for p in profs:
        p = p.strip().lower()
        s = note_for(p)
        print(f"\n[{p}] {s}")
        if args.write:
            fp = OUT_DIR / f"{p}.json"
            if fp.exists():
                d = json.loads(fp.read_text()); d["utah_note"] = s
                fp.write_text(json.dumps(d, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
