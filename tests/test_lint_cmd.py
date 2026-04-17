"""Tests for envoy_diff.commands.lint_cmd."""

import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from envoy_diff.commands.lint_cmd import add_lint_subparsers, run_lint_command


@pytest.fixture
def clean_env_file(tmp_path):
    f = tmp_path / "clean.env"
    f.write_text("DATABASE_URL=postgres://localhost/db\nAPP_PORT=8080\n")
    return str(f)


@pytest.fixture
def dirty_env_file(tmp_path):
    f = tmp_path / "dirty.env"
    f.write_text("lowercase_key=value\nHAS-HYPHEN=bad\nVALID=ok\n")
    return str(f)


def _make_args(file, fmt="text", strict=False):
    ns = argparse.Namespace(file=file, format=fmt, strict=strict)
    return ns


def test_lint_clean_file_returns_zero(clean_env_file):
    args = _make_args(clean_env_file)
    code = run_lint_command(args)
    assert code == 0


def test_lint_dirty_file_returns_nonzero(dirty_env_file):
    args = _make_args(dirty_env_file)
    code = run_lint_command(args)
    assert code != 0


def test_lint_text_output_contains_summary(clean_env_file, capsys):
    args = _make_args(clean_env_file)
    run_lint_command(args)
    captured = capsys.readouterr()
    assert "No lint issues" in captured.out


def test_lint_json_output_is_valid(dirty_env_file, capsys):
    args = _make_args(dirty_env_file, fmt="json")
    run_lint_command(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "issues" in data
    assert "error_count" in data


def test_lint_json_output_error_count_matches_issues(dirty_env_file, capsys):
    """Ensure error_count in JSON output is consistent with the issues list length."""
    args = _make_args(dirty_env_file, fmt="json")
    run_lint_command(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["error_count"] == len(data["issues"])


def test_lint_strict_warns_on_warnings(tmp_path, capsys):
    f = tmp_path / "warn.env"
    f.write_text("DOUBLE__SCORE=value\n")
    args = _make_args(str(f), strict=True)
    code = run_lint_command(args)
    assert code != 0


def test_lint_missing_file_returns_error(tmp_path):
    args = _make_args(str(tmp_path / "nonexistent.env"))
    code = run_lint_command(args)
    assert code == 1


def test_lint_dirty_file_json_issues_have_required_fields(dirty_env_file, capsys):
    """Each issue in JSON output should contain 'line', 'key', and 'message' fields."""
    args = _make_args(dirty_env_file, fmt="json")
    run_lint_command(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    for issue in data["issues"]:
        assert "line" in issue, f"Missing 'line' in issue: {issue}"
        assert "key" in issue, f"Missing 'key' in issue: {issue}"
        assert "message" in issue, f"Missing 'message' in issue: {issue}"


def test_add_lint_subparsers_registers_command():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_lint_subparsers(sub)
    parsed = parser.parse_args(["lint", "some.env"])
    assert parsed.file == "some.env"
