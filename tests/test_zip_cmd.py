"""Tests for envoy_diff.commands.zip_cmd."""
import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from envoy_diff.commands.zip_cmd import run_zip_command


@pytest.fixture
def left_env(tmp_path):
    p = tmp_path / "left.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=staging\n")
    return str(p)


@pytest.fixture
def right_env(tmp_path):
    p = tmp_path / "right.env"
    p.write_text("DB_HOST=prod-db\nDB_PORT=5432\nLOG_LEVEL=warn\n")
    return str(p)


def _make_args(left, right, fmt="text", no_sort=False, diff_only=False):
    ns = argparse.Namespace(
        left=left,
        right=right,
        fmt=fmt,
        no_sort=no_sort,
        diff_only=diff_only,
    )
    return ns


def test_zip_cmd_text_output(left_env, right_env, capsys):
    args = _make_args(left_env, right_env)
    rc = run_zip_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "zipped" in out


def test_zip_cmd_json_output(left_env, right_env, capsys):
    args = _make_args(left_env, right_env, fmt="json")
    rc = run_zip_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "rows" in data
    assert "summary" in data


def test_zip_cmd_diff_only_excludes_equal(left_env, right_env, capsys):
    args = _make_args(left_env, right_env, diff_only=True)
    rc = run_zip_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    # DB_PORT is equal in both — should not appear in diff-only output
    assert "DB_PORT" not in out


def test_zip_cmd_json_diff_only(left_env, right_env, capsys):
    args = _make_args(left_env, right_env, fmt="json", diff_only=True)
    rc = run_zip_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    equal_rows = [r for r in data["rows"] if r["equal"]]
    assert equal_rows == []


def test_zip_cmd_missing_file_returns_error(right_env, capsys):
    args = _make_args("/nonexistent/left.env", right_env)
    rc = run_zip_command(args)
    assert rc == 1


def test_zip_cmd_left_only_in_json(left_env, right_env, capsys):
    args = _make_args(left_env, right_env, fmt="json")
    run_zip_command(args)
    data = json.loads(capsys.readouterr().out)
    assert "APP_ENV" in data["left_only"]


def test_zip_cmd_right_only_in_json(left_env, right_env, capsys):
    args = _make_args(left_env, right_env, fmt="json")
    run_zip_command(args)
    data = json.loads(capsys.readouterr().out)
    assert "LOG_LEVEL" in data["right_only"]
