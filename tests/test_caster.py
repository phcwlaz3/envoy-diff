"""Tests for envoy_diff.caster."""
import pytest
from envoy_diff.caster import cast_config, CastResult


@pytest.fixture
def sample_config():
    return {
        "PORT": "8080",
        "DEBUG": "true",
        "RATIO": "0.75",
        "NAME": "myapp",
        "WORKERS": "4",
        "ENABLED": "false",
    }


def test_cast_int(sample_config):
    result = cast_config(sample_config, {"PORT": "int"})
    assert result.config["PORT"] == 8080
    assert isinstance(result.config["PORT"], int)


def test_cast_float(sample_config):
    result = cast_config(sample_config, {"RATIO": "float"})
    assert result.config["RATIO"] == pytest.approx(0.75)


def test_cast_bool_true(sample_config):
    result = cast_config(sample_config, {"DEBUG": "bool"})
    assert result.config["DEBUG"] is True


def test_cast_bool_false(sample_config):
    result = cast_config(sample_config, {"ENABLED": "bool"})
    assert result.config["ENABLED"] is False


def test_cast_str_unchanged(sample_config):
    result = cast_config(sample_config, {"NAME": "str"})
    assert result.config["NAME"] == "myapp"


def test_unspecified_keys_unchanged(sample_config):
    result = cast_config(sample_config, {"PORT": "int"})
    assert result.config["NAME"] == "myapp"
    assert result.config["DEBUG"] == "true"


def test_cast_keys_listed(sample_config):
    result = cast_config(sample_config, {"PORT": "int", "WORKERS": "int"})
    assert set(result.cast_keys) == {"PORT", "WORKERS"}


def test_failed_cast_recorded(sample_config):
    result = cast_config({"PORT": "not_a_number"}, {"PORT": "int"})
    assert "PORT" in result.failed_keys
    assert result.config["PORT"] == "not_a_number"


def test_has_failures_false_when_clean(sample_config):
    result = cast_config(sample_config, {"PORT": "int"})
    assert not result.has_failures()


def test_has_failures_true_when_bad(sample_config):
    result = cast_config({"PORT": "abc"}, {"PORT": "int"})
    assert result.has_failures()


def test_cast_count(sample_config):
    result = cast_config(sample_config, {"PORT": "int", "RATIO": "float", "DEBUG": "bool"})
    assert result.cast_count() == 3


def test_summary_no_failures(sample_config):
    result = cast_config(sample_config, {"PORT": "int"})
    assert "1 key(s) cast" in result.summary()
    assert "failure" not in result.summary()


def test_summary_with_failures():
    result = cast_config({"PORT": "bad"}, {"PORT": "int"})
    assert "failure" in result.summary()


def test_empty_type_map(sample_config):
    result = cast_config(sample_config, {})
    assert result.config == sample_config
    assert result.cast_count() == 0
