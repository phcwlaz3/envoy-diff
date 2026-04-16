"""Tests for envoy_diff.grouper."""
import pytest
from envoy_diff.grouper import group_config, GroupResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_KEY": "AKID",
        "AWS_SECRET": "secret",
        "LOG_LEVEL": "info",
        "STANDALONE": "value",
    }


def test_auto_detect_groups_by_prefix(sample_config):
    result = group_config(sample_config)
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_auto_detect_groups_correct_keys(sample_config):
    result = group_config(sample_config)
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT", "DB_NAME"}
    assert set(result.groups["AWS"]) == {"AWS_KEY", "AWS_SECRET"}


def test_single_occurrence_not_auto_grouped(sample_config):
    result = group_config(sample_config)
    # LOG appears once, should not be auto-grouped
    assert "LOG" not in result.groups
    assert "LOG_LEVEL" in result.ungrouped


def test_standalone_key_in_ungrouped(sample_config):
    result = group_config(sample_config)
    assert "STANDALONE" in result.ungrouped


def test_explicit_prefix_overrides_auto(sample_config):
    result = group_config(sample_config, prefixes=["LOG"], auto_detect=False)
    assert "LOG" in result.groups
    assert "LOG_LEVEL" in result.groups["LOG"]


def test_auto_detect_false_no_groups_without_prefixes(sample_config):
    result = group_config(sample_config, auto_detect=False)
    assert result.group_count() == 0
    assert len(result.ungrouped) == len(sample_config)


def test_empty_config_returns_empty_result():
    result = group_config({})
    assert result.group_count() == 0
    assert result.ungrouped == {}


def test_group_count(sample_config):
    result = group_config(sample_config)
    assert result.group_count() == 2  # DB and AWS


def test_summary_contains_group_names(sample_config):
    result = group_config(sample_config)
    s = result.summary()
    assert "DB" in s
    assert "AWS" in s


def test_summary_no_groups():
    result = GroupResult(ungrouped={"A": "1"})
    assert result.summary() == "No groups; ungrouped: 1"
