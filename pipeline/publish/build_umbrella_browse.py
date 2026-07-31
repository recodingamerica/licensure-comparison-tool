"""Per-state umbrella browse data — the data backing /umbrella/<STATE>.

For every state that has an umbrella_scope (walker + Pass 3 merged), emit a
self-contained file:

  pipeline/publish/web/public/data/umbrella/<STATE>.json

shape:
  {
    state, section_count, coverage: {universal, enumerated, undetermined},
    chapters: [
      {slug, label, sections: [
        {url, label, audience, applies_to, text}
      ]}
    ],
    all_professions: [...]   # every profession id assigned anywhere in the state
  }

Each section's `audience` is one of:
  "universal"     -> applies to all licensed professions in the state
                    (applies_to: null)
  "enumerated"    -> applies_to is the explicit list
  "undetermined"  -> the pipeline couldn't auto-scope it; honest residual

Unlike `build_state_browse`, this does NOT filter to a 6-profession subset and
does NOT need the trimmed/structured corpus — it works for every state with
umbrella data (43 today). Pure umbrella view.
"""

from __future__ import annotations

import argparse
import json
import logging
from collections import defaultdict
from pathlib import Path

from pipeline.paths import RESULTS_DIR, WEB_DATA_DIR
from pipeline._records import record_files
from pipeline.scope.scope_sources import is_universal, is_enumeration
from pipeline.scope.merged_scope import load_merged_scope
from pipeline.discover._profession_reverse_index import build_reverse_index

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
OUT_DIR = WEB_DATA_DIR / "umbrella"
# Derived inside main() so test monkeypatching of OUT_DIR flows through.

# Length of section text kept inline for the browse view. Full text is in
# umbrella_text — UI can fetch on demand if it needs more.
TEXT_SNIPPET_CHARS = 600

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build_umbrella_browse")


def _classify(scope_source: str | None) -> str:
    if is_universal(scope_source):
        return "universal"
    if is_enumeration(scope_source):
        return "enumerated"
    return "undetermined"


def build_state_umbrella(state: str) -> dict | None:
    """Assemble the umbrella browse payload for one state, or None if the
    state has no umbrella_scope (no walker output and no skeleton)."""
    merged = load_merged_scope(state)
    if merged is None:
        return None
    text_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    text_by_url: dict[str, dict] = {}
    if text_path.exists():
        for s in json.loads(text_path.read_text()).get("sections", []):
            text_by_url[s.get("url")] = s

    chap_label: dict[str, str] = {}
    chap_sections: dict[str, list[dict]] = defaultdict(list)
    coverage = {"universal": 0, "enumerated": 0, "undetermined": 0}
    all_profs: set[str] = set()

    for s in merged.get("sections", []):
        url = s.get("url") or ""
        chap = s.get("umbrella_chapter_slug") or ""
        if not url or not chap:
            continue
        audience = _classify(s.get("scope_source"))
        coverage[audience] += 1
        applies = s.get("applies_to_professions")
        if audience == "enumerated":
            all_profs.update(applies or [])
            applies_out: list[str] | None = sorted(set(applies or []))
        elif audience == "universal":
            applies_out = None
        else:
            applies_out = None  # undetermined

        ts = text_by_url.get(url, {})
        if not chap_label.get(chap):
            chap_label[chap] = (ts.get("umbrella_chapter_label") or chap).strip()
        full_text = (ts.get("text") or "").strip()
        snippet = full_text[:TEXT_SNIPPET_CHARS] + ("…" if len(full_text) > TEXT_SNIPPET_CHARS else "")
        chap_sections[chap].append({
            "url": url,
            "label": s.get("label") or "(unlabeled section)",
            "audience": audience,
            "applies_to": applies_out,
            "text": snippet,
        })

    chapters_out = [
        {"slug": slug, "label": chap_label.get(slug, slug),
         "sections": chap_sections[slug]}
        for slug in sorted(chap_sections, key=lambda k: chap_label.get(k, k))
    ]
    return {
        "state": state,
        "section_count": sum(coverage.values()),
        "coverage": coverage,
        "all_professions": sorted(all_profs),
        "chapters": chapters_out,
    }


def _states_with_scope() -> list[str]:
    scope_dir = RESULTS_DIR / "umbrella_scope"
    return [p.stem for p in record_files(scope_dir)]


def _build_by_profession(
    state_payloads: dict[str, dict],
    state_regulates: dict[str, set[str]],
) -> dict[str, dict]:
    """Pivot per-state payloads into per-profession payloads.

    For each profession id, emit per-state cards listing the sections that
    apply: every universal section in a state that regulates the profession,
    plus every enumerated section whose applies_to lists the profession.
    `directly_enumerated` counts only the enumerated hits — useful to separate
    "actively named" from "swept in by universal".

    Each state card also carries the state's *unclassified* umbrella sections —
    sections neither walker nor Pass 3 could confidently scope. They may or
    may not apply to this profession; we surface them as honest residual so
    the user can spot-check rather than silently hiding them.
    """
    # profession -> state -> {chapter_slug -> [section]} (filtered) + chapter labels
    # Each section's `audience` is one of (mirrors lib/audience.ts):
    #   "universal" — applies to every licensed profession in the state
    #   "multi"     — enumerated; applies_to lists multiple professions
    #                 including this one (e.g. "all medical professions")
    #   "single"    — enumerated; applies_to is exactly [this_profession]
    bucket: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {
        "chapter_labels": {},
        "sections_by_chapter": defaultdict(list),
        "universal": 0,
        "multi": 0,
        "single": 0,
    }))

    # state -> chapters of undetermined sections, shared across all professions
    # the state regulates (the residual is the same regardless of profession).
    undetermined_by_state: dict[str, dict] = {}
    for st, payload in state_payloads.items():
        ch_labels: dict[str, str] = {}
        ch_secs: dict[str, list[dict]] = defaultdict(list)
        n_undetermined = 0
        for ch in payload["chapters"]:
            for sec in ch["sections"]:
                if sec["audience"] != "undetermined":
                    continue
                ch_labels[ch["slug"]] = ch["label"]
                ch_secs[ch["slug"]].append(sec)
                n_undetermined += 1
        undetermined_by_state[st] = {
            "count": n_undetermined,
            "chapters": [
                {"slug": s, "label": ch_labels[s], "sections": ch_secs[s]}
                for s in sorted(ch_secs, key=lambda k: ch_labels.get(k, k))
            ],
        }

    for st, payload in state_payloads.items():
        regulates = state_regulates.get(st, set())
        for ch in payload["chapters"]:
            for sec in ch["sections"]:
                if sec["audience"] == "universal":
                    targets = regulates
                    kind = "universal"
                elif sec["audience"] == "enumerated":
                    targets = set(sec["applies_to"] or [])
                    kind = "multi" if len(targets) > 1 else "single"
                else:
                    continue  # undetermined — surfaced separately as residual
                for pid in targets:
                    b = bucket[pid][st]
                    b["chapter_labels"][ch["slug"]] = ch["label"]
                    # Stash the audience kind alongside the original walker
                    # audience so the page renders consistent badges. multi
                    # vs single depends on len(applies_to) — same for every
                    # pid in `targets`.
                    section_with_kind = {**sec, "audience_kind": kind}
                    b["sections_by_chapter"][ch["slug"]].append(section_with_kind)
                    b[kind] += 1

    out: dict[str, dict] = {}
    for pid, state_map in bucket.items():
        states_out = []
        totals = {"universal": 0, "multi": 0, "single": 0, "unclassified_in_state": 0}
        for st in sorted(state_map):
            b = state_map[st]
            chapters_out = []
            for slug in sorted(b["sections_by_chapter"],
                               key=lambda k: b["chapter_labels"].get(k, k)):
                chapters_out.append({
                    "slug": slug,
                    "label": b["chapter_labels"][slug],
                    "sections": b["sections_by_chapter"][slug],
                })
            ures = undetermined_by_state.get(st, {"count": 0, "chapters": []})
            n_classified = b["universal"] + b["multi"] + b["single"]
            states_out.append({
                "state": st,
                "section_count": n_classified,
                "coverage": {
                    "universal": b["universal"],
                    "multi": b["multi"],
                    "single": b["single"],
                    "unclassified_in_state": ures["count"],
                },
                "chapters": chapters_out,
                "unclassified_chapters": ures["chapters"],
            })
            totals["universal"] += b["universal"]
            totals["multi"] += b["multi"]
            totals["single"] += b["single"]
            totals["unclassified_in_state"] += ures["count"]
        # Sort states by classified section count (descending), so the meatiest
        # states surface first on the page.
        states_out.sort(key=lambda s: -s["section_count"])
        out[pid] = {
            "profession": pid,
            "state_count": len(states_out),
            "directly_enumerated_state_count": sum(
                1 for s in states_out if s["coverage"]["multi"] + s["coverage"]["single"] > 0
            ),
            "section_count": totals["universal"] + totals["multi"] + totals["single"],
            "coverage": totals,
            "states": states_out,
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", help="single state (default: every state with umbrella_scope)")
    args = ap.parse_args()

    states = [args.state.upper()] if args.state else _states_with_scope()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    prof_out_dir = OUT_DIR / "by_profession"
    prof_out_dir.mkdir(parents=True, exist_ok=True)

    index_states: list[dict] = []
    all_profession_ids: set[str] = set()
    # (state, profession) -> count of umbrella sections that apply
    matrix: dict[str, dict[str, int]] = {}
    written = 0
    state_payloads: dict[str, dict] = {}
    state_regulates: dict[str, set[str]] = {}
    for st in states:
        payload = build_state_umbrella(st)
        if payload is None:
            log.info("[%s] no umbrella_scope — skipped", st)
            continue
        (OUT_DIR / f"{st}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        written += 1
        state_payloads[st] = payload

        # Per-(state, profession) section count: a universal section counts for
        # every profession the state regulates (per its reverse_index); an
        # enumerated section counts only for the professions it lists.
        state_profs = set(p for ids in build_reverse_index(st).values() for p in ids)
        state_regulates[st] = state_profs
        all_profession_ids.update(state_profs)
        n_universal = payload["coverage"]["universal"]
        per_prof: dict[str, int] = {p: n_universal for p in state_profs}
        for ch in payload["chapters"]:
            for sec in ch["sections"]:
                if sec["audience"] == "enumerated":
                    for p in (sec["applies_to"] or []):
                        per_prof[p] = per_prof.get(p, 0) + 1
        matrix[st] = {p: n for p, n in per_prof.items() if n > 0}

        index_states.append({
            "state": st,
            "section_count": payload["section_count"],
            "coverage": payload["coverage"],
            "profession_count": len(payload["all_professions"]),
            "state_regulates": sorted(state_profs),
        })

    index = {
        "states": index_states,
        "professions": sorted(all_profession_ids),
        "matrix": matrix,   # {state: {profession: count}}
    }
    (OUT_DIR / "_index.json").write_text(json.dumps(index, indent=2))

    by_prof = _build_by_profession(state_payloads, state_regulates)
    # Clean stale per-profession files (rename / removal) before writing.
    for stale in record_files(prof_out_dir):
        if stale.stem not in by_prof:
            stale.unlink()
    prof_index = []
    for pid in sorted(by_prof):
        rec = by_prof[pid]
        (prof_out_dir / f"{pid}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
        prof_index.append({
            "profession": pid,
            "state_count": rec["state_count"],
            "directly_enumerated_state_count": rec["directly_enumerated_state_count"],
            "section_count": rec["section_count"],
            "coverage": rec["coverage"],
        })
    (prof_out_dir / "_index.json").write_text(json.dumps({"professions": prof_index}, indent=2))

    log.info("wrote %d per-state umbrella files + _index.json (matrix across %d states × %d professions) "
             "+ %d per-profession files to %s",
             written, len(index_states), len(all_profession_ids), len(by_prof), OUT_DIR)


if __name__ == "__main__":
    main()
