import pytest
from envoy_diff.renamer import rename_config, RenameResult


@pytest.fixture
def sample_config():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "abc123",
        "OLD_API_KEY": "key-xyz",
    }


def test_no_mapping_returns_original(sample_config):
    result = rename_config(sample_config)
    assert result.config == sample_config
    assert result.rename_count() == 0


def test_explicit_mapping_renames_key(sample_config):
    result = rename_config(sample_config, mapping={"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in result.config
    assert "DB_HOST" not in result.config
    assert result.config["DATABASE_HOST"] == "localhost"


def test_renamed_list_populated(sample_config):
    result = rename_config(sample_config, mapping={"DB_HOST": "DATABASE_HOST"})
    assert ("DB_HOST", "DATABASE_HOST") in result.renamed


def test_unmapped_keys_unchanged(sample_config):
    result = rename_config(sample_config, mapping={"DB_HOST": "DATABASE_HOST"})
    assert result.config["DB_PORT"] == "5432"
    assert result.config["APP_SECRET"] == "abc123"


def test_pattern_rename(sample_config):
    result = rename_config(sample_config, pattern=r"^OLD_", replacement="NEW_")
    assert "NEW_API_KEY" in result.config
    assert "OLD_API_KEY" not in result.config


def test_pattern_no_match_leaves_key(sample_config):
    result = rename_config(sample_config, pattern=r"^NONEXISTENT_", replacement="X_")
    assert result.config == sample_config
    assert result.rename_count() == 0


def test_mapping_and_pattern_combined():
    config = {"OLD_HOST": "h", "DB_PORT": "5432"}
    result = rename_config(
        config,
        mapping={"DB_PORT": "DATABASE_PORT"},
        pattern=r"^OLD_",
        replacement="NEW_",
    )
    assert "NEW_HOST" in result.config
    assert "DATABASE_PORT" in result.config
    assert result.rename_count() == 2


def test_conflict_skips_rename():
    config = {"OLD_KEY": "v1", "NEW_KEY": "v2"}
    result = rename_config(config, pattern=r"^OLD_", replacement="NEW_")
    assert "OLD_KEY" in result.config
    assert result.skipped == ["OLD_KEY"]


def test_has_renames_true_when_renamed(sample_config):
    result = rename_config(sample_config, mapping={"DB_HOST": "DATABASE_HOST"})
    assert result.has_renames() is True


def test_has_renames_false_when_nothing_renamed(sample_config):
    result = rename_config(sample_config)
    assert result.has_renames() is False


def test_summary_no_renames(sample_config):
    result = rename_config(sample_config)
    assert result.summary() == "No keys renamed."


def test_summary_with_renames(sample_config):
    result = rename_config(sample_config, mapping={"DB_HOST": "DATABASE_HOST"})
    assert "DB_HOST -> DATABASE_HOST" in result.summary()
