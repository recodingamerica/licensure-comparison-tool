"""Tests for state similarity scoring."""

from collections import Counter

from pipeline.publish.state_similarity import _bucket, score_state, SCORING_FIELDS


class TestBucket:
    def test_none_to_none_string(self):
        assert _bucket(None, "regulatory_model") == "none"

    def test_exams_count_bins_by_5(self):
        assert _bucket(0, "exams_count") == "0-4"
        assert _bucket(2, "exams_count") == "0-4"
        assert _bucket(5, "exams_count") == "5-9"
        assert _bucket(13, "exams_count") == "10-14"

    def test_ce_hours_bins_by_10(self):
        assert _bucket(0, "ce_hours") == "0-9"
        assert _bucket(50, "ce_hours") == "50-59"
        assert _bucket(127, "ce_hours") == "120-129"

    def test_categorical_unchanged(self):
        assert _bucket("license", "regulatory_model") == "license"
        assert _bucket(True, "license_required") is True


class TestScoreState:
    def test_typical_state_scores_low(self):
        """A state matching the majority on every field should score low."""
        frequencies = {f: Counter({"X": 40, "Y": 3}) for f in SCORING_FIELDS}
        row = {f: "X" for f in SCORING_FIELDS}
        score, _ = score_state(row, frequencies)
        # 12 fields × (1/40) = 0.3
        assert score < 0.5

    def test_unique_state_scores_high(self):
        """A state with rare values on every field scores high."""
        frequencies = {f: Counter({"X": 40, "Y": 3, "Z": 1}) for f in SCORING_FIELDS}
        row = {f: "Z" for f in SCORING_FIELDS}  # always the rarest
        score, _ = score_state(row, frequencies)
        # 12 × (1/1) = 12.0
        assert score >= 10

    def test_contributions_reported(self):
        frequencies = {f: Counter({"common": 40, "rare": 1}) for f in SCORING_FIELDS}
        row = {f: "rare" if f == "credential_type" else "common" for f in SCORING_FIELDS}
        _, contribs = score_state(row, frequencies)
        # Field-level breakdown is returned for human consumption
        cred = next(c for c in contribs if c[0] == "credential_type")
        assert cred[1] == "rare"
        assert cred[2] == 1

    def test_missing_field_counts_as_rare(self):
        """If a state has a value not in frequencies, treat as rare (count=1)."""
        frequencies = {f: Counter() for f in SCORING_FIELDS}
        row = {f: "unseen" for f in SCORING_FIELDS}
        score, _ = score_state(row, frequencies)
        # Each unseen → count=1 → contribution 1.0; total = 12
        assert score == 12.0
