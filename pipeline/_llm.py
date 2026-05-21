"""Shared LLM call helper.

Every script that asks an LLM for a Pydantic-constrained JSON response has
the same loop: call litellm, strip the code fence, json.loads, model_validate,
retry on parse or API error with exponential backoff. Consolidating it here
removes ~40 lines per call site and centralizes the retry policy.

Usage:
    result = call_structured(
        model="claude-sonnet-4-6",
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

import json
import logging
import re
import time
from typing import Callable, TypeVar

from pydantic import BaseModel, ValidationError

import litellm

T = TypeVar("T", bound=BaseModel)

_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)```")


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
    temperature: float = 0.0,
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
            resp = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                # Bound a single call so a hung API connection doesn't stall
                # a multi-hour bulk run (this happened on a 760K-char VA
                # podiatry corpus that never returned). The retry loop above
                # turns the timeout into a transient failure, so the next
                # state still gets attempted.
                timeout=timeout,
            )
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
