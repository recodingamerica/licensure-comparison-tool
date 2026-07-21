"""Evidence-tree walkers — schema-independent helpers split out of
`standard_model.py` so the many consumers that only need to *walk* an extracted
record (the verifier, span annotator, review-CSV builder, map_prep bucketer, DB
loader, repair script) don't have to import the 700-line Pydantic schema.

These functions know only the Evidence-carrier shape (`{value, quote, citation}`);
they have zero dependency on the schema classes, so importing this module is cheap
and never drags in pydantic. `standard_model` re-exports these names for
back-compat, so `from ...standard_model import iter_evidence` keeps working.
"""

from __future__ import annotations

from typing import Any, Iterator


_EVIDENCE_KEYS = frozenset({"value", "quote", "citation"})


def is_evidence_node(node: Any) -> bool:
    """True iff `node` is a dict with the Evidence-carrier shape."""
    return isinstance(node, dict) and _EVIDENCE_KEYS.issubset(node.keys())


def deep_get(node: Any, *path: str) -> Any:
    """Descend `node` by the given keys, returning None if any segment is missing or
    not a dict. The shared core of the several record-walkers (_g / _ev_at /
    _resolve_evidence) that each re-implemented this loop with a different wrapper."""
    cur = node
    for seg in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(seg)
    return cur


def iter_evidence(
    node: Any, path: tuple[str | int, ...] = ()
) -> Iterator[tuple[tuple[str | int, ...], dict]]:
    """Yield (path, evidence_dict) for every Evidence-shaped node in a tree.

    `path` is a tuple of keys/indices from the root to the node, so callers
    that need to know "which field is this Evidence carrying" can read it
    directly. Single point of truth for what counts as an Evidence node —
    the verifier, span annotator, review CSV builder, and repair script all
    walk the same way.
    """
    if isinstance(node, dict):
        if is_evidence_node(node):
            yield path, node
            return
        for k, v in node.items():
            yield from iter_evidence(v, path + (k,))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_evidence(v, path + (i,))
