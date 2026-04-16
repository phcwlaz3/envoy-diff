import pytest
from envoy_diff.truncator import truncate_config, TruncateResult, DEFAULT_MAX_LENGTH


@pytest.fixture
def sample_config():
    return {
        "SHORT": "hi",
        "EXACT": "x" * DEFAULT_MAX_LENGTH,
        "LONG": "y" * (DEFAULT_MAX_LENGTH + 20),
        "ALSO_LONG": "z" * 200,
    }


def test_short_value_unchanged(sample_config):
    result = truncate_config(sample_config)
    assert result.truncated["SHORT"] == "hi"


def test_exact_length_not_truncated(sample_config):
    result = truncate_config(sample_config)
    assert result.truncated["EXACT"] == "x" * DEFAULT_MAX_LENGTH
    assert "EXACT" not in result.truncated_keys


def test_long_value_is_truncated(sample_config):
    result = truncate_config(sample_config)
    v = result.truncated["LONG"]
    assert len(v) == DEFAULT_MAX_LENGTH
    assert v.endswith("...")


def test_truncated_keys_listed(sample_config):
    result = truncate_config(sample_config)
    assert "LONG" in result.truncated_keys
    assert "ALSO_LONG" in result.truncated_keys


def test_short_key_not_in_truncated_keys(sample_config):
    result = truncate_config(sample_config)
    assert "SHORT" not in result.truncated_keys


def test_truncation_count(sample_config):
    result = truncate_config(sample_config)
    assert result.truncation_count() == 2


def test_has_truncations_true(sample_config):
    result = truncate_config(sample_config)
    assert result.has_truncations() is True


def test_has_truncations_false():
    result = truncate_config({"A": "short"})
    assert result.has_truncations() is False


def test_summary_with_truncations(sample_config):
    result = truncate_config(sample_config)
    assert "truncated" in result.summary()


def test_summary_no_truncations():
    result = truncate_config({"A": "ok"})
    assert result.summary() == "No values truncated."


def test_custom_max_length():
    config = {"KEY": "hello world"}
    result = truncate_config(config, max_length=5)
    assert result.truncated["KEY"] == "he..."


def test_specific_keys_only():
    config = {"A": "y" * 100, "B": "z" * 100}
    result = truncate_config(config, keys=["A"])
    assert len(result.truncated["A"]) == DEFAULT_MAX_LENGTH
    assert result.truncated["B"] == "z" * 100
    assert "B" not in result.truncated_keys


def test_original_preserved(sample_config):
    result = truncate_config(sample_config)
    assert result.original is sample_config
