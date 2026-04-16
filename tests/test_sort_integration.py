import pytest
from envoy_diff.sorter import sort_config
from envoy_diff.loader import load_config


@pytest.fixture
def mixed_env(tmp_path):
    f = tmp_path / "mixed.env"
    f.write_text(
        "SENTRY_DSN=https://example.sentry.io\n"
        "APP_PORT=8080\n"
        "DB_HOST=localhost\n"
        "LOG_LEVEL=debug\n"
        "Z=last\n"
    )
    return str(f)


def test_integration_alpha_sort(mixed_env):
    config = load_config(mixed_env)
    result = sort_config(config, strategy="alpha")
    keys = list(result.config.keys())
    assert keys == sorted(keys)


def test_integration_length_sort(mixed_env):
    config = load_config(mixed_env)
    result = sort_config(config, strategy="length")
    keys = list(result.config.keys())
    lengths = [len(k) for k in keys]
    assert lengths == sorted(lengths)


def test_integration_value_length_sort(mixed_env):
    config = load_config(mixed_env)
    result = sort_config(config, strategy="value_length")
    keys = list(result.config.keys())
    val_lengths = [len(config[k]) for k in keys]
    assert val_lengths == sorted(val_lengths)


def test_integration_original_order_preserved(mixed_env):
    config = load_config(mixed_env)
    result = sort_config(config)
    assert set(result.original_order) == set(config.keys())
    assert len(result.original_order) == len(config)
