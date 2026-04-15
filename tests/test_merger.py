"""Tests for envoy_diff.merger module."""

import pytest
from envoy_diff.merger import MergeResult, MergeConflictError, merge_configs


def test_merge_empty_list_returns_empty():
    result = merge_configs([])
    assert result.merged == {}
    assert result.conflicts == {}


def test_merge_single_config_no_conflicts():
    cfg = {"HOST": "localhost", "PORT": "8080"}
    result = merge_configs([cfg])
    assert result.merged == cfg
    assert not result.has_conflicts()


def test_merge_two_configs_no_overlap():
    a = {"HOST": "localhost"}
    b = {"PORT": "8080"}
    result = merge_configs([a, b])
    assert result.merged == {"HOST": "localhost", "PORT": "8080"}
    assert not result.has_conflicts()


def test_merge_detects_conflict_on_differing_values():
    a = {"HOST": "localhost"}
    b = {"HOST": "production.host"}
    result = merge_configs([a, b])
    assert result.has_conflicts()
    assert "HOST" in result.conflicts
    assert "localhost" in result.conflicts["HOST"]
    assert "production.host" in result.conflicts["HOST"]


def test_merge_last_wins_strategy():
    a = {"HOST": "localhost"}
    b = {"HOST": "production.host"}
    result = merge_configs([a, b], strategy="last_wins")
    assert result.merged["HOST"] == "production.host"


def test_merge_first_wins_strategy():
    a = {"HOST": "localhost"}
    b = {"HOST": "production.host"}
    result = merge_configs([a, b], strategy="first_wins")
    assert result.merged["HOST"] == "localhost"


def test_merge_no_conflict_when_values_identical():
    a = {"HOST": "localhost"}
    b = {"HOST": "localhost"}
    result = merge_configs([a, b])
    assert not result.has_conflicts()
    assert result.merged["HOST"] == "localhost"


def test_merge_sources_stored_in_result():
    result = merge_configs([{"A": "1"}], sources=["staging"])
    assert result.sources == ["staging"]


def test_merge_summary_no_conflicts():
    result = merge_configs([{"A": "1"}, {"B": "2"}], sources=["dev", "prod"])
    summary = result.summary()
    assert "2 keys" in summary
    assert "cleanly" in summary


def test_merge_summary_with_conflicts():
    result = merge_configs(
        [{"HOST": "a"}, {"HOST": "b"}], sources=["dev", "prod"]
    )
    summary = result.summary()
    assert "1 conflict" in summary


def test_merge_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_configs([{"A": "1"}], strategy="random")


def test_merge_three_configs_accumulates_conflicts():
    a = {"KEY": "v1"}
    b = {"KEY": "v2"}
    c = {"KEY": "v3"}
    result = merge_configs([a, b, c])
    assert result.has_conflicts()
    assert len(result.conflicts["KEY"]) == 3
