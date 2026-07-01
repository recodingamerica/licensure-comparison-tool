"""One-time migration (2026-07-01): fold every RESIDUAL node in the committed
results/profession_index/<prof>.json files into config/mapping_overrides.yaml,
making the committed index a pure function of committed inputs.

"Residual" = a committed node that the generator does NOT reproduce AND that
carries a recognised provenance tag:
    via in {section_map_v2, chapter_map, missed_match_recall, coverage_add,
            coverage_fix, bucket2_contractor, umbrella_xref, section_scope,
            justia, manual_override}
    OR source == "section_match"

"Keep-rule" (new, 2026-07-01): for UNTAGGED committed-only nodes, a two-pass
approach determines whether each is a real loss or benign:
    Pass 1 — build regen1 with the tagged residuals already migrated;
    if the committed node's normalised url (or justia_url) appears in regen1
    it is benign (regen already covers it).  Otherwise it is a REAL LOSS:
    append it to this profession/state's add list with via="migration_keep"
    (flipping url→justia_url if the node carries one, same policy as tagged
    residuals).  Dict-equal duplicates after flipping are deduped.

Nodes WITHOUT a tag that ARE benign (covered by regen1) are stale drift —
not migrated; silently dropped.

Drift report (pass 2): AFTER the keep-rule writes migration_keep entries, the
report is built from regen2 (regeneration WITH all overrides including keeps)
vs the committed index — i.e. exactly what `git diff` will show when indexes
are regenerated. Category D ("Other drift") should be nearly empty; anything
there needs human review.

Excludes: NONE are written. The prior analysis's 1,166 would-be excludes were
almost entirely the expand_containers leaf-section false-positives fixed by the
parent_chapter_url filter in match_state (item 1). The genuine delta is all
add residuals.

Tripwire: add count outside 150–310 → stop and report.

Outputs:
  pipeline/config/mapping_overrides.yaml      — residual add entries only
  docs/reports/mapping_migration_drift_2026-07-01.md  — human-review artifact

Run:
  pipeline/.venv/bin/python -m pipeline.discover.migrate_mapping_overrides
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from pipeline.paths import HIERARCHY_DIR, PROFESSION_INDEX_DIR
from pipeline.config.states import ALL_STATES
from pipeline.discover.match_profession import build_index_for, load_professions, load_state_structure
from pipeline.discover._mapping_overrides import OVERRIDES_PATH, write_mapping_overrides

# Retune tripwire: expected ~201 tagged residuals + ~40-50 migration_keeps.
MIN_ADDS = 150
MAX_ADDS = 310

DRIFT_REPORT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "docs" / "reports" / "mapping_migration_drift_2026-07-01.md"
)

# Provenance tags that make a committed node a migration candidate.
_RESIDUAL_VIA = {
    "section_map_v2",
    "chapter_map",
    "missed_match_recall",
    "coverage_add",
    "coverage_fix",
    "bucket2_contractor",
    "umbrella_xref",
    "section_scope",
    "justia",
    "manual_override",
}


def _is_residual(node: dict) -> bool:
    """True if the node carries a recognised provenance tag."""
    via = node.get("via")
    if via and via in _RESIDUAL_VIA:
        return True
    if node.get("source") == "section_match":
        return True
    return False


def _node_key(n: dict) -> str:
    return json.dumps(n, sort_keys=True)


def _diff_state(
    prof: str,
    st: str,
    base_nodes: list[dict],
    targ_nodes: list[dict],
    warnings: list[str],
) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (residual_adds, untagged_drops, base_only) for this prof/state.

    residual_adds  — committed-only nodes WITH a residual tag (→ write to YAML)
    untagged_drops — committed-only nodes WITHOUT a tag (drift; apply keep-rule)
    base_only      — base-only nodes (regeneration will introduce; report only)
    """
    for side, nodes in (("base", base_nodes), ("target", targ_nodes)):
        for url, k in Counter(n.get("url") for n in nodes).items():
            if k > 1:
                msg = f"DUPLICATE URL ({side}): {prof} {st} {url} x{k}"
                warnings.append(msg)
                print(f"⚠  {msg}")

    base_by_url: dict[str, list[dict]] = {}
    for n in base_nodes:
        base_by_url.setdefault(n.get("url"), []).append(n)
    targ_by_url: dict[str, list[dict]] = {}
    for n in targ_nodes:
        targ_by_url.setdefault(n.get("url"), []).append(n)

    all_urls = list(dict.fromkeys(
        [n.get("url") for n in targ_nodes] + [n.get("url") for n in base_nodes]
    ))

    residual_adds: list[dict] = []
    untagged_drops: list[dict] = []
    base_only_nodes: list[dict] = []

    for url in all_urls:
        b = base_by_url.get(url) or []
        t = targ_by_url.get(url) or []
        if Counter(_node_key(n) for n in b) == Counter(_node_key(n) for n in t):
            continue
        # nodes in committed but not in base
        committed_only = [n for n in t if _node_key(n) not in {_node_key(x) for x in b}]
        for n in committed_only:
            if _is_residual(n):
                residual_adds.append(n)
            else:
                untagged_drops.append(n)
        # nodes in base but not in committed
        for n in b:
            if _node_key(n) not in {_node_key(x) for x in t}:
                base_only_nodes.append(n)

    return residual_adds, untagged_drops, base_only_nodes


def _norm_url(u: str) -> str:
    """Normalize a Justia url for relative↔absolute pairing."""
    return re.sub(r"^https?://law\.justia\.com", "", (u or "").rstrip("/"))


def _regen_paths_for_state(regen: dict, st: str) -> set[str]:
    """Return the set of normalised urls (and justia_urls) in regen for one state."""
    nodes = (regen["by_state"].get(st) or {}).get("matched") or []
    paths: set[str] = set()
    for n in nodes:
        if n.get("url"):
            paths.add(_norm_url(n["url"]))
        if n.get("justia_url"):
            paths.add(_norm_url(n["justia_url"]))
    return paths


def _apply_keep_rule(
    prof: str,
    st: str,
    untagged_drops: list[dict],
    prof_over: dict,
    hierarchies: dict,
    state_structure: dict,
    professions: dict,
) -> int:
    """Apply the keep-rule for untagged committed-only nodes.

    Builds regen1 with current prof_over to check coverage.  Real losses are
    appended to prof_over[st]['add'] with via='migration_keep'.

    Returns the count of new keeps added.
    """
    if not untagged_drops:
        return 0

    defn = professions[prof]
    regen1 = build_index_for(prof, defn, hierarchies, state_structure, {prof: prof_over})
    regen1_paths = _regen_paths_for_state(regen1, st)

    # Build new keep entries, flipping justia_url→url when present (same as tagged residuals).
    new_keeps: list[dict] = []
    for n in untagged_drops:
        url = n.get("url", "")
        justia_url = n.get("justia_url")
        # Check if this node is already covered by regen1.
        if _norm_url(url) in regen1_paths:
            continue
        if justia_url and _norm_url(justia_url) in regen1_paths:
            continue
        # Real loss — keep it.
        if justia_url:
            kept = {k: v for k, v in n.items() if k != "justia_url"}
            kept["url"] = justia_url
            kept["via"] = "migration_keep"
        else:
            kept = {**n, "via": "migration_keep"}
        new_keeps.append(kept)

    # Dedupe: remove dict-equal duplicates after flipping (e.g. SD electrician case).
    seen: set[str] = set()
    deduped: list[dict] = []
    for k in new_keeps:
        key = _node_key(k)
        if key not in seen:
            seen.add(key)
            deduped.append(k)

    if not deduped:
        return 0

    # Also dedupe against already-written adds for this state.
    existing_adds = (prof_over.get(st) or {}).get("add") or []
    existing_keys = {_node_key(x) for x in existing_adds}
    truly_new = [k for k in deduped if _node_key(k) not in existing_keys]

    if not truly_new:
        return 0

    prof_over.setdefault(st, {}).setdefault("add", []).extend(truly_new)
    for n in truly_new:
        print(f"  [migration_keep] {prof} {st} {n.get('url', '')[:70]}")
    return len(truly_new)


def _categorise_drift(
    prof: str,
    st: str,
    add_nodes: list[dict],
    drop_nodes: list[dict],
    committed_nodes_by_url: dict[str, dict],
) -> tuple[list[str], list[str], list[str], list[str]]:
    """Classify per-state drift lines into the four drift-report categories.

    add_nodes     — regen2-only nodes (regeneration will introduce)
    drop_nodes    — committed-only nodes in regen2 diff (regeneration will drop)
    committed_nodes_by_url — ALL committed nodes keyed by url (for justia_url lookup)

    Returns (flip_lines, urlform_lines, wa_umbrella_lines, other_lines),
    each line '- STATE ADD|DROP url — label'. DROP/ADD pairs that describe the
    same chapter are matched up and pulled out of 'other'.

    Flip detection: a committed-only drop node whose justia_url (or its norm)
    matches a regen-only add node's url (or its norm) → category A flip pair.
    """
    flip: list[str] = []
    urlform: list[str] = []
    wa_umbrella: list[str] = []
    other: list[str] = []

    adds_by_url = {n.get("url"): n for n in add_nodes}
    adds_by_norm: dict[str, list[dict]] = {}
    for n in add_nodes:
        adds_by_norm.setdefault(_norm_url(n.get("url")), []).append(n)
    consumed: set[int] = set()

    for n in drop_nodes:
        url, label = n.get("url", ""), n.get("label", "")
        # Official→Justia flip: committed node carries the official url and
        # remembers its justia_url; regeneration (templates retired) produces
        # the plain justia url.  Look up the committed node to find justia_url.
        committed_node = committed_nodes_by_url.get(url) or n
        j = committed_node.get("justia_url")
        partner = None
        if j:
            partner = adds_by_url.get(j)
            if partner is None:
                # Try norm match (e.g. http vs https, trailing slash differences).
                j_norm = _norm_url(j)
                cands = [a for a in adds_by_norm.get(j_norm, []) if id(a) not in consumed]
                if cands:
                    partner = cands[0]
        if partner is not None and id(partner) not in consumed:
            flip.append(f"- {st} DROP {url} — {label}")
            flip.append(f"- {st} ADD  {partner.get('url', '')} — {partner.get('label', '')}")
            consumed.add(id(partner))
            continue
        # URL-form pair: same Justia path, relative vs absolute (hierarchy-era churn).
        cands = [a for a in adds_by_norm.get(_norm_url(url), []) if id(a) not in consumed]
        if cands:
            a = cands[0]
            urlform.append(f"- {st} DROP {url} — {label}")
            urlform.append(f"- {st} ADD  {a.get('url', '')} — {a.get('label', '')}")
            consumed.add(id(a))
            continue
        other.append(f"- {st} DROP {url} — {label}")

    for n in add_nodes:
        if id(n) in consumed:
            continue
        url, label = n.get("url", ""), n.get("label", "")
        line = f"- {st} ADD {url} — {label}"
        if st == "WA" and ("18.130" in url or "18-130" in url or
                           n.get("via") == "state_structure_umbrella"):
            wa_umbrella.append(line)
        else:
            other.append(line)

    return flip, urlform, wa_umbrella, other


def main() -> int:
    professions = load_professions()
    state_structure = load_state_structure()
    hierarchies = {}
    for path in HIERARCHY_DIR.glob("*.json"):
        d = json.loads(path.read_text())
        hierarchies[d["state"]] = d

    overrides: dict = {}
    warnings: list[str] = []
    via_counts: Counter = Counter()
    n_residual_adds = 0
    n_keep_adds = 0
    zero_residual: list[str] = []

    # Drift report data
    # {prof: {"flip": [...], "urlform": [...], "wa_umbrella": [...], "other": [...]}}
    drift_by_prof: dict[str, dict[str, list[str]]] = {}

    for prof, defn in sorted(professions.items()):
        if prof.startswith("_"):
            continue
        committed_path = PROFESSION_INDEX_DIR / f"{prof}.json"
        if not committed_path.exists():
            continue
        base = build_index_for(prof, defn, hierarchies, state_structure, {})
        target = json.loads(committed_path.read_text())
        target_by_state = target.get("by_state") or {}

        for st in target_by_state:
            if st not in ALL_STATES:
                msg = f"TARGET STATE OUTSIDE ALL_STATES: {prof} {st}"
                warnings.append(msg)
                print(f"⚠  {msg}")

        prof_over: dict = {}
        prof_drift: dict[str, list[str]] = {"flip": [], "urlform": [], "wa_umbrella": [], "other": []}

        for st in sorted(set(base["by_state"]) | set(target_by_state)):
            b_rec = base["by_state"].get(st) or {}
            t_rec = target_by_state.get(st) or {}
            b_nodes = b_rec.get("matched") or []
            t_nodes = t_rec.get("matched") or []

            residual_adds, untagged_drops, _base_only = _diff_state(
                prof, st, b_nodes, t_nodes, warnings
            )

            # Write add entries for residual-tagged nodes. Justia-only decision
            # (2026-07-01): an add carrying a justia_url (official-source-era
            # template rewrite) is flipped back to its Justia url so the index —
            # and therefore future pulls — stays on Justia.
            if residual_adds:
                final_adds: list[dict] = []
                for n in residual_adds:
                    if n.get("justia_url"):
                        f = {k: v for k, v in n.items() if k != "justia_url"}
                        f["url"] = n["justia_url"]
                        final_adds.append(f)
                    else:
                        final_adds.append(n)
                prof_over.setdefault(st, {})["add"] = final_adds
                n_residual_adds += len(final_adds)
                for n in final_adds:
                    tag = n.get("via") or (
                        f"source:{n['source']}" if n.get("source") else "(untagged)"
                    )
                    via_counts[tag] += 1

            # Verbose report for untagged drops (candidates for keep-rule or drop)
            for n in untagged_drops:
                print(f"  [untagged-drop] {prof} {st} {n.get('url', '')[:70]}")

            # Keep-rule: check each untagged drop against regen1; real losses
            # are appended as migration_keep adds.
            n_new_keeps = _apply_keep_rule(
                prof, st, untagged_drops, prof_over,
                hierarchies, state_structure, professions,
            )
            n_keep_adds += n_new_keeps
            if n_new_keeps:
                via_counts["migration_keep"] += n_new_keeps

        # Pass 2: build regen2 with all adds (including keeps) and compute
        # drift vs committed — this is what git diff will show on regeneration.
        if prof_over:
            overrides[prof] = prof_over
        else:
            zero_residual.append(prof)

        regen2 = build_index_for(prof, defn, hierarchies, state_structure, {prof: prof_over} if prof_over else {})
        regen2_by_state = regen2["by_state"]

        # Build committed_nodes_by_url for flip detection (need justia_url from committed).
        all_committed_by_url: dict[str, dict[str, dict]] = {}  # state -> url -> node
        for st, rec in target_by_state.items():
            state_map: dict[str, dict] = {}
            for n in (rec.get("matched") or []):
                url = n.get("url")
                if url:
                    state_map[url] = n
            all_committed_by_url[st] = state_map

        for st in sorted(set(target_by_state) | set(regen2_by_state)):
            t_rec = target_by_state.get(st) or {}
            r2_rec = regen2_by_state.get(st) or {}
            t_nodes = t_rec.get("matched") or []
            r2_nodes = r2_rec.get("matched") or []

            t_keys = Counter(_node_key(n) for n in t_nodes)
            r2_keys = Counter(_node_key(n) for n in r2_nodes)
            if t_keys == r2_keys:
                continue

            # regen2-only = will be added on regeneration
            r2_only_keys = r2_keys - t_keys
            # committed-only = will be dropped on regeneration
            t_only_keys = t_keys - r2_keys

            r2_only_nodes = [n for n in r2_nodes if _node_key(n) in r2_only_keys]
            t_only_nodes = [n for n in t_nodes if _node_key(n) in t_only_keys]

            committed_nodes_by_url = all_committed_by_url.get(st) or {}
            fl, uf, wa, oth = _categorise_drift(
                prof, st, r2_only_nodes, t_only_nodes, committed_nodes_by_url
            )
            prof_drift["flip"].extend(fl)
            prof_drift["urlform"].extend(uf)
            prof_drift["wa_umbrella"].extend(wa)
            prof_drift["other"].extend(oth)

        if any(prof_drift[k] for k in prof_drift):
            drift_by_prof[prof] = prof_drift

    n_total_adds = n_residual_adds + n_keep_adds
    print("\n=== migration summary ===")
    print(f"professions with residual (written): {len(overrides)}")
    print(f"professions with zero residual (not written): {len(zero_residual)}")
    print(f"add entries: {n_total_adds}   ({n_residual_adds} tagged residuals + {n_keep_adds} migration_keeps)   by via tag:")
    for tag, k in via_counts.most_common():
        print(f"    {tag}: {k}")
    print("exclude entries: 0 (policy: no excludes written)")
    if warnings:
        print(f"warnings: {len(warnings)} (see ⚠  lines above)")

    if n_total_adds < MIN_ADDS or n_total_adds > MAX_ADDS:
        print(
            f"\nSTOP: add count {n_total_adds} outside expected range {MIN_ADDS}–{MAX_ADDS} "
            f"— NOT writing {OVERRIDES_PATH}. Investigate before re-running."
        )
        return 1

    write_mapping_overrides(overrides)
    print(f"\nwrote {OVERRIDES_PATH}")

    # --- Drift report ---
    _write_drift_report(drift_by_prof, n_total_adds)
    print(f"wrote {DRIFT_REPORT_PATH}")

    return 0


def _write_drift_report(
    drift_by_prof: dict[str, dict[str, list[str]]],
    n_adds: int,
) -> None:
    """Write docs/reports/mapping_migration_drift_2026-07-01.md."""
    lines: list[str] = [
        "# Mapping migration drift — 2026-07-01",
        "",
        "Changes that will occur when committed profession_index files are regenerated from",
        "config/mapping_overrides.yaml + committed inputs (regeneration WITH the written",
        "overrides vs the committed index — i.e. exactly what `git diff` will show when the",
        "indexes are regenerated). Each entry is one node that will be ADDED or DROPPED",
        "relative to the current committed index.",
        "",
        "Category D ('Other drift') should be nearly empty — anything there needs review.",
        "",
    ]

    categories = [
        ("flip", "A. Official→Justia URL flip",
         "Justia-only decision (2026-07-01, chapter_url_template retired): committed nodes\n"
         "carrying an official-source url flip back to their remembered justia_url on\n"
         "regeneration. Paired DROP (official url) / ADD (Justia url), same chapter."),
        ("urlform", "B. URL-form normalization",
         "Same Justia path, relative vs absolute url (hierarchy-era churn — expand_containers\n"
         "wrote relative-url duplicates). Paired DROP/ADD, same chapter; benign."),
        ("wa_umbrella", "C. WA umbrella (Ch 18.130)",
         "Nodes added by the WA Uniform Disciplinary Act umbrella mechanism (shipped Jun-30;\n"
         "indexes never regenerated since)."),
        ("other", "D. Other drift",
         "REQUIRES HUMAN REVIEW — anything not explained above. Should be nearly empty after\n"
         "the keep-rule preserved real losses. Remaining ADD lines = new base-only matches\n"
         "(junk → hand `exclude` entries); remaining DROP lines = untagged nodes not caught\n"
         "by the keep-rule (add by hand if needed)."),
    ]

    cat_totals = {k: 0 for k, _, _ in categories}
    prof_counts: dict[str, int] = {}
    for prof in sorted(drift_by_prof):
        d = drift_by_prof[prof]
        total = sum(len(d[k]) for k in d)
        if total == 0:
            continue
        prof_counts[prof] = total
        for k in cat_totals:
            cat_totals[k] += len(d.get(k) or [])

    for key, title, blurb in categories:
        lines += [f"## {title}", ""] + blurb.split("\n") + [""]
        any_hit = False
        for prof in sorted(drift_by_prof):
            cat_lines = drift_by_prof[prof].get(key) or []
            if cat_lines:
                any_hit = True
                lines.append(f"### {prof}")
                lines.extend(cat_lines)
                lines.append("")
        if not any_hit:
            lines += ["_(none)_", ""]

    total_drift = sum(cat_totals.values())
    lines += [
        "---",
        "",
        "## Category totals",
        "",
        "| Category | Lines |",
        "|---|---|",
    ]
    for key, title, _ in categories:
        lines.append(f"| {title} | {cat_totals[key]} |")
    lines += [
        f"| **Total** | **{total_drift}** |",
        "",
        f"Residual adds migrated to mapping_overrides.yaml: {n_adds}",
        "",
        "## Per-profession drift count",
        "",
        "| Profession | Changed nodes |",
        "|---|---|",
    ]
    for prof in sorted(prof_counts):
        lines.append(f"| {prof} | {prof_counts[prof]} |")
    lines.append("")

    DRIFT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DRIFT_REPORT_PATH.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
