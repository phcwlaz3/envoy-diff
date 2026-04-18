import pytest
from envoy_diff.freezer import freeze_config, check_drift, FreezeResult


@pytest.fixture
def base_config():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "staging"}


def test_freeze_returns_copy(base_config):
    frozen = freeze_config(base_config)
    assert frozen == base_config
    assert frozen is not base_config


def test_no_drift_when_identical(base_config):
    result = check_drift(base_config, dict(base_config))
    assert not result.has_drift
    assert result.drift_count == 0


def test_detects_changed_value(base_config):
    live = dict(base_config)
    live["DB_HOST"] = "prod-db"
    result = check_drift(base_config, live)
    assert result.has_drift
    assert "DB_HOST" in result.drifted


def test_detects_added_key(base_config):
    live = dict(base_config)
    live["NEW_KEY"] = "new_value"
    result = check_drift(base_config, live)
    assert "NEW_KEY" in result.added


def test_detects_removed_key(base_config):
    live = {k: v for k, v in base_config.items() if k != "APP_ENV"}
    result = check_drift(base_config, live)
    assert "APP_ENV" in result.removed


def test_ignore_keys_excluded_from_drift(base_config):
    live = dict(base_config)
    live["DB_HOST"] = "prod-db"
    result = check_drift(base_config, live, ignore_keys=["DB_HOST"])
    assert not result.has_drift
    assert "DB_HOST" not in result.drifted


def test_summary_no_drift(base_config):
    result = check_drift(base_config, dict(base_config))
    assert result.summary() == "No drift detected."


def test_summary_with_drift(base_config):
    live = dict(base_config)
    live["DB_HOST"] = "prod-db"
    live["EXTRA"] = "val"
    result = check_drift(base_config, live)
    s = result.summary()
    assert "Drift detected" in s
    assert "changed" in s
    assert "added" in s


def test_drift_count_combines_all(base_config):
    live = {"DB_HOST": "changed", "BRAND_NEW": "yes"}
    result = check_drift(base_config, live)
    assert result.drift_count == len(result.drifted) + len(result.added) + len(result.removed)
