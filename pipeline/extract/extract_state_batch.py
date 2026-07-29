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

  # Submit a queue from a JSON file (shape: {profession: [STATES]}). Runs a
  # preflight gate first and saves batch metadata to
  # pipeline/results/batches/<batch_id>.json.
  python -m pipeline.extract.extract_state_batch submit --queue myqueue.json

  # Poll an existing batch (fetches results when ready and writes them
  # to pipeline/results/structured/<profession>/<state>.json):
  python -m pipeline.extract.extract_state_batch poll BATCH_ID

  # List batches we've submitted (uses local metadata, not API):
  python -m pipeline.extract.extract_state_batch list
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# .env loader

from pipeline._env import load_env
from pipeline._records import write_json_atomic

load_env()

import anthropic  # noqa: E402
from pydantic import BaseModel, ValidationError  # noqa: E402

from pipeline.extract.extract_state import (
    SYSTEM_PROMPT,
    DEFAULT_MODEL,
    build_profile_model,
    build_user_message,
    finalize_and_persist,
    extract_one,
    _recover_invalid_fields,
)
from pipeline.paths import DISCOVERED_DIR, TRIMMED_DIR, STRUCTURED_DIR, LOGS_DIR, RESULTS_DIR
from pipeline import provenance
from pipeline._llm import loads_lenient
from pipeline.extract.preflight import run_preflight, format_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("extract_state_batch")

BATCH_DIR = RESULTS_DIR / "batches"
BATCH_DIR.mkdir(parents=True, exist_ok=True)

POLL_INTERVAL_SECS = 30


def _client() -> anthropic.Anthropic:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic()


def _build_user_message(state: str, profession: str) -> str | None:
    """Batch submitter's per-request prompt — the SAME formatter the sync path
    uses, so the two never drift. Logs the reason when there's nothing to send."""
    msg = build_user_message(state, profession)
    if msg is None:
        log.warning("[%s/%s] no trimmed sections — run pull_text + trim_state first", profession, state)
    return msg


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

    schema_shas: dict[str, str] = {}
    for profession, states in queue.items():
        discovered_path = DISCOVERED_DIR / f"{profession}.json"
        if not discovered_path.exists():
            log.error("[%s] missing discovered schema: %s", profession, discovered_path)
            for s in states:
                skipped.append((profession, s, "no_discovered_schema"))
            continue
        raw_schema = discovered_path.read_bytes()
        schema_shas[profession] = hashlib.sha256(raw_schema).hexdigest()
        discovered = json.loads(raw_schema)
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
        # sha256 of each discovered schema AS SUBMITTED — the prompts embed it, so poll
        # refuses to write results if the on-disk schema has changed since (the results
        # would carry field names the current schema doesn't have).
        "schema_shas": schema_shas,
        "request_count": len(requests),
        "skipped": [{"profession": p, "state": s, "reason": r} for p, s, r in skipped],
        "custom_ids": [r["custom_id"] for r in requests],
    }
    save_path = BATCH_DIR / f"{batch.id}.json"
    write_json_atomic(save_path, metadata)
    log.info("wrote batch metadata to %s", save_path)
    return metadata


def run_litellm(queue: dict[str, list[str]], model: str = DEFAULT_MODEL, force: bool = False) -> dict:
    """Vendor-neutral alternative to submit()/poll(): extract a queue synchronously
    through LiteLLM instead of Anthropic's Message Batches API.

    Why this exists: the batch path above talks to Anthropic's batch endpoint
    directly for its 50%-off discount, so it only works with Claude models. This
    path routes each cell through `extract_state.extract_one`, whose LLM call goes
    through the shared LiteLLM helper (`pipeline/_llm.py`) — so it works with ANY
    provider LiteLLM supports (OpenAI/ChatGPT, Gemini, Bedrock, …). Point it at a
    non-Claude model with `--model` and set that vendor's API key in the
    environment.

    Trade-offs vs the batch path: no 50% batch discount and no prompt-cache reuse,
    so per-cell cost is roughly double for the same model; and it runs inline
    (no durable server-side job to re-poll). Everything downstream is identical —
    same preflight gate, same `structured/<prof>/<state>.json` output, same
    provenance stamp — so results are interchangeable with the batch path's.
    """
    report = run_preflight(queue)
    log.info("preflight:\n%s", format_report(report))
    if not report["ok"] and not force:
        sys.exit("preflight FAILED — fix the blockers above or pass --force to override")

    written: list[dict] = []
    errored: list[dict] = []
    for profession, states in queue.items():
        discovered_path = DISCOVERED_DIR / f"{profession}.json"
        if not discovered_path.exists():
            log.error("[%s] missing discovered schema: %s", profession, discovered_path)
            for s in states:
                errored.append({"custom_id": f"{profession}__{s}", "reason": "no_discovered_schema"})
            continue
        discovered = json.loads(discovered_path.read_text())
        profile_cls = build_profile_model(profession, discovered)
        for state in states:
            cid = f"{profession}__{state}"
            log.info("[%s/%s] extracting via LiteLLM (model=%s)", profession, state, model)
            try:
                outcome = extract_one(state, profession, model, profile_cls)
            except Exception:
                log.exception("[%s/%s] crashed", profession, state)
                errored.append({"custom_id": cid, "reason": "exception"})
                continue
            if outcome is None:
                errored.append({"custom_id": cid, "reason": "no_result"})
                continue
            record, stats = outcome
            out_path = STRUCTURED_DIR / profession / f"{state}.json"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            write_json_atomic(out_path, record, ensure_ascii=False)
            provenance.record("extract", profession, state, model=model)
            written.append({"profession": profession, "state": state, **stats})

    log.info("litellm extract: wrote=%d errored=%d (model=%s)", len(written), len(errored), model)
    now = datetime.now().isoformat()
    metadata = {
        "batch_id": f"litellm-{now}",
        "backend": "litellm",
        "submitted_at": now,
        "completed_at": now,
        "model": model,
        "queue": queue,
        "request_count": len(written) + len(errored),
        "written": written,
        "errored": errored,
    }
    save_path = BATCH_DIR / f"litellm-{now.replace(':', '-')}.json"
    write_json_atomic(save_path, metadata)
    log.info("wrote litellm run metadata to %s", save_path)
    return metadata


def _load_metadata(batch_id: str) -> dict:
    p = BATCH_DIR / f"{batch_id}.json"
    if not p.exists():
        sys.exit(f"no local metadata for batch {batch_id} (looked at {p})")
    return json.loads(p.read_text())


def _parse_and_write(custom_id: str, response_message, profile_classes: dict[str, type[BaseModel]],
                     model: str | None = None) -> dict | None:
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
        data = loads_lenient(raw_text)
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
    # The SAME finalize pipeline the sync path runs (derive rung → scope matrices
    # + quote verify → consistency guard → write → provenance). Sharing it is why
    # batch and sync extractions can no longer diverge.
    stats = finalize_and_persist(record, profession, state, model)
    return {"profession": profession, "state": state, **stats}


def poll(batch_id: str, wait: bool = True) -> dict | None:
    """Fetch results for an existing batch and write each one to disk.

    Returns the batch metadata (including the `written`/`errored` accounting) once the
    batch has ended, or None if called with wait=False before it finished — so a caller
    can report exactly how many cells were written instead of assuming success."""
    metadata = _load_metadata(batch_id)
    if metadata.get("discarded"):
        sys.exit(f"batch {batch_id} is marked DISCARDED "
                 f"({metadata.get('discarded_reason', 'no reason recorded')}) — "
                 "polling it would overwrite good results with known-bad ones. "
                 "If you truly want it, delete the 'discarded' key from its metadata file.")
    queue = metadata["queue"]
    batch_model = metadata.get("model")
    # Rebuild the profile classes (so result parsing can validate). If the discovered
    # schema on disk is no longer the one the batch was submitted with, the results
    # embed a field set the current schema doesn't have — validating them against the
    # current file would either fail or, worse, silently write mismatched fields
    # (acupuncture/UT 2026-07-29). Refuse that profession's results instead.
    submitted_shas = metadata.get("schema_shas") or {}   # absent on pre-guard batches
    drifted_profs: set[str] = set()
    profile_classes: dict[str, type[BaseModel]] = {}
    for profession in queue:
        raw_schema = (DISCOVERED_DIR / f"{profession}.json").read_bytes()
        want = submitted_shas.get(profession)
        if want and hashlib.sha256(raw_schema).hexdigest() != want:
            drifted_profs.add(profession)
            log.error("[%s] discovered schema CHANGED since this batch was submitted — "
                      "refusing to write its results. Restore the schema the batch was "
                      "built with, or re-submit against the current one.", profession)
            continue
        discovered = json.loads(raw_schema)
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
            return None
        time.sleep(POLL_INTERVAL_SECS)

    log.info("batch ended — fetching results")
    written = []
    errored = []
    for result in client.messages.batches.results(batch_id):
        custom_id = result.custom_id
        if custom_id.split("__", 1)[0] in drifted_profs:
            errored.append({"custom_id": custom_id, "reason": "schema_changed_since_submit"})
            continue
        if result.result.type == "succeeded":
            outcome = _parse_and_write(
                custom_id, result.result.message, profile_classes, model=batch_model,
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
    write_json_atomic(BATCH_DIR / f"{batch_id}.json", metadata)
    return metadata


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
        if d.get("discarded"):
            status = f"DISCARDED ({d.get('discarded_reason', '')})"
        elif completed:
            status = f"completed wrote={written} err={errored}"
        else:
            status = "pending"
        print(f"  {bid}  submitted={submitted}  n={n}  {status}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)

    s_submit = sp.add_parser("submit", help="Submit a batch for the queue")
    s_submit.add_argument("--queue", required=True,
                          help="Path to a JSON file: {profession: [states]}")
    s_submit.add_argument("--model", default=DEFAULT_MODEL)
    s_submit.add_argument("--force", action="store_true",
                          help="Submit even if preflight finds blockers")

    s_poll = sp.add_parser("poll", help="Poll an existing batch and write results")
    s_poll.add_argument("batch_id")
    s_poll.add_argument("--no-wait", action="store_true", help="Exit immediately if still in_progress")

    s_lite = sp.add_parser(
        "litellm",
        help="Extract a queue synchronously via LiteLLM (any vendor, e.g. --model gpt-5; "
             "no 50%% batch discount)",
    )
    s_lite.add_argument("--queue", required=True,
                        help="Path to a JSON file: {profession: [states]}")
    s_lite.add_argument("--model", default=DEFAULT_MODEL,
                        help="Any LiteLLM-supported model name (default: the Claude batch model)")
    s_lite.add_argument("--force", action="store_true",
                        help="Run even if preflight finds blockers")

    sp.add_parser("list", help="Show local batch records")

    args = ap.parse_args()

    if args.cmd == "submit":
        queue = json.loads(Path(args.queue).read_text())
        submit(queue, model=args.model, force=args.force)
    elif args.cmd == "poll":
        poll(args.batch_id, wait=not args.no_wait)
    elif args.cmd == "litellm":
        queue = json.loads(Path(args.queue).read_text())
        run_litellm(queue, model=args.model, force=args.force)
    elif args.cmd == "list":
        list_batches()


if __name__ == "__main__":
    main()
