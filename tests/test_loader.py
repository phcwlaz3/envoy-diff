"""Tests for envoy_diff.loader module."""

import json
import os
import pytest
from pathlib import Path

from envoy_diff.loader import (
    load_config,
    load_env_file,
    load_json_file,
    UnsupportedFormatError,
)


@pytest.fixture
def tmp_env_file(tmp_path):
    content = (
        "# Production config\n"
        "DATABASE_URL=postgres://localhost/prod\n"
        "DEBUG=false\n"
        "SECRET_KEY='my-secret'\n"
        "  API_KEY = abc123  \n"
        "\n"
        "LOG_LEVEL=info\n"
    )
    env_file = tmp_path / "prod.env"
    env_file.write_text(content)
    return str(env_file)


@pytest.fixture
def tmp_json_file(tmp_path):
    data = {"DATABASE_URL": "postgres://localhost/staging", "DEBUG": "true", "PORT": "8080"}
    json_file = tmp_path / "staging.json"
    json_file.write_text(json.dumps(data))
    return str(json_file)


def test_load_env_file_basic(tmp_env_file):
    result = load_env_file(tmp_env_file)
    assert result["DATABASE_URL"] == "postgres://localhost/prod"
    assert result["DEBUG"] == "false"
    assert result["SECRET_KEY"] == "my-secret"
    assert result["API_KEY"] == "abc123"
    assert result["LOG_LEVEL"] == "info"


def test_load_env_file_ignores_comments_and_blanks(tmp_env_file):
    result = load_env_file(tmp_env_file)
    assert len(result) == 5


def test_load_env_file_not_found():
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_env_file("/nonexistent/path/.env")


def test_load_env_file_invalid_format(tmp_path):
    bad_file = tmp_path / "bad.env"
    bad_file.write_text("NODEQUALS\n")
    with pytest.raises(ValueError, match="Invalid format"):
        load_env_file(str(bad_file))


def test_load_json_file_basic(tmp_json_file):
    result = load_json_file(tmp_json_file)
    assert result["DATABASE_URL"] == "postgres://localhost/staging"
    assert result["DEBUG"] == "true"
    assert result["PORT"] == "8080"


def test_load_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_json_file("/no/such/file.json")


def test_load_json_file_non_dict(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text(json.dumps(["not", "a", "dict"]))
    with pytest.raises(ValueError, match="top-level object"):
        load_json_file(str(bad_json))


def test_load_config_dispatches_env(tmp_env_file):
    result = load_config(tmp_env_file)
    assert "DATABASE_URL" in result


def test_load_config_dispatches_json(tmp_json_file):
    result = load_config(tmp_json_file)
    assert "DATABASE_URL" in result


def test_load_config_unsupported_format(tmp_path):
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("key: value\n")
    with pytest.raises(UnsupportedFormatError, match="Unsupported file format"):
        load_config(str(yaml_file))
