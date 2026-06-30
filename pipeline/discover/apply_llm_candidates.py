"""Apply reviewed LLM-mapper candidates into profession_index (the loop's back-half).

Reads results/profession_index/_llm_candidates/<prof>.json (Pass-1 + Pass-2 +
human review) and writes the licensed mappings into
results/profession_index/<prof>.json so pull_text can pull them.

SURGICAL by default: only touches states the candidate file marks licensed with a
chapter URL, and SKIPS states that already have a `matched` node unless --overwrite
(so manual additions / prior pulls are preserved — re-running match_profession would
wipe those; this never does). States still flagged umbrella (unresolved) or
not-licensed are left alone (run Pass-2 first to resolve umbrellas).

Run:
  pipeline/.venv/bin/python -m pipeline.discover.apply_llm_candidates --profession electrician            # dry-run (default)
  pipeline/.venv/bin/python -m pipeline.discover.apply_llm_candidates --profession electrician --write
  pipeline/.venv/bin/python -m pipeline.discover.apply_llm_candidates --profession electrician --write --overwrite
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from paths import PROFESSION_INDEX_DIR as INDEX_DIR  # noqa: E402

CAND_DIR = INDEX_DIR / "_llm_candidates"


def apply(prof: str, write: bool, overwrite: bool) -> None:
    cand_fp = CAND_DIR / f"{prof}.json"
    if not cand_fp.exists():
        sys.exit(f"no candidate file: {cand_fp} — run the mapper first")
    idx_fp = INDEX_DIR / f"{prof}.json"
    idx = json.loads(idx_fp.read_text()) if idx_fp.exists() else {"profession": prof, "by_state": {}}
    by_state = idx.setdefault("by_state", {})
    cand = json.loads(cand_fp.read_text())

    applied, skipped_existing, skipped_unresolved = [], [], []
    for r in cand.get("states", []):
        st = r["state"]
        if not r.get("licensed") or not r.get("chapter_urls"):
            if r.get("umbrella_container_url"):
                skipped_unresolved.append(st)  # umbrella not expanded — run Pass-2
            continue
        existing = (by_state.get(st) or {}).get("matched")
        if existing and not overwrite:
            skipped_existing.append(st)
            continue
        nodes = [{"label": f"{prof} {st} (LLM-mapped)", "url": u,
                  "slug": u.rstrip("/").split("/")[-1], "via": "llm_map"}
                 for u in r["chapter_urls"]]
        by_state.setdefault(st, {})["matched"] = nodes
        applied.append(st)

    n_mapped = sum(1 for v in by_state.values() if v.get("matched"))
    print(f"{prof}: would apply {len(applied)} states: {sorted(applied)}")
    if skipped_existing:
        print(f"  skipped (already mapped, use --overwrite): {sorted(skipped_existing)}")
    if skipped_unresolved:
        print(f"  skipped (umbrella unresolved — run Pass-2): {sorted(skipped_unresolved)}")
    print(f"  profession_index would have {n_mapped} mapped states")
    if write:
        idx_fp.write_text(json.dumps(idx, indent=1, ensure_ascii=False))
        print(f"  WROTE {idx_fp}")
        if applied:
            print(f"  next: pipeline/.venv/bin/python -m pipeline.ingest.pull_text "
                  f"--profession {prof} --states {','.join(sorted(applied))} --limit-sections 250")
    else:
        print("  (dry-run; pass --write to apply)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--write", action="store_true", help="actually write (default: dry-run)")
    ap.add_argument("--overwrite", action="store_true", help="overwrite states that already have a mapping")
    args = ap.parse_args()
    apply(args.profession.lower(), args.write, args.overwrite)


if __name__ == "__main__":
    main()
