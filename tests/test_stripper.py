import pytest
from envoy_diff.stripper import strip_config, StripResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "APP_NAME": "envoy",
        "EMPTY_KEY": "",
        "WHITESPACE_KEY": "   ",
        "API_SECRET": "abc123",
    }


def test_no_filters_returns_all(sample_config):
    result = strip_config(sample_config)
    assert result.config == sample_config
    assert result.strip_count() == 0
    assert not result.has_stripped()


def test_strip_explicit_key(sample_config):
    result = strip_config(sample_config, keys=["DB_PASSWORD"])
    assert "DB_PASSWORD" not in result.config
    assert "DB_HOST" in result.config
    assert result.strip_count() == 1


def test_strip_multiple_explicit_keys(sample_config):
    result = strip_config(sample_config, keys=["DB_PASSWORD", "API_SECRET"])
    assert "DB_PASSWORD" not in result.config
    assert "API_SECRET" not in result.config
    assert result.strip_count() == 2


def test_strip_by_pattern(sample_config):
    result = strip_config(sample_config, patterns=[r"^DB_"])
    assert "DB_HOST" not in result.config
    assert "DB_PASSWORD" not in result.config
    assert "APP_NAME" in result.config
    assert result.strip_count() == 2


def test_strip_pattern_case_insensitive(sample_config):
    result = strip_config(sample_config, patterns=[r"secret"])
    assert "API_SECRET" not in result.config
    assert "DB_PASSWORD" not in result.config


def test_strip_empty_values(sample_config):
    result = strip_config(sample_config, strip_empty=True)
    assert "EMPTY_KEY" not in result.config
    assert "WHITESPACE_KEY" in result.config
    assert result.strip_count() == 1


def test_strip_whitespace_values(sample_config):
    result = strip_config(sample_config, strip_whitespace_values=True)
    assert "WHITESPACE_KEY" not in result.config
    assert "EMPTY_KEY" not in result.config
    assert result.strip_count() == 2


def test_strip_combined_filters(sample_config):
    result = strip_config(sample_config, keys=["APP_NAME"], patterns=[r"^DB_"])
    assert "APP_NAME" not in result.config
    assert "DB_HOST" not in result.config
    assert "DB_PASSWORD" not in result.config
    assert result.strip_count() == 3


def test_summary_no_stripped(sample_config):
    result = strip_config(sample_config)
    assert result.summary() == "No keys stripped."


def test_summary_with_stripped(sample_config):
    result = strip_config(sample_config, keys=["APP_NAME"])
    assert "1 key(s)" in result.summary()
    assert "APP_NAME" in result.summary()


def test_original_config_not_mutated(sample_config):
    original = dict(sample_config)
    strip_config(sample_config, keys=["DB_HOST"], strip_empty=True)
    assert sample_config == original
