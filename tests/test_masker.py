"""Tests for envoy_diff.masker."""
import pytest
from envoy_diff.masker import mask_config, MaskResult, DEFAULT_MASK


@pytest.fixture
def sample_config():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "AUTH_TOKEN": "tok-xyz",
        "LOG_LEVEL": "INFO",
        "PRIVATE_KEY": "-----BEGIN RSA",
    }


def test_sensitive_keys_are_masked(sample_config):
    result = mask_config(sample_config)
    assert result.masked["DB_PASSWORD"] == DEFAULT_MASK
    assert result.masked["API_KEY"] == DEFAULT_MASK
    assert result.masked["AUTH_TOKEN"] == DEFAULT_MASK
    assert result.masked["PRIVATE_KEY"] == DEFAULT_MASK


def test_non_sensitive_keys_unchanged(sample_config):
    result = mask_config(sample_config)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["LOG_LEVEL"] == "INFO"


def test_masked_keys_listed(sample_config):
    result = mask_config(sample_config)
    assert "DB_PASSWORD" in result.masked_keys
    assert "API_KEY" in result.masked_keys
    assert "APP_NAME" not in result.masked_keys


def test_mask_count(sample_config):
    result = mask_config(sample_config)
    assert result.mask_count() == 4


def test_has_masked_true(sample_config):
    result = mask_config(sample_config)
    assert result.has_masked() is True


def test_has_masked_false():
    result = mask_config({"APP_NAME": "x", "LOG_LEVEL": "DEBUG"})
    assert result.has_masked() is False


def test_custom_mask_string(sample_config):
    result = mask_config(sample_config, mask="[HIDDEN]")
    assert result.masked["DB_PASSWORD"] == "[HIDDEN]"


def test_extra_keys_masked(sample_config):
    result = mask_config(sample_config, extra_keys=["APP_NAME"])
    assert result.masked["APP_NAME"] == DEFAULT_MASK


def test_custom_patterns_override_defaults():
    config = {"DB_PASSWORD": "secret", "MY_CUSTOM": "value"}
    result = mask_config(config, patterns=[r".*custom.*"])
    assert result.masked["MY_CUSTOM"] == DEFAULT_MASK
    assert result.masked["DB_PASSWORD"] == "secret"


def test_summary_with_masked_keys(sample_config):
    result = mask_config(sample_config)
    assert "masked" in result.summary()
    assert str(result.mask_count()) in result.summary()


def test_summary_no_masked():
    result = mask_config({"X": "1"})
    assert result.summary() == "No keys masked."


def test_original_config_unchanged(sample_config):
    result = mask_config(sample_config)
    assert result.original["DB_PASSWORD"] == "s3cr3t"
