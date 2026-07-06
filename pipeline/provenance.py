"""Provenance stamping + freshness for the pipeline stages.

Problem: a stage's output is a function of its input AND its recipe (the prompt, the
schema, the model, the code). If we re-pull a corpus or change a prompt, a previously
"done" cell is silently stale — the file still exists, but it no longer reflects how we'd
produce it today. mtimes can't tell us this: `git clone` resets them.

Fix: when a stage writes a cell, record a content hash of the exact input it consumed
plus a hash of its recipe, in a side file `results/provenance/<prof>/<state>.json`
(kept OUT of the stage dirs so pristine payloads still hash stably and nothing pollutes
the many `glob('*.json')` call sites or the published frontend). Freshness is then a
recompute-and-compare:

    check(stage, prof, state) -> "current" | "stale" | "unstamped" | "missing"

Cross-stage staleness propagates for free through the input hash: change clean's output
and trim's stored input_hash stops matching, so trim reads stale, and extract after it.

Bump CODE_VERSION[stage] by hand when a stage's LOGIC changes in a way that should
invalidate its prior outputs (prompt/schema/model changes are detected automatically).
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache

from pipeline.paths import (
    TEXT_DIR, CLEAN_DIR, TRIMMED_DIR, STRUCTURED_DIR, DISCOVERED_DIR, RESULTS_DIR,
)
from pipeline._prompts import load_prompt

STAGES = ("clean", "trim", "extract")

_IN = {"clean": TEXT_DIR, "trim": CLEAN_DIR, "extract": TRIMMED_DIR}
_OUT = {"clean": CLEAN_DIR, "trim": TRIMMED_DIR, "extract": STRUCTURED_DIR}
_PROMPT_KEY = {"clean": None, "trim": "trim_state", "extract": "extract_state"}
_MODEL = {"clean": None, "trim": "claude-haiku-4-5-20251001", "extract": "claude-sonnet-4-6"}

# Manual code-version tags — bump when a stage's logic should invalidate old outputs.
CODE_VERSION = {"clean": 1, "trim": 1, "extract": 1}

PROV_DIR = RESULTS_DIR / "provenance"


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _payload_hash(path) -> str | None:
    """Hash a JSON file's meaningful content — defensively dropping any `_provenance`
    key so an (inlined) stamp can never perturb the hash."""
    if not path.exists():
        return None
    try:
        d = json.loads(path.read_text())
    except Exception:
        return None
    if isinstance(d, dict):
        d = {k: v for k, v in d.items() if k != "_provenance"}
    return _sha(json.dumps(d, sort_keys=True, ensure_ascii=False))


def _clean_source_path(prof: str, state: str):
    """The real text/<...>/<STATE>.json clean_text consumes (own / parent_corpus /
    sibling override) — NOT the hardcoded TEXT_DIR/<prof>/ which doesn't exist for a
    nested or override profession. Delegates to the shared resolver so provenance hashes
    exactly what clean reads. Imported lazily to keep the module import graph acyclic."""
    from pipeline.config.loaders import resolve_clean_source
    return resolve_clean_source(prof, state, _IN["clean"])


def _umbrella_hash(state: str) -> str | None:
    """Combined hash of the umbrella inputs extract folds into every extraction for this
    state (umbrella_text + umbrella_scope). None when the state has neither file. Tracked
    separately from input_hash (see stamp/check) so adding it doesn't retroactively flip
    every already-stamped extract cell stale."""
    ut = _payload_hash(RESULTS_DIR / "umbrella_text" / f"{state}.json")
    us = _payload_hash(RESULTS_DIR / "umbrella_scope" / f"{state}.json")
    if ut is None and us is None:
        return None
    return _sha(f"{ut or ''}|{us or ''}")


def input_hash(stage: str, prof: str, state: str) -> str | None:
    if stage == "clean":
        return _payload_hash(_clean_source_path(prof, state))
    return _payload_hash(_IN[stage] / prof / f"{state}.json")


@lru_cache(maxsize=None)
def recipe_hash(stage: str, prof: str, model: str | None = None) -> str:
    """Hash of everything besides the input that determines this stage's output:
    code version + prompt text + model + (for extract) the profession schema.

    `model` is the model actually used (threaded from the stage's --model). When None we
    fall back to the stage's canonical default table, so a default-model run hashes
    identically to before — only a non-default override shifts the recipe (and correctly
    reads stale against the canonical recipe until re-run)."""
    parts = [f"code={CODE_VERSION[stage]}"]
    key = _PROMPT_KEY[stage]
    if key:
        parts.append("prompt=" + _sha(load_prompt(key)))
    m = model or _MODEL[stage]
    if m:
        parts.append("model=" + m)
    if stage == "extract":
        parts.append("schema=" + (_payload_hash(DISCOVERED_DIR / f"{prof}.json") or "none"))
    return _sha("|".join(parts))


def stamp(stage: str, prof: str, state: str, model: str | None = None) -> dict:
    d = {"input_hash": input_hash(stage, prof, state),
         "recipe_hash": recipe_hash(stage, prof, model)}
    if stage == "extract":
        uh = _umbrella_hash(state)
        if uh is not None:
            d["umbrella_hash"] = uh
    return d


def _prov_path(prof: str, state: str):
    return PROV_DIR / prof / f"{state}.json"


def _load_prov(prof: str, state: str) -> dict:
    p = _prov_path(prof, state)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def record(stage: str, prof: str, state: str, model: str | None = None) -> None:
    """Stamp one stage into the cell's provenance file (read-modify-write, so the other
    stages' stamps are preserved). Call right after writing the stage output. Pass the
    model actually used (the stage's --model) so an off-default run is captured.

    `stamped_at` is metadata only — check() compares input_hash/recipe_hash, never the
    timestamp, so re-running with identical content doesn't read as stale."""
    from datetime import datetime
    p = _prov_path(prof, state)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = _load_prov(prof, state)
    data[stage] = {**stamp(stage, prof, state, model), "stamped_at": datetime.now().isoformat(timespec="seconds")}
    p.write_text(json.dumps(data, indent=2, sort_keys=True))


def check(stage: str, prof: str, state: str) -> str:
    """current | stale | unstamped | missing (missing = the stage output isn't there)."""
    if not (_OUT[stage] / prof / f"{state}.json").exists():
        return "missing"
    p = _load_prov(prof, state).get(stage)
    if not p or "input_hash" not in p:
        return "unstamped"
    if p.get("input_hash") != input_hash(stage, prof, state):
        return "stale"
    if p.get("recipe_hash") != recipe_hash(stage, prof):
        return "stale"
    # Umbrella context is a real extract input but is compared only when the stamp
    # recorded one: stamps written before umbrella tracking have no `umbrella_hash`, and
    # must NOT be flipped stale for lacking it. New extractions stamp it, so future
    # umbrella_text/umbrella_scope edits correctly invalidate them.
    if "umbrella_hash" in p and p.get("umbrella_hash") != _umbrella_hash(state):
        return "stale"
    return "current"


def last_stamped(prof: str, state: str) -> str | None:
    """Most recent `stamped_at` across a cell's stages (None if never stamped)."""
    data = _load_prov(prof, state)
    dates = [v.get("stamped_at") for v in data.values()
             if isinstance(v, dict) and v.get("stamped_at")]
    return max(dates) if dates else None


def cell_freshness(prof: str, state: str) -> tuple[str, str | None]:
    """Overall freshness of a cell that has structured output.

    Returns (verdict, earliest_stale_stage):
      - ("current", None)      every stage stamped and matching
      - ("stale", <stage>)     earliest stage whose input/recipe changed → re-run from there
      - ("unstamped", None)    output exists but at least one stage has no stamp yet
    """
    res = {s: check(s, prof, state) for s in STAGES}
    for s in STAGES:
        if res[s] == "stale":
            return "stale", s
    if all(res[s] == "current" for s in STAGES):
        return "current", None
    return "unstamped", None


# --- CLI: report + backfill ---------------------------------------------------

def _iter_done_cells():
    if not STRUCTURED_DIR.exists():
        return
    for pdir in sorted(STRUCTURED_DIR.iterdir()):
        if not pdir.is_dir():
            continue
        for f in sorted(pdir.iterdir()):
            if f.suffix == ".json" and not f.name.startswith("_"):
                yield pdir.name, f.stem


def _report() -> None:
    counts = {"current": 0, "stale": 0, "unstamped": 0}
    stale_by_stage: dict[str, int] = {}
    for prof, state in _iter_done_cells():
        verdict, stage = cell_freshness(prof, state)
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict == "stale":
            stale_by_stage[stage] = stale_by_stage.get(stage, 0) + 1
    total = sum(counts.values())
    print(f"structured cells: {total}")
    print(f"  current:   {counts['current']}")
    print(f"  stale:     {counts['stale']}  {stale_by_stage or ''}")
    print(f"  unstamped: {counts['unstamped']}  (no provenance yet — run backfill to baseline)")


def _backfill(professions: set[str] | None = None) -> None:
    """Stamp existing outputs with CURRENT hashes — an explicit operator assertion that
    the committed outputs reflect today's prompts/corpus. After this, any future recipe or
    corpus change correctly flips affected cells to stale.

    Pass `professions` to scope the assertion (e.g. only the professions you KNOW were
    re-extracted under the current prompts); others stay honestly unstamped."""
    n = 0
    for prof, state in _iter_done_cells():
        if professions is not None and prof not in professions:
            continue
        for s in STAGES:
            if (_OUT[s] / prof / f"{state}.json").exists():
                record(s, prof, state)
        n += 1
    scope = f" for {len(professions)} professions" if professions else ""
    print(f"backfilled provenance for {n} done cells{scope} (baseline = current recipe)")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Pipeline provenance / freshness.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("report", help="freshness tally across all structured cells")
    bf = sub.add_parser("backfill", help="stamp existing outputs as the current baseline")
    bf.add_argument("--professions", default="",
                    help="Comma-separated subset to stamp (default: all done cells)")
    args = ap.parse_args()
    if args.cmd == "report":
        _report()
    else:
        profs = {p.strip() for p in args.professions.split(",") if p.strip()} or None
        _backfill(profs)


if __name__ == "__main__":
    main()
