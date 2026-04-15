"""Tests for envoy_diff.validator module."""

import pytest
from envoy_diff.validator import (
    ValidationResult,
    validate_config,
    validate_keys_present,
    validate_no_empty_values,
)


SAMPLE_CONFIG = {
    "APP_ENV": "production",
    "DB_HOST": "db.example.com",
    "DB_PORT": "5432",
    "SECRET_KEY": "s3cr3t",
    "OPTIONAL_FEATURE": "",
}


def test_validate_keys_present_all_present():
    result = validate_keys_present(SAMPLE_CONFIG, {"APP_ENV", "DB_HOST"})
    assert result.valid is True
    assert result.errors == []


def test_validate_keys_present_missing_key():
    result = validate_keys_present(SAMPLE_CONFIG, {"APP_ENV", "MISSING_KEY"})
    assert result.valid is False
    assert any("MISSING_KEY" in e for e in result.errors)


def test_validate_keys_present_multiple_missing():
    result = validate_keys_present(SAMPLE_CONFIG, {"ALPHA", "BETA", "APP_ENV"})
    assert result.valid is False
    assert len(result.errors) == 2


def test_validate_no_empty_values_warns_on_empty():
    result = validate_no_empty_values(SAMPLE_CONFIG)
    assert result.valid is True
    assert any("OPTIONAL_FEATURE" in w for w in result.warnings)


def test_validate_no_empty_values_ignore_key():
    result = validate_no_empty_values(SAMPLE_CONFIG, ignore_keys={"OPTIONAL_FEATURE"})
    assert result.valid is True
    assert result.warnings == []


def test_validate_no_empty_values_no_empty():
    config = {"KEY": "value", "OTHER": "data"}
    result = validate_no_empty_values(config)
    assert result.valid is True
    assert result.warnings == []


def test_validate_config_passes_clean_config():
    config = {"APP_ENV": "staging", "DB_HOST": "localhost"}
    result = validate_config(config, required_keys={"APP_ENV", "DB_HOST"})
    assert result.valid is True
    assert result.errors == []
    assert result.warnings == []


def test_validate_config_fails_on_missing_required():
    result = validate_config(SAMPLE_CONFIG, required_keys={"APP_ENV", "NONEXISTENT"})
    assert result.valid is False
    assert any("NONEXISTENT" in e for e in result.errors)


def test_validate_config_warns_on_empty_value():
    result = validate_config(SAMPLE_CONFIG)
    assert result.valid is True
    assert any("OPTIONAL_FEATURE" in w for w in result.warnings)


def test_validate_config_no_required_keys():
    result = validate_config(SAMPLE_CONFIG)
    assert result.valid is True


def test_validation_result_bool_true():
    assert bool(ValidationResult(valid=True)) is True


def test_validation_result_bool_false():
    assert bool(ValidationResult(valid=False, errors=["oops"])) is False
