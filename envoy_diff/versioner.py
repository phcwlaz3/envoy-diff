"""Version-stamp environment configs with metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class VersionResult:
    config: Dict[str, str]
    version: str
    stamped_at: str
    label: Optional[str]
    keys_stamped: List[str] = field(default_factory=list)

    def stamp_count(self) -> int:
        return len(self.keys_stamped)

    def has_stamps(self) -> bool:
        return bool(self.keys_stamped)

    def summary(self) -> str:
        label_part = f" ({self.label})" if self.label else ""
        return (
            f"Version: {self.version}{label_part} | "
            f"Stamped: {self.stamp_count()} key(s) | "
            f"At: {self.stamped_at}"
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def version_config(
    config: Dict[str, str],
    version: str,
    *,
    label: Optional[str] = None,
    prefix: str = "ENVOY_",
    inject_keys: bool = True,
) -> VersionResult:
    """Stamp a config dict with version metadata.

    Optionally injects ENVOY_VERSION, ENVOY_STAMPED_AT, and ENVOY_LABEL
    keys into the returned config.
    """
    stamped_at = _utc_now()
    result = dict(config)
    keys_stamped: List[str] = []

    if inject_keys:
        version_key = f"{prefix}VERSION"
        result[version_key] = version
        keys_stamped.append(version_key)

        ts_key = f"{prefix}STAMPED_AT"
        result[ts_key] = stamped_at
        keys_stamped.append(ts_key)

        if label:
            label_key = f"{prefix}LABEL"
            result[label_key] = label
            keys_stamped.append(label_key)

    return VersionResult(
        config=result,
        version=version,
        stamped_at=stamped_at,
        label=label,
        keys_stamped=keys_stamped,
    )
