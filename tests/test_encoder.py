"""Tests for envoy_diff.encoder."""
import base64
import urllib.parse

import pytest

from envoy_diff.encoder import encode_config, EncodeResult


@pytest.fixture
def sample_config():
    return {
        "DB_URL": "postgres://localhost/mydb",
        "APP_NAME": "my app",
        "PORT": "8080",
        "EMPTY": "",
    }


def test_encode_base64_all_keys(sample_config):
    result = encode_config(sample_config, encoding="base64")
    assert result.encode_count() == len(sample_config)
    assert result.encoding == "base64"


def test_encode_base64_value_correct(sample_config):
    result = encode_config(sample_config, encoding="base64")
    expected = base64.b64encode(b"postgres://localhost/mydb").decode()
    assert result.encoded["DB_URL"] == expected


def test_encode_url_value_correct(sample_config):
    result = encode_config(sample_config, encoding="url")
    expected = urllib.parse.quote("postgres://localhost/mydb", safe="")
    assert result.encoded["DB_URL"] == expected


def test_encode_empty_value(sample_config):
    result = encode_config(sample_config, encoding="base64")
    expected = base64.b64encode(b"").decode()
    assert result.encoded["EMPTY"] == expected


def test_encode_selected_keys_only(sample_config):
    result = encode_config(sample_config, encoding="base64", keys=["DB_URL"])
    expected = base64.b64encode(b"postgres://localhost/mydb").decode()
    assert result.encoded["DB_URL"] == expected
    assert result.encoded["APP_NAME"] == "my app"
    assert result.encoded["PORT"] == "8080"


def test_encode_count_with_selected_keys(sample_config):
    result = encode_config(sample_config, encoding="base64", keys=["DB_URL", "PORT"])
    assert result.encode_count() == len(sample_config)


def test_no_skipped_by_default(sample_config):
    result = encode_config(sample_config, encoding="base64")
    assert not result.has_skipped()
    assert result.skipped == []


def test_summary_no_skipped(sample_config):
    result = encode_config(sample_config, encoding="base64")
    assert "base64" in result.summary()
    assert "skipped" not in result.summary()


def test_summary_with_skipped():
    result = EncodeResult(encoded={}, skipped=["KEY"], encoding="url")
    assert "skipped=1" in result.summary()


def test_encode_url_spaces(sample_config):
    result = encode_config(sample_config, encoding="url")
    assert result.encoded["APP_NAME"] == "my%20app"
