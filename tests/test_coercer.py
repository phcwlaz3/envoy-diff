import pytest
from envoy_diff.coercer import coerce_config, CoerceResult


@pytest.fixture
def sample_config():
    return {
        "PORT": "8080",
        "TIMEOUT": "3.14",
        "DEBUG": "true",
        "WORKERS": "4",
        "NAME": "myapp",
        "ENABLED": "yes",
    }


def test_coerce_int(sample_config):
    result = coerce_config(sample_config, {"PORT": "int"})
    assert result.config["PORT"] == 8080
    assert isinstance(result.config["PORT"], int)


def test_coerce_float(sample_config):
    result = coerce_config(sample_config, {"TIMEOUT": "float"})
    assert result.config["TIMEOUT"] == pytest.approx(3.14)


def test_coerce_bool_true_variants(sample_config):
    for val in ["true", "1", "yes", "on"]:
        cfg = {"FLAG": val}
        result = coerce_config(cfg, {"FLAG": "bool"})
        assert result.config["FLAG"] is True


def test_coerce_bool_false_variants():
    for val in ["false", "0", "no", "off"]:
        cfg = {"FLAG": val}
        result = coerce_config(cfg, {"FLAG": "bool"})
        assert result.config["FLAG"] is False


def test_coerce_str_is_noop(sample_config):
    result = coerce_config(sample_config, {"NAME": "str"})
    assert result.config["NAME"] == "myapp"
    assert result.coerced["NAME"] == "str"


def test_coerce_multiple_rules(sample_config):
    result = coerce_config(sample_config, {"PORT": "int", "DEBUG": "bool", "TIMEOUT": "float"})
    assert result.config["PORT"] == 8080
    assert result.config["DEBUG"] is True
    assert result.coerce_count() == 3


def test_missing_key_skipped(sample_config):
    result = coerce_config(sample_config, {"NONEXISTENT": "int"})
    assert "NONEXISTENT" not in result.coerced
    assert result.coerce_count() == 0


def test_invalid_int_recorded_as_failure():
    result = coerce_config({"PORT": "not_a_number"}, {"PORT": "int"})
    assert "PORT" in result.failures
    assert result.has_failures()
    assert result.config["PORT"] == "not_a_number"  # original preserved


def test_invalid_bool_recorded_as_failure():
    result = coerce_config({"FLAG": "maybe"}, {"FLAG": "bool"})
    assert "FLAG" in result.failures


def test_unknown_type_recorded_as_failure():
    result = coerce_config({"KEY": "val"}, {"KEY": "list"})
    assert "KEY" in result.failures


def test_summary_no_failures():
    result = coerce_config({"PORT": "9000"}, {"PORT": "int"})
    assert "1 key(s) coerced" in result.summary()
    assert "failure" not in result.summary()


def test_summary_with_failures():
    result = coerce_config({"PORT": "bad"}, {"PORT": "int"})
    assert "failure" in result.summary()


def test_unrelated_keys_unchanged(sample_config):
    result = coerce_config(sample_config, {"PORT": "int"})
    assert result.config["NAME"] == "myapp"
    assert result.config["DEBUG"] == "true"
