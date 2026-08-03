"""One definition of "absolutize a Justia url".

The hierarchy files and some mapping_overrides entries carry root-relative paths
("/codes/massachusetts/..."), everything else carries absolute ones. Emitting
whichever form the source happened to hold made a plain re-run of match_profession
rewrite unrelated cells, which reads as a real mapping change in review
(2026-08-03). pull_text absolutizes at fetch time regardless, so this only ever
affected the stored index — but a generated file that churns on a no-op rebuild
hides the changes you actually made.
"""

from __future__ import annotations

JUSTIA_ROOT = "https://law.justia.com"


def _abs_url(u: str) -> str:
    u = (u or "").strip()
    return JUSTIA_ROOT + u if u.startswith("/") else u
