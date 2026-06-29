"""Post-pull corpus-correctness gate (#53).

Discovery keys on chapter titles, so it occasionally pulls the WRONG law — a criminal
statute, a procurement chapter, a repealed shell, another profession's act — and
silently counts it as coverage. This runs a coverage check over a profession's pulled
corpus and flags any state whose text is not actually that occupation's licensure law,
so a wrong pull is caught instead of believed.

It's the durable form of the ad-hoc audit validated on 2026-06-29: across 4 trades /
146 states it flagged exactly the ~7 wrong/repealed pulls (WA-hvac = abandoned-fridge
criminal statute; KY-electrician, NH-plumbing = repealed; OR-electrician = fire-safety
statute; architecture ND/OR/AL) with NO false alarms, at ~$0.04/state. It is consistent
run-to-run (same verdict on the same corpus).

Wire it after a harvest (or run it over the back catalog) to separate real coverage from
wrong-chapter coverage before any compare/extract trusts the corpus. Uses the shared
pipeline._llm.call_structured helper.

Usage:
  python -m pipeline.discover.audit_corpus --profession hvac
  python -m pipeline.discover.audit_corpus --profession architecture --states ND,OR,AL
  python -m pipeline.discover.audit_corpus --profession hvac --bad-only
  python -m pipeline.discover.audit_corpus --profession hvac --gate   # exit 1 if any bad
"""
from __future__ import annotations

import argparse
import glob
import json
import logging
import os
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from typing import Literal

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pipeline"))
import _env  # noqa: E402
_env.load_env()
from _llm import call_structured, log_usage_summary  # noqa: E402

TEXT_DIR = REPO / "pipeline" / "results" / "text"
CONFIG_DIR = REPO / "pipeline" / "config"
OUT_DIR = REPO / "pipeline" / "results" / "corpus_audit"
MODEL = "claude-sonnet-4-6"
MAX_CHARS = 30000

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("audit_corpus")


class Verdict(BaseModel):
    corpus_verdict: Literal["correct_licensure_text", "wrong_chapter", "empty_or_repealed"] = Field(
        description="correct_licensure_text=this text actually licenses/regulates the practice of the "
        "occupation (including via a general-contractor or combined-trades chapter that names it); "
        "wrong_chapter=some OTHER statute (criminal, procurement, definitions-only, a different "
        "profession); empty_or_repealed=no operative text / all repealed.")
    reason: str = Field(description="one short sentence; NO double-quote characters")


SYS = (
    "Decide whether the provided statute text is the CORRECT licensing law for the named occupation. "
    "A general-contractor or combined-trades chapter that explicitly licenses this trade IS correct. A "
    "criminal statute, a procurement chapter, a repealed chapter, a definitions-only fragment, or another "
    "profession's act is wrong_chapter. Judge only from the provided text; do not use outside knowledge of "
    "what the state's real law is."
)


def _occupation_label(profession: str) -> str:
    try:
        conf = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text()) or {}
    except (OSError, yaml.YAMLError):
        conf = {}
    e = conf.get(profession) or {}
    disp = e.get("display", profession.replace("_", " "))
    pats = e.get("patterns") or []
    return f"{disp}" + (f" (a.k.a. {', '.join(pats[:4])})" if pats else "")


def _corpus_text(profession: str, state: str) -> str:
    p = TEXT_DIR / profession / f"{state}.json"
    try:
        d = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return ""
    return "\n\n".join(s.get("text", "") for s in (d.get("sections") or []) if isinstance(s, dict))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--states", help="comma-separated subset; default = all pulled")
    ap.add_argument("--bad-only", action="store_true", help="print only the flagged states")
    ap.add_argument("--gate", action="store_true", help="exit 1 if any state is not correct_licensure_text")
    args = ap.parse_args()

    prof = args.profession.lower()
    occ = _occupation_label(prof)
    pdir = TEXT_DIR / prof
    if not pdir.exists():
        return log.error("no corpus dir: %s", pdir) or 2

    states = sorted(os.path.basename(f)[:-5] for f in glob.glob(str(pdir / "*.json"))
                    if "_summary" not in f)
    if args.states:
        want = {s.strip().upper() for s in args.states.split(",")}
        states = [s for s in states if s in want]

    results: dict[str, dict] = {}
    for st in states:
        txt = _corpus_text(prof, st)[:MAX_CHARS]
        if len(txt.strip()) < 200:
            results[st] = {"verdict": "empty_or_repealed", "reason": "corpus under 200 chars"}
            continue
        r = call_structured(model=MODEL, system=SYS, schema_cls=Verdict, embed_schema=True,
                            max_tokens=400, log_prefix=f"[{prof}/{st}]",
                            user=f"Occupation: {occ}\nState: {st}\n\nStatute text:\n{txt}")
        results[st] = ({"verdict": r.corpus_verdict, "reason": r.reason} if r
                       else {"verdict": "CALL_FAILED", "reason": ""})

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{prof}.json").write_text(json.dumps(results, indent=2, sort_keys=True))

    bad = {s: v for s, v in results.items() if v["verdict"] != "correct_licensure_text"}
    ok = len(results) - len(bad)
    for st in sorted(results if not args.bad_only else bad):
        v = results[st]
        flag = "ok " if v["verdict"] == "correct_licensure_text" else "BAD"
        log.info("  [%s] %s: %s — %s", flag, st, v["verdict"], v["reason"][:90])
    log.info("\n[%s] %d/%d correct (%d%%); %d flagged. wrote %s",
             prof, ok, len(results), (100 * ok // len(results)) if results else 0,
             len(bad), (OUT_DIR / f"{prof}.json").relative_to(REPO))
    if bad:
        log.info("  flagged → re-discover the right chapter (try cross_ref_siblings, widen the title "
                 "net), or mark a genuine null: %s", ", ".join(sorted(bad)))

    log_usage_summary(log)
    return 1 if (args.gate and bad) else 0


if __name__ == "__main__":
    raise SystemExit(main())
