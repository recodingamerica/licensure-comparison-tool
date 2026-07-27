"""Automate the by-hand over-broad remap: detect targets the web_search locator
over-picked (a whole title / department / generically-named chapter) and NARROW them
to the profession's own section block — or flag a candidate correct-absence.

The locator (`_common.locate`) is biased toward chapters ("go UP a level ... capture
the whole regime"), so section-nested professions get mapped to a container that pulls
hundreds/thousands of irrelevant sections and times out. By hand we googled the real
statute, then scoped the target with `section_slug_pattern`/`section_url_list`. This
module does the same, LLM-free:

  DETECT (free, no fetch) — `--detect`:
    A cell is over-broad if the located URL is a whole-title root, OR it pulled a
    corpus bigger than --threshold sections whose located chapter LABEL does not match
    the profession's professions.yaml patterns. (Label-match is the discriminator that
    spares a legitimately-large named chapter like medicine/CA.)

  NARROW (fetches via Scrapling; run with the pull driver STOPPED — one Justia
  fetcher at a time) — `--apply P/ST…`:
    Walk the container one–two levels via expand_containers.container_children; if a
    sub-part's LABEL names the profession ("Part II - Emergency Medical Personnel",
    "Article 5 - Public Weighmasters") pull that part; else title-match the leaf
    sections and RANGE-FILL between the matched min/max so Definitions/Fees sections
    (which don't repeat the profession's name) come along too. Write the scoped target
    into the profession_index; zero matches → candidate absence, flagged for review.

  python -m pipeline.discover.gap_harvest.narrow --detect
  python -m pipeline.discover.gap_harvest.narrow --apply athlete_agent/KY emergency_medical_technician/LA

Recall caveat: title-matching only anchors where a section title contains one of the
profession's patterns. Where the statute's wording differs entirely from the patterns
(no anchor at all), the cell is flagged for a human rather than silently narrowed —
"reliable detection" over forced-but-wrong automation.

  DETECT MISMATCHED LABELS (free, no fetch) — `--detect-labels`:
    `is_over_broad` above only runs the label-match discriminator when the corpus is
    ALSO huge (>threshold sections). A small-but-wrong pick — e.g. hvac/MA located to
    Chapter 142A "Regulation of Home Improvement Contractors" (20 sections, plausible-
    sounding, topically wrong) — never trips that check, and locate.py never revisits a
    cell that already has an answer, so it stays wrong indefinitely. This scans every
    profession_index entry (not just the unpulled worklist) for the same label mismatch,
    regardless of size. A hit is a signal to look, not proof the corpus is wrong.

  python -m pipeline.discover.gap_harvest.narrow --detect-labels [--via T1,T2 | --all-via]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

from pipeline.paths import TEXT_DIR, PROFESSION_INDEX_DIR
from pipeline.config.loaders import load_professions
from pipeline.discover.match_profession import label_matches
from pipeline.discover.gap_harvest import _common as C
from pipeline.ingest._section_patterns import is_title_root
from pipeline.config.loaders import matched_for

OVER_BROAD_SECTIONS = 150          # a section-nested profession's real law is well under this
_CLUSTER_MAX_GAP = 4               # >this many non-hit sections between hits breaks the run
WALK_MAX_DEPTH = 2                 # container -> part -> sections
WORKLIST = "pull_worklist.json"    # {prof: [states]} the pull driver reads
ABSENCES = "narrow_absences.json"  # cells with no matching section — for human review


# --------------------------------------------------------------------------- #
# Pure helpers (no fetch — unit-tested)
# --------------------------------------------------------------------------- #
def whole_title(url: str) -> bool:
    """True if the URL points at a whole Justia title root (…/title-40/), which is
    never the right granularity for one profession."""
    return is_title_root(url)


def patterns_for(prof: str, profs: dict) -> tuple[list[str], list[str]]:
    meta = profs.get(prof, {}) or {}
    return (meta.get("patterns") or [], meta.get("excludes") or [])


def is_over_broad(url: str, label: str, patterns: list[str], excludes: list[str],
                  corpus_n: int | None, threshold: int = OVER_BROAD_SECTIONS) -> str | None:
    """Disk-only over-broad signal → reason string or None. `corpus_n` is the pulled
    section count (None if the cell never produced a corpus)."""
    if whole_title(url):
        return "whole_title"
    if corpus_n is not None and corpus_n > threshold and not label_matches(label, patterns, excludes):
        return "huge_corpus_label_mismatch"
    return None


# A label mismatch that ISN'T huge slides past `is_over_broad` untouched — e.g. hvac/MA
# mapped by the web_search locator to Chapter 142A "Regulation of Home Improvement
# Contractors" (20 sections, plausible-sounding, topically wrong). It's never big enough
# to trip the over-broad check, and locate.py never revisits a cell that already has an
# answer, so a wrong-but-small pick from one run stays wrong forever unless someone
# stumbles on it. `detect_mismatched_labels` is the same label_matches discriminator,
# unconditionally, over EVERY profession_index entry (not just the unpulled worklist).
# Automated (`via`) sources are the ones nobody ever reviewed line-by-line; a mismatch
# here is a signal to look, not proof the corpus is wrong.
AUTOMATED_VIA = {"gap_locator", "relocate", "null_recovery", "narrow",
                 "reused_from_existing_corpus", "section_map_v2", "migration_keep"}


def detect_mismatched_labels(via_filter: set[str] | None = AUTOMATED_VIA) -> list[dict]:
    """Full-index scan (LLM-free): every matched node whose label doesn't label_match
    its own profession's patterns, regardless of corpus size — UNLESS the pulled
    corpus's own full text does match (a terse chapter label like "Chapter 8A -
    Counselors" often doesn't repeat the profession's name even when the statute inside
    plainly does; checking the label alone produced ~60% false positives in practice).
    A cell with no pulled corpus yet can only be judged on the label."""
    profs = load_professions()
    out = []
    for idx_path in sorted(PROFESSION_INDEX_DIR.glob("*.json")):
        prof = idx_path.stem
        patterns, excludes = patterns_for(prof, profs)
        if not patterns:
            continue
        try:
            idx = json.loads(idx_path.read_text())
        except Exception:
            continue
        for st, rec in (idx.get("by_state") or {}).items():
            for node in rec.get("matched") or []:
                label, via = node.get("label", ""), node.get("via", "")
                if via_filter and via not in via_filter:
                    continue
                if node.get("section_slug_pattern") or node.get("section_url_list"):
                    continue  # already scoped to a specific range — someone looked
                if not label or label_matches(label, patterns, excludes):
                    continue
                text = corpus_text(prof, st)
                if text and content_matches(text, patterns, excludes):
                    continue  # label misses, but the actual statute text confirms it
                out.append({"prof": prof, "state": st, "via": via, "label": label,
                            "url": node.get("url", ""), "corpus_sections": corpus_count(prof, st),
                            "checked_text": text is not None})
    return out


_NUM = re.compile(r"(\d+)")


def section_key(url: str) -> tuple[int, ...] | None:
    """Comparable numeric key from a Justia section slug's trailing number, so we can
    range-fill. section-164-6901 -> (164,6901); rs-40-1133-1 -> (40,1133,1);
    statute-44-9204 -> (44,9204). Returns None if unparseable (letters-only tail)."""
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    nums = _NUM.findall(slug)
    return tuple(int(n) for n in nums) if nums else None


def is_leaf_label(label: str) -> bool:
    """A Justia leaf section's label starts with its number ('164.6901 - …'); a grouping
    reads 'Part II - …' / 'Article 5 - …'. Mirrors expand_containers._expandable."""
    return bool(re.match(r"^\s*\d", label or ""))


def scope_from_children(children: list[dict], patterns: list[str], excludes: list[str]) -> dict | None:
    """Given a container's immediate children, decide the scoped target. Pure — the
    container walk supplies `children`. Returns one of:
      {"url": <part-url>, "label": …}                    a named sub-part matched
      {"section_url_list": [...]}                          leaf sections (range-filled)
      None                                                 nothing matched (absence)
    """
    # 1) A named sub-part whose label names the profession → take the whole part.
    for c in children:
        if not is_leaf_label(c["label"]) and label_matches(c["label"], patterns, excludes):
            return {"url": c["url"], "label": c["label"]}

    # 2) Leaf sections whose TITLE names the profession → fill the DENSEST contiguous
    #    cluster of hits. (Global min/max range-fill is wrong when a broad chapter
    #    name-drops the profession in scattered sections — e.g. "insurance producer"
    #    appears all over a whole insurance chapter — which would recapture everything.
    #    The real licensing act is a tight run of hits; lone scattered hits are noise.)
    leaves = [c for c in children if is_leaf_label(c["label"])]
    keyed = sorted(((k, c) for c in leaves if (k := section_key(c["url"])) is not None),
                   key=lambda x: x[0])
    hit_pos = [i for i, (_k, c) in enumerate(keyed)
               if label_matches(c["label"], patterns, excludes)]
    if not hit_pos:
        exact = [c for c in leaves if label_matches(c["label"], patterns, excludes)]
        return {"section_url_list": [c["url"] for c in exact]} if exact else None
    # cluster hit positions: a gap of >_CLUSTER_MAX_GAP non-hit sections breaks the run
    clusters, cur = [], [hit_pos[0]]
    for i in hit_pos[1:]:
        if i - cur[-1] <= _CLUSTER_MAX_GAP:
            cur.append(i)
        else:
            clusters.append(cur)
            cur = [i]
    clusters.append(cur)
    best = max(clusters, key=len)                         # densest = the real act
    urls = [keyed[i][1]["url"] for i in range(best[0], best[-1] + 1)]  # fill gaps in the run
    if len(urls) > OVER_BROAD_SECTIONS:                   # still huge → can't cleanly narrow
        return None
    return {"section_url_list": sorted(set(urls))}


# --------------------------------------------------------------------------- #
# Container walk (headless Scrapling fetch — run with the pull driver STOPPED)
# --------------------------------------------------------------------------- #
def walk_container(url: str, max_depth: int = WALK_MAX_DEPTH) -> list[dict]:
    """Flatten a container's children down to `max_depth`, so a part→sections layout
    still yields the leaf sections. One fetch per intermediate node."""
    from pipeline.discover.expand_containers import container_children
    from pipeline.ingest import pull_text as pt

    kids = container_children(url)
    pt.polite_sleep()
    if max_depth <= 1:
        return kids
    flat: list[dict] = []
    for k in kids:
        if is_leaf_label(k["label"]):
            flat.append(k)
        else:                                 # a grouping — descend one level
            sub = container_children(k["url"])
            pt.polite_sleep()
            flat.extend(sub or [k])           # keep the part itself if it has no children
    return flat


def _load_index(prof: str) -> dict:
    return json.loads((PROFESSION_INDEX_DIR / f"{prof}.json").read_text())


def _atomic(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False))
    os.replace(tmp, path)


def corpus_count(prof: str, state: str) -> int | None:
    f = TEXT_DIR / prof / f"{state}.json"
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text())
    except Exception:
        return 0
    return len(d if isinstance(d, list) else d.get("sections", []))


def corpus_text(prof: str, state: str) -> str | None:
    """Full joined section text for one cell, or None if never pulled."""
    f = TEXT_DIR / prof / f"{state}.json"
    if not f.exists():
        return None
    try:
        d = json.loads(f.read_text())
    except Exception:
        return None
    secs = d if isinstance(d, list) else d.get("sections", [])
    return " ".join((s.get("text") or "") for s in secs)


def content_matches(text: str, patterns: list[str], excludes: list[str]) -> bool:
    """Pattern presence anywhere in a large corpus text. Deliberately NOT
    label_matches: its "(repealed)" universal-exclude bailout is a label-level
    heuristic (a whole SECTION label reading "(Repealed)") that misfires on bulk
    text — a many-thousand-word corpus spanning decades of amendments very often
    contains a repealed subsection marker somewhere, which would otherwise
    short-circuit an otherwise-correct match to a false negative."""
    L = text.lower()
    if not any(p.lower() in L for p in patterns):
        return False
    if excludes and any(e.lower() in L for e in excludes):
        return False
    return True


def narrow_cell(prof: str, state: str, profs: dict, threshold: int = OVER_BROAD_SECTIONS) -> dict:
    """Narrow one over-broad cell (fetches via Scrapling). Rewrites the profession_index target in place
    (via='narrow') and returns a verdict dict. Caller re-adds narrowed cells to the
    worklist and records absences."""
    patterns, excludes = patterns_for(prof, profs)
    idx = _load_index(prof)
    nodes = matched_for(idx, state)
    if not nodes:
        return {"prof": prof, "state": state, "verdict": "no_target"}
    node = nodes[0]
    url, label = node["url"], node.get("label", "")

    over = is_over_broad(url, label, patterns, excludes, corpus_count(prof, state), threshold)
    children = walk_container(url)
    # even if disk-signals were silent, use the live child count as the real test
    leaf_n = sum(1 for c in children if is_leaf_label(c["label"]))
    if not over and leaf_n <= threshold:
        return {"prof": prof, "state": state, "verdict": "ok", "leaves": leaf_n}

    scope = scope_from_children(children, patterns, excludes)
    if scope is None:
        return {"prof": prof, "state": state, "verdict": "absence", "leaves": leaf_n,
                "reason": over or "big_no_match"}

    new = {"url": scope.get("url", url), "label": scope.get("label", label),
           "slug": node.get("slug", ""), "via": "narrow"}
    if "section_url_list" in scope:
        new["section_url_list"] = scope["section_url_list"]
    idx["by_state"][state]["matched"] = [new]
    _atomic(PROFESSION_INDEX_DIR / f"{prof}.json", idx)
    return {"prof": prof, "state": state, "verdict": "narrowed", "leaves": leaf_n,
            "scoped_to": len(scope.get("section_url_list", [])) or scope.get("url")}


# --------------------------------------------------------------------------- #
# Detection report (free) + CLI
# --------------------------------------------------------------------------- #
def detect(threshold: int = OVER_BROAD_SECTIONS) -> list[dict]:
    """Free scan of the worklist's cells for over-broad targets (no fetch)."""
    profs = load_professions()
    wl = C.load_json(WORKLIST, {})
    out = []
    for prof, states in wl.items():
        idx_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        if not idx_path.exists():
            continue
        idx = json.loads(idx_path.read_text())
        patterns, excludes = patterns_for(prof, profs)
        for st in states:
            for node in matched_for(idx, st):
                if node.get("section_slug_pattern") or node.get("section_url_list"):
                    continue                                    # already scoped
                reason = is_over_broad(node["url"], node.get("label", ""),
                                       patterns, excludes, corpus_count(prof, st), threshold)
                if reason:
                    out.append({"prof": prof, "state": st, "reason": reason,
                                "label": node.get("label", ""), "url": node["url"]})
    return out


def _driver_running() -> bool:
    """True if a Justia fetch is in flight — we run one fetcher at a time.

    Matches the pull stages themselves rather than a launcher script, so the guard
    holds however the pull was started (annual crawl, manual one-off, batch).
    """
    for pattern in ("pipeline.ingest.refresh_corpus", "pipeline.ingest.pull_text"):
        try:
            if subprocess.run(["pgrep", "-f", pattern],
                              capture_output=True).returncode == 0:
                return True
        except Exception:
            continue
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--detect", action="store_true", help="free over-broad report (no fetch)")
    ap.add_argument("--detect-labels", action="store_true",
                    help="free full-index label-mismatch report, any corpus size (no fetch)")
    ap.add_argument("--via", help="with --detect-labels: comma-separated via tags (default: automated sources)")
    ap.add_argument("--all-via", action="store_true", help="with --detect-labels: don't filter by via")
    ap.add_argument("--apply", nargs="*", metavar="PROF/ST",
                    help="narrow these cells (driver must be stopped); empty = all --detect hits")
    ap.add_argument("--threshold", type=int, default=OVER_BROAD_SECTIONS)
    args = ap.parse_args()

    if args.detect_labels:
        via_filter = None if args.all_via else (
            set(args.via.split(",")) if args.via else AUTOMATED_VIA)
        hits = detect_mismatched_labels(via_filter)
        C.save_json("label_audit.json", hits)
        from collections import Counter
        by_via = Counter(h["via"] for h in hits)
        print(f"label mismatches: {len(hits)} (via filter: {via_filter or 'none'})")
        for via, n in by_via.most_common():
            print(f"  {via:28s} {n}")
        print("→ gap_harvest/label_audit.json")
        return 0

    if args.detect and args.apply is None:
        hits = detect(args.threshold)
        print(f"over-broad candidates: {len(hits)}")
        for h in hits:
            print(f"  {h['reason']:26s} {h['prof']}/{h['state']}  {h['label'][:44]}")
        return 0

    if args.apply is not None:
        if _driver_running():
            print("REFUSING: a Justia pull is running — narrowing fetches from Justia too, "
                  "and we run one Justia fetcher at a time. Stop the pull first."); return 2
        profs = load_professions()
        cells = [tuple(c.split("/", 1)) for c in args.apply] if args.apply \
            else [(h["prof"], h["state"]) for h in detect(args.threshold)]
        wl = C.load_json(WORKLIST, {})
        absences = C.load_json(ABSENCES, [])
        for prof, st in cells:
            r = narrow_cell(prof, st, profs, args.threshold)
            print(f"  {r['verdict']:9s} {prof}/{st}  {r.get('scoped_to', r.get('reason',''))}")
            if r["verdict"] == "narrowed":
                wl.setdefault(prof, [])
                if st not in wl[prof]:
                    wl[prof].append(st)
            elif r["verdict"] == "absence":
                if st in wl.get(prof, []):
                    wl[prof].remove(st)
                absences.append({"prof": prof, "state": st, "reason": r.get("reason", "")})
        C.save_json(WORKLIST, wl)
        C.save_json(ABSENCES, absences)
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
