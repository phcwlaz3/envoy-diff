import pytest
from envoy_diff.splitter import split_config, SplitResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
        "APP_ENV": "production",
        "STANDALONE": "value",
    }


def test_split_by_explicit_prefixes(sample_config):
    result = split_config(sample_config, prefixes=["DB", "REDIS"])
    assert set(result.buckets["DB"]) == {"DB_HOST", "DB_PORT"}
    assert set(result.buckets["REDIS"]) == {"REDIS_HOST", "REDIS_PORT"}


def test_split_unmatched_keys(sample_config):
    result = split_config(sample_config, prefixes=["DB"])
    assert "STANDALONE" in result.unmatched
    assert "APP_ENV" in result.unmatched


def test_split_has_unmatched_true(sample_config):
    result = split_config(sample_config, prefixes=["DB"])
    assert result.has_unmatched()


def test_split_no_unmatched_when_all_matched():
    config = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = split_config(config, prefixes=["DB"])
    assert not result.has_unmatched()


def test_split_bucket_count(sample_config):
    result = split_config(sample_config, prefixes=["DB", "REDIS", "APP"])
    assert result.bucket_count() == 3


def test_split_auto_detects_prefixes(sample_config):
    result = split_config(sample_config, auto=True)
    assert "DB" in result.buckets
    assert "REDIS" in result.buckets


def test_split_auto_skips_single_occurrence():
    config = {"DB_HOST": "localhost", "DB_PORT": "5432", "STANDALONE": "x"}
    result = split_config(config, auto=True)
    assert "STANDALONE" not in result.buckets
    assert "STANDALONE" in result.unmatched


def test_split_empty_config():
    result = split_config({}, prefixes=["DB"])
    assert result.buckets["DB"] == {}
    assert not result.has_unmatched()


def test_split_summary_contains_bucket_names(sample_config):
    result = split_config(sample_config, prefixes=["DB", "REDIS"])
    s = result.summary()
    assert "DB" in s
    assert "REDIS" in s


def test_split_no_prefixes_all_unmatched(sample_config):
    result = split_config(sample_config, prefixes=[])
    assert result.bucket_count() == 0
    assert len(result.unmatched) == len(sample_config)
