"""Remove Justia year-versioned duplicate sections from committed corpora.

Justia serves the same statute under `/codes/<state>/2023/...`, `/2024/...`, AND an
undated `/codes/<state>/...` path. `pull_text._dedupe_year_versions` collapses those
to one copy per section, and it runs on every fresh pull — but corpora pulled before
that dedup was added still carry all the copies. This applies the SAME dedup to the
already-committed corpora in place, with NO re-fetch (per CLAUDE.md: the transform is
safe to run on committed `sections`).

It is a pure local transform: fresh pulls are already de-duped, so this only cleans
up stale corpora and can't lose a section that isn't a year-duplicate of another.

  # report what would change (default — writes nothing):
  python -m pipeline.ingest.dedupe_corpora
  # write the de-duped corpora:
  python -m pipeline.ingest.dedupe_corpora --apply
  # limit to some professions:
  python -m pipeline.ingest.dedupe_corpora --professions medicine,nursing --apply

NOTE (downstream): de-duping text/ makes it inconsistent with the structured/ records
that were extracted from the bloated corpora — those cells need re-running through
clean -> trim -> extract (and a republish) for the change to reach the site. That is
a separate, cost-bearing step; this command only cleans the corpus text.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

from pipeline.ingest.pull_text import _dedupe_year_versions
from pipeline.paths import TEXT_DIR, CLEAN_DIR, TRIMMED_DIR
from pipeline._records import record_files, read_json

# The derived stages carry the same year-duplicate sections as text/. De-duping
# them directly (rather than re-running clean/trim) lets a republish reflect the
# fix without paying for the LLM trim/extract — the browse view reads trimmed/.
STAGES = ("text", "clean", "trimmed")


def _stage_dir(stage: str):
    # resolved at call time so tests can monkeypatch the dir module-globals
    return {"text": TEXT_DIR, "clean": CLEAN_DIR, "trimmed": TRIMMED_DIR}[stage]


def dedupe_corpus(d: dict) -> dict | None:
    """Return a de-duped copy of a corpus dict, or None if nothing changed. Recomputes
    total_chars from the surviving sections."""
    secs = d.get("sections") or []
    deduped = _dedupe_year_versions([dict(s) for s in secs])
    if len(deduped) == len(secs):
        return None
    nd = dict(d)
    nd["sections"] = deduped
    nd["total_chars"] = sum(len(s.get("text") or "") for s in deduped)
    return nd


# --- same-citation duplicates (2026-07-29) -----------------------------------------
# The UI resolves quote highlights by CITATION, last-wins — a corpus carrying two
# sections with the same citation string makes one unreachable. Measured 140 duplicate
# copies across the 13 published professions and classified them; only the two
# MECHANICAL classes are collapsed here:
#   identical_text — the same law fetched twice (same citation, byte-identical text).
#   edition_pair   — the same section under two year-stamped editions whose PATHS
#                    differ beyond the year (2022 /title-12/... vs 2023
#                    /title-12/health-care-professions-and-occupations/...), which the
#                    year-normalizing dedupe above can't see. Keep the newest edition.
# NEVER touched (they are different law sharing a citation string, or need triage):
#   PA flat acts ("§ 1" of the 1951 act vs the 1955 act — legis.state.pa.us), and
#   Justia SUBSECTION pages (different trailing section slugs, e.g. section-61-28b-3
#   vs section-61-28b-3-d-1). Those need citation disambiguation, not deletion.

_URL_YEAR = re.compile(r"/(19|20)(\d\d)/")


def _slug(url: str) -> str:
    parts = [p for p in (url or "").rstrip("/").split("/") if p]
    return parts[-1] if parts else ""


def dedupe_citation_copies(d: dict) -> tuple[dict | None, dict]:
    """Collapse the mechanical same-citation duplicate classes. Returns
    (deduped corpus or None if unchanged, {class: n_removed})."""
    secs = d.get("sections") or []
    by_cit: dict[str, list[int]] = {}
    for i, s in enumerate(secs):
        if isinstance(s, dict) and s.get("citation") and not s.get("error"):
            by_cit.setdefault(s["citation"], []).append(i)
    drop: set[int] = set()
    removed = {"identical_text": 0, "edition_pair": 0}
    for cit, idxs in by_cit.items():
        if len(idxs) < 2:
            continue
        copies = [secs[i] for i in idxs]
        urls = [c.get("url") or "" for c in copies]
        if any("legis.state.pa.us" in u for u in urls):
            continue                                    # flat acts: different law, keep all
        texts = [c.get("text") or "" for c in copies]
        if len(set(texts)) == 1:
            drop.update(idxs[1:])                       # same law twice: keep the first
            removed["identical_text"] += len(idxs) - 1
            continue
        if len({_slug(u) for u in urls}) > 1:
            continue                                    # subsection pages: needs triage, keep all
        years = [m and int(m.group(1) + m.group(2)) for m in (_URL_YEAR.search(u) for u in urls)]
        if all(years) and len(set(years)) > 1:
            keep = idxs[years.index(max(years))]        # editions: keep the newest year
            drop.update(i for i in idxs if i != keep)
            removed["edition_pair"] += len(idxs) - 1
    if not drop:
        return None, removed
    nd = dict(d)
    nd["sections"] = [s for i, s in enumerate(secs) if i not in drop]
    nd["total_chars"] = sum(len(s.get("text") or "") for s in nd["sections"]
                            if isinstance(s, dict))
    return nd, removed


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true",
                    help="Write the de-duped corpora. Default is a dry-run report.")
    ap.add_argument("--professions", default="",
                    help="Comma-separated subset (e.g. medicine,nursing); empty = all.")
    ap.add_argument("--stages", default="text",
                    help="Comma-separated result stages to dedupe: text,clean,trimmed "
                         "(default text). clean/trimmed let a republish reflect the fix "
                         "without re-running the LLM stages.")
    ap.add_argument("--citations", action="store_true",
                    help="Also collapse the mechanical same-citation duplicate classes "
                         "(identical_text + edition_pair; PA flat acts and Justia "
                         "subsection pages are never touched).")
    args = ap.parse_args(argv)
    only = {p.strip() for p in args.professions.split(",") if p.strip()}
    stages = [s.strip() for s in args.stages.split(",") if s.strip()]
    unknown = [s for s in stages if s not in STAGES]
    if unknown:
        sys.exit(f"unknown stage(s): {unknown} — choose from {list(STAGES)}")

    changed = 0
    removed = 0
    for stage in stages:
        base = _stage_dir(stage)
        for prof_dir in sorted(base.glob("*")):
            if not prof_dir.is_dir():
                continue
            prof = prof_dir.name
            if only and prof not in only:
                continue
            for path in record_files(prof_dir):
                d = read_json(path)
                if not isinstance(d, dict):
                    continue
                labels = []
                nd = dedupe_corpus(d)
                if nd is not None:
                    labels.append("year-versions")
                if args.citations:
                    nd2, by_class = dedupe_citation_copies(nd or d)
                    if nd2 is not None:
                        nd = nd2
                        labels += [f"{k}:{v}" for k, v in by_class.items() if v]
                if nd is None:
                    continue
                before, after = len(d["sections"]), len(nd["sections"])
                changed += 1
                removed += before - after
                print(f"  {stage}/{prof}/{path.stem}: {before} -> {after}  "
                      f"(-{before - after}; {', '.join(labels)})")
                if args.apply:
                    path.write_text(json.dumps(nd, indent=2))

    verb = "removed" if args.apply else "would remove"
    tail = "" if args.apply else "  (dry-run — pass --apply to write)"
    print(f"\n{changed} corpora across {stages}, {verb} {removed} "
          f"year-versioned duplicate sections{tail}")
    if not changed:
        sys.exit(0)


if __name__ == "__main__":
    main()
