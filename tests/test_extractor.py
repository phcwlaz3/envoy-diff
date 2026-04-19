import pytest
from envoy_diff.extractor import extract_config, ExtractResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
        "APP_NAME": "envoy",
        "SECRET_KEY": "abc123",
    }


def test_extract_by_explicit_keys(sample_config):
    result = extract_config(sample_config, keys=["DB_HOST", "APP_NAME"])
    assert "DB_HOST" in result.extracted
    assert "APP_NAME" in result.extracted
    assert len(result.extracted) == 2


def test_extract_by_pattern(sample_config):
    result = extract_config(sample_config, pattern=r"^DB_")
    assert "DB_HOST" in result.extracted
    assert "DB_PORT" in result.extracted
    assert "REDIS_HOST" not in result.extracted


def test_extract_by_prefix(sample_config):
    result = extract_config(sample_config, prefix="REDIS_")
    assert "REDIS_HOST" in result.extracted
    assert "REDIS_PORT" in result.extracted
    assert len(result.extracted) == 2


def test_extract_no_filters_returns_empty(sample_config):
    result = extract_config(sample_config)
    assert result.extracted == {}
    assert len(result.skipped) == len(sample_config)


def test_extract_skipped_contains_non_matching(sample_config):
    result = extract_config(sample_config, prefix="DB_")
    assert "REDIS_HOST" in result.skipped
    assert "APP_NAME" in result.skipped


def test_extract_count(sample_config):
    result = extract_config(sample_config, prefix="DB_")
    assert result.extract_count() == 2


def test_has_skipped_true(sample_config):
    result = extract_config(sample_config, keys=["DB_HOST"])
    assert result.has_skipped() is True


def test_has_skipped_false():
    config = {"DB_HOST": "localhost"}
    result = extract_config(config, keys=["DB_HOST"])
    assert result.has_skipped() is False


def test_summary_includes_pattern(sample_config):
    result = extract_config(sample_config, pattern=r"^DB_")
    assert "pattern" in result.summary()


def test_pattern_stored_in_result(sample_config):
    result = extract_config(sample_config, pattern=r"SECRET")
    assert result.pattern == r"SECRET"


def test_extract_empty_config():
    result = extract_config({}, prefix="DB_")
    assert result.extracted == {}
    assert result.skipped == []
