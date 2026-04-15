"""Tests for envoy_diff.commands.snapshot_cmd."""

from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path

import pytest

from envoy_diff.commands.snapshot_cmd import run_snapshot_command
from envoy_diff.snapshotter import save_snapshot

SAMPLE_CONFIG = {"APP_ENV": "staging", "PORT": "9000"}


@pytest.fixture()
def env_file(tmp_path) -> Path:
    f = tmp_path / "config.env"
    f.write_text("APP_ENV=staging\nPORT=9000\n", encoding="utf-8")
    return f


@pytest.fixture()
def snapshot_dir(tmp_path) -> Path:
    return tmp_path / "snaps"


def test_cmd_save_creates_snapshot(env_file, snapshot_dir, capsys):
    args = Namespace(
        snap_action="save",
        file=str(env_file),
        stage="staging",
        output_dir=str(snapshot_dir),
        label=None,
    )
    code = run_snapshot_command(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "Snapshot saved" in out
    assert snapshot_dir.exists()


def test_cmd_save_invalid_file_returns_error(snapshot_dir, capsys):
    args = Namespace(
        snap_action="save",
        file="/no/such/file.env",
        stage="staging",
        output_dir=str(snapshot_dir),
        label=None,
    )
    code = run_snapshot_command(args)
    assert code == 1
    assert "Error" in capsys.readouterr().err


def test_cmd_list_shows_snapshots(snapshot_dir, capsys):
    save_snapshot(SAMPLE_CONFIG, stage="staging", output_dir=str(snapshot_dir))
    save_snapshot(SAMPLE_CONFIG, stage="staging", output_dir=str(snapshot_dir))
    args = Namespace(snap_action="list", stage="staging", output_dir=str(snapshot_dir))
    code = run_snapshot_command(args)
    assert code == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 2


def test_cmd_list_no_snapshots(snapshot_dir, capsys):
    args = Namespace(snap_action="list", stage="prod", output_dir=str(snapshot_dir))
    code = run_snapshot_command(args)
    assert code == 0
    assert "No snapshots" in capsys.readouterr().out


def test_cmd_load_prints_config(snapshot_dir, capsys):
    path = save_snapshot(SAMPLE_CONFIG, stage="staging", output_dir=str(snapshot_dir))
    args = Namespace(snap_action="load", snapshot_file=str(path))
    code = run_snapshot_command(args)
    assert code == 0
    out = capsys.readouterr().out
    assert "APP_ENV=staging" in out
    assert "PORT=9000" in out


def test_cmd_load_missing_file_returns_error(capsys):
    args = Namespace(snap_action="load", snapshot_file="/no/such/snap.json")
    code = run_snapshot_command(args)
    assert code == 1
    assert "Error" in capsys.readouterr().err


def test_cmd_unknown_action_returns_error(capsys):
    args = Namespace(snap_action="destroy")
    code = run_snapshot_command(args)
    assert code == 1
    assert "Unknown" in capsys.readouterr().err
