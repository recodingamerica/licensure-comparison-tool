"""Pass 3 — bucket the FREE-TEXT fields that the original `map_prep` pass
left `not_mappable`.

Pass 1 of map_prep.run decides each field is continuous / categorical /
not_mappable. Categorical + continuous fields are normalized for the
choropleth. not_mappable fields (free-text idiosyncratic prose like
"education.degree_required" or "issuing_authority") got skipped — which
makes the per-state table cells unreadable: 50 distinct walls of statute
text in a column with no cross-state pattern.

This pass relaxes the bucketing constraint. We don't need a perfectly
comparable scale — we just need a loose categorization so the user can
scan the column and group similar states at a glance. Output buckets
are usually 3-7 labels per field, derived from the actual values seen.

Output: pipeline/results/map_prep/<profession>/text_buckets.json
Shape:
    {
      "profession": "podiatry",
      "fields": [
         {
           "field_name": "licensure.education.degree_required",
           "bucket_set": ["Doctor of Podiatric Medicine", "DPM or equivalent", "..."],
           "rationale": "Most states say DPM; a few use broader 'medical degree' phrasing.",
           "assignments": [
             {"state": "AL", "raw_value": "Doctor of Podiatry from...", "bucket": "Doctor of Podiatric Medicine"},
             ...
           ]
         },
         ...
      ]
    }

Per-item path (--per-item):
    For list-of-objects fields like `licensure.disciplinary_grounds` the
    default per-state path collapses a state's whole list into one bucket
    label, which loses signal — e.g. "does this state include a fraud
    ground?" can't be answered. The --per-item path fans out one row per
    item and assigns a bucket per (state, item_index). Output goes to a
    sibling file `text_buckets_per_item.json` so the per-state file and
    its downstream consumers stay intact.

Run:
    python -m pipeline.map_prep.bucket_text podiatry
    python -m pipeline.map_prep.bucket_text --all
    python -m pipeline.map_prep.bucket_text podiatry --per-item
    python -m pipeline.map_prep.bucket_text --all --per-item
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Same path setup pattern as run.py
_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from _env import load_env  # noqa: E402
from _llm import call_structured  # noqa: E402
from _prompts import load_prompt  # noqa: E402

load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bucket_text")

_OUT_ROOT = _PIPELINE_DIR / "results" / "map_prep"
_STRUCTURED_DIR = _PIPELINE_DIR / "results" / "structured"
_DISCOVERED_DIR = _PIPELINE_DIR / "results" / "discovered"


def discovered_list_fields(profession: str) -> list[str]:
    """Dotted paths of every `list[...]`-typed profession-specific field the
    discovery stage found for this profession (e.g.
    `profession_specific.laser_procedures_authorized`).

    These are structurally identical to `licensure.disciplinary_grounds` — a
    per-state list whose elements we can cluster into plain-English tags — so
    the per-item bucketer runs over all of them, not just discipline. This is
    what makes the tagging general instead of one field at a time.
    """
    path = _DISCOVERED_DIR / f"{profession}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    fields = data.get("fields") if isinstance(data, dict) else data
    out: list[str] = []
    for f in fields or []:
        name = f.get("name") or f.get("field_name")
        ftype = (f.get("type") or f.get("kind") or "")
        if name and ftype.startswith("list"):
            out.append(f"profession_specific.{name}")
    return out

MODEL = "claude-sonnet-4-6"

# Per-item path currently does both vocabulary DESIGN and per-row assignment
# in one call. Sonnet is required for the design quality (Haiku produced a
# weaker vocabulary in side-by-side: collapsed Drug Prescribing into
# Negligence, named impairment "Health & Fitness"). When this splits into a
# separate cross-profession design pass + per-profession assignment pass,
# the assignment pass can drop to Haiku.
MODEL_PER_ITEM = MODEL


class BucketAssignment(BaseModel):
    state: str
    raw_value: str
    bucket: str | None = Field(
        description="One of bucket_set, or null if the state's value doesn't fit any bucket.",
    )


# What the LLM actually returns: state + bucket only. The model used to echo
# `raw_value` back too, but that ballooned the output (49 states × up to 600
# chars) past max_tokens and truncated the JSON. We already hold raw_value on
# our side keyed by state, so we re-attach it after the call (see
# bucket_one_field). Nothing downstream reads raw_value off the LLM anyway.
class BucketAssignmentLLM(BaseModel):
    state: str
    bucket: str | None = Field(
        description="One of bucket_set, or null if the state's value doesn't fit any bucket.",
    )


class FieldBucketsLLM(BaseModel):
    field_name: str
    bucket_set: list[str] = Field(
        description=(
            "3-7 short labels covering the value distribution. Snake-case-or-Title-Case "
            "is fine — prefer concise human-readable phrases ('Doctorate degree', "
            "'Single state board') over jargon."
        ),
    )
    rationale: str
    assignments: list[BucketAssignmentLLM]


class FieldBuckets(BaseModel):
    """Stored shape: assignments carry raw_value (re-attached by us) so the
    file stays self-describing for audit. Consumers use only state + bucket."""
    field_name: str
    bucket_set: list[str]
    rationale: str
    assignments: list[BucketAssignment]


def _resolve_field(rec: dict, dotted: str):
    """Walk dotted path into a structured record. Returns None if missing/empty."""
    cur = rec
    for seg in dotted.split("."):
        if not isinstance(cur, dict) or seg not in cur:
            return None
        cur = cur[seg]
    # Evidence-wrapped values: pull the actual value
    if isinstance(cur, dict) and "value" in cur:
        return cur.get("value")
    return cur


def _collect_per_state(profession: str, dotted: str) -> list[dict]:
    out = []
    prof_dir = _STRUCTURED_DIR / profession
    if not prof_dir.exists():
        return out
    for f in sorted(prof_dir.glob("*.json")):
        if f.stem.startswith("_"):
            continue  # _summary.json and similar are not per-state
        rec = json.loads(f.read_text())
        if not isinstance(rec, dict):
            continue
        state = rec.get("state") or f.stem
        v = _resolve_field(rec, dotted)
        if v is None or v == "" or v == []:
            continue
        if isinstance(v, list):
            v = "; ".join(str(x) for x in v if x)
        out.append({"state": state, "raw_value": str(v)[:600]})
    return out


def bucket_one_field(profession: str, dotted: str, raw_per_state: list[dict]) -> FieldBuckets | None:
    if len(raw_per_state) < 2:
        log.info("[%s] %s: only %d states with values — skipping", profession, dotted, len(raw_per_state))
        return None
    system = load_prompt("map_prep_bucket_text")
    user = json.dumps({
        "profession": profession,
        "field_name": dotted,
        "per_state_raw_values": raw_per_state,
    }, ensure_ascii=False)
    log.info("[%s] %s: %d states → asking %s", profession, dotted, len(raw_per_state), MODEL)
    result = call_structured(
        model=MODEL,
        system=system,
        user=user,
        schema_cls=FieldBucketsLLM,
        embed_schema=True,
        max_tokens=8000,
        max_retries=2,
        temperature=None,
        log_prefix=f"[{profession}/{dotted}]",
        logger=log,
    )
    if result is None:
        return None
    # Re-attach raw_value from our side (the LLM no longer echoes it).
    raw_by_state = {r["state"]: r["raw_value"] for r in raw_per_state}
    assignments = [
        BucketAssignment(
            state=a.state,
            raw_value=raw_by_state.get(a.state, ""),
            bucket=a.bucket,
        )
        for a in result.assignments
    ]
    return FieldBuckets(
        field_name=result.field_name,
        bucket_set=result.bucket_set,
        rationale=result.rationale,
        assignments=assignments,
    )


def run_profession(profession: str) -> None:
    spec_path = _OUT_ROOT / profession / "spec.json"
    if not spec_path.exists():
        log.warning("[%s] no map_prep spec.json — run `python -m pipeline.map_prep.run %s` first",
                    profession, profession)
        return
    spec = json.loads(spec_path.read_text())
    not_mappable = [f["field_name"] for f in spec["fields"] if f.get("kind") == "not_mappable"]
    log.info("[%s] %d not_mappable fields to bucket", profession, len(not_mappable))

    field_results: list[FieldBuckets] = []
    for dotted in not_mappable:
        raw = _collect_per_state(profession, dotted)
        result = bucket_one_field(profession, dotted, raw)
        if result is not None:
            field_results.append(result)

    out_path = _OUT_ROOT / profession / "text_buckets.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "profession": profession,
        "fields": [r.model_dump() for r in field_results],
    }, indent=2, ensure_ascii=False))
    log.info("[%s] wrote %s — %d fields bucketed", profession, out_path.name, len(field_results))


# ---------- Per-item path (list-of-objects fields like disciplinary_grounds) ----------

# Default field for --per-item bucketing. The disciplinary_grounds list is the
# motivating case: each state has 10-24 grounds, and the cross-state question
# we want to answer is "which states include a fraud-type ground, a criminal-
# conviction-type ground, etc." — not "what flavor is this state's whole list."
_DEFAULT_PER_ITEM_FIELD = "licensure.disciplinary_grounds"

# Per-item LLM call output can run ~1000 assignments × ~35 tokens; the default
# 8k cap truncates. Sonnet 4.6 supports up to 64k output, so use a generous
# ceiling and let real usage land below it.
_PER_ITEM_MAX_TOKENS = 60000


# How many item-rows to assign per LLM call in the chunked assignment pass.
# Output is tiny per row ({state, item_index, bucket} ≈ 20 tokens), so the cap
# is about keeping each call comfortably under the connection timeout, not
# tokens. 788-row fields (podiatry disciplinary_grounds) split into ~5 chunks.
_PER_ITEM_ASSIGN_CHUNK = 150


class PerItemAssignment(BaseModel):
    state: str
    item_index: int = Field(description="0-based position of the item in that state's list")
    item_label: str = Field(description="Echo of the source short_label, for join-back")
    bucket: str | None = Field(
        description="One of bucket_set, or null if the item doesn't fit any bucket.",
    )


# Phase 1 output: just the vocabulary, designed once over all rows.
class PerItemVocab(BaseModel):
    bucket_set: list[str] = Field(
        description="3-9 short Title Case labels covering the value distribution.",
    )
    rationale: str


# Phase 2 output: minimal per-row assignment against a fixed vocabulary. No
# echoed item_label (re-attached our side) — keeps output small enough to
# chunk without timeouts.
class PerItemAssignmentLLM(BaseModel):
    state: str
    item_index: int
    bucket: str | None = Field(
        description="One of the provided bucket_set, or null if the item fits none.",
    )


class PerItemAssignmentChunk(BaseModel):
    assignments: list[PerItemAssignmentLLM]


class PerItemFieldBuckets(BaseModel):
    field_name: str
    bucket_set: list[str] = Field(
        description="3-9 short Title Case labels covering the value distribution.",
    )
    rationale: str
    assignments: list[PerItemAssignment]


def _collect_items_for_field(profession: str, dotted: str) -> list[dict]:
    """Fan out a list-of-objects field — one row per (state, item).

    Each row carries the item's `short_label` and `description` (the
    one-line plain-English summary the LLM populated at extract time).
    `description` is the primary bucketing signal; `short_label` is echoed
    back so per-item assignments can be joined to the source items.
    """
    out: list[dict] = []
    prof_dir = _STRUCTURED_DIR / profession
    if not prof_dir.exists():
        return out
    segs = dotted.split(".")
    for f in sorted(prof_dir.glob("*.json")):
        if f.stem.startswith("_"):
            continue
        rec = json.loads(f.read_text())
        if not isinstance(rec, dict):
            continue
        state = rec.get("state") or f.stem
        cur: Any = rec
        ok = True
        for seg in segs:
            if not isinstance(cur, dict) or seg not in cur:
                ok = False
                break
            cur = cur[seg]
        if not ok:
            continue
        # Two shapes feed this pass:
        #   - list-of-objects, stored bare (licensure.disciplinary_grounds):
        #     each item is a {short_label, description, …} dict.
        #   - list[str], Evidence-wrapped (profession_specific.* discovered
        #     fields like laser_procedures_authorized): {value: [...], quote}.
        # Unwrap the Evidence node so both reduce to "a list of items".
        if isinstance(cur, dict) and "value" in cur:
            cur = cur.get("value")
        if not isinstance(cur, list):
            continue
        for i, item in enumerate(cur):
            if isinstance(item, dict):
                short_label = (item.get("short_label") or "").strip()
                desc = (item.get("description") or item.get("name") or "").strip()
            elif isinstance(item, str):
                # A plain string list element is its own label and signal.
                short_label = item.strip()[:80]
                desc = item.strip()
            else:
                continue
            if not desc and not short_label:
                continue
            out.append({
                "state": state,
                "item_index": i,
                "item_label": short_label,
                "raw_value": desc[:400],
            })
    return out


def _design_per_item_vocab(profession: str, dotted: str, rows: list[dict]) -> PerItemVocab | None:
    """Phase 1: design the bucket vocabulary once, over ALL rows. Input can be
    large (that's fine), but output is just bucket_set + rationale, so it never
    truncates or times out."""
    system = load_prompt("map_prep_bucket_text_per_item_design")
    user = json.dumps({
        "profession": profession,
        "field_name": dotted,
        "per_item_rows": rows,
    }, ensure_ascii=False)
    log.info("[%s] %s per-item: designing vocab over %d rows → %s",
             profession, dotted, len(rows), MODEL_PER_ITEM)
    return call_structured(
        model=MODEL_PER_ITEM,
        system=system,
        user=user,
        schema_cls=PerItemVocab,
        embed_schema=True,
        max_tokens=4000,
        max_retries=2,
        temperature=None,
        log_prefix=f"[{profession}/{dotted}/per-item design]",
        logger=log,
    )


def _assign_per_item_chunk(
    profession: str, dotted: str, bucket_set: list[str], chunk: list[dict], chunk_no: int, n_chunks: int
) -> list[PerItemAssignmentLLM]:
    """Phase 2: assign one chunk of rows against the fixed vocabulary. Output
    is minimal ({state, item_index, bucket}) so a chunk stays well under the
    timeout. Returns [] if the chunk fails after retries (caller logs the gap)."""
    system = load_prompt("map_prep_bucket_text_per_item_assign")
    user = json.dumps({
        "profession": profession,
        "field_name": dotted,
        "bucket_set": bucket_set,
        "per_item_rows": chunk,
    }, ensure_ascii=False)
    log.info("[%s] %s per-item: assign chunk %d/%d (%d rows)",
             profession, dotted, chunk_no, n_chunks, len(chunk))
    result = call_structured(
        model=MODEL_PER_ITEM,
        system=system,
        user=user,
        schema_cls=PerItemAssignmentChunk,
        embed_schema=True,
        max_tokens=_PER_ITEM_MAX_TOKENS,
        max_retries=2,
        temperature=None,
        log_prefix=f"[{profession}/{dotted}/per-item assign {chunk_no}]",
        logger=log,
    )
    return result.assignments if result is not None else []


def bucket_per_item_field(profession: str, dotted: str) -> PerItemFieldBuckets | None:
    rows = _collect_items_for_field(profession, dotted)
    if len(rows) < 2:
        log.info("[%s] %s per-item: only %d rows — skipping", profession, dotted, len(rows))
        return None

    # Phase 1: design vocabulary once.
    vocab = _design_per_item_vocab(profession, dotted, rows)
    if vocab is None:
        log.error("[%s] %s per-item: vocab design failed — skipping", profession, dotted)
        return None

    # Phase 2: assign in chunks against the fixed vocabulary.
    n_chunks = (len(rows) + _PER_ITEM_ASSIGN_CHUNK - 1) // _PER_ITEM_ASSIGN_CHUNK
    llm_assignments: list[PerItemAssignmentLLM] = []
    for ci in range(n_chunks):
        chunk = rows[ci * _PER_ITEM_ASSIGN_CHUNK : (ci + 1) * _PER_ITEM_ASSIGN_CHUNK]
        got = _assign_per_item_chunk(profession, dotted, vocab.bucket_set, chunk, ci + 1, n_chunks)
        if not got:
            log.warning("[%s] %s per-item: chunk %d/%d returned nothing — %d rows unbucketed",
                        profession, dotted, ci + 1, n_chunks, len(chunk))
        llm_assignments.extend(got)

    if not llm_assignments:
        log.error("[%s] %s per-item: all chunks failed — skipping", profession, dotted)
        return None
    if len(llm_assignments) != len(rows):
        log.warning("[%s] %s per-item: input rows=%d but assignments=%d",
                    profession, dotted, len(rows), len(llm_assignments))

    # Re-attach item_label from input rows, keyed by (state, item_index).
    label_by_key = {(r["state"], r["item_index"]): r["item_label"] for r in rows}
    assignments = [
        PerItemAssignment(
            state=a.state,
            item_index=a.item_index,
            item_label=label_by_key.get((a.state, a.item_index), ""),
            bucket=a.bucket,
        )
        for a in llm_assignments
    ]
    return PerItemFieldBuckets(
        field_name=dotted,
        bucket_set=vocab.bucket_set,
        rationale=vocab.rationale,
        assignments=assignments,
    )


def run_profession_per_item(profession: str, field: str) -> None:
    result = bucket_per_item_field(profession, field)
    if result is None:
        return
    out_path = _OUT_ROOT / profession / "text_buckets_per_item.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # File holds a dict keyed by field_name so a single profession can grow
    # multiple per-item-bucketed fields later without overwriting.
    existing: dict = {"profession": profession, "fields": {}}
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text())
            if "fields" not in existing or not isinstance(existing.get("fields"), dict):
                existing["fields"] = {}
        except Exception:
            existing = {"profession": profession, "fields": {}}
    existing["profession"] = profession
    existing["fields"][field] = result.model_dump()
    out_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    log.info("[%s] wrote %s — field=%s, %d buckets, %d assignments",
             profession, out_path.name, field, len(result.bucket_set), len(result.assignments))


def run_profession_list_fields(profession: str) -> None:
    """Per-item-bucket every discovered list field for a profession. Sparse
    fields self-skip inside bucket_per_item_field. This is the general pass —
    laser, injectables, sedation types, license tiers, etc. all get tagged the
    same way disciplinary_grounds does, with no per-field configuration."""
    fields = discovered_list_fields(profession)
    if not fields:
        log.info("[%s] no discovered list fields to bucket", profession)
        return
    log.info("[%s] per-item bucketing %d discovered list fields: %s",
             profession, len(fields), ", ".join(fields))
    for dotted in fields:
        run_profession_per_item(profession, dotted)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("profession", nargs="?", help="single profession (omit + use --all)")
    ap.add_argument("--all", action="store_true", help="process every profession with a spec.json")
    ap.add_argument(
        "--per-item",
        action="store_true",
        help=(
            "Run the per-item path: fan out a list-of-objects field (default: "
            f"{_DEFAULT_PER_ITEM_FIELD}) into one row per item and assign "
            "a bucket per (state, item_index). Writes text_buckets_per_item.json."
        ),
    )
    ap.add_argument(
        "--field",
        default=_DEFAULT_PER_ITEM_FIELD,
        help="Dotted field path for --per-item. Default: licensure.disciplinary_grounds.",
    )
    ap.add_argument(
        "--list-fields",
        action="store_true",
        help=(
            "Per-item-bucket EVERY discovered list field for the profession "
            "(laser_procedures_authorized, etc.), not just --field. The general "
            "tagging pass; sparse fields self-skip."
        ),
    )
    args = ap.parse_args()

    if args.list_fields:
        if args.all:
            for p in sorted(_OUT_ROOT.iterdir()):
                if p.is_dir() and (p / "spec.json").exists():
                    run_profession_list_fields(p.name)
            return
        if not args.profession:
            ap.error("provide a profession or --all")
        run_profession_list_fields(args.profession)
        return

    if args.per_item:
        if args.all:
            for p in sorted(_OUT_ROOT.iterdir()):
                if p.is_dir() and (p / "spec.json").exists():
                    run_profession_per_item(p.name, args.field)
            return
        if not args.profession:
            ap.error("provide a profession or --all")
        run_profession_per_item(args.profession, args.field)
        return

    if args.all:
        for p in sorted(_OUT_ROOT.iterdir()):
            if p.is_dir() and (p / "spec.json").exists():
                run_profession(p.name)
        return
    if not args.profession:
        ap.error("provide a profession or --all")
    run_profession(args.profession)


if __name__ == "__main__":
    main()
