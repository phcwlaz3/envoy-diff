import pytest
from envoy_diff.aliaser import alias_config, AliasResult


@pytest.fixture
def sample_config():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "DB_HOST": "localhost",
        "APP_PORT": "8080",
    }


def test_alias_adds_new_key(sample_config):
    result = alias_config(sample_config, {"DB_URL": "DATABASE_URL"})
    assert result.config["DB_URL"] == "postgres://localhost/db"


def test_alias_preserves_original_key(sample_config):
    result = alias_config(sample_config, {"DB_URL": "DATABASE_URL"})
    assert "DATABASE_URL" in result.config


def test_alias_missing_source_key_skipped(sample_config):
    result = alias_config(sample_config, {"REDIS_ALIAS": "REDIS_URL"})
    assert "REDIS_ALIAS" not in result.config
    assert "REDIS_ALIAS" in result.skipped


def test_alias_existing_key_not_overwritten_by_default(sample_config):
    config = {**sample_config, "DB_URL": "original"}
    result = alias_config(config, {"DB_URL": "DATABASE_URL"})
    assert result.config["DB_URL"] == "original"
    assert "DB_URL" in result.skipped


def test_alias_existing_key_overwritten_when_flag_set(sample_config):
    config = {**sample_config, "DB_URL": "original"}
    result = alias_config(config, {"DB_URL": "DATABASE_URL"}, overwrite=True)
    assert result.config["DB_URL"] == "postgres://localhost/db"
    assert "DB_URL" in result.aliases_added


def test_alias_count(sample_config):
    result = alias_config(sample_config, {"DB_URL": "DATABASE_URL", "PORT": "APP_PORT"})
    assert result.alias_count() == 2


def test_has_aliases_true(sample_config):
    result = alias_config(sample_config, {"DB_URL": "DATABASE_URL"})
    assert result.has_aliases() is True


def test_has_aliases_false_when_all_skipped(sample_config):
    result = alias_config(sample_config, {"MISSING_ALIAS": "NO_SUCH_KEY"})
    assert result.has_aliases() is False


def test_summary_no_aliases(sample_config):
    result = alias_config(sample_config, {})
    assert result.summary() == "No aliases applied."


def test_summary_with_aliases_and_skipped(sample_config):
    result = alias_config(sample_config, {"DB_URL": "DATABASE_URL", "X": "MISSING"})
    summary = result.summary()
    assert "1 alias" in summary
    assert "1 skipped" in summary


def test_empty_config_returns_empty():
    result = alias_config({}, {"DB_URL": "DATABASE_URL"})
    assert result.config == {}
    assert result.alias_count() == 0
