"""End-to-end pipeline orchestrator (Path 1 — one command per profession).

Runs each stage for one profession, top to bottom. Every stage already works as
a standalone module; this just chains them in order and stops on the first
failure. Use --steps to run a subset (e.g. re-extract + republish after a prompt
change), --states to scope to specific states, --dry-run to print the plan.

Stages (in order):
  match     — discover.match_profession   → profession_index/<prof>.json
  pull      — ingest.pull_text            → text/<prof>/<STATE>.json
  clean     — ingest.clean_text           → clean/<prof>/<STATE>.json
  trim      — ingest.trim_state           → trimmed/<prof>/<STATE>.json
  discover  — extract.discover_schema     → discovered/<prof>.json
  extract   — extract.extract_state       → structured/<prof>/<STATE>.json
  map_prep  — map_prep.refresh            → map_prep/<prof>/*.json
  publish   — publish.refresh_all         → blob payloads (+ vercel with --deploy)

Usage:
  python -m pipeline.run --profession podiatry
  python -m pipeline.run --profession podiatry --states IL,PA
  python -m pipeline.run --profession podiatry --steps extract,map_prep,publish
  python -m pipeline.run --profession podiatry --deploy
  python -m pipeline.run --profession podiatry --dry-run

Caveat: for states where the profession is buried in a shared chapter or on a
non-Justia source (PA pa_legis, IL ILCS blobs), `match`/`pull` need a
config/state_structure.yaml entry first — this orchestrator surfaces those as
empty pulls in the per-stage output, it cannot invent the scoping.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

PY = sys.executable
REPO_ROOT = Path(__file__).resolve().parent.parent

# Ordered stages. `module` is the -m target; `args(opts)` returns the extra argv.
# `scoped` = honors --states; `force` = honors --force; `deploy` = honors --deploy.
STAGES: list[dict] = [
    {"name": "match",    "module": "pipeline.discover.match_profession",
     "args": lambda o: ["--profession", o.profession]},
    {"name": "pull",     "module": "pipeline.ingest.pull_text",     "scoped": True,
     "args": lambda o: ["--profession", o.profession]},
    {"name": "clean",    "module": "pipeline.ingest.clean_text",    "scoped": True,
     "args": lambda o: ["--profession", o.profession]},
    {"name": "trim",     "module": "pipeline.ingest.trim_state",    "scoped": True,
     "args": lambda o: ["--profession", o.profession]},
    {"name": "discover", "module": "pipeline.extract.discover_schema",
     "args": lambda o: ["--profession", o.profession]},
    {"name": "extract",  "module": "pipeline.extract.extract_state", "scoped": True, "force": True,
     "args": lambda o: ["--profession", o.profession]},
    {"name": "map_prep", "module": "pipeline.map_prep.refresh",
     "args": lambda o: ["--professions", o.profession]},
    {"name": "publish",  "module": "pipeline.publish.refresh_all", "deploy": True,
     "args": lambda o: ["--professions", o.profession]},
]
STAGE_NAMES = [s["name"] for s in STAGES]


def build_argv(stage: dict, opts) -> list[str]:
    argv = [PY, "-m", stage["module"], *stage["args"](opts)]
    if stage.get("scoped") and opts.states:
        argv += ["--states", opts.states]
    if stage.get("force") and opts.force:
        argv += ["--force"]
    if stage.get("deploy") and opts.deploy:
        argv += ["--deploy"]
    return argv


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profession", required=True, help="Profession slug from professions.yaml")
    ap.add_argument("--steps", default="", help=f"Comma-separated subset of: {','.join(STAGE_NAMES)} (default: all)")
    ap.add_argument("--states", default="", help="Comma-separated states to scope pull/clean/trim/extract")
    ap.add_argument("--deploy", action="store_true", help="Pass --deploy to the publish stage (vercel --prod)")
    ap.add_argument("--force", action="store_true", help="Pass --force to extract (re-extract already-present states)")
    ap.add_argument("--dry-run", action="store_true", help="Print the stage commands without running them")
    opts = ap.parse_args()

    if opts.steps:
        want = [s.strip() for s in opts.steps.split(",") if s.strip()]
        unknown = [s for s in want if s not in STAGE_NAMES]
        if unknown:
            sys.exit(f"unknown step(s): {unknown}; valid: {STAGE_NAMES}")
        selected = [s for s in STAGES if s["name"] in want]
    else:
        selected = STAGES

    print(f"=== run.py: profession={opts.profession} steps={[s['name'] for s in selected]} "
          f"states={opts.states or 'all'} deploy={opts.deploy} ===")

    results: list[tuple[str, str]] = []
    for stage in selected:
        argv = build_argv(stage, opts)
        printable = " ".join(argv[1:])  # drop the python path for readability
        print(f"\n--- [{stage['name']}] {printable} ---", flush=True)
        if opts.dry_run:
            results.append((stage["name"], "dry-run"))
            continue
        t0 = time.time()
        rc = subprocess.run(argv, cwd=REPO_ROOT).returncode
        dt = time.time() - t0
        if rc != 0:
            results.append((stage["name"], f"FAILED rc={rc} ({dt:.0f}s)"))
            print(f"\n✗ stage '{stage['name']}' failed (rc={rc}); stopping.", flush=True)
            _summary(results)
            return rc
        results.append((stage["name"], f"ok ({dt:.0f}s)"))

    _summary(results)
    return 0


def _summary(results: list[tuple[str, str]]) -> None:
    print("\n=== run.py summary ===")
    for name, status in results:
        print(f"  {name:10} {status}")


if __name__ == "__main__":
    raise SystemExit(main())
