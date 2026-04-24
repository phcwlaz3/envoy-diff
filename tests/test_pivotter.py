"""Tests for envoy_diff.pivotter."""
import pytest
from envoy_diff.pivotter import pivot_config, PivotResult


@pytest.fixture()
def sample_config() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "CACHE_URL": "redis://localhost",
        "CACHE_TTL": "300",
        "DEBUG": "true",
        "PORT": "8080",
    }


def test_pivot_returns_result(sample_config):
    result = pivot_config(sample_config)
    assert isinstance(result, PivotResult)


def test_pivot_groups_db_keys(sample_config):
    result = pivot_config(sample_config)
    assert "DB" in result.pivoted
    assert result.pivoted["DB"] == {"HOST": "localhost", "PORT": "5432", "NAME": "mydb"}


def test_pivot_groups_cache_keys(sample_config):
    result = pivot_config(sample_config)
    assert "CACHE" in result.pivoted
    assert result.pivoted["CACHE"] == {"URL": "redis://localhost", "TTL": "300"}


def test_pivot_ungrouped_keys_no_separator(sample_config):
    result = pivot_config(sample_config)
    assert "DEBUG" in result.ungrouped
    assert "PORT" in result.ungrouped


def test_pivot_ungrouped_in_pivoted_dict(sample_config):
    result = pivot_config(sample_config)
    assert "_ungrouped" in result.pivoted


def test_pivot_group_count(sample_config):
    result = pivot_config(sample_config)
    assert result.group_count == 2


def test_pivot_original_count(sample_config):
    result = pivot_config(sample_config)
    assert result.original_count == len(sample_config)


def test_pivot_has_ungrouped_true(sample_config):
    result = pivot_config(sample_config)
    assert result.has_ungrouped() is True


def test_pivot_has_ungrouped_false():
    config = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = pivot_config(config)
    assert result.has_ungrouped() is False


def test_pivot_empty_config():
    result = pivot_config({})
    assert result.pivoted == {}
    assert result.group_count == 0
    assert result.original_count == 0
    assert not result.has_ungrouped()


def test_pivot_custom_separator():
    config = {"db.host": "localhost", "db.port": "5432", "debug": "true"}
    result = pivot_config(config, separator=".")
    assert "db" in result.pivoted
    assert result.pivoted["db"] == {"host": "localhost", "port": "5432"}


def test_pivot_summary_contains_key_info(sample_config):
    result = pivot_config(sample_config)
    s = result.summary()
    assert "7 keys" in s
    assert "2 group" in s
    assert "ungrouped" in s


def test_pivot_min_prefix_length_filters_short_prefix():
    config = {"A_VALUE": "x", "DB_HOST": "localhost"}
    result = pivot_config(config, min_prefix_length=2)
    # "A" has length 1 < 2, so it should be ungrouped
    assert "A" not in result.pivoted
    assert "A_VALUE" in result.ungrouped
    assert "DB" in result.pivoted
