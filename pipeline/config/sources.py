"""Source registry: maps a URL host to a content-cleaner function.

Add an entry here when a new statute source is added. The cleaner function
takes raw text (already extracted from HTML) and returns cleaned text — it
should NOT remove substantive content, only chrome / nav / disclaimers.

Used by pipeline/ingest/clean_text.py.
"""

from __future__ import annotations

from typing import Callable

# Cleaners are registered as plain functions; the cleaning module imports them.
SOURCE_HOSTS = {
    "law.justia.com": "clean_justia",
    # Add: "leginfo.legislature.ca.gov": "clean_ca_leginfo", etc.
}
