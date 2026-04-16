"""Tests for envoy_diff.flattener."""
import pytest
from envoy_diff.flattener import flatten_config, FlattenResult


@pytest.fixture
def nested_config():
    return {
        "database": {
            "host": "localhost",
            "port": "5432",
            "credentials": {"user": "admin", "password": "secret"},
        },
        "debug": "true",
    }


def test_flatten_simple_dict():
    result = flatten_config({"A": "1", "B": "2"})
    assert result.config == {"A": "1", "B": "2"}


def test_flatten_nested_dict(nested_config):
    result = flatten_config(nested_config)
    assert result.config["database.host"] == "localhost"
    assert result.config["database.port"] == "5432"
    assert result.config["database.credentials.user"] == "admin"
    assert result.config["database.credentials.password"] == "secret"
    assert result.config["debug"] == "true"


def test_flatten_original_key_count(nested_config):
    result = flatten_config(nested_config)
    assert result.original_key_count == 2


def test_flatten_flattened_key_count(nested_config):
    result = flatten_config(nested_config)
    assert result.flattened_key_count == 5


def test_flatten_custom_separator():
    config = {"db": {"host": "localhost"}}
    result = flatten_config(config, sep="_")
    assert "db_host" in result.config


def test_flatten_uppercase_keys():
    config = {"db": {"host": "localhost"}}
    result = flatten_config(config, uppercase_keys=True)
    assert "DB_HOST" in result.config


def test_flatten_list_values():
    config = {"ports": ["8080", "9090"]}
    result = flatten_config(config)
    assert result.config["ports.0"] == "8080"
    assert result.config["ports.1"] == "9090"


def test_flatten_none_value_becomes_empty_string():
    result = flatten_config({"KEY": None})
    assert result.config["KEY"] == ""


def test_flatten_empty_config():
    result = flatten_config({})
    assert result.config == {}
    assert result.key_count == 0


def test_flatten_summary_contains_counts(nested_config):
    result = flatten_config(nested_config)
    assert "2" in result.summary
    assert "5" in result.summary


def test_flatten_result_is_flatten_result(nested_config):
    result = flatten_config(nested_config)
    assert isinstance(result, FlattenResult)
