"""LLM-FREE section-TITLE matcher — finds section-nested professions the
chapter-label matcher can't see.

match_profession works at the CHAPTER-LABEL level (results/hierarchy/<STATE>.json),
so it finds professions with their own named chapter ("Chapter 458 - Medical
Practice") but is blind to professions that live as SECTIONS inside a broad,
generically-named chapter — e.g. a public adjuster is §626.854 inside the Insurance
title, and the word "adjuster" never appears in any chapter label.

This matcher greps each profession's professions.yaml patterns against SECTION
TITLES instead. Section titles are specific ("§ 626.854 'Public adjuster' defined",
"Nonresident public adjuster license"), so a plain substring match is precise —
far less noisy than the body-density brute-force (which name-drops "public adjuster"
in unrelated producer sections). Output is a REVIEW worklist: a human eyeballs the
candidate sections, then we pull their bodies + extract.

Two title sources (--source):
  corpus     section titles from ALREADY-PULLED corpora (results/text/*/*.json) —
             a precise cross-ref: which profession is section-nested in which pulled
             sibling corpus. Free, no fetch. The validation + cheap-win source.
  hierarchy  section-level nodes in results/hierarchy/<STATE>.json (present once
             expand_containers has run depth-expansion on a state) — the "what to
             pull" answer for states we haven't pulled yet.

Usage:
  python -m pipeline.discover.match_sections --source corpus
  python -m pipeline.discover.match_sections --source corpus --profession public_adjuster
  python -m pipeline.discover.match_sections --source hierarchy --state FL
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import CONFIG_DIR, TEXT_DIR, HIERARCHY_DIR, RESULTS_DIR  # noqa: E402
from discover.match_profession import label_matches  # noqa: E402

PROF_YAML = CONFIG_DIR / "professions.yaml"
REPORT = RESULTS_DIR / "section_match_candidates.md"


def _professions() -> dict:
    return {k: v for k, v in (yaml.safe_load(PROF_YAML.read_text()) or {}).items()
            if not k.startswith("_") and (v or {}).get("patterns")}


def _section_title(sec: dict) -> str:
    """The identifying line of a section — citation + label/title/heading, NOT body."""
    if not isinstance(sec, dict):
        return ""
    return " ".join(str(sec.get(k, "")) for k in ("citation", "label", "title", "heading")).strip()


def corpus_titles() -> dict[tuple[str, str], list[str]]:
    """{(corpus_profession, state): [section titles]} from every pulled corpus."""
    out: dict[tuple[str, str], list[str]] = {}
    for f in glob.glob(str(TEXT_DIR / "*" / "*.json")):
        if "_summary" in f:
            continue
        prof = Path(f).parent.name
        state = Path(f).stem
        try:
            secs = json.loads(Path(f).read_text()).get("sections", []) or []
        except (OSError, json.JSONDecodeError):
            continue
        titles = [t for t in (_section_title(s) for s in secs) if t]
        if titles:
            out[(prof, state)] = titles
    return out


def hierarchy_titles(state: str) -> list[tuple[str, str]]:
    """[(label, url)] for every SECTION-level node in a state's expanded hierarchy.
    Section nodes are those expand_containers appended (carry parent_chapter_url)."""
    path = HIERARCHY_DIR / f"{state}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    out: list[tuple[str, str]] = []
    for ch in data.get("chapters", []) or []:
        # a chapter is a "section-ish" node when it was appended by depth-expansion
        if ch.get("parent_chapter_url") or ch.get("is_section"):
            out.append((ch.get("label", ""), ch.get("url", "")))
    return out


def match_corpus(only: str | None) -> dict[str, dict[str, list[str]]]:
    """{profession: {state: [matched section titles]}} where a profession's patterns
    hit a section title in a DIFFERENT profession's pulled corpus (section-nested)."""
    profs = _professions()
    if only:
        profs = {only: profs[only]} if only in profs else {}
    titles = corpus_titles()
    found: dict[str, dict[str, list[str]]] = {}
    for key, d in profs.items():
        pats, excl = d["patterns"], d.get("excludes", [])
        for (corpus_prof, state), sec_titles in titles.items():
            if corpus_prof == key:
                continue  # its own corpus — not a cross-ref
            hits = [t for t in sec_titles if label_matches(t, pats, excl)]
            if hits:
                found.setdefault(key, {}).setdefault(f"{state}:{corpus_prof}", []).extend(hits)
    return found


def write_report(found: dict[str, dict[str, list[str]]], source: str) -> int:
    rows = sum(len(v) for v in found.values())
    lines = [
        "# Section-title match candidates (REVIEW before pulling/extracting)",
        "",
        f"LLM-free: profession patterns matched against SECTION TITLES ({source} source). "
        f"A section *titled* for a profession is strong, specific evidence it is regulated "
        f"there — eyeball each, then pull the section bodies + extract.",
        "",
        f"**{rows} candidate location(s) across {len(found)} profession(s).**",
        "",
    ]
    for key in sorted(found):
        lines.append(f"## {key}")
        for loc, titles in sorted(found[key].items()):
            lines.append(f"- **{loc}** ({len(titles)} section(s)): "
                         + "; ".join(t[:70] for t in titles[:4])
                         + (" …" if len(titles) > 4 else ""))
        lines.append("")
    REPORT.write_text("\n".join(lines) + "\n")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["corpus", "hierarchy"], default="corpus")
    ap.add_argument("--profession", help="limit to one profession (corpus source)")
    ap.add_argument("--state", help="one state (hierarchy source)")
    args = ap.parse_args()

    if args.source == "hierarchy":
        profs = _professions()
        states = [args.state] if args.state else [Path(f).stem for f in
                  glob.glob(str(HIERARCHY_DIR / "*.json")) if "_summary" not in f]
        found: dict[str, dict[str, list[str]]] = {}
        for st in states:
            sec_nodes = hierarchy_titles(st)
            if not sec_nodes:
                if args.state:
                    print(f"  {st}: no section-level nodes — run expand_containers first")
                continue
            for key, d in profs.items():
                hits = [lbl for lbl, _ in sec_nodes if label_matches(lbl, d["patterns"], d.get("excludes", []))]
                if hits:
                    found.setdefault(key, {})[st] = hits
        n = write_report(found, "hierarchy")
        print(f"wrote {n} section-title candidate(s) across {len(found)} profession(s) to {REPORT.relative_to(RESULTS_DIR.parent.parent)}")
        return 0

    found = match_corpus(args.profession)
    for key in sorted(found):
        print(f"\n{key}:")
        for loc, titles in sorted(found[key].items()):
            print(f"  {loc}: {len(titles)} section(s) — {titles[0][:70]}")
    n = write_report(found, "corpus")
    print(f"\nwrote {n} candidate(s) across {len(found)} profession(s) to {REPORT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
