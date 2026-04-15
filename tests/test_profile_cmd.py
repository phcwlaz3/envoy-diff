"""Tests for envoy_diff.commands.profile_cmd."""

import json
import pytest
from unittest.mock import patch
from argparse import Namespace

from envoy_diff.commands.profile_cmd import run_profile_command


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / "config.env"
    p.write_text("HOST=localhost\nPORT=8080\nDEBUG=false\n")
    return str(p)


@pytest.fixture()
def dirty_env_file(tmp_path):
    p = tmp_path / "dirty.env"
    p.write_text("HOST=localhost\nAPI_KEY=abc123\nPORT=\n")
    return str(p)


def test_profile_text_output(env_file, capsys):
    args = Namespace(file=env_file, format="text")
    rc = run_profile_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "Score" in out
    assert "Grade" in out


def test_profile_json_output(env_file, capsys):
    args = Namespace(file=env_file, format="json")
    rc = run_profile_command(args)
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["score"] == 100
    assert payload["grade"] == "A"
    assert payload["empty_count"] == 0


def test_profile_dirty_file_shows_warnings(dirty_env_file, capsys):
    args = Namespace(file=dirty_env_file, format="text")
    rc = run_profile_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "⚠" in out


def test_profile_missing_file_returns_error(tmp_path, capsys):
    args = Namespace(file=str(tmp_path / "nope.env"), format="text")
    rc = run_profile_command(args)
    assert rc == 1
    err = capsys.readouterr().err
    assert "Error" in err


def test_profile_json_suspicious_key(dirty_env_file, capsys):
    args = Namespace(file=dirty_env_file, format="json")
    run_profile_command(args)
    payload = json.loads(capsys.readouterr().out)
    assert "API_KEY" in payload["suspicious_keys"]
    assert payload["score"] < 100
