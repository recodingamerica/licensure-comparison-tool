"""Smoke tests for the download exporter (pipeline.client.export_data)."""

import json

import openpyxl

from pipeline.client import export_data as ed
from pipeline.config import loaders


def _setup(tmp_path, monkeypatch):
    data, struct, clean = tmp_path / "data", tmp_path / "struct", tmp_path / "clean"
    (data / "state").mkdir(parents=True)
    (struct / "optometry").mkdir(parents=True)
    (clean / "optometry").mkdir(parents=True)
    (data / "optometry.json").write_text(json.dumps(
        {"display": "Optometry", "rows": [{"state": "UT", "license_required": True}]}))
    (struct / "optometry" / "UT.json").write_text(json.dumps(
        {"state": "UT", "licensure": {"license_required": {"value": True, "quote": "a license is required", "citation": "53-1"}}}))
    # the Raw tab reads CLEANED text (clean/), not the raw text/ corpus
    (clean / "optometry" / "UT.json").write_text(json.dumps(
        {"state": "UT", "sections": [{"citation": "53-1", "label": "Licensure", "text": "body"}]}))
    (data / "state" / "UT.json").write_text(json.dumps(
        {"sections": [{"profession": "optometry", "citation": "53-1", "label": "Licensure", "text": "body"}]}))
    monkeypatch.setattr(ed, "DATA_DIR", data)
    monkeypatch.setattr(ed, "STRUCTURED_DIR", struct)
    monkeypatch.setattr(ed, "CLEAN_DIR", clean)
    # Patch the registry at its source: _published_professions now delegates to
    # pipeline.paths.published_professions, which imports this lazily at call time.
    monkeypatch.setattr(loaders, "all_profession_ids", lambda: ["optometry"])


def test_export_occupation_three_sheets(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    out = tmp_path / "optometry.xlsx"
    r = ed.export_occupation("optometry", out)
    wb = openpyxl.load_workbook(out)
    assert wb.sheetnames == ["Processed", "Evidence", "Raw statute text"]
    assert r["evidence_rows"] == 1 and r["raw_sections"] == 1  # the one Evidence-wrapped field + section


def test_export_state_pivots_across_occupations(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    out = tmp_path / "state_UT.xlsx"
    r = ed.export_state("UT", out)
    wb = openpyxl.load_workbook(out)
    assert wb.sheetnames == ["Processed", "Evidence", "Raw statute text"]
    # Processed has one row per occupation (here just optometry), carrying a profession column
    ws = wb["Processed"]
    assert [c.value for c in next(ws.iter_rows(max_row=1))][0] == "profession"
    assert r["processed_rows"] == 1
