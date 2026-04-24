"""Integration tests: load real temp files through the full stack pipeline."""
import json
import argparse
import pytest
from envoy_diff.commands.stack_cmd import run_stack_command


@pytest.fixture
def defaults_env(tmp_path):
    p = tmp_path / "defaults.env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "REDIS_URL=redis://localhost:6379\n"
        "LOG_LEVEL=debug\n"
        "FEATURE_NEW_UI=false\n"
    )
    return str(p)


@pytest.fixture
def staging_env(tmp_path):
    p = tmp_path / "staging.env"
    p.write_text(
        "DB_HOST=staging.db.internal\n"
        "LOG_LEVEL=info\n"
        "SENTRY_DSN=https://sentry.io/staging\n"
    )
    return str(p)


@pytest.fixture
def production_env(tmp_path):
    p = tmp_path / "production.env"
    p.write_text(
        "DB_HOST=prod.db.internal\n"
        "LOG_LEVEL=warning\n"
        "SENTRY_DSN=https://sentry.io/prod\n"
        "FEATURE_NEW_UI=true\n"
    )
    return str(p)


def _args(files, strategy="last-wins", fmt="json"):
    return argparse.Namespace(files=files, strategy=strategy, fmt=fmt, show_all=False)


def test_integration_three_layer_key_count(defaults_env, staging_env, production_env, capsys):
    run_stack_command(_args([defaults_env, staging_env, production_env]))
    data = json.loads(capsys.readouterr().out)
    # Keys: DB_HOST, DB_PORT, REDIS_URL, LOG_LEVEL, FEATURE_NEW_UI, SENTRY_DSN
    assert len(data["entries"]) == 6


def test_integration_effective_value_is_production(defaults_env, staging_env, production_env, capsys):
    run_stack_command(_args([defaults_env, staging_env, production_env]))
    data = json.loads(capsys.readouterr().out)
    assert data["entries"]["DB_HOST"]["effective_value"] == "prod.db.internal"
    assert data["entries"]["LOG_LEVEL"]["effective_value"] == "warning"


def test_integration_first_wins_keeps_defaults(defaults_env, staging_env, production_env, capsys):
    run_stack_command(_args([defaults_env, staging_env, production_env], strategy="first-wins"))
    data = json.loads(capsys.readouterr().out)
    assert data["entries"]["DB_HOST"]["effective_value"] == "localhost"
    assert data["entries"]["LOG_LEVEL"]["effective_value"] == "debug"


def test_integration_override_count_correct(defaults_env, staging_env, production_env, capsys):
    run_stack_command(_args([defaults_env, staging_env, production_env]))
    data = json.loads(capsys.readouterr().out)
    # DB_HOST, LOG_LEVEL, SENTRY_DSN, FEATURE_NEW_UI all vary
    assert data["override_count"] >= 3


def test_integration_key_only_in_defaults_preserved(defaults_env, staging_env, production_env, capsys):
    run_stack_command(_args([defaults_env, staging_env, production_env]))
    data = json.loads(capsys.readouterr().out)
    assert "REDIS_URL" in data["entries"]
    assert data["entries"]["REDIS_URL"]["effective_value"] == "redis://localhost:6379"
