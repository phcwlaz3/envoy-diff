"""Tests for envoy_diff.differ_v2."""
import pytest
from envoy_diff.differ_v2 import DeltaEntry, DeltaResult, delta_configs


@pytest.fixture
def left():
    return {"HOST": "localhost", "PORT": "5432", "OLD_KEY": "gone"}


@pytest.fixture
def right():
    return {"HOST": "prod.db", "PORT": "5432", "NEW_KEY": "arrived"}


def test_delta_added_key(left, right):
    result = delta_configs(left, right)
    keys = [e.key for e in result.added]
    assert "NEW_KEY" in keys


def test_delta_removed_key(left, right):
    result = delta_configs(left, right)
    keys = [e.key for e in result.removed]
    assert "OLD_KEY" in keys


def test_delta_changed_key(left, right):
    result = delta_configs(left, right)
    keys = [e.key for e in result.changed]
    assert "HOST" in keys


def test_delta_unchanged_key(left, right):
    result = delta_configs(left, right)
    keys = [e.key for e in result.unchanged]
    assert "PORT" in keys


def test_delta_has_diff_true(left, right):
    result = delta_configs(left, right)
    assert result.has_diff is True


def test_delta_has_diff_false():
    cfg = {"A": "1", "B": "2"}
    result = delta_configs(cfg, cfg)
    assert result.has_diff is False


def test_delta_exclude_unchanged(left, right):
    result = delta_configs(left, right, include_unchanged=False)
    assert all(e.status != "unchanged" for e in result.entries)


def test_delta_left_value_on_removed(left, right):
    result = delta_configs(left, right)
    removed = {e.key: e for e in result.removed}
    assert removed["OLD_KEY"].left_value == "gone"
    assert removed["OLD_KEY"].right_value is None


def test_delta_right_value_on_added(left, right):
    result = delta_configs(left, right)
    added = {e.key: e for e in result.added}
    assert added["NEW_KEY"].right_value == "arrived"
    assert added["NEW_KEY"].left_value is None


def test_delta_both_values_on_changed(left, right):
    result = delta_configs(left, right)
    changed = {e.key: e for e in result.changed}
    assert changed["HOST"].left_value == "localhost"
    assert changed["HOST"].right_value == "prod.db"


def test_delta_summary_format(left, right):
    result = delta_configs(left, right)
    s = result.summary()
    assert "+1 added" in s
    assert "-1 removed" in s
    assert "~1 changed" in s
    assert "=1 unchanged" in s


def test_delta_to_dict_keys(left, right):
    result = delta_configs(left, right)
    d = result.to_dict()
    assert set(d.keys()) == {"added", "removed", "changed", "unchanged", "summary"}


def test_delta_entry_to_dict():
    entry = DeltaEntry(key="X", status="added", right_value="val")
    d = entry.to_dict()
    assert d["key"] == "X"
    assert d["status"] == "added"
    assert d["right_value"] == "val"
    assert d["left_value"] is None


def test_delta_empty_configs():
    result = delta_configs({}, {})
    assert result.has_diff is False
    assert result.entries == []
