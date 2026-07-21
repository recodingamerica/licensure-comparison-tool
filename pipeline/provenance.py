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
    MAP_PREP_DIR, WEB_PUBLIC_DIR, PROFESSION_INDEX_DIR,
)
from pipeline._records import write_json_atomic, read_json
from pipeline._prompts import load_prompt

# STAGES = the per-cell extract-path stages whose combined freshness defines whether a
# DONE cell (one with structured output) is current. cell_freshness()/_backfill() iterate
# these; do NOT add profession-scoped stages here (they aren't per-(prof,state)).
STAGES = ("clean", "trim", "extract")

# The full freshness contract spans 7 stages. `scope` decides the unit a stage's freshness
# is keyed on: a CELL stage is per (prof, state); a PROFESSION stage's input is ALL of a
# profession's states, so it stamps once at PROV_DIR/<prof>/_profession.json. The global
# publish `fanout` tail stays OUTSIDE the contract (its freshness is "did any profession
# change", which the runner decides).
_SCOPE = {
    "pull": "cell", "clean": "cell", "trim": "cell", "extract": "cell",
    "schema": "profession", "mapprep": "profession", "publish": "profession",
}

# Input/output dirs for the CELL stages (unchanged shape). pull's input is the frozen
# index (handled in input_hash), and profession stages read/write whole-profession trees
# (handled directly in input_hash/_out_exists), so neither needs an _IN/_OUT entry.
_IN = {"clean": TEXT_DIR, "trim": CLEAN_DIR, "extract": TRIMMED_DIR}
_OUT = {"clean": CLEAN_DIR, "trim": TRIMMED_DIR, "extract": STRUCTURED_DIR}

# Prompt keys per stage (a tuple, so a multi-prompt stage like map_prep lists all of
# them). Single-key stages hash identically to the old single-key form.
_PROMPT_KEYS = {
    "pull": (), "clean": (), "trim": ("trim_state",), "extract": ("extract_state",),
    "schema": ("discover_schema",),
    "mapprep": ("map_prep_spec", "map_prep_apply", "map_prep_bucket_text",
                "map_prep_bucket_text_per_item_design", "map_prep_bucket_text_per_item_assign"),
    "publish": (),
}

# Stage name -> config/models.yaml key (only the LLM stages; note map_prep's key differs
# from the stage name "mapprep"). clean/pull/publish use no model.
_MODEL_KEY = {"trim": "trim", "extract": "extract", "schema": "schema", "mapprep": "map_prep"}


def _model_for_stage(stage: str) -> str | None:
    """The model that produces a stage's output, from config/models.yaml (None for the
    no-LLM stages). Imported lazily to avoid a config↔provenance import cycle."""
    key = _MODEL_KEY.get(stage)
    if key is None:
        return None
    from pipeline.config.loaders import model_for
    return model_for(key)

# Manual code-version tags — bump when a stage's logic should invalidate old outputs.
CODE_VERSION = {"clean": 1, "trim": 1, "extract": 1,
                "pull": 1, "schema": 1, "mapprep": 1, "publish": 1}

PROV_DIR = RESULTS_DIR / "provenance"


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _payload_hash(path) -> str | None:
    """Hash a JSON file's meaningful content — defensively dropping any `_provenance`
    key so an (inlined) stamp can never perturb the hash."""
    d = read_json(path)
    if d is None:
        return None
    if isinstance(d, dict):
        d = {k: v for k, v in d.items() if k != "_provenance"}
    return _sha(json.dumps(d, sort_keys=True, ensure_ascii=False))


def _dir_hash(d) -> str | None:
    """Order-independent content hash of every record JSON in a directory — the input
    hash for a profession-scoped stage (whose input is all of a profession's state files).
    None when the dir is absent or holds no records."""
    if not d.exists():
        return None
    parts = []
    for f in sorted(d.glob("*.json")):
        if f.name.startswith("_"):
            continue
        h = _payload_hash(f)
        if h is not None:
            parts.append(f"{f.name}={h}")
    return _sha("|".join(parts)) if parts else None


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


def input_hash(stage: str, prof: str, state: str | None = None) -> str | None:
    if stage == "clean":
        return _payload_hash(_clean_source_path(prof, state))
    if stage == "pull":
        # pull's input is this state's slice of the frozen profession index (the url map
        # that determines what gets fetched), not a stage-output file.
        from pipeline.config.loaders import load_profession_index, matched_for
        idx = load_profession_index(prof)
        nodes = matched_for(idx, state) if idx else None
        return _sha(json.dumps(nodes, sort_keys=True, ensure_ascii=False)) if nodes else None
    if _SCOPE[stage] == "cell":                       # trim, extract
        return _payload_hash(_IN[stage] / prof / f"{state}.json")
    if stage == "schema":                             # profession: all trimmed states
        return _dir_hash(TRIMMED_DIR / prof)
    if stage == "mapprep":                            # profession: all structured states
        return _dir_hash(STRUCTURED_DIR / prof)
    if stage == "publish":                            # profession: structured + map_prep
        s, m = _dir_hash(STRUCTURED_DIR / prof), _dir_hash(MAP_PREP_DIR / prof)
        return _sha(f"{s or ''}|{m or ''}") if (s or m) else None
    return None


@lru_cache(maxsize=None)
def recipe_hash(stage: str, prof: str, model: str | None = None) -> str:
    """Hash of everything besides the input that determines this stage's output:
    code version + prompt text + model + (for extract) the profession schema.

    `model` is the model actually used (threaded from the stage's --model). When None we
    fall back to the stage's canonical default table, so a default-model run hashes
    identically to before — only a non-default override shifts the recipe (and correctly
    reads stale against the canonical recipe until re-run)."""
    parts = [f"code={CODE_VERSION[stage]}"]
    for key in _PROMPT_KEYS[stage]:
        parts.append("prompt=" + _sha(load_prompt(key)))
    m = model or _model_for_stage(stage)
    if m:
        parts.append("model=" + m)
    if stage == "extract":
        parts.append("schema=" + (_payload_hash(DISCOVERED_DIR / f"{prof}.json") or "none"))
    return _sha("|".join(parts))


def stamp(stage: str, prof: str, state: str | None = None, model: str | None = None) -> dict:
    d = {"input_hash": input_hash(stage, prof, state),
         "recipe_hash": recipe_hash(stage, prof, model)}
    if stage == "extract":
        uh = _umbrella_hash(state)
        if uh is not None:
            d["umbrella_hash"] = uh
    return d


def _prov_path(prof: str, state: str):
    return PROV_DIR / prof / f"{state}.json"


def _prof_prov_path(prof: str):
    """Profession-scoped stamps live in one file per profession, not per state."""
    return PROV_DIR / prof / "_profession.json"


def _prov_path_for(stage: str, prof: str, state: str | None):
    return _prof_prov_path(prof) if _SCOPE[stage] == "profession" else _prov_path(prof, state)


def _out_exists(stage: str, prof: str, state: str | None) -> bool:
    """Does this stage's output exist? Cell stages write <dir>/<prof>/<state>.json;
    profession stages write a single per-profession artifact."""
    if stage == "pull":
        return (TEXT_DIR / prof / f"{state}.json").exists()
    if _SCOPE[stage] == "cell":
        return (_OUT[stage] / prof / f"{state}.json").exists()
    if stage == "schema":
        return (DISCOVERED_DIR / f"{prof}.json").exists()
    if stage == "mapprep":
        return (MAP_PREP_DIR / prof).exists()
    if stage == "publish":
        return (WEB_PUBLIC_DIR / "data" / f"{prof}.json").exists()
    return False


def _load_prov(prof: str, state: str) -> dict:
    return read_json(_prov_path(prof, state), {})


def record(stage: str, prof: str, state: str | None = None, model: str | None = None) -> None:
    """Stamp one stage into its provenance file (read-modify-write, so the other stages'
    stamps are preserved). Call right after writing the stage output. Pass the model
    actually used (the stage's --model) so an off-default run is captured. Profession
    stages ignore `state` and stamp the per-profession file.

    `stamped_at` is metadata only — check() compares input_hash/recipe_hash, never the
    timestamp, so re-running with identical content doesn't read as stale."""
    from datetime import datetime
    p = _prov_path_for(stage, prof, state)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = read_json(p, {})
    data[stage] = {**stamp(stage, prof, state, model), "stamped_at": datetime.now().isoformat(timespec="seconds")}
    write_json_atomic(p, data, sort_keys=True)


def check(stage: str, prof: str, state: str | None = None) -> str:
    """current | stale | unstamped | missing (missing = the stage output isn't there)."""
    if not _out_exists(stage, prof, state):
        return "missing"
    p = read_json(_prov_path_for(stage, prof, state), {}).get(stage)
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


def _iter_done_professions():
    """Professions that have at least one structured record (a schema/mapprep/publish
    stamp is only meaningful once extraction has produced something to derive from)."""
    if not STRUCTURED_DIR.exists():
        return
    for pdir in sorted(STRUCTURED_DIR.iterdir()):
        if pdir.is_dir() and any(f.suffix == ".json" and not f.name.startswith("_")
                                 for f in pdir.iterdir()):
            yield pdir.name


# Profession-scoped stages, in dependency order (schema ⊂ trimmed, mapprep ⊂ structured,
# publish ⊂ structured+mapprep). _backfill() deliberately does NOT touch these — it stamps
# only the per-cell chain — so baselining them is a separate, opt-in assertion.
PROF_STAGES = ("schema", "mapprep", "publish")


def _backfill_professions(professions: set[str] | None = None) -> None:
    """Baseline the PROFESSION-scoped stamps (schema/mapprep/publish) as current for every
    done profession whose output for that stage exists. Separate from `_backfill` on
    purpose: it must NOT re-stamp the per-cell stages, because doing so would clobber the
    honest `stale`/`unstamped` signal on cells mid-refresh (e.g. text re-pulled but not yet
    re-cleaned). Run once so the runner reads live professions as `current` end-to-end
    instead of re-running map_prep just because it was never stamped."""
    n = 0
    for prof in _iter_done_professions():
        if professions is not None and prof not in professions:
            continue
        stamped = [s for s in PROF_STAGES if _out_exists(s, prof, None)]
        for s in stamped:
            record(s, prof)
        if stamped:
            n += 1
    scope = f" for {len(professions)} professions" if professions else ""
    print(f"backfilled profession-scoped provenance for {n} professions{scope} "
          f"(baseline = current recipe; per-cell stamps untouched)")


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
    bf = sub.add_parser("backfill", help="stamp existing per-cell outputs as the current baseline")
    bf.add_argument("--professions", default="",
                    help="Comma-separated subset to stamp (default: all done cells)")
    bfp = sub.add_parser("backfill-professions",
                         help="baseline the profession-scoped stamps (schema/mapprep/publish); "
                              "per-cell stamps untouched")
    bfp.add_argument("--professions", default="",
                     help="Comma-separated subset to stamp (default: all done professions)")
    args = ap.parse_args()
    if args.cmd == "report":
        _report()
    elif args.cmd == "backfill-professions":
        profs = {p.strip() for p in args.professions.split(",") if p.strip()} or None
        _backfill_professions(profs)
    else:
        profs = {p.strip() for p in args.professions.split(",") if p.strip()} or None
        _backfill(profs)


if __name__ == "__main__":
    main()
