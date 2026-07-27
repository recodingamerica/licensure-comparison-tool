"""The priority licensure concepts — defined ONCE, for every surface that shows them.

This list previously existed twice: PRIORITY_FIELDS here (the tag sheet) and
PRIORITY_CONCEPTS in web/src/components/map-view.tsx (the choropleth dropdown), with a
comment on the TypeScript side saying it "mirrors" the Python one. A comment is not a
mechanism, and they had already drifted four ways by 2026-07-27:

  * TypeScript had three concepts Python didn't: Regulation (UORF), School Approval
    Basis, Experience Requirement.
  * TypeScript's "Minimum Degree" preferred the normalized `degree_level` enum; Python
    only knew the older bucketed `degree_required`.
  * Python had Discipline, deliberately excluded from the map (it's per-item — a state
    has many grounds spanning several buckets, so it isn't a single-value choropleth).

Nothing detected any of that, because each side independently "worked".

Now Python owns it and build_frontend ships it in the payload for the frontend to read —
the same arrangement as config/web_colors.yaml, where one definition is generated into
the code that consumes it. To add a concept, add it here; both surfaces follow.

Flags, rather than two lists (two lists is how this started):
  choropleth  — appears in the map's field dropdown
  tag_sheet   — appears in the generated tag sheet
"""

from __future__ import annotations

PRIORITY_CONCEPTS: list[dict] = [
    {
        "concept": "Regulation (UORF)",
        "source": "scalar",
        "candidates": ["licensure.regulatory_model"],
        # A normalized enum, not a Pass-3 text bucket, so it has nothing to contribute
        # to the tag sheet — but it's the headline concept on the map.
        "choropleth": True,
        "tag_sheet": False,
    },
    {
        "concept": "Minimum Degree",
        "source": "scalar",
        # Prefer the normalized degree_level enum (#35); fall back to the older bucketed
        # free-text field until a re-extract populates the enum.
        "candidates": [
            "licensure.education.degree_level",
            "licensure.education.degree_required",
        ],
        "choropleth": True,
        "tag_sheet": True,
    },
    {
        "concept": "School Approval Basis",
        "source": "scalar",
        "candidates": ["licensure.education.school_approval_basis"],
        "choropleth": True,
        "tag_sheet": False,
    },
    {
        "concept": "Experience Requirement",
        "source": "scalar",
        "candidates": ["licensure.post_degree_experience.experience_source"],
        "choropleth": True,
        "tag_sheet": False,
    },
    {
        "concept": "Professional Experience",
        "source": "scalar",
        "candidates": [
            "licensure.post_degree_experience.kind",
            "licensure.post_degree_experience.duration",
        ],
        "choropleth": True,
        "tag_sheet": True,
    },
    {
        "concept": "Licensing Authority",
        "source": "scalar",
        "candidates": [
            "licensure.issuing_authority",
            "licensure.regulatory_authority.name",
        ],
        "choropleth": True,
        "tag_sheet": True,
    },
    {
        "concept": "Scope of Practice",
        "source": "scalar",
        # Scope wording is profession-specific: surgical professions bucket
        # `scope.methods_authorized`/`drug_authority`, optometry buckets
        # `profession_specific.surgery_definition`, etc. Include whatever exists.
        "candidates": [
            "scope.methods_authorized",
            "scope.drug_authority",
            "scope.definition_quote",
            "profession_specific.surgery_definition",
        ],
        "choropleth": True,
        "tag_sheet": True,
    },
    {
        "concept": "Discipline",
        "source": "per_item",
        "candidates": ["licensure.disciplinary_grounds"],
        # Per-item: a state has many grounds spanning several buckets, so there is no
        # single value to colour a state by. It lives on the tag sheet and the table's
        # category column instead.
        "choropleth": False,
        "tag_sheet": True,
    },
]


def for_tag_sheet() -> list[dict]:
    """Concepts the generated tag sheet covers."""
    return [c for c in PRIORITY_CONCEPTS if c.get("tag_sheet", True)]


def for_choropleth() -> list[dict]:
    """Concepts the map's field dropdown offers, in display order.

    Shipped into each profession payload by build_frontend so the frontend reads this
    list instead of restating it.
    """
    return [
        {"concept": c["concept"], "candidates": list(c["candidates"])}
        for c in PRIORITY_CONCEPTS
        if c.get("choropleth", True)
    ]
