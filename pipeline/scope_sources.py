"""Canonical meaning of umbrella `scope_source` values.

`assign_umbrella_scope.py` tags each umbrella section with a `scope_source`:

  universal / anchor_universal      → applies to ALL licensed professions
  anchor_enumeration / inherited_enumeration
                                    → applies to a specific enumerated set
                                      (the section's `applies_to_professions`)
  undetermined (or unset)           → the walker couldn't scope it; skip

Several places consume these values (the web build, the DB load, the coverage
matrix, the scope-rule generator). This module is the single source of truth
for what the values mean, so none of them re-encode the tuples or the
"who does this apply to" rule.
"""

from __future__ import annotations

# Section applies to every licensed profession in the state.
UNIVERSAL_SOURCES = ("universal", "anchor_universal")
# Section applies to a specific enumerated set (see `applies_to_professions`).
ENUMERATION_SOURCES = ("anchor_enumeration", "inherited_enumeration")
# Anything the walker could confidently scope (vs. "undetermined" / unset).
CLASSIFIED_SOURCES = UNIVERSAL_SOURCES + ENUMERATION_SOURCES


def is_universal(scope_source: str | None) -> bool:
    return scope_source in UNIVERSAL_SOURCES


def is_enumeration(scope_source: str | None) -> bool:
    return scope_source in ENUMERATION_SOURCES


def is_classified(scope_source: str | None) -> bool:
    return scope_source in CLASSIFIED_SOURCES


def professions_for(
    scope_source: str | None,
    applies_to_professions,
    all_professions,
) -> list | None:
    """Which professions an umbrella section applies to.

      universal      → every profession (`all_professions`)
      enumeration    → the explicit list (`applies_to_professions`, may be empty)
      undetermined/unset → None  (caller should skip the section)

    Returning None (rather than []) lets callers distinguish "applies to no one
    we could determine" from "explicitly an empty enumeration".
    """
    if is_universal(scope_source):
        return list(all_professions)
    if is_enumeration(scope_source):
        return list(applies_to_professions or [])
    return None
