"""Regression-check our podiatry extraction against the Westlaw-sourced
human-verified PDF (transcribed into podiatry_pdf_ground_truth.yaml).

For each state in the YAML, compare hand-transcribed values to our extracted
values. Output a markdown report: matches, disagreements (with both sides
shown), and missing values (we extracted nothing).

The human may also be wrong — disagreements should be investigated, not
assumed to be our error.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STRUCTURED_DIR = REPO_ROOT / "pipeline" / "results" / "structured" / "podiatry"
GROUND_TRUTH = REPO_ROOT / "pipeline" / "notes" / "podiatry_pdf_ground_truth.yaml"


def _ev_value(node):
    if isinstance(node, dict) and {"value", "quote", "citation"}.issubset(node.keys()):
        return node["value"]
    return node


def _get(d, *path):
    cur = d
    for k in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _normalize_anatomical(v: str | None) -> str | None:
    """Map our enum values + PDF prose to a coarse comparison bucket."""
    if v is None:
        return None
    v = v.lower().replace("_", " ")
    if "ankle" in v and "above" not in v:
        # foot+ankle-only — no further up
        return "ankle"
    if "lower leg" in v or "midcalf" in v or "myotendinous junction" in v:
        return "lower_leg"
    if "knee" in v:
        return "knee"
    if "tibial" in v and ("tubercle" in v or "tuberosity" in v):
        return "tibial_tuberosity"
    if "metaphyseal" in v or "tibial metaphyseal" in v or "distal tibial" in v:
        return "distal_tibial_metaphyseal_flair"
    return v


_AMPUTATION_AS_BOOL = {
    # Our enum value → coarse boolean meaning for PDF comparison
    "not_authorized": False,
    "foot_entirety_excluded": False,
    "prohibited": False,
    "toes_and_parts_of_foot": True,
    "toes_only": True,
    "chopart_joint_and_below": True,
    "transmetatarsal_and_below": True,
    "below_tibial_tuberosity": True,
    "foot_and_ankle": True,
}


def _to_bool_amputation(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = str(v).lower()
    if s in _AMPUTATION_AS_BOOL:
        return _AMPUTATION_AS_BOOL[s]
    # Heuristic on the string
    if any(t in s for t in ("not_auth", "excluded", "prohibit", "no_amput")):
        return False
    if any(t in s for t in ("authorized", "permitted", "allowed", "and_below", "and_parts")):
        return True
    return None  # unknown encoding


def compare_state(state: str, gt: dict) -> list[dict]:
    """Return a list of {field, gt_value, our_value, status, note} rows."""
    path = STRUCTURED_DIR / f"{state}.json"
    if not path.exists():
        return [{"field": "(no data)", "gt": "—", "ours": "—", "status": "missing_state", "note": ""}]

    rec = json.loads(path.read_text())
    lic = rec.get("licensure") or {}
    ps = rec.get("profession_specific") or {}

    ours = {
        "license_required": _ev_value(lic.get("license_required")),
        "amputation_authorized": _ev_value(ps.get("amputation_authorized")),
        "ankle_surgery_authorized": _ev_value(ps.get("ankle_surgery_authorized")),
        "anatomical_scope_upper_boundary": _ev_value(ps.get("anatomical_scope_upper_boundary")),
    }

    rows = []
    for field, gt_val in gt.items():
        our_val = ours.get(field)
        note = ""

        if our_val is None:
            status = "null"
        elif field == "amputation_authorized":
            # PDF is coarse bool; our enum has rich values. Compare by bool meaning.
            our_bool = _to_bool_amputation(our_val)
            if our_bool == gt_val:
                status = "match" if isinstance(our_val, bool) else "match_precise"
                if status == "match_precise":
                    note = "we have more specific enum value"
            else:
                status = "diff"
        elif field == "anatomical_scope_upper_boundary":
            our_norm = _normalize_anatomical(str(our_val) if our_val else None)
            gt_norm = _normalize_anatomical(str(gt_val) if gt_val else None)
            if our_norm == gt_norm:
                status = "match"
            elif our_norm and gt_norm and our_norm in gt_norm or (gt_norm and our_norm and gt_norm in our_norm):
                status = "match_approx"
                note = "different specificity"
            else:
                status = "diff"
        else:
            status = "match" if our_val == gt_val else "diff"

        rows.append({
            "field": field, "gt": gt_val, "ours": our_val,
            "status": status, "note": note,
        })
    return rows


def main():
    truth = yaml.safe_load(GROUND_TRUTH.read_text())
    states = truth.get("states", {})

    print(f"# Podiatry regression — extraction vs human-verified PDF\n")
    print(f"Comparing {len(states)} hand-transcribed states from the Utah-DPM Westlaw PDF\n")

    by_status: dict[str, int] = {"match": 0, "diff": 0, "null": 0, "missing_state": 0}

    for state, gt in sorted(states.items()):
        rows = compare_state(state, gt)
        print(f"## {state}")
        print()
        print(f"| Field | PDF (ground truth) | Ours | Status |")
        print(f"|---|---|---|---|")
        for r in rows:
            mark = {
                "match": "✓",
                "match_precise": "✓ (more specific)",
                "match_approx": "≈",
                "diff": "⚠ DIFF",
                "null": "∅ NULL",
                "missing_state": "❌",
            }.get(r["status"], "?")
            line = f"| `{r['field']}` | `{r['gt']}` | `{r['ours']}` | {mark}"
            if r.get("note"):
                line += f" — {r['note']}"
            line += " |"
            print(line)
            by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        print()

    print(f"## Summary\n")
    total = sum(by_status.values())
    for k in ("match", "match_precise", "match_approx", "diff", "null", "missing_state"):
        v = by_status.get(k, 0)
        if v == 0:
            continue
        pct = 100 * v / total if total else 0
        print(f"- **{k}**: {v} ({pct:.0f}%)")

    agreeing = by_status.get("match", 0) + by_status.get("match_precise", 0) + by_status.get("match_approx", 0)
    print()
    print(f"**Agreement rate: {agreeing}/{total} = {100*agreeing/total:.0f}%**")


if __name__ == "__main__":
    main()
