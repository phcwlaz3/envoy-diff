"""Tests for envoy_diff.sanitizer."""

import pytest

from envoy_diff.sanitizer import sanitize_config, SanitizeResult


@pytest.fixture()
def sample_config() -> dict:
    return {
        "CLEAN_KEY": "hello_world",
        "CONTROL_KEY": "bad\x01value",
        "NULL_KEY": "null\x00byte",
        "MIXED_KEY": "ok\x07bad\x1fend",
    }


def test_clean_value_unchanged(sample_config):
    result = sanitize_config(sample_config)
    assert result.config["CLEAN_KEY"] == "hello_world"


def test_control_char_stripped(sample_config):
    result = sanitize_config(sample_config, strip_control=True, replacement="")
    assert "\x01" not in result.config["CONTROL_KEY"]


def test_null_byte_replaced(sample_config):
    result = sanitize_config(sample_config, replace_nulls=True, replacement="")
    assert "\x00" not in result.config["NULL_KEY"]


def test_replacement_string_used():
    cfg = {"KEY": "a\x01b"}
    result = sanitize_config(cfg, strip_control=True, replacement="?")
    assert result.config["KEY"] == "a?b"


def test_sanitized_keys_listed(sample_config):
    result = sanitize_config(sample_config)
    assert "CONTROL_KEY" in result.sanitized_keys
    assert "NULL_KEY" in result.sanitized_keys
    assert "CLEAN_KEY" not in result.sanitized_keys


def test_sanitize_count(sample_config):
    result = sanitize_config(sample_config)
    # CONTROL_KEY, NULL_KEY, MIXED_KEY are all dirty
    assert result.sanitize_count() == 3


def test_has_sanitized_true(sample_config):
    result = sanitize_config(sample_config)
    assert result.has_sanitized() is True


def test_has_sanitized_false():
    result = sanitize_config({"A": "clean", "B": "also_clean"})
    assert result.has_sanitized() is False


def test_original_preserved(sample_config):
    result = sanitize_config(sample_config)
    assert result.original == sample_config


def test_allow_only_strips_disallowed():
    cfg = {"KEY": "hello world!"}
    # allow only word chars and underscores
    result = sanitize_config(cfg, strip_control=False, allow_only=r"[^ \w]", replacement="")
    # '!' should be stripped; space is allowed by the pattern
    assert "!" not in result.config["KEY"]
    assert "hello world" in result.config["KEY"]


def test_no_control_stripping_when_disabled():
    cfg = {"KEY": "keep\x01this"}
    result = sanitize_config(cfg, strip_control=False, replace_nulls=False)
    assert result.config["KEY"] == "keep\x01this"
    assert result.sanitize_count() == 0


def test_summary_clean():
    result = sanitize_config({"A": "ok", "B": "fine"})
    assert "nothing sanitized" in result.summary()


def test_summary_dirty(sample_config):
    result = sanitize_config(sample_config)
    assert "sanitized" in result.summary()
    for key in result.sanitized_keys:
        assert key in result.summary()


def test_empty_config_returns_empty():
    result = sanitize_config({})
    assert result.config == {}
    assert result.sanitize_count() == 0
