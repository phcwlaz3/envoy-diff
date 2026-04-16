"""Tests for envoy_diff.tagger."""
import pytest
from envoy_diff.tagger import tag_config, TagResult


RULES = {
    "secret": ["PASSWORD", "SECRET", "TOKEN"],
    "database": ["DB", "DATABASE", "POSTGRES"],
    "feature": ["FEATURE", "FLAG", "ENABLE"],
}


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "s3cr3t",
        "API_TOKEN": "abc123",
        "ENABLE_FEATURE_X": "true",
        "APP_PORT": "8080",
    }


def test_tag_database_key(sample_config):
    result = tag_config(sample_config, RULES)
    assert "database" in result.tagged["DB_HOST"]


def test_tag_multiple_tags_on_one_key(sample_config):
    result = tag_config(sample_config, RULES)
    tags = result.tagged["DB_PASSWORD"]
    assert "secret" in tags
    assert "database" in tags


def test_tag_secret_key(sample_config):
    result = tag_config(sample_config, RULES)
    assert "secret" in result.tagged["API_TOKEN"]


def test_tag_feature_key(sample_config):
    result = tag_config(sample_config, RULES)
    tags = result.tagged["ENABLE_FEATURE_X"]
    assert "feature" in tags


def test_untagged_key(sample_config):
    result = tag_config(sample_config, RULES)
    assert "APP_PORT" in result.untagged


def test_empty_config():
    result = tag_config({}, RULES)
    assert result.tagged == {}
    assert result.untagged == set()
    assert result.tag_count() == 0


def test_empty_rules(sample_config):
    result = tag_config(sample_config, {})
    assert result.tagged == {}
    assert result.untagged == set(sample_config.keys())


def test_tag_count(sample_config):
    result = tag_config(sample_config, RULES)
    assert result.tag_count() >= len(result.tagged)


def test_summary_format(sample_config):
    result = tag_config(sample_config, RULES)
    s = result.summary()
    assert "tagged" in s
    assert "/" in s
