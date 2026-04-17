import pytest
from envoy_diff.summarizer import summarize_config, SummaryResult


@pytest.fixture
def sample_config():
    return {
        "DATABASE_HOST": "localhost",
        "DATABASE_PORT": "5432",
        "CACHE_HOST": "localhost",
        "APP_SECRET": "",
        "LONG_KEY_NAME_HERE": "short",
        "X": "a_very_long_value_indeed",
    }


def test_empty_config_returns_zeroes():
    result = summarize_config({})
    assert result.total_keys == 0
    assert result.unique_values == 0
    assert result.empty_keys == []
    assert result.duplicate_values == {}
    assert result.longest_key == ""
    assert result.longest_value_key == ""


def test_total_keys(sample_config):
    result = summarize_config(sample_config)
    assert result.total_keys == 6


def test_unique_values(sample_config):
    result = summarize_config(sample_config)
    # "localhost" appears twice, so unique < total values
    assert result.unique_values == 5


def test_empty_keys_detected(sample_config):
    result = summarize_config(sample_config)
    assert "APP_SECRET" in result.empty_keys
    assert result.empty_count() == 1


def test_duplicate_values_detected(sample_config):
    result = summarize_config(sample_config)
    assert "localhost" in result.duplicate_values
    assert set(result.duplicate_values["localhost"]) == {"DATABASE_HOST", "CACHE_HOST"}


def test_duplicate_group_count(sample_config):
    result = summarize_config(sample_config)
    assert result.duplicate_group_count() == 1


def test_longest_key(sample_config):
    result = summarize_config(sample_config)
    assert result.longest_key == "LONG_KEY_NAME_HERE"


def test_longest_value_key(sample_config):
    result = summarize_config(sample_config)
    assert result.longest_value_key == "X"


def test_summary_string_contains_labels(sample_config):
    result = summarize_config(sample_config)
    text = result.summary()
    assert "Total keys" in text
    assert "Unique values" in text
    assert "Empty keys" in text
    assert "Duplicate groups" in text


def test_no_duplicates_when_all_unique():
    config = {"A": "1", "B": "2", "C": "3"}
    result = summarize_config(config)
    assert result.duplicate_group_count() == 0
    assert result.duplicate_values == {}
