"""End-to-end pipeline orchestrator.

Runs each stage for one profession, top to bottom. Use --steps to skip
forward (e.g. to re-run only extraction after a prompt change).

Stages:
  hierarchy    — discover.build_hierarchy (profession-agnostic; reuses cached output)
  match        — discover.match_profession  → profession_index/<prof>.json
  pull         — ingest.pull_text           → text/<prof>/<STATE>.json
  clean        — ingest.clean_text          → clean/<prof>/<STATE>.json
  trim         — ingest.trim_state          → trimmed/<prof>/<STATE>.json
  discover     — extract.discover_schema    → discovered/<prof>.json
  extract      — extract.extract_state      → structured/<prof>/<STATE>.json
  publish      — publish.build_frontend     → publish/site/data.json

NOT YET IMPLEMENTED — each step shells out to the underlying script. Once the
hierarchy + match stages are real, this orchestrator becomes the canonical
way to run the pipeline.

Usage:
  python -m pipeline.run --profession podiatry [--steps pull,clean,trim,extract,publish]
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    sys.exit("run.py orchestrator not yet implemented — invoke individual stage scripts directly for now")
