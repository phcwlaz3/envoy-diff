"""Pivot a flat env config into a nested dict grouped by key prefix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class PivotResult:
    pivoted: Dict[str, Any]
    original_count: int
    group_count: int
    ungrouped: Dict[str, str]

    def key_count(self) -> int:
        return self.original_count

    def has_ungrouped(self) -> bool:
        return bool(self.ungrouped)

    def summary(self) -> str:
        parts = [
            f"{self.original_count} keys pivoted into {self.group_count} group(s)",
        ]
        if self.ungrouped:
            parts.append(f"{len(self.ungrouped)} ungrouped")
        return ", ".join(parts)


def pivot_config(
    config: Dict[str, str],
    *,
    separator: str = "_",
    min_prefix_length: int = 2,
) -> PivotResult:
    """Pivot *config* into a nested dict keyed by the first token of each key.

    Keys that do not contain *separator*, or whose prefix is shorter than
    *min_prefix_length*, are placed in the ``_ungrouped`` bucket.
    """
    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}

    for key, value in config.items():
        if separator in key:
            prefix, remainder = key.split(separator, 1)
            if len(prefix) >= min_prefix_length:
                groups.setdefault(prefix, {})[remainder] = value
                continue
        ungrouped[key] = value

    pivoted: Dict[str, Any] = {k: dict(v) for k, v in groups.items()}
    if ungrouped:
        pivoted["_ungrouped"] = ungrouped

    return PivotResult(
        pivoted=pivoted,
        original_count=len(config),
        group_count=len(groups),
        ungrouped=ungrouped,
    )
