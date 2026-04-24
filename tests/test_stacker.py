import pytest
from envoy_diff.stacker import stack_configs, StackResult


@pytest.fixture
def base_layer():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "LOG_LEVEL": "info"}


@pytest.fixture
def override_layer():
    return {"DB_HOST": "prod.db.example.com", "CACHE_URL": "redis://cache"}


def test_stack_empty_list_returns_empty():
    result = stack_configs([])
    assert len(result.entries) == 0
    assert result.layer_count == 0


def test_stack_single_layer_no_overrides(base_layer):
    result = stack_configs([base_layer])
    assert result.layer_count == 1
    assert result.override_count == 0
    assert set(result.entries.keys()) == set(base_layer.keys())


def test_stack_single_layer_effective_values(base_layer):
    result = stack_configs([base_layer])
    assert result.entries["DB_HOST"].effective_value == "localhost"
    assert result.entries["DB_PORT"].effective_value == "5432"


def test_stack_last_wins_strategy(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer], strategy="last-wins")
    assert result.entries["DB_HOST"].effective_value == "prod.db.example.com"
    assert result.entries["DB_HOST"].source_index == 1


def test_stack_first_wins_strategy(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer], strategy="first-wins")
    assert result.entries["DB_HOST"].effective_value == "localhost"
    assert result.entries["DB_HOST"].source_index == 0


def test_stack_key_only_in_later_layer(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer])
    assert "CACHE_URL" in result.entries
    assert result.entries["CACHE_URL"].effective_value == "redis://cache"
    assert result.entries["CACHE_URL"].source_index == 1


def test_stack_key_only_in_base_layer(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer])
    assert "LOG_LEVEL" in result.entries
    assert result.entries["LOG_LEVEL"].effective_value == "info"


def test_stack_override_count(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer])
    # DB_HOST differs across layers
    assert result.override_count == 1


def test_stack_all_values_recorded(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer])
    db_host_entry = result.entries["DB_HOST"]
    assert len(db_host_entry.all_values) == 2
    assert (0, "localhost") in db_host_entry.all_values
    assert (1, "prod.db.example.com") in db_host_entry.all_values


def test_stack_summary_string(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer])
    s = result.summary()
    assert "2 layers" in s
    assert "overridden" in s


def test_stack_to_dict(base_layer, override_layer):
    result = stack_configs([base_layer, override_layer])
    d = result.to_dict()
    assert d["layer_count"] == 2
    assert "entries" in d
    assert "DB_HOST" in d["entries"]


def test_stack_three_layers():
    l1 = {"A": "1", "B": "x"}
    l2 = {"A": "2"}
    l3 = {"A": "3", "C": "z"}
    result = stack_configs([l1, l2, l3])
    assert result.entries["A"].effective_value == "3"
    assert result.entries["A"].source_index == 2
    assert result.layer_count == 3
    assert result.override_count == 1  # only A varies
