"""Coverage scorecard: per (profession × Atharv's universal field), what
fraction of states have the field populated in our extracted data.

Atharv's PDF "Universal Category" table compares one state per profession
(AL Podiatry, MD Nursing, MS Optometry, LA Dentistry, VT Accountancy, NE
Medicine). We have 40+ states per profession, so we can answer the same
question across the whole dataset — useful as a "how well are we matching
your schema" artifact.

Output: a markdown table at pipeline/results/cross_comparison_scorecard.md.
Cells use Atharv's notation:
  ✓ = ≥80% of covered states have the field populated
  ~ = 1–79% have it
  ✗ = 0% (no state populates it)

Usage:
  python -m pipeline.publish.cross_comparison_scorecard
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from extract.standard_model import is_evidence_node  # noqa: E402
from paths import RESULTS_DIR, STRUCTURED_DIR  # noqa: E402


# Atharv's "Universal Category" list from the cross-comparison PDF, mapped to
# accessors over our structured-record shape. Each accessor returns a
# populated/empty signal — populated == True if the field carries data.
#
# (Some of Atharv's categories don't have a clean home in our universal block —
# Prohibited Activities, Supervision, Authorized Settings — those live in
# `profession_specific` and vary per profession. For those we check whether
# any profession_specific key starts with a matching prefix.)

def _ev_populated(node: Any) -> bool:
    if not is_evidence_node(node):
        return False
    return node.get("value") not in (None, "", [])


def _ev_at(record: dict, *path: str) -> bool:
    cur: Any = record
    for k in path:
        if not isinstance(cur, dict):
            return False
        cur = cur.get(k)
    return _ev_populated(cur)


def _any_exam_field(record: dict, field: str) -> bool:
    lic = record.get("licensure") or {}
    exams = lic.get("exams") or []
    return any(e.get(field) not in (None, "", []) for e in exams)


def _any_exam_name(record: dict) -> bool:
    lic = record.get("licensure") or {}
    exams = lic.get("exams") or []
    return any(e.get("name") for e in exams)


def _any_prof_specific(record: dict, name_substrs: list[str]) -> bool:
    """True if the record's profession_specific block has any populated field
    whose name contains any of the given substrings. Lets us check things
    like `Supervision` and `Authorized Settings` that the discovered schema
    surfaces per-profession under various names."""
    ps = (record.get("profession_specific") or {})
    for k, v in ps.items():
        if not any(s in k.lower() for s in name_substrs):
            continue
        if v is None:
            continue
        if isinstance(v, dict):
            if _ev_populated(v):
                return True
        elif isinstance(v, list):
            if any(_ev_populated(x) if isinstance(x, dict) else bool(x) for x in v):
                return True
        elif v:
            return True
    return False


def _compacts_present(record: dict) -> bool:
    """Compacts are derived in build_frontend via regex on quote text; emulate
    that here so the scorecard reflects the published shape, not raw schema."""
    import re
    pats = [
        r"\b(?:nurse\s+licensure\s+compact|NLC)\b",
        r"\b(?:interstate\s+medical\s+licensure\s+compact|IMLC)\b",
        r"\b(?:dentist\s+(?:and\s+dental\s+hygienist\s+)?compact|dental\s+(?:hygienist\s+)?compact|DDH-?C)\b",
        r"\b(?:optometry\s+licensure\s+compact|OD-?C)\b",
        r"\b(?:physical\s+therapy\s+(?:licensure\s+)?compact|PTC)\b",
        r"\bcounseling\s+compact\b",
        r"\bsubstantial\s+equivalency\b",  # accountancy
    ]
    compiled = [re.compile(p, re.I) for p in pats]
    def walk(node):
        if isinstance(node, str):
            return any(p.search(node) for p in compiled)
        if isinstance(node, dict):
            return any(walk(v) for v in node.values())
        if isinstance(node, list):
            return any(walk(v) for v in node)
        return False
    return walk(record)


Accessor = Callable[[dict], bool]

UNIVERSAL_FIELDS: list[tuple[str, Accessor]] = [
    ("Scope of Practice",                 lambda r: _ev_at(r, "scope", "definition_quote")
                                                     or _ev_at(r, "scope", "methods_authorized")),
    ("Prohibited Activities",             lambda r: _any_prof_specific(r, ["prohibit", "unlawful", "exception"])),
    ("Advisory Board Status",             lambda r: _ev_at(r, "licensure", "advisory_board", "exists")),
    ("Advisory Board Authority Status",   lambda r: _ev_at(r, "licensure", "advisory_board", "authority")),
    ("Education (Min. Degree)",           lambda r: _ev_at(r, "licensure", "education", "degree_required")),
    ("Continuing Education",              lambda r: _ev_at(r, "licensure", "continuing_education", "required")
                                                     or _ev_at(r, "licensure", "continuing_education", "hours_per_period")),
    ("Professional Experience",           lambda r: _ev_at(r, "licensure", "post_degree_experience", "required")
                                                     or _ev_at(r, "licensure", "post_degree_experience", "duration")),
    ("Renewal Frequency (Years)",         lambda r: _ev_at(r, "licensure", "renewal", "interval_years")),
    ("National Certification",            lambda r: _ev_at(r, "licensure", "national_certification")),
    ("National Association",              lambda r: _ev_at(r, "licensure", "national_association")),
    ("Licensing Authority",               lambda r: _ev_at(r, "licensure", "issuing_authority")),
    ("Compacts",                          _compacts_present),
    ("Renewal Fee ($)",                   lambda r: _ev_at(r, "licensure", "renewal_fee_usd")),
    ("Supervision",                       lambda r: _any_prof_specific(r, ["supervis", "delegation"])),
    ("License/Cert/Training (taxonomy)",  lambda r: _ev_at(r, "licensure", "regulatory_model")),
    ("Exam (formal name)",                _any_exam_name),
    ("Exam Jurisdiction",                 lambda r: _any_exam_field(r, "jurisdiction")),
    ("Permitted Exam Attempts",           lambda r: _any_exam_field(r, "permitted_attempts")),
    ("Authorized Settings",               lambda r: _any_prof_specific(r, ["setting", "facility", "premises"])),
]

PROFESSIONS = [
    "podiatry", "nursing", "medicine", "dentistry", "optometry", "public_accountancy",
]


def fill_rate(profession: str, accessor: Accessor) -> tuple[int, int]:
    """Returns (n_populated, n_states) — covered states only."""
    pdir = STRUCTURED_DIR / profession
    n = filled = 0
    for p in sorted(pdir.glob("*.json")):
        if p.name.startswith("_"):
            continue
        rec = json.loads(p.read_text())
        n += 1
        if accessor(rec):
            filled += 1
    return filled, n


def symbol(filled: int, total: int) -> str:
    if total == 0:
        return "—"
    pct = filled / total
    if pct == 0:
        return "✗"
    if pct >= 0.8:
        return "✓"
    return "~"


def main() -> None:
    rows = []
    for field_label, accessor in UNIVERSAL_FIELDS:
        cells = []
        for prof in PROFESSIONS:
            filled, total = fill_rate(prof, accessor)
            sym = symbol(filled, total)
            cells.append(f"{sym} ({filled}/{total})")
        rows.append((field_label, cells))

    # Markdown
    out_lines = [
        "# Universal Field Cross-Comparison Scorecard",
        "",
        "How well our extracted data matches Atharv's universal-field schema",
        "(see PDF cross-comparison table). One row per universal field, one",
        "column per profession. Each cell shows `symbol (populated/total)` —",
        "where `total` counts only states with substantive extractions for",
        "that profession.",
        "",
        "Symbols mirror the PDF: **✓** = ≥80% populated, **~** = 1–79%,",
        "**✗** = 0%, **—** = no data.",
        "",
    ]

    header = "| Universal Category | " + " | ".join(p.title().replace("_", " ") for p in PROFESSIONS) + " |"
    sep = "|" + "---|" * (len(PROFESSIONS) + 1)
    out_lines.append(header)
    out_lines.append(sep)
    for field_label, cells in rows:
        out_lines.append(f"| {field_label} | " + " | ".join(cells) + " |")

    output = "\n".join(out_lines) + "\n"
    out_path = RESULTS_DIR / "cross_comparison_scorecard.md"
    out_path.write_text(output)
    print(f"wrote {out_path}\n")
    print(output)


if __name__ == "__main__":
    main()
