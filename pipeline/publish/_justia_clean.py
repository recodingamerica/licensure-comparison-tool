"""Strip Justia navigation chrome from scraped section text.

Justia section pages are laid out as
    [version-history navigation]
    [breadcrumb of Title / Article / Section]
    [citation info + AALL universal-citation explainer]
    Next
    [actual section content]
    Next
    Disclaimer: [boilerplate]
    [page-footer notes]

The umbrella scraper currently keeps the whole soup. Per-profession
trimmed sections go through a different pipeline that already strips
this. This module gives the publish step a deterministic way to remove
the chrome from any text that still has it — both for the existing
umbrella_text data (so we don't have to re-scrape) and as a defense in
depth for future ingest.
"""

from __future__ import annotations

import re


# Lines that mark the boundaries of the actual content. "Next" alone on a
# line is Justia's "next section" pagination control — it appears
# immediately before AND after the body. "Disclaimer" / "Justia Free
# Databases" / footer-style lines reliably mark the end.
_BODY_START_MARKERS = (
    "Next",
    "Universal Citation:",  # If "Next" missing, fall back to citation header
)

_BODY_END_MARKERS = (
    "Next",
    "Disclaimer",
    "These codes may not be the most recent version.",
    "Justia Free Databases",
)


# Pre-body lines that are always chrome — used as a sanity check.
_CHROME_PREFIXES = (
    "Go to Previous Versions",
    "of",
    "this Section",
    "View All Versions",
    "Universal Citation:",
    "Learn more",
    "This media-neutral citation is based",
)


def clean_justia_text(text: str) -> str:
    """Return the section's content with Justia chrome removed.

    Heuristic: split on lines, walk down until we pass the citation block
    (marked by a "Learn more" + media-neutral note + the FIRST "Next"
    line). Everything until the NEXT "Next" / "Disclaimer" is content.

    Falls back to the original text if we can't find the markers — better
    to ship chrome than to ship nothing.
    """
    if not text:
        return text

    lines = text.splitlines()
    # Normalize whitespace on each line so "Next " or "    Next" still match.
    stripped = [ln.strip() for ln in lines]

    # Find the index of the first standalone "Next" line — that marks the
    # start of the actual body.
    first_next: int | None = None
    for i, ln in enumerate(stripped):
        if ln == "Next":
            first_next = i
            break

    if first_next is None:
        # No "Next" marker — try a fallback that looks for "Learn more" and
        # the media-neutral note, then takes everything after.
        for i, ln in enumerate(stripped):
            if ln.startswith("This media-neutral citation is based"):
                # Skip ahead to after the wrapped continuation lines.
                j = i + 1
                while j < len(stripped) and stripped[j] and not stripped[j].endswith("."):
                    j += 1
                first_next = j  # body starts here
                break

    if first_next is None:
        # Still no signal — return original.
        return text

    # Find the END marker: another "Next" OR a "Disclaimer" line.
    body_end: int | None = None
    for i in range(first_next + 1, len(stripped)):
        if stripped[i] in _BODY_END_MARKERS or stripped[i].startswith("Disclaimer"):
            body_end = i
            break

    if body_end is None:
        body_end = len(stripped)

    body_lines = lines[first_next + 1 : body_end]

    # Drop empty leading/trailing lines.
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()

    # Collapse multiple consecutive blank lines into single blanks, and
    # normalize indentation — Justia sometimes ships its HTML with deeply
    # indented continuation lines we don't want preserved as visual breaks.
    out_lines: list[str] = []
    prev_blank = False
    for ln in body_lines:
        s = ln.strip()
        if not s:
            if not prev_blank and out_lines:
                out_lines.append("")
                prev_blank = True
            continue
        out_lines.append(s)
        prev_blank = False

    cleaned = "\n".join(out_lines)
    # If the cleaning left us with almost nothing, prefer the original.
    if len(cleaned) < 30 and len(text) > 60:
        return text
    return cleaned
