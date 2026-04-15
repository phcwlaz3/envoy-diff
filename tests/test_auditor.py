"""Tests for envoy_diff.auditor module."""

import json
from pathlib import Path

import pytest

from envoy_diff.auditor import (
    AuditEntry,
    AuditLog,
    AuditError,
    create_entry,
    load_audit_log,
    save_audit_log,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_entry() -> AuditEntry:
    return create_entry(
        stage_a="staging",
        stage_b="production",
        has_diff=True,
        validation_passed=False,
        added=2,
        removed=1,
        changed=3,
        label="release-42",
    )


@pytest.fixture()
def audit_log(sample_entry: AuditEntry) -> AuditLog:
    log = AuditLog()
    log.append(sample_entry)
    return log


# ---------------------------------------------------------------------------
# create_entry
# ---------------------------------------------------------------------------


def test_create_entry_fields(sample_entry: AuditEntry) -> None:
    assert sample_entry.stage_a == "staging"
    assert sample_entry.stage_b == "production"
    assert sample_entry.has_diff is True
    assert sample_entry.validation_passed is False
    assert sample_entry.added == 2
    assert sample_entry.removed == 1
    assert sample_entry.changed == 3
    assert sample_entry.label == "release-42"


def test_create_entry_timestamp_is_set(sample_entry: AuditEntry) -> None:
    assert sample_entry.timestamp
    assert "T" in sample_entry.timestamp  # ISO-8601 contains 'T'


def test_create_entry_defaults() -> None:
    entry = create_entry("a", "b", has_diff=False, validation_passed=True)
    assert entry.added == 0
    assert entry.removed == 0
    assert entry.changed == 0
    assert entry.label is None


# ---------------------------------------------------------------------------
# AuditEntry.to_dict
# ---------------------------------------------------------------------------


def test_entry_to_dict_keys(sample_entry: AuditEntry) -> None:
    d = sample_entry.to_dict()
    expected_keys = {
        "timestamp", "stage_a", "stage_b", "has_diff",
        "validation_passed", "added", "removed", "changed", "label",
    }
    assert set(d.keys()) == expected_keys


# ---------------------------------------------------------------------------
# save_audit_log / load_audit_log
# ---------------------------------------------------------------------------


def test_save_creates_file(tmp_path: Path, audit_log: AuditLog) -> None:
    dest = tmp_path / "audit.json"
    save_audit_log(audit_log, dest)
    assert dest.exists()


def test_save_and_load_roundtrip(tmp_path: Path, audit_log: AuditLog) -> None:
    dest = tmp_path / "audit.json"
    save_audit_log(audit_log, dest)
    loaded = load_audit_log(dest)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].stage_a == "staging"
    assert loaded.entries[0].label == "release-42"


def test_save_appends_to_existing(tmp_path: Path, sample_entry: AuditEntry) -> None:
    dest = tmp_path / "audit.json"
    log1 = AuditLog(entries=[sample_entry])
    save_audit_log(log1, dest)
    log2 = AuditLog(entries=[create_entry("dev", "staging", False, True)])
    save_audit_log(log2, dest)
    loaded = load_audit_log(dest)
    assert len(loaded.entries) == 2


def test_save_creates_parent_dirs(tmp_path: Path, audit_log: AuditLog) -> None:
    dest = tmp_path / "nested" / "dir" / "audit.json"
    save_audit_log(audit_log, dest)
    assert dest.exists()


def test_load_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(AuditError, match="not found"):
        load_audit_log(tmp_path / "nonexistent.json")


def test_load_corrupt_file_raises(tmp_path: Path) -> None:
    dest = tmp_path / "audit.json"
    dest.write_text("{bad json")
    with pytest.raises(AuditError, match="Failed to load"):
        load_audit_log(dest)


def test_save_corrupt_existing_raises(tmp_path: Path, audit_log: AuditLog) -> None:
    dest = tmp_path / "audit.json"
    dest.write_text("{bad json")
    with pytest.raises(AuditError, match="Corrupt"):
        save_audit_log(audit_log, dest)
