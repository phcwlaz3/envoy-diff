"""Tests for envoy_diff.scorer."""

import pytest

from envoy_diff.differ import DiffResult
from envoy_diff.scorer import ScoreResult, score_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_diff(added=None, removed=None, changed=None, unchanged=None):
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
        unchanged=unchanged or {},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_empty_diff_scores_100():
    result = score_diff(_make_diff())
    assert result.score == 100.0


def test_empty_diff_risk_is_low():
    result = score_diff(_make_diff())
    assert result.risk_level == "low"


def test_added_keys_reduce_score():
    diff = _make_diff(added={"NEW_KEY": "val"})
    result = score_diff(diff)
    assert result.score < 100.0


def test_removed_keys_penalise_more_than_added():
    diff_added = _make_diff(added={"A": "1", "B": "2"})
    diff_removed = _make_diff(removed={"A": "1", "B": "2"})
    assert score_diff(diff_removed).score < score_diff(diff_added).score


def test_changed_keys_reduce_score():
    diff = _make_diff(changed={"KEY": ("old", "new")})
    result = score_diff(diff)
    assert result.score < 100.0


def test_score_never_below_zero():
    # Flood with changes to ensure capping works
    many = {f"K{i}": str(i) for i in range(200)}
    diff = _make_diff(removed=many)
    result = score_diff(diff)
    assert result.score >= 0.0


def test_score_never_above_100():
    result = score_diff(_make_diff())
    assert result.score <= 100.0


def test_breakdown_keys_present():
    diff = _make_diff(added={"X": "1"}, removed={"Y": "2"}, changed={"Z": ("a", "b")})
    result = score_diff(diff)
    assert "added" in result.breakdown
    assert "removed" in result.breakdown
    assert "changed" in result.breakdown


def test_high_risk_when_score_low():
    many_removed = {f"K{i}": str(i) for i in range(50)}
    diff = _make_diff(removed=many_removed)
    result = score_diff(diff)
    assert result.risk_level == "high"


def test_note_added_for_many_removals():
    diff = _make_diff(
        removed={"A": "1", "B": "2", "C": "3"},
        added={"D": "4"},
    )
    result = score_diff(diff)
    assert any("removed" in note.lower() for note in result.notes)


def test_note_added_for_many_changes():
    changed = {f"K{i}": ("old", "new") for i in range(6)}
    result = score_diff(_make_diff(changed=changed))
    assert any("changed" in note.lower() for note in result.notes)


def test_summary_contains_score():
    result = score_diff(_make_diff())
    assert "100.0" in result.summary()
    assert "low" in result.summary()
