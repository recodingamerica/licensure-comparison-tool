"""Refresh ALL downstream site artifacts from existing extraction output.

The pipeline's expensive stages (extract, map_prep) call LLMs and run only when
the underlying data changes. Everything *downstream* of them — the per-profession
payloads, the choropleth/map data, the tag sheet, the scorecard, the state and
umbrella browse data — is pure deterministic reshaping of files already on disk
(`structured/`, `map_prep/`, `umbrella_scope/`, ...). None of it calls an LLM.

Those publish stages were scattered one-off scripts, so artifacts drifted (e.g.
the scorecard sat 3 weeks stale, missing a whole profession). This orchestrator
runs them all in one shot — NO LLM CALLS — so after any data change you run this
once and the entire site is consistent again.

It is INCREMENTAL: it fingerprints each profession's inputs (structured/ +
map_prep/) and skips re-building/re-uploading professions whose inputs are
unchanged since the last run (the slow part is uploading ~50 browse files per
profession to Blob). A full refresh re-uploads everything; a one-profession
change only touches that profession. Use --force to rebuild everything.

What it does NOT do: re-extract or re-run map_prep (those are the LLM stages).
If structured data changed, run those first; then run this.

Usage:
  python -m pipeline.publish.refresh_all                # incremental: changed professions only
  python -m pipeline.publish.refresh_all --deploy       # ...then redeploy Vercel
  python -m pipeline.publish.refresh_all --force        # rebuild every profession
  python -m pipeline.publish.refresh_all --professions optometry dietetics
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import STRUCTURED_DIR, MAP_PREP_DIR, RESULTS_DIR, PIPELINE_ROOT, core_professions  # noqa: E402

PY = sys.executable
WEB_DIR = PIPELINE_ROOT / "publish" / "web"
# Local cache of last-built input fingerprints (not committed — derived state).
MANIFEST = RESULTS_DIR / ".refresh_manifest.json"


def fingerprint(profession: str) -> str:
    """Content hash of a profession's publish inputs (structured + map_prep).
    Changes iff any of those files change → drives the incremental skip."""
    h = hashlib.sha256()
    for base in (STRUCTURED_DIR / profession, MAP_PREP_DIR / profession):
        if not base.exists():
            continue
        for f in sorted(base.glob("*.json")):
            h.update(f.name.encode())
            h.update(f.read_bytes())
    return h.hexdigest()


def run(cmd: list[str], label: str) -> bool:
    print(f"\n=== {label} ===\n$ {' '.join(cmd)}", flush=True)
    r = subprocess.run(cmd, cwd=PIPELINE_ROOT.parent)
    if r.returncode != 0:
        print(f"!! {label} FAILED (exit {r.returncode}) — continuing", flush=True)
        return False
    return True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", nargs="+", help="Limit to these (default: all core professions)")
    ap.add_argument("--force", action="store_true", help="Rebuild every profession, ignore the fingerprint cache")
    ap.add_argument("--deploy", action="store_true", help="Redeploy Vercel (prod) after refreshing")
    args = ap.parse_args()

    all_profs = args.professions or core_professions()
    if not all_profs:
        sys.exit("no core professions found in structured/")

    manifest: dict[str, str] = {}
    if MANIFEST.exists() and not args.force:
        try:
            manifest = json.loads(MANIFEST.read_text())
        except Exception:
            manifest = {}

    fps = {p: fingerprint(p) for p in all_profs}
    if args.force or args.professions:
        changed = list(all_profs)  # explicit list or --force ⇒ rebuild those
    else:
        changed = [p for p in all_profs if manifest.get(p) != fps[p]]

    print(f"Core professions: {len(all_profs)} ({', '.join(all_profs)})")
    print(f"Changed / to rebuild: {changed or 'none'}")
    print("(deterministic / no LLM calls)")

    if not changed:
        print("\nNothing changed — site already reflects current data. Done.")
        return

    results: list[tuple[str, bool]] = []

    # 1. Per-profession payloads (+ per-state browse) — only the changed ones.
    for p in changed:
        ok = run([PY, "-m", "pipeline.publish.build_frontend", "--profession", p],
                 f"build_frontend {p}")
        results.append((f"build_frontend:{p}", ok))
        if ok:
            manifest[p] = fps[p]  # only record success

    # 2-5. Global artifacts aggregate across all professions, so refresh them
    #      whenever anything changed.
    results.append(("build_tag_sheet",
                    run([PY, "-m", "pipeline.publish.build_tag_sheet", "--upload"], "build_tag_sheet")))
    results.append(("scorecard",
                    run([PY, "-m", "pipeline.publish.cross_comparison_scorecard", "--upload"], "scorecard")))
    results.append(("build_state_browse",
                    run([PY, "-m", "pipeline.publish.build_state_browse"], "build_state_browse")))
    results.append(("build_umbrella_browse",
                    run([PY, "-m", "pipeline.publish.build_umbrella_browse"], "build_umbrella_browse")))

    MANIFEST.write_text(json.dumps(manifest, indent=2))

    print("\n==== summary ====")
    for name, ok in results:
        print(f"  {'ok ' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in results if not ok]

    if args.deploy:
        if failed:
            print(f"\nNOT deploying — {len(failed)} stage(s) failed: {failed}")
            sys.exit(1)
        # Deploy runs from WEB_DIR, which is the `utah-licensing` project. (The
        # repo root has a stray .vercel linked to a different project — never
        # deploy from there.)
        print("\n=== deploy (vercel --prod) ===", flush=True)
        r = subprocess.run(["npx", "vercel", "--prod", "--yes"], cwd=WEB_DIR)
        if r.returncode != 0:
            sys.exit(f"vercel deploy failed (exit {r.returncode})")
        print("deployed → utah-licensing.vercel.app")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
