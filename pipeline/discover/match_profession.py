"""Match canonical professions (config/professions.yaml) to nodes in each
state's hierarchy tree (results/hierarchy/<STATE>.json).

Pure pattern matching against chapter labels — no LLM, no fetching.
Outputs:
  results/profession_index/<profession>.json — per-state matched nodes
  results/profession_index/_coverage.csv     — matrix of profession × state

Usage:
  python -m pipeline.discover.match_profession
  python -m pipeline.discover.match_profession --profession podiatry
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import HIERARCHY_DIR, PROFESSION_INDEX_DIR, CONFIG_DIR, LOGS_DIR, RESULTS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402

SECTION_MAPS_DIR = RESULTS_DIR / "section_maps"
CHAPTER_MAPS_DIR = RESULTS_DIR / "chapter_maps"

LOG_PATH = LOGS_DIR / "match_profession.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
PROFESSION_INDEX_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("match_profession")


def load_professions() -> dict[str, dict]:
    path = CONFIG_DIR / "professions.yaml"
    return yaml.safe_load(path.read_text())


def label_matches(label: str, patterns: list[str], excludes: list[str]) -> bool:
    L = label.lower()
    if not any(p.lower() in L for p in patterns):
        return False
    if excludes and any(e.lower() in L for e in excludes):
        return False
    return True


def match_state(profession_def: dict, state_record: dict) -> list[dict]:
    """Return matched chapter nodes for one state."""
    patterns = profession_def.get("patterns", [])
    excludes = profession_def.get("excludes", [])
    matched: list[dict] = []
    for ch in state_record.get("chapters", []):
        if label_matches(ch.get("label", ""), patterns, excludes):
            matched.append({
                "label": ch["label"],
                "url": ch["url"],
                "slug": ch.get("slug", ""),
            })
    return matched


def load_state_structure() -> dict:
    """Load config/state_structure.yaml. Returns {} if missing.

    Shape:
        STATE_CODE:
          source: justia | revisor_mn | mi_legis | pa_complex | …
          layout: chapter | section_fallback | subtitled | external | broken
          professions:
            <profession>:
              url, section_slug_pattern, section_url_list, label, note
    """
    path = CONFIG_DIR / "state_structure.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def _node_from_override(ov: dict) -> dict:
    """Build a matched-node dict from one override entry (state_structure
    or manual_overrides shape; both have identical fields per profession)."""
    node = {
        "label": ov.get("label", ""),
        "url": ov.get("url", ""),
        "slug": (ov.get("url") or "").rstrip("/").rsplit("/", 1)[-1],
        "via": ov.get("_source", "manual_override"),
        "note": ov.get("note", ""),
    }
    if ov.get("section_slug_pattern"):
        node["section_slug_pattern"] = ov["section_slug_pattern"]
    if ov.get("section_url_list"):
        node["section_url_list"] = ov["section_url_list"]
    return node


def load_section_maps(state_structure: dict) -> dict[str, dict]:
    """Load per-state v2 section maps for every section_fallback state.

    Returns: { state: { profession: {section_url_list, label} } }
    The v2 mapper is the primary source of truth for which sections belong
    to which profession in flat-section-list states; this lets a new
    profession appear without per-state hand-curation, as long as v2 has
    been run for that state.
    """
    out: dict[str, dict] = {}
    for st, entry in state_structure.items():
        if (entry or {}).get("layout") != "section_fallback":
            continue
        path = SECTION_MAPS_DIR / f"{st}_v2.json"
        if not path.exists():
            continue
        m = json.loads(path.read_text())
        out[st] = m.get("professions") or {}
    return out


def load_chapter_maps() -> dict[str, dict]:
    """Load any per-state chapter maps from results/chapter_maps/<STATE>.json.

    Returns: { state: { profession: {url, chapter_slug, label} } }
    Lower precedence than state_structure.yaml — only used as a safety net
    when no hand-curated entry exists. Limited reliability for buried
    chapters (e.g. podiatry inside a "Medicine and Other Healing Arts"
    chapter), recodification cases, and subtitled-hierarchy states; see
    map_state_chapters.py for caveats.
    """
    out: dict[str, dict] = {}
    if not CHAPTER_MAPS_DIR.exists():
        return out
    for path in CHAPTER_MAPS_DIR.glob("*.json"):
        st = path.stem
        m = json.loads(path.read_text())
        profs = m.get("professions") or {}
        if profs:
            out[st] = profs
    return out


def build_index_for(
    profession: str,
    defn: dict,
    hierarchies: dict[str, dict],
    state_structure: dict,
    section_maps: dict[str, dict],
    chapter_maps: dict[str, dict],
) -> dict:
    by_state: dict = {}
    matched_states = 0
    overrides_used = 0
    section_maps_used = 0
    chapter_maps_used = 0
    for st in ALL_STATES:
        record = hierarchies.get(st)
        m: list[dict] = []
        if record:
            m = match_state(defn, record)

        # state_structure.yaml is the single source of truth for per-state overrides.
        # An entry can either set its own `url` (most cases) or rely on the state's
        # `title_url` (for section-filter overrides, where the chapter is the title itself).
        state_entry = state_structure.get(st) or {}
        ss_entry = (state_entry.get("professions") or {}).get(profession)
        if ss_entry:
            url = ss_entry.get("url") or state_entry.get("title_url")
            if url:
                existing = next((x for x in m if x["url"] == url), None)
                if existing is None:
                    merged = {**ss_entry, "url": url, "_source": "state_structure"}
                    m.append(_node_from_override(merged))
                    overrides_used += 1
                else:
                    # Same URL was found by label match — merge in override-only
                    # fields (section_slug_pattern, section_url_list) so we don't
                    # silently drop them.
                    if ss_entry.get("section_slug_pattern"):
                        existing["section_slug_pattern"] = ss_entry["section_slug_pattern"]
                    if ss_entry.get("section_url_list"):
                        existing["section_url_list"] = ss_entry["section_url_list"]
                    if ss_entry.get("section_slug_pattern") or ss_entry.get("section_url_list"):
                        overrides_used += 1
        elif st in section_maps and profession in section_maps[st]:
            # No hand-curated entry — fall back to v2 section-map output.
            urls = section_maps[st][profession].get("section_url_list") or []
            if urls:
                title_url = state_entry.get("title_url")
                if title_url and title_url not in {x["url"] for x in m}:
                    m.append(_node_from_override({
                        "url": title_url,
                        "label": section_maps[st][profession].get("label", ""),
                        "section_url_list": urls,
                        "_source": "section_map_v2",
                    }))
                    section_maps_used += 1
        elif not m and st in chapter_maps and profession in chapter_maps[st]:
            # Last resort safety net — chapter map (labels-only LLM mapping).
            ch = chapter_maps[st][profession]
            url = ch.get("url")
            if url:
                m.append(_node_from_override({
                    "url": url,
                    "label": ch.get("label", ""),
                    "_source": "chapter_map",
                }))
                chapter_maps_used += 1

        # For section_fallback states, an override with section_url_list /
        # section_slug_pattern is the canonical set; the label-matched
        # section nodes are subsumed by it. Drop them to keep the index
        # clean and avoid wasted fetches downstream.
        if (state_entry.get("layout") == "section_fallback"
                and any(n.get("section_url_list") or n.get("section_slug_pattern") for n in m)):
            m = [n for n in m if n.get("section_url_list") or n.get("section_slug_pattern")]

        if not record and not m:
            by_state[st] = {"matched": [], "note": "no_hierarchy"}
            continue
        by_state[st] = {"matched": m}
        if m:
            matched_states += 1
    return {
        "profession": profession,
        "display": defn.get("display", profession),
        "patterns": defn.get("patterns", []),
        "excludes": defn.get("excludes", []),
        "coverage": {
            "states_matched": matched_states,
            "states_total": len(ALL_STATES),
            "overrides_used": overrides_used,
            "section_maps_used": section_maps_used,
            "chapter_maps_used": chapter_maps_used,
        },
        "by_state": by_state,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="", help="If set, only build index for this profession")
    args = ap.parse_args()

    professions = load_professions()
    if args.profession:
        if args.profession not in professions:
            sys.exit(f"profession not in registry: {args.profession}")
        professions = {args.profession: professions[args.profession]}

    # Load all state hierarchies once
    hierarchies = {}
    for path in HIERARCHY_DIR.glob("*.json"):
        d = json.loads(path.read_text())
        hierarchies[d["state"]] = d
    log.info("loaded %d state hierarchies", len(hierarchies))

    state_structure = load_state_structure()
    if state_structure:
        n_prof_entries = sum(len((s or {}).get("professions") or {}) for s in state_structure.values())
        log.info("loaded state_structure for %d states (%d profession entries)", len(state_structure), n_prof_entries)

    section_maps = load_section_maps(state_structure)
    if section_maps:
        log.info("loaded v2 section maps for %d section_fallback states: %s", len(section_maps), sorted(section_maps))

    chapter_maps = load_chapter_maps()
    if chapter_maps:
        log.info("loaded chapter maps for %d states: %s", len(chapter_maps), sorted(chapter_maps))

    rebuilt: dict[str, dict] = {}
    for prof, defn in professions.items():
        index = build_index_for(prof, defn, hierarchies, state_structure, section_maps, chapter_maps)
        out_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        out_path.write_text(json.dumps(index, indent=2))
        log.info("[%s] %d/%d states matched", prof, index["coverage"]["states_matched"], index["coverage"]["states_total"])
        rebuilt[prof] = index

    # Coverage matrix: union of just-rebuilt indexes plus whatever else is on disk.
    coverage_rows: list[dict] = []
    seen: set[str] = set()
    for prof, index in rebuilt.items():
        seen.add(prof)
        coverage_rows.append(_coverage_row(prof, index))
    for path in sorted(PROFESSION_INDEX_DIR.glob("*.json")):
        prof = path.stem
        if prof in seen or prof.endswith("_suggestions") or prof.startswith("_"):
            continue
        index = json.loads(path.read_text())
        coverage_rows.append(_coverage_row(prof, index))

    cov_path = PROFESSION_INDEX_DIR / "_coverage.csv"
    with cov_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["profession", "display", "states_matched", "states_total", "missing_states"])
        w.writeheader()
        for row in sorted(coverage_rows, key=lambda r: -r["states_matched"]):
            w.writerow(row)
    log.info("wrote coverage matrix: %s (%d professions)", cov_path, len(coverage_rows))


def _coverage_row(profession: str, index: dict) -> dict:
    cov = index.get("coverage", {})
    by_state = index.get("by_state", {})
    return {
        "profession": profession,
        "display": index.get("display", ""),
        "states_matched": cov.get("states_matched", 0),
        "states_total": cov.get("states_total", len(ALL_STATES)),
        "missing_states": ",".join(s for s in ALL_STATES if not (by_state.get(s) or {}).get("matched")),
    }


if __name__ == "__main__":
    main()
