"""Build the scope-of-practice capability data the Map tab's Scope view renders.

Scope of practice is multi-dimensional and list/text-valued, so a single choropleth
can't represent it. This emits, per profession, the set of *comparable* scope
capabilities — bucketed scope tags and which states authorize each — so the frontend
can show a capability presence-matrix + per-capability maps, filtered by how widely
shared a capability is (the N knob).

Source: the already-built tag sheet (results-side bucketing of every field's per-state
values) + each profession's discovered-field categories (to keep only genuine scope
fields, dropping license structure / exams / fees / CE / reporting / education, which
are not scope of practice). The single field-selection rule lives in SCOPE_STD_FIELDS +
NON_SCOPE_CATEGORY_MARKERS below — the one place to tune what counts as scope.

Input:  web/public/data/tag_sheet.json  +  results/discovered/<profession>.json
Output: web/public/data/scope_capabilities.json
  { <profession>: { display, capabilities: [ { label, states: [ST, ...] }, ... ] } }
Capabilities are sorted by coverage (most states first).

Run:
  python -m pipeline.publish.build_scope_capabilities
Runs AFTER build_tag_sheet (it reads tag_sheet.json).
"""

from __future__ import annotations

import argparse
import json

from pipeline.paths import DISCOVERED_DIR, WEB_PUBLIC_DIR, core_professions
from pipeline._runlog import record_run

DATA_DIR = WEB_PUBLIC_DIR / "data"
TAG_SHEET = DATA_DIR / "tag_sheet.json"
OUT = DATA_DIR / "scope_capabilities.json"

# --- The field-selection rule (single source of truth) --------------------------
# The two standard-model scope fields are always scope-of-practice.
SCOPE_STD_FIELDS = ("methods_authorized", "drug_authority")
# A discovered profession-specific field is scope UNLESS its category (or name)
# names one of these non-scope concerns — license structure, credentials, admin,
# money, education, reporting, discipline, mobility, penalties.
NON_SCOPE_CATEGORY_MARKERS = (
    "licens", "tier", "role", "credential", "kind of", "type", "exam", "fee", "financ",
    "insur", "suret", "bond", "renew", "continuing", "educat", "school", "program stand",
    "accredit", "compact", "multistate", "impair", "report", "whistle", "applicat",
    "paperwork", "discipl", "enforce", "backgr", "fingerprint", "reciproc", "registry",
    "who a ", "work under", "oversight", "aide", "specialty_certification_types",
    "misdemeanor", "penalt", "fine", "jail", "felony", "residency", "ecfmg", "graduat",
    "postgrad", "jurisdiction", "agent for service", "mobility", "practice privilege",
    "cessation", "complian",
)


def _is_scope_field(field_name: str, category: str | None) -> bool:
    """True if this tag_sheet subfield is a genuine scope-of-practice field."""
    base = field_name.split(".")[-1]
    if field_name.endswith(SCOPE_STD_FIELDS):
        return True
    if category is None:  # not a discovered field (and not a std scope field) → skip
        return False
    hay = f"{category} {base}".lower()
    return not any(m in hay for m in NON_SCOPE_CATEGORY_MARKERS)


def _discovered_categories(profession: str) -> dict[str, str]:
    fp = DISCOVERED_DIR / f"{profession}.json"
    if not fp.exists():
        return {}
    d = json.loads(fp.read_text())
    fields = d.get("fields") or d.get("discovered_fields") or []
    return {f.get("name"): f.get("category") for f in fields if f.get("name")}


def build() -> dict:
    tag_sheet = json.loads(TAG_SHEET.read_text())
    published = set(core_professions())
    out: dict = {}
    for prof in tag_sheet.get("data", []):
        name = prof["profession"]
        if name not in published:
            continue
        cats = _discovered_categories(name)
        caps: list[dict] = []
        for field in prof.get("fields", []):
            for sf in field.get("subfields", []):
                fn = sf.get("field_name", "")
                if not _is_scope_field(fn, cats.get(fn.split(".")[-1])):
                    continue
                by_bucket: dict[str, set[str]] = {}
                for a in sf.get("assignments", []):
                    by_bucket.setdefault(a["bucket"], set()).add(a["state"])
                for tag, states in by_bucket.items():
                    caps.append({"label": tag, "states": sorted(states)})
        caps.sort(key=lambda c: -len(c["states"]))
        out[name] = {"display": _display(name, tag_sheet), "capabilities": caps}
    return out


def _display(profession: str, tag_sheet: dict) -> str:
    # tag_sheet entries don't carry display names; fall back to a humanized id.
    # (build_frontend has the canonical display; the frontend also has professions.json,
    # so this is only a convenience label.)
    return profession.replace("_", " ")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upload", action="store_true",
                    help="Also upload data/scope_capabilities.json to Vercel Blob.")
    args = ap.parse_args()

    data = build()
    payload = json.dumps(data)
    OUT.write_text(payload + "\n")
    n_caps = sum(len(v["capabilities"]) for v in data.values())
    print(f"scope_capabilities: {len(data)} professions, {n_caps} capabilities → {OUT}")
    if args.upload:
        from pipeline.publish.blob_upload import upload_json
        url, skipped = upload_json("data/scope_capabilities.json", payload)
        print(f"{'cached' if skipped else 'uploaded'} → {url}")
    record_run("scope_capabilities", professions=len(data), capabilities=n_caps)


if __name__ == "__main__":
    main()
