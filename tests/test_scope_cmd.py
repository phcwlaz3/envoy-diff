import argparse
import json
import pytest
from unittest.mock import patch
from envoy_diff.commands.scope_cmd import run_scope_command


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "app.env"
    f.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nAUTH_SECRET=s3cr3t\nAPP_NAME=myapp\n"
    )
    return str(f)


def _make_args(**kwargs):
    defaults = {
        "format": "text",
        "extra_prefixes": None,
        "show_excluded": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_scope_cmd_text_output(env_file, capsys):
    args = _make_args(file=env_file, scope="database")
    rc = run_scope_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "DB_HOST" in out
    assert "DB_PORT" in out
    assert "AUTH_SECRET" not in out


def test_scope_cmd_json_output(env_file, capsys):
    args = _make_args(file=env_file, scope="database", format="json")
    rc = run_scope_command(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert rc == 0
    assert data["scope"] == "database"
    assert "DB_HOST" in data["matched"]
    assert data["matched_count"] == 2


def test_scope_cmd_show_excluded(env_file, capsys):
    args = _make_args(file=env_file, scope="database", show_excluded=True)
    rc = run_scope_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "Excluded keys" in out
    assert "APP_NAME" in out


def test_scope_cmd_unknown_scope_no_match(env_file, capsys):
    args = _make_args(file=env_file, scope="unknown_xyz")
    rc = run_scope_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "no keys matched" in out


def test_scope_cmd_extra_prefix(env_file, capsys):
    args = _make_args(file=env_file, scope="database", extra_prefixes=["APP_"])
    rc = run_scope_command(args)
    out = capsys.readouterr().out
    assert "APP_NAME" in out


def test_scope_cmd_invalid_file_returns_error(tmp_path, capsys):
    args = _make_args(file=str(tmp_path / "missing.env"), scope="database")
    rc = run_scope_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err
