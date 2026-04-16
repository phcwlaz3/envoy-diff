"""Tests for envoy_diff.filterer."""

import pytest
from envoy_diff.filterer import filter_config


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_ENV": "production",
        "APP_DEBUG": "false",
        "SECRET_KEY": "abc123",
        "LOG_LEVEL": "info",
    }


def test_no_filters_returns_all(sample_config):
    result = filter_config(sample_config)
    assert result.filtered == sample_config
    assert result.excluded == []
    assert result.kept_count() == 6


def test_include_prefix(sample_config):
    result = filter_config(sample_config, include_prefix="DB_")
    assert set(result.filtered.keys()) == {"DB_HOST", "DB_PORT"}
    assert result.excluded_count() == 4


def test_exclude_prefix(sample_config):
    result = filter_config(sample_config, exclude_prefix="APP_")
    assert "APP_ENV" not in result.filtered
    assert "APP_DEBUG" not in result.filtered
    assert result.kept_count() == 4


def test_include_pattern(sample_config):
    result = filter_config(sample_config, include_pattern=r"^DB_")
    assert set(result.filtered.keys()) == {"DB_HOST", "DB_PORT"}


def test_exclude_pattern(sample_config):
    result = filter_config(sample_config, exclude_pattern=r"SECRET")
    assert "SECRET_KEY" not in result.filtered
    assert result.kept_count() == 5


def test_keys_whitelist(sample_config):
    result = filter_config(sample_config, keys=["LOG_LEVEL", "APP_ENV"])
    assert set(result.filtered.keys()) == {"LOG_LEVEL", "APP_ENV"}


def test_combined_filters(sample_config):
    result = filter_config(
        sample_config,
        include_prefix="APP_",
        exclude_pattern=r"DEBUG",
    )
    assert result.filtered == {"APP_ENV": "production"}


def test_summary_string(sample_config):
    result = filter_config(sample_config, include_prefix="DB_")
    assert "2/6" in result.summary()
    assert "4 excluded" in result.summary()


def test_empty_config():
    result = filter_config({}, include_prefix="DB_")
    assert result.filtered == {}
    assert result.original_count == 0
