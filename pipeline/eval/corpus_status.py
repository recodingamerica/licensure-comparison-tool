"""Reproducible corpus-sync + extract-backlog status (read-only, offline).

Promotes two throwaway scripts (corpus_sync_audit.py / finalize_worklist.py)
into a tracked tool so the hand-prep behind a bulk extract is repeatable. Reads
only `results/` and `config/`; never fetches or writes corpus data.

NOTE: this is the cross-stage *sync/completeness* audit (are the pipeline stages
in step, what's the extract backlog). It is distinct from
`pipeline.discover.audit_corpus`, which is the LLM corpus-*correctness* gate
(is the pulled text actually this profession's law).

Two subcommands:

  sync     Per (profession, state) cross-stage health. Flags:
             PULL_ERROR     text/ file has a non-empty 'errors' list
             NO_TEXT        downstream stage exists but text/ missing
             NEEDS_CLEAN    in text/ but no clean/ file
             STALE_CLEAN    clean/ mtime older than text/ — clean rebuilt from an
                            older text (re-pull without re-clean). The real footgun.
             CLEAN_EMPTY    clean/ kept 0 sections though text/ had some
             CLEAN_GT_TEXT  clean/ has MORE sections than text/ (anomaly)
             INDEX_ONLY     text/ is just a chapter-index page (1 tiny section, no
                            real statute text) — "covered" but extracts as garbage
             JUNK_AS_200    a section is a Cloudflare/bot block page saved as content
             THIN           1-2 sections where the profession median is >=10
                            (likely under-matched / wrong chapter)
             NEEDS_EXTRACT  no structured/ file (the backlog)
           NOTE: a plain count drop (clean < text) is normal (dedup + empty-drop)
           and is deliberately NOT flagged — only mtime staleness is.

  backlog  Classify the extract backlog (has text, no structured) into
             raw-empty / post-clean-empty / ready, bucketed by published vs
             override-sibling vs other-heldout. With --write-queues <dir>,
             emit {profession:[states]} queue JSONs:
               extract_ready.json        ready + has discovered schema
               needs_schema_first.json   ready but no discovered/<prof>.json
               effectively_empty.json    raw-empty + post-clean-empty (repull list)

Usage:
  python -m pipeline.eval.corpus_status sync
  python -m pipeline.eval.corpus_status backlog [--write-queues out/dir]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

import yaml

from pipeline.paths import (
    TEXT_DIR, CLEAN_DIR, TRIMMED_DIR, STRUCTURED_DIR, DISCOVERED_DIR,
    CONFIG_DIR, RESULTS_DIR,
)
from pipeline.config.loaders import load_corpus_overrides
from pipeline.eval.corpus_drift import (
    audit_one as _drift_one, _active_official_sources, _index_nodes as _drift_index_nodes,
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


# Cloudflare/bot block-page + Justia soft-404 markers. Import the SINGLE source of
# truth from pull_text rather than re-listing it — a hand-copied mirror here silently
# drifted (it predated the 2026-07-09 soft-404 nav-blob markers), so 44 committed
# corpora holding Justia's "Find a Lawyer" nav blob passed `sync` unflagged as real
# content. Importing pull_text is cheap and does NOT pull in Scrapling/camoufox
# (those are lazy-imported inside fetch()); this tool already runs from the venv.
from pipeline.ingest.pull_text import _BLOCK_MARKERS  # noqa: E402


def has_block_page(text_path: Path) -> bool:
    """True if any non-error section's text looks like a Cloudflare/bot block page
    saved as content (HTTP 200 junk that passed coverage but isn't statute text)."""
    d = _load(text_path)
    if not isinstance(d, dict):
        return False
    for s in (d.get("sections") or []):
        if s.get("error"):
            continue
        low = (s.get("text") or "").lower()
        if any(m in low for m in _BLOCK_MARKERS):
            return True
    return False


def is_index_only(text_path: Path) -> bool:
    """True if a text corpus is just a chapter *index* page — exactly one
    non-error section whose URL is a chapter landing page (no `section-…`
    segment) and whose text is tiny (<2500 chars). It passes the "has a corpus"
    bar but contains no real statute text (the per-section drill never ran), so
    it would extract as garbage. The high-confidence half of the thin-corpus
    completeness check.
    """
    d = _load(text_path)
    if not isinstance(d, dict):
        return False
    secs = [s for s in (d.get("sections") or []) if not s.get("error")]
    if len(secs) != 1:
        return False
    last = [seg for seg in urlparse(secs[0].get("url", "")).path.split("/") if seg]
    leaf = last[-1] if last else ""
    return "section" not in leaf and secs[0].get("text_len", 0) < 2500


def _pull_errors(fp: Path) -> int:
    d = _load(fp)
    if isinstance(d, dict):
        return len(d.get("errors") or [])
    return 0


def is_section_capped(text_path: Path) -> int | None:
    """Return the cap value if the corpus was truncated by --limit-sections, else None."""
    d = _load(text_path)
    if isinstance(d, dict):
        v = d.get("section_cap_hit")
        if isinstance(v, int):
            return v
    return None


def _override_professions() -> set[str]:
    ov = load_corpus_overrides()
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
            if is_index_only(tpath):
                flags.append("INDEX_ONLY")    # chapter-index page only, no real sections
            if has_block_page(tpath):
                flags.append("JUNK_AS_200")   # block/challenge page saved as content
            cap = is_section_capped(tpath)
            if cap is not None:
                flags.append(f"CAPPED({cap})")  # corpus truncated by --limit-sections
        elif any(k in st for k in ("clean", "trimmed", "structured")):
            flags.append("NO_TEXT")
        if cpath:
            clean_n = _sec_count(cpath)
        if tpath:
            if not cpath:
                flags.append("NEEDS_CLEAN")
            else:
                # Real staleness is mtime-based: clean was rebuilt from an OLDER
                # text (re-pull without re-clean). A plain count drop
                # (clean_n < text_n) is NORMAL — clean_text dedups year-versions
                # and drops empty sections — so it is deliberately NOT flagged.
                if cpath.stat().st_mtime < tpath.stat().st_mtime - 1:
                    flags.append("STALE_CLEAN")
                if clean_n == 0 and text_n:
                    flags.append("CLEAN_EMPTY")       # clean dropped everything
                elif clean_n is not None and text_n is not None and clean_n > text_n:
                    flags.append("CLEAN_GT_TEXT")     # anomaly: clean can't add sections
            if "structured" not in st:
                flags.append("NEEDS_EXTRACT")
        rows.append({"prof": prof, "state": state, "text_n": text_n,
                     "clean_n": clean_n, "flags": flags})

    # Peer-relative THIN: a corpus with 1-2 sections where the profession's median
    # (across states with real data) is >=10 is very likely under-matched / a wrong
    # chapter / a flat-index page. Needs cross-corpus context, so it's a post-pass.
    by_prof_counts: dict[str, list[int]] = defaultdict(list)
    for r in rows:
        if r["text_n"]:
            by_prof_counts[r["prof"]].append(r["text_n"])
    medians = {}
    for p, counts in by_prof_counts.items():
        c = sorted(counts)
        medians[p] = c[len(c) // 2] if c else 0
    for r in rows:
        n = r["text_n"]
        if n and 0 < n <= 2 and medians.get(r["prof"], 0) >= 10 and "INDEX_ONLY" not in r["flags"]:
            r["flags"].append("THIN")
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


def umbrella_candidates(min_refs: int = 5) -> dict:
    """Find shared 'umbrella' chapters a corpus depends on but we never pulled —
    general-provisions chapters (discipline, renewal, unprofessional conduct) that a
    profession's act heavily cites. The WA 18.130 pattern, generalized. Numeric
    Title-Chapter cite heuristic (covers UT/IN/SD/NM/GA/SC/CO/AL/AR/... — not prose
    cites like KRS/RS). Returns {state: {chapter: [professions...]}} for chapters an
    UNPULLED chapter is cited >= min_refs times within a corpus."""
    by_state: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    if not TEXT_DIR.exists():
        return {}
    for fp in TEXT_DIR.glob("*/*.json"):
        if fp.stem.startswith("_"):
            continue
        prof, state = fp.parent.name, fp.stem
        d = _load(fp)
        if not isinstance(d, dict):
            continue
        secs = [s for s in (d.get("sections") or []) if not s.get("error")]
        pulled = {f"{m.group(1)}-{m.group(2)}" for s in secs
                  if (m := re.match(r"(\d+)-(\d+)", s.get("citation", "")))}
        if not pulled:
            continue
        text = " ".join((s.get("text") or "") for s in secs)
        # Drop public-law / session-law refs whose second component is a 4-digit
        # year (e.g. 'P.L. 194-2005', 'Acts 214-1993') — those aren't chapters and
        # were polluting the umbrella candidates.
        refs = Counter(
            f"{a}-{b}" for a, b in re.findall(r"\b(\d+)-(\d+)", text)
            if not (len(b) == 4 and 1900 <= int(b) <= 2099)
        )
        for ch, n in refs.items():
            if ch not in pulled and n >= min_refs:
                by_state[state][ch].add(prof)
    return {st: {ch: sorted(profs) for ch, profs in chs.items()} for st, chs in by_state.items()}


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
        "NEEDS_CLEAN": [r for r in rows if "NEEDS_CLEAN" in r["flags"]],
        "STALE_CLEAN": [r for r in rows if "STALE_CLEAN" in r["flags"]],
        "CLEAN_EMPTY": [r for r in rows if "CLEAN_EMPTY" in r["flags"]],
        "CLEAN_GT_TEXT": [r for r in rows if "CLEAN_GT_TEXT" in r["flags"]],
        "INDEX_ONLY": [r for r in rows if "INDEX_ONLY" in r["flags"]],
        "JUNK_AS_200": [r for r in rows if "JUNK_AS_200" in r["flags"]],
        "THIN": [r for r in rows if "THIN" in r["flags"]],
        "PULL_ERROR": [r for r in rows if "PULL_ERROR" in r["flags"]],
        "CAPPED": [r for r in rows if any(f.startswith("CAPPED(") for f in r["flags"])],
        "NEEDS_EXTRACT": [r for r in rows if "NEEDS_EXTRACT" in r["flags"]],
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
    blocking = sum(len(cats[k]) for k in
                   ("STALE_CLEAN", "CLEAN_GT_TEXT", "INDEX_ONLY", "JUNK_AS_200", "PULL_ERROR", "NO_TEXT", "CAPPED"))
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


def cmd_umbrella(min_refs: int, min_profs: int) -> int:
    cand = umbrella_candidates(min_refs)
    corpora = sum(len(profs) for chs in cand.values() for profs in chs.values())
    strong = [(st, ch, profs) for st, chs in cand.items()
              for ch, profs in chs.items() if len(profs) >= min_profs]
    strong.sort(key=lambda x: -len(x[2]))
    print(f"UMBRELLA-MISSING: shared chapters cited >= {min_refs}x but never pulled")
    print(f"  (profession,state) corpora affected: {corpora}")
    print(f"  strong candidates (chapter cited by >= {min_profs} professions in a state): {len(strong)}\n")
    print(f"  {'state':6s} {'chapter':12s} {'#profs':>6s}  example professions")
    for st, ch, profs in strong:
        print(f"  {st:6s} {ch:12s} {len(profs):6d}  {', '.join(profs[:5])}{' …' if len(profs) > 5 else ''}")
    # nonzero if any strong candidate — these are recoverable missing law
    return 1 if strong else 0


# --- unified health gate ----------------------------------------------------
# ONE exit code for "is the committed corpus/mapping state healthy?", composing
# the cross-stage sync flags (audit_sync) with corpus-vs-index drift
# (corpus_drift.audit_one) — replacing the two separate standalone gates so
# there is one place to ask. Preserves each partition exactly: HOST_DRIFT blocks
# (EXTRA/MISSING_CHAPTER report but don't); and the sync blocking-set below is
# the same one cmd_sync uses (THIN / NEEDS_EXTRACT / NEEDS_CLEAN / CLEAN_EMPTY
# are deliberately NON-blocking).
_SYNC_BLOCKING_EXACT = {"STALE_CLEAN", "CLEAN_GT_TEXT", "INDEX_ONLY",
                        "JUNK_AS_200", "PULL_ERROR", "NO_TEXT"}


def _blocking_flags(flags: list[str]) -> list[str]:
    return [f for f in flags
            if f in _SYNC_BLOCKING_EXACT or f.startswith("CAPPED(")]


def _probe_urls(prof: str, state: str) -> list[str]:
    """Network tier: probe each url the index maps for (prof, state) and return the
    bad verdicts as reason tags (URL_STUB / URL_DEAD_404). FETCHES — callers gate
    this behind --check-urls, and it must not run while the refresh holds the
    one-fetcher lane."""
    from pipeline.eval.verify_urls import probe  # lazy: pulls in pull_text.fetch
    tags: set[str] = set()
    for node in _drift_index_nodes(prof, state):
        for u in [node.get("url", ""), *(node.get("section_url_list") or [])]:
            if not u:
                continue
            v = probe(u).get("verdict")
            if v in ("STUB", "DEAD_404"):
                tags.add(f"URL_{v}")
    return sorted(tags)


def _llm_verdicts(suspects: list[tuple[str, str, list[str]]]) -> dict[tuple[str, str], str]:
    """LLM tier: run the corpus-correctness audit on the suspect cells (batched by
    profession) and return {(prof, state): verdict}. COSTS LLM calls — gated behind
    --check-llm."""
    from pipeline.discover.audit_corpus import audit_states
    by_prof: dict[str, list[str]] = defaultdict(list)
    for prof, state, _ in suspects:
        by_prof[prof].append(state)
    out: dict[tuple[str, str], str] = {}
    for prof, states in by_prof.items():
        for st, v in audit_states(prof, sorted(set(states))).items():
            out[(prof, st)] = v.get("verdict", "?")
    return out


def cmd_gate(check_urls: bool = False, check_llm: bool = False) -> int:
    official = _active_official_sources()
    suspects: list[tuple[str, str, list[str]]] = []
    for r in audit_sync(index_stages()):
        reasons = _blocking_flags(r["flags"])
        d = _drift_one(r["prof"], r["state"], official)
        if d and "HOST_DRIFT" in d["verdicts"]:
            reasons = [*reasons, "HOST_DRIFT"]
        if reasons:
            suspects.append((r["prof"], r["state"], reasons))

    # Opt-in network tier: re-probe already-suspect cells' mapped urls so a dead/
    # stub LINK (needs a new url) is told apart from a stale-but-live corpus. Bounded
    # to the offline suspects on purpose — probe() fetches, so a full-index sweep
    # would be thousands of fetches and can't run against the live refresh.
    if check_urls:
        suspects = [(p, s, [*reasons, *_probe_urls(p, s)]) for p, s, reasons in suspects]

    # Opt-in LLM tier: re-check the suspect cells' corpus correctness so a
    # wrong-chapter pull (right sync state, wrong law) is caught. Same suspect-only
    # bound — audit_states costs an LLM call per state.
    if check_llm:
        verdicts = _llm_verdicts(suspects)
        suspects = [
            (p, s, [*reasons, "WRONG_CHAPTER"] if verdicts.get((p, s)) == "wrong_chapter" else reasons)
            for p, s, reasons in suspects
        ]

    for prof, state, reasons in suspects:
        print(f"  {prof}/{state}: {', '.join(reasons)}")
    print(f"\n=== health gate: {len(suspects)} blocking cell(s) ===")
    return 1 if suspects else 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s_gate = sp.add_parser("gate", help="unified health gate (sync flags + corpus/index drift) -> exit 1 if any blocking")
    s_gate.add_argument("--check-urls", action="store_true",
                        help="network tier: probe suspect cells' mapped urls, fold STUB/DEAD_404 in (FETCHES — don't run during a refresh)")
    s_gate.add_argument("--check-llm", action="store_true",
                        help="LLM tier: audit suspect cells' corpus correctness, fold wrong_chapter in (costs LLM calls)")
    sp.add_parser("sync", help="cross-stage corpus-sync health report")
    s_bk = sp.add_parser("backlog", help="extract-backlog classification + queues")
    s_bk.add_argument("--write-queues", help="dir to emit queue JSONs into")
    s_um = sp.add_parser("umbrella", help="unpulled shared/general-provisions chapters a corpus depends on")
    s_um.add_argument("--min-refs", type=int, default=5, help="min text references to flag (default 5)")
    s_um.add_argument("--min-profs", type=int, default=3,
                      help="only show chapters cited by >= this many professions in a state (default 3)")
    args = ap.parse_args()

    if args.cmd == "gate":
        sys.exit(cmd_gate(check_urls=args.check_urls, check_llm=args.check_llm))
    elif args.cmd == "sync":
        sys.exit(cmd_sync())
    elif args.cmd == "backlog":
        sys.exit(cmd_backlog(args.write_queues))
    elif args.cmd == "umbrella":
        sys.exit(cmd_umbrella(args.min_refs, args.min_profs))


if __name__ == "__main__":
    main()
