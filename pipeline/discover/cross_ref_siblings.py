"""Sibling-trade cross-reference: fill a profession's missing states from a
sibling's already-harvested corpus, with NO new fetch (#53).

The trades taught us that one statutory chapter often governs several occupations
— TN Title 62 Ch.6 covers HVAC + electrician + plumber; AK Title 8 Ch.48 covers
architects + engineers + surveyors. When the discovery step keyed on chapter
titles it pulled that chapter for ONE trade and logged the others as gaps, even
though the practice-defining text for all of them is sitting in the corpus we
already pulled.

This step closes that gap automatically and durably:

  1. For each state where `profession` has NO corpus, look at the corpora we DID
     pull for its sibling professions (same `family` in professions.yaml, or an
     explicit --siblings list).
  2. Keyword-prefilter: does the sibling corpus even mention this trade (its
     professions.yaml `patterns`)? Cheap; skips the obvious non-matches.
  3. LLM-confirm (shared pipeline._llm.call_structured): does this chapter actually
     license/regulate the *practice* of the target profession — not just name-drop
     it? Guards against a passing cross-reference.
  4. Record confirmed hits in config/corpus_overrides.yaml as
     `{profession: {STATE: sibling}}`. clean_text reads that and pulls the state's
     text from the sibling corpus, so a normal clean→trim→extract fills the gap.

Run it after a harvest (or against the back catalog) and the gap self-heals
instead of needing a re-fetch. Genuine local-only nulls (no sibling carries the
trade) are left untouched — they're a real "not regulated at the state level",
not a data gap.

Usage:
  # dry-run report (default): what would be wired, with the confirming quote
  python -m pipeline.discover.cross_ref_siblings --profession architecture
  # restrict the sibling pool / states
  python -m pipeline.discover.cross_ref_siblings --profession hvac --siblings construction_trades,plumbing
  python -m pipeline.discover.cross_ref_siblings --profession plumbing --states AK,MS,PA
  # write the confirmed links into config/corpus_overrides.yaml
  python -m pipeline.discover.cross_ref_siblings --profession architecture --apply
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import yaml
from pydantic import BaseModel

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "pipeline"))
import _env  # noqa: E402
_env.load_env()
from _llm import call_structured, log_usage_summary  # noqa: E402

TEXT_DIR = REPO / "pipeline" / "results" / "text"
CONFIG_DIR = REPO / "pipeline" / "config"
PROFESSIONS = CONFIG_DIR / "professions.yaml"
OVERRIDES = CONFIG_DIR / "corpus_overrides.yaml"
MODEL = "claude-sonnet-4-6"
MAX_CONFIRM_CHARS = 8000  # cap the statute text sent per confirmation

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("cross_ref_siblings")


class Confirm(BaseModel):
    licenses_practice: bool
    governing_quote: str  # the language that shows it (empty if false)


def _profs() -> dict:
    return yaml.safe_load(PROFESSIONS.read_text()) or {}


def _states_with_corpus(prof: str) -> set[str]:
    d = TEXT_DIR / prof
    if not d.exists():
        return set()
    return {p.stem.upper() for p in d.glob("*.json") if not p.name.startswith("_")}


def _corpus_text(prof: str, state: str) -> str:
    p = TEXT_DIR / prof / f"{state}.json"
    if not p.exists():
        return ""
    try:
        d = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return ""
    secs = d.get("sections") or []
    return "\n\n".join(s.get("text", "") for s in secs if isinstance(s, dict))


def _matching_excerpt(text: str, patterns: list[str]) -> str | None:
    """Return up to MAX_CONFIRM_CHARS of text centered on the first pattern hit,
    or None if no pattern appears at all (the cheap prefilter)."""
    low = text.lower()
    hits = [low.find(p.lower()) for p in patterns]
    hits = [h for h in hits if h >= 0]
    if not hits:
        return None
    i = min(hits)
    start = max(0, i - 1000)
    return text[start : start + MAX_CONFIRM_CHARS]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--siblings", help="comma-separated; default = same family in professions.yaml")
    ap.add_argument("--states", help="comma-separated subset of the missing states")
    ap.add_argument("--apply", action="store_true", help="write confirmed links to corpus_overrides.yaml")
    args = ap.parse_args()

    target = args.profession.lower()
    conf = _profs()
    if target not in conf:
        return log.error("unknown profession %s", target) or 2
    patterns = conf[target].get("patterns") or [target.replace("_", " ")]
    display = conf[target].get("display", target)

    # sibling pool: explicit, else same-family professions (minus the target)
    if args.siblings:
        siblings = [s.strip().lower() for s in args.siblings.split(",")]
    else:
        fam = set(conf[target].get("family") or [])
        siblings = [p for p, e in conf.items()
                    if p != target and fam & set((e or {}).get("family") or [])]
    siblings = [s for s in siblings if (TEXT_DIR / s).exists()]

    have = _states_with_corpus(target)
    missing = sorted({p.stem.upper() for s in siblings for p in (TEXT_DIR / s).glob("*.json")
                      if not p.name.startswith("_")} - have)
    if args.states:
        want = {s.strip().upper() for s in args.states.split(",")}
        missing = [s for s in missing if s in want]

    log.info("[%s] %d states with corpus; checking %d missing against siblings %s",
             target, len(have), len(missing), siblings)

    found: dict[str, dict] = {}
    for state in missing:
        for sib in siblings:
            text = _corpus_text(sib, state)
            if not text:
                continue
            excerpt = _matching_excerpt(text, patterns)
            if excerpt is None:
                continue  # sibling doesn't even mention the trade
            res = call_structured(
                model=MODEL, schema_cls=Confirm, embed_schema=True, max_tokens=400,
                log_prefix=f"[{target}/{state}<-{sib}]",
                system=(
                    f"You decide whether a statute chapter licenses or regulates the PRACTICE of "
                    f"{display}. Answer true only if the text sets requirements to practice/be "
                    f"licensed as {display} (registration, qualifications, scope, a board) — not if "
                    f"it merely mentions the word in passing or in a cross-reference. Quote the "
                    f"governing language."
                ),
                user=f"Target occupation: {display}\n\nStatute text (from the {sib} corpus for {state}):\n{excerpt}",
            )
            if res and res.licenses_practice:
                found[state] = {"sibling": sib, "quote": res.governing_quote[:200]}
                log.info("  ✓ %s ← %s: %s", state, sib, res.governing_quote[:90])
                break  # first confirming sibling wins
        else:
            continue

    log.info("\n[%s] confirmed %d/%d missing states fillable from a sibling corpus (no fetch):",
             target, len(found), len(missing))
    for st, info in sorted(found.items()):
        log.info("    %s ← %s", st, info["sibling"])
    unfilled = [s for s in missing if s not in found]
    if unfilled:
        log.info("  not fillable (genuine null or needs fetch): %s", ", ".join(unfilled))

    if args.apply and found:
        ov = {}
        if OVERRIDES.exists():
            ov = yaml.safe_load(OVERRIDES.read_text()) or {}
        ov.setdefault(target, {})
        for st, info in found.items():
            ov[target][st] = info["sibling"]
        OVERRIDES.write_text(
            "# Per-(profession, state) corpus reuse, written by discover.cross_ref_siblings (#53).\n"
            "# {profession: {STATE: sibling_profession}} — clean_text reads the state's text from\n"
            "# the sibling's already-harvested corpus (a combined/contractor chapter). No new fetch.\n"
            + yaml.safe_dump(ov, sort_keys=True, default_flow_style=False)
        )
        log.info("\nwrote %d links to %s", len(found), OVERRIDES.relative_to(REPO))
    elif found:
        log.info("\n(dry run — re-run with --apply to write %d links to corpus_overrides.yaml)", len(found))

    log_usage_summary(log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
