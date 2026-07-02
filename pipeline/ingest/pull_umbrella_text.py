"""Pull text for the umbrella / cross-cutting chapters identified by
find_umbrella_chapters.py. Output: results/umbrella_text/<STATE>.json
with the same section-list shape as results/text/<profession>/<STATE>.json.

Once cached, extract_state can read this and include it as supplemental
context when extracting any profession in the state.

Usage:
  python -m pipeline.ingest.pull_umbrella_text --state TX
  python -m pipeline.ingest.pull_umbrella_text          # all states with umbrella files
"""

from __future__ import annotations

import argparse
import json
import logging
import time

from pipeline.paths import RESULTS_DIR, LOGS_DIR
from pipeline.config.states import ALL_STATES
from pipeline._fetch_config import PER_HOST_DELAY  # noqa: E402

# Reuse the existing pull infrastructure
from pipeline.ingest.pull_text import (  # noqa: E402
    fetch, is_section_url, extract_section_text, collect_section_targets,
)

UMBRELLA_TEXT_DIR = RESULTS_DIR / "umbrella_text"
UMBRELLA_CHAPTERS_DIR = RESULTS_DIR / "umbrella_chapters"
LOG_PATH = LOGS_DIR / "pull_umbrella_text.log"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
UMBRELLA_TEXT_DIR.mkdir(parents=True, exist_ok=True)

# No per-chapter section cap: the corpus on disk is the durable asset, so the
# puller NEVER decides relevance or truncates. A huge chapter (IN article-0.5
# declares 345 sections) is logged loudly so the operator can judge whether it's
# really umbrella law — that judgment belongs to a human/agent at run time, not
# to a number in this file. Over-pulling text is not a failure mode.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, mode="w"), logging.StreamHandler()],
)
log = logging.getLogger("pull_umbrella_text")


def select_umbrella_chapters(
    chapters: list[dict],
    cached_slugs: set[str],
    manifest_blessed: set[str],
    manifest_dropped: set[str],
) -> tuple[list[dict], list[tuple[str, str, str]]]:
    """label_filter selection: keep a chapter if its label matches _UMBRELLA_LABEL
    OR its slug is blessed (scope manifest) OR already cached with text —
    UNLESS the manifest drops it (authoritative, wins over everything).

    Returns (kept, drop_log) where drop_log is [(slug, label, reason), ...].
    """
    from pipeline.discover.umbrella_from_citations import _UMBRELLA_LABEL

    kept: list[dict] = []
    drop_log: list[tuple[str, str, str]] = []

    for ch in chapters:
        slug = ch.get("slug", "")
        label = ch.get("label", "")

        if slug in manifest_dropped:
            drop_log.append((slug, label, "manifest-drop"))
            continue

        label_match = bool(_UMBRELLA_LABEL.search(label))
        blessed = slug in manifest_blessed
        cached = slug in cached_slugs

        if label_match or blessed or cached:
            kept.append(ch)
        else:
            drop_log.append((slug, label, "no-label-match-and-not-blessed"))

    return kept, drop_log


def pull_state_umbrella(state: str, force: bool, source_filter: str | None = None,
                        label_filter: bool = False) -> dict | None:
    umb_path = UMBRELLA_CHAPTERS_DIR / f"{state}.json"
    out_path = UMBRELLA_TEXT_DIR / f"{state}.json"
    if not umb_path.exists():
        log.info("[%s] no umbrella_chapters file, skip", state)
        return None

    rec = json.loads(umb_path.read_text())
    chapters = rec.get("umbrella_chapters", [])
    filtering = bool(source_filter or label_filter)
    if source_filter:
        chapters = [c for c in chapters if c.get("source") == source_filter]

    if label_filter:
        # Keep only genuinely cross-cutting chapters (any source). The old
        # find_umbrella_chapters LLM over-included profession-specific chapters
        # (Medical Practice, University of Arkansas) — pulling those pollutes
        # umbrella_text and cross-contaminates every profession's extraction.
        #
        # Selection = regex OR manifest-blessed OR already-cached-with-text
        # MINUS manifest-dropped (authoritative, wins over everything).
        # We must read the cache BEFORE filtering so cached_slugs is available.

        # Read existing cache first (needed for grandfather logic in select)
        existing_record_pre: dict | None = None
        existing_sections_pre: list[dict] = []
        if out_path.exists():
            existing_record_pre = json.loads(out_path.read_text())
            existing_sections_pre = existing_record_pre.get("sections") or []
        cached_slugs_pre = {s.get("umbrella_chapter_slug", "")
                            for s in existing_sections_pre if s.get("text")}

        # Load manifest for blessed/dropped sets
        from pipeline.discover._state_scope_manifest import load_manifest
        manifest = load_manifest(state)
        manifest_blessed = (manifest.universal_chapters
                            | set(manifest.chapter_applies_to.keys()))
        manifest_dropped = manifest.drop_chapters

        chapters, drop_log = select_umbrella_chapters(
            chapters, cached_slugs_pre, manifest_blessed, manifest_dropped,
        )
        for slug, label, reason in drop_log:
            log.info("[%s] drop %s (%s): %s", state, slug, reason, label[:60])

    if not chapters:
        # A FILTER yielding nothing means "nothing to do here" — never wipe an
        # existing cache (that was the --force bug). Only write empty when the state
        # genuinely declares no umbrella chapters at all.
        log.info("[%s] no umbrella chapters%s", state, " after filter" if filtering else " declared")
        if filtering:
            return None
        out_path.write_text(json.dumps({"state": state, "sections": []}, indent=2))
        return None

    # Auto-healing: when umbrella_text already exists, fetch only chapters
    # that are declared in umbrella_chapters but missing from the cache
    # (zero sections). Lets us recover from per-chapter Justia timeouts
    # without --force (which would re-fetch already-cached chapters and,
    # if Justia is in another flaky window, risk wiping good data).
    existing_record: dict | None = None
    existing_sections: list[dict] = []
    if out_path.exists():
        existing_record = json.loads(out_path.read_text())
        existing_sections = existing_record.get("sections") or []

    cached_slugs = {s.get("umbrella_chapter_slug", "")
                    for s in existing_sections if s.get("text")}
    declared_slugs = {c.get("slug", "") for c in chapters}
    missing_slugs = declared_slugs - cached_slugs

    if force:
        # Full re-pull: ignore everything in cache.
        chapters_to_pull = chapters
        kept_sections: list[dict] = []
    elif not missing_slugs:
        log.info("[%s] all %d chapter(s) cached, skip", state, len(chapters))
        return existing_record
    else:
        chapters_to_pull = [c for c in chapters if c.get("slug") in missing_slugs]
        # Preserve sections for chapters we're NOT re-pulling.
        kept_sections = [s for s in existing_sections
                         if s.get("umbrella_chapter_slug") in cached_slugs]
        log.info(
            "[%s] retrying %d/%d chapter(s) missing from cache: %s",
            state, len(chapters_to_pull), len(chapters), sorted(missing_slugs),
        )

    new_sections: list[dict] = []
    for ch in chapters_to_pull:
        url = ch["url"]
        label = ch.get("label", "")
        slug = ch.get("slug", "")
        log.info("[%s] umbrella chapter %s — %s", state, slug, label[:60])

        if is_section_url(url):
            section_targets = [{"url": url, "label": label, "slug": slug}]
        else:
            section_targets, err = collect_section_targets(url, label, slug, depth=0)
            if err:
                log.warning("  collect_section_targets error: %s", err)

        if len(section_targets) > 100:
            # Not a cap — just make scale unmissable so the operator can judge
            # whether this chapter is really umbrella law before an hours-long walk.
            log.warning("  LARGE chapter: %d section targets for %s (%s) — pulling ALL of them",
                        len(section_targets), slug, label[:60])
        log.info("  -> %d section targets", len(section_targets))
        for target in section_targets:
            sec_url = target["url"]
            status, html, err = fetch(sec_url)
            time.sleep(PER_HOST_DELAY)
            if err or not html or (status and not 200 <= status < 300):
                log.warning("    %s: %s", sec_url, err or f"http {status}")
                continue
            text = extract_section_text(html)
            if not text:
                continue
            new_sections.append({
                "url": sec_url,
                "label": target.get("label", ""),
                "slug": target.get("slug", ""),
                "umbrella_chapter_slug": slug,
                "umbrella_chapter_label": label,
                "text": text,
                "text_len": len(text),
            })

    all_sections = kept_sections + new_sections
    log.info(
        "[%s] -> %d total umbrella sections (%d cached + %d newly fetched)",
        state, len(all_sections), len(kept_sections), len(new_sections),
    )

    # Cache-write guard: don't replace a populated cache with an empty
    # result. That's almost always a transient upstream failure (Justia
    # rate-limiting / timeouts) rather than a real "this state has no
    # umbrella text" signal. Without this guard, a --force re-run during
    # a flaky window silently wipes the good data. If the caller really
    # wants the empty record, delete the file by hand.
    if not all_sections and existing_sections:
        log.warning(
            "[%s] fetched 0 sections but %d cached — keeping cache, not overwriting",
            state, len(existing_sections),
        )
        return existing_record

    record: dict = {
        "state": state,
        "umbrella_chapter_count": len(chapters),
        "sections": all_sections,
    }
    out_path.write_text(json.dumps(record, indent=2))
    return record


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="")
    ap.add_argument("--states", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--source", default="",
                    help="pull ONLY umbrella chapters with this source tag (e.g. citation_audit).")
    ap.add_argument("--label-filter", action="store_true",
                    help="pull ONLY chapters with a cross-cutting umbrella label (any source) — "
                         "excludes the old find_umbrella_chapters profession-specific over-picks. "
                         "Use with --force to rebuild umbrella_text clean.")
    args = ap.parse_args()

    if args.state:
        targets = [args.state.upper()]
    elif args.states:
        targets = [s.strip().upper() for s in args.states.split(",") if s.strip()]
    else:
        targets = list(ALL_STATES)

    log.info("pulling umbrella text for %d states%s%s", len(targets),
             f" (source={args.source})" if args.source else "",
             " (label-filter)" if args.label_filter else "")
    for st in targets:
        try:
            pull_state_umbrella(st, args.force, args.source or None, args.label_filter)
        except Exception:
            log.exception("[%s] crashed", st)


if __name__ == "__main__":
    main()
