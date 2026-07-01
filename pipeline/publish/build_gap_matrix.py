"""Stage 3 — gap matrix across the 5 audit fields.

For each (profession × state × sub-field) in the audit set (see
pipeline/notes/FIELD_AUDIT.md), classify the cell status as one of:

  - populated     — Evidence-wrapped field has a value (and quote verified)
  - unverified    — populated but the verifier flagged the quote
  - null          — structured record exists but this field is null
  - not_licensed  — state has no matched chapter for this profession
                    (per pipeline/results/profession_index/<prof>.json)
  - no_record     — profession_index says matched but no structured/<state>.json

For nulls, "statute-genuinely-silent" vs "extraction-miss" can't be
distinguished from the structured record alone — that needs a source-text
re-check on a sampled subset. This script reports the raw null counts; the
silent-vs-miss classification is a follow-on.

Output:
  pipeline/results/gap_matrix/cells.csv    — one row per (prof, state, field)
  pipeline/results/gap_matrix/summary.csv  — counts per (prof, field)
  stdout                                    — readable per-profession summary

Usage:
  python -m pipeline.publish.build_gap_matrix
  python -m pipeline.publish.build_gap_matrix --professions podiatry,medicine
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from typing import Any


from pipeline._records import record_files
from pipeline.paths import STRUCTURED_DIR as _STRUCTURED_DIR, PROFESSION_INDEX_DIR as _PROF_INDEX_DIR

_OUT_DIR = _PIPELINE_DIR / "results" / "gap_matrix"

# The 5 audit fields, decomposed into the leaf sub-fields that actually carry
# Evidence in the structured records. `kind` controls how status is decided:
#   "evidence"      — leaf is an Evidence-shaped dict ({value, quote, citation,
#                     [unverified]}); populated iff value is non-null.
#   "list_nonempty" — leaf is a list of objects (e.g. disciplinary_grounds);
#                     populated iff len > 0.
AUDIT_FIELDS: list[tuple[str, str, str]] = [
    ("education",  "licensure.education.degree_required",            "evidence"),
    ("education",  "licensure.education.accrediting_body",           "evidence"),
    ("experience", "licensure.post_degree_experience.required",      "evidence"),
    ("experience", "licensure.post_degree_experience.duration",      "evidence"),
    ("experience", "licensure.post_degree_experience.kind",          "evidence"),
    ("authority",  "licensure.issuing_authority",                    "evidence"),
    ("authority",  "licensure.regulatory_authority.name",            "evidence"),
    ("authority",  "licensure.regulatory_authority.type",            "evidence"),
    ("authority",  "licensure.regulatory_authority.umbrella_agency", "evidence"),
    ("discipline", "licensure.disciplinary_grounds",                 "list_nonempty"),
    ("scope",      "scope.definition_quote",                         "evidence"),
    ("scope",      "scope.methods_authorized",                       "evidence"),
    ("scope",      "scope.drug_authority",                           "evidence"),
    ("scope",      "licensure.scope_protection",                     "evidence"),
]

STATUS_POP = "populated"
STATUS_UNV = "unverified"
STATUS_NULL = "null"
STATUS_NOT_LIC = "not_licensed"
STATUS_NO_REC = "no_record"
STATUSES = [STATUS_POP, STATUS_UNV, STATUS_NULL, STATUS_NOT_LIC, STATUS_NO_REC]


def _resolve(rec: dict, dotted: str) -> Any:
    cur: Any = rec
    for seg in dotted.split("."):
        if not isinstance(cur, dict) or seg not in cur:
            return None
        cur = cur[seg]
    return cur


def _evidence_status(node: Any) -> tuple[str, str, str, str]:
    """(status, value_str, quote, citation) for an Evidence-shaped node."""
    if not isinstance(node, dict):
        return STATUS_NULL, "", "", ""
    val = node.get("value")
    if val is None:
        return STATUS_NULL, "", "", ""
    status = STATUS_UNV if node.get("unverified") else STATUS_POP
    val_str = "; ".join(str(x) for x in val if x is not None) if isinstance(val, list) else str(val)
    return status, val_str[:200], (node.get("quote") or "")[:200], node.get("citation") or ""


def _list_nonempty_status(node: Any) -> tuple[str, str, str, str]:
    """(status, value_str, _, _) for a list-of-objects field like disciplinary_grounds."""
    if not isinstance(node, list) or len(node) == 0:
        return STATUS_NULL, "", "", ""
    n_unv = sum(1 for it in node if isinstance(it, dict) and it.get("unverified"))
    status = STATUS_UNV if n_unv == len(node) else STATUS_POP
    return status, f"{len(node)} items ({n_unv} unverified)", "", ""


def _state_licensed(prof_index: dict, state: str) -> bool:
    matched = (prof_index.get("by_state", {}).get(state) or {}).get("matched") or []
    return bool(matched)


def cells_for_profession(profession: str) -> list[dict]:
    pi_path = _PROF_INDEX_DIR / f"{profession}.json"
    if not pi_path.exists():
        print(f"WARN: no profession_index for {profession}", file=sys.stderr)
        return []
    prof_index = json.loads(pi_path.read_text())
    all_states = sorted(prof_index.get("by_state", {}).keys())

    rec_by_state: dict[str, dict] = {}
    prof_dir = _STRUCTURED_DIR / profession
    if prof_dir.exists():
        for f in record_files(prof_dir):
            try:
                d = json.loads(f.read_text())
            except Exception as e:
                # A corrupt record would otherwise vanish and read as a true
                # gap (missing state). Surface it loudly instead.
                print(f"WARN: unreadable {profession}/{f.stem}.json — {str(e)[:120]}", file=sys.stderr)
                continue
            if isinstance(d, dict):
                rec_by_state[f.stem] = d

    rows: list[dict] = []
    for state in all_states:
        licensed = _state_licensed(prof_index, state)
        rec = rec_by_state.get(state)
        for group, dotted, kind in AUDIT_FIELDS:
            if not licensed:
                status, value, quote, citation = STATUS_NOT_LIC, "", "", ""
            elif rec is None:
                status, value, quote, citation = STATUS_NO_REC, "", "", ""
            else:
                node = _resolve(rec, dotted)
                if kind == "evidence":
                    status, value, quote, citation = _evidence_status(node)
                else:
                    status, value, quote, citation = _list_nonempty_status(node)
            rows.append({
                "profession": profession,
                "state": state,
                "group": group,
                "field": dotted,
                "status": status,
                "value": value,
                "quote": quote,
                "citation": citation,
            })
    return rows


def write_cells(all_rows: list[dict]) -> None:
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = _OUT_DIR / "cells.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["profession", "state", "group", "field", "status", "value", "quote", "citation"],
        )
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    print(f"wrote {out} ({len(all_rows)} rows)")


def write_summary(all_rows: list[dict]) -> None:
    counts: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in all_rows:
        counts[(r["profession"], r["group"], r["field"])][r["status"]] += 1
    out = _OUT_DIR / "summary.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["profession", "group", "field"] + STATUSES + ["total"])
        for key in sorted(counts.keys()):
            row = counts[key]
            total = sum(row.values())
            w.writerow(list(key) + [row.get(s, 0) for s in STATUSES] + [total])
    print(f"wrote {out}")


def print_summary(all_rows: list[dict]) -> None:
    counts: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in all_rows:
        counts[(r["profession"], r["group"], r["field"])][r["status"]] += 1
    by_prof: dict[str, list] = defaultdict(list)
    for (prof, group, field), c in counts.items():
        by_prof[prof].append((group, field, c))
    for prof in sorted(by_prof):
        print(f"\n== {prof} ==")
        print(f"{'field':<55} {'pop':>5} {'unv':>5} {'null':>5} {'!lic':>5} {'!rec':>5} {'tot':>5}")
        for group, field, c in sorted(by_prof[prof], key=lambda x: (x[0], x[1])):
            total = sum(c.values())
            print(
                f"{field:<55} {c.get(STATUS_POP, 0):>5} {c.get(STATUS_UNV, 0):>5} "
                f"{c.get(STATUS_NULL, 0):>5} {c.get(STATUS_NOT_LIC, 0):>5} "
                f"{c.get(STATUS_NO_REC, 0):>5} {total:>5}"
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", help="Comma-separated list (default: all in structured/)")
    args = ap.parse_args()

    if args.professions:
        profs = [p.strip() for p in args.professions.split(",") if p.strip()]
    else:
        profs = sorted([d.name for d in _STRUCTURED_DIR.iterdir() if d.is_dir()])

    all_rows: list[dict] = []
    for p in profs:
        all_rows.extend(cells_for_profession(p))

    if not all_rows:
        print("no data", file=sys.stderr)
        return

    write_cells(all_rows)
    write_summary(all_rows)
    print_summary(all_rows)


if __name__ == "__main__":
    main()
