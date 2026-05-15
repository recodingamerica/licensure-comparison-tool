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
from paths import STRUCTURED_DIR, DISCOVERED_DIR, TRIMMED_DIR, RESULTS_DIR  # noqa: E402
from config.states import ALL_STATES  # noqa: E402
from extract.locate_quote import locate_quote_in_section  # noqa: E402
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


def _annotate_quote_spans(record: dict, sections: list[dict]) -> tuple[int, int]:
    """For each verified Evidence node, find the cited section's text and
    attach `quote_spans`: a list of (start, end) char offsets into that
    same `text` field the frontend will render. The UI then slices
    directly — no re-derived regex, no Python-vs-TS parity drift.

    The lookup mirrors evidence-row.tsx: try the raw citation, then the
    bracket-stripped form. Unverified nodes are skipped (highlight would
    be misleading), and nodes whose citation we can't pin to a single
    section are left without spans (verifier may still have accepted them
    via the combined chapter+umbrella corpus — see STATUS.md's
    corpus-boundary case; UI shows the quote without a highlight).

    Returns (with_spans, without_spans) across verified nodes.
    """
    by_cite: dict[str, dict] = {}
    for s in sections:
        cite = s.get("citation") or ""
        if not cite:
            continue
        by_cite[cite] = s
        by_cite[f"[{cite}]"] = s

    with_spans = without_spans = 0

    def walk(node: Any):
        nonlocal with_spans, without_spans
        if isinstance(node, dict):
            if {"value", "quote", "citation"}.issubset(node.keys()):
                if not node.get("unverified"):
                    cite = node.get("citation") or ""
                    sec = by_cite.get(cite) or by_cite.get(cite.strip("[]"))
                    text = (sec or {}).get("text") or ""
                    spans = (
                        locate_quote_in_section(node.get("quote") or "", text)
                        if text
                        else None
                    )
                    if spans:
                        # Pydantic dumps tuples as lists already; be explicit
                        # so JSON output is `[[s, e], ...]` either way.
                        node["quote_spans"] = [list(p) for p in spans]
                        with_spans += 1
                    else:
                        without_spans += 1
                return
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(record)
    return with_spans, without_spans


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


def _derive_credential_and_mandatory(lic: dict) -> tuple[str | None, bool | None]:
    """Decompose the legacy single-axis regulatory_model rung into the two
    orthogonal axes the meeting Q1 asked for. If credential_type / is_mandatory
    were extracted directly (newer runs), prefer those; otherwise derive from
    regulatory_model.

    Returns (credential_type_value, is_mandatory_value), each may be None.
    """
    direct_ct = _ev_value(lic.get("credential_type"))
    direct_im = _ev_value(lic.get("is_mandatory"))
    if direct_ct is not None or direct_im is not None:
        return direct_ct, direct_im

    rm_val = _ev_value(lic.get("regulatory_model"))
    if rm_val is None:
        return None, None
    try:
        from pipeline.extract.standard_model import RegulatoryModel, decompose_regulatory_model
        rung = RegulatoryModel(rm_val) if not isinstance(rm_val, RegulatoryModel) else rm_val
        ct, im = decompose_regulatory_model(rung)
        return ct.value, im
    except (ValueError, KeyError):
        return None, None


def hoist_row(record: dict) -> dict:
    """Universal columns. Profession-specific dimensions live in the modal."""
    lic = record.get("licensure") or {}
    verified, unverified = _count_evidence(record)
    credential_type, is_mandatory = _derive_credential_and_mandatory(lic)
    return {
        "state": record["state"],
        "coverage_gap": False,
        "license_required": _ev_value(lic.get("license_required")),
        "regulatory_model": _ev_value(lic.get("regulatory_model")),
        "credential_type": credential_type,
        "is_mandatory": is_mandatory,
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
        "credential_type": None,
        "is_mandatory": None,
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

    umbrella_text_dir = RESULTS_DIR / "umbrella_text"

    if trimmed_dir.exists():
        for p in trimmed_dir.glob("*.json"):
            if p.stem.startswith("_"):
                continue
            d = json.loads(p.read_text())
            trimmed_with_text[p.stem] = d.get("total_chars", 0)
            chapter_urls_by_state[p.stem] = d.get("chapter_urls", []) or []
            # Section bodies as the LLM saw them — used for "view in context" panel
            section_list = [
                {"url": s.get("url"), "citation": s.get("citation"),
                 "label": s.get("label"), "text": s.get("text")}
                for s in (d.get("sections") or [])
                if s.get("text")
            ]
            # ALSO include umbrella sections so the UI can highlight quotes the
            # extractor drew from umbrella context. Multiple umbrella section
            # bodies share the same "UMBRELLA / <chapter_label>" citation prefix
            # (that's how extract_state.load_umbrella_text labels them), so
            # concatenate their text under a single ref per chapter.
            umb_path = umbrella_text_dir / f"{p.stem}.json"
            if umb_path.exists():
                umb = json.loads(umb_path.read_text())
                by_chap: dict[str, dict] = {}
                for s in umb.get("sections", []):
                    if not s.get("text"):
                        continue
                    chap_label = (s.get("umbrella_chapter_label") or "")[:60]
                    cite = f"UMBRELLA / {chap_label}"
                    if cite not in by_chap:
                        by_chap[cite] = {
                            "url": s.get("url"),  # first section's URL
                            "citation": cite,
                            "label": f"umbrella context — {chap_label}",
                            "text": s.get("text") or "",
                        }
                    else:
                        by_chap[cite]["text"] += "\n" + (s.get("text") or "")
                section_list.extend(by_chap.values())
            sections_by_state[p.stem] = section_list

    rows: list[dict] = []
    span_with = span_without = 0
    for st in ALL_STATES:
        if st in have_struct:
            rec = json.loads((structured_dir / f"{st}.json").read_text())
            row = hoist_row(rec)
            row["source_chapter_urls"] = chapter_urls_by_state.get(st, [])
            row["sections"] = sections_by_state.get(st, [])
            # Attach highlight spans now, against the EXACT section text we're
            # about to publish. Computing on this side (rather than during
            # extract/reverify) avoids any normalization drift between the
            # text the verifier saw and the text the UI will slice.
            w, wo = _annotate_quote_spans(row["_full"], row["sections"])
            span_with += w
            span_without += wo
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

    structured_by_state = {
        r["state"]: r["_full"] for r in rows if not r["coverage_gap"]
    }
    map_prep = _load_map_prep(profession, structured_by_state)

    return {
        "profession": profession,
        "display": _profession_display(profession),
        "discovered_fields": discovered["fields"],
        "rows": rows,
        "map_prep": map_prep,
        "evidence_summary": {
            "verified": verified,
            "unverified": unverified,
            # How many verified nodes got per-section highlight spans
            # vs. only verified against the combined corpus. The latter
            # show in the UI without a yellow highlight.
            "with_quote_spans": span_with,
            "without_quote_spans": span_without,
        },
    }


def _resolve_evidence(record: dict, dotted: str) -> dict | None:
    """Walk a structured record by dotted path and return the Evidence node
    ({value, quote, citation, ...}) sitting at that path, if any.

    Used to enrich map_prep rows with the verbatim statute quote — the
    normalizer only saw `.value`, so the quote lives on the original record.
    """
    parts = dotted.split(".")
    node: Any = record
    for p in parts:
        if not isinstance(node, dict):
            return None
        node = node.get(p)
    if isinstance(node, dict) and {"value", "quote", "citation"}.issubset(node.keys()):
        return node
    return None


def _load_map_prep(profession: str, structured_by_state: dict[str, dict]) -> dict | None:
    """Attach the choropleth normalization output (pipeline/map_prep/run.py)
    so the UI can render maps without re-doing the normalization client-side.
    Also enrich each row with the verbatim statute quote + citation pulled
    from the structured record, so the map tooltip can show the source text.

    Returns {"spec": [...mappable FieldSpec...], "rows": [...NormalizedRow+quote...]}
    or None if map_prep hasn't been run for this profession yet.
    """
    src = RESULTS_DIR / "map_prep" / profession
    spec_path = src / "spec.json"
    rows_path = src / "normalized.json"
    if not (spec_path.exists() and rows_path.exists()):
        return None
    spec = json.loads(spec_path.read_text())
    rows = json.loads(rows_path.read_text())
    # Only ship mappable specs to the UI; not_mappable fields are noise here.
    mappable = [f for f in spec.get("fields", []) if f.get("mappable")]

    enriched_rows: list[dict] = []
    for r in rows.get("rows", []):
        rec = structured_by_state.get(r.get("state"))
        if rec:
            ev = _resolve_evidence(rec, r.get("field_name", ""))
            if ev:
                r = {**r, "quote": ev.get("quote"), "citation": ev.get("citation")}
        enriched_rows.append(r)
    return {"spec": mappable, "rows": enriched_rows}


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
    ap.add_argument("--deploy", action="store_true",
                    help="After uploading to blob, redeploy the Vercel project so the live site picks up the new data.")
    args = ap.parse_args()

    profession = args.profession.lower()
    payload = build(profession)
    body = json.dumps(payload, indent=2)
    # Mirror to public/data/ so downstream tooling (state_similarity, review CSV)
    # sees the same data the live site does, without round-tripping Vercel Blob.
    local_path = Path(__file__).resolve().parent / "web" / "public" / "data" / f"{profession}.json"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(body)
    print(f"wrote {local_path}")
    url = upload_json(f"data/{profession}.json", body)
    print(f"uploaded data/{profession}.json → {url}")
    summary = {
        "covered": sum(1 for r in payload["rows"] if not r["coverage_gap"]),
        "gaps":    sum(1 for r in payload["rows"] if r["coverage_gap"]),
        "fields":  len(payload["discovered_fields"]),
        "evidence": payload["evidence_summary"],
    }
    print(f"summary: {summary}")

    if args.deploy:
        import subprocess
        web_dir = Path(__file__).resolve().parent / "web"
        print(f"deploying via vercel --prod from {web_dir}")
        r = subprocess.run(["npx", "vercel", "--prod", "--yes"], cwd=web_dir)
        if r.returncode != 0:
            sys.exit(f"vercel deploy failed (exit {r.returncode})")
        print("deployed")


if __name__ == "__main__":
    main()
