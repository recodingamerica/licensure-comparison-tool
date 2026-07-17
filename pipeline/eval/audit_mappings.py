"""Audit committed corpora for broken / absent chapter mappings (read-only).

The annual refresh surfaced cells that have a committed corpus but no PULLABLE
mapping in the frozen index — e.g. land_surveying/WY has one stray title-level
section and an empty `matched` list, so a re-pull yields EMPTY. This finds them:

  NO_MAPPING  — a committed corpus exists but the frozen index has no matched
                chapters for that state (empty/missing `matched`). A re-pull would
                return nothing; the committed sections can't be reproduced.
  STRAY_ONLY  — the corpus's sections sit under NO mapped chapter (they're
                title-level strays), so a re-pull can't reproduce them either.
  SOME_STRAY  — some sections aren't under any mapped chapter (partial gap).

Writes nothing. Run:  python -m pipeline.eval.audit_mappings
"""

from __future__ import annotations

import argparse
import collections
import json

from pipeline.paths import TEXT_DIR, PROFESSION_INDEX_DIR
from pipeline._records import record_files
# reuse the SAME attribution logic the refresh uses (single source of truth)
from pipeline.ingest.refresh_corpus import sections_per_chapter
from pipeline.ingest._section_patterns import container_segment

def _is_leaf(url: str) -> bool:
    """True unless `url`'s last path segment is a bare container landing page
    (the shared CONTAINER_SEG classifier — see pipeline.ingest._section_patterns)."""
    return not container_segment(url)


def _index_chapters(profession: str) -> dict[str, list[str]]:
    """{STATE: [chapter_url, ...]} from the frozen index — the re-pull source of truth."""
    idx_path = PROFESSION_INDEX_DIR / f"{profession}.json"
    if not idx_path.exists():
        return {}
    idx = json.loads(idx_path.read_text())
    out: dict[str, list[str]] = {}
    for st, node in (idx.get("by_state") or {}).items():
        out[st] = [n["url"] for n in (node.get("matched") or []) if n.get("url")]
    return out


def audit() -> list[tuple[str, str, str, str]]:
    """Return (profession, state, issue, detail) for every cell with a mapping gap."""
    findings = []
    for prof_dir in sorted(TEXT_DIR.glob("*")):
        if not prof_dir.is_dir():
            continue
        prof = prof_dir.name
        by_state = _index_chapters(prof)
        for path in record_files(prof_dir):
            state = path.stem
            try:
                sections = (json.loads(path.read_text()).get("sections")) or []
            except (OSError, json.JSONDecodeError):
                continue
            if not sections:
                continue
            n = len(sections)
            # Only-landing-page junk: a SMALL corpus (<=3) whose every "section" is a
            # container page — i.e. the walk captured a chapter/title page and no real
            # sections (land_surveying/WY = 1x chapter-29). Capped at 3 so a large,
            # genuine corpus that merely uses container-ish section URLs (ND/IL act
            # structures) isn't false-flagged.
            if n <= 3 and not any(_is_leaf(s.get("url", "")) for s in sections):
                findings.append((prof, state, "TITLE_STRAY",
                                 f"{n} section(s), only a container/landing page (no real sections)"))
                continue
            chapter_urls = by_state.get(state) or []
            if not chapter_urls:
                findings.append((prof, state, "NO_MAPPING",
                                 f"{n} committed section(s), index has no matched chapters"))
                continue
            attributed = sum(sections_per_chapter(chapter_urls, sections).values())
            if attributed == 0:
                findings.append((prof, state, "STRAY_ONLY",
                                 f"{n} section(s), none under a mapped chapter"))
            elif attributed < n:
                findings.append((prof, state, "SOME_STRAY",
                                 f"{n - attributed}/{n} section(s) not under a mapped chapter"))
    return findings


def main(argv: list[str] | None = None) -> None:
    argparse.ArgumentParser(description=__doc__.split("\n\n")[0]).parse_args(argv)
    findings = audit()
    by_type = collections.Counter(f[2] for f in findings)
    print(f"scanned committed corpora — {len(findings)} cell(s) with mapping gaps: {dict(by_type)}")
    for prof, state, issue, detail in sorted(findings, key=lambda f: (f[2], f[0], f[1])):
        print(f"  {prof}/{state}  [{issue}]  {detail}")


if __name__ == "__main__":
    main()
