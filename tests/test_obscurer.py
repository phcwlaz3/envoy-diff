import pytest
from envoy_diff.obscurer import obscure_config, ObscureResult, MASK_CHAR, MASK_LENGTH


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abcdef123456",
        "APP_TOKEN": "tok_live_xyz",
        "LOG_LEVEL": "info",
    }


def test_sensitive_keys_are_obscured(sample_config):
    result = obscure_config(sample_config)
    assert result.obscured["DB_PASSWORD"] != sample_config["DB_PASSWORD"]
    assert result.obscured["API_KEY"] != sample_config["API_KEY"]
    assert result.obscured["APP_TOKEN"] != sample_config["APP_TOKEN"]


def test_non_sensitive_keys_unchanged(sample_config):
    result = obscure_config(sample_config)
    assert result.obscured["DB_HOST"] == "localhost"
    assert result.obscured["LOG_LEVEL"] == "info"


def test_obscured_keys_listed(sample_config):
    result = obscure_config(sample_config)
    assert "DB_PASSWORD" in result.obscured_keys
    assert "API_KEY" in result.obscured_keys
    assert "APP_TOKEN" in result.obscured_keys
    assert "DB_HOST" not in result.obscured_keys


def test_visible_prefix_preserved(sample_config):
    result = obscure_config(sample_config, visible_chars=4)
    assert result.obscured["DB_PASSWORD"].startswith("supe")
    assert result.obscured["API_KEY"].startswith("abcd")


def test_mask_suffix_appended(sample_config):
    result = obscure_config(sample_config, visible_chars=4)
    suffix = MASK_CHAR * MASK_LENGTH
    assert result.obscured["DB_PASSWORD"].endswith(suffix)


def test_obscure_count(sample_config):
    result = obscure_config(sample_config)
    assert result.obscure_count() == 3


def test_has_obscured_true(sample_config):
    result = obscure_config(sample_config)
    assert result.has_obscured() is True


def test_has_obscured_false():
    result = obscure_config({"LOG_LEVEL": "debug", "APP_ENV": "staging"})
    assert result.has_obscured() is False


def test_empty_value_not_broken():
    result = obscure_config({"API_KEY": ""})
    assert result.obscured["API_KEY"] == ""


def test_custom_pattern():
    config = {"MY_CUSTOM_SECRET_FIELD": "value123", "NORMAL_KEY": "hello"}
    result = obscure_config(config, patterns=[r"(?i)custom"])
    assert result.obscured["MY_CUSTOM_SECRET_FIELD"] != "value123"
    assert result.obscured["NORMAL_KEY"] == "hello"


def test_summary_string(sample_config):
    result = obscure_config(sample_config)
    s = result.summary()
    assert "3" in s
    assert "5" in s


def test_original_unchanged(sample_config):
    result = obscure_config(sample_config)
    assert result.original["DB_PASSWORD"] == "supersecret"
