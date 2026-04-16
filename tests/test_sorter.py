import pytest
from envoy_diff.sorter import sort_config, SortResult


@pytest.fixture
def sample_config():
    return {
        "ZEBRA_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_PASSWORD": "secret",
        "LOG_LEVEL": "info",
        "X": "val",
    }


def test_sort_alpha_default(sample_config):
    result = sort_config(sample_config)
    assert list(result.config.keys()) == sorted(sample_config.keys())


def test_sort_alpha_reverse(sample_config):
    result = sort_config(sample_config, strategy="alpha", reverse=True)
    assert list(result.config.keys()) == sorted(sample_config.keys(), reverse=True)


def test_sort_by_length(sample_config):
    result = sort_config(sample_config, strategy="length")
    keys = list(result.config.keys())
    lengths = [len(k) for k in keys]
    assert lengths == sorted(lengths)


def test_sort_by_value_length(sample_config):
    result = sort_config(sample_config, strategy="value_length")
    keys = list(result.config.keys())
    val_lengths = [len(sample_config[k]) for k in keys]
    assert val_lengths == sorted(val_lengths)


def test_sort_preserves_values(sample_config):
    result = sort_config(sample_config)
    for k, v in result.config.items():
        assert sample_config[k] == v


def test_sort_original_order_recorded(sample_config):
    result = sort_config(sample_config)
    assert result.original_order == list(sample_config.keys())


def test_sort_unknown_strategy_raises(sample_config):
    with pytest.raises(ValueError, match="Unknown sort strategy"):
        sort_config(sample_config, strategy="random")


def test_sort_key_count(sample_config):
    result = sort_config(sample_config)
    assert result.key_count() == len(sample_config)


def test_sort_summary_contains_strategy(sample_config):
    result = sort_config(sample_config, strategy="length")
    assert "length" in result.summary()
    assert str(len(sample_config)) in result.summary()


def test_sort_empty_config():
    result = sort_config({})
    assert result.config == {}
    assert result.key_count() == 0
