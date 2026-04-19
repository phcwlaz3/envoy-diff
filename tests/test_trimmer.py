import pytest
from envoy_diff.trimmer import TrimResult, trim_config


@pytest.fixture
def sample_config():
    return {
        "DATABASE_URL": "  postgres://localhost/db  ",
        "APP_NAME": "myapp",
        "SECRET_KEY": "\tsecret\t",
        "PORT": "8080",
        "EMPTY": "   ",
    }


def test_no_whitespace_returns_original():
    config = {"KEY": "value", "OTHER": "clean"}
    result = trim_config(config)
    assert result.config == config
    assert result.trim_count() == 0


def test_trims_leading_and_trailing_spaces(sample_config):
    result = trim_config(sample_config)
    assert result.config["DATABASE_URL"] == "postgres://localhost/db"


def test_trims_tabs(sample_config):
    result = trim_config(sample_config)
    assert result.config["SECRET_KEY"] == "secret"


def test_trims_empty_to_empty_string(sample_config):
    result = trim_config(sample_config)
    assert result.config["EMPTY"] == ""


def test_untouched_key_not_in_trimmed_list(sample_config):
    result = trim_config(sample_config)
    assert "APP_NAME" not in result.trimmed_keys
    assert "PORT" not in result.trimmed_keys


def test_trimmed_keys_listed(sample_config):
    result = trim_config(sample_config)
    assert "DATABASE_URL" in result.trimmed_keys
    assert "SECRET_KEY" in result.trimmed_keys
    assert "EMPTY" in result.trimmed_keys


def test_trim_count(sample_config):
    result = trim_config(sample_config)
    assert result.trim_count() == 3


def test_has_trimmed_true(sample_config):
    result = trim_config(sample_config)
    assert result.has_trimmed() is True


def test_has_trimmed_false():
    result = trim_config({"KEY": "clean"})
    assert result.has_trimmed() is False


def test_selective_keys_only_trims_specified():
    config = {"A": "  hello  ", "B": "  world  "}
    result = trim_config(config, keys=["A"])
    assert result.config["A"] == "hello"
    assert result.config["B"] == "  world  "
    assert result.trimmed_keys == ["A"]


def test_custom_strip_chars():
    config = {"KEY": "***value***", "OTHER": "clean"}
    result = trim_config(config, strip_chars="*")
    assert result.config["KEY"] == "value"
    assert result.config["OTHER"] == "clean"


def test_summary_no_trims():
    result = trim_config({"KEY": "value"})
    assert result.summary() == "No values trimmed."


def test_summary_with_trims():
    result = trim_config({"KEY": "  value  "})
    assert "1 value(s) trimmed" in result.summary()
    assert "KEY" in result.summary()
