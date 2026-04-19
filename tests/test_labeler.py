import pytest
from envoy_diff.labeler import label_config, LabelResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "REDIS_URL": "redis://localhost",
        "FEATURE_DARK_MODE": "true",
        "APP_NAME": "myapp",
        "API_TOKEN": "abc123",
    }


def test_database_key_labeled(sample_config):
    result = label_config(sample_config)
    assert "database" in result.labels["DB_HOST"]


def test_secret_key_labeled(sample_config):
    result = label_config(sample_config)
    assert "secret" in result.labels["DB_PASSWORD"]


def test_multiple_labels_on_one_key(sample_config):
    result = label_config(sample_config)
    # DB_PASSWORD matches both database and secret
    labels = result.labels["DB_PASSWORD"]
    assert "database" in labels
    assert "secret" in labels


def test_cache_key_labeled(sample_config):
    result = label_config(sample_config)
    assert "cache" in result.labels["REDIS_URL"]


def test_feature_key_labeled(sample_config):
    result = label_config(sample_config)
    assert "feature" in result.labels["FEATURE_DARK_MODE"]


def test_unlabeled_key_not_in_labels(sample_config):
    result = label_config(sample_config)
    assert "APP_NAME" not in result.labels


def test_label_count(sample_config):
    result = label_config(sample_config)
    assert result.label_count() > 0


def test_has_labels_true(sample_config):
    result = label_config(sample_config)
    assert result.has_labels()


def test_has_labels_false_empty():
    result = label_config({"APP_NAME": "x", "VERSION": "1"})
    assert not result.has_labels()


def test_extra_rules_applied(sample_config):
    result = label_config(sample_config, extra_rules={"versioned": r"VERSION"})
    # no VERSION key in sample, just verify no crash
    assert isinstance(result, LabelResult)


def test_extra_rule_matches():
    config = {"BUILD_VERSION": "1.2.3", "APP_NAME": "x"}
    result = label_config(config, extra_rules={"versioned": r"VERSION"})
    assert "versioned" in result.labels["BUILD_VERSION"]


def test_summary_string(sample_config):
    result = label_config(sample_config)
    s = result.summary()
    assert "label" in s
    assert "key" in s


def test_original_config_preserved(sample_config):
    result = label_config(sample_config)
    assert result.config == sample_config


def test_api_token_labeled(sample_config):
    """API_TOKEN should be labeled as a secret due to TOKEN keyword match."""
    result = label_config(sample_config)
    assert "secret" in result.labels["API_TOKEN"]


def test_empty_config():
    """label_config should handle an empty config without errors."""
    result = label_config({})
    assert isinstance(result, LabelResult)
    assert result.labels == {}
    assert not result.has_labels()
    assert result.label_count() == 0
