import argparse
import pytest
from unittest.mock import patch
from envoy_diff.commands.extract_cmd import run_extract_command


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "app.env"
    p.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nREDIS_URL=redis://localhost\nAPP_NAME=envoy\n"
    )
    return str(p)


def _make_args(**kwargs):
    defaults = {
        "file": "",
        "keys": None,
        "pattern": None,
        "prefix": None,
        "fmt": "text",
        "show_skipped": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_extract_cmd_text_output(env_file, capsys):
    args = _make_args(file=env_file, prefix="DB_")
    rc = run_extract_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "DB_HOST" in out
    assert "DB_PORT" in out


def test_extract_cmd_json_output(env_file, capsys):
    import json
    args = _make_args(file=env_file, prefix="DB_", fmt="json")
    rc = run_extract_command(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert rc == 0
    assert "DB_HOST" in data["extracted"]
    assert data["extract_count"] == 2


def test_extract_cmd_pattern(env_file, capsys):
    args = _make_args(file=env_file, pattern=r"^REDIS")
    rc = run_extract_command(args)
    out = capsys.readouterr().out
    assert rc == 0
    assert "REDIS_URL" in out
    assert "DB_HOST" not in out


def test_extract_cmd_show_skipped(env_file, capsys):
    args = _make_args(file=env_file, prefix="DB_", show_skipped=True)
    rc = run_extract_command(args)
    out = capsys.readouterr().out
    assert "REDIS_URL" in out
    assert "APP_NAME" in out


def test_extract_cmd_invalid_file(capsys):
    args = _make_args(file="/nonexistent/path.env")
    rc = run_extract_command(args)
    assert rc == 1
    err = capsys.readouterr().err
    assert "error" in err
