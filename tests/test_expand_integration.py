import pytest
from envoy_diff.loader import load_config
from envoy_diff.expander import expand_config


@pytest.fixture
def mixed_env(tmp_path):
    f = tmp_path / "mixed.env"
    f.write_text(
        "DB_HOSTS=primary,replica1,replica2\n"
        "CACHE_NODES=redis1,redis2\n"
        "APP_NAME=myapp\n"
        "LOG_LEVEL=info\n"
        "FEATURE_FLAGS=flag_a,flag_b,flag_c\n"
    )
    return str(f)


def test_integration_expands_three_multi_value_keys(mixed_env):
    config = load_config(mixed_env)
    result = expand_config(config)
    assert result.expand_count == 3


def test_integration_db_hosts_expanded(mixed_env):
    config = load_config(mixed_env)
    result = expand_config(config)
    assert result.config["DB_HOSTS_1"] == "primary"
    assert result.config["DB_HOSTS_2"] == "replica1"
    assert result.config["DB_HOSTS_3"] == "replica2"


def test_integration_single_value_keys_unchanged(mixed_env):
    config = load_config(mixed_env)
    result = expand_config(config)
    assert result.config["APP_NAME"] == "myapp"
    assert result.config["LOG_LEVEL"] == "info"


def test_integration_feature_flags_count(mixed_env):
    config = load_config(mixed_env)
    result = expand_config(config)
    assert len(result.expanded["FEATURE_FLAGS"]) == 3


def test_integration_summary_mentions_count(mixed_env):
    config = load_config(mixed_env)
    result = expand_config(config)
    assert "3 key(s)" in result.summary()
