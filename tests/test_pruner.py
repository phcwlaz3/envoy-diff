"""Tests for envoy_diff.pruner."""
import pytest
from envoy_diff.pruner import prune_config


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "CACHE_HOST": "redis",
        "CACHE_TTL": "300",
        "APP_DEBUG": "true",
        "APP_SECRET": "s3cr3t",
    }


def test_no_filters_returns_all(sample_config):
    result = prune_config(sample_config)
    assert result.pruned == sample_config
    assert result.removed_keys == []


def test_prune_explicit_keys(sample_config):
    result = prune_config(sample_config, keys=["DB_HOST", "APP_DEBUG"])
    assert "DB_HOST" not in result.pruned
    assert "APP_DEBUG" not in result.pruned
    assert "DB_PORT" in result.pruned


def test_prune_pattern(sample_config):
    result = prune_config(sample_config, patterns=["DB_*"])
    assert "DB_HOST" not in result.pruned
    assert "DB_PORT" not in result.pruned
    assert "CACHE_HOST" in result.pruned


def test_prune_multiple_patterns(sample_config):
    result = prune_config(sample_config, patterns=["DB_*", "CACHE_*"])
    assert result.removed_count() == 4
    assert set(result.pruned.keys()) == {"APP_DEBUG", "APP_SECRET"}


def test_prune_keys_and_patterns_combined(sample_config):
    result = prune_config(sample_config, keys=["APP_SECRET"], patterns=["DB_*"])
    assert "APP_SECRET" not in result.pruned
    assert "DB_HOST" not in result.pruned
    assert "CACHE_HOST" in result.pruned


def test_removed_keys_listed(sample_config):
    result = prune_config(sample_config, keys=["DB_HOST"])
    assert "DB_HOST" in result.removed_keys


def test_has_removals_true(sample_config):
    result = prune_config(sample_config, keys=["DB_HOST"])
    assert result.has_removals() is True


def test_has_removals_false(sample_config):
    result = prune_config(sample_config)
    assert result.has_removals() is False


def test_removed_count(sample_config):
    result = prune_config(sample_config, patterns=["APP_*"])
    assert result.removed_count() == 2


def test_summary_no_removals(sample_config):
    result = prune_config(sample_config)
    assert result.summary() == "No keys pruned."


def test_summary_with_removals(sample_config):
    result = prune_config(sample_config, keys=["DB_HOST"])
    assert "1 key(s)" in result.summary()
    assert "DB_HOST" in result.summary()


def test_original_config_unchanged(sample_config):
    original_copy = dict(sample_config)
    prune_config(sample_config, patterns=["DB_*"])
    assert sample_config == original_copy


def test_prune_nonexistent_key_ignored(sample_config):
    """Pruning a key that doesn't exist should not raise and should not affect result."""
    result = prune_config(sample_config, keys=["NONEXISTENT_KEY"])
    assert result.pruned == sample_config
    assert result.removed_keys == []
    assert result.has_removals() is False


def test_prune_empty_config():
    """Pruning an empty config should return empty pruned dict with no removals."""
    result = prune_config({}, keys=["DB_HOST"], patterns=["APP_*"])
    assert result.pruned == {}
    assert result.removed_keys == []
    assert result.removed_count() == 0
