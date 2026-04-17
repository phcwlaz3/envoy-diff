import pytest
from envoy_diff.scoper import scope_config, BUILTIN_SCOPES


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AUTH_SECRET": "abc123",
        "JWT_EXPIRY": "3600",
        "LOG_LEVEL": "INFO",
        "FEATURE_DARK_MODE": "true",
        "APP_NAME": "myapp",
        "PORT": "8080",
    }


def test_scope_database_keys(sample_config):
    result = scope_config(sample_config, "database")
    assert "DB_HOST" in result.matched
    assert "DB_PORT" in result.matched
    assert "APP_NAME" not in result.matched


def test_scope_auth_keys(sample_config):
    result = scope_config(sample_config, "auth")
    assert "AUTH_SECRET" in result.matched
    assert "JWT_EXPIRY" in result.matched
    assert "DB_HOST" not in result.matched


def test_scope_excluded_contains_rest(sample_config):
    result = scope_config(sample_config, "database")
    assert "APP_NAME" in result.excluded
    assert "PORT" in result.excluded
    assert "DB_HOST" not in result.excluded


def test_scope_unknown_scope_matches_nothing(sample_config):
    result = scope_config(sample_config, "nonexistent")
    assert result.matched == {}
    assert len(result.excluded) == len(sample_config)


def test_scope_extra_prefixes_extend_match(sample_config):
    result = scope_config(sample_config, "database", extra_prefixes=["APP_"])
    assert "APP_NAME" in result.matched
    assert "DB_HOST" in result.matched


def test_scope_matched_count(sample_config):
    result = scope_config(sample_config, "logging")
    assert result.matched_count() == 1
    assert result.matched["LOG_LEVEL"] == "INFO"


def test_scope_summary_string(sample_config):
    result = scope_config(sample_config, "database")
    s = result.summary()
    assert "database" in s
    assert "matched" in s
    assert "excluded" in s


def test_scope_case_insensitive_key_match(sample_config):
    config = {"db_host": "localhost", "APP_NAME": "x"}
    result = scope_config(config, "database")
    assert "db_host" in result.matched


def test_scope_unknown_with_extra_prefixes():
    config = {"CUSTOM_KEY": "val", "OTHER": "x"}
    result = scope_config(config, "custom", extra_prefixes=["CUSTOM_"])
    assert "CUSTOM_KEY" in result.matched
    assert "OTHER" in result.excluded


def test_builtin_scopes_keys_exist():
    for scope in ["database", "auth", "logging", "feature", "cache"]:
        assert scope in BUILTIN_SCOPES
