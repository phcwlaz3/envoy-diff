"""Tests for envoy_diff.inverter."""
import pytest

from envoy_diff.inverter import InvertResult, invert_config


@pytest.fixture()
def sample_config() -> dict:
    return {
        "APP_HOST": "localhost",
        "DB_HOST": "db.internal",
        "CACHE_HOST": "cache.internal",
    }


def test_invert_swaps_keys_and_values(sample_config):
    result = invert_config(sample_config)
    assert result.inverted["localhost"] == "APP_HOST"
    assert result.inverted["db.internal"] == "DB_HOST"
    assert result.inverted["cache.internal"] == "CACHE_HOST"


def test_invert_original_count(sample_config):
    result = invert_config(sample_config)
    assert result.original_count == 3


def test_invert_no_collisions_when_values_unique(sample_config):
    result = invert_config(sample_config)
    assert not result.has_collisions()
    assert result.collision_count() == 0


def test_invert_detects_collision():
    config = {"A": "same", "B": "same"}
    result = invert_config(config)
    assert result.has_collisions()
    assert "same" in result.collisions


def test_invert_last_wins_strategy():
    config = {"A": "same", "B": "same"}
    result = invert_config(config, on_collision="last")
    assert result.inverted["same"] == "B"


def test_invert_first_wins_strategy():
    config = {"A": "same", "B": "same"}
    result = invert_config(config, on_collision="first")
    assert result.inverted["same"] == "A"


def test_invert_empty_config():
    result = invert_config({})
    assert result.inverted == {}
    assert result.original_count == 0
    assert not result.has_collisions()


def test_invert_single_entry():
    result = invert_config({"KEY": "value"})
    assert result.inverted == {"value": "KEY"}


def test_invert_invalid_strategy_raises():
    with pytest.raises(ValueError, match="on_collision"):
        invert_config({"A": "x"}, on_collision="random")


def test_invert_summary_no_collisions(sample_config):
    result = invert_config(sample_config)
    s = result.summary()
    assert "3 key(s) processed" in s
    assert "collision" not in s


def test_invert_summary_with_collisions():
    config = {"A": "dup", "B": "dup", "C": "unique"}
    result = invert_config(config)
    s = result.summary()
    assert "collision" in s
    assert "dup" in s


def test_invert_result_is_dataclass(sample_config):
    result = invert_config(sample_config)
    assert isinstance(result, InvertResult)
