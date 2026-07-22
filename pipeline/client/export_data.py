"""Export the data as a single Excel workbook — by OCCUPATION (all states) or by STATE (all
occupations). The download feature's one source of truth: reshapes data already on disk (no
fetch, no LLM) into a three-tab .xlsx a non-coder can open. Build-time pre-generation uploads
these to Blob and the site links them; this module is also runnable directly.

Each workbook has three sheets:
  - "Processed"        — the extracted fields (regulatory_model, license_required, education,
                         the profession-specific scope fields, …). By occupation: one row per
                         state. By state: one row per occupation.
  - "Evidence"         — the raw↔processed link: one row per field with the extracted VALUE plus
                         the verbatim statute QUOTE and CITATION it came from.
  - "Raw statute text" — the actual statute sections (citation, label, full text).

  python -m pipeline.client.export_data --profession optometry
  python -m pipeline.client.export_data --state UT
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from openpyxl import Workbook

from pipeline.paths import TEXT_DIR, STRUCTURED_DIR, PIPELINE_ROOT
from pipeline.config.loaders import all_profession_ids

DATA_DIR = PIPELINE_ROOT / "publish" / "web" / "public" / "data"
EXPORT_DIR = PIPELINE_ROOT / "results" / "exports"
XLSX_CELL_MAX = 32000                       # Excel's hard limit is 32,767 chars/cell
_ILLEGAL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")   # control chars openpyxl rejects
EVIDENCE_COLS = ["field", "value", "quote", "citation"]
RAW_COLS = ["citation", "label", "text"]


def _clean(v):
    """Make a value Excel-safe: JSON-encode nested dict/list, strip illegal control chars,
    truncate over-long statute text."""
    if isinstance(v, (dict, list)):
        v = json.dumps(v, ensure_ascii=False)
    if isinstance(v, str):
        v = _ILLEGAL.sub("", v)
        if len(v) > XLSX_CELL_MAX:
            v = v[:XLSX_CELL_MAX] + "… [truncated]"
    return v


def _cols(rows: list[dict], lead: list[str]) -> list[str]:
    """Ordered column union across `rows`, with `lead` columns pinned to the front."""
    seen = dict.fromkeys(lead)
    for r in rows:
        for k in r:
            seen.setdefault(k, None)
    return list(seen)


def _walk_evidence(node, path: str, out: list[dict]) -> None:
    """Flatten an Evidence-wrapped record to leaf rows (field, value, quote, citation)."""
    if isinstance(node, dict):
        if "value" in node and ("quote" in node or "citation" in node):
            out.append({"field": path, "value": node.get("value"),
                        "quote": node.get("quote", ""), "citation": node.get("citation", "")})
            return
        for k, v in node.items():
            _walk_evidence(v, f"{path}.{k}" if path else k, out)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            _walk_evidence(item, f"{path}[{i}]", out)


def _published_professions() -> list[str]:
    """Professions with a published payload on disk (registry-intersect, so artifacts like
    scorecard/tag_sheet are never treated as professions)."""
    registry = set(all_profession_ids())
    return sorted(f.stem for f in DATA_DIR.glob("*.json") if f.stem in registry)


def _write(sheets: list[tuple[str, list[str], list[dict]]], out_path: Path) -> dict:
    wb = Workbook()
    wb.remove(wb.active)
    counts: dict[str, int] = {}
    for name, cols, rows in sheets:
        ws = wb.create_sheet(name)
        ws.append(cols)
        for r in rows:
            ws.append([_clean(r.get(c)) for c in cols])
        counts[name] = len(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    return {"path": str(out_path), "processed_rows": counts["Processed"],
            "evidence_rows": counts["Evidence"], "raw_sections": counts["Raw statute text"]}


# --- by OCCUPATION (all states) -----------------------------------------------

def export_occupation(prof: str, out_path: Path) -> dict:
    payload_path = DATA_DIR / f"{prof}.json"
    if not payload_path.exists():
        sys.exit(f"no published payload for {prof!r} at {payload_path} — build_frontend it first")
    processed = json.loads(payload_path.read_text()).get("rows") or []

    evidence: list[dict] = []
    raw: list[dict] = []
    for f in sorted((STRUCTURED_DIR / prof).glob("*.json")):
        if not f.stem.startswith("_"):
            d = json.loads(f.read_text())
            st = d.get("state", f.stem)
            leaves: list[dict] = []
            _walk_evidence(d, "", leaves)
            evidence += [{"state": st, **lf} for lf in leaves]
    for f in sorted((TEXT_DIR / prof).glob("*.json")):
        if not f.stem.startswith("_"):
            d = json.loads(f.read_text())
            st = d.get("state", f.stem)
            raw += [{"state": st, "citation": s.get("citation", ""), "label": s.get("label", ""),
                     "text": s.get("text", "")} for s in (d.get("sections") or []) if not s.get("error")]
    return _write([
        ("Processed", _cols(processed, ["state"]), processed),
        ("Evidence", ["state"] + EVIDENCE_COLS, evidence),
        ("Raw statute text", ["state"] + RAW_COLS, raw),
    ], out_path)


# --- by STATE (all published occupations) -------------------------------------

def export_state(state: str, out_path: Path) -> dict:
    st = state.upper()
    processed: list[dict] = []
    evidence: list[dict] = []
    for prof in _published_professions():
        payload = json.loads((DATA_DIR / f"{prof}.json").read_text())
        for row in payload.get("rows") or []:
            if row.get("state") == st:
                processed.append({"profession": prof, **row})
        sfile = STRUCTURED_DIR / prof / f"{st}.json"
        if sfile.exists():
            leaves: list[dict] = []
            _walk_evidence(json.loads(sfile.read_text()), "", leaves)
            evidence += [{"profession": prof, "state": st, **lf} for lf in leaves]

    raw: list[dict] = []
    state_blob = DATA_DIR / "state" / f"{st}.json"
    if state_blob.exists():
        d = json.loads(state_blob.read_text())
        raw = [{"profession": s.get("profession", s.get("audience", "")), "citation": s.get("citation", ""),
                "label": s.get("label", ""), "text": s.get("text", "")} for s in (d.get("sections") or [])]
    if not processed and not raw:
        sys.exit(f"no published data for state {st!r} (no rows in any payload; no data/state/{st}.json)")
    return _write([
        ("Processed", _cols(processed, ["profession", "state"]), processed),
        ("Evidence", ["profession", "state"] + EVIDENCE_COLS, evidence),
        ("Raw statute text", ["profession"] + RAW_COLS, raw),
    ], out_path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--profession", help="one occupation, all states")
    g.add_argument("--state", help="one state, all published occupations")
    ap.add_argument("--out", help="output .xlsx (default: results/exports/<name>.xlsx)")
    args = ap.parse_args()

    if args.profession:
        out = Path(args.out) if args.out else EXPORT_DIR / f"{args.profession}.xlsx"
        r = export_occupation(args.profession, out)
    else:
        out = Path(args.out) if args.out else EXPORT_DIR / f"state_{args.state.upper()}.xlsx"
        r = export_state(args.state, out)
    print(f"wrote {r['path']}  —  Processed: {r['processed_rows']} rows, "
          f"Evidence: {r['evidence_rows']} field-rows, Raw statute text: {r['raw_sections']} sections")


if __name__ == "__main__":
    main()
