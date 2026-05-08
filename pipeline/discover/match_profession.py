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
from paths import HIERARCHY_DIR, PROFESSION_INDEX_DIR, CONFIG_DIR, LOGS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402

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


def load_overrides() -> dict:
    """Load config/manual_overrides.yaml. Returns {} if empty/missing.
    (Legacy profession-keyed format. state_structure.yaml is the preferred
    long-term home; both are merged at match time.)"""
    path = CONFIG_DIR / "manual_overrides.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


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


def build_index_for(
    profession: str,
    defn: dict,
    hierarchies: dict[str, dict],
    overrides: dict,
    state_structure: dict,
) -> dict:
    by_state: dict = {}
    matched_states = 0
    overrides_used = 0
    prof_overrides = (overrides.get(profession) or {})
    for st in ALL_STATES:
        record = hierarchies.get(st)
        m: list[dict] = []
        if record:
            m = match_state(defn, record)

        # Precedence: state_structure (preferred) > manual_overrides (legacy)
        # Each can contribute zero, one, or several matched nodes per (profession, state).
        ss_for_state = (state_structure.get(st) or {}).get("professions") or {}
        ss_entry = ss_for_state.get(profession)
        if ss_entry:
            ss_entry = {**ss_entry, "_source": "state_structure"}
            if ss_entry.get("url") and ss_entry["url"] not in {x["url"] for x in m}:
                m.append(_node_from_override(ss_entry))
                overrides_used += 1

        for ov in prof_overrides.get(st, []) or []:
            if ov["url"] not in {x["url"] for x in m}:
                m.append(_node_from_override({**ov, "_source": "manual_override"}))
                overrides_used += 1

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

    overrides = load_overrides()
    if overrides:
        log.info("loaded legacy manual_overrides for %d professions", len(overrides))
    state_structure = load_state_structure()
    if state_structure:
        n_prof_entries = sum(len((s or {}).get("professions") or {}) for s in state_structure.values())
        log.info("loaded state_structure for %d states (%d profession entries)", len(state_structure), n_prof_entries)

    coverage_rows = []
    for prof, defn in professions.items():
        index = build_index_for(prof, defn, hierarchies, overrides, state_structure)
        out_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        out_path.write_text(json.dumps(index, indent=2))
        log.info("[%s] %d/%d states matched", prof, index["coverage"]["states_matched"], index["coverage"]["states_total"])
        coverage_rows.append({
            "profession": prof,
            "display": defn.get("display", ""),
            "states_matched": index["coverage"]["states_matched"],
            "states_total": index["coverage"]["states_total"],
            "missing_states": ",".join(s for s in ALL_STATES if not index["by_state"][s]["matched"]),
        })

    # Coverage matrix
    cov_path = PROFESSION_INDEX_DIR / "_coverage.csv"
    with cov_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["profession", "display", "states_matched", "states_total", "missing_states"])
        w.writeheader()
        for row in sorted(coverage_rows, key=lambda r: -r["states_matched"]):
            w.writerow(row)
    log.info("wrote coverage matrix: %s", cov_path)


if __name__ == "__main__":
    main()
