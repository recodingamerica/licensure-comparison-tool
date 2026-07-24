"""Build the three-state scope MATRICES the Scope tab renders above the
capability presence-matrix.

Unlike scope_capabilities.json (a binary present/absent view bucketed from the
tag sheet), this carries the richer discover→per-state matrices produced by
pipeline.discover.scope_vocab + the scope__* fields in the structured records:
for a corpus-discovered vocabulary of a scope dimension (e.g. optometry laser
procedures), each state is authorized / prohibited / not_addressed per item. The
prohibited vs not_addressed distinction is exactly what the binary capability
view can't show.

Input:  results/scope_vocab/<profession>.json  (which dimensions + vocab)
        results/structured/<profession>/<STATE>.json  (the scope__* matrices)
Output: web/public/data/scope_matrices.json
  { <profession>: { display, dimensions: [
      { source_field, label, eval_flavor, vocab: [...],
        matrix: { <ST>: { <item>: "authorized"|"prohibited"|"not_addressed" } } } ] } }

Only professions that have a scope_vocab file appear. Runs AFTER extract (reads
structured records); order-independent of build_scope_capabilities.

Run:
  python -m pipeline.publish.build_scope_matrices [--upload]
"""

from __future__ import annotations

import argparse
import json

from pipeline._records import record_files
from pipeline._runlog import record_run
from pipeline.paths import SCOPE_VOCAB_DIR, STRUCTURED_DIR, WEB_PUBLIC_DIR

DATA_DIR = WEB_PUBLIC_DIR / "data"
OUT = DATA_DIR / "scope_matrices.json"


def _label(source_field: str) -> str:
    """Humanize a source field name into a short tab label."""
    base = source_field
    for suffix in ("_authorized", "_permitted", "_allowed"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    base = base.replace("_", " ").strip()
    return base[:1].upper() + base[1:] if base else source_field


def _profession_display(profession: str) -> str:
    return profession.replace("_", " ").title()


def _dimension_matrix(profession: str, dim: dict) -> dict:
    """Per-state item→status map for one scope dimension, read from the
    structured records' scope__<dim> field. States with no record are omitted."""
    fld, vocab = dim["matrix_field"], dim["vocab"]
    vocab_set = set(vocab)
    matrix: dict[str, dict[str, str]] = {}
    prof_dir = STRUCTURED_DIR / profession
    for f in record_files(prof_dir):
        rec = json.loads(f.read_text())
        if not isinstance(rec, dict):
            continue
        state = rec.get("state") or f.stem
        items = (rec.get("profession_specific") or {}).get(fld)
        if not isinstance(items, list) or not items:
            continue  # state not re-extracted with scope matrices — omit (no false silence)
        row = {it["item"]: it.get("status") for it in items
               if isinstance(it, dict) and it.get("item") in vocab_set}
        if row:
            matrix[state] = row
    return matrix


def build() -> dict:
    out: dict = {}
    for path in sorted(SCOPE_VOCAB_DIR.glob("*.json")):
        profession = path.stem
        dims = json.loads(path.read_text()).get("dimensions", [])
        rendered = []
        for dim in dims:
            matrix = _dimension_matrix(profession, dim)
            if not matrix:
                continue
            rendered.append({
                "source_field": dim["source_field"],
                "label": _label(dim["source_field"]),
                "eval_flavor": dim["eval_flavor"],
                "vocab": dim["vocab"],
                "matrix": matrix,
            })
        if rendered:
            out[profession] = {"display": _profession_display(profession), "dimensions": rendered}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--upload", action="store_true",
                    help="Also upload data/scope_matrices.json to Vercel Blob.")
    args = ap.parse_args()

    data = build()
    payload = json.dumps(data)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(payload + "\n")
    n_dims = sum(len(v["dimensions"]) for v in data.values())
    print(f"scope_matrices: {len(data)} professions, {n_dims} dimensions → {OUT}")
    if args.upload:
        from pipeline.publish.blob_upload import upload_json
        url, skipped = upload_json("data/scope_matrices.json", payload)
        print(f"{'cached' if skipped else 'uploaded'} → {url}")
    record_run("scope_matrices", professions=len(data), dimensions=n_dims)


if __name__ == "__main__":
    main()
