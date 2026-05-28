"""Per-state umbrella scope manifests.

Each state can have an optional yaml at ``pipeline/config/state_scope/<ST>.yaml``
that hardcodes facts the regex walker and LLM Pass 3 can't reliably infer
from section text alone:

  umbrella_chapters_drop:
    - chapter-77    # Kansas administrative procedure act, not licensing
  chapter_universal:
    - chapter-1     # explicit "applies to every licensed profession in state"
  chapter_applies_to:
    chapter-23-74:  # RI: applies to a defined sub-cohort
      professions: [nursing, medicine, dentistry, ...]
      note: "Unlicensed Health Care Practices — health professions only"

**Semantics: authoritative.** Manifest decisions override the walker and Pass 3
for the chapters they cover. States without a manifest file behave exactly
as before (zero risk for the 22 pinned-golden-test states and the 8 fully-
classified states).

Why this exists: the upstream `find_umbrella_chapters.py` sometimes pulls in
chapters that aren't licensing umbrella (KS-style noise); other chapters
ARE umbrella but no single section text enumerates the regulated set
(CA's Department of Consumer Affairs chapters apply to ~40 boards but no
section lists them). Both cases need explicit per-state knowledge. See
the user feedback memory feedback_state_scope_manifests.md for the
strategic context.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

MANIFEST_DIR = Path(__file__).resolve().parent.parent / "config" / "state_scope"

log = logging.getLogger("state_scope_manifest")


@dataclass(frozen=True)
class StateScopeManifest:
    """Parsed manifest for one state. Empty when no file exists."""
    drop_chapters: frozenset[str] = field(default_factory=frozenset)
    universal_chapters: frozenset[str] = field(default_factory=frozenset)
    # chapter_slug -> tuple[profession_id, ...]
    chapter_applies_to: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def is_empty(self) -> bool:
        return not self.drop_chapters and not self.universal_chapters and not self.chapter_applies_to


_EMPTY = StateScopeManifest()


@lru_cache(maxsize=None)
def load_manifest(state: str) -> StateScopeManifest:
    """Read pipeline/config/state_scope/<STATE>.yaml. Missing file → empty
    manifest (caller sees the same behavior as before this module existed)."""
    path = MANIFEST_DIR / f"{state}.yaml"
    if not path.exists():
        return _EMPTY
    try:
        raw = yaml.safe_load(path.read_text()) or {}
    except yaml.YAMLError as e:
        log.error("[%s] manifest YAML parse error in %s: %s", state, path, e)
        return _EMPTY

    drop = frozenset(raw.get("umbrella_chapters_drop") or [])
    universal = frozenset(raw.get("chapter_universal") or [])
    applies_to_raw = raw.get("chapter_applies_to") or {}
    applies_to: dict[str, tuple[str, ...]] = {}
    for chap, spec in applies_to_raw.items():
        if isinstance(spec, dict):
            profs = spec.get("professions") or []
        elif isinstance(spec, list):
            profs = spec
        else:
            log.warning("[%s] chapter_applies_to[%s] has unexpected shape %r — skipped",
                        state, chap, type(spec).__name__)
            continue
        applies_to[chap] = tuple(profs)

    overlap = drop & (universal | applies_to_raw.keys())
    if overlap:
        log.warning(
            "[%s] manifest contradiction — chapters listed in BOTH drop and a scope rule: %s. "
            "Drop wins (these chapters will be excluded from the corpus).",
            state, sorted(overlap),
        )

    m = StateScopeManifest(
        drop_chapters=drop,
        universal_chapters=universal - drop,
        chapter_applies_to={c: p for c, p in applies_to.items() if c not in drop},
    )
    if not m.is_empty():
        log.info(
            "[%s] manifest loaded: %d dropped, %d universal, %d enumerated",
            state, len(m.drop_chapters), len(m.universal_chapters), len(m.chapter_applies_to),
        )
    return m


def manifest_decision_for(
    manifest: StateScopeManifest, chap: str,
) -> dict | None:
    """Manifest's authoritative decision for a chapter, or None if the
    manifest doesn't cover it. Caller applies it to every section in the
    chapter (skipping the regex walker for that chapter)."""
    if chap in manifest.universal_chapters:
        return {"kind": "universal"}
    if chap in manifest.chapter_applies_to:
        return {"kind": "enumerated", "professions": list(manifest.chapter_applies_to[chap])}
    return None
