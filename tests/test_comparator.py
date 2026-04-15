"""Tests for envoy_diff.comparator module."""

import pytest
from envoy_diff.comparator import compare_configs, ComparisonResult


CONFIG_A = {
    "HOST": "localhost",
    "PORT": "8080",
    "DEBUG": "true",
}

CONFIG_B = {
    "HOST": "prod.example.com",
    "PORT": "443",
    "LOG_LEVEL": "warn",
}


def test_compare_detects_added_keys():
    result = compare_configs(CONFIG_A, CONFIG_B)
    assert "LOG_LEVEL" in result.diff.added


def test_compare_detects_removed_keys():
    result = compare_configs(CONFIG_A, CONFIG_B)
    assert "DEBUG" in result.diff.removed


def test_compare_detects_changed_keys():
    result = compare_configs(CONFIG_A, CONFIG_B)
    assert "HOST" in result.diff.changed
    assert "PORT" in result.diff.changed


def test_compare_has_diff_true_when_differences():
    result = compare_configs(CONFIG_A, CONFIG_B)
    assert result.has_diff is True


def test_compare_has_diff_false_when_identical():
    result = compare_configs(CONFIG_A, CONFIG_A)
    assert result.has_diff is False


def test_compare_labels_stored():
    result = compare_configs(CONFIG_A, CONFIG_B, label_a="staging", label_b="prod")
    assert result.label_a == "staging"
    assert result.label_b == "prod"


def test_compare_validation_passes_with_required_keys_present():
    result = compare_configs(
        {"HOST": "a", "PORT": "1"},
        {"HOST": "b", "PORT": "2"},
        required_keys=["HOST", "PORT"],
    )
    assert result.is_valid is True


def test_compare_validation_fails_when_required_key_missing():
    result = compare_configs(
        {"HOST": "a"},
        {"HOST": "b", "PORT": "443"},
        required_keys=["HOST", "PORT"],
    )
    # CONFIG_A side is missing PORT
    assert result.is_valid is False


def test_compare_required_keys_stored():
    result = compare_configs(CONFIG_A, CONFIG_B, required_keys=["HOST"])
    assert "HOST" in result.required_keys


def test_summary_contains_labels():
    result = compare_configs(CONFIG_A, CONFIG_B, label_a="dev", label_b="prod")
    summary = result.summary()
    assert "dev" in summary
    assert "prod" in summary


def test_summary_contains_counts():
    result = compare_configs(CONFIG_A, CONFIG_B)
    summary = result.summary()
    assert "Added keys" in summary
    assert "Removed keys" in summary
    assert "Changed keys" in summary


def test_compare_no_required_keys_defaults_to_empty():
    result = compare_configs(CONFIG_A, CONFIG_B)
    assert result.required_keys == []
