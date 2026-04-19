"""Tests for envoy_diff.resolver."""

import pytest

from envoy_diff.resolver import ResolveResult, resolve_config


@pytest.fixture
def base_config():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


@pytest.fixture
def override_config():
    return {"HOST": "prod.example.com", "PORT": "5432"}


def test_resolve_uses_config_values(base_config, override_config):
    result = resolve_config(override_config, base=base_config)
    assert result.resolved["HOST"] == "prod.example.com"
    assert result.resolved["PORT"] == "5432"


def test_resolve_falls_back_to_base(base_config, override_config):
    result = resolve_config(override_config, base=base_config)
    assert result.resolved["DEBUG"] == "false"


def test_resolve_no_base_returns_config_only():
    config = {"FOO": "bar", "BAZ": "qux"}
    result = resolve_config(config)
    assert result.resolved == {"FOO": "bar", "BAZ": "qux"}


def test_resolve_system_env_overrides_config(monkeypatch, base_config):
    monkeypatch.setenv("HOST", "env-host.internal")
    config = {"HOST": "config-host"}
    result = resolve_config(config, base=base_config, use_system_env=True)
    assert result.resolved["HOST"] == "env-host.internal"


def test_resolve_system_env_override_tracked(monkeypatch):
    monkeypatch.setenv("API_KEY", "from-env")
    config = {"API_KEY": "from-config"}
    result = resolve_config(config, use_system_env=True)
    assert "API_KEY" in result.overrides


def test_resolve_no_override_when_values_match(monkeypatch):
    monkeypatch.setenv("PORT", "8080")
    config = {"PORT": "8080"}
    result = resolve_config(config, use_system_env=True)
    assert "PORT" not in result.overrides


def test_resolve_missing_required_keys(base_config):
    result = resolve_config(base_config, required_keys=["HOST", "SECRET_KEY"])
    assert "SECRET_KEY" in result.missing
    assert "HOST" not in result.missing


def test_resolve_empty_value_counts_as_missing():
    config = {"TOKEN": ""}
    result = resolve_config(config, required_keys=["TOKEN"])
    assert "TOKEN" in result.missing


def test_resolve_result_summary_all_ok():
    config = {"A": "1", "B": "2"}
    result = resolve_config(config)
    assert "2 keys resolved" in result.summary()


def test_resolve_result_summary_with_missing():
    config = {"A": "1"}
    result = resolve_config(config, required_keys=["A", "B"])
    assert "missing" in result.summary()
    assert "B" in result.summary()


def test_resolve_override_count_property(monkeypatch):
    monkeypatch.setenv("X", "env-val")
    config = {"X": "config-val", "Y": "other"}
    result = resolve_config(config, use_system_env=True)
    assert result.override_count == 1


def test_resolve_missing_count_property():
    result = resolve_config({}, required_keys=["A", "B", "C"])
    assert result.missing_count == 3


def test_resolve_base_keys_not_in_config_are_included(base_config):
    """Keys present only in base should appear in resolved output."""
    config = {"HOST": "override-host"}
    result = resolve_config(config, base=base_config)
    assert "PORT" in result.resolved
    assert "DEBUG" in result.resolved
    assert result.resolved["PORT"] == "5432"
