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
SITE_DIR             = PIPELINE_ROOT / "publish" / "site"        # legacy jQuery+Bootstrap viewer
WEB_PUBLIC_DIR       = PIPELINE_ROOT / "publish" / "web" / "public"  # Next.js viewer's public/ (canonical)
