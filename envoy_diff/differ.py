"""Core diffing logic for comparing environment variable configs across stages."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two environment configs."""

    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)
    unchanged: Set[str] = field(default_factory=set)

    @property
    def has_diff(self) -> bool:
        """Return True if there are any differences."""
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        """Return a human-readable summary of the diff."""
        lines = []
        if self.added:
            lines.append(f"  Added:   {len(self.added)} key(s)")
        if self.removed:
            lines.append(f"  Removed: {len(self.removed)} key(s)")
        if self.changed:
            lines.append(f"  Changed: {len(self.changed)} key(s)")
        if not lines:
            return "No differences found."
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Return a plain dictionary representation of the diff result.

        Useful for serialisation (e.g. JSON output or test assertions).
        """
        return {
            "added": self.added,
            "removed": self.removed,
            "changed": {k: {"old": old, "new": new} for k, (old, new) in self.changed.items()},
            "unchanged": sorted(self.unchanged),
        }


def diff_configs(
    source: Dict[str, str],
    target: Dict[str, str],
    ignore_keys: Optional[List[str]] = None,
) -> DiffResult:
    """Compare two environment configs and return a DiffResult.

    Args:
        source: The baseline config (e.g., staging).
        target: The config to compare against (e.g., production).
        ignore_keys: Optional list of keys to exclude from comparison.

    Returns:
        A DiffResult describing additions, removals, and changes.
    """
    ignored: Set[str] = set(ignore_keys or [])
    source_keys = {k for k in source if k not in ignored}
    target_keys = {k for k in target if k not in ignored}

    result = DiffResult()

    result.added = {k: target[k] for k in target_keys - source_keys}
    result.removed = {k: source[k] for k in source_keys - target_keys}

    for key in source_keys & target_keys:
        if source[key] != target[key]:
            result.changed[key] = (source[key], target[key])
        else:
            result.unchanged.add(key)

    return result
