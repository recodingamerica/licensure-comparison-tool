"""Reusable batched + prompt-cached LLM calls via Anthropic's Message Batches.

Wraps the Anthropic SDK so any pipeline stage that makes many same-model calls
can submit them as one batch and pull validated Pydantic models back. Saves
50% on tokens (batch discount) and an additional 10x on the cacheable prefix
(prompt caching). Combined, a cached read inside a batch is ~5% of the normal
sync price.

The Anthropic batch is durable: results persist server-side for 29 days, so
a crashed poll loop doesn't lose work.

Typical use:

    from pipeline._batch import BatchRequest, submit_batch, poll_batch

    reqs = [
        BatchRequest(
            custom_id="medicine__pass1",
            system=SYSTEM_PROMPT + "\\n\\n" + schema_text,
            user=user_json,
            schema_cls=SpecResult,
            max_tokens=16000,
        ),
        ...
    ]
    batch_id = submit_batch(reqs, model=model_for("extract"))
    # ... later (or after a crash) ...
    parsed = poll_batch(batch_id, schema_by_custom_id={r.custom_id: r.schema_cls for r in reqs})

The system message is wrapped in a single `cache_control: ephemeral` block so
the per-batch cache write happens once per distinct system prefix; subsequent
requests in the same batch with the same system text read at the cache-discount
rate. Group requests with identical system+schema together to maximize cache
hits.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

import anthropic
from pydantic import BaseModel, ValidationError

from pipeline._llm import extract_json  # reuse the JSON-extraction helper

log = logging.getLogger("_batch")

POLL_INTERVAL_SECS = 30


@dataclass
class BatchRequest:
    custom_id: str
    system: str
    user: str
    schema_cls: type[BaseModel]
    max_tokens: int = 16000
    recover_fn: Any = None  # optional (data, ve) -> repaired_data


@dataclass
class BatchResult:
    custom_id: str
    parsed: BaseModel | None  # validated model, or None on parse/validation failure
    raw_text: str = ""
    error: str | None = None
    usage: dict = field(default_factory=dict)


def _client() -> anthropic.Anthropic:
    import os
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    return anthropic.Anthropic()


def submit_batch(reqs: list[BatchRequest], model: str) -> str:
    """Submit a list of requests as one Anthropic Message Batch. Returns batch_id."""
    if not reqs:
        raise ValueError("no requests to submit")
    client = _client()
    requests = []
    for r in reqs:
        requests.append({
            "custom_id": r.custom_id,
            "params": {
                "model": model,
                "max_tokens": r.max_tokens,
                "system": [{
                    "type": "text",
                    "text": r.system,
                    "cache_control": {"type": "ephemeral"},
                }],
                "messages": [{"role": "user", "content": r.user}],
            },
        })
    log.info("submitting batch: %d requests, model=%s", len(reqs), model)
    batch = client.messages.batches.create(requests=requests)
    log.info("submitted: batch_id=%s status=%s", batch.id, batch.processing_status)
    return batch.id


def _wait_for_end(batch_id: str, poll_secs: int = POLL_INTERVAL_SECS) -> None:
    """Block until batch ends. Retries transient 5xx errors."""
    client = _client()
    transient_errors = 0
    while True:
        try:
            b = client.messages.batches.retrieve(batch_id)
        except anthropic.APIStatusError as e:
            transient_errors += 1
            log.warning("transient #%d polling batch: %s — sleeping %ds",
                        transient_errors, str(e)[:120], poll_secs * 2)
            time.sleep(poll_secs * 2)
            continue
        log.info("batch %s: status=%s counts=%s", batch_id, b.processing_status, dict(b.request_counts))
        if b.processing_status == "ended":
            return
        time.sleep(poll_secs)


def poll_batch(
    batch_id: str,
    schema_by_custom_id: dict[str, type[BaseModel]],
    recover_by_custom_id: dict[str, Any] | None = None,
    wait: bool = True,
) -> dict[str, BatchResult]:
    """Block until batch is done, fetch results, parse + validate each.

    Returns {custom_id: BatchResult}. BatchResult.parsed is the validated
    Pydantic model on success, or None on failure (error message recorded).
    """
    if wait:
        _wait_for_end(batch_id)
    client = _client()
    recover_by_custom_id = recover_by_custom_id or {}
    out: dict[str, BatchResult] = {}
    for result in client.messages.batches.results(batch_id):
        cid = result.custom_id
        schema_cls = schema_by_custom_id.get(cid)
        if schema_cls is None:
            out[cid] = BatchResult(custom_id=cid, parsed=None, error="no schema registered")
            continue
        if result.result.type != "succeeded":
            out[cid] = BatchResult(
                custom_id=cid, parsed=None,
                error=f"batch result type={result.result.type}",
            )
            continue
        msg = result.result.message
        text_parts = [b.text for b in msg.content if getattr(b, "type", None) == "text"]
        raw_text = "\n".join(text_parts)
        u = msg.usage
        usage = {
            "input_tokens": u.input_tokens,
            "output_tokens": u.output_tokens,
            "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
            "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
        }
        try:
            data = json.loads(extract_json(raw_text))
        except json.JSONDecodeError as e:
            out[cid] = BatchResult(custom_id=cid, parsed=None, raw_text=raw_text,
                                   error=f"JSON parse: {e}", usage=usage)
            continue
        try:
            parsed = schema_cls.model_validate(data)
        except ValidationError as ve:
            recover_fn = recover_by_custom_id.get(cid)
            if recover_fn is None:
                out[cid] = BatchResult(custom_id=cid, parsed=None, raw_text=raw_text,
                                       error=f"validation: {str(ve)[:200]}", usage=usage)
                continue
            try:
                repaired = recover_fn(data, ve)
                parsed = schema_cls.model_validate(repaired)
            except ValidationError as ve2:
                out[cid] = BatchResult(custom_id=cid, parsed=None, raw_text=raw_text,
                                       error=f"validation after recover: {str(ve2)[:200]}", usage=usage)
                continue
        out[cid] = BatchResult(custom_id=cid, parsed=parsed, raw_text=raw_text, usage=usage)
    return out


def aggregate_usage(results: dict[str, BatchResult]) -> dict:
    """Sum usage across results + compute Sonnet 4.6 post-discount cost.
    Sonnet 4.6: input $3, cache_write $3.75, cache_read $0.30, output $15 per 1M.
    Batch API: 50% off everything.
    """
    tot = {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0}
    for r in results.values():
        u = r.usage
        if not u:
            continue
        tot["in"] += u.get("input_tokens", 0)
        tot["out"] += u.get("output_tokens", 0)
        tot["cache_read"] += u.get("cache_read_input_tokens", 0)
        tot["cache_write"] += u.get("cache_creation_input_tokens", 0)
    cost = (
        tot["in"]          / 1e6 *  3.00 * 0.5
        + tot["cache_write"] / 1e6 *  3.75 * 0.5
        + tot["cache_read"]  / 1e6 *  0.30 * 0.5
        + tot["out"]       / 1e6 * 15.00 * 0.5
    )
    sync_baseline = (
        (tot["in"] + tot["cache_read"] + tot["cache_write"]) / 1e6 * 3.00
        + tot["out"] / 1e6 * 15.00
    )
    tot["cost_usd"] = round(cost, 4)
    tot["sync_no_cache_baseline_usd"] = round(sync_baseline, 4)
    tot["saved_pct"] = round(100 * (sync_baseline - cost) / max(sync_baseline, 0.0001), 1)
    return tot
