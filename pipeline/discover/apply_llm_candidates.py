"""Apply reviewed LLM-mapper candidates into mapping_overrides.yaml (the loop's back-half).

Reads results/profession_index/_llm_candidates/<prof>.json (Pass-1 + Pass-2 +
human review) and writes the licensed mappings into
config/mapping_overrides.yaml so match_profession can include them, then
rebuilds profession_index/<prof>.json via rebuild_and_write.

SURGICAL by default: only touches states the candidate file marks licensed with
a chapter URL, and SKIPS states that already have a `matched` node in the
regenerated base (unless --overwrite — in which case exclude entries are also
written for every url the base produces for that state, replacing the generated
mapping with the LLM-mapped one).

States still flagged umbrella (unresolved) or not-licensed are left alone (run
Pass-2 first to resolve umbrellas).

Dry-run by default — pass --write to actually write YAML entries and rebuild.

Run:
  pipeline/.venv/bin/python -m pipeline.discover.apply_llm_candidates --profession electrician            # dry-run
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
from discover.match_profession import rebuild_index, rebuild_and_write  # noqa: E402
from discover._mapping_overrides import add_override_entry, add_exclude_entry  # noqa: E402

CAND_DIR = INDEX_DIR / "_llm_candidates"


def apply(prof: str, write: bool, overwrite: bool) -> None:
    cand_fp = CAND_DIR / f"{prof}.json"
    if not cand_fp.exists():
        sys.exit(f"no candidate file: {cand_fp} — run the mapper first")
    cand = json.loads(cand_fp.read_text())

    # Regenerated base index (with existing overrides) — used to detect
    # already-mapped states and, in --overwrite mode, to enumerate urls to exclude.
    base_idx = rebuild_index(prof)
    by_state_base = base_idx["by_state"]

    applied, skipped_existing, skipped_unresolved = [], [], []
    pending_adds: list[tuple[str, dict]] = []   # (state, node) pairs
    pending_excludes: list[tuple[str, str]] = []  # (state, url) pairs

    for r in cand.get("states", []):
        st = r["state"]
        if not r.get("licensed") or not r.get("chapter_urls"):
            if r.get("umbrella_container_url"):
                skipped_unresolved.append(st)  # umbrella not expanded — run Pass-2
            continue
        existing_matched = (by_state_base.get(st) or {}).get("matched") or []
        if existing_matched and not overwrite:
            skipped_existing.append(st)
            continue

        nodes = [{"label": f"{prof} {st} (LLM-mapped)", "url": u,
                  "slug": u.rstrip("/").split("/")[-1], "via": "llm_map"}
                 for u in r["chapter_urls"]]

        if overwrite and existing_matched:
            # Emit exclude entries for every url the base currently produces for
            # this state, so the LLM-mapped nodes fully replace the generated set.
            for n in existing_matched:
                url = n.get("url")
                if url:
                    pending_excludes.append((st, url))

        for node in nodes:
            pending_adds.append((st, node))
        applied.append(st)

    # Compute how many mapped states the index would have after applying
    n_currently_mapped = sum(1 for v in by_state_base.values() if v.get("matched"))
    n_new = len(applied)
    print(f"{prof}: would apply {n_new} state(s): {sorted(applied)}")
    if skipped_existing:
        print(f"  skipped (already mapped, use --overwrite): {sorted(skipped_existing)}")
    if skipped_unresolved:
        print(f"  skipped (umbrella unresolved — run Pass-2): {sorted(skipped_unresolved)}")
    print(f"  profession_index would have ~{n_currently_mapped + n_new} mapped state(s)")

    if write:
        for st, url in pending_excludes:
            add_exclude_entry(prof, st, url)
        for st, node in pending_adds:
            add_override_entry(prof, st, node)
        if pending_adds or pending_excludes:
            rebuild_and_write(prof)
            print(f"  WROTE mapping_overrides.yaml + rebuilt profession_index/{prof}.json")
        else:
            print("  nothing to write")
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
