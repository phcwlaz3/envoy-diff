"""Tests for envoy_diff.patcher."""

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.patcher import PatchError, PatchResult, patch_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(
    added=None,
    removed=None,
    changed=None,
    unchanged=None,
) -> DiffResult:
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_patch_adds_new_keys():
    base = {"HOST": "localhost"}
    diff = _make_diff(added={"PORT": "5432"})
    result = patch_config(base, diff)
    assert result.patched["PORT"] == "5432"
    assert "PORT" in result.applied


def test_patch_removes_keys():
    base = {"HOST": "localhost", "DEBUG": "true"}
    diff = _make_diff(removed={"DEBUG": "true"})
    result = patch_config(base, diff)
    assert "DEBUG" not in result.patched
    assert "DEBUG" in result.applied


def test_patch_changes_values():
    base = {"HOST": "localhost"}
    diff = _make_diff(changed={"HOST": ("localhost", "db.prod")})
    result = patch_config(base, diff)
    assert result.patched["HOST"] == "db.prod"
    assert "HOST" in result.applied


def test_patch_unchanged_keys_preserved():
    base = {"HOST": "localhost", "PORT": "5432"}
    diff = _make_diff(unchanged={"PORT": "5432"})
    result = patch_config(base, diff)
    assert result.patched["PORT"] == "5432"


def test_patch_add_conflict_records_error():
    base = {"PORT": "5432"}
    diff = _make_diff(added={"PORT": "9999"})
    result = patch_config(base, diff)
    assert result.has_errors
    assert any("PORT" in e for e in result.errors)
    assert result.patched["PORT"] == "5  # unchanged


def test_patch_add_conflict_strict_raises():
    base = {"PORT": "5432"}
    diff = _make_diff(added={"PORT": "9999"})
    with pytest.raises(PatchError, match="PORT"):
        patch_config(base, diff, strict=True)


def test_patch_change_conflict_records_error():
    base = {"HOST": "staging.host"}
    diff = _make_diff(changed={"HOST": ("localhost", "prod.host")})
    result = patch_config(base, diff)
    assert result.has_errors
    assert any("HOST" in e for e in result.errors)


def test_patch_remove_missing_key_records_error():
    base = {"HOST": "localhost"}
    diff = _make_diff(removed={"MISSING_KEY": "val"})
    result = patch_config(base, diff)
    assert result.has_errors


def test_patch_ignore_removed_skips_removal():
    base = {"HOST": "localhost", "DEBUG": "true"}
    diff = _make_diff(removed={"DEBUG": "true"})
    result = patch_config(base, diff, ignore_removed=True)
    assert "DEBUG" in result.patched
    assert "DEBUG" in result.skipped
    assert not result.has_errors


def test_patch_apply_count():
    base = {"A": "1", "B": "2"}
    diff = _make_diff(
        added={"C": "3"},
        changed={"A": ("1", "10")},
        removed={"B": "2"},
    )
    result = patch_config(base, diff)
    assert result.apply_count == 3


def test_patch_summary_no_issues():
    base = {"A": "1"}
    diff = _make_diff(added={"B": "2"})
    result = patch_config(base, diff)
    assert "1 change(s) applied" in result.summary()


def test_patch_summary_with_skipped():
    base = {"A": "1", "B": "old"}
    diff = _make_diff(removed={"B": "old"})
    result = patch_config(base, diff, ignore_removed=True)
    assert "skipped" in result.summary()


def test_patch_empty_diff_returns_base_unchanged():
    base = {"HOST": "localhost", "PORT": "5432"}
    diff = _make_diff()
    result = patch_config(base, diff)
    assert result.patched == base
    assert result.apply_count == 0
