"""Tests for envoy_diff.clamper."""
import pytest
from envoy_diff.clamper import clamp_config, ClampResult


@pytest.fixture
def sample_config():
    return {
        "SHORT": "hi",
        "EXACT": "hello",
        "LONG": "this_is_a_very_long_value",
        "EMPTY": "",
    }


def test_no_bounds_returns_original(sample_config):
    result = clamp_config(sample_config)
    assert result.config == sample_config
    assert result.clamp_count() == 0


def test_max_len_truncates_long_value(sample_config):
    result = clamp_config(sample_config, max_len=5)
    assert result.config["LONG"] == "this_"


def test_max_len_leaves_short_values_unchanged(sample_config):
    result = clamp_config(sample_config, max_len=10)
    assert result.config["SHORT"] == "hi"
    assert result.config["EXACT"] == "hello"


def test_min_len_pads_short_value(sample_config):
    result = clamp_config(sample_config, min_len=5)
    assert result.config["SHORT"] == "hi   "
    assert len(result.config["SHORT"]) == 5


def test_min_len_leaves_long_values_unchanged(sample_config):
    result = clamp_config(sample_config, min_len=3)
    assert result.config["LONG"] == sample_config["LONG"]


def test_custom_pad_char(sample_config):
    result = clamp_config(sample_config, min_len=6, pad_char="0")
    assert result.config["SHORT"] == "hi0000"


def test_both_bounds_applied(sample_config):
    result = clamp_config(sample_config, min_len=4, max_len=8)
    assert result.config["SHORT"] == "hi  "    # padded
    assert result.config["LONG"] == "this_is_"  # truncated
    assert result.config["EXACT"] == "hello"    # unchanged


def test_clamped_list_populated(sample_config):
    result = clamp_config(sample_config, max_len=4)
    keys_clamped = [k for k, _, _ in result.clamped]
    assert "LONG" in keys_clamped
    assert "SHORT" not in keys_clamped


def test_clamp_count_correct(sample_config):
    result = clamp_config(sample_config, max_len=4)
    assert result.clamp_count() == result.clamped.__len__()


def test_has_clamped_true_when_truncated(sample_config):
    result = clamp_config(sample_config, max_len=3)
    assert result.has_clamped() is True


def test_has_clamped_false_when_no_change(sample_config):
    result = clamp_config(sample_config, max_len=100)
    assert result.has_clamped() is False


def test_specific_keys_only(sample_config):
    result = clamp_config(sample_config, max_len=3, keys=["LONG"])
    assert result.config["LONG"] == "thi"
    assert result.config["EXACT"] == "hello"  # untouched


def test_missing_key_in_keys_recorded_as_skipped(sample_config):
    result = clamp_config(sample_config, max_len=3, keys=["LONG", "NONEXISTENT"])
    assert "NONEXISTENT" in result.skipped


def test_invalid_bounds_raise_value_error(sample_config):
    with pytest.raises(ValueError, match="min_len"):
        clamp_config(sample_config, min_len=10, max_len=5)


def test_summary_no_clamped(sample_config):
    result = clamp_config(sample_config, max_len=100)
    assert "none clamped" in result.summary()


def test_summary_with_clamped(sample_config):
    result = clamp_config(sample_config, max_len=3)
    assert "clamped" in result.summary()


def test_empty_config_returns_empty():
    result = clamp_config({})
    assert result.config == {}
    assert result.clamp_count() == 0
