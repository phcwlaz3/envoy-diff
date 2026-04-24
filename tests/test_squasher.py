"""Tests for envoy_diff.squasher."""
import pytest
from envoy_diff.squasher import squash_config, SquashResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DATABASE_HOST": "localhost",
        "CACHE_HOST": "redis",
        "SESSION_HOST": "redis",
        "APP_NAME": "envoy",
    }


def test_no_duplicates_returns_all_keys():
    config = {"A": "1", "B": "2", "C": "3"}
    result = squash_config(config)
    assert len(result.config) == 3
    assert not result.has_squashed()


def test_squash_count_zero_when_no_duplicates():
    config = {"A": "1", "B": "2"}
    result = squash_config(config)
    assert result.squash_count() == 0


def test_detects_duplicate_values(sample_config):
    result = squash_config(sample_config)
    assert result.has_squashed()


def test_keep_first_retains_earlier_key(sample_config):
    result = squash_config(sample_config, keep="first")
    assert "DB_HOST" in result.config
    assert "DATABASE_HOST" not in result.config


def test_keep_last_retains_later_key(sample_config):
    result = squash_config(sample_config, keep="last")
    assert "DATABASE_HOST" in result.config
    assert "DB_HOST" not in result.config


def test_keep_shortest_retains_shortest_key():
    config = {"DATABASE_HOST": "localhost", "DB_HOST": "localhost"}
    result = squash_config(config, keep="shortest")
    assert "DB_HOST" in result.config
    assert "DATABASE_HOST" not in result.config


def test_squash_count_correct(sample_config):
    result = squash_config(sample_config, keep="first")
    # DB_HOST / DATABASE_HOST -> 1 removed; CACHE_HOST / SESSION_HOST -> 1 removed
    assert result.squash_count() == 2


def test_original_count_preserved(sample_config):
    result = squash_config(sample_config)
    assert result.original_count == len(sample_config)


def test_non_duplicate_key_always_present(sample_config):
    result = squash_config(sample_config)
    assert "APP_NAME" in result.config
    assert result.config["APP_NAME"] == "envoy"


def test_squashed_metadata_lists_removed_keys(sample_config):
    result = squash_config(sample_config, keep="first")
    assert "DATABASE_HOST" in result.squashed.get("DB_HOST", [])


def test_invalid_keep_strategy_raises():
    with pytest.raises(ValueError, match="Invalid keep strategy"):
        squash_config({"A": "1"}, keep="random")


def test_empty_config_returns_empty():
    result = squash_config({})
    assert result.config == {}
    assert result.squash_count() == 0
    assert not result.has_squashed()


def test_summary_no_duplicates():
    result = squash_config({"A": "x", "B": "y"})
    assert "No duplicate" in result.summary()


def test_summary_with_duplicates(sample_config):
    result = squash_config(sample_config, keep="first")
    assert "Squashed" in result.summary()
    assert "->" in result.summary()


def test_all_same_value_leaves_one_key():
    config = {"X": "same", "Y": "same", "Z": "same"}
    result = squash_config(config, keep="first")
    assert len(result.config) == 1
    assert result.squash_count() == 2
