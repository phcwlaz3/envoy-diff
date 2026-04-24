"""Tests for envoy_diff.censor."""
import pytest
from envoy_diff.censor import censor_config, CensorResult, _DEFAULT_PLACEHOLDER


@pytest.fixture()
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "APP_SECRET": "xyz789",
        "AUTH_TOKEN": "tok_live_abc",
        "LOG_LEVEL": "INFO",
        "FEATURE_FLAG": "true",
    }


def test_sensitive_keys_are_censored(sample_config):
    result = censor_config(sample_config)
    assert result.config["DB_PASSWORD"] == _DEFAULT_PLACEHOLDER
    assert result.config["API_KEY"] == _DEFAULT_PLACEHOLDER
    assert result.config["APP_SECRET"] == _DEFAULT_PLACEHOLDER
    assert result.config["AUTH_TOKEN"] == _DEFAULT_PLACEHOLDER


def test_non_sensitive_keys_unchanged(sample_config):
    result = censor_config(sample_config)
    assert result.config["DB_HOST"] == "localhost"
    assert result.config["LOG_LEVEL"] == "INFO"
    assert result.config["FEATURE_FLAG"] == "true"


def test_censored_keys_listed(sample_config):
    result = censor_config(sample_config)
    assert "DB_PASSWORD" in result.censored_keys
    assert "API_KEY" in result.censored_keys
    assert "DB_HOST" not in result.censored_keys


def test_censor_count(sample_config):
    result = censor_config(sample_config)
    assert result.censor_count() == 4


def test_has_censored_true(sample_config):
    result = censor_config(sample_config)
    assert result.has_censored() is True


def test_has_censored_false():
    result = censor_config({"LOG_LEVEL": "DEBUG", "PORT": "8080"})
    assert result.has_censored() is False


def test_custom_placeholder(sample_config):
    result = censor_config(sample_config, placeholder="<REDACTED>")
    assert result.config["DB_PASSWORD"] == "<REDACTED>"
    assert result.placeholder == "<REDACTED>"


def test_custom_patterns():
    config = {"MY_CUSTOM_HIDDEN": "value", "VISIBLE": "ok"}
    result = censor_config(config, patterns=[r".*hidden.*"])
    assert result.config["MY_CUSTOM_HIDDEN"] == _DEFAULT_PLACEHOLDER
    assert result.config["VISIBLE"] == "ok"


def test_extra_keys_explicit():
    config = {"PLAIN_KEY": "some_value", "OTHER": "fine"}
    result = censor_config(config, extra_keys=["PLAIN_KEY"])
    assert result.config["PLAIN_KEY"] == _DEFAULT_PLACEHOLDER
    assert result.config["OTHER"] == "fine"


def test_empty_config_returns_empty():
    result = censor_config({})
    assert result.config == {}
    assert result.censor_count() == 0


def test_summary_no_censored():
    result = censor_config({"PORT": "3000"})
    assert result.summary() == "No keys censored."


def test_summary_with_censored(sample_config):
    result = censor_config(sample_config)
    assert "censored" in result.summary()
    assert str(result.censor_count()) in result.summary()
