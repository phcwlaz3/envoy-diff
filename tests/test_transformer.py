"""Tests for envoy_diff.transformer module."""

import pytest
from envoy_diff.transformer import (
    TransformResult,
    transform_config,
)


@pytest.fixture
def sample_config():
    return {
        "db_host": "  localhost  ",
        "db_port": "5432",
        "api_key": "secret",
    }


def test_no_transforms_returns_original(sample_config):
    result = transform_config(sample_config, transforms=[])
    assert result.config == sample_config
    assert result.transform_count == 0


def test_uppercase_keys(sample_config):
    result = transform_config(sample_config, transforms=["uppercase_keys"])
    assert "DB_HOST" in result.config
    assert "db_host" not in result.config
    assert result.transform_count == 1
    assert "uppercase_keys" in result.applied


def test_strip_values(sample_config):
    result = transform_config(sample_config, transforms=["strip_values"])
    assert result.config["db_host"] == "localhost"
    assert result.transform_count == 1


def test_multiple_transforms_applied_in_order(sample_config):
    result = transform_config(sample_config, transforms=["strip_values", "uppercase_keys"])
    assert result.config["DB_HOST"] == "localhost"
    assert len(result.applied) == 2


def test_unknown_transform_is_skipped(sample_config):
    result = transform_config(sample_config, transforms=["nonexistent_transform"])
    assert result.config == sample_config
    assert "nonexistent_transform" in result.skipped
    assert result.transform_count == 0


def test_prefix_applied(sample_config):
    result = transform_config(sample_config, transforms=[], prefix="APP_")
    assert all(k.startswith("APP_") for k in result.config)
    assert result.transform_count == 1


def test_prefix_combined_with_uppercase(sample_config):
    result = transform_config(sample_config, transforms=["uppercase_keys"], prefix="PROD_")
    assert "PROD_DB_HOST" in result.config
    assert result.transform_count == 2


def test_summary_no_transforms(sample_config):
    result = transform_config(sample_config, transforms=[])
    assert result.summary() == "No transformations applied."


def test_summary_with_transforms(sample_config):
    result = transform_config(sample_config, transforms=["uppercase_keys"])
    assert "uppercase_keys" in result.summary()
    assert "1 transformation" in result.summary()


def test_summary_with_skipped(sample_config):
    result = transform_config(sample_config, transforms=["uppercase_keys", "bad_one"])
    assert "Skipped" in result.summary()
    assert "bad_one" in result.summary()


def test_original_config_not_mutated(sample_config):
    original = dict(sample_config)
    transform_config(sample_config, transforms=["uppercase_keys", "strip_values"], prefix="X_")
    assert sample_config == original
