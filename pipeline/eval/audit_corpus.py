"""Reproducible corpus-sync + extract-backlog audit (read-only, offline).

Promotes two throwaway scripts (corpus_sync_audit.py / finalize_worklist.py)
into a tracked tool so the hand-prep behind a bulk extract is repeatable. Reads
only `results/` and `config/`; never fetches or writes corpus data.

Two subcommands:

  sync     Per (profession, state) cross-stage health. Flags:
             PULL_ERROR     text/ file has a non-empty 'errors' list
             NO_TEXT        downstream stage exists but text/ missing
             NEEDS_CLEAN    in text/ but no clean/ file
             STALE_CLEAN    clean/ section count != text/ section count (the footgun)
             CLEAN_OLDER    clean/ mtime older than text/ (secondary staleness)
             NEEDS_EXTRACT  no structured/ file (the backlog)

  backlog  Classify the extract backlog (has text, no structured) into
             raw-empty / post-clean-empty / ready, bucketed by published vs
             override-sibling vs other-heldout. With --write-queues <dir>,
             emit {profession:[states]} queue JSONs:
               extract_ready.json        ready + has discovered schema
               needs_schema_first.json   ready but no discovered/<prof>.json
               effectively_empty.json    raw-empty + post-clean-empty (repull list)

Usage:
  python -m pipeline.eval.audit_corpus sync
  python -m pipeline.eval.audit_corpus backlog [--write-queues out/dir]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

import yaml  # noqa: E402

from paths import (  # noqa: E402
    TEXT_DIR, CLEAN_DIR, TRIMMED_DIR, STRUCTURED_DIR, DISCOVERED_DIR,
    CONFIG_DIR, RESULTS_DIR,
)

# The 7 professions with published map/blob payloads (per CLAUDE.md). Kept here
# explicitly because there is no single in-code constant for them.
PUBLISHED = {
    "dentistry", "dietetics", "medicine", "nursing",
    "optometry", "podiatry", "public_accountancy",
}

STAGE_DIRS = {
    "text": TEXT_DIR,
    "clean": CLEAN_DIR,
    "trimmed": TRIMMED_DIR,
    "structured": STRUCTURED_DIR,
}


def _load(fp: Path):
    try:
        return json.loads(fp.read_text())
    except Exception:
        return None


def _sec_count(fp: Path) -> int | None:
    d = _load(fp)
    if isinstance(d, dict) and isinstance(d.get("sections"), list):
        return len(d["sections"])
    return None


def _pull_errors(fp: Path) -> int:
    d = _load(fp)
    if isinstance(d, dict):
        return len(d.get("errors") or [])
    return 0


def _override_professions() -> set[str]:
    ov = yaml.safe_load((CONFIG_DIR / "corpus_overrides.yaml").read_text()) or {}
    return set(ov.keys())


def index_stages() -> dict[tuple[str, str], dict[str, Path]]:
    """(profession, state) -> {stage: filepath} across all stages on disk."""
    idx: dict[tuple[str, str], dict[str, Path]] = defaultdict(dict)
    for stage, base in STAGE_DIRS.items():
        if not base.exists():
            continue
        for fp in base.glob("*/*.json"):
            state = fp.stem
            if state.startswith("_"):  # _summary.json etc.
                continue
            prof = fp.parent.name
            idx[(prof, state)][stage] = fp
    return idx


def audit_sync(idx) -> list[dict]:
    rows = []
    for (prof, state), st in sorted(idx.items()):
        flags: list[str] = []
        tpath = st.get("text")
        cpath = st.get("clean")
        text_n = clean_n = None
        if tpath:
            text_n = _sec_count(tpath)
            if _pull_errors(tpath) > 0:
                flags.append("PULL_ERROR")
        elif any(k in st for k in ("clean", "trimmed", "structured")):
            flags.append("NO_TEXT")
        if cpath:
            clean_n = _sec_count(cpath)
        if tpath:
            if not cpath:
                flags.append("NEEDS_CLEAN")
            else:
                if text_n is not None and clean_n is not None and text_n != clean_n:
                    flags.append(f"STALE_CLEAN({text_n}!={clean_n})")
                if cpath.stat().st_mtime < tpath.stat().st_mtime - 1:
                    flags.append("CLEAN_OLDER")
            if "structured" not in st:
                flags.append("NEEDS_EXTRACT")
        rows.append({"prof": prof, "state": state, "text_n": text_n,
                     "clean_n": clean_n, "flags": flags})
    return rows


def classify_backlog(idx):
    """Split the (has text, no structured) backlog into raw_empty /
    postclean_empty / ready[(prof,state,kept)]."""
    backlog = [(p, s) for (p, s), st in idx.items()
               if "text" in st and "structured" not in st]
    raw_empty, postclean_empty, ready = [], [], []
    for (p, s) in sorted(backlog):
        tn = _sec_count(TEXT_DIR / p / f"{s}.json")
        if not tn:
            raw_empty.append((p, s))
            continue
        cn = _sec_count(CLEAN_DIR / p / f"{s}.json")
        if cn is None:
            ready.append((p, s, tn))  # clean missing — surface as ready w/ text count
            continue
        if cn == 0:
            postclean_empty.append((p, s))
            continue
        ready.append((p, s, cn))
    return raw_empty, postclean_empty, ready


def _bucket(prof: str, overrides: set[str]) -> str:
    if prof in PUBLISHED:
        return "PUBLISHED"
    if prof in overrides:
        return "OVERRIDE_SIBLING"
    return "OTHER_HELDOUT"


def _print_by_prof(title: str, pairs: list[tuple[str, str]]) -> None:
    by_prof: dict[str, list[str]] = defaultdict(list)
    for p, s in pairs:
        by_prof[p].append(s)
    print(f"===== {title} ({len(pairs)}) =====")
    for prof in sorted(by_prof):
        sts = sorted(by_prof[prof])
        print(f"  {prof:32s} {len(sts):3d}  {' '.join(sts)}")


def cmd_sync() -> int:
    rows = audit_sync(index_stages())

    def has(prefix, flags):
        return any(f.startswith(prefix) for f in flags)

    cats = {
        "NEEDS_CLEAN": [r for r in rows if has("NEEDS_CLEAN", r["flags"])],
        "STALE_CLEAN": [r for r in rows if has("STALE_CLEAN", r["flags"])],
        "CLEAN_OLDER": [r for r in rows if "CLEAN_OLDER" in r["flags"] and not has("STALE_CLEAN", r["flags"])],
        "PULL_ERROR": [r for r in rows if "PULL_ERROR" in r["flags"]],
        "NEEDS_EXTRACT": [r for r in rows if has("NEEDS_EXTRACT", r["flags"])],
        "NO_TEXT": [r for r in rows if "NO_TEXT" in r["flags"]],
    }
    print(f"TOTAL (prof,state) pairs indexed: {len(rows)}")
    print(f"  professions: {len(set(r['prof'] for r in rows))}\n")
    for name, rs in cats.items():
        print(f"  {name:14s}: {len(rs)}")
    print()
    for name, rs in cats.items():
        if rs:
            _print_by_prof(name, [(r["prof"], r["state"]) for r in rs])
            print()
    # sync issues (excluding the always-large NEEDS_EXTRACT backlog) → nonzero
    blocking = sum(len(cats[k]) for k in ("STALE_CLEAN", "PULL_ERROR", "NO_TEXT"))
    return 1 if blocking else 0


def cmd_backlog(write_queues: str | None) -> int:
    idx = index_stages()
    overrides = _override_professions()
    raw_empty, postclean_empty, ready = classify_backlog(idx)

    bk: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for (p, s, _n) in ready:
        bk[_bucket(p, overrides)][p].append(s)

    print(f"EXTRACT BACKLOG: {len(raw_empty) + len(postclean_empty) + len(ready)}")
    print(f"  raw_empty (0 text sections)      : {len(raw_empty)}")
    print(f"  post-clean empty (clean kept==0) : {len(postclean_empty)}")
    print(f"  READY to trim+extract            : {len(ready)}\n")
    for b in ("PUBLISHED", "OVERRIDE_SIBLING", "OTHER_HELDOUT"):
        npairs = sum(len(v) for v in bk[b].values())
        print(f"  {b:18s} ready_pairs={npairs:4d}  professions={len(bk[b])}")
    print()
    _print_by_prof("POST-CLEAN EMPTY (clean dropped everything)", postclean_empty)

    if write_queues:
        out = Path(write_queues)
        out.mkdir(parents=True, exist_ok=True)
        ready_by_prof: dict[str, list[str]] = defaultdict(list)
        for (p, s, _n) in ready:
            ready_by_prof[p].append(s)
        extract_ready, needs_schema = {}, {}
        for p, states in ready_by_prof.items():
            target = extract_ready if (DISCOVERED_DIR / f"{p}.json").exists() else needs_schema
            target[p] = sorted(states)
        empty_by_prof: dict[str, list[str]] = defaultdict(list)
        for p, s in raw_empty:
            empty_by_prof[p].append(f"{s}(raw)")
        for p, s in postclean_empty:
            empty_by_prof[p].append(f"{s}(postclean)")

        def _write(name, mapping):
            q = {p: sorted(v) for p, v in mapping.items() if v}
            (out / f"{name}.json").write_text(json.dumps(q, indent=2, sort_keys=True))
            return sum(len(v) for v in q.values())

        nr = _write("extract_ready", extract_ready)
        ns = _write("needs_schema_first", needs_schema)
        ne = _write("effectively_empty", empty_by_prof)
        print(f"\nWrote queues to {out}/: extract_ready={nr} needs_schema_first={ns} effectively_empty={ne}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("sync", help="cross-stage corpus-sync health report")
    s_bk = sp.add_parser("backlog", help="extract-backlog classification + queues")
    s_bk.add_argument("--write-queues", help="dir to emit queue JSONs into")
    args = ap.parse_args()

    if args.cmd == "sync":
        sys.exit(cmd_sync())
    elif args.cmd == "backlog":
        sys.exit(cmd_backlog(args.write_queues))


if __name__ == "__main__":
    main()
