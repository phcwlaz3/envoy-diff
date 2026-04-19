from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import pytest

from envoy_diff.commands.summarize_cmd import run_summarize_command


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / "config.env"
    p.write_text(
        textwrap.dedent("""\
        DB_HOST=localhost
        DB_PORT=5432
        API_KEY=secret
        CACHE_URL=
        BACKUP_HOST=localhost
        """)
    )
    return p


def _make_args(file: str, fmt: str = "text") -> argparse.Namespace:
    return argparse.Namespace(file=file, fmt=fmt, func=run_summarize_command)


def test_summarize_cmd_text_output(env_file: Path, capsys):
    rc = run_summarize_command(_make_args(str(env_file)))
    assert rc == 0
    out = capsys.readouterr().out
    assert "Total keys" in out
    assert "5" in out


def test_summarize_cmd_json_output(env_file: Path, capsys):
    rc = run_summarize_command(_make_args(str(env_file), fmt="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total_keys"] == 5
    assert "unique_values" in data
    assert "empty_count" in data
    assert "duplicate_group_count" in data


def test_summarize_cmd_detects_empty_value(env_file: Path, capsys):
    rc = run_summarize_command(_make_args(str(env_file), fmt="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["empty_count"] == 1


def test_summarize_cmd_detects_duplicate_values(env_file: Path, capsys):
    rc = run_summarize_command(_make_args(str(env_file), fmt="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    # DB_HOST and BACKUP_HOST both have 'localhost'
    assert data["duplicate_group_count"] >= 1


def test_summarize_cmd_missing_file_returns_error(tmp_path: Path, capsys):
    rc = run_summarize_command(_make_args(str(tmp_path / "missing.env")))
    assert rc == 1
    assert "error" in capsys.readouterr().err
