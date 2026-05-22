"""Build hierarchy trees from Justia section URLs.

Both the per-profession browse view (build_frontend.py) and the per-state
browse view (build_state_browse.py) need to organize sections by the
statute's own hierarchy — title → chapter/article → part → section —
not as a flat list.

This module parses Justia URLs (which encode the hierarchy in their path)
and returns a nested tree structure the frontend can render as
collapsible nodes.

Examples of URLs we handle:
  https://law.justia.com/codes/colorado/title-12/article-290/part-1/section-12-290-101/
    → title-12 / article-290 / part-1 / section-12-290-101
  https://law.justia.com/codes/utah/title-58/chapter-1/section-58-1-101/
    → title-58 / chapter-1 / section-58-1-101
  https://law.justia.com/codes/arizona/title-32/chapter-19/section-32-851/
    → title-32 / chapter-19 / section-32-851

Some sections sit directly under a title (no chapter/article), which is
why each intermediate level is optional in the model.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

# Path segments that look like hierarchy nodes. We recognize the standard
# four kinds; anything else (e.g. "general", "2024" for year-prefixed URLs)
# is skipped.
_LEVEL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("title",   re.compile(r"^title-")),
    ("chapter", re.compile(r"^chapter-")),
    ("article", re.compile(r"^article-")),
    ("part",    re.compile(r"^part-")),
    ("section", re.compile(r"^section-")),
]

# Slug → display label. We humanize the slug ("article-290" → "Article 290").
def _humanize_slug(slug: str) -> str:
    parts = slug.split("-", 1)
    if len(parts) != 2:
        return slug
    kind, num = parts
    return f"{kind.capitalize()} {num}"


def _classify_segment(seg: str) -> tuple[str, str] | None:
    """Returns (level, normalized_slug) or None if segment isn't a hierarchy node."""
    for level, pat in _LEVEL_PATTERNS:
        if pat.match(seg):
            return level, seg
    return None


def parse_hierarchy(url: str) -> list[tuple[str, str]]:
    """Walks a Justia section URL and returns the hierarchy path as
    [(level, slug), ...] from top to bottom — e.g.

      title-12 article-290 part-1 section-12-290-101

    For URLs that lack intermediate levels the list is correspondingly
    short. URLs we can't parse return an empty list."""
    if not url:
        return []
    path = urlparse(url).path.rstrip("/")
    if not path:
        return []
    segments = [s for s in path.split("/") if s]
    out: list[tuple[str, str]] = []
    for seg in segments:
        c = _classify_segment(seg)
        if c is not None:
            out.append(c)
    return out


def _new_branch(level: str, slug: str, label: str | None) -> dict[str, Any]:
    return {
        "slug": slug,
        "level": level,
        "label": label or _humanize_slug(slug),
        "url": None,
        "children": [],
    }


def build_tree(
    sections: list[dict],
    *,
    chapter_label_overrides: dict[str, str] | None = None,
) -> list[dict]:
    """Given a list of sections (each must have at least `url`), return
    the top-level forest. Sections without parseable URLs are appended
    at the root as orphan leaves so we don't silently drop them.

    `chapter_label_overrides` lets the caller pass in known human labels
    (e.g. "Article 1 - GENERAL PROVISIONS" from umbrella_chapter_label
    on umbrella sections), keyed by chapter slug — they replace the
    slug-derived label on the matching branch.
    """
    overrides = chapter_label_overrides or {}
    root_branches: dict[str, dict[str, Any]] = {}
    # Dedup by the *parsed* hierarchy path (e.g. title-12/article-290/
    # part-1/section-12-290-101). Same section is sometimes scraped from
    # multiple year-prefixed Justia URLs — different URLs, same statute.
    # Keying off the parsed path collapses them.
    seen_paths: set[str] = set()

    for sec in sections:
        url = sec.get("url") or ""
        path = parse_hierarchy(url)
        dedup_key = "/".join(s for _, s in path) if path else (
            (sec.get("citation") or "") + "|" + (sec.get("label") or "")
        )
        if dedup_key in seen_paths:
            continue
        seen_paths.add(dedup_key)
        if not path:
            # Orphan — attach at root as a bare leaf so it stays visible.
            slug = (sec.get("citation") or sec.get("label") or url)[:60] or "orphan"
            root_branches.setdefault("_orphans", _new_branch("title", "_orphans", "(unstructured)"))
            root_branches["_orphans"]["children"].append({
                "slug": slug,
                "level": "section",
                "label": sec.get("citation") or sec.get("label") or "(no citation)",
                "url": url or None,
                "section": sec,
                "children": [],
            })
            continue

        # Walk the hierarchy, getting-or-creating each branch.
        if path[-1][0] != "section":
            # No section-level slug in the URL — the section itself doesn't
            # have a leaf identifier we recognize. Append as a leaf under
            # the deepest branch we have.
            section_slug = (sec.get("citation") or url)[:60]
            path = path + [("section", section_slug)]

        # First-level branch — title (or whatever the top-most parsed level is)
        top_level, top_slug = path[0]
        if top_slug not in root_branches:
            root_branches[top_slug] = _new_branch(
                top_level, top_slug, overrides.get(top_slug),
            )
        cur = root_branches[top_slug]

        # Intermediate branches: chapter / article / part
        for level, slug in path[1:-1]:
            child = next((c for c in cur["children"] if c["slug"] == slug), None)
            if child is None:
                child = _new_branch(level, slug, overrides.get(slug))
                cur["children"].append(child)
            cur = child

        # Leaf — the section itself
        leaf_level, leaf_slug = path[-1]
        cur["children"].append({
            "slug": leaf_slug,
            "level": leaf_level,
            "label": sec.get("citation") or sec.get("label") or _humanize_slug(leaf_slug),
            "url": url or None,
            "section": sec,
            "children": [],
        })

    # Sort children at every level by slug — gives a stable, intuitive order
    # (numeric sort would be nicer but slugs like "section-12-290-101" sort
    # correctly lexicographically within a chapter).
    def _sort(node: dict[str, Any]) -> None:
        node["children"].sort(key=lambda c: c["slug"])
        for child in node["children"]:
            _sort(child)

    forest = sorted(root_branches.values(), key=lambda b: b["slug"])
    for top in forest:
        _sort(top)
    return forest
