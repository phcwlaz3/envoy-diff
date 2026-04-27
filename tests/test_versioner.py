"""Tests for envoy_diff.versioner."""
import pytest
from envoy_diff.versioner import version_config, VersionResult


@pytest.fixture
def sample_config():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


def test_version_result_contains_original_keys(sample_config):
    result = version_config(sample_config, version="1.0.0")
    assert result.config["DB_HOST"] == "localhost"
    assert result.config["DB_PORT"] == "5432"


def test_version_injects_version_key(sample_config):
    result = version_config(sample_config, version="2.3.1")
    assert result.config["ENVOY_VERSION"] == "2.3.1"


def test_version_injects_stamped_at(sample_config):
    result = version_config(sample_config, version="1.0.0")
    assert "ENVOY_STAMPED_AT" in result.config
    assert result.config["ENVOY_STAMPED_AT"].endswith("Z")


def test_version_injects_label_when_provided(sample_config):
    result = version_config(sample_config, version="1.0.0", label="release-42")
    assert result.config["ENVOY_LABEL"] == "release-42"
    assert "ENVOY_LABEL" in result.keys_stamped


def test_version_no_label_key_when_omitted(sample_config):
    result = version_config(sample_config, version="1.0.0")
    assert "ENVOY_LABEL" not in result.config


def test_version_stamp_count_without_label(sample_config):
    result = version_config(sample_config, version="1.0.0")
    assert result.stamp_count() == 2


def test_version_stamp_count_with_label(sample_config):
    result = version_config(sample_config, version="1.0.0", label="v1")
    assert result.stamp_count() == 3


def test_version_has_stamps_true(sample_config):
    result = version_config(sample_config, version="1.0.0")
    assert result.has_stamps() is True


def test_version_no_inject_skips_stamps(sample_config):
    result = version_config(sample_config, version="1.0.0", inject_keys=False)
    assert result.stamp_count() == 0
    assert result.has_stamps() is False
    assert "ENVOY_VERSION" not in result.config


def test_version_custom_prefix(sample_config):
    result = version_config(sample_config, version="3.0.0", prefix="APP_META_")
    assert "APP_META_VERSION" in result.config
    assert result.config["APP_META_VERSION"] == "3.0.0"


def test_version_result_stores_version_field(sample_config):
    result = version_config(sample_config, version="0.9.0")
    assert result.version == "0.9.0"


def test_version_summary_contains_version(sample_config):
    result = version_config(sample_config, version="1.2.3")
    assert "1.2.3" in result.summary()


def test_version_summary_contains_label(sample_config):
    result = version_config(sample_config, version="1.0.0", label="hotfix")
    assert "hotfix" in result.summary()


def test_version_does_not_mutate_input(sample_config):
    original_keys = set(sample_config.keys())
    version_config(sample_config, version="1.0.0")
    assert set(sample_config.keys()) == original_keys
