"""Canonical filesystem paths for the pipeline.

Every stage script imports from here so paths can move atomically.
Stage scripts also depend on this for fail-loud behavior:
the dirs are created lazily by each stage as it writes, never up front,
so a missing dir at read time means the previous stage didn't run.
"""

from __future__ import annotations

from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PIPELINE_ROOT.parent          # the git repo root (parents[2] of a stage module)

CONFIG_DIR = PIPELINE_ROOT / "config"
RESULTS_DIR = PIPELINE_ROOT / "results"
LOGS_DIR = PIPELINE_ROOT / "logs"

# Stage output directories
HIERARCHY_DIR        = RESULTS_DIR / "hierarchy"           # state → tree (one-time per state)
PROFESSION_INDEX_DIR = RESULTS_DIR / "profession_index"    # profession → matched nodes per state
TEXT_DIR             = RESULTS_DIR / "text"                # raw fetched section text
CLEAN_DIR            = RESULTS_DIR / "clean"               # source-keyed cleanup
TRIMMED_DIR          = RESULTS_DIR / "trimmed"             # LLM keep/drop
DISCOVERED_DIR       = RESULTS_DIR / "discovered"          # pass 1b aggregator output
STRUCTURED_DIR       = RESULTS_DIR / "structured"          # pass 2 per-state extraction
MAP_PREP_DIR         = RESULTS_DIR / "map_prep"            # pass 3 normalization + text-bucket tags
SCOPE_VOCAB_DIR      = RESULTS_DIR / "scope_vocab"         # per-profession discovered scope-matrix vocab
WEB_PUBLIC_DIR       = PIPELINE_ROOT / "publish" / "web" / "public"  # Next.js viewer's public/
WEB_DATA_DIR         = WEB_PUBLIC_DIR / "data"             # built site payloads (one per published prof)


# Minimum extracted states for a profession to count as "fully wired" (vs. the
# UT-only scaffolding the OPLR held-out test leaves behind, 1 state each).
MIN_STATES_FOR_CORE = 10


def _publish_excluded() -> set[str]:
    """Professions marked `publish: false` in professions.yaml — retired from the site
    without deleting their data. Honoured by BOTH profession sets below: the flag has to
    mean one thing everywhere, or a profession gets dropped from the scorecard while a
    stale payload keeps it in the browse view and the occupation picker (#121)."""
    try:
        from pipeline.config.loaders import registry_professions  # deferred: loaders imports us
    except ImportError:
        return set()   # the import cycle is the only failure worth absorbing
    # A malformed professions.yaml PROPAGATES. Swallowing it here would silently
    # un-retire an occupation — the config says don't publish, the code publishes anyway —
    # which is the failure mode this flag exists to prevent.
    return {k for k, v in registry_professions().items()
            if isinstance(v, dict) and v.get("publish") is False}


def core_professions(min_states: int = MIN_STATES_FOR_CORE) -> list[str]:
    """The fully-wired professions — those with at least `min_states` extracted
    states under `structured/` — alphabetical.

    Single source of truth for "which professions are real," so publish stages
    (scorecard, tag sheet, refresh_all, …) agree and don't each reinvent the
    filter. Excludes partial scaffolding (e.g. a 1-state held-out test run).

    A state count alone can't tell you a profession is worth shipping: public_adjuster
    cleared the threshold at 11/50 and still looked broken next to 50-state neighbours
    (#121). `publish: false` in professions.yaml opts one out — a config decision, not
    a code edit, and it keeps the opt-out next to the profession it describes.
    """
    if not STRUCTURED_DIR.exists():
        return []
    excluded = _publish_excluded()
    out: list[str] = []
    for d in sorted(STRUCTURED_DIR.iterdir()):
        if not d.is_dir() or d.name in excluded:
            continue
        n = sum(
            1 for f in d.iterdir()
            if f.suffix == ".json" and not f.name.startswith("_")
        )
        if n >= min_states:
            out.append(d.name)
    return out


def published_professions(data_dir: Path | None = None) -> list[str]:
    """The professions the SITE actually ships — those with a built payload in
    `publish/web/public/data/` — alphabetical.

    Single source of truth for "which professions are published," the companion to
    `core_professions()` ("which professions are real"). Three copies of this glob had
    drifted apart (client/handoff_doc, client/export_data, and a hand-maintained literal
    list in publish/build_state_browse), and the literal one silently fell a profession
    behind: dietetics shipped to the site but was missing from every per-state browse
    blob. Derive, don't hand-maintain.

    Intersected with the registry so cross-profession artifacts that also live in data/
    — scorecard, tag_sheet, scope_capabilities, and any future one — can never be
    miscounted as a profession. An allowlist that auto-corrects, vs. a blocklist that
    rots. `data_dir` exists so callers with their own DATA_DIR seam (and tests) can
    point it elsewhere; production callers pass nothing.

    A payload can outlive the decision to ship a profession — the site prebuild pulls
    every blob down, so a retired occupation reappears locally until its blob is deleted.
    `publish: false` therefore wins over the presence of a file.
    """
    from pipeline.config.loaders import all_profession_ids  # deferred: loaders imports us
    d = data_dir if data_dir is not None else WEB_DATA_DIR
    if not d.exists():
        return []
    registry = set(all_profession_ids()) - _publish_excluded()
    return sorted(f.stem for f in d.glob("*.json") if f.stem in registry)
