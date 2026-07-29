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

It is INCREMENTAL: a profession is rebuilt only when its `publish` provenance
(a content hash of its structured/ + map_prep/ inputs) isn't current — so a
one-profession change only touches that profession. --force rebuilds everything.
The per-profession `publish` and the cross-profession `fanout` are now the runner's
stages (pipeline.pipeline_stages); this module is a thin caller of them.

What it does NOT do: re-extract or re-run map_prep (those are the LLM stages).
If structured data changed, run those first; then run this.

Usage:
  python -m pipeline.publish.refresh_all                # incremental: changed professions only
  python -m pipeline.publish.refresh_all --deploy       # ...then redeploy Vercel
  python -m pipeline.publish.refresh_all --force        # rebuild every profession
  python -m pipeline.publish.refresh_all --professions optometry dietetics
  python -m pipeline.publish.refresh_all --dry-run      # print the plan, build nothing
"""

from __future__ import annotations

import argparse
import subprocess
import sys

from pipeline import provenance
from pipeline.paths import PIPELINE_ROOT, core_professions
from pipeline.pipeline_stages import run_to, run_fanout

WEB_DIR = PIPELINE_ROOT / "publish" / "web"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", nargs="+", help="Limit to these (default: all core professions)")
    ap.add_argument("--force", action="store_true", help="Rebuild every profession, ignore publish freshness")
    ap.add_argument("--deploy", action="store_true", help="Redeploy Vercel (prod) after refreshing")
    ap.add_argument("--payload-only", action="store_true",
                    help="Tags/table/map changed but browse didn't: skip per-state browse regeneration "
                         "(the CPU hog) and the browse-builder stages. ~10x faster. Rebuilds payloads + tag sheet only.")
    ap.add_argument("--skip-consistency-check", action="store_true",
                    help="Bypass the cross-field consistency gate (not recommended).")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print which professions would rebuild and stop — spends nothing, writes nothing.")
    args = ap.parse_args()

    all_profs = args.professions or core_professions()
    if not all_profs:
        sys.exit("no core professions found in structured/")

    # --force also forces the content-hash upload skip in blob_upload to
    # re-upload everything (subprocesses inherit this env).
    if args.force:
        import os
        os.environ["BLOB_FORCE_UPLOAD"] = "1"

    # Incremental skip = publish provenance (replaces the old .refresh_manifest fingerprint).
    # An explicit --professions list or --force rebuilds regardless of freshness.
    if args.force or args.professions:
        changed = list(all_profs)
    else:
        changed = [p for p in all_profs if provenance.check("publish", p) != "current"]

    print(f"Core professions: {len(all_profs)} ({', '.join(all_profs)})")
    print(f"Changed / to rebuild: {changed or 'none'}")
    print("(deterministic / no LLM calls)")

    if not changed:
        print("\nNothing changed — site already reflects current data. Done.")
        return

    if args.dry_run:
        print(f"\n--dry-run: would rebuild publish for {len(changed)} profession(s): {', '.join(changed)}")
        print(f"           then run the cross-profession fanout"
              f"{' (payload-only)' if args.payload_only else ''}. Nothing built.")
        return

    opts = {"payload_only": args.payload_only, "skip_consistency": args.skip_consistency_check}
    results: list[tuple[str, bool]] = []

    # 1. Per-profession publish — only the changed ones. start="verify" keeps this a pure
    #    downstream rebuild (cell stages are out of range, so it can never silently
    #    re-extract) while letting provenance run verify + mapprep when the data actually
    #    moved. (Until 2026-07-29 this used start="publish" because the chain CRASHED at
    #    verify — so refreshed data shipped with unverified negatives and stale buckets.)
    for p in changed:
        res = run_to("publish", p, start="verify", force=False, yes=True, opts=opts)
        results.append((f"publish:{p}", res["ok"]))

    # 2. Cross-profession fan-out (tag sheet, scope, scorecard, browse, analysis) — once.
    results.extend(run_fanout(changed, payload_only=args.payload_only))

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
