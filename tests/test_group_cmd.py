"""Tests for envoy_diff.commands.group_cmd."""
import argparse
import json
import pytest
from unittest.mock import patch
from envoy_diff.commands.group_cmd import run_group_command


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "test.env"
    f.write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=AKID\nAWS_SECRET=s3cr3t\nSTANDALONE=yes\n"
    )
    return str(f)


def _make_args(file, prefixes=None, auto_detect=True, fmt="text"):
    ns = argparse.Namespace(
        file=file,
        prefixes=prefixes or [],
        auto_detect=auto_detect,
        format=fmt,
    )
    return ns


def test_group_cmd_text_output(env_file, capsys):
    args = _make_args(env_file)
    rc = run_group_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB" in out
    assert "AWS" in out


def test_group_cmd_json_output(env_file, capsys):
    args = _make_args(env_file, fmt="json")
    rc = run_group_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "groups" in data
    assert "ungrouped" in data
    assert "summary" in data


def test_group_cmd_explicit_prefix(env_file, capsys):
    args = _make_args(env_file, prefixes=["DB"], auto_detect=False)
    rc = run_group_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "[DB]" in out


def test_group_cmd_no_auto_no_prefix(env_file, capsys):
    args = _make_args(env_file, auto_detect=False)
    rc = run_group_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "ungrouped" in out


def test_group_cmd_missing_file_returns_error(capsys):
    args = _make_args("/nonexistent/file.env")
    rc = run_group_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err
