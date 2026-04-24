"""Tests for envoy_diff.zipper."""
import pytest
from envoy_diff.zipper import ZipRow, ZipResult, zip_configs


@pytest.fixture
def left_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_ENV": "staging",
    }


@pytest.fixture
def right_config():
    return {
        "DB_HOST": "prod-db",
        "DB_PORT": "5432",
        "LOG_LEVEL": "warn",
    }


def test_zip_returns_result(left_config, right_config):
    result = zip_configs(left_config, right_config)
    assert isinstance(result, ZipResult)


def test_zip_all_keys_present(left_config, right_config):
    result = zip_configs(left_config, right_config)
    keys = {r.key for r in result.rows}
    assert keys == {"DB_HOST", "DB_PORT", "APP_ENV", "LOG_LEVEL"}


def test_zip_aligned_count(left_config, right_config):
    result = zip_configs(left_config, right_config)
    # DB_HOST and DB_PORT appear in both
    assert result.aligned_count() == 2


def test_zip_equal_count(left_config, right_config):
    result = zip_configs(left_config, right_config)
    # Only DB_PORT has the same value
    assert result.equal_count() == 1


def test_zip_diff_count(left_config, right_config):
    result = zip_configs(left_config, right_config)
    # DB_HOST differs
    assert result.diff_count() == 1


def test_zip_left_only(left_config, right_config):
    result = zip_configs(left_config, right_config)
    assert "APP_ENV" in result.left_only
    assert len(result.left_only) == 1


def test_zip_right_only(left_config, right_config):
    result = zip_configs(left_config, right_config)
    assert "LOG_LEVEL" in result.right_only
    assert len(result.right_only) == 1


def test_zip_row_is_aligned_true(left_config, right_config):
    result = zip_configs(left_config, right_config)
    db_host_row = next(r for r in result.rows if r.key == "DB_HOST")
    assert db_host_row.is_aligned is True


def test_zip_row_is_aligned_false_for_left_only(left_config, right_config):
    result = zip_configs(left_config, right_config)
    app_env_row = next(r for r in result.rows if r.key == "APP_ENV")
    assert app_env_row.is_aligned is False
    assert app_env_row.right is None


def test_zip_sorted_keys(left_config, right_config):
    result = zip_configs(left_config, right_config, sort=True)
    keys = [r.key for r in result.rows]
    assert keys == sorted(keys)


def test_zip_empty_configs():
    result = zip_configs({}, {})
    assert result.rows == []
    assert result.aligned_count() == 0


def test_zip_summary_string(left_config, right_config):
    result = zip_configs(left_config, right_config)
    s = result.summary()
    assert "zipped" in s
    assert "aligned" in s
