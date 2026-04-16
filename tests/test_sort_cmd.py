import json
import pytest
from unittest.mock import patch
from argparse import Namespace
from envoy_diff.commands.sort_cmd import run_sort_command


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "test.env"
    f.write_text("ZEBRA=z\nAPP=a\nMID=m\n")
    return str(f)


def _make_args(file, strategy="alpha", reverse=False, fmt="text"):
    return Namespace(file=file, strategy=strategy, reverse=reverse, fmt=fmt)


def test_sort_cmd_text_output(env_file, capsys):
    rc = run_sort_command(_make_args(env_file))
    assert rc == 0
    out = capsys.readouterr().out
    assert "APP" in out
    assert "ZEBRA" in out
    idx_app = out.index("APP")
    idx_zebra = out.index("ZEBRA")
    assert idx_app < idx_zebra


def test_sort_cmd_json_output(env_file, capsys):
    rc = run_sort_command(_make_args(env_file, fmt="json"))
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["strategy"] == "alpha"
    assert "APP" in data["config"]


def test_sort_cmd_reverse(env_file, capsys):
    rc = run_sort_command(_make_args(env_file, reverse=True))
    assert rc == 0
    out = capsys.readouterr().out
    idx_app = out.index("APP")
    idx_zebra = out.index("ZEBRA")
    assert idx_zebra < idx_app


def test_sort_cmd_invalid_file_returns_error(capsys):
    rc = run_sort_command(_make_args("/no/such/file.env"))
    assert rc == 1
    assert "Error" in capsys.readouterr().err


def test_sort_cmd_length_strategy(env_file, capsys):
    rc = run_sort_command(_make_args(env_file, strategy="length"))
    assert rc == 0
    out = capsys.readouterr().out
    assert "length" in out
