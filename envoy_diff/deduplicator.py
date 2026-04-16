"""Deduplicator: detect and remove duplicate values across a config."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DeduplicateResult:
    config: Dict[str, str]
    duplicates: Dict[str, List[str]]  # value -> list of keys sharing it

    def duplicate_count(self) -> int:
        return sum(len(keys) - 1 for keys in self.duplicates.values())

    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates():
            return "No duplicate values found."
        lines = [f"Found {self.duplicate_count()} duplicate value(s):"]
        for value, keys in self.duplicates.items():
            display = value if len(value) <= 40 else value[:37] + "..."
            lines.append(f"  {display!r}: {', '.join(keys)}")
        return "\n".join(lines)


def deduplicate_config(
    config: Dict[str, str],
    keep: str = "first",
) -> DeduplicateResult:
    """Detect keys that share identical values.

    Args:
        config: mapping of env var names to values.
        keep: 'first' keeps the first occurrence, 'last' keeps the last.

    Returns:
        DeduplicateResult with a deduplicated config and duplicate map.
    """
    value_to_keys: Dict[str, List[str]] = {}
    for key, value in config.items():
        value_to_keys.setdefault(value, []).append(key)

    duplicates = {v: keys for v, keys in value_to_keys.items() if len(keys) > 1}

    keys_to_remove: set[str] = set()
    for keys in duplicates.values():
        if keep == "last":
            keys_to_remove.update(keys[:-1])
        else:
            keys_to_remove.update(keys[1:])

    deduped = {k: v for k, v in config.items() if k not in keys_to_remove}
    return DeduplicateResult(config=deduped, duplicates=duplicates)
