"""Pin and unpin environment variable values for drift detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class PinError(Exception):
    """Raised when a pin operation fails."""


@dataclass
class PinResult:
    pinned: Dict[str, str]
    unpinned: List[str] = field(default_factory=list)
    drifted: Dict[str, tuple] = field(default_factory=dict)

    @property
    def pin_count(self) -> int:
        return len(self.pinned)

    @property
    def drift_count(self) -> int:
        return len(self.drifted)

    def has_drift(self) -> bool:
        return bool(self.drifted)

    def summary(self) -> str:
        parts = [f"{self.pin_count} pinned"]
        if self.unpinned:
            parts.append(f"{len(self.unpinned)} unpinned")
        if self.drifted:
            parts.append(f"{self.drift_count} drifted")
        return ", ".join(parts)


def pin_config(config: Dict[str, str], keys: List[str] | None = None) -> PinResult:
    """Pin specified keys (or all) from config."""
    if keys is None:
        keys = list(config.keys())
    pinned = {k: config[k] for k in keys if k in config}
    unpinned = [k for k in keys if k not in config]
    return PinResult(pinned=pinned, unpinned=unpinned)


def check_drift(
    config: Dict[str, str], pins: Dict[str, str]
) -> PinResult:
    """Compare current config against pinned values and report drift."""
    drifted: Dict[str, tuple] = {}
    for key, pinned_val in pins.items():
        current_val = config.get(key)
        if current_val is None or current_val != pinned_val:
            drifted[key] = (pinned_val, current_val)
    return PinResult(pinned=pins, drifted=drifted)
