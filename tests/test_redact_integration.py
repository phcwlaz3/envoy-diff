"""Integration tests: redactor + loader working together."""

import json
import pytest

from envoy_diff.loader import load_config
from envoy_diff.redactor import redact_config, DEFAULT_MASK


@pytest.fixture
def mixed_env(tmp_path):
    f = tmp_path / "mixed.env"
    f.write_text(
        "SERVICE=auth-service\n"
        "AUTH_TOKEN=tok_abc123\n"
        "PRIVATE_KEY=-----BEGIN RSA-----\n"
        "LOG_LEVEL=info\n"
        "REPLICAS=3\n"
        "# this is a comment\n"
        "\n"
        "DB_PASSWORD=mypassword\n"
    )
    return str(f)


@pytest.fixture
def mixed_json(tmp_path):
    f = tmp_path / "mixed.json"
    data = {
        "SERVICE": "worker",
        "API_KEY": "key_xyz",
        "TIMEOUT": "30",
    }
    f.write_text(json.dumps(data))
    return str(f)


def test_integration_env_file_sensitive_keys_masked(mixed_env):
    config = load_config(mixed_env)
    result = redact_config(config)
    assert result.redacted["AUTH_TOKEN"] == DEFAULT_MASK
    assert result.redacted["PRIVATE_KEY"] == DEFAULT_MASK
    assert result.redacted["DB_PASSWORD"] == DEFAULT_MASK
    assert result.redacted["SERVICE"] == "auth-service"
    assert result.redacted["LOG_LEVEL"] == "info"


def test_integration_json_file_sensitive_keys_masked(mixed_json):
    config = load_config(mixed_json)
    result = redact_config(config)
    assert result.redacted["API_KEY"] == DEFAULT_MASK
    assert result.redacted["SERVICE"] == "worker"
    assert result.redacted["TIMEOUT"] == "30"


def test_integration_redaction_count_matches(mixed_env):
    config = load_config(mixed_env)
    result = redact_config(config)
    assert result.redaction_count == 3


def test_integration_original_preserved_after_redaction(mixed_env):
    config = load_config(mixed_env)
    result = redact_config(config)
    assert result.original == config
    assert config["AUTH_TOKEN"] == "tok_abc123"
