import pytest
from envoy_diff.loader import load_config
from envoy_diff.renamer import rename_config


@pytest.fixture
def mixed_env(tmp_path):
    f = tmp_path / "mixed.env"
    f.write_text(
        "OLD_DB_HOST=db.internal\n"
        "OLD_DB_PORT=5432\n"
        "APP_SECRET=topsecret\n"
        "FEATURE_FLAG=true\n"
    )
    return str(f)


def test_integration_pattern_renames_all_old_keys(mixed_env):
    config = load_config(mixed_env)
    result = rename_config(config, pattern=r"^OLD_", replacement="")
    assert "DB_HOST" in result.config
    assert "DB_PORT" in result.config
    assert "OLD_DB_HOST" not in result.config
    assert "OLD_DB_PORT" not in result.config


def test_integration_rename_count_correct(mixed_env):
    config = load_config(mixed_env)
    result = rename_config(config, pattern=r"^OLD_", replacement="")
    assert result.rename_count() == 2


def test_integration_unmatched_keys_preserved(mixed_env):
    config = load_config(mixed_env)
    result = rename_config(config, pattern=r"^OLD_", replacement="")
    assert result.config.get("APP_SECRET") == "topsecret"
    assert result.config.get("FEATURE_FLAG") == "true"


def test_integration_explicit_mapping_takes_priority(mixed_env):
    config = load_config(mixed_env)
    result = rename_config(
        config,
        mapping={"OLD_DB_HOST": "PRIMARY_HOST"},
        pattern=r"^OLD_",
        replacement="",
    )
    assert "PRIMARY_HOST" in result.config
    assert "DB_PORT" in result.config
    assert result.rename_count() == 2
