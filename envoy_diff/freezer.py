"""Freeze a config snapshot and detect drift against a live config."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FreezeResult:
    frozen: Dict[str, str]
    drifted: List[str] = field(default_factory=list)
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    @property
    def drift_count(self) -> int:
        return len(self.drifted) + len(self.added) + len(self.removed)

    @property
    def has_drift(self) -> bool:
        return self.drift_count > 0

    def summary(self) -> str:
        if not self.has_drift:
            return "No drift detected."
        parts = []
        if self.drifted:
            parts.append(f"{len(self.drifted)} changed")
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        return "Drift detected: " + ", ".join(parts) + "."


def freeze_config(config: Dict[str, str]) -> Dict[str, str]:
    """Return an immutable snapshot copy of config."""
    return dict(config)


def check_drift(
    frozen: Dict[str, str],
    live: Dict[str, str],
    ignore_keys: Optional[List[str]] = None,
) -> FreezeResult:
    """Compare a frozen snapshot against a live config and report drift."""
    ignore = set(ignore_keys or [])
    frozen_keys = set(frozen) - ignore
    live_keys = set(live) - ignore

    drifted = [
        k for k in frozen_keys & live_keys if frozen[k] != live[k]
    ]
    added = sorted(live_keys - frozen_keys)
    removed = sorted(frozen_keys - live_keys)

    return FreezeResult(
        frozen=frozen,
        drifted=sorted(drifted),
        added=added,
        removed=removed,
    )
