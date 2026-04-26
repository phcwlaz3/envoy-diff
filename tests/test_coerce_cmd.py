from __future__ import annotations

import json
import os
import pytest

from argparse import Namespace
from envoy_diff.commands.coerce_cmd import run_coerce_command


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "config.env"
    f.write_text(
        "PORT=8080\n"
        "DEBUG=true\n"
        "RATIO=3.14\n"
        "NAME=myapp\n"
    )
    return str(f)


@pytest.fixture
def dirty_env_file(tmp_path):
    f = tmp_path / "dirty.env"
    f.write_text(
        "PORT=8080\n"
        "DEBUG=true\n"
        "NAME=myapp\n"
    )
    return str(f)


def _make_args(file, fmt="text", strict=False):
    return Namespace(file=file, format=fmt, strict=strict)


def test_coerce_cmd_text_output(env_file, capsys):
    rc = run_coerce_command(_make_args(env_file))
    captured = capsys.readouterr()
    assert rc == 0
    assert "coerced" in captured.out.lower() or "Coerced" in captured.out


def test_coerce_cmd_json_output(env_file, capsys):
    rc = run_coerce_command(_make_args(env_file, fmt="json"))
    captured = capsys.readouterr()
    assert rc == 0
    data = json.loads(captured.out)
    assert "coerced" in data
    assert "failures" in data
    assert "coerce_count" in data
    assert "has_failures" in data
    assert "summary" in data


def test_coerce_cmd_int_coerced(env_file, capsys):
    rc = run_coerce_command(_make_args(env_file, fmt="json"))
    captured = capsys.readouterr()
    assert rc == 0
    data = json.loads(captured.out)
    assert "PORT" in data["coerced"]
    assert data["coerced"]["PORT"] == 8080


def test_coerce_cmd_bool_coerced(env_file, capsys):
    rc = run_coerce_command(_make_args(env_file, fmt="json"))
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["coerced"]["DEBUG"] is True


def test_coerce_cmd_missing_file_returns_error(tmp_path, capsys):
    rc = run_coerce_command(_make_args(str(tmp_path / "missing.env")))
    assert rc == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err


def test_coerce_cmd_strict_no_failures_returns_zero(env_file):
    rc = run_coerce_command(_make_args(env_file, strict=True))
    assert rc == 0
