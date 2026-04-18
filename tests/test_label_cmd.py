import pytest
from unittest.mock import patch
from argparse import Namespace
from envoy_diff.commands.label_cmd import run_label_command


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "app.env"
    f.write_text(
        "DB_HOST=localhost\nDB_PASSWORD=secret\nAPP_NAME=myapp\nFEATURE_X=true\n"
    )
    return str(f)


def _make_args(file, fmt="text", rule=None, only_labeled=False):
    return Namespace(file=file, fmt=fmt, rule=rule or [], only_labeled=only_labeled)


def test_label_cmd_text_output(env_file, capsys):
    rc = run_label_command(_make_args(env_file))
    out = capsys.readouterr().out
    assert rc == 0
    assert "label" in out


def test_label_cmd_json_output(env_file, capsys):
    import json
    rc = run_label_command(_make_args(env_file, fmt="json"))
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert "labels" in data
    assert "label_count" in data


def test_label_cmd_database_key_labeled(env_file, capsys):
    run_label_command(_make_args(env_file, fmt="json"))
    import json
    # re-run to capture
    run_label_command(_make_args(env_file, fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DB_HOST" in data["labels"]


def test_label_cmd_only_labeled(env_file, capsys):
    rc = run_label_command(_make_args(env_file, only_labeled=True))
    out = capsys.readouterr().out
    assert rc == 0
    assert "APP_NAME" not in out


def test_label_cmd_extra_rule(env_file, capsys):
    import json
    rc = run_label_command(_make_args(env_file, fmt="json", rule=[["app", "APP_"]]))
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert "app" in data["labels"].get("APP_NAME", [])


def test_label_cmd_invalid_file_returns_error(capsys):
    rc = run_label_command(_make_args("/no/such/file.env"))
    assert rc == 1
    assert "error" in capsys.readouterr().out
