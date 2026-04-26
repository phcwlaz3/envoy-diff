from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envoy_diff.commands.prefix_cmd import run_prefix_command


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "CACHE_URL=redis://localhost\n"
        "APP_DEBUG=true\n"
    )
    return p


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "action": "add",
        "prefix": "PROD_",
        "skip_prefixed": False,
        "format": "text",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_prefix_cmd_text_output(env_file: Path, capsys):
    args = _make_args(file=str(env_file))
    rc = run_prefix_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "PROD_" in out


def test_prefix_cmd_json_output(env_file: Path, capsys):
    args = _make_args(file=str(env_file), format="json")
    rc = run_prefix_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "config" in data
    assert "change_count" in data
    assert data["change_count"] == 4


def test_prefix_cmd_add_renames_all_keys(env_file: Path, capsys):
    args = _make_args(file=str(env_file), prefix="PROD_", format="json")
    run_prefix_command(args)
    data = json.loads(capsys.readouterr().out)
    for key in data["config"]:
        assert key.startswith("PROD_")


def test_prefix_cmd_remove_strips_prefix(env_file: Path, tmp_path: Path, capsys):
    prefixed = tmp_path / "prefixed.env"
    prefixed.write_text(
        "PROD_DB_HOST=localhost\n"
        "PROD_DB_PORT=5432\n"
        "OTHER_KEY=value\n"
    )
    args = _make_args(file=str(prefixed), action="remove", prefix="PROD_", format="json")
    rc = run_prefix_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "DB_HOST" in data["config"]
    assert "DB_PORT" in data["config"]
    # Key without prefix is unchanged
    assert "OTHER_KEY" in data["config"]


def test_prefix_cmd_skip_already_prefixed(env_file: Path, tmp_path: Path, capsys):
    already = tmp_path / "already.env"
    already.write_text("PROD_DB_HOST=localhost\nDB_PORT=5432\n")
    args = _make_args(
        file=str(already),
        prefix="PROD_",
        skip_prefixed=True,
        format="json",
    )
    rc = run_prefix_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    # Only DB_PORT should have been renamed; PROD_DB_HOST was skipped
    assert data["change_count"] == 1


def test_prefix_cmd_invalid_file_returns_error(capsys):
    args = _make_args(file="/nonexistent/path/.env")
    rc = run_prefix_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err
