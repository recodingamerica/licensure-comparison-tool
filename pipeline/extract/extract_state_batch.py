"""Batched + prompt-cached extraction across many (state, profession) pairs.

Wraps `extract_state.extract_one`'s LLM call in Anthropic's Message Batches
API plus prompt caching, for the re-extraction queue that doesn't need
real-time results. Savings vs the synchronous path:

  - Message Batches API: 50% off input AND output tokens for the whole call.
  - Prompt caching (ephemeral): the system prompt + JSON schema (the static
    portion per profession) is marked cacheable. Subsequent reads inside
    the cache window pay 10% of normal. First write costs 1.25x.
  - The two compose: a cached read inside a batched call is roughly 5% of
    the un-batched/un-cached cost.

Durability: results live server-side for 29 days. If this script crashes
after submission, re-run with `poll <batch_id>` to fetch.

CLI:

  # Submit the default re-extract queue (the (state, profession) pairs the
  # post-yaml-cleanup work invalidated). Saves batch metadata to
  # pipeline/results/batches/<batch_id>.json.
  python -m pipeline.extract.extract_state_batch submit

  # Submit a custom queue from a JSON file (shape: {profession: [STATES]}):
  python -m pipeline.extract.extract_state_batch submit --queue myqueue.json

  # Poll an existing batch (fetches results when ready and writes them
  # to pipeline/results/structured/<profession>/<state>.json):
  python -m pipeline.extract.extract_state_batch poll BATCH_ID

  # List batches we've submitted (uses local metadata, not API):
  python -m pipeline.extract.extract_state_batch list
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# .env loader
_PIPELINE_DIR = Path(__file__).resolve().parent.parent
if str(_PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_DIR))

from _env import load_env  # noqa: E402

load_env()

import anthropic  # noqa: E402
from pydantic import BaseModel, ValidationError  # noqa: E402

from extract.extract_state import (  # noqa: E402
    SYSTEM_PROMPT,
    DEFAULT_MODEL,
    build_profile_model,
    build_state_text,
    load_umbrella_text,
    annotate_evidence,
    _recover_invalid_fields,
    _normalize_for_match,
)
from paths import DISCOVERED_DIR, TRIMMED_DIR, STRUCTURED_DIR, LOGS_DIR, RESULTS_DIR  # noqa: E402
from _llm import extract_json  # noqa: E402
from extract.preflight import run_preflight, format_report  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("extract_state_batch")

BATCH_DIR = RESULTS_DIR / "batches"
BATCH_DIR.mkdir(parents=True, exist_ok=True)

POLL_INTERVAL_SECS = 30

# The re-extract queue created by the YAML cleanup pass (2026-06-01). Keys
# are professions; values are states whose chapter list changed (new match,
# corpus revision, or upstream pipeline-stage retry).
DEFAULT_QUEUE: dict[str, list[str]] = {
    "medicine":           ["ME", "RI", "WA", "MA", "NJ", "MS", "CA", "OR", "NE", "MN", "MI"],
    "podiatry":           ["MA", "NJ", "NE"],
    "dentistry":          ["ME", "MA", "NJ", "WA", "NE", "MN", "MI"],
    "nursing":            ["MA", "NJ", "NE", "MN", "MI"],
    "optometry":          ["MA", "NJ", "NE", "MN", "MI"],
    "public_accountancy": ["MA", "NJ", "NE", "MN", "MI", "TN", "NM"],
}


def _client() -> anthropic.Anthropic:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic()


def _build_user_message(state: str, profession: str) -> str | None:
    in_path = TRIMMED_DIR / profession / f"{state}.json"
    if not in_path.exists():
        log.warning("[%s/%s] no trimmed file at %s — run pull_text + trim_state first",
                    profession, state, in_path)
        return None
    raw = json.loads(in_path.read_text())
    if not raw.get("sections"):
        log.warning("[%s/%s] trimmed file has no sections", profession, state)
        return None
    state_text = build_state_text(raw)
    umbrella_text = load_umbrella_text(state, profession)
    if umbrella_text:
        return (
            f"State: {state}\nProfession: {profession}\n\n"
            f"Practice act text (extract values from here primarily):\n{state_text}\n\n"
            f"=== Cross-cutting umbrella context (definitions, board rules, "
            f"licensing procedures that apply to this profession too) ===\n"
            f"{umbrella_text}"
        )
    return f"State: {state}\nProfession: {profession}\n\nTrimmed statute text:\n{state_text}"


def _system_with_schema(schema_cls: type[BaseModel]) -> str:
    """Same system-prompt + schema text the sync path builds — but as a string.
    Marking this whole block as a single cache_control segment maximizes
    the cacheable prefix size."""
    schema = schema_cls.model_json_schema()
    return (
        SYSTEM_PROMPT
        + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema, indent=2)
        + "\n\nReturn ONLY a single JSON object."
    )


def submit(queue: dict[str, list[str]], model: str = DEFAULT_MODEL, force: bool = False) -> dict:
    """Submit a batch covering every (profession, state) in `queue`.

    Runs the preflight gate first (missing schema / trimmed / empty / poisoned).
    On any blocker, prints the report and exits nonzero unless `force` is set.
    """
    report = run_preflight(queue)
    log.info("preflight:\n%s", format_report(report))
    if not report["ok"] and not force:
        sys.exit("preflight FAILED — fix the blockers above or pass --force to override")

    requests: list[dict] = []
    skipped: list[tuple[str, str, str]] = []
    profile_classes: dict[str, type[BaseModel]] = {}

    for profession, states in queue.items():
        discovered_path = DISCOVERED_DIR / f"{profession}.json"
        if not discovered_path.exists():
            log.error("[%s] missing discovered schema: %s", profession, discovered_path)
            for s in states:
                skipped.append((profession, s, "no_discovered_schema"))
            continue
        discovered = json.loads(discovered_path.read_text())
        profile_cls = build_profile_model(profession, discovered)
        profile_classes[profession] = profile_cls
        # The cacheable prefix is profession-specific (each profession has
        # different discovered_fields → different schema). Anthropic caches
        # per-distinct-prefix, so multiple professions in one batch is fine —
        # each gets its own cache.
        system_text = _system_with_schema(profile_cls)
        system_blocks = [{
            "type": "text",
            "text": system_text,
            "cache_control": {"type": "ephemeral"},
        }]
        for state in states:
            user_msg = _build_user_message(state, profession)
            if user_msg is None:
                skipped.append((profession, state, "no_trimmed_text"))
                continue
            requests.append({
                "custom_id": f"{profession}__{state}",
                "params": {
                    "model": model,
                    "max_tokens": 32000,
                    "system": system_blocks,
                    "messages": [{"role": "user", "content": user_msg}],
                },
            })

    if not requests:
        log.error("no requests to submit — every state skipped: %s", skipped)
        sys.exit(1)

    log.info("submitting batch: %d requests across %d professions (%d skipped)",
             len(requests), len(queue), len(skipped))
    client = _client()
    batch = client.messages.batches.create(requests=requests)
    log.info("submitted: batch_id=%s status=%s", batch.id, batch.processing_status)

    metadata = {
        "batch_id": batch.id,
        "submitted_at": datetime.now().isoformat(),
        "model": model,
        "queue": queue,
        "request_count": len(requests),
        "skipped": [{"profession": p, "state": s, "reason": r} for p, s, r in skipped],
        "custom_ids": [r["custom_id"] for r in requests],
    }
    save_path = BATCH_DIR / f"{batch.id}.json"
    save_path.write_text(json.dumps(metadata, indent=2))
    log.info("wrote batch metadata to %s", save_path)
    return metadata


def _load_metadata(batch_id: str) -> dict:
    p = BATCH_DIR / f"{batch_id}.json"
    if not p.exists():
        sys.exit(f"no local metadata for batch {batch_id} (looked at {p})")
    return json.loads(p.read_text())


def _parse_and_write(custom_id: str, response_message, profile_classes: dict[str, type[BaseModel]]) -> dict | None:
    """Validate one batch result and write structured/<profession>/<state>.json."""
    profession, state = custom_id.split("__", 1)
    profile_cls = profile_classes.get(profession)
    if profile_cls is None:
        log.error("[%s/%s] no profile class loaded for profession", profession, state)
        return None
    # Anthropic response shape: response_message.content is a list of content blocks
    text_parts = [b.text for b in response_message.content if getattr(b, "type", None) == "text"]
    raw_text = "\n".join(text_parts)
    try:
        data = json.loads(extract_json(raw_text))
    except json.JSONDecodeError as e:
        log.error("[%s/%s] JSON parse failed: %s", profession, state, e)
        return None
    try:
        model_obj = profile_cls.model_validate(data)
    except ValidationError as ve:
        try:
            repaired = _recover_invalid_fields(data, ve)
            model_obj = profile_cls.model_validate(repaired)
        except ValidationError as ve2:
            log.error("[%s/%s] schema validation failed: %s", profession, state, str(ve2)[:200])
            return None

    record = model_obj.model_dump()
    # Re-run verifier annotations on the record (mirror of extract_one's flow).
    raw_trim = json.loads((TRIMMED_DIR / profession / f"{state}.json").read_text())
    state_text = build_state_text(raw_trim)
    umbrella_text = load_umbrella_text(state, profession)
    normalized_corpus = _normalize_for_match(state_text + "\n" + umbrella_text)
    verified, unverified = annotate_evidence(record, normalized_corpus)
    log.info("[%s/%s] evidence: verified=%d unverified=%d", profession, state, verified, unverified)

    out_path = STRUCTURED_DIR / profession / f"{state}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2, ensure_ascii=False))
    return {"profession": profession, "state": state, "verified": verified, "unverified": unverified}


def poll(batch_id: str, wait: bool = True) -> None:
    """Fetch results for an existing batch and write each one to disk."""
    metadata = _load_metadata(batch_id)
    queue = metadata["queue"]
    # Rebuild the profile classes (so result parsing can validate)
    profile_classes: dict[str, type[BaseModel]] = {}
    for profession in queue:
        discovered = json.loads((DISCOVERED_DIR / f"{profession}.json").read_text())
        profile_classes[profession] = build_profile_model(profession, discovered)

    client = _client()
    log.info("polling batch %s ...", batch_id)
    transient_errors = 0
    while True:
        try:
            batch = client.messages.batches.retrieve(batch_id)
        except anthropic.APIStatusError as e:
            # Transient Anthropic outages (503 overloaded_error, 502) shouldn't
            # kill a poll loop — the batch is durable, just back off and retry.
            transient_errors += 1
            log.warning("transient error #%d polling batch: %s — sleeping %ds and retrying",
                        transient_errors, str(e)[:120], POLL_INTERVAL_SECS * 2)
            time.sleep(POLL_INTERVAL_SECS * 2)
            continue
        log.info("status=%s  counts=%s", batch.processing_status, dict(batch.request_counts))
        if batch.processing_status == "ended":
            break
        if not wait:
            log.info("not waiting — exit; re-run later to fetch results")
            return
        time.sleep(POLL_INTERVAL_SECS)

    log.info("batch ended — fetching results")
    written = []
    errored = []
    for result in client.messages.batches.results(batch_id):
        custom_id = result.custom_id
        if result.result.type == "succeeded":
            outcome = _parse_and_write(
                custom_id, result.result.message, profile_classes,
            )
            if outcome:
                written.append(outcome)
            else:
                errored.append({"custom_id": custom_id, "reason": "parse_or_validate_failed"})
        else:
            errored.append({"custom_id": custom_id, "reason": result.result.type, "error": getattr(result.result, "error", None)})
            log.error("[%s] batch result type=%s", custom_id, result.result.type)

    log.info("results: wrote=%d errored=%d", len(written), len(errored))

    # Aggregate usage + cost — Sonnet 4.6 pricing with cache + batch discounts.
    # Pricing (per 1M tokens):
    #   input            $3.00
    #   cache write      $3.75 (1.25× input)
    #   cache read       $0.30 (0.10× input)
    #   output           $15.00
    # Message Batches API gives 50% off everything; the batch result usage
    # fields are pre-discount counts, so we apply 0.5× ourselves.
    tot = {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0}
    for result in client.messages.batches.results(batch_id):
        if result.result.type != "succeeded":
            continue
        u = result.result.message.usage
        tot["in"] += u.input_tokens
        tot["out"] += u.output_tokens
        tot["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
        tot["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
    cost = (
        tot["in"]         / 1e6 *  3.00 * 0.5
        + tot["cache_write"] / 1e6 *  3.75 * 0.5
        + tot["cache_read"]  / 1e6 *  0.30 * 0.5
        + tot["out"]      / 1e6 * 15.00 * 0.5
    )
    sync_no_cache_baseline = (
        (tot["in"] + tot["cache_read"] + tot["cache_write"]) / 1e6 * 3.00
        + tot["out"] / 1e6 * 15.00
    )
    log.info("=== batch usage (Sonnet 4.6, post-discount) ===")
    log.info("  input tokens:   %d", tot["in"])
    log.info("  cache writes:   %d", tot["cache_write"])
    log.info("  cache reads:    %d", tot["cache_read"])
    log.info("  output tokens:  %d", tot["out"])
    log.info("  COST: $%.4f  (vs ~$%.4f synchronous-no-cache baseline, %d%% saved)",
             cost, sync_no_cache_baseline,
             100 * (sync_no_cache_baseline - cost) / max(sync_no_cache_baseline, 0.0001))

    metadata["completed_at"] = datetime.now().isoformat()
    metadata["written"] = written
    metadata["errored"] = errored
    metadata["usage"] = {**tot, "cost_usd": round(cost, 4), "baseline_usd": round(sync_no_cache_baseline, 4)}
    (BATCH_DIR / f"{batch_id}.json").write_text(json.dumps(metadata, indent=2))


def list_batches() -> None:
    """List local batch metadata files."""
    files = sorted(BATCH_DIR.glob("*.json"))
    if not files:
        print("no batches recorded")
        return
    for p in files:
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        # skip non-batch files that share this dir (queue inputs, candidate lists, etc.)
        if not isinstance(d, dict) or ("batch_id" not in d and "submitted_at" not in d):
            continue
        bid = d.get("batch_id", p.stem)
        submitted = d.get("submitted_at", "?")
        completed = d.get("completed_at", "")
        n = d.get("request_count", 0)
        written = len(d.get("written") or [])
        errored = len(d.get("errored") or [])
        status = f"completed wrote={written} err={errored}" if completed else "pending"
        print(f"  {bid}  submitted={submitted}  n={n}  {status}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)

    s_submit = sp.add_parser("submit", help="Submit a batch for the queue")
    s_submit.add_argument("--queue", help="Path to a JSON file: {profession: [states]}")
    s_submit.add_argument("--model", default=DEFAULT_MODEL)
    s_submit.add_argument("--force", action="store_true",
                          help="Submit even if preflight finds blockers")

    s_poll = sp.add_parser("poll", help="Poll an existing batch and write results")
    s_poll.add_argument("batch_id")
    s_poll.add_argument("--no-wait", action="store_true", help="Exit immediately if still in_progress")

    sp.add_parser("list", help="Show local batch records")

    args = ap.parse_args()

    if args.cmd == "submit":
        if args.queue:
            queue = json.loads(Path(args.queue).read_text())
        else:
            queue = DEFAULT_QUEUE
        submit(queue, model=args.model, force=args.force)
    elif args.cmd == "poll":
        poll(args.batch_id, wait=not args.no_wait)
    elif args.cmd == "list":
        list_batches()


if __name__ == "__main__":
    main()
