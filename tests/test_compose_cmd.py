"""Tests for the compose CLI sub-command."""
import json
from argparse import Namespace
from pathlib import Path

import pytest

from envoy_diff.commands.compose_cmd import run_compose_command


@pytest.fixture
def base_env(tmp_path: Path) -> Path:
    p = tmp_path / "base.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=development\n")
    return p


@pytest.fixture
def override_env(tmp_path: Path) -> Path:
    p = tmp_path / "override.env"
    p.write_text("DB_HOST=prod-db\nCACHE_URL=redis://cache:6379\n")
    return p


def _make_args(files, order=None, on_conflict="last_wins", fmt="text"):
    return Namespace(
        files=files,
        order=order,
        on_conflict=on_conflict,
        format=fmt,
    )


def test_compose_cmd_text_output(base_env, override_env, capsys):
    args = _make_args([f"base={base_env}", f"override={override_env}"])
    rc = run_compose_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST=prod-db" in out
    assert "CACHE_URL=redis://cache:6379" in out


def test_compose_cmd_json_output(base_env, override_env, capsys):
    args = _make_args([f"base={base_env}", f"override={override_env}"], fmt="json")
    rc = run_compose_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "config" in data
    assert data["config"]["DB_HOST"] == "prod-db"
    assert "fragments_used" in data


def test_compose_cmd_first_wins(base_env, override_env, capsys):
    args = _make_args(
        [f"base={base_env}", f"override={override_env}"],
        on_conflict="first_wins",
    )
    rc = run_compose_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST=localhost" in out


def test_compose_cmd_missing_file_returns_error(tmp_path, capsys):
    args = _make_args([str(tmp_path / "missing.env")])
    rc = run_compose_command(args)
    assert rc == 1
    assert "error" in capsys.readouterr().err


def test_compose_cmd_conflict_shown_in_text(base_env, override_env, capsys):
    args = _make_args([f"base={base_env}", f"override={override_env}"])
    run_compose_command(args)
    out = capsys.readouterr().out
    assert "conflict" in out.lower()


def test_compose_cmd_json_summary_present(base_env, override_env, capsys):
    args = _make_args([f"base={base_env}", f"override={override_env}"], fmt="json")
    run_compose_command(args)
    data = json.loads(capsys.readouterr().out)
    assert "summary" in data
    assert "fragment" in data["summary"]
