"""Aggregate per-state structured extractions into one data.json for the viewer.

Schema is now Evidence-wrapped: each leaf is {value, quote, citation, [unverified]}.
We pass the entire structured record through to the frontend so the modal can
show evidence; for table columns we surface UNIVERSAL fields only (license,
issuing authority, education, post-degree experience, exams, renewal, CE,
reciprocity). Profession-specific fields live in the modal.

Usage:
  python build_frontend.py --profession podiatry
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from paths import STRUCTURED_DIR, DISCOVERED_DIR, TRIMMED_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402
from publish.blob_upload import upload_json  # noqa: E402


def _ev_value(node: Any) -> Any:
    """If `node` is Evidence-shaped, return .value; otherwise return as-is."""
    if isinstance(node, dict) and {"value", "quote", "citation"}.issubset(node.keys()):
        return node["value"]
    return node


def _g(d: dict | None, *path: str) -> Any:
    cur: Any = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _count_evidence(record: dict) -> tuple[int, int]:
    """Walk record for Evidence-shaped objects, count verified vs unverified."""
    verified = unverified = 0

    def walk(node: Any):
        nonlocal verified, unverified
        if isinstance(node, dict):
            if {"value", "quote", "citation"}.issubset(node.keys()):
                if node.get("unverified"):
                    unverified += 1
                else:
                    verified += 1
                return
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(record)
    return verified, unverified


def hoist_row(record: dict) -> dict:
    """Universal columns. Profession-specific dimensions live in the modal."""
    lic = record.get("licensure") or {}
    verified, unverified = _count_evidence(record)
    return {
        "state": record["state"],
        "coverage_gap": False,
        "license_required": _ev_value(lic.get("license_required")),
        "regulatory_model": _ev_value(lic.get("regulatory_model")),
        "title_protection": _ev_value(lic.get("title_protection")),
        "scope_protection": _ev_value(lic.get("scope_protection")),
        "issuing_authority": _ev_value(lic.get("issuing_authority")),
        "education_degree": _ev_value(_g(lic, "education", "degree_required")),
        "post_degree_duration": _ev_value(_g(lic, "post_degree_experience", "duration")),
        "exams_count": len(lic.get("exams") or []),
        "renewal_years": _ev_value(_g(lic, "renewal", "interval_years")),
        "ce_hours": _ev_value(_g(lic, "continuing_education", "hours_per_period")),
        "ce_period_years": _ev_value(_g(lic, "continuing_education", "period_years")),
        "reciprocity_available": _ev_value(_g(lic, "reciprocity", "available")),
        "disciplinary_grounds_count": len(lic.get("disciplinary_grounds") or []),
        "evidence_verified": verified,
        "evidence_unverified": unverified,
        "_full": record,
    }


COVERAGE_REASON_LABELS = {
    "no_chapter_located":              "No podiatry chapter found in our scrape",
    "all_sections_dropped_or_repealed":"All sections in the chapter were repealed",
    "extraction_failed":               "LLM extraction failed",
}


def stub_row(state: str, profession: str, reason: str) -> dict:
    return {
        "state": state,
        "coverage_gap": True,
        "coverage_gap_reason": reason,
        "coverage_gap_label": COVERAGE_REASON_LABELS.get(reason, reason),
        "license_required": None,
        "regulatory_model": None,
        "title_protection": None,
        "scope_protection": None,
        "issuing_authority": None,
        "education_degree": None,
        "post_degree_duration": None,
        "exams_count": 0,
        "renewal_years": None,
        "ce_hours": None,
        "ce_period_years": None,
        "reciprocity_available": None,
        "disciplinary_grounds_count": 0,
        "evidence_verified": 0,
        "evidence_unverified": 0,
        "_full": {"state": state, "profession": profession},
    }


def build(profession: str) -> dict:
    structured_dir = STRUCTURED_DIR / profession
    discovered = json.loads((DISCOVERED_DIR / f"{profession}.json").read_text())
    trimmed_dir = TRIMMED_DIR / profession

    have_struct = {p.stem for p in structured_dir.glob("*.json") if not p.stem.startswith("_")}
    trimmed_with_text: dict[str, int] = {}
    chapter_urls_by_state: dict[str, list[str]] = {}
    sections_by_state: dict[str, list[dict]] = {}
    if trimmed_dir.exists():
        for p in trimmed_dir.glob("*.json"):
            if p.stem.startswith("_"):
                continue
            d = json.loads(p.read_text())
            trimmed_with_text[p.stem] = d.get("total_chars", 0)
            chapter_urls_by_state[p.stem] = d.get("chapter_urls", []) or []
            # Section bodies as the LLM saw them — used for "view in context" panel
            sections_by_state[p.stem] = [
                {"url": s.get("url"), "citation": s.get("citation"),
                 "label": s.get("label"), "text": s.get("text")}
                for s in (d.get("sections") or [])
                if s.get("text")
            ]

    rows: list[dict] = []
    for st in ALL_STATES:
        if st in have_struct:
            rec = json.loads((structured_dir / f"{st}.json").read_text())
            row = hoist_row(rec)
            row["source_chapter_urls"] = chapter_urls_by_state.get(st, [])
            row["sections"] = sections_by_state.get(st, [])
            rows.append(row)
        else:
            chars = trimmed_with_text.get(st, 0)
            if st not in trimmed_with_text:
                reason = "no_chapter_located"
            elif chars == 0:
                reason = "all_sections_dropped_or_repealed"
            else:
                reason = "extraction_failed"
            rows.append(stub_row(st, profession, reason))

    # Evidence audit summary (across covered states)
    verified = unverified = 0
    for r in rows:
        if r["coverage_gap"]:
            continue
        for ev in _walk_evidence(r["_full"]):
            if ev.get("unverified"):
                unverified += 1
            else:
                verified += 1

    return {
        "profession": profession,
        "display": _profession_display(profession),
        "discovered_fields": discovered["fields"],
        "rows": rows,
        "evidence_summary": {"verified": verified, "unverified": unverified},
    }


def _profession_display(profession: str) -> str:
    """Pull a friendly display name from config/professions.yaml; fall back to title-case."""
    try:
        import yaml
        from paths import CONFIG_DIR
        cfg = yaml.safe_load((CONFIG_DIR / "professions.yaml").read_text()) or {}
        return cfg.get(profession, {}).get("display", profession.replace("_", " ").title())
    except Exception:
        return profession.replace("_", " ").title()


def _walk_evidence(node: Any):
    if isinstance(node, dict):
        if {"value", "quote", "citation"}.issubset(node.keys()):
            yield node
            return
        for v in node.values():
            yield from _walk_evidence(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk_evidence(v)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    args = ap.parse_args()

    profession = args.profession.lower()
    payload = build(profession)
    body = json.dumps(payload, indent=2)
    url = upload_json(f"data/{profession}.json", body)
    print(f"uploaded data/{profession}.json → {url}")
    summary = {
        "covered": sum(1 for r in payload["rows"] if not r["coverage_gap"]),
        "gaps":    sum(1 for r in payload["rows"] if r["coverage_gap"]),
        "fields":  len(payload["discovered_fields"]),
        "evidence": payload["evidence_summary"],
    }
    print(f"summary: {summary}")


if __name__ == "__main__":
    main()
