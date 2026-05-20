"""One-off: re-extract a small sample of states on Haiku and diff the new
universal-field density against the on-disk Sonnet output.

The decision we're making: "does Haiku populate the schema-aligned fields
(advisory_board, national_certification, national_association, renewal_fee_usd,
Exam.jurisdiction, Exam.permitted_attempts) reliably enough to use it for the
other 5 professions' bulk re-extraction, or do we need Sonnet for those too?"

This script runs Haiku in memory only (no disk writes) and prints a side-by-side
field-fill density comparison so we can answer that without overwriting the
Sonnet output that's already on disk.

Usage:
  python -m pipeline.extract.compare_models_new_fields --profession podiatry \\
      --states AK,AL,CA,CO,FL
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Make sibling modules + pipeline.paths importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extract_state import (  # noqa: E402
    SYSTEM_PROMPT,
    build_profile_model,
    build_state_text,
    call_model,
    load_umbrella_text,
)
from paths import DISCOVERED_DIR, STRUCTURED_DIR, TRIMMED_DIR  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("compare_models")

HAIKU = "claude-haiku-4-5-20251001"

# The fields we added to LicensureRequirements for schema alignment with the
# universal-comparison list. Each entry is (display_name, accessor) where
# accessor(licensure_dict) returns a populated/empty signal.
NEW_FIELDS = [
    ("advisory_board.exists", lambda lic: (lic.get("advisory_board") or {}).get("exists")),
    ("advisory_board.name", lambda lic: (lic.get("advisory_board") or {}).get("name")),
    ("advisory_board.authority", lambda lic: (lic.get("advisory_board") or {}).get("authority")),
    ("renewal_fee_usd", lambda lic: lic.get("renewal_fee_usd")),
    ("national_certification", lambda lic: lic.get("national_certification")),
    ("national_association", lambda lic: lic.get("national_association")),
]


def is_populated(node: Any) -> bool:
    """Evidence-wrapped fields are populated iff value is non-null."""
    if node is None:
        return False
    if isinstance(node, dict):
        return node.get("value") is not None
    return bool(node)


def exam_field_populated(record: dict, field: str) -> int:
    """Count how many exams in the record have `field` populated."""
    exams = (record.get("licensure") or {}).get("exams") or []
    return sum(1 for e in exams if e.get(field) is not None)


def summarize_fields(record: dict) -> dict[str, Any]:
    lic = record.get("licensure") or {}
    out = {}
    for name, accessor in NEW_FIELDS:
        out[name] = is_populated(accessor(lic))
    out["exam.jurisdiction(any)"] = exam_field_populated(record, "jurisdiction") > 0
    out["exam.permitted_attempts(any)"] = exam_field_populated(record, "permitted_attempts") > 0
    return out


def extract_state_in_memory(state: str, profession: str, model: str, profile_cls) -> dict | None:
    """Mirrors extract_state.extract_one but skips the disk write and the
    annotate_evidence step (we only care about field fill density here)."""
    in_path = TRIMMED_DIR / profession / f"{state}.json"
    raw = json.loads(in_path.read_text())
    if not raw.get("sections"):
        return None
    state_text = build_state_text(raw)
    umbrella_text = load_umbrella_text(state, profession)
    if umbrella_text:
        user_msg = (
            f"State: {state}\nProfession: {profession}\n\n"
            f"Practice act text (extract values from here primarily):\n{state_text}\n\n"
            f"=== Cross-cutting umbrella context (definitions, board rules, "
            f"licensing procedures that apply to this profession too) ===\n"
            f"{umbrella_text}"
        )
    else:
        user_msg = f"State: {state}\nProfession: {profession}\n\nTrimmed statute text:\n{state_text}"
    result = call_model(model, SYSTEM_PROMPT, user_msg, profile_cls)
    return None if result is None else result.model_dump()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profession", required=True)
    ap.add_argument("--states", required=True, help="Comma-separated, e.g. 'AK,AL,CA'")
    args = ap.parse_args()

    profession = args.profession.lower()
    states = [s.strip().upper() for s in args.states.split(",") if s.strip()]

    discovered = json.loads((DISCOVERED_DIR / f"{profession}.json").read_text())
    profile_cls = build_profile_model(profession, discovered)

    sonnet_dir = STRUCTURED_DIR / profession
    rows = []
    for state in states:
        sonnet_path = sonnet_dir / f"{state}.json"
        if not sonnet_path.exists():
            log.warning("[%s] no Sonnet output on disk — skipping", state)
            continue
        sonnet_rec = json.loads(sonnet_path.read_text())
        log.info("[%s] running Haiku…", state)
        haiku_rec = extract_state_in_memory(state, profession, HAIKU, profile_cls)
        if haiku_rec is None:
            log.warning("[%s] Haiku call failed", state)
            continue
        rows.append({
            "state": state,
            "sonnet": summarize_fields(sonnet_rec),
            "haiku": summarize_fields(haiku_rec),
        })

    if not rows:
        sys.exit("no comparisons completed")

    # Pretty per-field summary: how many states each model populated the field for.
    field_names = list(rows[0]["sonnet"].keys())
    print()
    print(f"{'field':45s}  {'Sonnet':>8s}  {'Haiku':>8s}  parity")
    print("-" * 75)
    for f in field_names:
        s = sum(1 for r in rows if r["sonnet"][f])
        h = sum(1 for r in rows if r["haiku"][f])
        parity = f"{(h/s*100):.0f}%" if s else "n/a"
        print(f"{f:45s}  {s:>4d}/{len(rows):>3d}  {h:>4d}/{len(rows):>3d}  {parity}")

    print()
    print("Per-state (1 = populated, 0 = null):")
    print(f"{'state':6s}  " + "  ".join(f"{n[:12]:>12s}" for n in field_names))
    for r in rows:
        sonnet_row = "  ".join(f"{'1' if r['sonnet'][f] else '0':>12s}" for f in field_names)
        haiku_row =  "  ".join(f"{'1' if r['haiku'][f] else '0':>12s}" for f in field_names)
        print(f"{r['state']:6s}  S:")
        print(f"        {sonnet_row}")
        print(f"        H:")
        print(f"        {haiku_row}")


if __name__ == "__main__":
    main()
