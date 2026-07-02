"""Corpus/index DRIFT audit — LLM-free, offline (reads only results/).

The bug this catches (UT trades, 2026-07-02): a committed corpus can silently
diverge from the mapping it was pulled under. electrician/UT's index mapped
`le.utah.gov` (single node, no umbrella), but its committed corpus was 94 stale
Justia sections (chapter-55 + a chapter-1 umbrella) from a much older pull — the
mapping had been changed WITHOUT a re-pull. Nobody noticed until the next re-pull
shrank it 94->37. The corpus looked complete but was answering to a mapping that
no longer existed.

This audit compares, per (profession, state) with a committed corpus, the HOSTS
and CHAPTER paths of the corpus's section urls against the chapters the index
CURRENTLY maps. Signals:

  HOST_DRIFT     corpus has sections from a host the index no longer maps (the
                 strongest signal — a whole-corpus source mismatch, e.g. corpus on
                 le.utah.gov but index says law.justia.com). ← the UT case.
  EXTRA_CHAPTER  corpus has a chapter the index doesn't map (e.g. a stale umbrella
                 chapter still baked into the corpus after it was dropped from the
                 index). Re-pull would drop it.
  MISSING_CHAPTER an index chapter with ZERO corpus sections (mapping added but
                 never pulled).

HOST_DRIFT and EXTRA_CHAPTER mean the committed corpus is STALE vs its mapping —
a re-pull would change it. Run this in preflight/CI so drift is caught the moment
a mapping changes, not on the next accidental re-pull.

Usage:
  python -m pipeline.eval.corpus_drift              # all professions
  python -m pipeline.eval.corpus_drift --profession electrician
  python -m pipeline.eval.corpus_drift --host-drift-only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urlparse

from pipeline.paths import TEXT_DIR, PROFESSION_INDEX_DIR
from pipeline.config.loaders import load_state_structure


def _active_official_sources() -> set[str]:
    """States with an ACTIVE (uncommented) non-justia `source:` handler — their
    index carries a Justia url but the pull deliberately routes to an official
    host (is_X_url intercept). A corpus on that official host is BY DESIGN, not
    drift. A retired/commented source (MN, UT, MD, NV) is NOT here, so those flip
    back to real drift detection."""
    ss = load_state_structure()
    return {st for st, blk in ss.items()
            if isinstance(blk, dict) and (blk.get("source") or "justia") != "justia"}


def _host(url: str) -> str:
    """Host of a url; a relative Justia path (/codes/...) implies law.justia.com."""
    if url.startswith("/codes/"):
        return "law.justia.com"
    return (urlparse(url).netloc or "").lower()


# A trailing path segment that lives BELOW the chapter: a section leaf
# (section-…, a bare s123 / 0101.htm), a part, or a version suffix. NOT things
# like "statute-act-297-of-1965" or "subtitle-4" that ARE the chapter-level node.
_LEAF_RE = re.compile(
    r"^(section-.+|part-\d.*|subpart-.+|s?\d+[a-z]?(-version-\d+)?(\.htm)?)$", re.I)


def _chapter_key(url: str) -> str:
    """Normalize a url to a host+chapter key by stripping trailing sub-chapter
    (leaf) segments, so a chapter index and its section leaves collapse to the
    same key. Keeps at least two path segments so it never strips to nothing."""
    host = _host(url)
    path = url if url.startswith("/codes/") else urlparse(url).path
    segs = [s for s in path.split("/") if s]
    while len(segs) > 2 and _LEAF_RE.match(segs[-1]):
        segs.pop()
    return host + "/" + "/".join(segs)


def _index_nodes(prof: str, state: str) -> list[dict]:
    path = PROFESSION_INDEX_DIR / f"{prof}.json"
    if not path.exists():
        return []
    idx = json.loads(path.read_text())
    return idx.get("by_state", {}).get(state, {}).get("matched", [])


def _index_targets(nodes: list[dict]) -> tuple[set[str], set[str]]:
    """(hosts, chapter_keys) the index currently maps. Includes section_url_list
    entries (the real pull targets for scoped states)."""
    hosts, chapters = set(), set()
    for n in nodes:
        for u in [n.get("url", ""), *(n.get("section_url_list") or [])]:
            if not u:
                continue
            hosts.add(_host(u))
            chapters.add(_chapter_key(u))
    return hosts, chapters


def _covered(key: str, index_keys: set[str]) -> bool:
    """A corpus chapter-key is covered if some index key is a prefix of it (corpus
    same-or-more-granular, e.g. index chapter-28 covers corpus chapter-28/
    subchapter-1) or vice versa (index deeper than corpus)."""
    return any(key.startswith(k) or k.startswith(key) for k in index_keys)


def audit_one(prof: str, state: str, official_source_states: set[str]) -> dict | None:
    """Return a drift record for (prof, state), or None if aligned / no corpus."""
    corpus_path = TEXT_DIR / prof / f"{state}.json"
    if not corpus_path.exists():
        return None
    try:
        sections = (json.loads(corpus_path.read_text()).get("sections") or [])
    except Exception:
        return None
    if not sections:
        return None
    # Active official-source states pull from an official host BY DESIGN (the index
    # carries a Justia url that an is_X_url intercept rewrites). Their whole
    # corpus-vs-index host mismatch is expected, so drift detection there would need
    # a host-agnostic comparison — out of scope; skip them (documented limitation).
    if state in official_source_states:
        return None
    nodes = _index_nodes(prof, state)
    if not nodes:
        return None  # no mapping to compare against (held-out / unmapped)

    idx_hosts, idx_chaps = _index_targets(nodes)
    corp_hosts = {_host(s.get("url", "")) for s in sections if s.get("url")}
    corp_chaps = {_chapter_key(s.get("url", "")) for s in sections if s.get("url")}

    host_drift = sorted(corp_hosts - idx_hosts)
    extra_chap = sorted(k for k in corp_chaps if not _covered(k, idx_chaps))
    missing_chap = sorted(k for k in idx_chaps if not _covered(k, corp_chaps))

    if not (host_drift or extra_chap or missing_chap):
        return None
    verdicts = []
    if host_drift:
        verdicts.append("HOST_DRIFT")
    if extra_chap:
        verdicts.append("EXTRA_CHAPTER")
    if missing_chap:
        verdicts.append("MISSING_CHAPTER")
    return {
        "profession": prof, "state": state, "verdicts": verdicts,
        "host_drift": host_drift, "extra_chapters": extra_chap,
        "missing_chapters": missing_chap, "sections": len(sections),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profession", help="limit to one profession")
    ap.add_argument("--host-drift-only", action="store_true",
                    help="report only the high-confidence HOST_DRIFT cases")
    args = ap.parse_args()

    profs = ([args.profession] if args.profession
             else sorted(p.stem for p in PROFESSION_INDEX_DIR.glob("*.json")
                         if not p.stem.startswith("_")))
    official = _active_official_sources()
    records = []
    for prof in profs:
        pdir = TEXT_DIR / prof
        if not pdir.exists():
            continue
        for fp in sorted(pdir.glob("*.json")):
            rec = audit_one(prof, fp.stem, official)
            if rec and (not args.host_drift_only or "HOST_DRIFT" in rec["verdicts"]):
                records.append(rec)

    host_n = 0
    for r in records:
        print(f"{'+'.join(r['verdicts']):32s} {r['profession']}/{r['state']}  ({r['sections']} secs)")
        if r["host_drift"]:
            print(f"    corpus hosts not in index: {r['host_drift']}")
            host_n += 1
        for k in ("extra_chapters", "missing_chapters"):
            if r[k]:
                print(f"    {k}: {r[k][:4]}{' …' if len(r[k]) > 4 else ''}")
    print(f"\n=== {len(records)} drifted (prof,state); {host_n} with HOST_DRIFT ===")
    sys.exit(1 if host_n else 0)


if __name__ == "__main__":
    main()
