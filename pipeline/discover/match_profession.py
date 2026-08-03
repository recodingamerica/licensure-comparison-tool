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
import re
import sys
import urllib.parse

from pipeline.paths import HIERARCHY_DIR, PROFESSION_INDEX_DIR, CONFIG_DIR, LOGS_DIR
from pipeline.config.states import ALL_STATES
from pipeline.config.loaders import load_professions, load_state_structure  # noqa: F401 — re-exported for backward compat
from pipeline.discover._url import _abs_url
from pipeline.discover._mapping_overrides import (
    load_mapping_overrides,
    apply_mapping_overrides,
    apply_override_adds,
)

LOG_PATH = LOGS_DIR / "match_profession.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
PROFESSION_INDEX_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("match_profession")


# Universal exclusion: repealed chapters shouldn't be pulled into extraction
# (NM has 3 CPA-named chapters, two marked "(Repealed.)" — extracting their
# placeholder text wastes LLM and confuses output. Applies to every profession.)
_UNIVERSAL_EXCLUDES = ("(repealed.)", "(repealed)", "[repealed]")


def label_matches(label: str, patterns: list[str], excludes: list[str]) -> bool:
    L = label.lower()
    if any(u in L for u in _UNIVERSAL_EXCLUDES):
        return False
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
        # Skip leaf-section nodes appended by expand_containers — they carry
        # parent_chapter_url and are matched by match_sections, not here.
        if ch.get("parent_chapter_url"):
            continue
        if label_matches(ch.get("label", ""), patterns, excludes):
            matched.append({
                "label": ch["label"],
                "url": _abs_url(ch["url"]),
                "slug": ch.get("slug", ""),
            })
    return matched


def _official_url(template: str, justia_url: str) -> str | None:
    """Fill an official-source chapter_url_template from a Justia chapter url.

    Parses {title}/{chapter}/{section} out of the Justia path and normalizes
    each (strip zero-padding, upper-case any letter suffix), e.g.
      .../south-dakota/title-36/chapter-06a/  +  ".../{title}-{chapter}"
        -> ".../36-6A"
    Returns None if a placeholder the template needs can't be filled.
    """
    parts: dict[str, str] = {}
    for seg in [s for s in urllib.parse.urlparse(justia_url).path.split("/") if s]:
        for key in ("title", "chapter", "section"):
            if seg.startswith(key + "-"):
                raw = seg[len(key) + 1:]
                m = re.match(r"^0*(\d+)([a-zA-Z]*)$", raw)
                if m:
                    parts[key] = m.group(1) + m.group(2).upper()      # 393B (SD/NV)
                    parts[key + "_lc"] = m.group(1) + m.group(2).lower()  # 393b (CT)
                else:
                    parts[key] = parts[key + "_lc"] = raw
                # hyphen→dot form for cite-style sources (WA 19-28→19.28, VA 54-1→54.1)
                parts[key + "_dot"] = parts[key].replace("-", ".")
    try:
        return template.format(**parts)
    except KeyError:
        return None


def _node_from_override(ov: dict) -> dict:
    """Build a matched-node dict from one override entry (state_structure
    or manual_overrides shape; both have identical fields per profession)."""
    node = {
        "label": ov.get("label", ""),
        "url": _abs_url(ov.get("url", "")),
        "slug": (ov.get("url") or "").rstrip("/").rsplit("/", 1)[-1],
        "via": ov.get("_source", "manual_override"),
        "note": ov.get("note", ""),
    }
    if ov.get("section_slug_pattern"):
        node["section_slug_pattern"] = ov["section_slug_pattern"]
    if ov.get("section_url_list"):
        node["section_url_list"] = ov["section_url_list"]
    if ov.get("pa_keep_sections"):
        node["pa_keep_sections"] = ov["pa_keep_sections"]
    return node


def _umbrella_nodes_for(state_entry: dict, profession: str, existing_urls: set[str]) -> list[dict]:
    """Additive umbrella chapters for a profession (e.g. WA Ch 18.130, the
    Uniform Disciplinary Act that every WA health profession defers to).

    A state-level `umbrella:` block declares which professions inherit which
    extra chapters; the nodes are ADDITIVE (not authoritative) and skip any url
    already matched. They carry a Justia-style chapter url so the state's
    `chapter_url_template` rewrites them to the official source like any other
    node. Returns [] when the state has no umbrella or this profession isn't
    in scope.
    """
    umbrella = state_entry.get("umbrella") or {}
    profs = umbrella.get("professions") or []
    if profession not in profs:
        return []
    nodes = []
    for ch in umbrella.get("chapters") or []:
        url = ch.get("url")
        if not url or url in existing_urls:
            continue
        nodes.append(_node_from_override({**ch, "_source": "state_structure_umbrella"}))
    return nodes


def build_index_for(
    profession: str,
    defn: dict,
    hierarchies: dict[str, dict],
    state_structure: dict,
    mapping_overrides: dict,
) -> dict:
    by_state: dict = {}
    matched_states = 0
    overrides_used = 0
    mapping_overrides_used = 0
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

        # Manual mapping overrides (config/mapping_overrides.yaml), pass 1 of 2:
        # adds are inserted HERE — where the old section_map/chapter_map fallbacks
        # sat — so an add carrying section_url_list/section_slug_pattern subsumes
        # bare label-matched section nodes below, exactly as the fallbacks did.
        m = apply_override_adds(profession, st, m, mapping_overrides)

        # For section_fallback states, an override with section_url_list /
        # section_slug_pattern is the canonical set; the label-matched
        # section nodes are subsumed by it. Drop them to keep the index
        # clean and avoid wasted fetches downstream.
        if (state_entry.get("layout") == "section_fallback"
                and any(n.get("section_url_list") or n.get("section_slug_pattern") for n in m)):
            m = [n for n in m if n.get("section_url_list") or n.get("section_slug_pattern")]
        # Opt-in: `authoritative: true` on a state_structure profession entry means
        # its url IS the complete source — drop label-matched siblings (noise like
        # adjacent articles or a whole-chapter node). Off by default, because many
        # entries are ADDITIVE (an umbrella/general-provisions url meant to
        # supplement the label-matched practice act, e.g. NY/WA medicine).
        elif ss_entry and ss_entry.get("authoritative") and ss_entry.get("url"):
            if any(n["url"] == ss_entry["url"] for n in m):
                m = [n for n in m if n["url"] == ss_entry["url"]]

        # Additive umbrella chapters (state-level): appended AFTER authoritative
        # pruning so they survive it, BEFORE the template rewrite so they get
        # translated to the official source. E.g. WA Ch 18.130 for every WA
        # health profession.
        umbrella_nodes = _umbrella_nodes_for(state_entry, profession, {n["url"] for n in m})
        if umbrella_nodes:
            m.extend(umbrella_nodes)
            overrides_used += 1

        # Official-source translation: states with a chapter_url_template carry
        # their profession→chapter mapping via the Justia hierarchy, but fetch
        # from the state's own (non-Cloudflare) source. Rewrite each matched
        # node's url to the official url; pull_text dispatches on the new host.
        template = (state_entry or {}).get("chapter_url_template")
        if template and m:
            for n in m:
                official = _official_url(template, n.get("url", ""))
                if official:
                    n["justia_url"] = n["url"]
                    n["url"] = official

        # Manual mapping overrides, pass 2 of 2 (the LAST transformation):
        # excludes drop generated nodes (an exclude guarantees the url is out);
        # adds are re-ensured in case a pruning rule above ate one (an add
        # guarantees the node is in). A state with no hierarchy record but with
        # add nodes becomes a real matched record, not a "no_hierarchy" stub.
        m = apply_mapping_overrides(profession, st, m, mapping_overrides)
        if (mapping_overrides.get(profession) or {}).get(st):
            mapping_overrides_used += 1

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
            "mapping_overrides_used": mapping_overrides_used,
        },
        "by_state": by_state,
    }


def rebuild_index(profession: str, mapping_overrides: dict | None = None) -> dict:
    """Regenerate one profession's index IN MEMORY from committed inputs
    (hierarchies + professions.yaml + state_structure.yaml + mapping_overrides.yaml).

    mapping_overrides=None loads config/mapping_overrides.yaml; pass {} to build
    the pure generated BASE (what the index would be with no manual patches).
    """
    professions = load_professions()
    if profession not in professions:
        raise KeyError(f"profession not in registry: {profession}")
    hierarchies = {}
    for path in HIERARCHY_DIR.glob("*.json"):
        d = json.loads(path.read_text())
        hierarchies[d["state"]] = d
    if mapping_overrides is None:
        mapping_overrides = load_mapping_overrides()
    return build_index_for(profession, professions[profession], hierarchies,
                           load_state_structure(), mapping_overrides)


def rebuild_and_write(profession: str) -> dict:
    """Regenerate one profession's index and write profession_index/<prof>.json.
    Shared by the curation CLIs (match_sections --write-targets,
    apply_llm_candidates) so the committed index is only ever written by the
    generator — manual decisions go through config/mapping_overrides.yaml."""
    index = rebuild_index(profession)
    out_path = PROFESSION_INDEX_DIR / f"{profession}.json"
    out_path.write_text(json.dumps(index, indent=2))
    return index


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", default="", help="If set, only build index for this profession")
    args = ap.parse_args()

    professions = load_professions()
    # Skip config keys like _families — they're registry metadata, not professions.
    professions = {k: v for k, v in professions.items() if not k.startswith("_")}
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

    mapping_overrides = load_mapping_overrides()
    if mapping_overrides:
        log.info("loaded mapping overrides for %d professions", len(mapping_overrides))

    rebuilt: dict[str, dict] = {}
    for prof, defn in professions.items():
        index = build_index_for(prof, defn, hierarchies, state_structure, mapping_overrides)
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
        for row in sorted(coverage_rows, key=lambda r: (-r["states_matched"], r["profession"])):
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
