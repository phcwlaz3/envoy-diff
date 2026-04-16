"""Integration tests for grouper with real config loading."""
import pytest
from envoy_diff.loader import load_config
from envoy_diff.grouper import group_config


@pytest.fixture
def mixed_env(tmp_path):
    f = tmp_path / "mixed.env"
    f.write_text(
        "DB_HOST=db.internal\n"
        "DB_PORT=5432\n"
        "DB_USER=admin\n"
        "REDIS_HOST=redis.internal\n"
        "REDIS_PORT=6379\n"
        "APP_ENV=production\n"
        "APP_DEBUG=false\n"
        "SENTRY_DSN=https://sentry.io/x\n"
    )
    return str(f)


def test_integration_auto_groups_three_prefixes(mixed_env):
    config = load_config(mixed_env)
    result = group_config(config)
    assert "DB" in result.groups
    assert "REDIS" in result.groups
    assert "APP" in result.groups


def test_integration_single_key_ungrouped(mixed_env):
    config = load_config(mixed_env)
    result = group_config(config)
    assert "SENTRY_DSN" in result.ungrouped


def test_integration_explicit_prefix_captures_sentry(mixed_env):
    config = load_config(mixed_env)
    result = group_config(config, prefixes=["SENTRY"], auto_detect=False)
    assert "SENTRY" in result.groups
    assert "SENTRY_DSN" in result.groups["SENTRY"]


def test_integration_summary_reflects_groups(mixed_env):
    config = load_config(mixed_env)
    result = group_config(config)
    s = result.summary()
    assert "DB" in s
    assert "REDIS" in s
    assert "APP" in s
