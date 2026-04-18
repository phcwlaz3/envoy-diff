"""Tests for the diff command."""
import json
import pytest
from argparse import Namespace
from pathlib import Path

from envoy_diff.commands.diff_cmd import run_diff_command


@pytest.fixture
def base_env(tmp_path):
    f = tmp_path / "base.env"
    f.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=staging\n")
    return str(f)


@pytest.fixture
def head_env(tmp_path):
    f = tmp_path / "head.env"
    f.write_text("DB_HOST=prod.db\nDB_PORT=5432\nNEW_KEY=hello\n")
    return str(f)


def _make_args(**kwargs):
    defaults = {"format": "text", "score": False}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_diff_text_output(base_env, head_env, capsys):
    args = _make_args(base=base_env, head=head_env)
    rc = run_diff_command(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert rc == 1


def test_diff_json_output(base_env, head_env, capsys):
    args = _make_args(base=base_env, head=head_env, format="json")
    rc = run_diff_command(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "added" in data
    assert "removed" in data
    assert data["has_diff"] is True


def test_diff_no_differences_returns_zero(base_env, capsys):
    args = _make_args(base=base_env, head=base_env)
    rc = run_diff_command(args)
    assert rc == 0


def test_diff_with_score(base_env, head_env, capsys):
    args = _make_args(base=base_env, head=head_env, score=True)
    run_diff_command(args)
    out = capsys.readouterr().out
    assert "Risk score" in out


def test_diff_invalid_file_returns_error(tmp_path, capsys):
    args = _make_args(base="missing.env", head="also_missing.env")
    rc = run_diff_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err


def test_diff_json_includes_score(base_env, head_env, capsys):
    args = _make_args(base=base_env, head=head_env, format="json", score=True)
    run_diff_command(args)
    data = json.loads(capsys.readouterr().out)
    assert "score" in data
    assert "risk" in data
