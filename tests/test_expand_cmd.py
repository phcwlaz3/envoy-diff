import json
import pytest
from argparse import Namespace
from envoy_diff.commands.expand_cmd import run_expand_command


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / "test.env"
    f.write_text("HOSTS=host1,host2,host3\nDB_URL=postgres://localhost/db\nTAGS=alpha,beta\n")
    return str(f)


def _make_args(file, delimiter=",", suffix_template="_{i}", fmt="text"):
    return Namespace(file=file, delimiter=delimiter, suffix_template=suffix_template, format=fmt)


def test_expand_cmd_text_output(env_file, capsys):
    args = _make_args(env_file)
    rc = run_expand_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "HOSTS_1=host1" in out
    assert "HOSTS_2=host2" in out


def test_expand_cmd_json_output(env_file, capsys):
    args = _make_args(env_file, fmt="json")
    rc = run_expand_command(args)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert "HOSTS_1" in data["config"]
    assert "expand_count" in data
    assert data["expand_count"] == 2


def test_expand_cmd_non_multi_preserved(env_file, capsys):
    args = _make_args(env_file, fmt="json")
    run_expand_command(args)
    data = json.loads(capsys.readouterr().out)
    assert data["config"]["DB_URL"] == "postgres://localhost/db"


def test_expand_cmd_invalid_file(capsys):
    args = _make_args("/nonexistent/path.env")
    rc = run_expand_command(args)
    assert rc == 1
    assert "Error" in capsys.readouterr().out


def test_expand_cmd_custom_delimiter(tmp_path, capsys):
    f = tmp_path / "pipes.env"
    f.write_text("SERVERS=a|b|c\n")
    args = _make_args(str(f), delimiter="|")
    rc = run_expand_command(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "SERVERS_1=a" in out
    assert "SERVERS_3=c" in out
