"""Integration tests: profiler + profile_cmd together."""

import json
import pytest
from argparse import Namespace

.profile_cmd import run_profile_command
from envoy_diff.profiler import profile_config


@pytest.fixture()
def mixed_env(tmp_path):
    p = tmp_path / "mixed.env"
    lines = .example.com",
        "PORT=443",
        "DB_PASSWORD=hunter2",
        "AUTH_TOKEN=mysecret",
        "EMPTY_VAR="=false",
    ]
    p.write_text("\n".join(lines) + "\n")
    return str(p)


def test_integration_score_issues(mixed_env, capsys):
    args = Namespace(file=mixed_env, format="json")
    rc = run_profile_command(args)
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["score"] < 100
    assert payload["empty_count"] == 1
    assert len(payload["suspicious_keys"]) >= 2


def test_integration_profile_config_directly():
    config = {
        "HOST": "localhost",
        "PORT": "5432",
        "DB_SECRET": "topsecret",
        "MISSING": "",
    }
    result = profile_config(config)
    assert result.total_keys == 4
    assert result.empty_count == 1
    assert "DB_SECRET" in result.suspicious_keys
    assert result.score < 100
    assert result.grade() in list("ABCDF")


def test_integration_perfect_config_scores_100():
    config = {
        "HOST": "localhost",
        "PORT": "8080",
        "LOG_LEVEL": "info",
        "TIMEOUT": "30",
    }
    result = profile_config(config)
    assert result.score == 100
    assert result.grade() == "A"
    assert result.notes == []
