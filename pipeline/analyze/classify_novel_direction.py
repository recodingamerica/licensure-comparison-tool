"""Tag each novel policy as more restrictive / more permissive / neutral (#52c).

Atharv asked to filter novel policies by *what kind* they are beyond Field —
specifically whether a rare policy is MORE RESTRICTIVE or MORE PERMISSIVE than
what most states do. That direction isn't derivable by rule: "more" flips sign
(higher insurance minimum = restrictive, but higher dollar threshold before
licensing applies = permissive), and coverage-novelty policies have no value to
compare at all — direction has to be read off the statute quote. So we ask the
LLM, giving it the field, the rare value, the majority (from similarity.py's
`majority`), and the quote.

DRY + cheap:
  - Uses the shared pipeline._llm.call_structured helper (one retry/validation
    loop for the whole repo) — no bespoke call code here.
  - Dedupes globally to distinct (field, value) pairs and CACHES the verdict to
    results/novel_direction_cache.json. Direction is a property of (field, value),
    not of the occupation, so each pair is classified exactly once — ever. New
    professions / re-runs only classify genuinely-new pairs.
  - Batches ~25 pairs per call, so the whole corpus is a handful of calls.

Runs AFTER similarity.py (needs `majority`) and BEFORE publish_analysis:
  python -m pipeline.analyze.similarity --profession optometry --json
  python -m pipeline.analyze.classify_novel_direction            # all analyzed
  python -m pipeline.analyze.publish_analysis

Usage:
  python -m pipeline.analyze.classify_novel_direction
  python -m pipeline.analyze.classify_novel_direction --professions optometry,plumbing
  python -m pipeline.analyze.classify_novel_direction --rebuild   # ignore cache
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

REPO = Path(__file__).resolve().parents[2]
from pipeline._env import load_env
load_env()
from pipeline._llm import call_structured, log_usage_summary
from pipeline.config.loaders import model_for

ANALYSIS_DIR = REPO / "pipeline" / "results" / "analysis"
CACHE_PATH = REPO / "pipeline" / "results" / "novel_direction_cache.json"
MODEL = model_for("novel_direction")
CHUNK = 25  # pairs per LLM call

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("classify_novel_direction")

Direction = Literal["more_restrictive", "more_permissive", "neutral"]


class Verdict(BaseModel):
    id: int
    direction: Direction
    reason: str


class VerdictBatch(BaseModel):
    items: list[Verdict]


SYSTEM = (
    "You judge whether a US state's occupational-licensing policy choice is MORE RESTRICTIVE or "
    "MORE PERMISSIVE than what most states do, for the people the licensing law governs.\n"
    "- more_restrictive = higher barriers to enter or practice: more requirements, prohibitions, "
    "mandated insurance/bonding, caps, or burdens placed on practitioners.\n"
    "- more_permissive = lower barriers: fewer requirements, more options, or higher dollar/size "
    "thresholds before the regulation even applies (so fewer people are regulated).\n"
    "- neutral = an organizational or definitional choice with no clear direction of burden.\n"
    "Judge the RARE value relative to the MAJORITY. 'More' does not always mean restrictive — a higher "
    "minimum-insurance figure is more restrictive, but a higher dollar threshold before a license is "
    "required is more permissive. When there is no comparable value (the field is one most states don't "
    "address at all), read the direction off the statute quote. Return one verdict per item by id."
)


def _key(field: str, value) -> str:
    return f"{field}|{value}"


def _pair_block(idx: int, field: str, value, maj: dict, quote: str, label: str) -> str:
    mv, mn = maj.get("value"), maj.get("n")
    un, tot = maj.get("unstated"), maj.get("total")
    most = f"value={mv} (held by {mn})" if mv is not None else "no comparable value — most states don't address this"
    return (
        f"[{idx}] field={field}\n"
        f"     this state's rare value: {value}\n"
        f"     most states: {most}; unstated={un}/{tot}\n"
        f"     plain label: {label}\n"
        f"     statute quote: {(quote or '')[:400]}"
    )


def classify_pairs(pairs: list[dict]) -> dict[str, dict]:
    """pairs: [{key, field, value, majority, quote, label}, ...] -> {key: {direction, reason}}."""
    out: dict[str, dict] = {}
    for start in range(0, len(pairs), CHUNK):
        chunk = pairs[start : start + CHUNK]
        user = "Classify each policy below.\n\n" + "\n\n".join(
            _pair_block(i, p["field"], p["value"], p["majority"], p["quote"], p["label"])
            for i, p in enumerate(chunk)
        )
        res = call_structured(
            model=MODEL, system=SYSTEM, user=user, schema_cls=VerdictBatch,
            embed_schema=True, max_tokens=4000, log_prefix=f"[dir {start}-{start+len(chunk)}]",
        )
        if res is None:
            log.warning("chunk %d-%d failed; leaving uncached", start, start + len(chunk))
            continue
        by_id = {v.id: v for v in res.items}
        for i, p in enumerate(chunk):
            v = by_id.get(i)
            if v is not None:
                out[p["key"]] = {"direction": v.direction, "reason": v.reason}
        log.info("classified %d/%d pairs", len([1 for p in chunk if p["key"] in out]), len(chunk))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", help="comma-separated; default = all in results/analysis")
    ap.add_argument("--rebuild", action="store_true", help="ignore the cache and re-classify everything")
    args = ap.parse_args()

    profs = (
        [p.strip().lower() for p in args.professions.split(",")]
        if args.professions
        else [p.stem for p in sorted(ANALYSIS_DIR.glob("*.json"))]
    )

    cache: dict[str, dict] = {}
    if CACHE_PATH.exists() and not args.rebuild:
        cache = json.loads(CACHE_PATH.read_text())

    # Collect distinct (field, value) pairs needing classification, with one
    # representative quote/majority/label each.
    need: dict[str, dict] = {}
    files = [ANALYSIS_DIR / f"{p}.json" for p in profs]
    for fp in files:
        if not fp.exists():
            continue
        d = json.loads(fp.read_text())
        for p in d.get("novel_policies", []):
            k = _key(p["field"], p.get("value"))
            if k in cache or k in need:
                continue
            need[k] = {
                "key": k, "field": p["field"], "value": p.get("value"),
                "majority": p.get("majority") or {}, "quote": p.get("quote", ""), "label": p["label"],
            }

    if need:
        log.info("classifying %d new (field,value) pairs (%d already cached)", len(need), len(cache))
        cache.update(classify_pairs(list(need.values())))
        CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True))
    else:
        log.info("nothing new to classify (%d cached)", len(cache))

    # Stamp `direction` onto every novel policy from the cache.
    for fp in files:
        if not fp.exists():
            continue
        d = json.loads(fp.read_text())
        changed = 0
        for p in d.get("novel_policies", []):
            v = cache.get(_key(p["field"], p.get("value")))
            if v and p.get("direction") != v["direction"]:
                p["direction"] = v["direction"]
                changed += 1
            elif v and "direction" not in p:
                p["direction"] = v["direction"]
        fp.write_text(json.dumps(d, indent=2))
        log.info("[%s] %d policies tagged", fp.stem, sum(1 for p in d.get("novel_policies", []) if "direction" in p))

    log_usage_summary(log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
