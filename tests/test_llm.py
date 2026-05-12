"""Tests for pipeline._llm.

Covers the JSON-fence stripper + the retry loop (mocking litellm). We don't
want real API calls in tests.
"""

import json
import logging
from unittest.mock import patch, MagicMock

import pytest
from pydantic import BaseModel, ValidationError

from pipeline._llm import extract_json, call_structured


class TestExtractJson:
    def test_strips_json_fence(self):
        raw = "```json\n{\"a\": 1}\n```"
        assert extract_json(raw) == '{"a": 1}'

    def test_strips_bare_fence(self):
        raw = "```\n{\"a\": 1}\n```"
        assert extract_json(raw) == '{"a": 1}'

    def test_no_fence(self):
        assert extract_json('{"a": 1}') == '{"a": 1}'

    def test_leading_prose_recovers_object(self):
        """Model sometimes writes 'Here is the JSON: { ... }'."""
        assert extract_json('Here is the JSON: {"a": 1}') == '{"a": 1}'

    def test_empty(self):
        assert extract_json("") == ""

    def test_returns_array_unchanged(self):
        assert extract_json("[1, 2, 3]") == "[1, 2, 3]"


class Result(BaseModel):
    answer: str
    count: int


def _mock_resp(text: str) -> MagicMock:
    """Build a fake litellm completion response carrying `text` as content."""
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = text
    return resp


class TestCallStructured:
    def test_happy_path_returns_validated_model(self):
        with patch("pipeline._llm.litellm.completion") as mock:
            mock.return_value = _mock_resp('{"answer": "hi", "count": 3}')
            r = call_structured(
                model="m", system="s", user="u", schema_cls=Result, max_retries=0
            )
            assert isinstance(r, Result)
            assert r.answer == "hi"
            assert r.count == 3

    def test_retries_on_invalid_json(self):
        with patch("pipeline._llm.litellm.completion") as mock:
            mock.side_effect = [
                _mock_resp("not valid json"),
                _mock_resp('{"answer": "hi", "count": 3}'),
            ]
            r = call_structured(
                model="m", system="s", user="u", schema_cls=Result, max_retries=2
            )
            assert r is not None
            assert mock.call_count == 2

    def test_retries_on_validation_error(self):
        with patch("pipeline._llm.litellm.completion") as mock:
            mock.side_effect = [
                _mock_resp('{"answer": "hi"}'),  # missing count
                _mock_resp('{"answer": "hi", "count": 3}'),
            ]
            r = call_structured(
                model="m", system="s", user="u", schema_cls=Result, max_retries=2
            )
            assert r is not None
            assert r.count == 3

    def test_retries_on_api_error(self):
        with patch("pipeline._llm.litellm.completion") as mock:
            mock.side_effect = [
                RuntimeError("API error"),
                _mock_resp('{"answer": "hi", "count": 3}'),
            ]
            r = call_structured(
                model="m", system="s", user="u", schema_cls=Result, max_retries=2
            )
            assert r is not None

    def test_returns_none_after_all_retries(self):
        with patch("pipeline._llm.litellm.completion") as mock:
            mock.return_value = _mock_resp("not json")
            r = call_structured(
                model="m", system="s", user="u", schema_cls=Result, max_retries=1
            )
            assert r is None
            assert mock.call_count == 2  # initial + 1 retry

    def test_passes_max_tokens_through(self):
        with patch("pipeline._llm.litellm.completion") as mock:
            mock.return_value = _mock_resp('{"answer": "hi", "count": 3}')
            call_structured(
                model="m", system="s", user="u", schema_cls=Result,
                max_tokens=16000, max_retries=0,
            )
            assert mock.call_args.kwargs["max_tokens"] == 16000

    def test_log_prefix_appears_on_error(self, caplog):
        caplog.set_level(logging.WARNING)
        with patch("pipeline._llm.litellm.completion") as mock:
            mock.return_value = _mock_resp("not json")
            call_structured(
                model="m", system="s", user="u", schema_cls=Result,
                max_retries=0, log_prefix="[TX]",
            )
            assert any("[TX]" in rec.message for rec in caplog.records)
