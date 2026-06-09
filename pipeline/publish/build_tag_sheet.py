"""Tag sheet: the "rough tagging" for each profession's key licensure fields.

Pass 3 (`pipeline.map_prep.bucket_text`) already clusters each profession's
messy free-text field values into ~4-9 plain-English tags and assigns every
state to a tag. That output lives in
`results/map_prep/<profession>/text_buckets.json` (scalar fields) and
`text_buckets_per_item.json` (list-of-objects fields like disciplinary_grounds).

This script does NOT re-run any LLM. It reads those existing bucket files and
reshapes them into a single, readable artifact organized around the five
fields we care about most:

  Minimum Degree · Professional Experience · Licensing Authority ·
  Scope of Practice · Discipline

Each field can map to more than one underlying bucketed dotted-field (e.g.
licensing authority lives in both `issuing_authority` and
`regulatory_authority.name`; scope wording is profession-specific). We include
every candidate that the bucket pass actually produced for that profession, so
the sheet stays honest about what exists rather than inventing structure.

Output (mirrors the scorecard publisher):
  - publish/web/public/data/tag_sheet.json   (machine-readable, web route)
  - results/tag_sheet.md                      (repo-tracked markdown snapshot)

Usage:
  python -m pipeline.publish.build_tag_sheet
  python -m pipeline.publish.build_tag_sheet --professions optometry podiatry
  python -m pipeline.publish.build_tag_sheet --upload
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import MAP_PREP_DIR, RESULTS_DIR, WEB_PUBLIC_DIR  # noqa: E402

# The five priority fields, each mapped to the dotted bucketed-field names that
# carry it. `source` says which bucket file to read:
#   "scalar"   -> text_buckets.json          (one tag per state)
#   "per_item" -> text_buckets_per_item.json (one tag per list item)
# Candidates are tried in order; every candidate that the profession's bucket
# pass produced is included (not just the first match).
PRIORITY_FIELDS: list[dict] = [
    {
        "concept": "Minimum Degree",
        "source": "scalar",
        "candidates": ["licensure.education.degree_required"],
    },
    {
        "concept": "Professional Experience",
        "source": "scalar",
        "candidates": [
            "licensure.post_degree_experience.kind",
            "licensure.post_degree_experience.duration",
        ],
    },
    {
        "concept": "Licensing Authority",
        "source": "scalar",
        "candidates": [
            "licensure.issuing_authority",
            "licensure.regulatory_authority.name",
        ],
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
    },
    {
        "concept": "Discipline",
        "source": "per_item",
        "candidates": ["licensure.disciplinary_grounds"],
    },
]


def _load_buckets(profession: str) -> tuple[dict, dict]:
    """Return (scalar_by_field, per_item_by_field) for a profession, keyed by
    dotted field name. Missing files -> empty dicts (profession may not have a
    Pass-3 bucket run yet)."""
    pdir = MAP_PREP_DIR / profession
    scalar: dict[str, dict] = {}
    per_item: dict[str, dict] = {}

    scalar_path = pdir / "text_buckets.json"
    if scalar_path.exists():
        for entry in json.loads(scalar_path.read_text()).get("fields", []):
            scalar[entry["field_name"]] = entry

    per_item_path = pdir / "text_buckets_per_item.json"
    if per_item_path.exists():
        fields = json.loads(per_item_path.read_text()).get("fields", {})
        # per-item file stores fields as a dict keyed by field name.
        if isinstance(fields, dict):
            per_item.update(fields)
        else:  # tolerate a list form too
            for entry in fields:
                per_item[entry["field_name"]] = entry

    return scalar, per_item


def _scalar_subfield(entry: dict) -> dict:
    """Reshape a scalar text_buckets entry: tag -> state count, plus the raw
    state->tag assignments WITH the original value text (`text`) so the web
    side can show, per tag, which states fall under it and what they actually
    say."""
    assignments = [
        {"state": a["state"], "bucket": a["bucket"], "text": a.get("raw_value", "")}
        for a in entry.get("assignments", [])
        if a.get("bucket")
    ]
    counts: dict[str, int] = {}
    for a in assignments:
        counts[a["bucket"]] = counts.get(a["bucket"], 0) + 1
    tags = [
        {"label": b, "count": counts.get(b, 0)}
        for b in entry.get("bucket_set", [])
    ]
    return {
        "field_name": entry["field_name"],
        "kind": "scalar",
        "unit": "states",
        "rationale": entry.get("rationale", ""),
        "tags": tags,
        "assignments": assignments,
    }


def _per_item_subfield(entry: dict) -> dict:
    """Reshape a per-item entry: tag -> item count, plus how many distinct
    states have at least one item in each tag. No single state->tag mapping
    exists here (a state has many disciplinary grounds), so assignments are
    left empty and the web side renders the tag frequencies."""
    item_counts: dict[str, int] = {}
    state_sets: dict[str, set] = {}
    assignments = []
    for a in entry.get("assignments", []):
        b = a.get("bucket")
        if not b:
            continue
        item_counts[b] = item_counts.get(b, 0) + 1
        state_sets.setdefault(b, set()).add(a["state"])
        # `text` = the per-item label so hover can show each ground under a tag.
        assignments.append(
            {"state": a["state"], "bucket": b, "text": a.get("item_label", "")}
        )
    tags = [
        {
            "label": b,
            "count": item_counts.get(b, 0),
            "states": len(state_sets.get(b, ())),
        }
        for b in entry.get("bucket_set", [])
    ]
    return {
        "field_name": entry["field_name"],
        "kind": "per_item",
        "unit": "grounds",
        "rationale": entry.get("rationale", ""),
        "tags": tags,
        "assignments": assignments,
    }


_NAMESPACE_PREFIXES = ("licensure.", "scope.", "profession_specific.")

# Evidence-wrapper internals that a stale/older bucket run may have split out
# as if they were real fields (e.g. `issuing_authority.value`,
# `is_mandatory.approximate.ratio`). They are plumbing, never real fields — skip
# them so the sheet stays clean even when a profession's bucket file predates
# the run.py flatten fix.
_EVIDENCE_INTERNAL_SUFFIXES = (
    ".value", ".quote", ".citation", ".unverified",
    ".approximate.ratio", ".approximate.matched_normalized",
)


def _is_evidence_internal(dotted: str) -> bool:
    return any(dotted.endswith(s) for s in _EVIDENCE_INTERNAL_SUFFIXES)


def _humanize(dotted: str) -> str:
    """Readable label for a dotted field name, dropping the top-level
    namespace: 'profession_specific.controlled_substance_schedule_restrictions'
    -> 'Controlled substance schedule restrictions'."""
    name = dotted
    for pre in _NAMESPACE_PREFIXES:
        if name.startswith(pre):
            name = name[len(pre):]
            break
    words = name.replace(".", " ").replace("_", " ").strip()
    return words[:1].upper() + words[1:] if words else dotted


def build_for_profession(profession: str) -> dict:
    """Every bucketed field, priority concepts first (grouped, possibly
    multi-subfield), then all remaining bucketed fields one per group."""
    scalar, per_item = _load_buckets(profession)
    fields_out: list[dict] = []
    used: set[tuple[str, str]] = set()  # (source, dotted) consumed by priority concepts

    # 1. Priority concepts, in PRIORITY_FIELDS order.
    for spec in PRIORITY_FIELDS:
        source = scalar if spec["source"] == "scalar" else per_item
        reshape = _scalar_subfield if spec["source"] == "scalar" else _per_item_subfield
        subfields = []
        for name in spec["candidates"]:
            if name in source:
                subfields.append(reshape(source[name]))
                used.add((spec["source"], name))
        fields_out.append(
            {
                "label": spec["concept"],
                "priority": True,
                "present": bool(subfields),
                "subfields": subfields,
            }
        )

    # 2. Everything else that got bucketed, alphabetical by readable label.
    others: list[tuple[str, str, dict]] = []
    for name, entry in scalar.items():
        if ("scalar", name) not in used and not _is_evidence_internal(name):
            others.append((_humanize(name), name, _scalar_subfield(entry)))
    for name, entry in per_item.items():
        if ("per_item", name) not in used and not _is_evidence_internal(name):
            others.append((_humanize(name), name, _per_item_subfield(entry)))
    for label, _name, subfield in sorted(others, key=lambda x: x[0].lower()):
        fields_out.append(
            {
                "label": label,
                "priority": False,
                "present": True,
                "subfields": [subfield],
            }
        )

    return {"profession": profession, "fields": fields_out}


def discover_professions() -> list[str]:
    """Every profession with a Pass-3 scalar bucket file, alphabetical."""
    if not MAP_PREP_DIR.exists():
        return []
    return sorted(
        p.name
        for p in MAP_PREP_DIR.iterdir()
        if p.is_dir() and (p / "text_buckets.json").exists()
    )


def build_payload(professions: list[str]) -> dict:
    return {
        "generated_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "concepts": [f["concept"] for f in PRIORITY_FIELDS],
        "professions": professions,
        "data": [build_for_profession(p) for p in professions],
    }


def to_markdown(payload: dict) -> str:
    lines = [
        "# Field Tag Sheet",
        "",
        f"_Generated {payload['generated_at']}_",
        "",
        "Plain-English tags for each profession's key licensure fields, derived",
        "by `pipeline.map_prep.bucket_text` (no per-row hand-curation — the LLM",
        "clustered each field's actual state values into a handful of buckets).",
        "Counts are states per tag (or disciplinary grounds per tag, for the",
        "Discipline field). Scope wording is profession-specific, so the bucketed",
        "field name varies by profession.",
        "",
    ]
    def emit_field(field: dict) -> None:
        lines.append(f"#### {field['label']}")
        if not field["present"]:
            lines.append("")
            lines.append("_No bucketed tags for this field (data too sparse "
                         "or not yet run)._")
            lines.append("")
            return
        for sf in field["subfields"]:
            lines.append("")
            lines.append(f"`{sf['field_name']}` — {sf['unit']} per tag:")
            lines.append("")
            for t in sf["tags"]:
                extra = ""
                if sf["kind"] == "per_item" and "states" in t:
                    extra = f", {t['states']} states"
                lines.append(f"- **{t['label']}** ({t['count']}{extra})")
        lines.append("")

    for prof in payload["data"]:
        lines.append(f"## {prof['profession'].replace('_', ' ').title()}")
        lines.append("")
        priority = [f for f in prof["fields"] if f.get("priority")]
        other = [f for f in prof["fields"] if not f.get("priority")]
        lines.append("### Priority fields")
        lines.append("")
        for field in priority:
            emit_field(field)
        if other:
            lines.append("### Other bucketed fields")
            lines.append("")
            for field in other:
                emit_field(field)
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--professions",
        nargs="+",
        help="Limit to these professions (default: every profession with a "
        "Pass-3 bucket run).",
    )
    ap.add_argument(
        "--upload",
        action="store_true",
        help="Also upload data/tag_sheet.json to Vercel Blob.",
    )
    args = ap.parse_args()

    professions = args.professions or discover_professions()
    if not professions:
        raise SystemExit(
            "no professions with map_prep/<prof>/text_buckets.json — run "
            "pipeline.map_prep.bucket_text first"
        )

    payload = build_payload(professions)
    payload_json = json.dumps(payload, indent=2)

    web_path = WEB_PUBLIC_DIR / "data" / "tag_sheet.json"
    web_path.parent.mkdir(parents=True, exist_ok=True)
    web_path.write_text(payload_json)
    print(f"wrote {web_path}  ({len(professions)} professions)")

    md_path = RESULTS_DIR / "tag_sheet.md"
    md_path.write_text(to_markdown(payload))
    print(f"wrote {md_path}")

    if args.upload:
        from publish.blob_upload import upload_json

        url = upload_json("data/tag_sheet.json", payload_json)
        print(f"uploaded → {url}")


if __name__ == "__main__":
    main()
