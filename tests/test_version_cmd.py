"""Tests for envoy_diff.commands.version_cmd."""
import argparse
import json
import pytest
from unittest.mock import patch

from envoy_diff.commands.version_cmd import run_version_command


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "app.env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP_ENV=staging\n")
    return str(p)


def _make_args(file, version, **kwargs):
    defaults = {
        "label": None,
        "prefix": "ENVOY_",
        "no_inject": False,
        "format": "text",
    }
    defaults.update(kwargs)
    ns = argparse.Namespace(file=file, version=version, **defaults)
    return ns


def test_version_cmd_text_output(env_file, capsys):
    args = _make_args(env_file, "1.0.0")
    rc = run_version_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "1.0.0" in out
    assert "ENVOY_VERSION" in out


def test_version_cmd_json_output(env_file, capsys):
    args = _make_args(env_file, "2.1.0", format="json")
    rc = run_version_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["version"] == "2.1.0"
    assert "ENVOY_VERSION" in data["config"]
    assert "ENVOY_STAMPED_AT" in data["config"]


def test_version_cmd_with_label(env_file, capsys):
    args = _make_args(env_file, "3.0.0", label="release-99", format="json")
    rc = run_version_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["label"] == "release-99"
    assert data["config"]["ENVOY_LABEL"] == "release-99"


def test_version_cmd_no_inject(env_file, capsys):
    args = _make_args(env_file, "1.0.0", no_inject=True, format="json")
    rc = run_version_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["stamp_count"] == 0
    assert "ENVOY_VERSION" not in data["config"]


def test_version_cmd_custom_prefix(env_file, capsys):
    args = _make_args(env_file, "5.0.0", prefix="META_", format="json")
    rc = run_version_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "META_VERSION" in data["config"]
    assert "ENVOY_VERSION" not in data["config"]


def test_version_cmd_invalid_file_returns_error(tmp_path, capsys):
    args = _make_args(str(tmp_path / "missing.env"), "1.0.0")
    rc = run_version_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err
