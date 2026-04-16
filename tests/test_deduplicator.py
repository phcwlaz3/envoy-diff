import pytest
from envoy_diff.deduplicator import deduplicate_config, DeduplicateResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",
        "APP_ENV": "production",
        "STAGE": "production",
        "PORT": "8080",
    }


def test_no_duplicates_returns_original():
    config = {"A": "1", "B": "2", "C": "3"}
    result = deduplicate_config(config)
    assert result.config == config
    assert not result.has_duplicates()


def test_detects_duplicate_values(sample_config):
    result = deduplicate_config(sample_config)
    assert "localhost" in result.duplicates
    assert set(result.duplicates["localhost"]) == {"DB_HOST", "CACHE_HOST"}


def test_detects_multiple_duplicate_groups(sample_config):
    result = deduplicate_config(sample_config)
    assert "localhost" in result.duplicates
    assert "production" in result.duplicates


def test_keep_first_removes_later_keys(sample_config):
    result = deduplicate_config(sample_config, keep="first")
    assert "DB_HOST" in result.config
    assert "CACHE_HOST" not in result.config


def test_keep_last_removes_earlier_keys(sample_config):
    result = deduplicate_config(sample_config, keep="last")
    assert "CACHE_HOST" in result.config
    assert "DB_HOST" not in result.config


def test_unique_keys_always_retained(sample_config):
    result = deduplicate_config(sample_config)
    assert "PORT" in result.config


def test_duplicate_count(sample_config):
    result = deduplicate_config(sample_config)
    # localhost: 2 keys -> 1 duplicate; production: 2 keys -> 1 duplicate
    assert result.duplicate_count() == 2


def test_has_duplicates_true(sample_config):
    result = deduplicate_config(sample_config)
    assert result.has_duplicates()


def test_has_duplicates_false():
    result = deduplicate_config({"X": "1", "Y": "2"})
    assert not result.has_duplicates()


def test_summary_no_duplicates():
    result = deduplicate_config({"A": "unique"})
    assert result.summary() == "No duplicate values found."


def test_summary_with_duplicates(sample_config):
    result = deduplicate_config(sample_config)
    summary = result.summary()
    assert "duplicate" in summary.lower()
    assert "localhost" in summary


def test_empty_config():
    result = deduplicate_config({})
    assert result.config == {}
    assert not result.has_duplicates()
