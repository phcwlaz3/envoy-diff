"""Prune keys from a config based on patterns or an explicit list."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class PruneResult:
    original: Dict[str, str]
    pruned: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)

    def removed_count(self) -> int:
        return len(self.removed_keys)

    def has_removals(self) -> bool:
        return bool(self.removed_keys)

    def summary(self) -> str:
        if not self.has_removals():
            return "No keys pruned."
        return (
            f"Pruned {self.removed_count()} key(s): "
            + ", ".join(sorted(self.removed_keys))
        )


def prune_config(
    config: Dict[str, str],
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
) -> PruneResult:
    """Remove keys that match *keys* exactly or *patterns* via fnmatch."""
    keys = keys or []
    patterns = patterns or []

    removed: List[str] = []
    pruned: Dict[str, str] = {}

    for k, v in config.items():
        if k in keys or any(fnmatch(k, p) for p in patterns):
            removed.append(k)
        else:
            pruned[k] = v

    return PruneResult(original=dict(config), pruned=pruned, removed_keys=removed)
