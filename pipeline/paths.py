"""Canonical filesystem paths for the pipeline.

Every stage script imports from here so paths can move atomically.
Stage scripts also depend on this for fail-loud behavior:
the dirs are created lazily by each stage as it writes, never up front,
so a missing dir at read time means the previous stage didn't run.
"""

from __future__ import annotations

from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parent

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
WEB_PUBLIC_DIR       = PIPELINE_ROOT / "publish" / "web" / "public"  # Next.js viewer's public/


# Minimum extracted states for a profession to count as "fully wired" (vs. the
# UT-only scaffolding the OPLR held-out test leaves behind, 1 state each).
MIN_STATES_FOR_CORE = 10


def core_professions(min_states: int = MIN_STATES_FOR_CORE) -> list[str]:
    """The fully-wired professions — those with at least `min_states` extracted
    states under `structured/` — alphabetical.

    Single source of truth for "which professions are real," so publish stages
    (scorecard, tag sheet, refresh_all, …) agree and don't each reinvent the
    filter. Excludes partial scaffolding (e.g. a 1-state held-out test run).
    """
    if not STRUCTURED_DIR.exists():
        return []
    out: list[str] = []
    for d in sorted(STRUCTURED_DIR.iterdir()):
        if not d.is_dir():
            continue
        n = sum(
            1 for f in d.iterdir()
            if f.suffix == ".json" and not f.name.startswith("_")
        )
        if n >= min_states:
            out.append(d.name)
    return out
