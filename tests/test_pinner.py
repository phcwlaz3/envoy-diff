"""Tests for envoy_diff.pinner."""

import pytest
from envoy_diff.pinner import PinResult, pin_config, check_drift


@pytest.fixture
def sample_config():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


def test_pin_all_keys(sample_config):
    result = pin_config(sample_config)
    assert result.pinned == sample_config
    assert result.unpinned == []


def test_pin_selected_keys(sample_config):
    result = pin_config(sample_config, keys=["DB_HOST", "APP_ENV"])
    assert result.pinned == {"DB_HOST": "localhost", "APP_ENV": "production"}
    assert "DB_PORT" not in result.pinned


def test_pin_missing_keys_reported(sample_config):
    result = pin_config(sample_config, keys=["DB_HOST", "MISSING_KEY"])
    assert "MISSING_KEY" in result.unpinned
    assert "DB_HOST" in result.pinned


def test_pin_count(sample_config):
    result = pin_config(sample_config)
    assert result.pin_count == 3


def test_no_drift_when_config_matches(sample_config):
    pins = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = check_drift(sample_config, pins)
    assert not result.has_drift()
    assert result.drift_count == 0


def test_drift_detected_on_changed_value(sample_config):
    pins = {"DB_HOST": "remotehost"}
    result = check_drift(sample_config, pins)
    assert result.has_drift()
    assert "DB_HOST" in result.drifted
    assert result.drifted["DB_HOST"] == ("remotehost", "localhost")


def test_drift_detected_on_missing_key():
    config = {"APP_ENV": "staging"}
    pins = {"APP_ENV": "staging", "DB_HOST": "localhost"}
    result = check_drift(config, pins)
    assert "DB_HOST" in result.drifted
    assert result.drifted["DB_HOST"][1] is None


def test_summary_no_issues(sample_config):
    result = pin_config(sample_config)
    assert "pinned" in result.summary()


def test_summary_with_drift(sample_config):
    pins = {"DB_HOST": "other"}
    result = check_drift(sample_config, pins)
    assert "drifted" in result.summary()


def test_summary_with_unpinned(sample_config):
    result = pin_config(sample_config, keys=["DB_HOST", "GHOST"])
    assert "unpinned" in result.summary()
