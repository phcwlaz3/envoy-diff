"""Merge multiple environment configs with conflict detection."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MergeConflictError(Exception):
    """Raised when configs have irreconcilable conflicts during merge."""


@dataclass
class MergeResult:
    merged: Dict[str, str]
    conflicts: Dict[str, List[str]]  # key -> list of differing values
    sources: List[str] = field(default_factory=list)

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def summary(self) -> str:
        total = len(self.merged)
        conflict_count = len(self.conflicts)
        src = ", ".join(self.sources) if self.sources else "unknown"
        if conflict_count:
            return (
                f"Merged {total} keys from [{src}] "
                f"with {conflict_count} conflict(s)."
            )
        return f"Merged {total} keys from [{src}] cleanly."


def merge_configs(
    configs: List[Dict[str, str]],
    sources: Optional[List[str]] = None,
    strategy: str = "last_wins",
) -> MergeResult:
    """Merge a list of env configs into one.

    Args:
        configs: List of env dicts to merge.
        sources: Optional labels for each config (for reporting).
        strategy: 'last_wins' keeps the final value; 'first_wins' keeps the first.
                  Any conflict is still recorded regardless of strategy.

    Returns:
        MergeResult with merged dict and any detected conflicts.
    """
    if not configs:
        return MergeResult(merged={}, conflicts={}, sources=sources or [])

    if strategy not in ("last_wins", "first_wins"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    merged: Dict[str, str] = {}
    seen: Dict[str, str] = {}  # key -> first value observed
    conflicts: Dict[str, List[str]] = {}

    for config in configs:
        for key, value in config.items():
            if key not in seen:
                seen[key] = value
                merged[key] = value
            else:
                if seen[key] != value:
                    if key not in conflicts:
                        conflicts[key] = [seen[key]]
                    if value not in conflicts[key]:
                        conflicts[key].append(value)
                    if strategy == "last_wins":
                        merged[key] = value

    return MergeResult(
        merged=merged,
        conflicts=conflicts,
        sources=sources or [],
    )
