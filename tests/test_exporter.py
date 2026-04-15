"""Tests for envoy_diff.exporter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.exporter import ExportError, export_json_summary, export_report
from envoy_diff.reporter import Report
from envoy_diff.validator import ValidationResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def clean_report() -> Report:
    diff = DiffResult(added={}, removed={}, changed={}, unchanged={"KEY": "val"})
    validation = ValidationResult(missing_keys=set(), empty_keys=set())
    return Report(diff=diff, validation=validation)


@pytest.fixture()
def dirty_report() -> Report:
    diff = DiffResult(
        added={"NEW": "1"},
        removed={"OLD": "2"},
        changed={"HOST": ("old", "new")},
        unchanged={},
    )
    validation = ValidationResult(missing_keys={"SECRET"}, empty_keys={"TOKEN"})
    return Report(diff=diff, validation=validation)


# ---------------------------------------------------------------------------
# export_report – stdout
# ---------------------------------------------------------------------------


def test_export_report_text_to_stdout(clean_report, capsys):
    export_report(clean_report, fmt="text")
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_export_report_json_to_stdout(clean_report, capsys):
    export_report(clean_report, fmt="json")
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, dict)


def test_export_report_unsupported_format_raises(clean_report):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_report(clean_report, fmt="xml")


# ---------------------------------------------------------------------------
# export_report – file
# ---------------------------------------------------------------------------


def test_export_report_writes_file(tmp_path, clean_report):
    out_file = tmp_path / "report.txt"
    export_report(clean_report, output_path=str(out_file), fmt="text")
    assert out_file.exists()
    assert out_file.stat().st_size > 0


def test_export_report_creates_parent_dirs(tmp_path, clean_report):
    out_file = tmp_path / "nested" / "dir" / "report.json"
    export_report(clean_report, output_path=str(out_file), fmt="json")
    assert out_file.exists()


def test_export_report_raises_on_bad_path(clean_report):
    with pytest.raises(ExportError):
        export_report(clean_report, output_path="/no_permission/x/report.txt")


# ---------------------------------------------------------------------------
# export_json_summary
# ---------------------------------------------------------------------------


def test_export_json_summary_stdout(dirty_report, capsys):
    export_json_summary(dirty_report)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["has_issues"] is True
    assert data["diff_keys_added"] == 1
    assert data["diff_keys_removed"] == 1
    assert data["diff_keys_changed"] == 1
    assert "SECRET" in data["validation_missing_keys"]
    assert data["validation_passed"] is False


def test_export_json_summary_clean_report(clean_report, capsys):
    export_json_summary(clean_report)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["has_issues"] is False
    assert data["validation_passed"] is True


def test_export_json_summary_writes_file(tmp_path, dirty_report):
    out_file = tmp_path / "summary.json"
    export_json_summary(dirty_report, output_path=str(out_file))
    data = json.loads(out_file.read_text())
    assert "has_issues" in data
