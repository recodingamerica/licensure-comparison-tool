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
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from typing import Literal

REPO = Path(__file__).resolve().parents[2]
from pipeline._env import load_env
load_env()
from pipeline._llm import call_structured, log_usage_summary
from pipeline.config.loaders import load_professions, load_limits

TEXT_DIR = REPO / "pipeline" / "results" / "text"
CONFIG_DIR = REPO / "pipeline" / "config"
OUT_DIR = REPO / "pipeline" / "results" / "corpus_audit"
MODEL = "claude-sonnet-4-6"
MAX_CHARS = load_limits()["audit_corpus"]["sample_max_chars"]

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
    "Decide whether the provided corpus CONTAINS the licensing law for the named occupation. You are given "
    "the full list of section citations plus text sampled from across the corpus (it may be large and span "
    "several chapters). The corpus is CORRECT (correct_licensure_text) if the occupation's own licensure "
    "law is present ANYWHERE in it — even when bundled with a shared enforcement/administrative chapter "
    "(e.g. a uniform disciplinary act) or some sections of an adjacent profession. A general-contractor or "
    "combined-trades chapter that explicitly licenses the trade IS correct. Only answer wrong_chapter if the "
    "occupation's licensure law is NOT present at all — the corpus is entirely some OTHER statute (criminal, "
    "procurement, a different profession, a definitions-only fragment). Answer empty_or_repealed only if "
    "there is no operative text / all repealed. Judge only from what is provided; do not use outside "
    "knowledge of the state's real law. The citation list shows the full chapter coverage — use it: a "
    "profession chapter that appears in the citation list counts as present even if its text wasn't sampled."
)


def _occupation_label(profession: str) -> str:
    try:
        conf = load_professions()
    except (OSError, yaml.YAMLError):
        conf = {}
    e = conf.get(profession) or {}
    disp = e.get("display", profession.replace("_", " "))
    pats = e.get("patterns") or []
    return f"{disp}" + (f" (a.k.a. {', '.join(pats[:4])})" if pats else "")


def _sec_cite(s: dict) -> str:
    return str(s.get("citation") or s.get("id") or s.get("label") or "?")


def _corpus_sample(profession: str, state: str) -> tuple[str, int, int, bool]:
    """Build a REPRESENTATIVE view of the corpus, not just its front.

    A naive head-truncation flags false wrong_chapter whenever a large shared
    chapter sorts first and pushes the profession's own chapter past the budget
    (e.g. NJ Title 45 Ch 1 Uniform Enforcement Act = 114 sections before Ch 6
    Dentistry; OR a couple giant VA 54.1 sections). So: (1) show the FULL list of
    section citations so a chapter that sorts last is still visible, and (2) take
    text evenly STRIDED across all sections so the sample spans the whole corpus.
    Returns (sample_text, n_sections_total, n_sections_sampled, sample_truncated)."""
    p = TEXT_DIR / profession / f"{state}.json"
    try:
        d = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return "", 0, 0, False
    secs = [s for s in (d.get("sections") or []) if isinstance(s, dict)]
    if not secs:
        return "", 0, 0, False
    index = ", ".join(_sec_cite(s) for s in secs)[:6000]
    # Stride through sections so the char budget spreads across the corpus rather
    # than front-loading; always include the first section.
    budget = MAX_CHARS - len(index) - 200
    order = list(range(0, len(secs), max(1, len(secs) // 60))) if len(secs) > 60 else list(range(len(secs)))
    parts, used = [], 0
    truncated = False
    for i in order:
        s = secs[i]
        body = (s.get("text") or "")[:2500]
        chunk = f"[{_sec_cite(s)}] {body}"
        if used + len(chunk) > budget:
            truncated = True
            break
        parts.append(chunk)
        used += len(chunk)
    sample = f"Section citations present ({len(secs)} total): {index}\n\n--- sampled section bodies (spread across the corpus) ---\n" + "\n\n".join(parts)
    return sample, len(secs), len(parts), truncated


def audit_states(prof: str, states: list[str]) -> dict[str, dict]:
    """Verdict each state's committed corpus for `prof`. Importable so the harvest
    (pull_all) can gate a fresh pull, not just the CLI.
    Returns {state: {verdict, reason, n_sections_total, n_sections_sampled, sample_truncated}}."""
    occ = _occupation_label(prof)
    results: dict[str, dict] = {}
    for st in states:
        txt, n_total, n_sampled, truncated = _corpus_sample(prof, st)
        meta = {
            "n_sections_total": n_total,
            "n_sections_sampled": n_sampled,
            "sample_truncated": truncated,
        }
        if len(txt.strip()) < 200:
            results[st] = {"verdict": "empty_or_repealed", "reason": "corpus under 200 chars", **meta}
            continue
        if truncated:
            log.warning("[%s/%s] sample truncated at budget (%d/%d sections sampled) — verdict may miss unseen sections",
                        prof, st, n_sampled, n_total)
        r = call_structured(model=MODEL, system=SYS, schema_cls=Verdict, embed_schema=True,
                            max_tokens=400, log_prefix=f"[{prof}/{st}]",
                            user=f"Occupation: {occ}\nState: {st}\n\n{txt}")
        results[st] = ({**{"verdict": r.corpus_verdict, "reason": r.reason}, **meta} if r
                       else {"verdict": "CALL_FAILED", "reason": "", **meta})
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--states", help="comma-separated subset; default = all pulled")
    ap.add_argument("--bad-only", action="store_true", help="print only the flagged states")
    ap.add_argument("--gate", action="store_true", help="exit 1 if any state is not correct_licensure_text")
    args = ap.parse_args()

    prof = args.profession.lower()
    pdir = TEXT_DIR / prof
    if not pdir.exists():
        return log.error("no corpus dir: %s", pdir) or 2

    states = sorted(os.path.basename(f)[:-5] for f in glob.glob(str(pdir / "*.json"))
                    if "_summary" not in f)
    if args.states:
        want = {s.strip().upper() for s in args.states.split(",")}
        states = [s for s in states if s in want]

    results = audit_states(prof, states)

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
