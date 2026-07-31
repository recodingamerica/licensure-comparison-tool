"""Build the three-state scope MATRICES the Scope tab renders above the
capability presence-matrix.

Scope of practice is captured in the extracted records in several field SHAPES,
and this surfaces all of them as one comparable per-state matrix — the
included / excluded / not-addressed signal the client wants for every scope
attribute, with NO re-extraction (it reads values already extracted):

  bool   → included / excluded / not_addressed, normalized by field-name POLARITY
           so the matrix reads uniformly (`*_authorized` true=included;
           `*_excluded`/`*_prohibited`/`*_restricted` true=excluded; `*_required`
           is a separate condition: required / not / ·). null/absent = not_addressed.
  enum   → graded: the per-state value, with explicit not_authorized/excluded/none
           values mapped to the excluded state.
  list   → if a discovered scope vocabulary + re-extracted scope__ matrix exists
           (optometry), the per-item three-state matrix; otherwise present/absent
           per distinct listed value, with polarity from the field name
           (exclusion lists → present = excluded).
  int/str → NOT included here (quantities belong to the value map; free text is
           prose). Counted + reported, never silently dropped.

Scope-field SELECTION reuses build_scope_capabilities._is_scope_field (the single
category-based rule for "is this scope of practice vs license/fee/admin").

Input:  results/discovered/<profession>.json      (field types + categories)
        results/structured/<profession>/<STATE>.json  (extracted values)
        results/scope_vocab/<profession>.json      (optional: list-field vocab)
Output: web/public/data/scope_matrices.json
  { <profession>: { display, rows: [
      { label, field, kind: "included_excluded"|"condition"|"graded",
        cells: { <ST>: <status-or-value> },
        order?: [...]   # graded: value order for coloring
      } ] } }

Run:
  python -m pipeline.publish.build_scope_matrices [--upload]
"""

from __future__ import annotations

import argparse
import json
import re

from pipeline._records import record_files
from pipeline._runlog import record_run
from pipeline.extract.model_helpers import is_evidence_node
from pipeline.paths import DISCOVERED_DIR, SCOPE_VOCAB_DIR, STRUCTURED_DIR, WEB_PUBLIC_DIR
from pipeline.publish.build_scope_capabilities import _is_scope_field

DATA_DIR = WEB_PUBLIC_DIR / "data"
OUT = DATA_DIR / "scope_matrices.json"

# Field-name polarity → how (true/false) maps to (included/excluded), or a
# separate "condition" (required-style) axis. Order matters: exclusion before
# inclusion so `not_authorized` doesn't read as inclusion.
_EXCLUSION = ("exclud", "prohibit", "restrict", "not_authorized", "barred", "disallow", "forbidden")
_INCLUSION = ("authoriz", "permitt", "allowed", "available", "authority", "_included", "eligible", "may_")
_CONDITION = ("required", "requirement", "mandatory", "must_", "_needed")
# Enum values that read as the excluded end.
_ENUM_EXCLUDED = ("not_authorized", "none", "not_allowed", "excluded", "prohibited", "no_authority")


def _polarity(field_name: str) -> str:
    n = field_name.lower()
    if any(k in n for k in _EXCLUSION):
        return "exclusion"
    if any(k in n for k in _CONDITION):
        return "condition"
    return "inclusion"  # default: *_authorized-style


def _bool_status(value, polarity: str) -> str:
    """Map a bool value + field polarity to a uniform status."""
    if value is None:
        return "not_addressed"
    if polarity == "condition":
        return "required" if value else "not_required"
    if polarity == "exclusion":
        return "excluded" if value else "included"
    return "included" if value else "excluded"


def _label(field_name: str) -> str:
    base = re.sub(r"_(authorized|permitted|allowed|available|required|excluded|restriction)$", "", field_name)
    base = base.replace("_", " ").strip()
    return (base[:1].upper() + base[1:]) if base else field_name


def _all_fields(profession: str) -> list[dict]:
    d = json.loads((DISCOVERED_DIR / f"{profession}.json").read_text())
    return [f for f in d.get("fields", []) if f.get("name")]


def _records(profession: str):
    for f in record_files(STRUCTURED_DIR / profession):
        rec = json.loads(f.read_text())
        if isinstance(rec, dict):
            yield rec.get("state") or f.stem, rec


def _val(rec: dict, name: str):
    """Extracted value for a profession_specific field, or None if absent/silent."""
    node = (rec.get("profession_specific") or {}).get(name)
    if node is None:
        return None
    return node.get("value") if is_evidence_node(node) else node


def _scope_vocab_dim(profession: str, field_name: str) -> dict | None:
    p = SCOPE_VOCAB_DIR / f"{profession}.json"
    if not p.exists():
        return None
    for dim in json.loads(p.read_text()).get("dimensions", []):
        if dim.get("source_field") == field_name:
            return dim
    return None


def _bool_rows(profession: str, field_name: str, recs: list[tuple[str, dict]]) -> dict:
    polarity = _polarity(field_name)
    kind = "condition" if polarity == "condition" else "included_excluded"
    cells = {st: _bool_status(_val(rec, field_name), polarity) for st, rec in recs}
    return {"label": _label(field_name), "field": field_name, "kind": kind, "cells": cells}


def _enum_rows(profession: str, field_name: str, recs: list[tuple[str, dict]]) -> dict:
    cells: dict[str, str] = {}
    values: list[str] = []
    for st, rec in recs:
        v = _val(rec, field_name)
        if v is None:
            continue
        v = str(v)
        cells[st] = v
        if v not in values:
            values.append(v)
    return {"label": _label(field_name), "field": field_name, "kind": "graded",
            "cells": cells, "order": values,
            "excluded_values": [v for v in values if any(k in v.lower() for k in _ENUM_EXCLUDED)]}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def _list_rows(profession: str, field_name: str, recs: list[tuple[str, dict]]) -> list[dict]:
    """Per-item rows for a list field — ONLY when we have a canonical vocabulary
    for it (from scope_vocab). Raw free-text list values across 50 states produce
    hundreds of near-duplicate rows, so an uncanonicalized list field is skipped
    (returns []), not exploded.

    - Re-extracted three-state matrix present (optometry scope__<dim>): one
      included/excluded row per vocab item, from the classified status.
    - Canonical vocab but no re-extraction: present/absent per vocab item,
      matching each state's raw listed values to the vocab. Polarity from the
      field name (an exclusion list → present = excluded)."""
    dim = _scope_vocab_dim(profession, field_name)
    if not dim:
        return []  # no canonical vocab → skip rather than explode
    vocab = dim["vocab"]
    mf = dim["matrix_field"]
    reextracted = any(isinstance((r.get("profession_specific") or {}).get(mf), list) for _, r in recs)
    lbl = _label(field_name)

    if reextracted:
        # How many items in this state share each quote? A quote attached to several
        # items IS a category clause ("Surgery of any kind is expressly prohibited"
        # covering nine procedures); a quote used for exactly one item named that item.
        # That is a structural fact about the record, not a guess about its wording.
        #
        # It matters because the two kinds are not equally reliable. Scored against
        # OPLR's optometry scans, item-specific answers agreed 22/22 (100%) while
        # category-derived ones agreed 28/43 (65%) — every disagreement we have with
        # their benchmark is a category answer. A lexical check ("does the quote name
        # the item") independently found the same split, 100% vs 62%, which is why we
        # trust the finding even though that first instrument was noisy.
        #
        # 76% of optometry's coloured cells are category-derived and today they render
        # identically to statutory fact. The UI needs to be able to say which is which.
        # Reuse ALONE is not enough. An ENUMERATED grant — "Laser capsulotomy, laser
        # peripheral iridotomy, and laser trabeculoplasty" (CO) — is one quote answering
        # three items while naming every one of them. Reuse would call that inferred; it
        # is the opposite, the most explicit form a grant takes.
        # So a shared quote only counts as a category read when it ALSO fails to name the
        # item. Neither signal is sufficient by itself: reuse misreads enumerations, and
        # name-matching alone misreads ranges ("Schedule III through V" covers Schedule IV
        # without naming it) and compound wording ("pterygium surgery" vs "Pterygium
        # removal").
        shared: dict[str, set[str]] = {}
        for st, rec in recs:
            counts: dict[str, int] = {}
            for it in ((rec.get("profession_specific") or {}).get(mf) or []):
                q = (it.get("quote") or "").strip() if isinstance(it, dict) else ""
                if q:
                    counts[q] = counts.get(q, 0) + 1
            shared[st] = {q for q, n in counts.items() if n > 1}

        aliases = dim.get("aliases") or {}

        def _quote_names(quote: str, item: str) -> bool:
            """Does this quote name the item, by the vocabulary's own alias list?"""
            q = quote.lower()
            for name in [item, *aliases.get(item, [])]:
                bare = re.sub(r"\(.*?\)", " ", name)          # drop "(PRK)"-style asides
                toks = [t for t in re.split(r"[^a-z0-9]+", bare.lower()) if len(t) > 3]
                if toks and all(t in q for t in toks):
                    return True
            return False

        rows = []
        for item in vocab:
            cells = {}
            # Per-cell evidence. The status is decided per ITEM, but the row only named
            # its parent field, so the UI had nothing item-level to show and fell back to
            # the parent's Evidence — which is why a not-addressed cell displayed a
            # neighbouring prohibition quote and an authorized cell showed nothing
            # relevant (#122). Carry the item's own quote/citation. Only cells that
            # actually have a quote get an entry, so "no key" IS "no statute" — the
            # invariant the Scope view's colours claim (see tests/test_scope_matrix_evidence).
            ev: dict[str, dict] = {}
            for st, rec in recs:
                items = (rec.get("profession_specific") or {}).get(mf) or []
                hit = next((it for it in items if isinstance(it, dict) and it.get("item") == item), None)
                status = hit.get("status") if hit else None
                cells[st] = {"authorized": "included", "prohibited": "excluded"}.get(status, "not_addressed")
                quote = ((hit or {}).get("quote") or "").strip()
                if quote:
                    ev[st] = {
                        "quote": quote,
                        "citation": ((hit or {}).get("citation") or "").strip(),
                        # "category" = the quote answers OTHER items too AND doesn't name
                        # this one, so we read it as covering rather than naming. Anything
                        # else — a quote cited for this item alone, or a shared quote that
                        # does name it (an enumerated grant) — is "named".
                        "basis": (
                            "category"
                            if quote in shared.get(st, ()) and not _quote_names(quote, item)
                            else "named"
                        ),
                    }
            row = {"label": f"{lbl}: {item}", "field": field_name,
                   "kind": "included_excluded", "cells": cells}
            if ev:
                row["evidence"] = ev
            rows.append(row)
        return rows

    # Present/absent against the canonical vocab (no re-extraction needed).
    present_status = "excluded" if _polarity(field_name) == "exclusion" else "included"
    vocab_keys = {_norm(v): v for v in vocab}
    per_state: dict[str, set[str]] = {}
    for st, rec in recs:
        v = _val(rec, field_name)
        if isinstance(v, list):
            per_state[st] = {vocab_keys[k] for x in v if (k := _norm(x)) in vocab_keys}
    rows = []
    for item in vocab:
        cells = {st: (present_status if item in got else "not_addressed") for st, got in per_state.items()}
        rows.append({"label": f"{lbl}: {item}", "field": field_name, "kind": "included_excluded", "cells": cells})
    return rows


def build_profession(profession: str) -> tuple[dict | None, dict]:
    recs = list(_records(profession))
    if not recs:
        return None, {}
    fields = _all_fields(profession)
    rows: list[dict] = []
    counts = {"bool": 0, "enum": 0, "list": 0, "int_skipped": 0, "str_skipped": 0}
    for f in fields:
        name, typ = f["name"], f.get("type")
        category = f.get("category") or "other"
        is_scope = _is_scope_field(name, f.get("category"))
        made: list[dict] = []
        if typ == "bool":
            r = _bool_rows(profession, name, recs)
            if any(v != "not_addressed" for v in r["cells"].values()):
                made = [r]; counts["bool"] += 1
        elif typ == "enum":
            r = _enum_rows(profession, name, recs)
            if r["cells"]:
                made = [r]; counts["enum"] += 1
        elif typ == "list[str]":
            made = [r for r in _list_rows(profession, name, recs)
                    if any(v != "not_addressed" for v in r["cells"].values())]
            if made:
                counts["list"] += 1
        elif typ == "int":
            counts["int_skipped"] += 1
        elif typ == "str":
            counts["str_skipped"] += 1
        for r in made:
            r["category"] = category
            r["is_scope"] = is_scope
        rows.extend(made)
    if not rows:
        return None, counts
    display = profession.replace("_", " ").title()
    return {"display": display, "rows": rows}, counts


def build(only: set[str] | None = None) -> tuple[dict, dict]:
    out: dict = {}
    tallies: dict = {}
    for dp in sorted(DISCOVERED_DIR.glob("*.json")):
        profession = dp.stem
        if only and profession not in only:
            continue
        prof_data, counts = build_profession(profession)
        if prof_data:
            out[profession] = prof_data
        if counts:
            tallies[profession] = counts
    return out, tallies


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upload", action="store_true",
                    help="Also upload data/scope_matrices.json to Vercel Blob.")
    ap.add_argument("--professions", help="Comma-separated subset to build (default: all).")
    args = ap.parse_args()

    only = {s.strip() for s in args.professions.split(",")} if args.professions else None
    data, tallies = build(only)
    payload = json.dumps(data)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(payload + "\n")
    n_rows = sum(len(v["rows"]) for v in data.values())
    int_sk = sum(t.get("int_skipped", 0) for t in tallies.values())
    str_sk = sum(t.get("str_skipped", 0) for t in tallies.values())
    print(f"scope_matrices: {len(data)} professions, {n_rows} rows → {OUT}")
    print(f"  (skipped {int_sk} int + {str_sk} str fields — quantities/prose belong to the value map, not the three-state matrix)")
    for p in sorted(data):
        scope_n = sum(1 for r in data[p]["rows"] if r.get("is_scope"))
        print(f"  {p:26} {len(data[p]['rows']):3} rows ({scope_n} scope)  tally={tallies.get(p)}")
    if args.upload:
        from pipeline.publish.blob_upload import upload_json
        url, skipped = upload_json("data/scope_matrices.json", payload)
        print(f"{'cached' if skipped else 'uploaded'} → {url}")
    record_run("scope_matrices", professions=len(data), rows=n_rows)


if __name__ == "__main__":
    main()
