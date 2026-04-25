"""Tests for envoy_diff.prefixer."""
import pytest
from envoy_diff.prefixer import add_prefix, strip_prefix, PrefixResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "CACHE_URL": "redis://localhost",
        "APP_ENV": "production",
    }


# --- add_prefix ---

def test_add_prefix_all_keys_changed(sample_config):
    result = add_prefix(sample_config, "MYAPP_", skip_already_prefixed=False)
    assert all(k.startswith("MYAPP_") for k in result.result)


def test_add_prefix_change_count(sample_config):
    result = add_prefix(sample_config, "MYAPP_", skip_already_prefixed=False)
    assert result.change_count() == len(sample_config)


def test_add_prefix_values_preserved(sample_config):
    result = add_prefix(sample_config, "X_")
    for original_key, value in sample_config.items():
        new_key = f"X_{original_key}"
        assert result.result[new_key] == value


def test_add_prefix_skip_already_prefixed():
    config = {"PRE_FOO": "1", "BAR": "2"}
    result = add_prefix(config, "PRE_", skip_already_prefixed=True)
    assert "PRE_FOO" in result.result
    assert "PRE_PRE_FOO" not in result.result
    assert result.change_count() == 1


def test_add_prefix_no_skip_doubles_prefix():
    config = {"PRE_FOO": "1"}
    result = add_prefix(config, "PRE_", skip_already_prefixed=False)
    assert "PRE_PRE_FOO" in result.result
    assert result.change_count() == 1


def test_add_prefix_empty_config():
    result = add_prefix({}, "ENV_")
    assert result.result == {}
    assert result.has_changes() is False


def test_add_prefix_has_changes_true(sample_config):
    result = add_prefix(sample_config, "Z_")
    assert result.has_changes() is True


def test_add_prefix_summary_contains_count(sample_config):
    result = add_prefix(sample_config, "Z_")
    assert str(result.change_count()) in result.summary()
    assert "Z_" in result.summary()


# --- strip_prefix ---

def test_strip_prefix_removes_prefix(sample_config):
    result = strip_prefix(sample_config, "DB_")
    assert "HOST" in result.result
    assert "PORT" in result.result


def test_strip_prefix_change_count(sample_config):
    result = strip_prefix(sample_config, "DB_")
    assert result.change_count() == 2


def test_strip_prefix_keeps_unmatched_by_default(sample_config):
    result = strip_prefix(sample_config, "DB_")
    assert "CACHE_URL" in result.result
    assert "APP_ENV" in result.result


def test_strip_prefix_drops_unmatched_when_flag_false(sample_config):
    result = strip_prefix(sample_config, "DB_", keep_unmatched=False)
    assert "CACHE_URL" not in result.result
    assert "APP_ENV" not in result.result


def test_strip_prefix_no_match_returns_original_unchanged():
    config = {"FOO": "bar"}
    result = strip_prefix(config, "NOPE_")
    assert result.result == config
    assert result.has_changes() is False


def test_strip_prefix_summary_no_changes():
    config = {"FOO": "bar"}
    result = strip_prefix(config, "NOPE_")
    assert "No keys" in result.summary()


def test_strip_prefix_original_not_mutated(sample_config):
    original_copy = dict(sample_config)
    strip_prefix(sample_config, "DB_")
    assert sample_config == original_copy
