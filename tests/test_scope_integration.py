"""Integration tests: load a real file then scope it."""
import pytest
from envoy_diff.loader import load_config
from envoy_diff.scoper import scope_config


@pytest.fixture
def mixed_env(tmp_path):
    f = tmp_path / "mixed.env"
    f.write_text(
        "DB_HOST=pg.local\n"
        "DB_PORT=5432\n"
        "REDIS_URL=redis://localhost\n"
        "AUTH_TOKEN=tok\n"
        "JWT_SECRET=jwtsecret\n"
        "LOG_LEVEL=DEBUG\n"
        "FEATURE_BETA=true\n"
        "APP_ENV=production\n"
    )
    return str(f)


def test_integration_database_scope(mixed_env):
    config = load_config(mixed_env)
    result = scope_config(config, "database")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT"}


def test_integration_cache_scope(mixed_env):
    config = load_config(mixed_env)
    result = scope_config(config, "cache")
    assert "REDIS_URL" in result.matched


def test_integration_auth_scope(mixed_env):
    config = load_config(mixed_env)
    result = scope_config(config, "auth")
    assert "AUTH_TOKEN" in result.matched
    assert "JWT_SECRET" in result.matched


def test_integration_excluded_count_correct(mixed_env):
    config = load_config(mixed_env)
    result = scope_config(config, "database")
    assert result.excluded_count() == len(config) - result.matched_count()


def test_integration_summary_contains_scope_name(mixed_env):
    config = load_config(mixed_env)
    result = scope_config(config, "feature")
    assert "feature" in result.summary()
    assert "FEATURE_BETA" in result.matched
