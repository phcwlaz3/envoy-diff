"""Tests for envoy_diff.highlighter."""
import pytest
from envoy_diff.highlighter import (
    highlight_config,
    ADDED_MARKER,
    REMOVED_MARKER,
    CHANGED_MARKER,
    UNCHANGED_MARKER,
)


@pytest.fixture
def base_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_ENV": "staging",
    }


@pytest.fixture
def new_config():
    return {
        "DB_HOST": "prod-db.example.com",
        "DB_PORT": "5432",
        "LOG_LEVEL": "info",
    }


def test_added_key_marked(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert result.highlighted["LOG_LEVEL"].startswith(ADDED_MARKER)


def test_removed_key_marked(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert result.highlighted["APP_ENV"].startswith(REMOVED_MARKER)


def test_changed_key_marked(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert result.highlighted["DB_HOST"].startswith(CHANGED_MARKER)


def test_unchanged_key_marked(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert result.highlighted["DB_PORT"].startswith(UNCHANGED_MARKER)


def test_added_keys_list(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert "LOG_LEVEL" in result.added_keys


def test_removed_keys_list(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert "APP_ENV" in result.removed_keys


def test_changed_keys_list(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert "DB_HOST" in result.changed_keys


def test_highlight_count(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert result.highlight_count() == 3


def test_has_highlights_true(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    assert result.has_highlights() is True


def test_has_highlights_false():
    cfg = {"KEY": "value"}
    result = highlight_config(cfg, reference=cfg)
    assert result.has_highlights() is False


def test_no_reference_all_keys_added():
    cfg = {"A": "1", "B": "2"}
    result = highlight_config(cfg)
    assert set(result.added_keys) == {"A", "B"}
    assert result.removed_keys == []
    assert result.changed_keys == []


def test_summary_no_differences():
    cfg = {"X": "y"}
    result = highlight_config(cfg, reference=cfg)
    assert "No differences" in result.summary()


def test_summary_with_differences(base_config, new_config):
    result = highlight_config(new_config, reference=base_config)
    s = result.summary()
    assert "added" in s
    assert "removed" in s
    assert "changed" in s
