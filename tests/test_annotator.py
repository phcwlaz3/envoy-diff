"""Tests for envoy_diff.annotator."""
import pytest
from envoy_diff.annotator import annotate_config, AnnotateResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "API_KEY": "secret",
        "LOG_LEVEL": "info",
    }


def test_annotate_matching_keys(sample_config):
    result = annotate_config(sample_config, {"DB_HOST": "primary database host"})
    assert "DB_HOST" in result.annotated
    assert result.annotated["DB_HOST"]["annotation"] == "primary database host"
    assert result.annotated["DB_HOST"]["value"] == "localhost"


def test_annotate_preserves_value(sample_config):
    result = annotate_config(sample_config, {"API_KEY": "sensitive"})
    assert result.annotated["API_KEY"]["value"] == "secret"


def test_annotate_missing_key_skipped(sample_config):
    result = annotate_config(sample_config, {"MISSING_KEY": "some note"})
    assert "MISSING_KEY" not in result.annotated
    assert "MISSING_KEY" in result.skipped


def test_annotate_multiple_keys(sample_config):
    annotations = {"DB_HOST": "host", "DB_PORT": "port", "LOG_LEVEL": "verbosity"}
    result = annotate_config(sample_config, annotations)
    assert result.annotation_count() == 3
    assert len(result.skipped) == 0


def test_annotate_empty_config():
    result = annotate_config({}, {"DB_HOST": "note"})
    assert result.annotation_count() == 0
    assert "DB_HOST" in result.skipped


def test_annotate_empty_annotations(sample_config):
    result = annotate_config(sample_config, {})
    assert result.annotation_count() == 0
    assert result.skipped == []


def test_annotation_count(sample_config):
    result = annotate_config(sample_config, {"DB_HOST": "a", "API_KEY": "b"})
    assert result.annotation_count() == 2


def test_summary_string(sample_config):
    result = annotate_config(
        sample_config,
        {"DB_HOST": "note", "MISSING": "other"},
    )
    s = result.summary()
    assert "1 of 2 keys annotated" in s
    assert "1 skipped" in s


def test_partial_overlap(sample_config):
    annotations = {"DB_HOST": "host", "UNKNOWN": "x", "API_KEY": "key"}
    result = annotate_config(sample_config, annotations)
    assert result.annotation_count() == 2
    assert "UNKNOWN" in result.skipped
