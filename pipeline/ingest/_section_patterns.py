"""Shared URL-segment regexes, in a dependency-free module.

`SECTION_SEG` matches a Justia URL path segment that names a leaf STATUTE SECTION
(vs a container like a title/chapter). It's needed both by the scraping stack
(pull_text, which walks Justia) and by the LLM-free scope walker (discover._scope_rules).
Keeping it here — importing only `re` — lets both import the SAME pattern without the
scope walker dragging in the scraping deps (curl_cffi/bs4) that `pull_text` pulls in.
Previously each kept a hand-copied duplicate that could silently drift.
"""

from __future__ import annotations

import re

SECTION_SEG = re.compile(
    r"^(section[-_]|§|s[-_]\d|statute[-_]|rs[-_]|\d+[a-z]?[-_:.]\d|\d{3,}\b)",
    re.IGNORECASE,
)
