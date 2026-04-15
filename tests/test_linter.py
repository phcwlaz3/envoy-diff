"""Tests for envoy_diff.linter."""

import pytest
from envoy_diff.linter import lint_config, LintResult, LintIssue


@pytest.fixture
def clean_config():
    return {"DATABASE_URL": "postgres://localhost/db", "APP_PORT": "8080"}


@pytest.fixture
def dirty_config():
    return {
        "lowercase_key": "value",
        "VALID_KEY": "ok",
        "has-hyphen": "bad",
        "1STARTS_WITH_DIGIT": "bad",
        "DOUBLE__UNDERSCORE": "warn",
    }


def test_clean_config_no_issues(clean_config):
    result = lint_config(clean_config)
    assert not result.has_issues
    assert result.error_count == 0
    assert result.warning_count == 0


def test_lowercase_key_flagged():
    result = lint_config({"my_key": "value"})
    assert result.has_issues
    assert any(i.key == "my_key" for i in result.issues)


def test_invalid_character_is_error():
    result = lint_config({"HAS-HYPHEN": "value"})
    errors = [i for i in result.issues if i.severity == "error"]
    assert len(errors) >= 1


def test_digit_start_is_error():
    result = lint_config({"1BAD_KEY": "value"})
    errors = [i for i in result.issues if i.severity == "error"]
    assert len(errors) >= 1


def test_double_underscore_is_warning():
    result = lint_config({"DOUBLE__SCORE": "value"})
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert len(warnings) >= 1


def test_long_key_is_warning():
    long_key = "A" * 65
    result = lint_config({long_key: "value"})
    warnings = [i for i in result.issues if i.severity == "warning"]
    assert any("64" in w.message for w in warnings)


def test_summary_no_issues(clean_config):
    result = lint_config(clean_config)
    assert result.summary() == "No lint issues found."


def test_summary_with_issues(dirty_config):
    result = lint_config(dirty_config)
    assert "issue" in result.summary()
    assert "error" in result.summary()


def test_empty_config_no_issues():
    result = lint_config({})
    assert not result.has_issues


def test_multiple_issues_counted(dirty_config):
    result = lint_config(dirty_config)
    assert len(result.issues) >= 3
