"""Tests for envoy_diff.padder."""
import pytest
from envoy_diff.padder import pad_config, has_padded, pad_count, PadResult


@pytest.fixture
def sample_config():
    return {
        "APP_NAME": "myapp",
        "PORT": "8080",
        "DB_HOST": "localhost",
        "SHORT": "x",
    }


def test_pad_left_default(sample_config):
    result = pad_config(sample_config, width=10)
    assert result.padded["SHORT"] == "x         "
    assert len(result.padded["SHORT"]) == 10


def test_pad_right(sample_config):
    result = pad_config(sample_config, width=10, align="right")
    assert result.padded["SHORT"] == "         x"
    assert len(result.padded["SHORT"]) == 10


def test_already_wide_values_skipped(sample_config):
    result = pad_config(sample_config, width=3)
    assert "APP_NAME" in result.skipped
    assert result.padded["APP_NAME"] == "myapp"


def test_pad_count_correct(sample_config):
    result = pad_config(sample_config, width=10)
    assert pad_count(result) == result.pad_count
    assert result.pad_count > 0


def test_has_padded_true(sample_config):
    result = pad_config(sample_config, width=20)
    assert has_padded(result)


def test_has_padded_false():
    config = {"A": "hello world long enough"}
    result = pad_config(config, width=5)
    assert not has_padded(result)


def test_custom_fill_char(sample_config):
    result = pad_config(sample_config, width=10, fill_char="0")
    assert result.padded["SHORT"].endswith("0")
    assert result.padded["SHORT"] == "x000000000"


def test_specific_keys_only(sample_config):
    result = pad_config(sample_config, width=10, keys=["SHORT"])
    assert result.pad_count == 1
    assert result.padded["APP_NAME"] == "myapp"  # untouched


def test_invalid_fill_char_raises(sample_config):
    with pytest.raises(ValueError, match="fill_char"):
        pad_config(sample_config, width=10, fill_char="ab")


def test_invalid_align_raises(sample_config):
    with pytest.raises(ValueError, match="align"):
        pad_config(sample_config, width=10, align="center")


def test_width_stored_in_result(sample_config):
    result = pad_config(sample_config, width=15)
    assert result.width == 15


def test_summary_includes_width(sample_config):
    result = pad_config(sample_config, width=10)
    assert "10" in result.summary()


def test_summary_mentions_skipped(sample_config):
    result = pad_config(sample_config, width=3)
    assert "skipped" in result.summary()
