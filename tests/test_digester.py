"""Tests for envoy_diff.digester."""
import pytest
from envoy_diff.digester import digest_config, DigestResult


@pytest.fixture
def sample_config():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "false"}


def test_digest_returns_result(sample_config):
    result = digest_config(sample_config)
    assert isinstance(result, DigestResult)


def test_digest_is_string(sample_config):
    result = digest_config(sample_config)
    assert isinstance(result.digest, str)
    assert len(result.digest) == 64  # sha256 hex


def test_digest_key_count(sample_config):
    result = digest_config(sample_config)
    assert result.key_count == 3


def test_digest_empty_config():
    result = digest_config({})
    assert result.key_count == 0
    assert len(result.digest) == 64


def test_digest_deterministic(sample_config):
    r1 = digest_config(sample_config)
    r2 = digest_config(sample_config)
    assert r1.digest == r2.digest


def test_digest_order_independent():
    a = digest_config({"X": "1", "Y": "2"})
    b = digest_config({"Y": "2", "X": "1"})
    assert a.digest == b.digest


def test_digest_changes_when_value_changes(sample_config):
    r1 = digest_config(sample_config)
    modified = {**sample_config, "DB_PORT": "5433"}
    r2 = digest_config(modified)
    assert r1.digest != r2.digest


def test_no_previous_digest_not_changed(sample_config):
    result = digest_config(sample_config)
    assert result.changed is False
    assert result.previous_digest is None


def test_same_previous_digest_not_changed(sample_config):
    r1 = digest_config(sample_config)
    r2 = digest_config(sample_config, previous_digest=r1.digest)
    assert r2.changed is False


def test_different_previous_digest_changed(sample_config):
    result = digest_config(sample_config, previous_digest="deadbeef" * 8)
    assert result.changed is True


def test_algorithm_md5(sample_config):
    result = digest_config(sample_config, algorithm="md5")
    assert result.algorithm == "md5"
    assert len(result.digest) == 32


def test_unsupported_algorithm_raises(sample_config):
    with pytest.raises(ValueError, match="Unsupported"):
        digest_config(sample_config, algorithm="rot13")


def test_summary_contains_digest_prefix(sample_config):
    result = digest_config(sample_config)
    assert result.digest[:16] in result.summary()


def test_summary_shows_changed(sample_config):
    result = digest_config(sample_config, previous_digest="deadbeef" * 8)
    assert "changed" in result.summary()


def test_summary_shows_unchanged(sample_config):
    r1 = digest_config(sample_config)
    r2 = digest_config(sample_config, previous_digest=r1.digest)
    assert "unchanged" in r2.summary()
