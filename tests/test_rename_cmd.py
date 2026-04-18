import argparse
import pytest
from unittest.mock import patch
from envoy_diff.commands.rename_cmd import run_rename_command


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "config.env"
    f.write_text("OLD_HOST=localhost\nDB_PORT=5432\nAPP_KEY=secret\n")
    return str(f)


def _make_args(file, mappings=None, pattern=None, replacement="", fmt="text"):
    return argparse.Namespace(
        file=file,
        mappings=mappings or [],
        pattern=pattern,
        replacement=replacement,
        fmt=fmt,
    )


def test_rename_cmd_text_output(env_file, capsys):
    args = _make_args(env_file, mappings=[["OLD_HOST", "NEW_HOST"]])
    rc = run_rename_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "OLD_HOST -> NEW_HOST" in out
    assert "NEW_HOST=localhost" in out


def test_rename_cmd_json_output(env_file, capsys):
    import json
    args = _make_args(env_file, mappings=[["DB_PORT", "DATABASE_PORT"]], fmt="json")
    rc = run_rename_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["rename_count"] == 1
    assert "DATABASE_PORT" in data["config"]


def test_rename_cmd_pattern(env_file, capsys):
    args = _make_args(env_file, pattern="^OLD_", replacement="NEW_")
    rc = run_rename_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "NEW_HOST=localhost" in out


def test_rename_cmd_no_renames(env_file, capsys):
    args = _make_args(env_file)
    rc = run_rename_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No keys renamed" in out


def test_rename_cmd_invalid_file(capsys):
    args = _make_args("/nonexistent/path.env")
    rc = run_rename_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err
