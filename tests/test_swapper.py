"""Tests for envoy_diff.swapper."""
import pytest
from envoy_diff.swapper import swap_config, SwapResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "CACHE_HOST": "redis",
        "CACHE_PORT": "6379",
        "APP_ENV": "production",
    }


def test_no_pairs_returns_original(sample_config):
    result = swap_config(sample_config)
    assert result.config == sample_config


def test_no_pairs_swap_count_zero(sample_config):
    result = swap_config(sample_config)
    assert result.swap_count() == 0


def test_swap_two_keys(sample_config):
    result = swap_config(sample_config, pairs=[("DB_HOST", "CACHE_HOST")])
    assert result.config["DB_HOST"] == "redis"
    assert result.config["CACHE_HOST"] == "localhost"


def test_swap_recorded_in_swapped(sample_config):
    result = swap_config(sample_config, pairs=[("DB_HOST", "CACHE_HOST")])
    assert ("DB_HOST", "CACHE_HOST") in result.swapped


def test_swap_count_correct(sample_config):
    result = swap_config(sample_config, pairs=[
        ("DB_HOST", "CACHE_HOST"),
        ("DB_PORT", "CACHE_PORT"),
    ])
    assert result.swap_count() == 2


def test_has_swaps_true_when_swapped(sample_config):
    result = swap_config(sample_config, pairs=[("DB_HOST", "CACHE_HOST")])
    assert result.has_swaps() is True


def test_has_swaps_false_when_none(sample_config):
    result = swap_config(sample_config)
    assert result.has_swaps() is False


def test_missing_key_skipped(sample_config):
    result = swap_config(sample_config, pairs=[("DB_HOST", "NONEXISTENT")])
    assert "NONEXISTENT" in result.skipped
    assert result.swap_count() == 0


def test_missing_key_does_not_mutate_existing(sample_config):
    result = swap_config(sample_config, pairs=[("DB_HOST", "NONEXISTENT")])
    assert result.config["DB_HOST"] == "localhost"


def test_both_missing_keys_both_skipped(sample_config):
    result = swap_config(sample_config, pairs=[("MISSING_A", "MISSING_B")])
    assert "MISSING_A" in result.skipped
    assert "MISSING_B" in result.skipped


def test_unrelated_keys_preserved(sample_config):
    result = swap_config(sample_config, pairs=[("DB_HOST", "CACHE_HOST")])
    assert result.config["APP_ENV"] == "production"


def test_summary_no_swaps(sample_config):
    result = swap_config(sample_config)
    assert result.summary() == "No swaps performed."


def test_summary_with_swaps(sample_config):
    result = swap_config(sample_config, pairs=[("DB_HOST", "CACHE_HOST")])
    assert "DB_HOST<->CACHE_HOST" in result.summary()
    assert "1 pair" in result.summary()


def test_summary_with_skipped(sample_config):
    result = swap_config(sample_config, pairs=[
        ("DB_HOST", "CACHE_HOST"),
        ("DB_HOST", "GHOST_KEY"),
    ])
    assert "Skipped" in result.summary()
    assert "GHOST_KEY" in result.summary()


def test_empty_pairs_list_returns_original(sample_config):
    result = swap_config(sample_config, pairs=[])
    assert result.config == sample_config
    assert result.swap_count() == 0
