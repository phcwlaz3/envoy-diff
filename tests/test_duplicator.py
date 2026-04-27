"""Tests for envoy_diff.duplicator."""
import pytest
from envoy_diff.duplicator import duplicate_config, DuplicateResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "CACHE_HOST": "redis",
    }


def test_no_mapping_returns_original(sample_config):
    result = duplicate_config(sample_config, {})
    assert result.config == sample_config


def test_duplicate_adds_target_key(sample_config):
    result = duplicate_config(sample_config, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.config
    assert result.config["DATABASE_HOST"] == "localhost"


def test_original_key_preserved(sample_config):
    result = duplicate_config(sample_config, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" in result.config


def test_duplicated_list_populated(sample_config):
    result = duplicate_config(sample_config, {"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" in result.duplicated


def test_missing_source_key_skipped(sample_config):
    result = duplicate_config(sample_config, {"MISSING_KEY": "NEW_KEY"})
    assert "MISSING_KEY" in result.skipped
    assert "NEW_KEY" not in result.config


def test_existing_target_not_overwritten_by_default(sample_config):
    result = duplicate_config(sample_config, {"DB_HOST": "CACHE_HOST"})
    assert result.config["CACHE_HOST"] == "redis"
    assert "DB_HOST" in result.skipped


def test_existing_target_overwritten_when_flag_set(sample_config):
    result = duplicate_config(sample_config, {"DB_HOST": "CACHE_HOST"}, overwrite=True)
    assert result.config["CACHE_HOST"] == "localhost"
    assert "DB_HOST" in result.duplicated


def test_multiple_mappings(sample_config):
    mapping = {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
    result = duplicate_config(sample_config, mapping)
    assert result.config["DATABASE_HOST"] == "localhost"
    assert result.config["DATABASE_PORT"] == "5432"
    assert result.duplicate_count() == 2


def test_has_duplicates_true(sample_config):
    result = duplicate_config(sample_config, {"DB_HOST": "DATABASE_HOST"})
    assert result.has_duplicates() is True


def test_has_duplicates_false(sample_config):
    result = duplicate_config(sample_config, {})
    assert result.has_duplicates() is False


def test_summary_no_duplicates(sample_config):
    result = duplicate_config(sample_config, {})
    assert result.summary() == "No keys duplicated."


def test_summary_with_duplicates(sample_config):
    result = duplicate_config(sample_config, {"DB_HOST": "DATABASE_HOST"})
    assert "Duplicated 1 key(s)" in result.summary()
    assert "DB_HOST" in result.summary()


def test_summary_with_skipped(sample_config):
    result = duplicate_config(sample_config, {"MISSING": "NEW"})
    # No duplicated keys, so summary is the no-op message
    assert result.summary() == "No keys duplicated."
