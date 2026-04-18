"""Tests for envoy_diff.counter."""
import pytest
from envoy_diff.counter import count_config, CountResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "",
        "AUTH_TOKEN": "abc123",
        "AUTH_ENABLED": "true",
        "FEATURE_FLAG": "false",
        "TIMEOUT": "30",
        "RATIO": "0.75",
        "PLAIN": "hello",
    }


def test_total_count(sample_config):
    result = count_config(sample_config)
    assert result.total == 9


def test_prefix_grouping(sample_config):
    result = count_config(sample_config)
    assert result.by_prefix["DB"] == 3
    assert result.by_prefix["AUTH"] == 2
    assert result.by_prefix["FEATURE"] == 1


def test_no_prefix_key_not_counted(sample_config):
    result = count_config(sample_config)
    # "PLAIN" and "TIMEOUT" and "RATIO" have no underscore
    assert "PLAIN" not in result.by_prefix
    assert "TIMEOUT" not in result.by_prefix


def test_value_type_empty(sample_config):
    result = count_config(sample_config)
    assert result.by_value_type["empty"] == 1


def test_value_type_bool(sample_config):
    result = count_config(sample_config)
    assert result.by_value_type["bool"] == 2


def test_value_type_int(sample_config):
    result = count_config(sample_config)
    assert result.by_value_type["int"] == 2  # 5432, 30


def test_value_type_float(sample_config):
    result = count_config(sample_config)
    assert result.by_value_type["float"] == 1  # 0.75


def test_value_type_str(sample_config):
    result = count_config(sample_config)
    assert result.by_value_type["str"] >= 1


def test_longest_keys_length(sample_config):
    result = count_config(sample_config)
    assert len(result.longest_keys) <= 5
    # longest key by char count should come first
    assert len(result.longest_keys[0]) >= len(result.longest_keys[-1])


def test_longest_values_is_list(sample_config):
    result = count_config(sample_config)
    assert isinstance(result.longest_values, list)


def test_empty_config():
    result = count_config({})
    assert result.total == 0
    assert result.by_prefix == {}
    assert result.by_value_type == {}
    assert result.longest_keys == []
    assert result.longest_values == []


def test_summary_contains_total(sample_config):
    result = count_config(sample_config)
    assert "total=9" in result.summary()


def test_summary_contains_types(sample_config):
    result = count_config(sample_config)
    s = result.summary()
    assert "types=[" in s
