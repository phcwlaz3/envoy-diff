"""Integration tests for diff command combining loader + differ + scorer."""
import json
import pytest
from argparse import Namespace
from envoy_diff.commands.diff_cmd import run_diff_command


@pytest.fixture
def staging(tmp_path):
    f = tmp_path / "staging.env"
    f.write_text(
        "DB_HOST=staging.db\nDB_PASS=secret\nFEATURE_X=false\nLOG_LEVEL=debug\n"
    )
    return str(f)


@pytest.fixture
def production(tmp_path):
    f = tmp_path / "production.env"
    f.write_text(
        "DB_HOST=prod.db\nDB_PASS=hunter2\nFEATURE_X=true\nNEW_RELIC_KEY=abc123\n"
    )
    return str(f)


def _args(base, head, fmt="json", score=False):
    return Namespace(base=base, head=head, format=fmt, score=score)


def test_integration_detects_all_change_types(staging, production, capsys):
    run_diff_command(_args(staging, production))
    data = json.loads(capsys.readouterr().out)
    assert "NEW_RELIC_KEY" in data["added"]
    assert "LOG_LEVEL" in data["removed"]
    assert "DB_HOST" in data["changed"]


def test_integration_unchanged_count(staging, production, capsys):
    run_diff_command(_args(staging, production))
    data = json.loads(capsys.readouterr().out)
    # DB_PASS changed, so unchanged = 0 from those keys
    assert isinstance(data["unchanged_count"], int)


def test_integration_score_present_when_requested(staging, production, capsys):
    run_diff_command(_args(staging, production, score=True))
    data = json.loads(capsys.readouterr().out)
    assert 0 <= data["score"] <= 100
    assert data["risk"] in ("low", "medium", "high")


def test_integration_identical_files_score_100(staging, capsys):
    run_diff_command(_args(staging, staging, score=True))
    data = json.loads(capsys.readouterr().out)
    assert data["score"] == 100
    assert data["risk"] == "low"
