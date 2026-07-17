"""Shared Justia URL-segment regexes, in a dependency-free module.

These classify a Justia URL path segment by granularity — leaf SECTION vs drill-able
INTERMEDIATE vs bare CONTAINER landing page. They're needed across the scraping stack
(pull_text), the LLM-free scope/hierarchy walkers (discover._scope_rules, discover._extract),
and the mapping auditor (eval.audit_mappings). Keeping them here — importing only `re` —
lets every consumer import the SAME pattern without dragging in the scraping deps
(curl_cffi/bs4) that pull_text pulls in. Each was previously a hand-copied duplicate that
silently drifted (see the #69 dedup and its miss in discover._extract).
"""

from __future__ import annotations

import re

# Last path segment names a leaf STATUTE SECTION (not a container).
SECTION_SEG = re.compile(
    r"^(section[-_]|§|s[-_]\d|statute[-_]|rs[-_]|\d+[a-z]?[-_:.]\d|\d{3,}\b)",
    re.IGNORECASE,
)

# An intermediate container we want to DRILL INTO (subchapter/part/article/…) to reach
# its sections — has a token after the type (`subchapter-2`), unlike a bare landing page.
INTERMEDIATE_SEG = re.compile(
    r"^(subchapter|subpart|part|division|subdivision|chapter|subtitle|article)[-_][0-9a-z]",
    re.IGNORECASE,
)

# Last path segment is a bare CONTAINER landing page (title-/chapter-/article-/…), not a
# leaf. Deliberately NARROWER than SECTION_SEG's inverse: it must NOT flag real sections
# nested under IL `act-225-ilcs-80` / ND `chapter-43-36` act structures, so it only
# catches genuine container-pages-mistaken-for-sections (e.g. land_surveying/WY's lone
# `.../chapter-29/`). Match against a url's LAST segment via `container_segment(url)`.
CONTAINER_SEG = re.compile(r"^(title|chapter|article|part|subchapter|division)\b", re.I)


def container_segment(url: str) -> bool:
    """True if `url`'s last path segment is a bare container landing page (CONTAINER_SEG)."""
    import urllib.parse
    segs = [s for s in urllib.parse.urlparse(url or "").path.split("/") if s]
    return bool(segs) and bool(CONTAINER_SEG.match(segs[-1]))
