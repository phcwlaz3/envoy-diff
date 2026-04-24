"""Tests for envoy_diff.mapper."""
import pytest
from envoy_diff.mapper import map_config, MapResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "CACHE_URL": "redis://localhost",
        "APP_DEBUG": "true",
        "SECRET_KEY": "abc123",
    }


def test_no_mapping_returns_original(sample_config):
    result = map_config(sample_config)
    assert result.mapped == sample_config
    assert result.map_count() == 0
    assert result.unmapped == list(sample_config.keys())


def test_explicit_mapping_renames_key(sample_config):
    result = map_config(sample_config, explicit={"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.mapped
    assert "DB_HOST" not in result.mapped
    assert result.mapped["DATABASE_HOST"] == "localhost"


def test_explicit_mapping_recorded(sample_config):
    result = map_config(sample_config, explicit={"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST" in result.mapping_applied


def test_unmapped_keys_preserved_by_default(sample_config):
    result = map_config(sample_config, explicit={"DB_HOST": "DATABASE_HOST"})
    assert "DB_PORT" in result.mapped
    assert "CACHE_URL" in result.mapped


def test_drop_unmapped_excludes_unmatched_keys(sample_config):
    result = map_config(
        sample_config,
        explicit={"DB_HOST": "DATABASE_HOST"},
        drop_unmapped=True,
    )
    assert "DATABASE_HOST" in result.mapped
    assert "DB_PORT" not in result.mapped
    assert len(result.mapped) == 1


def test_pattern_mapping_renames_matching_keys(sample_config):
    result = map_config(sample_config, patterns={r"^DB_": "DATABASE_"})
    assert "DATABASE_HOST" in result.mapped
    assert "DATABASE_PORT" in result.mapped
    assert result.map_count() == 2


def test_pattern_mapping_leaves_non_matching_keys(sample_config):
    result = map_config(sample_config, patterns={r"^DB_": "DATABASE_"})
    assert "CACHE_URL" in result.mapped
    assert "APP_DEBUG" in result.mapped


def test_explicit_takes_priority_over_pattern(sample_config):
    result = map_config(
        sample_config,
        explicit={"DB_HOST": "OVERRIDE_HOST"},
        patterns={r"^DB_": "DATABASE_"},
    )
    assert "OVERRIDE_HOST" in result.mapped
    assert "DATABASE_HOST" not in result.mapped
    # DB_PORT still matched by pattern
    assert "DATABASE_PORT" in result.mapped


def test_map_count_correct(sample_config):
    result = map_config(sample_config, patterns={r"^DB_": "DATABASE_"})
    assert result.map_count() == 2


def test_has_unmapped_true_when_keys_not_matched(sample_config):
    result = map_config(sample_config, explicit={"DB_HOST": "DATABASE_HOST"})
    assert result.has_unmapped() is True


def test_has_unmapped_false_when_all_matched():
    config = {"DB_HOST": "localhost"}
    result = map_config(config, explicit={"DB_HOST": "DATABASE_HOST"})
    assert result.has_unmapped() is False


def test_summary_includes_mapped_count(sample_config):
    result = map_config(sample_config, patterns={r"^DB_": "DATABASE_"})
    assert "2 key(s) mapped" in result.summary()


def test_summary_includes_unmapped_count(sample_config):
    result = map_config(sample_config, patterns={r"^DB_": "DATABASE_"})
    assert "unmapped" in result.summary()


def test_empty_config_returns_empty():
    result = map_config({}, explicit={"FOO": "BAR"})
    assert result.mapped == {}
    assert result.map_count() == 0
