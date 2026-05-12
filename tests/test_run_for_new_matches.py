"""Tests for the coverage-diff logic in run_for_new_matches.

Confirms the helper correctly identifies which (state, profession) pairs
went from missing → matched between two snapshots.
"""

import csv
from pathlib import Path

import pytest

from pipeline import run_for_new_matches as rfnm


@pytest.fixture
def fake_before(tmp_path, monkeypatch):
    """Point BEFORE_PATH at a tmp file with known coverage state."""
    path = tmp_path / "coverage_before.csv"
    with path.open("w") as f:
        w = csv.DictWriter(f, fieldnames=["profession", "display", "states_matched", "states_total", "missing_states"])
        w.writeheader()
        w.writerow({
            "profession": "public_accountancy",
            "display": "CPA",
            "states_matched": "32",
            "states_total": "50",
            "missing_states": "AR,CA,CO,KY,NM,OR,TX,WI",
        })
        w.writerow({
            "profession": "podiatry",
            "display": "Podiatry",
            "states_matched": "49",
            "states_total": "50",
            "missing_states": "PA",
        })
    monkeypatch.setattr(rfnm, "BEFORE_PATH", path)
    return path


@pytest.fixture
def fake_after(tmp_path, monkeypatch):
    path = tmp_path / "coverage_after.csv"
    with path.open("w") as f:
        w = csv.DictWriter(f, fieldnames=["profession", "display", "states_matched", "states_total", "missing_states"])
        w.writeheader()
        # AR, CA, CO, KY, OR newly matched; NM still missing; TX, WI still missing
        w.writerow({
            "profession": "public_accountancy",
            "display": "CPA",
            "states_matched": "37",
            "states_total": "50",
            "missing_states": "NM,TX,WI",
        })
        # podiatry: no change
        w.writerow({
            "profession": "podiatry",
            "display": "Podiatry",
            "states_matched": "49",
            "states_total": "50",
            "missing_states": "PA",
        })
    monkeypatch.setattr(rfnm, "AFTER_PATH", path)
    return path


def test_new_matches_finds_newly_matched_states(fake_before, fake_after):
    new = rfnm.new_matches()
    assert set(new.keys()) == {"public_accountancy"}
    assert set(new["public_accountancy"]) == {"AR", "CA", "CO", "KY", "OR"}


def test_no_new_matches(fake_before, monkeypatch, tmp_path):
    # After == before
    path = tmp_path / "coverage_after.csv"
    with path.open("w") as f:
        w = csv.DictWriter(f, fieldnames=["profession", "display", "states_matched", "states_total", "missing_states"])
        w.writeheader()
        w.writerow({
            "profession": "public_accountancy",
            "display": "CPA",
            "states_matched": "32",
            "states_total": "50",
            "missing_states": "AR,CA,CO,KY,NM,OR,TX,WI",
        })
    monkeypatch.setattr(rfnm, "AFTER_PATH", path)
    assert rfnm.new_matches() == {}


def test_new_matches_handles_missing_before(monkeypatch, tmp_path):
    """No before snapshot → empty `before_missing` for each prof, so all 'matched'
    states are reported as newly matched (defensive: typical CSV header still present)."""
    after = tmp_path / "after.csv"
    with after.open("w") as f:
        w = csv.DictWriter(f, fieldnames=["profession", "display", "states_matched", "states_total", "missing_states"])
        w.writeheader()
        w.writerow({"profession": "x", "display": "X", "states_matched": "0", "states_total": "50", "missing_states": ""})
    before = tmp_path / "before_doesnt_exist.csv"
    monkeypatch.setattr(rfnm, "BEFORE_PATH", before)
    monkeypatch.setattr(rfnm, "AFTER_PATH", after)
    # With no before, every prof's before_missing = empty, so newly = empty - empty = empty
    assert rfnm.new_matches() == {}
