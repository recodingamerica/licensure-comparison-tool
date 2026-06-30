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
from _records import record_files  # noqa: E402
from eval.check_consistency import check_record  # noqa: E402

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
    ap.add_argument("--payload-only", action="store_true",
                    help="Tags/table/map changed but browse didn't: skip per-state browse regeneration "
                         "(the CPU hog) and the browse-builder stages. ~10x faster. Rebuilds payloads + tag sheet only.")
    ap.add_argument("--skip-consistency-check", action="store_true",
                    help="Bypass the cross-field consistency gate (not recommended).")
    args = ap.parse_args()

    all_profs = args.professions or core_professions()
    if not all_profs:
        sys.exit("no core professions found in structured/")

    # --force also forces the content-hash upload skip in blob_upload to
    # re-upload everything (subprocesses inherit this env).
    if args.force:
        import os
        os.environ["BLOB_FORCE_UPLOAD"] = "1"

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

    # Pre-publish gate: don't ship records that violate the prompt's own
    # cross-field invariants (e.g. a title-protection rung flipped to `license`).
    # Covers any extract path (interactive or batch). Override with
    # --skip-consistency-check if a flagged record is being intentionally shipped.
    if not args.skip_consistency_check:
        viols: list[dict] = []
        for p in changed:
            for jf in record_files(STRUCTURED_DIR / p):
                try:
                    rec = json.loads(jf.read_text())
                except json.JSONDecodeError as e:
                    # A corrupt record can't be consistency-checked. Don't skip
                    # it silently into publish — make it a gate violation so the
                    # build halts and the bad file gets surfaced.
                    viols.append({"profession": p, "state": jf.stem,
                                  "rule": "unreadable_json", "detail": str(e)[:120]})
                    continue
                viols.extend(check_record(p, jf.stem, rec))
        if viols:
            print(f"\n✗ consistency gate: {len(viols)} violation(s) in records to be published — NOT building.")
            for v in viols:
                print(f"   [{v['profession']}/{v['state']}] {v['rule']}: {v['detail']}")
            print("Re-extract the flagged record(s), or pass --skip-consistency-check to override.")
            sys.exit(1)
        print("consistency gate: clean")

    results: list[tuple[str, bool]] = []

    # 1. Per-profession payloads (+ per-state browse) — only the changed ones.
    fe_cmd = ["--payload-only"] if args.payload_only else []
    for p in changed:
        ok = run([PY, "-m", "pipeline.publish.build_frontend", "--profession", p, *fe_cmd],
                 f"build_frontend {p}{' (payload-only)' if args.payload_only else ''}")
        results.append((f"build_frontend:{p}", ok))
        if ok and not args.payload_only:
            # In payload-only mode the browse blobs are intentionally NOT
            # rebuilt, so the fingerprint doesn't fully reflect what's on Blob —
            # don't record it, or a later full refresh would wrongly skip.
            manifest[p] = fps[p]  # only record success

    # 1a. Field dictionaries — regenerate the methodology-tracks-code data dictionary
    #     for each changed profession (deterministic; reads the model + a structured
    #     record). Keeps docs/methodology/<prof>_field_dictionary.{md,json} from drifting.
    for p in changed:
        run([PY, "-m", "pipeline.publish.generate_field_dictionary", "--profession", p],
            f"field_dictionary {p}")

    # 1b. Similarity / outlier analysis — deterministic (no LLM). Reads the payloads
    #     we just built, writes results/analysis/, then publish_analysis mirrors to
    #     public/data/analysis/ + Blob (like the payloads). Best-effort per profession
    #     (skips ones without map_prep).
    for p in changed:
        run([PY, "-m", "pipeline.analyze.similarity", "--profession", p, "--json"], f"similarity {p}")
    # 1b-direction: re-stamp novel-policy restrictive/permissive direction (#52c).
    #   similarity (above) rewrites results/analysis/ and DROPS `direction`, so this
    #   must run after it and before publish_analysis ships. Cached by (field,value),
    #   so re-runs only classify genuinely-new pairs (≈ free here). Best-effort — not
    #   gated into `results`, so a failure can't block the deploy (mirrors the
    #   similarity loop), it just leaves direction absent that round.
    if changed:
        run([PY, "-m", "pipeline.analyze.classify_novel_direction",
             "--professions", ",".join(changed)], "classify_novel_direction")
    results.append(("publish_analysis",
                    run([PY, "-m", "pipeline.analyze.publish_analysis"], "publish_analysis")))

    # 2. Tag sheet aggregates the per-item tags, so always refresh it.
    results.append(("build_tag_sheet",
                    run([PY, "-m", "pipeline.publish.build_tag_sheet", "--upload"], "build_tag_sheet")))

    # 3-5. Scorecard + browse artifacts are unaffected by a tags-only change,
    #      so skip them in payload-only mode (they're the other slow stages).
    if not args.payload_only:
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
