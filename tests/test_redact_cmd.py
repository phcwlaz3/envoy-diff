"""Tests for envoy_diff.commands.redact_cmd."""

import json
import pytest

from envoy_diff.commands.redact_cmd import add_redact_subparsers, run_redact_command
import argparse


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "app.env"
    f.write_text(
        "APP_NAME=myapp\n"
        "API_KEY=super_secret\n"
        "PORT=9000\n"
        "DB_PASSWORD=hunter2\n"
    )
    return str(f)


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_redact_subparsers(sub)
    return p


def _make_args(file, mask="***REDACTED***", output_format="text", show_summary=False):
    ns = argparse.Namespace(
        file=file,
        mask=mask,
        output_format=output_format,
        show_summary=show_summary,
    )
    return ns


def test_redact_cmd_text_output(env_file, capsys):
    args = _make_args(env_file)
    rc = run_redact_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "APP_NAME=myapp" in out
    assert "PORT=9000" in out
    assert "***REDACTED***" in out
    assert "super_secret" not in out
    assert "hunter2" not in out


def test_redact_cmd_json_output(env_file, capsys):
    args = _make_args(env_file, output_format="json")
    rc = run_redact_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["APP_NAME"] == "myapp"
    assert data["API_KEY"] == "***REDACTED***"
    assert data["DB_PASSWORD"] == "***REDACTED***"


def test_redact_cmd_custom_mask(env_file, capsys):
    args = _make_args(env_file, mask="[HIDDEN]")
    run_redact_command(args)
    out = capsys.readouterr().out
    assert "[HIDDEN]" in out


def test_redact_cmd_show_summary(env_file, capsys):
    args = _make_args(env_file, show_summary=True)
    run_redact_command(args)
    err = capsys.readouterr().err
    assert "redacted" in err


def test_redact_cmd_invalid_file(capsys):
    args = _make_args("/nonexistent/path.env")
    rc = run_redact_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().err


def test_redact_cmd_parser_registered(parser):
    args = parser.parse_args(["redact", "somefile.env"])
    assert args.command == "redact"
    assert args.file == "somefile.env"
    assert args.mask == "***REDACTED***"
    assert args.output_format == "text"
