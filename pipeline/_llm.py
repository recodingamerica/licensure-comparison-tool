"""Shared LLM call helper.

Every script that asks an LLM for a Pydantic-constrained JSON response has
the same loop: call litellm, strip the code fence, json.loads, model_validate,
retry on parse or API error with exponential backoff. Consolidating it here
removes ~40 lines per call site and centralizes the retry policy.

Usage:
    result = call_structured(
        model=model_for("extract"),  # from config/models.yaml
        system=system_prompt,
        user=user_prompt,
        schema_cls=ResultModel,
        max_tokens=8000,
    )
    if result is None:
        # all retries failed; logged at WARN
        return None
    # result is a ResultModel instance
"""

from __future__ import annotations

import atexit
import json
import logging
import re
import time
from collections import defaultdict
from typing import Callable, TypeVar

from pydantic import BaseModel, ValidationError

import litellm

T = TypeVar("T", bound=BaseModel)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```")


# Process-wide usage accumulator, bucketed per model. Cost comes from
# litellm.completion_cost which carries the per-model pricing table; unknown
# models fall back to 0.0 (logged once at WARN). One-row-per-model keeps the
# summary readable — per-call labels still appear in live log lines.
_USAGE: dict[str, dict[str, float]] = defaultdict(
    lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
)
_USAGE_WARN_MODELS: set[str] = set()


def _record_usage(resp, model: str) -> None:
    """Pull token + cost from a litellm response and add to _USAGE."""
    try:
        usage = getattr(resp, "usage", None) or {}
        prompt = int(getattr(usage, "prompt_tokens", 0) or usage.get("prompt_tokens", 0))
        completion = int(
            getattr(usage, "completion_tokens", 0) or usage.get("completion_tokens", 0)
        )
    except Exception:
        prompt = completion = 0
    try:
        cost = float(litellm.completion_cost(completion_response=resp) or 0.0)
    except Exception as e:
        cost = 0.0
        if model not in _USAGE_WARN_MODELS:
            _USAGE_WARN_MODELS.add(model)
            logging.getLogger(__name__).warning(
                "no pricing for model %s — cost will be 0 (%s)", model, str(e)[:80]
            )
    bucket = _USAGE[model]
    bucket["calls"] += 1
    bucket["prompt_tokens"] += prompt
    bucket["completion_tokens"] += completion
    bucket["cost_usd"] += cost


def usage_summary() -> dict:
    """Snapshot of recorded usage per model, plus totals."""
    totals = {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0}
    rows = []
    for model, v in sorted(_USAGE.items()):
        rows.append({"model": model, **v})
        for k in totals:
            totals[k] += v[k]
    return {"rows": rows, "totals": totals}


def log_usage_summary(logger: logging.Logger | None = None) -> None:
    """Emit a human-readable summary of recorded LLM usage. No-op if nothing
    was recorded. Called automatically at process exit via atexit."""
    if not _USAGE:
        return
    log = logger or logging.getLogger(__name__)
    summ = usage_summary()
    log.info("=== LLM usage ===")
    for r in summ["rows"]:
        log.info(
            "  %s: %d calls, %d in / %d out tokens, $%.4f",
            r["model"], r["calls"],
            r["prompt_tokens"], r["completion_tokens"], r["cost_usd"],
        )
    if len(summ["rows"]) > 1:
        t = summ["totals"]
        log.info(
            "  TOTAL: %d calls, %d in / %d out tokens, $%.4f",
            t["calls"], t["prompt_tokens"], t["completion_tokens"], t["cost_usd"],
        )


atexit.register(log_usage_summary)


def extract_json(raw: str) -> str:
    """Strip ``` fences and locate the JSON object in a model response."""
    if not raw:
        return ""
    m = _JSON_FENCE_RE.search(raw)
    s = m.group(1).strip() if m else raw.strip()
    if s.startswith("{") or s.startswith("["):
        return s
    # find first '{' and last '}'
    i, j = s.find("{"), s.rfind("}")
    return s[i : j + 1] if 0 <= i < j else s


def _system_with_schema(system: str, schema_cls: type[BaseModel]) -> str:
    """Append the Pydantic JSON schema to a system prompt. Callers that want
    the LLM constrained to a structured output pass `embed_schema=True` —
    the schema becomes part of the system message so the model sees it
    alongside the instructions."""
    return (
        system
        + "\n\nReturn JSON matching exactly this schema:\n"
        + json.dumps(schema_cls.model_json_schema(), indent=2)
        + "\n\nReturn ONLY a single JSON object. No prose, no code fences."
    )


def call_structured(
    *,
    model: str,
    system: str,
    user: str,
    schema_cls: type[T],
    embed_schema: bool = False,
    max_tokens: int = 8000,
    temperature: float | None = 0.0,
    max_retries: int = 2,
    backoff_base: float = 1.5,
    timeout: float = 300.0,
    log_prefix: str = "",
    logger: logging.Logger | None = None,
    recover_fn: Callable[[dict, ValidationError], dict] | None = None,
) -> T | None:
    """Call the LLM and validate response against `schema_cls`.

    Retries on JSON parse errors AND on API errors. Backoff is
    `backoff_base ** attempt` seconds between tries. Returns the validated
    Pydantic model or None if all retries fail (final error is logged at
    ERROR).

    embed_schema: when True, the Pydantic JSON schema is appended to the
    system prompt so the model sees the exact shape it must return. Use
    this for tasks where the prompt itself doesn't already pin down output
    structure.

    recover_fn: optional callback invoked when validation fails. Receives
    the parsed dict and the ValidationError; can return a modified dict
    that will be re-validated. Used by extract_state to null out invalid
    enum/literal fields rather than discard the whole record.

    log_prefix: a short identifier (e.g. "[TX]") prepended to log lines.
    """
    log = logger or logging.getLogger(__name__)
    prefix = f"{log_prefix} " if log_prefix else ""
    system_msg = _system_with_schema(system, schema_cls) if embed_schema else system
    last_err: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            kwargs = dict(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user},
                ],
                max_tokens=max_tokens,
                # Bound a single call so a hung API connection doesn't stall
                # a multi-hour bulk run (this happened on a 760K-char VA
                # podiatry corpus that never returned). The retry loop above
                # turns the timeout into a transient failure, so the next
                # state still gets attempted.
                timeout=timeout,
            )
            # temperature is removed on some models (e.g. Opus 4.7 — sending it
            # 400s). Pass temperature=None to omit it.
            if temperature is not None:
                kwargs["temperature"] = temperature
            resp = litellm.completion(**kwargs)
            _record_usage(resp, model=model)
            raw = resp.choices[0].message.content or ""
            data = json.loads(extract_json(raw))
            try:
                return schema_cls.model_validate(data)
            except ValidationError as ve:
                if recover_fn is None:
                    raise
                repaired = recover_fn(data, ve)
                return schema_cls.model_validate(repaired)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = e
            log.warning("%sparse attempt %d failed: %s", prefix, attempt + 1, str(e)[:200])
        except Exception as e:
            last_err = e
            log.warning("%sapi attempt %d failed: %s", prefix, attempt + 1, str(e)[:200])
        if attempt < max_retries:
            time.sleep(backoff_base ** attempt)

    log.error("%sgiving up: %s", prefix, str(last_err)[:200])
    return None
