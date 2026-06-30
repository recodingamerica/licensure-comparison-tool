"""Generate a field dictionary (methodology that tracks the code) per profession.

Inspired by pull_usaspending's variable-lineage doc: the technical columns are
auto-extracted from the code so they can't drift; only a small block of category
intros is hand-maintained.

Here the source of truth is the **Pydantic extraction model** — `build_profile_model`
composes the universal base (standard_model.py: licensure, scope) with the profession's
discovered schema. `model_json_schema()` exposes every leaf field's name, type, enum
values, and description, so this walks that schema and emits, per field:

  field path · value type (+ controlled vocabulary) · what it means (the model/prompt
  description) · a real example (value + the verbatim statute quote + citation)

Output (per profession): docs/methodology/<profession>_field_dictionary.md + .json.
The .json is a self-contained data dictionary a non-technical reader can download and
hand to an LLM alongside the data — the Utah-OPLR-handoff use case.

Every extracted leaf is an Evidence object {value, quote, citation}: the value, the
verbatim phrase from the statute that supports it, and the citation it came from.

Run:
  python -m pipeline.publish.generate_field_dictionary --profession dietetics
  python -m pipeline.publish.generate_field_dictionary --all          # every published profession
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from paths import DISCOVERED_DIR, STRUCTURED_DIR, PIPELINE_ROOT, core_professions  # noqa: E402
from extract.extract_state import build_profile_model  # noqa: E402
from _records import record_files  # noqa: E402

OUT_DIR = PIPELINE_ROOT.parent / "docs" / "methodology"

# The ONLY hand-maintained part: a one-line intro per top-level group. Everything
# else (fields, types, vocabularies, descriptions, examples) is read from the code.
GROUP_INTROS = {
    "licensure": "Whether and how the state credentials this profession — the regulatory "
                 "model, credential type, authority, exams, fees, and renewal.",
    "scope": "What the practice act lets (or reserves to) this profession — the defined "
             "scope and any title/scope protection.",
    "profession_specific": "Fields discovered specifically for this profession (auto-derived "
                            "from its statutes; they vary profession to profession).",
}


def _resolve(schema: dict, defs: dict) -> dict:
    """Follow a $ref one level; return the node otherwise."""
    if "$ref" in schema:
        return defs.get(schema["$ref"].split("/")[-1], {})
    return schema


def _value_spec(ev_schema: dict, defs: dict) -> tuple[str, list[str]]:
    """Given an Evidence model schema, describe its `value` field: (type, enum_values)."""
    val = (ev_schema.get("properties") or {}).get("value")
    if not val:
        return "object", []
    # value may be a $ref to an enum, an anyOf, or a plain typed field
    node = _resolve(val, defs)
    if "enum" in node:
        return "enum", list(node["enum"])
    if "enum" in val:
        return "enum", list(val["enum"])
    t = node.get("type") or val.get("type") or "string"
    if t == "array":
        return "list", []
    return t, []


def _field_rows(group_schema: dict, defs: dict) -> list[dict]:
    """One row per leaf field in a group model."""
    rows = []
    for name, prop in (group_schema.get("properties") or {}).items():
        # Optional fields are anyOf:[ {$ref|type}, {null} ]; pull the non-null branch.
        branch = prop
        if "anyOf" in prop:
            non_null = [b for b in prop["anyOf"] if b.get("type") != "null"]
            branch = non_null[0] if non_null else prop
        target = _resolve(branch, defs)
        desc = prop.get("description") or target.get("description") or ""
        props = target.get("properties") or {}
        if {"value", "quote", "citation"} <= set(props):           # an Evidence wrapper
            vtype, enum = _value_spec(target, defs)
            # prefer the field-level description, fall back to value's
            if not desc:
                desc = (props["value"].get("description") or "")
            rows.append({"field": name, "type": vtype, "vocabulary": enum, "meaning": desc})
        elif branch.get("type") == "array":                        # list of sub-objects
            rows.append({"field": name, "type": "list", "vocabulary": [], "meaning": desc})
        else:                                                      # nested sub-model
            rows.append({"field": name, "type": target.get("title", "object"),
                         "vocabulary": [], "meaning": desc})
    return rows


def _example_record(profession: str) -> dict | None:
    files = list(record_files(STRUCTURED_DIR / profession))
    return json.loads(files[0].read_text()) if files else None


def _example_for(record: dict, group: str, field: str) -> dict | None:
    leaf = ((record or {}).get(group) or {}).get(field)
    if isinstance(leaf, dict) and "value" in leaf:
        return {"value": leaf.get("value"), "quote": (leaf.get("quote") or "")[:200],
                "citation": leaf.get("citation")}
    return None


def build_dictionary(profession: str) -> dict:
    discovered = json.loads((DISCOVERED_DIR / f"{profession}.json").read_text())
    model = build_profile_model(profession, discovered)
    schema = model.model_json_schema()
    defs = schema.get("$defs") or {}
    record = _example_record(profession)

    groups = []
    for gname in ("licensure", "scope", "profession_specific"):
        gprop = (schema.get("properties") or {}).get(gname)
        if not gprop:
            continue
        gschema = _resolve(gprop, defs)
        rows = _field_rows(gschema, defs)
        for r in rows:
            r["example"] = _example_for(record, gname, r["field"])
        groups.append({"group": gname, "intro": GROUP_INTROS.get(gname, ""), "fields": rows})
    return {"profession": profession, "groups": groups,
            "example_state": (record or {}).get("state")}


def render_md(d: dict) -> str:
    L = [f"# Field dictionary — {d['profession']}", ""]
    L.append("_Auto-generated from the extraction model (`standard_model.py` + the "
             "profession's discovered schema). Do not edit by hand — regenerate with "
             "`python -m pipeline.publish.generate_field_dictionary`._")
    L.append("")
    L.append("Every field is an **Evidence** object: a `value`, the verbatim `quote` from "
             "the statute that supports it, and the `citation` it came from. Examples below "
             f"are sampled from {d['profession']}/{d.get('example_state') or '?'}.")
    L.append("")
    for g in d["groups"]:
        L.append(f"## {g['group']}")
        L.append(f"_{g['intro']}_")
        L.append("")
        L.append("| field | type | what it means | example value |")
        L.append("|---|---|---|---|")
        for f in g["fields"]:
            vocab = f" — one of: {', '.join(f['vocabulary'])}" if f["vocabulary"] else ""
            ex = f["example"]
            exval = "" if ex is None else json.dumps(ex["value"])[:60]
            meaning = (f["meaning"] or "").replace("\n", " ").replace("|", "\\|").strip()
            L.append(f"| `{f['field']}` | {f['type']}{vocab} | {meaning} | {exval} |")
        L.append("")
    return "\n".join(L)


def generate(profession: str) -> Path:
    d = build_dictionary(profession)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / f"{profession}_field_dictionary.md"
    json_path = OUT_DIR / f"{profession}_field_dictionary.json"
    md_path.write_text(render_md(d) + "\n")
    json_path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    n = sum(len(g["fields"]) for g in d["groups"])
    print(f"{profession}: wrote {n} fields → {md_path.name} + {json_path.name}")
    return md_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profession")
    ap.add_argument("--all", action="store_true", help="every published (core) profession")
    args = ap.parse_args()
    if args.all:
        for p in core_professions():
            generate(p)
    elif args.profession:
        generate(args.profession)
    else:
        ap.error("pass --profession NAME or --all")


if __name__ == "__main__":
    main()
