"""Integration tests for the compose feature."""
from pathlib import Path

import pytest

from envoy_diff.composer import compose_configs
from envoy_diff.loader import load_config


@pytest.fixture
def defaults_env(tmp_path: Path) -> Path:
    p = tmp_path / "defaults.env"
    p.write_text(
        "LOG_LEVEL=info\nDB_PORT=5432\nAPP_TIMEOUT=30\nFEATURE_X=false\n"
    )
    return p


@pytest.fixture
def staging_env(tmp_path: Path) -> Path:
    p = tmp_path / "staging.env"
    p.write_text("DB_HOST=staging-db\nDB_PORT=5433\nAPP_ENV=staging\n")
    return p


@pytest.fixture
def production_env(tmp_path: Path) -> Path:
    p = tmp_path / "production.env"
    p.write_text("DB_HOST=prod-db\nAPP_ENV=production\nFEATURE_X=true\n")
    return p


def test_integration_three_layer_compose(defaults_env, staging_env, production_env):
    fragments = {
        "defaults": load_config(str(defaults_env)),
        "staging": load_config(str(staging_env)),
        "production": load_config(str(production_env)),
    }
    result = compose_configs(
        fragments,
        order=["defaults", "staging", "production"],
    )
    assert result.fragment_count == 3
    # production wins over staging and defaults
    assert result.config["DB_HOST"] == "prod-db"
    assert result.config["APP_ENV"] == "production"
    assert result.config["FEATURE_X"] == "true"
    # defaults value not overridden
    assert result.config["LOG_LEVEL"] == "info"


def test_integration_conflict_list_accurate(defaults_env, staging_env, production_env):
    fragments = {
        "defaults": load_config(str(defaults_env)),
        "staging": load_config(str(staging_env)),
        "production": load_config(str(production_env)),
    }
    result = compose_configs(
        fragments,
        order=["defaults", "staging", "production"],
    )
    # DB_PORT overridden by staging; APP_ENV, FEATURE_X overridden by production
    assert "DB_PORT" in result.conflicts
    assert "APP_ENV" in result.conflicts
    assert "FEATURE_X" in result.conflicts


def test_integration_total_key_count(defaults_env, staging_env, production_env):
    fragments = {
        "defaults": load_config(str(defaults_env)),
        "staging": load_config(str(staging_env)),
        "production": load_config(str(production_env)),
    }
    result = compose_configs(fragments, order=["defaults", "staging", "production"])
    # unique keys: LOG_LEVEL, DB_PORT, APP_TIMEOUT, FEATURE_X, DB_HOST, APP_ENV = 6
    assert len(result.config) == 6


def test_integration_first_wins_preserves_defaults(defaults_env, staging_env):
    fragments = {
        "defaults": load_config(str(defaults_env)),
        "staging": load_config(str(staging_env)),
    }
    result = compose_configs(
        fragments,
        order=["defaults", "staging"],
        on_conflict="first_wins",
    )
    assert result.config["DB_PORT"] == "5432"
