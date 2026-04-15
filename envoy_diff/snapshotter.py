"""Snapshot management for saving and loading env config states."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

SNAPSHOT_VERSION = 1


class SnapshotError(Exception):
    """Raised when snapshot operations fail."""


def save_snapshot(
    config: Dict[str, str],
    stage: str,
    output_dir: str = ".envoy_snapshots",
    label: Optional[str] = None,
) -> Path:
    """Persist a config snapshot to disk as JSON.

    Args:
        config: The environment variable mapping to snapshot.
        stage: Deployment stage name (e.g. 'production').
        output_dir: Directory where snapshots are stored.
        label: Optional human-readable label for the snapshot.

    Returns:
        Path to the written snapshot file.
    """
    snapshot_dir = Path(output_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"{stage}_{timestamp}.json"
    filepath = snapshot_dir / filename

    payload = {
        "version": SNAPSHOT_VERSION,
        "stage": stage,
        "timestamp": timestamp,
        "label": label or "",
        "config": config,
    }

    try:
        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as exc:
        raise SnapshotError(f"Failed to write snapshot to {filepath}: {exc}") from exc

    return filepath


def load_snapshot(filepath: str) -> Dict[str, str]:
    """Load a previously saved config snapshot.

    Args:
        filepath: Path to the snapshot JSON file.

    Returns:
        The config mapping stored in the snapshot.

    Raises:
        SnapshotError: If the file is missing, unreadable, or malformed.
    """
    path = Path(filepath)
    if not path.exists():
        raise SnapshotError(f"Snapshot file not found: {filepath}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"Failed to read snapshot {filepath}: {exc}") from exc

    if "config" not in data:
        raise SnapshotError(f"Invalid snapshot format in {filepath}: missing 'config' key")

    return data["config"]


def list_snapshots(stage: str, output_dir: str = ".envoy_snapshots") -> list[Path]:
    """Return sorted list of snapshot paths for a given stage."""
    snapshot_dir = Path(output_dir)
    if not snapshot_dir.exists():
        return []
    return sorted(snapshot_dir.glob(f"{stage}_*.json"))
