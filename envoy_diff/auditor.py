"""Auditor module: tracks and records diff/validation audit events."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class AuditError(Exception):
    """Raised when an audit operation fails."""


@dataclass
class AuditEntry:
    timestamp: str
    stage_a: str
    stage_b: str
    has_diff: bool
    validation_passed: bool
    added: int = 0
    removed: int = 0
    changed: int = 0
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "stage_a": self.stage_a,
            "stage_b": self.stage_b,
            "has_diff": self.has_diff,
            "validation_passed": self.validation_passed,
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "label": self.label,
        }


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def append(self, entry: AuditEntry) -> None:
        self.entries.append(entry)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_entry(
    stage_a: str,
    stage_b: str,
    has_diff: bool,
    validation_passed: bool,
    added: int = 0,
    removed: int = 0,
    changed: int = 0,
    label: Optional[str] = None,
) -> AuditEntry:
    """Create a new AuditEntry with the current UTC timestamp."""
    return AuditEntry(
        timestamp=_now_iso(),
        stage_a=stage_a,
        stage_b=stage_b,
        has_diff=has_diff,
        validation_passed=validation_passed,
        added=added,
        removed=removed,
        changed=changed,
        label=label,
    )


def save_audit_log(log: AuditLog, path: Path) -> None:
    """Persist an AuditLog to a JSON file, appending to existing entries."""
    existing: List[dict] = []
    if path.exists():
        try:
            data = json.loads(path.read_text())
            existing = data.get("entries", [])
        except (json.JSONDecodeError, KeyError) as exc:
            raise AuditError(f"Corrupt audit log at {path}: {exc}") from exc

    all_entries = existing + [e.to_dict() for e in log.entries]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"entries": all_entries}, indent=2))


def load_audit_log(path: Path) -> AuditLog:
    """Load an AuditLog from a JSON file."""
    if not path.exists():
        raise AuditError(f"Audit log not found: {path}")
    try:
        data = json.loads(path.read_text())
        entries = [
            AuditEntry(**{k: v for k, v in e.items()}) for e in data.get("entries", [])
        ]
        return AuditLog(entries=entries)
    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        raise AuditError(f"Failed to load audit log: {exc}") from exc
