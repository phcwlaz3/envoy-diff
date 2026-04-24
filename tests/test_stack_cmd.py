import argparse
import json
import pytest
from unittest.mock import patch
from envoy_diff.commands.stack_cmd import run_stack_command


@pytest.fixture
def base_env(tmp_path):
    p = tmp_path / "base.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nLOG_LEVEL=info\n")
    return str(p)


@pytest.fixture
def prod_env(tmp_path):
    p = tmp_path / "prod.env"
    p.write_text("DB_HOST=prod.db.example.com\nCACHE_URL=redis://cache\n")
    return str(p)


def _make_args(files, strategy="last-wins", fmt="text", show_all=False):
    ns = argparse.Namespace(
        files=files,
        strategy=strategy,
        fmt=fmt,
        show_all=show_all,
    )
    return ns


def test_stack_cmd_text_output(base_env, prod_env, capsys):
    args = _make_args([base_env, prod_env])
    rc = run_stack_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "DB_HOST" in out
    assert "prod.db.example.com" in out


def test_stack_cmd_json_output(base_env, prod_env, capsys):
    args = _make_args([base_env, prod_env], fmt="json")
    rc = run_stack_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert data["layer_count"] == 2
    assert "DB_HOST" in data["entries"]


def test_stack_cmd_last_wins_default(base_env, prod_env, capsys):
    args = _make_args([base_env, prod_env], fmt="json")
    run_stack_command(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["entries"]["DB_HOST"]["effective_value"] == "prod.db.example.com"


def test_stack_cmd_first_wins(base_env, prod_env, capsys):
    args = _make_args([base_env, prod_env], strategy="first-wins", fmt="json")
    run_stack_command(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["entries"]["DB_HOST"]["effective_value"] == "localhost"


def test_stack_cmd_show_all_flag(base_env, prod_env, capsys):
    args = _make_args([base_env, prod_env], show_all=True)
    rc = run_stack_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    # Both values for DB_HOST should appear
    assert "localhost" in out
    assert "prod.db.example.com" in out


def test_stack_cmd_invalid_file_returns_error(base_env, capsys):
    args = _make_args([base_env, "/nonexistent/file.env"])
    rc = run_stack_command(args)
    assert rc == 1
    err = capsys.readouterr().err
    assert "error" in err.lower()


def test_stack_cmd_override_count_in_json(base_env, prod_env, capsys):
    args = _make_args([base_env, prod_env], fmt="json")
    run_stack_command(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["override_count"] == 1
