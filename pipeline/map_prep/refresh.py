"""Batched + cached refresh of map_prep (spec + apply) AND bucket_text
(per-state + per-item) for multiple professions in two big Anthropic batches.

The sync paths (map_prep.run and bucket_text) are fine for one-off runs;
this module is for periodic full-refreshes across many professions. Costs
~50% less than serial sync (Message Batches 50% discount), plus cache hits
on the system prompts shave another 5-10%.

Why two batches: `map_prep.run` has an internal dependency — pass 2
(`apply_spec`) only runs on fields pass 1 (`build_spec`) marks mappable. So
we can't squash everything into one batch. Layout:

  Batch A: one spec call per profession.
  (wait for A → read spec.fields, decide which fields are mappable vs
   not_mappable per profession, and which list-of-objects fields exist)
  Batch B: apply chunks (mappable fields) + per-state bucket calls
   (not_mappable fields) + per-item bucket calls (list-of-objects fields).

All independent within each batch, so within-batch parallelism is fine.

Usage:
  python -m pipeline.map_prep.refresh --professions all
  python -m pipeline.map_prep.refresh --professions medicine,dentistry
  python -m pipeline.map_prep.refresh --professions medicine --skip-bucket-item
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from _env import load_env  # noqa: E402
load_env()

from _batch import BatchRequest, submit_batch, poll_batch, aggregate_usage  # noqa: E402
from _llm import _system_with_schema  # noqa: E402
from _prompts import load_prompt  # noqa: E402
# Generic "null the failing leaf" recover used as the default for every batch
# call. Same one extract_state uses — guards against LLM drift returning a
# value out of a Literal set or null where the schema expects a type.
from extract.extract_state import _recover_invalid_fields  # noqa: E402

# Reuse the existing scripts' Pydantic models + helper functions
from map_prep.run import (  # noqa: E402
    SpecResult, ApplyResult, NormalizedRow,
    _load_profession, _field_index,
    APPLY_CHUNK_SIZE,
)
from map_prep.bucket_text import (  # noqa: E402
    FieldBuckets, _collect_per_state,
    run_profession_per_item, run_profession_list_fields, _DEFAULT_PER_ITEM_FIELD,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("map_prep.refresh")

MODEL = "claude-sonnet-4-6"
from paths import MAP_PREP_DIR as _OUT_ROOT, DISCOVERED_DIR as _DISCOVERED_DIR  # noqa: E402


# Anthropic batch custom_id pattern is ^[a-zA-Z0-9_-]{1,64}$ — no dots allowed,
# 64-char cap. We encode field dotted-paths to a short stable index per profession
# and keep the field-name lookup separate.

_FIELD_INDEX: dict[tuple[str, str], int] = {}  # (profession, field) → small int


def _field_idx(prof: str, field: str) -> int:
    key = (prof, field)
    if key not in _FIELD_INDEX:
        _FIELD_INDEX[key] = len([k for k in _FIELD_INDEX if k[0] == prof])
    return _FIELD_INDEX[key]


def _cid_spec(prof: str) -> str:
    return f"{prof}__spec"


def _cid_apply(prof: str, chunk_i: int) -> str:
    return f"{prof}__apply_{chunk_i}"


def _cid_bucket_state(prof: str, field: str) -> str:
    return f"{prof}__bks_{_field_idx(prof, field)}"


# ---------- Stage A: spec ----------

def stage_a_spec(
    professions: list[str], reuse_existing: bool = True,
) -> tuple[dict[str, SpecResult], dict[str, dict], dict]:
    """Build spec requests for each profession, submit as one batch, return parsed results.

    If reuse_existing=True (default), professions with an on-disk spec.json
    are read from disk and skipped from the batch — avoids re-paying for
    Stage A when only Stage B failed previously.
    """
    spec_sys = load_prompt("map_prep_spec")
    sys_text = _system_with_schema(spec_sys, SpecResult)

    specs: dict[str, SpecResult] = {}
    per_field_by_prof: dict[str, dict] = {}
    reqs = []

    for prof in professions:
        per_state = _load_profession(prof)
        per_field = _field_index(per_state)
        per_field_by_prof[prof] = per_field

        spec_path = _OUT_ROOT / prof / "spec.json"
        if reuse_existing and spec_path.exists():
            specs[prof] = SpecResult.model_validate_json(spec_path.read_text())
            log.info("[%s] reusing existing spec.json (%d fields, %d mappable)",
                     prof, len(specs[prof].fields),
                     sum(1 for s in specs[prof].fields if s.mappable))
            continue

        user = json.dumps({"profession": prof, "fields": per_field}, ensure_ascii=False)
        reqs.append(BatchRequest(
            custom_id=_cid_spec(prof),
            system=sys_text,
            user=user,
            schema_cls=SpecResult,
            max_tokens=16000,
        ))

    if not reqs:
        log.info("Stage A: all specs already on disk — skipping batch")
        return specs, per_field_by_prof, {"cost_usd": 0, "sync_no_cache_baseline_usd": 0, "saved_pct": 0}

    log.info("=== Stage A: %d spec calls ===", len(reqs))
    schema_map = {r.custom_id: r.schema_cls for r in reqs}
    recover_map = {r.custom_id: _recover_invalid_fields for r in reqs}
    batch_id = submit_batch(reqs, MODEL)
    results = poll_batch(batch_id, schema_map, recover_by_custom_id=recover_map)

    for prof in professions:
        if prof in specs:  # reused from disk
            continue
        r = results.get(_cid_spec(prof))
        if r is None or r.parsed is None:
            log.error("[%s] spec call failed: %s", prof, r.error if r else "no result")
            continue
        specs[prof] = r.parsed
        out_dir = _OUT_ROOT / prof
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "spec.json").write_text(r.parsed.model_dump_json(indent=2))
        log.info("[%s] wrote spec.json (%d fields, %d mappable)",
                 prof, len(r.parsed.fields), sum(1 for s in r.parsed.fields if s.mappable))

    return specs, per_field_by_prof, aggregate_usage(results)


# ---------- Stage B: apply + per-state + per-item, all in one batch ----------

def stage_b_apply_and_bucket(
    professions: list[str],
    specs: dict[str, SpecResult],
    per_field_by_prof: dict[str, dict],
    do_per_item: bool = True,
) -> dict:
    """Build all post-spec calls (apply chunks + bucket per-state + bucket per-item),
    submit as one batch, parse results, write to disk."""

    apply_sys = _system_with_schema(load_prompt("map_prep_apply"), ApplyResult)
    bucket_state_sys = _system_with_schema(load_prompt("map_prep_bucket_text"), FieldBuckets)

    reqs: list[BatchRequest] = []
    chunks_by_prof: dict[str, int] = {}
    bucket_state_fields_by_prof: dict[str, list[str]] = {}

    for prof in professions:
        spec = specs.get(prof)
        if spec is None:
            log.warning("[%s] no spec — skipping in Stage B", prof)
            continue
        per_field = per_field_by_prof[prof]

        # --- apply (categorical / continuous normalization) ---
        mappable = [s for s in spec.fields if s.mappable and s.kind != "not_mappable"]
        for i in range(0, len(mappable), APPLY_CHUNK_SIZE):
            chunk = mappable[i : i + APPLY_CHUNK_SIZE]
            chunk_names = {s.field_name for s in chunk}
            trimmed = {fn: per_field[fn] for fn in chunk_names if fn in per_field}
            payload = {
                "profession": prof,
                "spec": [s.model_dump() for s in chunk],
                "raw_values": trimmed,
            }
            user = json.dumps(payload, ensure_ascii=False)
            chunk_i = i // APPLY_CHUNK_SIZE + 1
            reqs.append(BatchRequest(
                custom_id=_cid_apply(prof, chunk_i),
                system=apply_sys,
                user=user,
                schema_cls=ApplyResult,
                max_tokens=32000,
            ))
        chunks_by_prof[prof] = (len(mappable) + APPLY_CHUNK_SIZE - 1) // APPLY_CHUNK_SIZE

        # --- per-state bucket calls (not_mappable free-text fields) ---
        not_mappable = [s.field_name for s in spec.fields if s.kind == "not_mappable"]
        bucket_state_fields_by_prof[prof] = not_mappable
        for dotted in not_mappable:
            raw = _collect_per_state(prof, dotted)
            if len(raw) < 2:
                continue  # mirrors bucket_text's skip rule
            user = json.dumps({
                "profession": prof,
                "field_name": dotted,
                "per_state_raw_values": raw,
            }, ensure_ascii=False)
            reqs.append(BatchRequest(
                custom_id=_cid_bucket_state(prof, dotted),
                system=bucket_state_sys,
                user=user,
                schema_cls=FieldBuckets,
                max_tokens=4000,
            ))

    if not reqs:
        log.info("Stage B: no requests to submit")
        return {"cost_usd": 0, "sync_no_cache_baseline_usd": 0, "saved_pct": 0}

    log.info("=== Stage B: %d requests ===", len(reqs))
    schema_map = {r.custom_id: r.schema_cls for r in reqs}
    recover_map = {r.custom_id: _recover_invalid_fields for r in reqs}
    batch_id = submit_batch(reqs, MODEL)
    results = poll_batch(batch_id, schema_map, recover_by_custom_id=recover_map)

    # ---- Apply results to disk per profession ----
    # 1. apply chunks → assemble per profession's normalized.json
    # 2. bucket per-state → text_buckets.json per profession
    # (per-item bucketing is delegated to bucket_text after this loop)
    for prof in professions:
        if prof not in specs:
            continue
        out_dir = _OUT_ROOT / prof
        out_dir.mkdir(parents=True, exist_ok=True)

        # apply
        all_rows: list[NormalizedRow] = []
        n_chunks = chunks_by_prof.get(prof, 0)
        any_apply_failed = False
        for i in range(1, n_chunks + 1):
            r = results.get(_cid_apply(prof, i))
            if r is None or r.parsed is None:
                log.error("[%s] apply chunk %d failed: %s", prof, i, r.error if r else "missing")
                any_apply_failed = True
                continue
            all_rows.extend(r.parsed.rows)
        if not any_apply_failed:
            applied = ApplyResult(profession=prof, rows=all_rows)
            (out_dir / "normalized.json").write_text(applied.model_dump_json(indent=2))
            log.info("[%s] wrote normalized.json (%d rows)", prof, len(all_rows))

        # bucket per-state
        field_results: list[FieldBuckets] = []
        for dotted in bucket_state_fields_by_prof.get(prof, []):
            cid = _cid_bucket_state(prof, dotted)
            r = results.get(cid)
            if r is None or r.parsed is None:
                continue  # was a skip or failure; bucket_text would have skipped too
            field_results.append(r.parsed)
        if field_results:
            (out_dir / "text_buckets.json").write_text(json.dumps({
                "profession": prof,
                "fields": [fb.model_dump() for fb in field_results],
            }, indent=2, ensure_ascii=False))
            log.info("[%s] wrote text_buckets.json (%d fields)", prof, len(field_results))

    # Per-item bucketing (list-of-objects fields) runs through the canonical
    # two-stage design→assign implementation in bucket_text — NOT a duplicated
    # single-call batch path. That duplication is exactly what drifted and broke:
    # it called prompt key `map_prep_bucket_text_per_item`, which the sync path
    # long ago split into `_design`/`_assign` and removed. Delegating keeps one
    # source of truth (and buckets every discovered list field, not just a fixed
    # list). Sync, but per-item assign is already chunked into small calls —
    # correctness over the marginal batch discount on this one stage.
    if do_per_item:
        for prof in professions:
            if prof not in specs:
                continue
            # Standard list field (disciplinary_grounds) + every discovered
            # profession_specific list field. Both are needed: discovered_list_fields
            # only returns profession_specific.* paths, so the standard field must be
            # bucketed explicitly (this is the pairing bucket_text's CLI exposes as
            # `--per-item` + `--list-fields`).
            run_profession_per_item(prof, _DEFAULT_PER_ITEM_FIELD)
            run_profession_list_fields(prof)

    return aggregate_usage(results)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--professions", required=True,
                    help="'all' or a comma-separated list of profession names")
    ap.add_argument("--skip-bucket-item", action="store_true",
                    help="Skip per-item bucketing (list-of-objects fields). Cheaper test runs.")
    args = ap.parse_args()

    if args.professions == "all":
        professions = sorted([d.name for d in _DISCOVERED_DIR.iterdir() if d.is_file() and d.name.endswith(".json")])
        professions = [p[:-5] for p in professions]  # strip .json
    else:
        professions = [p.strip() for p in args.professions.split(",") if p.strip()]

    log.info("refreshing %d professions: %s", len(professions), professions)

    specs, per_field_by_prof, usage_a = stage_a_spec(professions)
    log.info("Stage A cost: $%.4f (vs $%.4f sync, saved %.1f%%)",
             usage_a["cost_usd"], usage_a["sync_no_cache_baseline_usd"], usage_a["saved_pct"])

    usage_b = stage_b_apply_and_bucket(
        professions, specs, per_field_by_prof, do_per_item=not args.skip_bucket_item
    )
    log.info("Stage B cost: $%.4f (vs $%.4f sync, saved %.1f%%)",
             usage_b["cost_usd"], usage_b["sync_no_cache_baseline_usd"], usage_b["saved_pct"])

    total = usage_a["cost_usd"] + usage_b["cost_usd"]
    baseline = usage_a["sync_no_cache_baseline_usd"] + usage_b["sync_no_cache_baseline_usd"]
    log.info("=== TOTAL refresh cost: $%.4f (vs $%.4f sync, saved $%.4f / %.1f%%) ===",
             total, baseline, baseline - total,
             100 * (baseline - total) / max(baseline, 0.0001))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
