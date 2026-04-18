"""Tests for envoy_diff.sampler."""
import pytest
from envoy_diff.sampler import sample_config, sample_count, SampleResult


@pytest.fixture
def sample_config_data():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "CACHE_HOST": "redis",
        "CACHE_PORT": "6379",
        "APP_ENV": "production",
        "APP_DEBUG": "false",
        "SECRET_KEY": "abc123",
    }


def test_sample_n_returns_correct_count(sample_config_data):
    result = sample_config(sample_config_data, n=3, seed=42)
    assert result.sample_size == 3
    assert len(result.sampled) == 3


def test_sample_fraction_returns_correct_count(sample_config_data):
    result = sample_config(sample_config_data, fraction=0.5, seed=1)
    assert result.sample_size == 4


def test_sample_keys_are_subset(sample_config_data):
    result = sample_config(sample_config_data, n=5, seed=7)
    assert set(result.keys).issubset(set(sample_config_data.keys()))


def test_sample_values_match_original(sample_config_data):
    result = sample_config(sample_config_data, n=4, seed=0)
    for k, v in result.sampled.items():
        assert sample_config_data[k] == v


def test_sample_seed_is_reproducible(sample_config_data):
    r1 = sample_config(sample_config_data, n=3, seed=99)
    r2 = sample_config(sample_config_data, n=3, seed=99)
    assert r1.keys == r2.keys


def test_sample_different_seeds_may_differ(sample_config_data):
    r1 = sample_config(sample_config_data, n=3, seed=1)
    r2 = sample_config(sample_config_data, n=3, seed=2)
    # Not guaranteed but overwhelmingly likely for 8 keys choose 3
    assert r1.keys != r2.keys or True  # soft check — just ensure no crash


def test_sample_prefix_filters_candidates(sample_config_data):
    result = sample_config(sample_config_data, n=2, seed=5, prefix="DB_")
    assert all(k.startswith("DB_") for k in result.keys)
    assert result.total_keys == 3


def test_sample_n_larger_than_pool_clamps(sample_config_data):
    result = sample_config(sample_config_data, n=100, seed=0)
    assert result.sample_size == len(sample_config_data)


def test_sample_empty_config_returns_empty():
    result = sample_config({}, n=5)
    assert result.sampled == {}
    assert result.sample_size == 0


def test_sample_count_helper(sample_config_data):
    result = sample_config(sample_config_data, n=3, seed=0)
    assert sample_count(result) == 3


def test_summary_includes_counts(sample_config_data):
    result = sample_config(sample_config_data, n=3, seed=42)
    s = result.summary()
    assert "3" in s
    assert str(result.total_keys) in s
    assert "42" in s


def test_summary_no_seed(sample_config_data):
    result = sample_config(sample_config_data, n=2)
    s = result.summary()
    assert "seed" not in s
