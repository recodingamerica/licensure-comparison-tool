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


def build_index_for(profession: str, defn: dict, hierarchies: dict[str, dict]) -> dict:
    by_state = {}
    matched_states = 0
    for st in ALL_STATES:
        record = hierarchies.get(st)
        if not record:
            by_state[st] = {"matched": [], "note": "no_hierarchy"}
            continue
        m = match_state(defn, record)
        by_state[st] = {"matched": m}
        if m:
            matched_states += 1
    return {
        "profession": profession,
        "display": defn.get("display", profession),
        "patterns": defn.get("patterns", []),
        "excludes": defn.get("excludes", []),
        "coverage": {"states_matched": matched_states, "states_total": len(ALL_STATES)},
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

    coverage_rows = []
    for prof, defn in professions.items():
        index = build_index_for(prof, defn, hierarchies)
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
