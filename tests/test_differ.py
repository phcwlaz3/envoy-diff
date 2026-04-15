"""Tests for envoy_diff.differ and envoy_diff.formatter."""

import json
import pytest

from envoy_diff.differ import diff_configs, DiffResult
from envoy_diff.formatter import format_diff


SOURCE = {
    "APP_ENV": "staging",
    "DB_HOST": "db.staging.internal",
    "SECRET_KEY": "abc123",
    "LOG_LEVEL": "DEBUG",
}

TARGET = {
    "APP_ENV": "production",
    "DB_HOST": "db.prod.internal",
    "SECRET_KEY": "abc123",
    "NEW_RELIC_KEY": "nr-xyz",
}


def test_diff_detects_added_keys():
    result = diff_configs(SOURCE, TARGET)
    assert "NEW_RELIC_KEY" in result.added
    assert result.added["NEW_RELIC_KEY"] == "nr-xyz"


def test_diff_detects_removed_keys():
    result = diff_configs(SOURCE, TARGET)
    assert "LOG_LEVEL" in result.removed
    assert result.removed["LOG_LEVEL"] == "DEBUG"


def test_diff_detects_changed_keys():
    result = diff_configs(SOURCE, TARGET)
    assert "APP_ENV" in result.changed
    assert result.changed["APP_ENV"] == ("staging", "production")
    assert "DB_HOST" in result.changed


def test_diff_unchanged_keys():
    result = diff_configs(SOURCE, TARGET)
    assert "SECRET_KEY" in result.unchanged


def test_diff_no_differences():
    result = diff_configs(SOURCE, SOURCE)
    assert not result.has_diff
    assert result.summary() == "No differences found."


def test_diff_ignore_keys():
    result = diff_configs(SOURCE, TARGET, ignore_keys=["APP_ENV", "LOG_LEVEL", "NEW_RELIC_KEY"])
    assert "APP_ENV" not in result.changed
    assert "LOG_LEVEL" not in result.removed
    assert "NEW_RELIC_KEY" not in result.added


def test_diff_has_diff_true():
    result = diff_configs(SOURCE, TARGET)
    assert result.has_diff is True


def test_format_text_shows_symbols():
    result = diff_configs(SOURCE, TARGET)
    output = format_diff(result, fmt="text", show_values=True)
    assert "+ NEW_RELIC_KEY" in output
    assert "- LOG_LEVEL" in output
    assert "~ APP_ENV" in output


def test_format_text_no_values():
    result = diff_configs(SOURCE, TARGET)
    output = format_diff(result, fmt="text", show_values=False)
    assert "nr-xyz" not in output
    assert "+ NEW_RELIC_KEY" in output


def test_format_json_structure():
    result = diff_configs(SOURCE, TARGET)
    output = format_diff(result, fmt="json", show_values=True)
    data = json.loads(output)
    assert "added" in data
    assert "removed" in data
    assert "changed" in data
    assert data["added"]["NEW_RELIC_KEY"] == "nr-xyz"
    assert data["changed"]["APP_ENV"]["from"] == "staging"
    assert data["changed"]["APP_ENV"]["to"] == "production"


def test_format_no_diff_text():
    result = DiffResult()
    assert format_diff(result, fmt="text") == "No differences found."
