"""Produce per-state aggregate blobs for the /browse/<state> view.

The per-profession /browse/<state>/<prof> view ships only ONE profession's
sections. This view aggregates across all six professions: every umbrella
section for a state PLUS every profession's practice-act sections, all in
one blob the page can filter client-side.

Output: pipeline/publish/web/public/data/state/<XX>.json + uploaded to
Vercel Blob under the same path. One blob per state, ~3-8 MB depending on
state size.

Each section is tagged with `audience`:
  - "universal":      umbrella section that applies to every licensee
                      (scope_source ∈ universal / anchor_universal)
  - "multi":          umbrella section that applies to a specific set
                      of professions (scope_source ∈ anchor_enumeration /
                      inherited_enumeration); applies_to lists the set
  - "single":         practice-act section, belongs to a single profession;
                      `profession` field carries which one

Evidence per section is aggregated across all professions — if both
nursing and podiatry drew a quote from the same umbrella section, both
appear under that section.

Usage:
  python -m pipeline.publish.build_state_browse              # all 50 states
  python -m pipeline.publish.build_state_browse --state AZ   # one state
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Make sibling modules importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _env import load_env  # noqa: E402
load_env()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from extract.standard_model import iter_evidence  # noqa: E402
from extract.locate_quote import locate_quote_in_section  # noqa: E402
from scope_sources import is_universal, is_enumeration  # noqa: E402
from merged_scope import merged_scope_by_url  # noqa: E402
from publish.blob_upload import upload_json  # noqa: E402
from publish._browse_tree import build_tree  # noqa: E402
from publish._justia_clean import clean_justia_text  # noqa: E402
from paths import RESULTS_DIR, TRIMMED_DIR, STRUCTURED_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("build_state_browse")

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"

PROFESSIONS = [
    "podiatry", "nursing", "medicine", "dentistry", "optometry", "public_accountancy",
    "construction_trades", "electrician", "plumbing", "hvac",
    "architecture", "professional_engineering",
]


def _load_scope_lookup(state: str) -> dict[str, dict]:
    """{url → merged section} for a state — walker scope with Pass-3 LLM
    decisions overlaid (see pipeline/merged_scope.py)."""
    return merged_scope_by_url(state)


def _section_evidence_for_profession(
    record: dict, text: str, profession: str,
) -> list[dict]:
    """For one section's text, find all Evidence in `record` whose quote
    matches in it. Returns list of {field_path, value, quote, spans,
    unverified, profession} — profession identifies WHICH extraction
    pulled this quote, so the UI can show "nursing drew X from here".
    """
    if not text:
        return []
    out: list[dict] = []
    for path, node in iter_evidence(record):
        quote = node.get("quote") or ""
        if not quote:
            continue
        spans = locate_quote_in_section(quote, text)
        if not spans:
            continue
        out.append({
            "field_path": ".".join(str(p) for p in path),
            "value": node.get("value"),
            "quote": quote,
            "spans": [list(p) for p in spans],
            "unverified": bool(node.get("unverified")),
            "profession": profession,
        })
    return out


def _aggregate_evidence(text: str, prof_records: dict[str, dict]) -> list[dict]:
    """Run the evidence-quote matcher across ALL professions' structured
    records for this state. Returns merged list of evidence-spans, each
    tagged with which profession produced it."""
    out: list[dict] = []
    for prof, rec in prof_records.items():
        out.extend(_section_evidence_for_profession(rec, text, prof))
    return out


def build_state(state: str) -> dict[str, Any] | None:
    """Aggregate every profession's data for one state into a single
    browseable structure."""
    state = state.upper()

    # Load each profession's structured record + trimmed sections, if present.
    prof_records: dict[str, dict] = {}
    prof_practice: dict[str, list[dict]] = {}
    for prof in PROFESSIONS:
        struct_path = STRUCTURED_DIR / prof / f"{state}.json"
        trimmed_path = TRIMMED_DIR / prof / f"{state}.json"
        if not struct_path.exists() or not trimmed_path.exists():
            continue
        prof_records[prof] = json.loads(struct_path.read_text())
        trimmed = json.loads(trimmed_path.read_text())
        prof_practice[prof] = [
            {"url": s.get("url"), "citation": s.get("citation"),
             "label": s.get("label"), "text": s.get("text")}
            for s in (trimmed.get("sections") or []) if s.get("text")
        ]

    if not prof_records:
        return None

    umb_scope = _load_scope_lookup(state)
    umb_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    umb_data = json.loads(umb_path.read_text()) if umb_path.exists() else None

    sections: list[dict] = []

    # 1. Umbrella sections (universal + multi-prof enumeration).
    if umb_data:
        for s in umb_data.get("sections") or []:
            # Umbrella scraper preserved Justia's navigation chrome
            # (version list, breadcrumbs, citation explainer, disclaimer).
            # Strip it on the publish side so the browse view shows just
            # the statute text.
            text = clean_justia_text(s.get("text") or "")
            url = s.get("url") or ""
            if not text or not url:
                continue
            info = umb_scope.get(url) or {}
            scope_source = info.get("scope_source") or ""
            applies_to = info.get("applies_to_professions")

            if is_universal(scope_source):
                audience = "universal"
                applies_to = None  # explicit: applies to all
            elif is_enumeration(scope_source):
                audience = "multi"
                # Filter applies_to to the professions we actually track
                # (the scope assigner may emit names beyond our 6).
                if applies_to:
                    applies_to = [p for p in applies_to if p in PROFESSIONS]
                if not applies_to:
                    # Multi-prof but the set doesn't intersect our tracked
                    # professions — skip rather than show an empty bucket.
                    continue
            else:
                # undetermined — skip
                continue

            chap_label = (s.get("umbrella_chapter_label") or "").strip()
            label = s.get("label") or chap_label or "umbrella section"

            sections.append({
                "url": url,
                "citation": label,
                "label": label,
                "text": text,
                "audience": audience,
                "applies_to": applies_to,
                "profession": None,
                "scope_source": scope_source,
                "evidence": _aggregate_evidence(text, prof_records),
            })

    # 2. Practice-act sections per profession.
    for prof, practice in prof_practice.items():
        # Only THIS profession's record was used to find evidence for its
        # own practice-act sections — cross-profession matching would be
        # noise (e.g. a podiatry quote happening to land in a nursing
        # practice-act section is almost always coincidence).
        rec = prof_records.get(prof) or {}
        for s in practice:
            # Practice-act trimmed sections also carry Justia chrome
            # (breadcrumb + citation header + disclaimer). Strip it so the
            # detail panel renders only the statute paragraphs.
            text = clean_justia_text(s.get("text") or "")
            if not text:
                continue
            sections.append({
                "url": s.get("url") or "",
                "citation": s.get("citation") or "",
                "label": s.get("label") or "",
                "text": text,
                "audience": "single",
                "applies_to": [prof],
                "profession": prof,
                "scope_source": None,
                "evidence": _section_evidence_for_profession(rec, text, prof),
            })

    # Build hierarchical trees per audience group. Universal first, then
    # multi-prof buckets keyed by their exact applies_to set, then single-
    # prof buckets per profession. Each group's `tree` is a forest of
    # nested branches (title → chapter/article → part → section) derived
    # from the section URLs by _browse_tree.build_tree.
    chapter_labels: dict[str, str] = {}
    if umb_data:
        for s in umb_data.get("sections") or []:
            slug = s.get("umbrella_chapter_slug")
            label = s.get("umbrella_chapter_label")
            if slug and label and slug not in chapter_labels:
                chapter_labels[slug] = label

    universal = [s for s in sections if s["audience"] == "universal"]
    multi = [s for s in sections if s["audience"] == "multi"]
    single_by_prof: dict[str, list[dict]] = {}
    for s in sections:
        if s["audience"] == "single" and s.get("profession"):
            single_by_prof.setdefault(s["profession"], []).append(s)

    # One "Multi-profession" group instead of one per unique applies_to set
    # — the per-section applies_to is surfaced as a chip on each leaf
    # instead of being baked into a separate group header. Cuts visual
    # noise on states with many enumerated chapters.
    groups: list[dict] = []
    if universal:
        groups.append({
            "key": "universal",
            "kind": "universal",
            "tree": build_tree(universal, chapter_label_overrides=chapter_labels),
        })
    if multi:
        groups.append({
            "key": "multi",
            "kind": "multi",
            "tree": build_tree(multi, chapter_label_overrides=chapter_labels),
        })
    for prof, secs in sorted(single_by_prof.items()):
        groups.append({
            "key": f"single:{prof}",
            "kind": "single",
            "profession": prof,
            "tree": build_tree(secs),
        })

    return {
        "state": state,
        "professions_available": sorted(prof_records.keys()),
        "groups": groups,
        # Keep the flat sections list too for any caller that wants it —
        # it's redundant with the trees but small relative to the rest.
        "sections": sections,
    }


def write_and_upload(state: str, payload: dict, *, upload: bool = True) -> None:
    out_dir = Path(__file__).resolve().parent / "web" / "public" / "data" / "state"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{state}.json"
    body = json.dumps(payload, indent=2)
    out_path.write_text(body)
    if upload:
        url, skipped = upload_json(f"data/state/{state}.json", body)
        log.info("[%s] %s %d sections (%d bytes) → %s",
                 state, "cached" if skipped else "uploaded",
                 len(payload["sections"]), len(body), url)
    else:
        log.info("[%s] wrote %d sections (%d bytes, local only)",
                 state, len(payload["sections"]), len(body))


def write_states_index(entries: list[dict], *, upload: bool = True) -> None:
    """Emit /states.json — the homepage's state picker reads this to render
    the by-state card list. Same role as /professions.json for the by-
    profession view. Each entry: { state, sections, professions }."""
    out_dir = Path(__file__).resolve().parent / "web" / "public"
    body = json.dumps(entries, indent=2)
    (out_dir / "states.json").write_text(body)
    if upload:
        url, skipped = upload_json("states.json", body)
        log.info("states.json (%d entries) %s → %s",
                 len(entries), "cached" if skipped else "uploaded", url)
    else:
        log.info("wrote states.json with %d entries (local only)", len(entries))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", help="One state code (else all)")
    ap.add_argument("--no-upload", action="store_true",
                    help="Skip Blob upload, write local only")
    ap.add_argument("--skip-index", action="store_true",
                    help="Don't rebuild /states.json (use when running one state)")
    args = ap.parse_args()

    states = [args.state.upper()] if args.state else list(ALL_STATES)
    upload = not args.no_upload

    entries: list[dict] = []
    for st in states:
        payload = build_state(st)
        if payload is None:
            log.info("[%s] no data, skipping", st)
            continue
        write_and_upload(st, payload, upload=upload)
        entries.append({
            "state": st,
            "sections": len(payload["sections"]),
            "professions": payload["professions_available"],
        })

    # Only rewrite the index when we just built every state, otherwise
    # we'd be regenerating it from a partial set.
    if not args.skip_index and not args.state:
        entries.sort(key=lambda e: e["state"])
        write_states_index(entries, upload=upload)


if __name__ == "__main__":
    main()
