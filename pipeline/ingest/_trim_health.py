"""Shared health check for trimmed corpora.

A trimmed record is *poisoned* when `trim_state`'s LLM step failed and it fell
back to keep-everything: the kept sections are not a real trim decision, so
feeding them to extraction wastes budget on un-trimmed corpus. Two markers,
either one is enough:

  - explicit: a top-level ``trim_degraded: true`` flag (set since 2026-06-30).
  - legacy:   ``skipped`` is non-empty AND every entry's reason is
              ``llm_failed_kept_by_default`` (the old silent fallback).

Both `trim_state` (the writer) and `preflight` (the gate) import this so the
definition lives in exactly one place.
"""

from __future__ import annotations

LLM_FAIL_REASON = "llm_failed_kept_by_default"


def is_poisoned(trimmed: dict) -> bool:
    """True if this trimmed record is a degraded keep-everything fallback."""
    if trimmed.get("trim_degraded"):
        return True
    skipped = trimmed.get("skipped") or []
    if skipped and all(s.get("reason") == LLM_FAIL_REASON for s in skipped):
        return True
    return False
