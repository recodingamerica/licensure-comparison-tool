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
import subprocess
import sys
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from paths import DISCOVERED_DIR, STRUCTURED_DIR, PIPELINE_ROOT, core_professions  # noqa: E402
from extract.extract_state import build_profile_model  # noqa: E402
from _records import record_files  # noqa: E402

OUT_DIR = PIPELINE_ROOT.parent / "docs" / "methodology"

# Nothing in this file is hand-maintained per-field. Group intros come from the model
# docstrings; field meanings/types/vocabularies from Field(description=) + the schema.
EVIDENCE_KEYS = {"value", "quote", "citation"}
MAX_DEPTH = 3


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


def _unwrap(prop: dict, defs: dict) -> tuple[dict, dict]:
    """Pull the non-null branch of an Optional, return (branch, resolved_target)."""
    branch = prop
    if "anyOf" in prop:
        nn = [b for b in prop["anyOf"] if b.get("type") != "null"]
        branch = nn[0] if nn else prop
    return branch, _resolve(branch, defs)


def _walk(model_schema: dict, defs: dict, prefix: str = "", depth: int = 0) -> list[dict]:
    """Recursively flatten a model's fields into rows with dotted paths. Evidence
    wrappers are leaves; nested sub-models and list items are drilled into. The
    universal quote/citation companions aren't emitted as rows (the doc header
    explains every field carries them)."""
    rows: list[dict] = []
    for name, prop in (model_schema.get("properties") or {}).items():
        if name in ("quote", "citation"):
            continue
        path = f"{prefix}{name}"
        branch, target = _unwrap(prop, defs)
        desc = prop.get("description") or target.get("description") or ""
        tprops = target.get("properties") or {}
        if EVIDENCE_KEYS <= set(tprops):                       # Evidence wrapper → leaf
            vtype, enum = _value_spec(target, defs)
            if not desc:
                desc = tprops["value"].get("description") or ""
            rows.append({"field": path, "type": vtype, "vocabulary": enum, "meaning": desc, "depth": depth})
        elif branch.get("type") == "array":                   # list of sub-objects
            rows.append({"field": path, "type": "list", "vocabulary": [], "meaning": desc, "depth": depth})
            _, item_t = _unwrap(branch.get("items") or {}, defs)
            if depth < MAX_DEPTH and item_t.get("properties"):
                rows += _walk(item_t, defs, f"{path}[].", depth + 1)
        elif tprops and depth < MAX_DEPTH:                     # nested sub-model → recurse
            rows.append({"field": path, "type": "object", "vocabulary": [], "meaning": desc, "depth": depth})
            rows += _walk(target, defs, f"{path}.", depth + 1)
        else:                                                 # scalar leaf
            enum = list(target.get("enum") or branch.get("enum") or [])
            t = "enum" if enum else (target.get("type") or branch.get("type") or "string")
            rows.append({"field": path, "type": t, "vocabulary": enum, "meaning": desc, "depth": depth})
    return rows


def _example_record(profession: str) -> dict | None:
    files = list(record_files(STRUCTURED_DIR / profession))
    return json.loads(files[0].read_text()) if files else None


def _data_as_of(profession: str) -> str | None:
    """Date (YYYY-MM-DD) of the last commit that touched this profession's structured
    records — i.e. how current the data behind this dictionary is. Deterministic (git
    history, not wall-clock), so regenerating without a data change produces no diff."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(STRUCTURED_DIR / profession)],
            cwd=PIPELINE_ROOT.parent, capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def _example_at(record: dict, group: str, path: str) -> dict | None:
    """Resolve a dotted (with `[]`) field path against a record; return its Evidence
    example (value+quote+citation) or a scalar value."""
    cur = (record or {}).get(group)
    for seg in path.split("."):
        if not isinstance(cur, dict):
            return None
        arr = seg.endswith("[]")
        cur = cur.get(seg[:-2] if arr else seg)
        if arr:
            if not isinstance(cur, list) or not cur:
                return None
            cur = cur[0]
    if isinstance(cur, dict) and "value" in cur:
        return {"value": cur.get("value"), "quote": (cur.get("quote") or "")[:200],
                "citation": cur.get("citation")}
    if isinstance(cur, (str, int, float, bool)):
        return {"value": cur}
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
        rows = _walk(gschema, defs)
        for r in rows:
            r["example"] = _example_at(record, gname, r["field"])
        groups.append({"group": gname, "intro": gschema.get("description", ""), "fields": rows})
    return {"profession": profession, "data_as_of": _data_as_of(profession), "groups": groups,
            "example_state": (record or {}).get("state")}


def render_md(d: dict) -> str:
    L = [f"# Field dictionary — {d['profession']}", ""]
    L.append("_Auto-generated from the extraction model (`standard_model.py` + the "
             "profession's discovered schema). Do not edit by hand — regenerate with "
             "`python -m pipeline.publish.generate_field_dictionary`._")
    L.append("")
    L.append(f"**Reflects extracted data as of {d.get('data_as_of') or 'unknown'}** "
             f"(latest commit to `{d['profession']}` records). Regenerate to refresh.")
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
            indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * f.get("depth", 0)
            L.append(f"| {indent}`{f['field']}` | {f['type']}{vocab} | {meaning} | {exval} |")
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
