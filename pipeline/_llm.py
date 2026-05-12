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
from typing import TypeVar

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


def call_structured(
    *,
    model: str,
    system: str,
    user: str,
    schema_cls: type[T],
    max_tokens: int = 8000,
    temperature: float = 0.0,
    max_retries: int = 2,
    log_prefix: str = "",
    logger: logging.Logger | None = None,
) -> T | None:
    """Call the LLM and validate response against `schema_cls`.

    Retries on JSON parse errors AND on API errors. Backoff is 1.5**attempt
    seconds between tries. Returns the validated Pydantic model or None if
    all retries fail (final error is logged at ERROR).

    log_prefix: a short identifier (e.g. "[TX]") prepended to log lines.
    """
    log = logger or logging.getLogger(__name__)
    prefix = f"{log_prefix} " if log_prefix else ""
    last_err: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            resp = litellm.completion(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            raw = resp.choices[0].message.content or ""
            data = json.loads(extract_json(raw))
            return schema_cls.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_err = e
            log.warning("%sparse attempt %d failed: %s", prefix, attempt + 1, str(e)[:200])
        except Exception as e:
            last_err = e
            log.warning("%sapi attempt %d failed: %s", prefix, attempt + 1, str(e)[:200])
        if attempt < max_retries:
            time.sleep(1.5 ** attempt)

    log.error("%sgiving up: %s", prefix, str(last_err)[:200])
    return None
