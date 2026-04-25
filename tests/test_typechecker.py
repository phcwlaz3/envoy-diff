"""Tests for envoy_diff.typechecker."""
import pytest
from envoy_diff.typechecker import (
    TypeCheckResult,
    TypeViolation,
    typecheck_config,
)


@pytest.fixture
def sample_config():
    return {
        "PORT": "8080",
        "DEBUG": "true",
        "TIMEOUT": "30",
        "RATE": "0.95",
        "API_URL": "https://api.example.com",
        "ADMIN_EMAIL": "admin@example.com",
        "NAME": "my-service",
    }


def test_all_valid_returns_no_violations(sample_config):
    rules = {
        "PORT": "port",
        "DEBUG": "bool",
        "TIMEOUT": "int",
        "RATE": "float",
        "API_URL": "url",
        "ADMIN_EMAIL": "email",
    }
    result = typecheck_config(sample_config, rules)
    assert not result.has_violations
    assert result.violation_count == 0


def test_invalid_int_flagged():
    config = {"TIMEOUT": "thirty"}
    result = typecheck_config(config, {"TIMEOUT": "int"})
    assert result.has_violations
    assert result.violations[0].key == "TIMEOUT"
    assert result.violations[0].expected_type == "int"


def test_invalid_float_flagged():
    config = {"RATE": "fast"}
    result = typecheck_config(config, {"RATE": "float"})
    assert result.has_violations


def test_invalid_bool_flagged():
    config = {"DEBUG": "maybe"}
    result = typecheck_config(config, {"DEBUG": "bool"})
    assert result.has_violations


def test_valid_bool_variants_accepted():
    for val in ("true", "false", "1", "0", "yes", "no", "True", "FALSE"):
        config = {"FLAG": val}
        result = typecheck_config(config, {"FLAG": "bool"})
        assert not result.has_violations, f"Expected {val!r} to be valid bool"


def test_invalid_url_flagged():
    config = {"API_URL": "not-a-url"}
    result = typecheck_config(config, {"API_URL": "url"})
    assert result.has_violations


def test_invalid_email_flagged():
    config = {"ADMIN_EMAIL": "not-an-email"}
    result = typecheck_config(config, {"ADMIN_EMAIL": "email"})
    assert result.has_violations


def test_invalid_port_flagged():
    config = {"PORT": "99999"}
    result = typecheck_config(config, {"PORT": "port"})
    assert result.has_violations


def test_key_missing_from_config_skipped():
    config = {"OTHER": "value"}
    result = typecheck_config(config, {"PORT": "port"})
    assert not result.has_violations
    assert len(result.checked) == 0


def test_unknown_type_passes_through():
    config = {"THING": "anything"}
    result = typecheck_config(config, {"THING": "uuid"})
    assert not result.has_violations


def test_summary_all_pass(sample_config):
    result = typecheck_config(sample_config, {"PORT": "port", "DEBUG": "bool"})
    assert "pass" in result.summary()


def test_summary_with_violations():
    config = {"PORT": "bad"}
    result = typecheck_config(config, {"PORT": "int"})
    assert "failed" in result.summary()


def test_violation_to_dict():
    v = TypeViolation(key="PORT", value="bad", expected_type="int")
    d = v.to_dict()
    assert d == {"key": "PORT", "value": "bad", "expected_type": "int"}


def test_checked_keys_populated(sample_config):
    rules = {"PORT": "port", "DEBUG": "bool"}
    result = typecheck_config(sample_config, rules)
    assert set(result.checked.keys()) == {"PORT", "DEBUG"}
