"""Careful per-(trade,state) verification of the remaining #53 gaps.

The haiku first-pass screen (llm_map_profession) OVER-CLAIMS state licensure — it
guesses 'licensed=true' for local-only trades (PA/NY/IL electrician) just because
the state has an occupational title. This is the careful second pass: a stronger
model, grounded in the state's real chapter list, that REFUSES to assume — it must
name the specific state chapter, or call it local_only / not_regulated.

Reads the (trade,state) pairs to check from argv as `trade:STATE,STATE;trade:...`.
Writes results/gap_verify/<trade>.json. Pull only the state_licensed ones; the
local_only / not_regulated ones are confirmed correct-blanks (with evidence).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pipeline"))
import _env  # noqa: E402
_env.load_env()
from _llm import call_structured, log_usage_summary  # noqa: E402
from discover.llm_map_profession import state_chapter_list, load_profession  # noqa: E402

MODEL = "claude-sonnet-4-6"
OUT = REPO / "pipeline" / "results" / "gap_verify"


class Verdict(BaseModel):
    status: Literal["state_licensed", "local_only", "not_regulated"] = Field(
        description="state_licensed = a STATE statute requires a license/registration/certification to "
        "practice this trade, and you can point to the specific chapter in the list. local_only = the "
        "trade is licensed only by cities/counties/municipalities (NO statewide credential) — common for "
        "electricians and plumbers. not_regulated = no state credential of any kind.")
    chapter_label: str | None = Field(default=None, description="If state_licensed: the EXACT chapter label from the list that holds the licensing law. Else null.")
    chapter_url: str | None = Field(default=None, description="If state_licensed: that chapter's url from the list. Else null.")
    reasoning: str = Field(description="One or two sentences citing the specific chapter label (or its absence). No double-quotes.")


SYSTEM = (
    "You decide whether a building trade is licensed AT THE STATE LEVEL in one U.S. state, given that "
    "state's actual list of code chapters. Be skeptical and precise. DO NOT assume a trade is state-"
    "licensed just because the state has a 'Professions and Occupations' or 'Occupational Code' title — "
    "many building trades (especially electricians and plumbers) are licensed ONLY by individual cities "
    "or counties, which is local_only, NOT state_licensed. Answer state_licensed ONLY if a specific "
    "chapter in the provided list plainly establishes a statewide license/registration/certification to "
    "practice this trade (a contractor-registration or combined-trades chapter that names the trade "
    "counts). If you cannot point to such a chapter in the list, answer local_only (if you have reason to "
    "think it's municipally licensed) or not_regulated. Prefer local_only/not_regulated over a guess."
)


def verify(trade: str, defn: dict, state: str) -> dict:
    chapters = state_chapter_list(state)
    if not chapters:
        return {"state": state, "status": "not_regulated", "reasoning": "no chapter list / hierarchy"}
    listing = "\n".join(f"- {c['label']}  [{c['url']}]" for c in chapters)
    user = (f"TRADE: {defn.get('display', trade)} (terms: {', '.join(defn.get('patterns') or [])})\n"
            f"STATE: {state}\nCHAPTERS:\n{listing}\n\n"
            "Is this trade licensed at the STATE level here? If yes, name the exact chapter.")
    r = call_structured(model=MODEL, system=SYSTEM, user=user, schema_cls=Verdict,
                        embed_schema=True, max_tokens=500, log_prefix=f"[{trade}/{state}]")
    return {"state": state, **(r.model_dump() if r else {"status": "CALL_FAILED", "reasoning": ""})}


def main() -> int:
    spec = sys.argv[1]  # "hvac:CO,MA;electrician:PA,NY"
    OUT.mkdir(parents=True, exist_ok=True)
    for group in spec.split(";"):
        trade, states = group.split(":")
        defn = load_profession(trade)
        results = [verify(trade, defn, s.strip()) for s in states.split(",") if s.strip()]
        (OUT / f"{trade}.json").write_text(json.dumps(results, indent=2))
        for r in results:
            print(f"  {trade}/{r['state']}: {r['status']:16s} {(r.get('chapter_label') or '')[:38]:38s} — {r['reasoning'][:70]}")
    log_usage_summary(__import__("logging").getLogger())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
