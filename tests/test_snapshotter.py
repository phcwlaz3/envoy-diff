"""Tests for envoy_diff.snapshotter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envoy_diff.snapshotter import (
    SnapshotError,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)

SAMPLE_CONFIG = {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}


def test_save_snapshot_creates_file(tmp_path):
    filepath = save_snapshot(SAMPLE_CONFIG, stage="prod", output_dir=str(tmp_path))
    assert filepath.exists()
    assert filepath.suffix == ".json"
    assert "prod_" in filepath.name


def test_save_snapshot_content(tmp_path):
    filepath = save_snapshot(SAMPLE_CONFIG, stage="staging", output_dir=str(tmp_path))
    data = json.loads(filepath.read_text())
    assert data["stage"] == "staging"
    assert data["config"] == SAMPLE_CONFIG
    assert data["version"] == 1
    assert "timestamp" in data


def test_save_snapshot_with_label(tmp_path):
    filepath = save_snapshot(
        SAMPLE_CONFIG, stage="dev", output_dir=str(tmp_path), label="pre-release"
    )
    data = json.loads(filepath.read_text())
    assert data["label"] == "pre-release"


def test_save_snapshot_creates_output_dir(tmp_path):
    nested = tmp_path / "deep" / "nested"
    save_snapshot(SAMPLE_CONFIG, stage="prod", output_dir=str(nested))
    assert nested.exists()


def test_load_snapshot_returns_config(tmp_path):
    filepath = save_snapshot(SAMPLE_CONFIG, stage="prod", output_dir=str(tmp_path))
    loaded = load_snapshot(str(filepath))
    assert loaded == SAMPLE_CONFIG


def test_load_snapshot_file_not_found():
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot("/nonexistent/path/snapshot.json")


def test_load_snapshot_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json", encoding="utf-8")
    with pytest.raises(SnapshotError, match="Failed to read"):
        load_snapshot(str(bad_file))


def test_load_snapshot_missing_config_key(tmp_path):
    bad_file = tmp_path / "missing_key.json"
    bad_file.write_text(json.dumps({"stage": "prod"}), encoding="utf-8")
    with pytest.raises(SnapshotError, match="missing 'config' key"):
        load_snapshot(str(bad_file))


def test_list_snapshots_returns_sorted(tmp_path):
    save_snapshot(SAMPLE_CONFIG, stage="prod", output_dir=str(tmp_path))
    save_snapshot(SAMPLE_CONFIG, stage="prod", output_dir=str(tmp_path))
    save_snapshot(SAMPLE_CONFIG, stage="staging", output_dir=str(tmp_path))

    results = list_snapshots("prod", output_dir=str(tmp_path))
    assert len(results) == 2
    assert all("prod_" in p.name for p in results)
    assert results == sorted(results)


def test_list_snapshots_empty_when_no_dir(tmp_path):
    results = list_snapshots("prod", output_dir=str(tmp_path / "missing"))
    assert results == []


def test_list_snapshots_empty_when_no_matching_stage(tmp_path):
    save_snapshot(SAMPLE_CONFIG, stage="staging", output_dir=str(tmp_path))
    results = list_snapshots("prod", output_dir=str(tmp_path))
    assert results == []
