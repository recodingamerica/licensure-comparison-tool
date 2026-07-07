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

  NARROW (CDP, driver MUST be stopped — shares the one debug Chrome) — `--apply P/ST…`:
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
    if not url:
        return False
    return bool(re.search(r"/title-[0-9a-z]+/?$", url.rstrip("/") + "/", re.I))


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
    """Given a container's immediate children, decide the scoped target. Pure — the CDP
    walk supplies `children`. Returns one of:
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
# CDP walk (needs the debug Chrome — run with the pull driver STOPPED)
# --------------------------------------------------------------------------- #
def walk_container(url: str, max_depth: int = WALK_MAX_DEPTH) -> list[dict]:
    """Flatten a container's children down to `max_depth`, so a part→sections layout
    still yields the leaf sections. One CDP fetch per intermediate node."""
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


def narrow_cell(prof: str, state: str, profs: dict, threshold: int = OVER_BROAD_SECTIONS) -> dict:
    """CDP: narrow one over-broad cell. Rewrites the profession_index target in place
    (via='narrow') and returns a verdict dict. Caller re-adds narrowed cells to the
    worklist and records absences."""
    patterns, excludes = patterns_for(prof, profs)
    idx = _load_index(prof)
    nodes = idx.get("by_state", {}).get(state, {}).get("matched", [])
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
            for node in idx.get("by_state", {}).get(st, {}).get("matched", []):
                if node.get("section_slug_pattern") or node.get("section_url_list"):
                    continue                                    # already scoped
                reason = is_over_broad(node["url"], node.get("label", ""),
                                       patterns, excludes, corpus_count(prof, st), threshold)
                if reason:
                    out.append({"prof": prof, "state": st, "reason": reason,
                                "label": node.get("label", ""), "url": node["url"]})
    return out


def _driver_running() -> bool:
    try:
        return subprocess.run(["pgrep", "-f", "gap_pull.sh"],
                              capture_output=True).returncode == 0
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--detect", action="store_true", help="free over-broad report (no fetch)")
    ap.add_argument("--apply", nargs="*", metavar="PROF/ST",
                    help="CDP-narrow these cells (driver must be stopped); empty = all --detect hits")
    ap.add_argument("--threshold", type=int, default=OVER_BROAD_SECTIONS)
    args = ap.parse_args()

    if args.detect and args.apply is None:
        hits = detect(args.threshold)
        print(f"over-broad candidates: {len(hits)}")
        for h in hits:
            print(f"  {h['reason']:26s} {h['prof']}/{h['state']}  {h['label'][:44]}")
        return 0

    if args.apply is not None:
        if _driver_running():
            print("REFUSING: gap_pull.sh is running — narrowing needs the one debug Chrome. "
                  "Stop the driver first."); return 2
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
