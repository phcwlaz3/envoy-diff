"""Tests for envoy_diff.reporter module."""

import json

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.reporter import Report, build_report, render_report
from envoy_diff.validator import ValidationResult


@pytest.fixture
def sample_diff() -> DiffResult:
    return DiffResult(
        added={"NEW_KEY"},
        removed={"OLD_KEY"},
        changed={"CHANGED_KEY"},
        unchanged={"SAME_KEY"},
    )


@pytest.fixture
def clean_diff() -> DiffResult:
    return DiffResult(added=set(), removed=set(), changed=set(), unchanged={"A", "B"})


@pytest.fixture
def failed_validation() -> ValidationResult:
    return ValidationResult(missing_keys=["REQUIRED"], empty_keys=[])


@pytest.fixture
def passing_validation() -> ValidationResult:
    return ValidationResult(missing_keys=[], empty_keys=[])


def test_build_report_defaults():
    report = build_report("staging", "production")
    assert report.stage_a == "staging"
    assert report.stage_b == "production"
    assert report.diff is None
    assert report.validation_results == []


def test_has_issues_with_diff_changes(sample_diff):
    report = build_report("staging", "production", diff=sample_diff)
    assert report.has_issues is True


def test_no_issues_with_clean_diff(clean_diff, passing_validation):
    report = build_report(
        "staging", "production", diff=clean_diff, validation_results=[passing_validation]
    )
    assert report.has_issues is False


def test_has_issues_with_failed_validation(clean_diff, failed_validation):
    report = build_report(
        "staging", "production", diff=clean_diff, validation_results=[failed_validation]
    )
    assert report.has_issues is True


def test_has_issues_no_diff_no_validation():
    report = build_report("dev", "staging")
    assert report.has_issues is False


def test_render_report_text_contains_stages(sample_diff):
    report = build_report("dev", "prod", diff=sample_diff)
    output = render_report(report, fmt="text")
    assert "dev" in output
    assert "prod" in output


def test_render_report_text_shows_counts(sample_diff):
    report = build_report("dev", "prod", diff=sample_diff)
    output = render_report(report, fmt="text")
    assert "Added   : 1" in output
    assert "Removed : 1" in output
    assert "Changed : 1" in output


def test_render_report_text_no_diff():
    report = build_report("dev", "prod")
    output = render_report(report, fmt="text")
    assert "not performed" in output


def test_render_report_json_structure(sample_diff, passing_validation):
    report = build_report(
        "dev", "prod", diff=sample_diff, validation_results=[passing_validation]
    )
    output = render_report(report, fmt="json")
    data = json.loads(output)
    assert data["stage_a"] == "dev"
    assert data["stage_b"] == "prod"
    assert "diff" in data
    assert "validation" in data
    assert data["has_issues"] is True


def test_render_report_json_null_diff():
    report = build_report("dev", "prod")
    output = render_report(report, fmt="json")
    data = json.loads(output)
    assert data["diff"] is None
