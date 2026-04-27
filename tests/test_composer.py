"""Tests for envoy_diff.composer."""
import pytest
from envoy_diff.composer import ComposeResult, compose_configs


@pytest.fixture
def base_fragment():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "development"}


@pytest.fixture
def override_fragment():
    return {"DB_HOST": "prod-db", "CACHE_URL": "redis://cache:6379"}


def test_compose_empty_fragments_returns_empty():
    result = compose_configs({})
    assert result.config == {}
    assert result.fragment_count == 0


def test_compose_single_fragment_no_conflicts(base_fragment):
    result = compose_configs({"base": base_fragment})
    assert result.config == base_fragment
    assert result.fragments_used == ["base"]
    assert not result.has_conflicts


def test_compose_two_non_overlapping_fragments():
    a = {"KEY_A": "1"}
    b = {"KEY_B": "2"}
    result = compose_configs({"a": a, "b": b})
    assert result.config == {"KEY_A": "1", "KEY_B": "2"}
    assert result.fragment_count == 2


def test_compose_last_wins_on_conflict(base_fragment, override_fragment):
    result = compose_configs(
        {"base": base_fragment, "override": override_fragment},
        order=["base", "override"],
        on_conflict="last_wins",
    )
    assert result.config["DB_HOST"] == "prod-db"


def test_compose_first_wins_on_conflict(base_fragment, override_fragment):
    result = compose_configs(
        {"base": base_fragment, "override": override_fragment},
        order=["base", "override"],
        on_conflict="first_wins",
    )
    assert result.config["DB_HOST"] == "localhost"


def test_compose_conflict_recorded(base_fragment, override_fragment):
    result = compose_configs(
        {"base": base_fragment, "override": override_fragment},
        order=["base", "override"],
    )
    assert "DB_HOST" in result.conflicts


def test_compose_no_conflict_when_values_identical():
    a = {"KEY": "same"}
    b = {"KEY": "same"}
    result = compose_configs({"a": a, "b": b})
    assert not result.has_conflicts
    assert result.config["KEY"] == "same"


def test_compose_skips_missing_fragment_names(base_fragment):
    result = compose_configs(
        {"base": base_fragment},
        order=["base", "nonexistent"],
    )
    assert "nonexistent" in result.skipped_fragments
    assert result.fragment_count == 1


def test_compose_order_respected():
    fragments = {"z": {"K": "z"}, "a": {"K": "a"}}
    result = compose_configs(fragments, order=["z", "a"], on_conflict="last_wins")
    assert result.config["K"] == "a"
    result2 = compose_configs(fragments, order=["a", "z"], on_conflict="last_wins")
    assert result2.config["K"] == "z"


def test_compose_summary_string(base_fragment, override_fragment):
    result = compose_configs(
        {"base": base_fragment, "override": override_fragment},
        order=["base", "override"],
    )
    s = result.summary()
    assert "2 fragment(s) composed" in s
    assert "conflict" in s


def test_compose_unordered_fragments_sorted_alphabetically():
    fragments = {"z": {"Z": "1"}, "a": {"A": "2"}, "m": {"M": "3"}}
    result = compose_configs(fragments)
    assert result.fragments_used == ["a", "m", "z"]
