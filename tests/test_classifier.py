"""Tests for envoy_diff.classifier module."""

import pytest
from envoy_diff.classifier import classify_config, ClassificationResult, UNCATEGORIZED


@pytest.fixture
def mixed_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "JWT_SECRET": "supersecret",
        "LOG_LEVEL": "INFO",
        "FEATURE_DARK_MODE": "true",
        "AWS_REGION": "us-east-1",
        "APP_NAME": "myapp",
        "PORT": "8080",
    }


def test_classify_database_keys(mixed_config):
    result = classify_config(mixed_config)
    assert "DB_HOST" in result.categories["database"]
    assert "DB_PORT" in result.categories["database"]


def test_classify_auth_keys(mixed_config):
    result = classify_config(mixed_config)
    assert "JWT_SECRET" in result.categories["auth"]


def test_classify_logging_keys(mixed_config):
    result = classify_config(mixed_config)
    assert "LOG_LEVEL" in result.categories["logging"]


def test_classify_feature_flag_keys(mixed_config):
    result = classify_config(mixed_config)
    assert "FEATURE_DARK_MODE" in result.categories["feature_flags"]


def test_classify_infrastructure_keys(mixed_config):
    result = classify_config(mixed_config)
    assert "AWS_REGION" in result.categories["infrastructure"]


def test_classify_network_keys(mixed_config):
    result = classify_config(mixed_config)
    assert "PORT" in result.categories["network"]


def test_uncategorized_keys(mixed_config):
    result = classify_config(mixed_config)
    assert "APP_NAME" in result.categories[UNCATEGORIZED]


def test_total_count(mixed_config):
    result = classify_config(mixed_config)
    assert result.total == len(mixed_config)


def test_category_count(mixed_config):
    result = classify_config(mixed_config)
    assert result.category_count() >= 5


def test_empty_config():
    result = classify_config({})
    assert result.total == 0
    assert result.category_count() == 0
    assert result.summary() == "No keys classified."


def test_summary_contains_category_info(mixed_config):
    result = classify_config(mixed_config)
    summary = result.summary()
    assert "database" in summary
    assert "auth" in summary
    assert "key(s)" in summary
