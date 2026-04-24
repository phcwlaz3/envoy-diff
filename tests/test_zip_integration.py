"""Integration tests for the zipper feature end-to-end."""
import json
import pytest

from envoy_diff.loader import load_config
from envoy_diff.zipper import zip_configs


@pytest.fixture
def staging_env(tmp_path):
    p = tmp_path / "staging.env"
    p.write_text(
        "DB_HOST=staging-db\n"
        "DB_PORT=5432\n"
        "CACHE_URL=redis://staging:6379\n"
        "APP_ENV=staging\n"
        "DEBUG=true\n"
    )
    return str(p)


@pytest.fixture
def production_env(tmp_path):
    p = tmp_path / "production.env"
    p.write_text(
        "DB_HOST=prod-db\n"
        "DB_PORT=5432\n"
        "CACHE_URL=redis://prod:6379\n"
        "APP_ENV=production\n"
        "NEW_RELIC_KEY=abc123\n"
    )
    return str(p)


def test_integration_total_row_count(staging_env, production_env):
    left = load_config(staging_env)
    right = load_config(production_env)
    result = zip_configs(left, right)
    # 5 staging + 5 production - 4 shared = 6 unique keys
    assert len(result.rows) == 6


def test_integration_aligned_keys(staging_env, production_env):
    left = load_config(staging_env)
    right = load_config(production_env)
    result = zip_configs(left, right)
    assert result.aligned_count() == 4  # DB_HOST, DB_PORT, CACHE_URL, APP_ENV


def test_integration_equal_keys(staging_env, production_env):
    left = load_config(staging_env)
    right = load_config(production_env)
    result = zip_configs(left, right)
    assert result.equal_count() == 1  # only DB_PORT


def test_integration_diff_count(staging_env, production_env):
    left = load_config(staging_env)
    right = load_config(production_env)
    result = zip_configs(left, right)
    assert result.diff_count() == 3  # DB_HOST, CACHE_URL, APP_ENV


def test_integration_left_only(staging_env, production_env):
    left = load_config(staging_env)
    right = load_config(production_env)
    result = zip_configs(left, right)
    assert result.left_only == ["DEBUG"]


def test_integration_right_only(staging_env, production_env):
    left = load_config(staging_env)
    right = load_config(production_env)
    result = zip_configs(left, right)
    assert result.right_only == ["NEW_RELIC_KEY"]


def test_integration_summary_mentions_zipped(staging_env, production_env):
    left = load_config(staging_env)
    right = load_config(production_env)
    result = zip_configs(left, right)
    assert "zipped" in result.summary()
    assert "6" in result.summary()
