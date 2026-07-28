"""The model sometimes emits statute text containing raw `"` inside a JSON string.

Delaware nursing failed this way twice (2026-07-24 and again on re-run), always at
the same spot: the statute defines a term -- `Committee's ("Committee") purpose` --
and those inner quotes went out unescaped, making the whole response unparseable.
`stop_reason` was `end_turn`, so it was malformed output, not truncation.

These tests pin BOTH directions: the repair fixes that class, and it stays out of
the way otherwise.
"""

from __future__ import annotations

import json

import pytest

from pipeline._llm import loads_lenient


def test_repairs_unescaped_inner_quotes():
    """The real Delaware shape: a defined term in parentheses inside a quote."""
    raw = """{
      "exists": {
        "value": true,
        "quote": "The Committee's ("Committee") purpose is to: recommend rules.",
        "citation": "§ 1934"
      }
    }"""
    data = loads_lenient(raw)
    assert data["exists"]["quote"] == 'The Committee\'s ("Committee") purpose is to: recommend rules.'
    assert data["exists"]["citation"] == "§ 1934"


def test_valid_json_is_untouched():
    """STRICT FIRST -- a good response must never go through the repair."""
    payload = {"quote": 'he said "hello" loudly', "n": 3, "ok": True, "sub": {"a": [1, 2]}}
    raw = json.dumps(payload)
    assert loads_lenient(raw) == payload


def test_already_escaped_quotes_survive_a_repair_pass():
    """A line with correctly-escaped quotes must not get double-escaped when the
    repair runs because of a DIFFERENT bad line."""
    raw = """{
      "good": "already \\"escaped\\" properly",
      "bad": "raw "quotes" here"
    }"""
    data = loads_lenient(raw)
    assert data["good"] == 'already "escaped" properly'
    assert data["bad"] == 'raw "quotes" here'


def test_missing_comma_raises_rather_than_merging_fields():
    """The dangerous failure mode: a repair that yields VALID but WRONG JSON.

    With a comma missing between two fields, a naive escaper would swallow the second
    key into the first value and hand back a plausible object with data silently lost.
    A `"` followed by `:` reads as a key terminator, so the runaway stops and the
    caller gets an error instead of quiet corruption.
    """
    with pytest.raises(json.JSONDecodeError):
        loads_lenient('{\n  "a": "first"\n  "b": "second"\n}')


def test_value_ending_in_a_quoted_term_is_preserved():
    """`... as defined in "Committee"` -- the inner quote sits at the very end of the
    value, adjacent to the real closing quote."""
    data = loads_lenient('{"q": "as defined in "Committee"", "n": 1}')
    assert data == {"q": 'as defined in "Committee"', "n": 1}


def test_unrepairable_json_raises_the_original_error():
    """A truncated response is not a quoting problem; the caller must see the real
    error rather than a repair artifact."""
    with pytest.raises(json.JSONDecodeError):
        loads_lenient('{"a": {"b": [1, 2')


def test_fenced_response_still_works():
    """extract_json's fence stripping stays in the path."""
    raw = '```json\n{"quote": "a "b" c"}\n```'
    assert loads_lenient(raw)["quote"] == 'a "b" c'
