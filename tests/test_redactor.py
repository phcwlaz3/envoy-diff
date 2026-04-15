"""Tests for envoy_diff.redactor."""

import pytest
from envoy_diff.redactor import (
    DEFAULT_MASK,
    RedactionResult,
    redact_config,
)


@pytest.fixture
def sample_config():
    return {
        "DATABASE_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "APP_NAME": "myapp",
        "PORT": "8080",
        "SECRET_TOKEN": "tok_xyz",
        "DEBUG": "true",
    }


def test_redact_sensitive_keys_are_masked(sample_config):
    result = redact_config(sample_config)
    assert result.redacted["DATABASE_PASSWORD"] == DEFAULT_MASK
    assert result.redacted["API_KEY"] == DEFAULT_MASK
    assert result.redacted["SECRET_TOKEN"] == DEFAULT_MASK


def test_redact_non_sensitive_keys_unchanged(sample_config):
    result = redact_config(sample_config)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["PORT"] == "8080"
    assert result.redacted["DEBUG"] == "true"


def test_redact_tracks_redacted_keys(sample_config):
    result = redact_config(sample_config)
    assert "DATABASE_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys
    assert "SECRET_TOKEN" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_redact_count(sample_config):
    result = redact_config(sample_config)
    assert result.redaction_count == 3


def test_redact_original_unchanged(sample_config):
    result = redact_config(sample_config)
    assert result.original["DATABASE_PASSWORD"] == "s3cr3t"
    assert result.original["API_KEY"] == "abc123"


def test_redact_empty_config():
    result = redact_config({})
    assert result.redacted == {}
    assert result.redacted_keys == []
    assert result.redaction_count == 0


def test_redact_custom_mask(sample_config):
    result = redact_config(sample_config, mask="[HIDDEN]")
    assert result.redacted["API_KEY"] == "[HIDDEN]"


def test_redact_custom_pattern():
    config = {"MY_INTERNAL_VAR": "secret_value", "OTHER": "fine"}
    result = redact_config(config, patterns=[r"(?i)internal"])
    assert result.redacted["MY_INTERNAL_VAR"] == DEFAULT_MASK
    assert result.redacted["OTHER"] == "fine"


def test_redact_summary_with_redactions(sample_config):
    result = redact_config(sample_config)
    summary = result.summary()
    assert "redacted" in summary
    assert str(result.redaction_count) in summary


def test_redact_summary_no_redactions():
    result = redact_config({"APP": "ok", "PORT": "80"})
    assert result.summary() == "No sensitive keys detected."


def test_redact_case_insensitive_key():
    config = {"db_password": "hunter2"}
    result = redact_config(config)
    assert result.redacted["db_password"] == DEFAULT_MASK
